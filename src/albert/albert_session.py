import requests

class AlbertSession(requests.Session):
    """
    A session that has a base URL, which is prefixed to all request URLs.

    Parameters
    ----------
    base_url : str
        The base URL to prefix to all requests.
    """

    def __init__(self, base_url: str = '', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        # Prefix the base URL if not a fully hard-coded URL
        full_url = f'{self.base_url}{url}' if not url.startswith('http') else url
        return super().request(method, full_url, *args, **kwargs)
