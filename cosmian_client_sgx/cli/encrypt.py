"""cosmian_client_sgx.cli.encrypt module."""

from argparse import Namespace
from pathlib import Path
import shutil
import tempfile

from cosmian_client_sgx.crypto.helper import encrypt_directory, encrypt_file
from cosmian_client_sgx.util.fs import tar


def parse_encrypt(args: Namespace) -> None:
    key: bytes
    out_path: Path

    if args.directory:
        dir_path: Path = Path(args.directory).absolute()
        print(f"==> Encrypt directory {dir_path}...")
        if not dir_path.exists():
            raise FileNotFoundError

        key = (Path(args.key_file).read_bytes() if args.key_file
               else bytes.fromhex(args.key))

        out_path = Path(args.output_dir).absolute()

        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_dir_path: Path = Path(temp_dir)
            encrypt_directory(dir_path=dir_path,
                              patterns=["*"],
                              key=key,
                              exceptions=["run.py"],
                              dir_exceptions=[],
                              out_dir_path=tmp_dir_path)

            dst_path: Path
            if args.tar:
                dst_path = out_path / f"{dir_path.name}.tar"
                tar(tmp_dir_path, dst_path)
            else:
                dst_path = out_path
                shutil.copytree(tmp_dir_path, dst_path)
            print(f"  --> Directory encrypted and copied to {dst_path}")
    else:
        file_path: Path = Path(args.file).absolute()
        print(f"==> Encrypt file {file_path.name}...")

        if not file_path.exists():
            raise FileNotFoundError

        key = (Path(args.key_file).read_bytes() if args.key_file
               else bytes.fromhex(args.key))

        out_path = Path(args.output_dir).absolute()

        encrypt_file(out_path / file_path.name, key)
