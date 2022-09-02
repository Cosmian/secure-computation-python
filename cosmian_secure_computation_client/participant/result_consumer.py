"""cosmian_secure_computation_client.participant.result_consumer module."""

import time
from typing import Optional, cast

import requests

from cosmian_secure_computation_client.api.provider import download_result
from cosmian_secure_computation_client.computations import EnclaveStateType
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
        if ctx.side != Side.ResultConsumer:
            raise Exception(
                f"Can't create {self.__class__} with CryptoContext side {ctx.side}"
            )
        super().__init__(token, ctx)

    def fetch_result(self, computation_uuid: str) -> Optional[bytes]:
        """Download the result of the computation if available."""
        self.log.debug("Result available")
        r: requests.Response = download_result(
            conn=self.conn, computation_uuid=computation_uuid)

        if r.status_code == requests.codes["accepted"]:
            return None

        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        encrypted_result: bytes
        try:
            # backward compatibility with old API
            encrypted_result = bytes.fromhex(r.json()["message"])
        except requests.JSONDecodeError:
            encrypted_result = r.content

        self.log.debug("Decrypt result...")
        result: bytes = self.ctx.decrypt(encrypted_result)
        self.log.info("Result received and successfully decrypted")

        return result

    def wait_result(self,
                    computation_uuid: str,
                    sleep_duration: int = 30) -> bytes:
        """Wait for the result to be available and fetch it."""
        self.log.info("Waiting for result...")
        status = self.get_status(computation_uuid)
        while not status.has_result():
            time.sleep(sleep_duration)
            status = self.get_status(computation_uuid)

        if status.enclave_state == EnclaveStateType.Failure:
            raise Exception("Execution failed: "
                            f"{status.enclave_state}")

        return cast(bytes, self.fetch_result(computation_uuid))
