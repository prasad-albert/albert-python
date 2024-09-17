import requests

import albert
from albert.utils.exceptions import handle_api_error


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

        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        self.has_client_credentials = self.client_id and self.client_secret

        if self.token is None and self.has_client_credentials:
            self._refresh_token()
        elif self.token is None:
            raise ValueError("Either token or client credentials must be specified.")

    def _refresh_token(self) -> None:
        pass

    def _update_headers(self) -> dict[str, str]:
        self.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": f"albert-SDK V.{albert.__version__}",
            }
        )

    def request(self, method: str, url: str, *args, **kwargs):
        # Prefix the base URL if not a fully hard-coded URL
        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        response = super().request(method, full_url, *args, **kwargs)
        handle_api_error(response=response)
        return response
