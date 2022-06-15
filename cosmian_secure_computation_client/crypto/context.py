"""cosmian_secure_computation_client.crypto.context module."""

from pathlib import Path
from typing import Optional, List

from cosmian_secure_computation_client.crypto.helper import (ed25519_keygen,
                                                             ed25519_seed_keygen,
                                                             ed25519_to_x25519_keypair,
                                                             ed25519_to_x25519_pubkey,
                                                             encrypt,
                                                             decrypt,
                                                             encrypt_file,
                                                             decrypt_file,
                                                             encrypt_directory,
                                                             decrypt_directory,
                                                             random_symkey,
                                                             pubkey_fingerprint,
                                                             seal,
                                                             sign)


class CryptoContext:
    def __init__(self,
                 ed25519_seed: Optional[bytes] = None,
                 symkey: Optional[bytes] = None) -> None:
        self.ed25519_pk, self.ed25519_seed, self.ed25519_sk = (
            ed25519_keygen() if ed25519_seed is None else
            ed25519_seed_keygen(ed25519_seed)
        )  # type: bytes, bytes, bytes
        self.x25519_pk, self.x25519_sk = ed25519_to_x25519_keypair(
            self.ed25519_pk,
            self.ed25519_seed
        )  # type: bytes, bytes
        self.ed25519_fingerprint: bytes = pubkey_fingerprint(self.ed25519_pk)
        self._symkey: bytes = symkey if symkey else random_symkey()

    @property
    def public_key(self) -> bytes:
        return self.ed25519_pk

    @property
    def fingerprint(self) -> bytes:
        return self.ed25519_fingerprint

    @property
    def symkey(self) -> bytes:
        return self._symkey

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

    def sign(self, data: bytes) -> bytes:
        return sign(data, self.ed25519_seed)

    def seal_symkey(self, ed25519_recipient_pk: bytes) -> bytes:
        x25519_recipient_pk: bytes = ed25519_to_x25519_pubkey(ed25519_recipient_pk)
        seal_box: bytes = seal(self._symkey, x25519_recipient_pk)
        sig: bytes = self.sign(seal_box)

        return sig + seal_box
