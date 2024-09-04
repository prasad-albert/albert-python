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
    def __init__(self, session):
        """
        Initializes the RoleCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_url = "/api/v3/acl/roles"

    def list(self, params={}) -> List[Role]:
        """Lists the available Roles

        Parameters
        ----------
        params : dict, optional
            _description_, by default {}

        Returns
        -------
        List
            List of available Roles
        """
        response = self.session.get(
            self.base_url, params=params
        )
        if response.status_code != 200:
            self.handle_api_error(response=response)
            return None
        role_data = response.json().get("Items", [])
        return [Role(**r) for r in role_data]
