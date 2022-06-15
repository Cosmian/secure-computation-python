"""cosmian_secure_computation_client.api.computation_owner module."""

from pathlib import Path
import tempfile
from typing import Optional, Dict, List, Tuple
import os

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from cosmian_secure_computation_client.api.auth import Token
from cosmian_secure_computation_client.api.side import Side
from cosmian_secure_computation_client.api.common import CommonAPI
from cosmian_secure_computation_client.api.computations import Computation


class ComputationOwnerAPI:
    def __init__(self, token: str) -> None:
        self.url: str = os.getenv('COSMIAN_BASE_URL', default="https://backend.cosmian.com")
        self.session: requests.Session = requests.Session()
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=0.3,
            status_forcelist=(502, 503), # BadGateway from Nginx / Temporary unavailable
            allowed_methods=None,
            raise_on_status=False,
            raise_on_redirect=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.token = Token(self.session, self.url, token)

    def create_computation(self, name: str, owner_public_key: str, code_provider_email: str, data_providers_emails: List[str], result_consumers_emails: List[str]) -> Computation:
        resp: requests.Response = self.session.post(
            url=f"{self.url}/computations",
            json={
                "name": name,
                "code_provider_email": code_provider_email,
                "data_providers_emails": data_providers_emails,
                "result_consumers_emails": result_consumers_emails,
                "owner_public_key": owner_public_key,
            },
            headers={
                "Authorization": f"Bearer {self.token.access_token}",
            },
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return Computation.from_json_dict(resp.json())

    def approve_participants(self, computation_uuid: str, signature: str) -> Computation:
        resp: requests.Response = self.session.post(
            url=f"{self.url}/computations/{computation_uuid}/approve/participants",
            json={
                "signature": signature,
            },
            headers={
                "Authorization": f"Bearer {self.token.access_token}",
            },
        )

        if not resp.ok:
            raise Exception(
                f"Unexpected response ({resp.status_code}): {resp.content}"
            )

        return Computation.from_json_dict(resp.json())
