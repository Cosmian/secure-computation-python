"""cosmian_client_sgx.api.algo_provider module."""

from pathlib import Path
import tempfile
from typing import Optional, Dict, List

import requests

from cosmian_client_sgx.util.fs import tar
from cosmian_client_sgx.api.side import Side
from cosmian_client_sgx.api.common import CommonAPI


class AlgoProviderAPI(CommonAPI):
    def __init__(self, hostname: str, port: int, ssl: bool = False) -> None:
        self.algo_name: Optional[str] = None
        super().__init__(Side.AlgoProvider, hostname, port, ssl)

    def upload_tar(self, tar_path: Path) -> Dict[str, str]:
        if not tar_path.exists():
            raise FileNotFoundError("Can't find tar file!")

        self.algo_name = tar_path.stem

        with tar_path.open("rb") as fp:
            resp: requests.Response = self.session.post(
                url=f"{self.url}/enclave/upload_algo/{self.algo_name}",
                files={
                    "file": (tar_path.name, fp, "application/tar", {
                        "Expires": "0"
                    })
                },
                timeout=None)

            if not resp.ok:
                raise Exception(
                    f"Unexpected response ({resp.status_code}): {resp.content}"
                )

            return resp.json()

    def upload(self, dir_path: Path, exceptions: Optional[List[str]] = None, encrypt: bool = True) -> Dict[str, str]:
        tar_path: Path
        if encrypt:
            enc_dir_path: Path = Path(tempfile.gettempdir()) / dir_path.name
            self.encrypt_directory(dir_path=dir_path,
                                   patterns=["*"],
                                   exceptions=[] if exceptions is None else exceptions,
                                   dir_exceptions=[".git"],
                                   out_dir_path=enc_dir_path)
            tar_path = tar(enc_dir_path, enc_dir_path / f"{enc_dir_path.name}.tar")
        else:
            tar_path = tar(dir_path, dir_path / f"{dir_path.name}.tar")
        return self.upload_tar(tar_path)
