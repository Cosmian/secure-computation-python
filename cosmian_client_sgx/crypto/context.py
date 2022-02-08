"""cosmian_client_sgx.crypto.context module."""

from pathlib import Path
from typing import Optional, List

from cosmian_client_sgx.crypto.helper import (x25519_keypair, x25519_pubkey_from_privkey,
                                              client_shared_key, encrypt, decrypt,
                                              encrypt_file, decrypt_file,
                                              encrypt_directory, decrypt_directory,
                                              pubkey_fingerprint)


class CryptoContext:
    def __init__(self, private_key: Optional[bytes] = None):
        self.privkey: bytes
        self.pubkey: bytes
        if private_key is None:
            self.pubkey, self.privkey = x25519_keypair()
        else:
            self.pubkey, self.privkey = x25519_pubkey_from_privkey(private_key), private_key
        self.fingerprint: bytes = pubkey_fingerprint(self.pubkey)
        self.remote_pubkey: Optional[bytes] = None
        self._shared_key: Optional[bytes] = None

    def set_keypair(self, public_key: bytes, private_key: bytes) -> None:
        self.pubkey = public_key
        self.privkey = private_key
        self.fingerprint = pubkey_fingerprint(self.pubkey)

        if self.remote_pubkey:
            self.key_exchange(self.remote_pubkey)

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
        return encrypt(data, self._shared_key)

    def encrypt_file(self, path: Path) -> Path:
        return encrypt_file(path, self._shared_key)

    def encrypt_directory(self, dir_path: Path, patterns: List[str],
                          exceptions: List[str], dir_exceptions: List[str],
                          out_dir_path: Path) -> bool:
        return encrypt_directory(dir_path, patterns, self._shared_key,
                                 exceptions, dir_exceptions, out_dir_path)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        return decrypt(encrypted_data, self._shared_key)

    def decrypt_file(self, path: Path) -> Path:
        return decrypt_file(path, self._shared_key)

    def decrypt_directory(self, dir_path: Path) -> bool:
        return decrypt_directory(dir_path, self._shared_key)
