from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import requests

import albert
from albert.utils.exceptions import handle_api_error

EXPIRATION_BUFFER: timedelta = timedelta(minutes=1)


def get_token_expiration(expires_in: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=expires_in)


class AlbertSession(requests.Session):
    """
    A session that has a base URL, which is prefixed to all request URLs.

    Parameters
    ----------
    base_url : str
        The base URL to prefix to all requests.
    """

    def __init__(
        self,
        *,
        base_url: str,
        token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        super().__init__()
        self.base_url = base_url
        self.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"albert-SDK V.{albert.__version__}",
            }
        )

        self._client_id = client_id
        self._client_secret = client_secret

        self._access_token: str = token
        self._access_token_expiration: datetime | None = datetime.now(timezone.utc)

        if self.has_client_credentials:
            self._client_login()
        elif self._access_token is None:
            raise ValueError("Either token or client credentials must be specified.")
        self._update_headers()

    @property
    def has_client_credentials(self) -> bool:
        return self._client_id is not None and self._client_secret is not None

    def _set_bearer_header(self) -> None:
        self.headers["Authorization"] = f"Bearer {self._access_token}"

    def _client_login(self) -> None:
        path = "/api/v3/login/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        response = self._send_request("POST", path, data=payload)
        data = response.json()
        self._access_token = data["access_token"]
        self._access_token_expiration = get_token_expiration(data["expires_in"])

    def _requires_refresh(self) -> bool:
        expire_time = self._access_token_expiration - EXPIRATION_BUFFER
        return datetime.now(timezone.utc) > expire_time

    def _send_request(self, method: str, path: str, *args, **kwargs) -> requests.Response:
        full_url = urljoin(self.base_url, path) if not path.startswith("http") else path
        response = super().request(method, full_url, *args, **kwargs)
        handle_api_error(response)
        return response

    def request(self, method: str, path: str, *args, **kwargs) -> requests.Response:
        if self._requires_refresh() and self.has_client_credentials:
            self._client_login()
        return self._send_request(method, path, args, kwargs)
