"""cosmian_client_sgx.api.data_provider module."""

from pathlib import Path
from typing import Dict, Iterable

import requests

from cosmian_client_sgx.api.side import Side
from cosmian_client_sgx.api.common import CommonAPI


class DataProviderAPI(CommonAPI):
    def __init__(self, hostname: str, port: int, ssl: bool = False) -> None:
        super().__init__(Side.DataProvider, hostname, port, ssl)

    def push_data(self, algo_name: str, data_name: str, data: bytes) -> Dict[str, str]:
        encrypted_data: bytes = self.encrypt(data)

        resp: requests.Response = self.session.post(
            url=f"{self.url}/enclave/data/{algo_name}/{self.fingerprint.hex()}",
            files={
                "file": (f"{data_name}.enc", encrypted_data, "application/octet-stream", {
                    "Expires": "0"
                })
            },
            timeout=None)

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return resp.json()

    def push_files(self, algo_name: str, paths: Iterable[Path]) -> bool:
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError
            print(self.push_data(algo_name, path.name, path.read_bytes()))

        return True

    def list_data(self, algo_name: str) -> Dict[str, str]:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/enclave/data/{algo_name}/{self.fingerprint.hex()}")

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return resp.json()
