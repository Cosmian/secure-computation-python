"""cosmian_secure_computation_client.participant.result_consumer module."""

from typing import Optional

import requests

from cosmian_secure_computation_client.api.provider import download_result
from cosmian_secure_computation_client.participant.base import BaseAPI
from cosmian_secure_computation_client.side import Side
from cosmian_secure_computation_client.crypto.context import CryptoContext


class ResultConsumerAPI(BaseAPI):
    """ResultConsumerAPI class derived from BaseAPI.

    Parameters
    ----------
    token : str
        Refresh token to authenticate with Cosmian's backend.
    ctx : CryptoContext
        Context with cryptographic secrets.

    """

    def __init__(self, token: str, ctx: CryptoContext) -> None:
        """Init constructor of ResultConsumerAPI."""
        super().__init__(Side.ResultConsumer, token, ctx)

    def fetch_result(self, computation_uuid: str) -> Optional[bytes]:
        """Download the result of the computation if available."""
        r: requests.Response = download_result(
            conn=self.conn,
            computation_uuid=computation_uuid
        )

        if r.status_code == requests.codes["accepted"]:
            return None

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

        result: bytes
        try:
            # backward compatibility with old API
            result = bytes.fromhex(r.json()["message"])
        except requests.JSONDecodeError:
            result = r.content

        return self.ctx.decrypt(result)
