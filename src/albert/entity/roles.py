from albert.base_entity import BaseAlbertModel
from albert.base_collection import BaseCollection
from pydantic import Field
from typing import Any, List, Optional
import requests


class Role(BaseAlbertModel):
    id: str = Field(alias="albertId")
    name: str
    policies: Optional[List[Any]] = Field(None)
    tenant: str


class RoleCollection(BaseCollection):
    def __init__(self, client):
        """
        Initializes the TagCollection with the provided client.

        Parameters
        ----------
        client : Any
            The Albert client instance.
        """
        super().__init__(client=client)
        self.tag_cache = {}
        self.base_url = f"{self.client.base_url}/api/v3/acl/roles"

    def list(self, params={}) -> List[Role]:
        """Lists the available roles

        Parameters
        ----------
        params : dict, optional
            _description_, by default {}

        Returns
        -------
        List
            List of available Roles
        """
        response = requests.get(
            self.base_url, headers=self.client.headers, params=params
        )
        if response.status_code != 200:
            self.handle_api_error(response=response)
            return None
        role_data = response.json().get("Items", [])
        return [Role(**r) for r in role_data]
