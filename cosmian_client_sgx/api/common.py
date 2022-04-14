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

        content: Dict[str, str] = resp.json()
        return content["access_token"]

    def register(self, computation_id: str, public_key: str) -> Dict[str, str]:
        resp: requests.Response = self.session.post(
            url=f"{self.url}/computations/{computation_id}/register",
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

        return resp.json()

    def get_computation(self, computation_id: str) -> Computation:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/computations/{computation_id}",
            headers={
                "Authorization": f"Bearer {self.access_token()}",
            },
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return Computation.from_json_dict(resp.json())

    def status(self) -> Dict[str, Dict[Side, List[bytes]]]:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/enclave/status",
            auth=self.auth
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )
        content: Dict[str, Dict[str, List[bytes]]] = resp.json()

        return {
            "pub_keys": {
                Side[key]: [bytes(value) for value in values]
                for key, values in content["pub_keys"].items()
            }
        }


    def key_finalize(self) -> Dict[str, Union[Side, bytes]]:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/enclave/key/finalize",
            auth=self.auth
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        content: Dict[str, Union[str, List[int]]] = resp.json()

        self.remote_pubkey = bytes(content["pub_key"])

        return {
            "pub_key": self.remote_pubkey,
            "side": Side[content["side"]],
            "isvEnclaveQuote": content["isvEnclaveQuote"]
        }

    def key_provisioning(self, computation_uuid: str, sealed_symetric_key: bytes) -> Dict[str, str]:
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

        return resp.json()

    def remote_attestation(self, quote: Dict[str, str]) -> bool:
        resp: requests.Response = self.session.post(
            url=f"{self.url}/enclave/remote_attestation",
            json=quote,
            auth=self.auth
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        pems = unquote(resp.headers["x-iasreport-signing-certificate"])
        m = re.findall(
            r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
            pems,
            flags=re.DOTALL
        )
        intel_cert = x509.load_pem_x509_certificate(m[0].encode("utf-8"))
        intel_pubkey = intel_cert.public_key()

        intel_pubkey.verify(
            resp.headers["x-iasreport-signature"].encode("utf-8"),
            resp.content,
            hashes.SHA256()
        )

        return True

    def get_quote(self) -> Dict[str, str]:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/enclave/quote",
            auth=self.auth
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )
        return resp.json()

    def reset(self) -> bool:
        resp: requests.Response = self.session.delete(
            url=f"{self.url}/enclave/reset",
            auth=self.auth
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return "success" in resp.json()
