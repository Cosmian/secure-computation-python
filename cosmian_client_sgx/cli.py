"""cosmian_client_sgx.cli module."""

import argparse
from pathlib import Path
import tempfile

from cosmian_client_sgx.crypto.helper import encrypt_directory
from cosmian_client_sgx.util.fs import tar


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Encrypt/Decrypt using NaCl's family primitives")
    parser.add_argument("--encrypt-and-tar",
                        help="Encrypt files of directory and tar",
                        required=True)
    parser.add_argument("--key",
                        help="Secret key used to encrypt/decrypt",
                        required=True)

    args = parser.parse_args()

    dir_path: Path = Path(args.encrypt_and_tar).absolute()
    out_path: Path = Path().cwd()

    if not dir_path.is_dir():
        raise FileNotFoundError

    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_dir_path: Path = Path(temp_dir)
        encrypt_directory(dir_path=dir_path,
                          patterns=["*"],
                          key=bytes.fromhex(args.key),
                          exceptions=[
                              "run.py", "server.py", "setup.py",
                              "requirements.txt", "README.md", "fullchain.pem",
                              "privkey.pem"
                          ],
                          dir_exceptions=["webui"],
                          out_dir_path=tmp_dir_path)
        tar(tmp_dir_path, out_path / f"{dir_path.name}.tar")

    return 0
