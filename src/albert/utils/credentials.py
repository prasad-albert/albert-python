import os
from datetime import datetime, timedelta, timezone
from typing import Literal, Union
from urllib.parse import urljoin

import jwt
import requests
from pydantic import SecretStr

from albert.utils.types import BaseAlbertModel


class ClientCredentials(BaseAlbertModel):
    """Client authentication credentials for the Albert API."""

    id: str
    secret: SecretStr

    @classmethod
    def from_env(
        cls,
        *,
        client_id_env: str = "ALBERT_CLIENT_ID",
        client_secret_env: str = "ALBERT_CLIENT_SECRET",
    ) -> Union["ClientCredentials", None]:
        """Read `ClientCredentials` from the environment.

        Returns None if the `client_id_env` and `client_secret_env` environment variables
        are not defined.

        Parameters
        ----------
        client_id_env : str
            Name of the environment variable containing the client ID
            (defaults to "ALBERT_CLIENT_ID")
        client_secret_env : str
            Name of the environment variable containing the client secret
            (defaults to "ALBERT_CLIENT_SECRET")

        Returns
        -------
        ClientCredentials | None
            The client credentials obtained from the environment, if present.
        """
        client_id = os.getenv(client_id_env)
        client_secret = os.getenv(client_secret_env)
        if client_id is not None and client_secret is not None:
            return cls(id=client_id, secret=client_secret)


class CreateOauthToken(BaseAlbertModel):
    """Model for creating an OAuth token."""

    grant_type: Literal["client_credentials"] = "client_credentials"
    client_id: str
    client_secret: str


class CredentialsManager:
    """Helper to manage refreshing an access token from OAuth endpoint."""

    oauth_path: str = "/api/v3/login/oauth/token"

    def __init__(self, base_url: str, client_credentials: ClientCredentials):
        self.oauth_url = urljoin(base_url, self.oauth_path)
        self.client_credentials = client_credentials

        self._access_token: str | None = None
        self._refresh_time: datetime | None = None

    @staticmethod
    def _get_refresh_time(token: str, *, buffer: timedelta | None) -> datetime:
        claims = jwt.decode(token, options={"verify_signature": False})
        try:
            exp_time = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
        except (OSError, ValueError):
            # exp is in millis, not seconds, so datetime fails
            exp_time = datetime.fromtimestamp(claims["exp"] / 1000, tz=timezone.utc)
        buffer = buffer or timedelta(seconds=0)
        return exp_time - buffer

    def _refresh_token(self) -> str:
        # TODO: Implement using refresh_token once it is working
        payload = CreateOauthToken(
            client_id=self.client_credentials.id,
            client_secret=self.client_credentials.secret.get_secret_value(),
        )
        response = requests.post(
            self.oauth_url,
            data=payload.model_dump(mode="json"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = response.json()["access_token"]
        self._access_token = token
        self._refresh_time = self._get_refresh_time(token, buffer=timedelta(minutes=1))

    def _requires_refresh(self) -> bool:
        return (
            self._access_token is None
            or self._refresh_time is None
            or datetime.now(timezone.utc) > self._refresh_time
        )

    def get_access_token(self) -> str:
        if self._requires_refresh():
            self._refresh_token()
        return self._access_token
