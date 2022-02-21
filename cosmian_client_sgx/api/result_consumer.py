"""cosmian_client_sgx.api.result_owner module."""

from typing import Optional

import requests

from cosmian_client_sgx.api.side import Side
from cosmian_client_sgx.api.common import CommonAPI


class ResultConsumerAPI(CommonAPI):
    def __init__(self, hostname: str, port: int, ssl: bool = False) -> None:
        super().__init__(Side.ResultConsumer, hostname, port, ssl)

    def run(self, algo_name: str, entrypoint: str) -> bool:
        resp: requests.Response = self.session.post(
            url=f"{self.url}/enclave/run/{algo_name}/{self.fingerprint.hex()}",
            json={"entrypoint": entrypoint})

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        # output = resp.json()["success"]
        # print(f"Output: {output}")
        #
        # return self.decrypt(bytes.fromhex(output))

        return True if "success" in resp.json() else False

    def fetch_result(self, algo_name: str) -> Optional[bytes]:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/enclave/result/{algo_name}/{self.fingerprint.hex()}"
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        if "success" not in resp.json():
            return None

        return self.decrypt(bytes.fromhex(resp.json()["success"]))
