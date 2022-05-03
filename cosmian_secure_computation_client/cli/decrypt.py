"""cosmian_secure_computation_client.cli.decrypt module."""

from argparse import Namespace
from pathlib import Path

from cosmian_secure_computation_client.crypto.helper import (decrypt_directory,
                                                             decrypt_file)


def parse_decrypt(args: Namespace):
    key: bytes
    out_path: Path

    if args.directory:
        dir_path: Path = Path(args.directory).absolute()
        print(f"==> Decrypt directory {dir_path}...")
        if not dir_path.exists():
            raise FileNotFoundError

        key = (Path(args.key_file).read_bytes() if args.key_file
               else bytes.fromhex(args.key))

        decrypt_directory(dir_path=dir_path,
                          key=key)
    else:
        file_path: Path = Path(args.file).absolute()
        print(f"==> Decrypt file {file_path.name}...")

        if not file_path.exists():
            raise FileNotFoundError

        key = (Path(args.key_file).read_bytes() if args.key_file
               else bytes.fromhex(args.key))

        decrypt_file(file_path, key)
