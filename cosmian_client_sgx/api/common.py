"""cosmian_client_sgx.api.common module."""

import re
from typing import Optional, Dict, Union, List
from urllib.parse import unquote

from cosmian_client_sgx.crypto.context import CryptoContext
from cosmian_client_sgx.api.side import Side

import requests


class CommonAPI(CryptoContext):
    def __init__(self,
                 side: Side,
                 hostname: str,
                 port: Optional[int],
                 ssl: bool = False) -> None:
        assert side != Side.Enclave, "Can't control Enclave keypair!"
        self.side: Side = side
        self.session: requests.Session = requests.Session()
        self.url: str = (f"{'https://' if ssl else 'http://'}"
                         f"{f'{hostname}:{port}' if port else f'{hostname}'}")
        super().__init__()

    def status(self) -> Dict[str, Dict[Side, bytes]]:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/enclave/status")

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )
        content = resp.json()

        return {
            "pub_keys": {
                Side[key]: [bytes(value) for value in values]
                for key, values in content["pub_keys"].items()
            }
        }

    def handshake(self) -> Dict[str, Union[Side, bytes]]:
        resp: requests.Response = self.session.post(
            url=f"{self.url}/enclave/handshake",
            json={
                "pub_key": list(self.pubkey),
                "side": str(self.side)
            })

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )
        content: Dict[str, Union[str, List[int]]] = resp.json()
        self.remote_pubkey = bytes(content["pub_key"])
        self.key_exchange(self.remote_pubkey)

        return {"pub_key": self.remote_pubkey, "side": Side[content["side"]]}

    def remote_attestation(self, quote: Dict[str, str]) -> bool:
        resp: requests.Response = self.session.post(
            url=f"{self.url}/enclave/remote_attestation",
            json=quote
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )
        # print(resp.headers)
        # print(resp.json())
        pems = unquote(resp.headers["x-iasreport-signing-certificate"])
        m = re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", pems, flags=re.DOTALL)
        print(m)
        # print(x509.load_pem_x509_certificate(m[0].encode("utf-8")))
        return True

    def get_quote(self) -> Dict[str, str]:
        resp: requests.Response = self.session.get(
            url=f"{self.url}/enclave/quote")

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )
        return resp.json()
