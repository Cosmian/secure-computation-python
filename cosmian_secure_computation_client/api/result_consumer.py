"""cosmian_secure_computation_client.api.result_consumer module."""

from typing import Optional, Tuple

import requests

from cosmian_secure_computation_client.api.side import Side
from cosmian_secure_computation_client.api.common import CommonAPI


class ResultConsumerAPI(CommonAPI):
    def __init__(self, token: str) -> None:
        super().__init__(Side.ResultConsumer, token)

    def fetch_results(self, computation_uuid: str) -> Optional[bytes]:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/computations/{computation_uuid}/results",
            headers={
                "Authorization": f"Bearer {self.access_token()}",
            },
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return bytes.fromhex(resp.json()["message"])
