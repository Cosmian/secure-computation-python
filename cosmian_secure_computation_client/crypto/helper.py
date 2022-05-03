"""cosmian_secure_computation_client.crypto.helper module."""

import hashlib
from pathlib import Path
import shutil
from typing import Tuple, List

import nacl.public
import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, PublicKey, SealedBox
from nacl.secret import SecretBox
from nacl.bindings.crypto_scalarmult import (crypto_scalarmult,
                                             crypto_scalarmult_ed25519_base,
                                             crypto_scalarmult_ed25519_SCALARBYTES)
from nacl.bindings import (crypto_sign_keypair,
                           crypto_sign_ed25519_sk_to_curve25519,
                           crypto_sign_ed25519_pk_to_curve25519,
                           crypto_sign_SEEDBYTES)
from nacl.hash import blake2b
from nacl.encoding import RawEncoder

ENC_EXT: str = ".enc"


def pubkey_fingerprint(public_key: bytes) -> bytes:
    return hashlib.sha3_256(public_key).digest()[-8:]


def x25519_keypair() -> Tuple[bytes, bytes]:
    private_key: PrivateKey = PrivateKey.generate()
    public_key: PublicKey = private_key.public_key

    return bytes(public_key), bytes(private_key)


def x25519_pubkey_from_privkey(private_key: bytes) -> bytes:
    return bytes(PrivateKey(private_key).public_key)


def ed25519_keygen() -> Tuple[bytes, bytes, bytes]:
    public_key, sk = crypto_sign_keypair()  # type: bytes, bytes
    seed: bytes = sk[:crypto_sign_SEEDBYTES]
    private_key: bytes = hashlib.sha512(
        seed
    ).digest()[:crypto_scalarmult_ed25519_SCALARBYTES]

    return public_key, seed, private_key


def ed25519_pubkey_from_privkey(private_key: bytes) -> bytes:
    return crypto_scalarmult_ed25519_base(private_key)


def ed25519_to_x25519(public_key: bytes, seed: bytes) -> Tuple[bytes, bytes]:
    x25519_privkey: bytes = crypto_sign_ed25519_sk_to_curve25519(seed + public_key)
    x25519_pubkey: bytes = crypto_sign_ed25519_pk_to_curve25519(public_key)

    return x25519_pubkey, x25519_privkey


def x25519(private_key: bytes, public_key: bytes) -> bytes:
    return crypto_scalarmult(private_key, public_key)


def server_shared_key(public_key: bytes, private_key: bytes,
                      remote_pubkey: bytes) -> bytes:
    shared_key: bytes = x25519(private_key, remote_pubkey)

    # Blake2b(shared_key || remote_pubkey || public_key)
    return blake2b(shared_key + remote_pubkey + public_key, encoder=RawEncoder)


def client_shared_key(public_key: bytes, private_key: bytes,
                      remote_pubkey: bytes) -> bytes:
    shared_key = crypto_scalarmult(private_key, remote_pubkey)

    # Blake2b(shared_key || public_key || remote_pubkey)
    return blake2b(shared_key + public_key + remote_pubkey, encoder=RawEncoder)


def encrypt(data: bytes, key: bytes) -> bytes:
    box: SecretBox = SecretBox(key)

    return box.encrypt(data)


def encrypt_file(path: Path, key: bytes) -> Path:
    if not path.is_file():
        raise FileNotFoundError

    out_path: Path = path.with_suffix(f"{path.suffix}{ENC_EXT}")
    out_path.write_bytes(encrypt(path.read_bytes(), key))

    return out_path


def encrypt_directory(dir_path: Path, patterns: List[str], key: bytes,
                      exceptions: List[str], dir_exceptions: List[str],
                      out_dir_path: Path) -> bool:
    if not dir_path.is_dir():
        raise NotADirectoryError

    if out_dir_path.exists():
        shutil.rmtree(out_dir_path)

    shutil.copytree(dir_path, out_dir_path)

    for pattern in patterns:  # type: str
        for path in out_dir_path.rglob(pattern):  # type: Path
            if path.is_file() and path.name not in exceptions and all(
                    directory not in path.parts for directory in dir_exceptions):
                encrypt_file(path, key)
                path.unlink()

    return True


def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
    box: SecretBox = SecretBox(key)

    return box.decrypt(encrypted_data)


def decrypt_file(path: Path, key: bytes) -> Path:
    if not path.is_file():
        raise FileNotFoundError

    out_path: Path = path.with_suffix("")
    out_path.write_bytes(decrypt(path.read_bytes(), key))

    return out_path


def decrypt_directory(dir_path: Path, key: bytes) -> bool:
    if not dir_path.is_dir():
        raise NotADirectoryError

    for path in dir_path.rglob(f"*{ENC_EXT}"):  # type: Path
        if path.is_file():
            decrypt_file(path, key)
            path.unlink()

    return True


def seal(data: bytes, recipient_public_key: bytes) -> bytes:
    box = SealedBox(PublicKey(recipient_public_key))

    return box.encrypt(data)


def unseal(encrypted_data: bytes, private_key: bytes) -> bytes:
    box = SealedBox(PrivateKey(private_key))

    return box.decrypt(encrypted_data)


def random_symkey() -> bytes:
    return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
