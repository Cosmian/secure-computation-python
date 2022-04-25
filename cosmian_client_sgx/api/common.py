"""cosmian_client_sgx.api.common module."""

import re
from typing import Optional, Dict, Union, List, Tuple

from urllib.parse import unquote
from cryptography import x509
from cryptography.hazmat.primitives import hashes
import requests
import os

from cosmian_client_sgx.crypto.context import CryptoContext
from cosmian_client_sgx.api.side import Side
from cosmian_client_sgx.api.computations import Computation


class CommonAPI(CryptoContext):
    def __init__(self, side: Side, token: str) -> None:
        assert side != Side.Enclave, "Can't control Enclave keypair!"
        self.side: Side = side
        self.session: requests.Session = requests.Session()
        self.url: str = os.getenv('COSMIAN_BASE_URL', default="https://backend.cosmian.com")
        self.token = token
        super().__init__()

    def access_token(self) -> str: 
        resp: requests.Response = self.session.post(
            url=f"{self.url}/oauth/token",
            json={
                "type": 'refresh_token',
                "refresh_token": self.token,
            },
        )

        if not resp.ok:
            raise Exception(
                f"Invalid token. Please check that your token."
            )

        content: Dict[str, str] = resp.json()
        return content["access_token"]

    def register(self, computation_uuid: str, public_key: str) -> Computation:
        resp: requests.Response = self.session.post(
            url=f"{self.url}/computations/{computation_uuid}/register",
            json={
                "public_key": public_key,
                "side": str(self.side),
            },
            headers={
                "Authorization": f"Bearer {self.access_token()}",
            },
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return Computation.from_json_dict(resp.json())

    def get_computation(self, computation_uuid: str) -> Computation:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/computations/{computation_uuid}",
            headers={
                "Authorization": f"Bearer {self.access_token()}",
            },
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return Computation.from_json_dict(resp.json())

    def key_provisioning(self, computation_uuid: str, sealed_symetric_key: bytes) -> Computation:
        resp: requests.Response = self.session.post(
            url=f"{self.url}/computations/{computation_uuid}/key/provisioning",
            json={
                "role": str(self.side),
                "sealed_symetric_key": list(sealed_symetric_key),
            },
            headers={
                "Authorization": f"Bearer {self.access_token()}",
            },
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return Computation.from_json_dict(resp.json())
