"""cosmian_secure_computation_client.crypto.context module."""

from pathlib import Path
from typing import Optional, List

from cosmian_secure_computation_client.crypto.helper import (x25519_keypair,
                                                             x25519_pubkey_from_privkey,
                                                             client_shared_key,
                                                             encrypt,
                                                             decrypt,
                                                             encrypt_file,
                                                             decrypt_file,
                                                             encrypt_directory,
                                                             decrypt_directory,
                                                             random_symkey,
                                                             pubkey_fingerprint,
                                                             seal)


class CryptoContext:
    def __init__(self, private_key: Optional[bytes] = None):
        self.privkey: bytes
        self.pubkey: bytes
        self.pubkey, self.privkey = (
            x25519_keypair() if private_key is None else
            (x25519_pubkey_from_privkey(private_key), private_key)
        )
        self.fingerprint: bytes = pubkey_fingerprint(self.pubkey)
        self.remote_pubkey: Optional[bytes] = None
        self._shared_key: Optional[bytes] = None
        self._symkey: bytes = random_symkey()

    def set_keypair(self, public_key: bytes, private_key: bytes) -> None:
        self.pubkey = public_key
        self.privkey = private_key
        self.fingerprint = pubkey_fingerprint(self.pubkey)

    def set_symkey(self, symkey: bytes) -> None:
        self._symkey = symkey

    @classmethod
    def from_path(cls, private_key_path: Path):
        pass

    @classmethod
    def from_pem(cls, private_key: str):
        pass

    def key_exchange(self, remote_public_key: bytes) -> None:
        self.remote_pubkey = remote_public_key
        self._shared_key = client_shared_key(
            self.pubkey,
            self.privkey,
            self.remote_pubkey
        )

    def encrypt(self, data: bytes) -> bytes:
        return encrypt(data, self._symkey)

    def encrypt_file(self, path: Path) -> Path:
        return encrypt_file(path, self._symkey)

    def encrypt_directory(self, dir_path: Path, patterns: List[str],
                          exceptions: List[str], dir_exceptions: List[str],
                          out_dir_path: Path) -> bool:
        return encrypt_directory(dir_path, patterns, self._symkey,
                                 exceptions, dir_exceptions, out_dir_path)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        return decrypt(encrypted_data, self._symkey)

    def decrypt_file(self, path: Path) -> Path:
        return decrypt_file(path, self._symkey)

    def decrypt_directory(self, dir_path: Path) -> bool:
        return decrypt_directory(dir_path, self._symkey)

    def seal_symkey(self) -> bytes:
        if self.remote_pubkey is None:
            raise Exception("Remote public key must be setup first!")

        return seal(self._symkey, self.remote_pubkey)
