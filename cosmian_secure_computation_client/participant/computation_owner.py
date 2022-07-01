"""cosmian_secure_computation_client.participant.computation_owner module."""

from typing import List, Tuple
import os

import requests

from cosmian_secure_computation_client.api.provider import (create_computation,
                                                            computations)
from cosmian_secure_computation_client.api.auth import Connection
from cosmian_secure_computation_client.computations import Computation
from cosmian_secure_computation_client.util.mnemonic import random_words


class ComputationOwnerAPI:
    """ComputationOwnerAPI class.

    Parameters
    ----------
    token : str
        Refresh token to authenticate with Cosmian's backend.

    Attributes
    ----------
    conn : Connection
        Manage authentication to Cosmian's backend.

    """

    def __init__(self, token: str) -> None:
        """Init constructor of ComputationOwnerAPI."""
        self.conn = Connection(
            base_url=os.getenv("COSMIAN_BASE_URL",
                               default="https://backend.cosmian.com"),
            refresh_token=token
        )

    @staticmethod
    def random_words() -> Tuple[str, str, str]:
        """Generate 3 random words to be used as pre-shared secret."""
        return random_words()

    def create_computation(self,
                           name: str,
                           code_provider_email: str,
                           data_providers_emails: List[str],
                           result_consumers_emails: List[str]) -> Computation:
        """Invite participants to a new computation named `name`."""
        r: requests.Response = create_computation(
            conn=self.conn,
            name=name,
            cp_mail=code_provider_email,
            dps_mail=data_providers_emails,
            rcs_mail=result_consumers_emails
        )

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

        return Computation.from_json_dict(r.json())

    def get_computations(self) -> List[Computation]:
        """Retriveve all computations related to your account."""
        r: requests.Response = computations(conn=self.conn)

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

        return [Computation.from_json_dict(dct) for dct in r.json()]
