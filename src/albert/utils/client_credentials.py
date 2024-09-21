import os
from typing import Union

from pydantic import BaseModel, SecretStr


class ClientCredentials(BaseModel):
    """Client authentication information for the Albert API."""

    id: str
    secret: SecretStr

    @classmethod
    def from_env(cls) -> Union["ClientCredentials", None]:
        """Read `ClientCredentials` from the environment.

        Returns `None` if the `ALBERT_CLIENT_ID` and `ALBERT_CLIENT_SECRET` environment variables
        are not defined.
        """
        client_id = os.getenv("ALBERT_CLIENT_ID")
        client_secret = os.getenv("ALBERT_CLIENT_SECRET")
        if client_id is not None and client_secret is not None:
            return cls(id=client_id, secret=client_secret)
