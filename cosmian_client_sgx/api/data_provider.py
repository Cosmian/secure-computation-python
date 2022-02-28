"""cosmian_client_sgx.api.data_provider module."""

from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import requests

from cosmian_client_sgx.api.side import Side
from cosmian_client_sgx.api.common import CommonAPI


class DataProviderAPI(CommonAPI):
    def __init__(self,
                 hostname: str,
                 port: int,
                 ssl: bool = False,
                 auth: Optional[Tuple[str, str]] = None
                 ) -> None:
        super().__init__(Side.DataProvider, hostname, port, ssl, auth)

    def push_data(self,
                  code_name: str,
                  data_name: str,
                  data: bytes,
                  encrypt: bool = True) -> Dict[str, str]:
        encrypted_data: bytes = self.encrypt(data) if encrypt else data

        resp: requests.Response = self.session.post(
            url=f"{self.url}/enclave/data/{code_name}/{self.fingerprint.hex()}",
            files={
                "file": (f"{data_name}.enc", encrypted_data, "application/octet-stream", {
                    "Expires": "0"
                })
            },
            timeout=None,
            auth=self.auth
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return resp.json()

    def push_files(self,
                   code_name: str,
                   paths: Iterable[Path],
                   encrypt: bool = True) -> bool:
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError

            resp = self.push_data(code_name,
                                  path.name,
                                  path.read_bytes(),
                                  encrypt)

            if "success" not in resp:
                raise Exception(
                    f"Unexpected response ({resp.status_code}): {resp.content}"
                )

        return True

    def list_data(self, code_name: str) -> Dict[str, str]:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/enclave/data/{code_name}/{self.fingerprint.hex()}",
            auth=self.auth
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return resp.json()
