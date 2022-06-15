"""cosmian_secure_computation_client.api.token module."""

import requests


class Token:
    def __init__(self, session: requests.Session, url: str, token: str) -> None:
        self.session: requests.Session = session
        self.url: str = url
        self.refresh_token: str = token
        self.access_token: str = Token.new_access_token(
            self.session,
            self.url,
            self.refresh_token
        )

    @staticmethod
    def new_access_token(session: requests.Session, url: str, refresh_token: str) -> str:
        r: requests.Response = session.post(
            url=f"{url}/oauth/token",
            json={
                "type": 'refresh_token',
                "refresh_token": refresh_token,
            }
        )

        if not r.ok:
            raise Exception(
                f"Cannot fetch access token! "
                f"Status {r.status_code}: {r.content}"
            )

        return r.json()["access_token"]

    def refresh(self) -> None:
        self.access_token = Token.new_access_token(
            self.session,
            self.url,
            self.refresh_token
        )