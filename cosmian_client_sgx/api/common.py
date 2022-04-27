"""cosmian_client_sgx.api.common module."""

import base64
import os
from typing import Optional, Dict, Any

from cryptography import x509
import requests
from cryptography.hazmat.primitives.serialization import (Encoding,
                                                          PublicFormat)
import jwt

from cosmian_client_sgx.crypto.context import CryptoContext
from cosmian_client_sgx.api.side import Side
from cosmian_client_sgx.api.computations import Computation
from cosmian_client_sgx.util.base64url import base64url_encode, base64url_decode


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

    def key_provisioning(self, computation_uuid: str, sealed_symmetric_key: bytes) -> Computation:
        resp: requests.Response = self.session.post(
            url=f"{self.url}/computations/{computation_uuid}/key/provisioning",
            json={
                "role": str(self.side),
                "sealed_symmetric_key": list(sealed_symmetric_key),
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

    @staticmethod
    def microsoft_azure_attestation(quote: str, enclave_held_data: Optional[bytes]) -> Dict[str, Any]:
        raw_quote: bytes = base64.b64decode(quote)
        payload: Dict[str, Any] = {"quote": base64url_encode(raw_quote)}

        if enclave_held_data is not None:
            payload["runtimeData"] = {
                "data": base64url_encode(enclave_held_data),
                "dataType": "Binary"
            }

        response = requests.post(
            url="https://sharedneu.neu.attest.azure.net/attest/SgxEnclave",
            params={
                "api-version": "2020-10-01"
            },
            json=payload
        )

        return response.json()

    @staticmethod
    def microsoft_signing_certs() -> Dict[str, Any]:
        response = requests.get(
            url="https://sharedneu.neu.attest.azure.net/certs",
        )

        return response.json()

    @staticmethod
    def verify_jws(jws: str, jwks: Dict[str, Any]) -> Dict[str, Any]:
        header = jwt.get_unverified_header(jws)
        kid = header["kid"]

        for jwk in jwks["keys"]:
            if jwk["kid"] == kid:
                x5c, *_ = jwk["x5c"]
                assert jwk["kty"] == "RSA"
                raw_cert: bytes = base64url_decode(x5c)
                cert = x509.load_der_x509_certificate(raw_cert)
                return jwt.decode(
                    jws,
                    cert.public_key().public_bytes(
                        Encoding.PEM,
                        PublicFormat.PKCS1
                    ),
                    algorithms="RS256"
                )

        raise Exception("can't verify MAA signature")

    def remote_attestation(self, quote: str) -> Dict[str, Any]:
        token = self.microsoft_azure_attestation(quote=quote, enclave_held_data=None)["token"]
        certs: Dict[str, Any] = self.microsoft_signing_certs()

        return self.verify_jws(token, certs)
