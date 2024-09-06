from albert.collections.base_collection import BaseCollection
from typing import List
from albert.resources.roles import Role


class RoleCollection(BaseCollection):
    def __init__(self,*, session):
        """
        Initializes the RoleCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_url = "/api/v3/acl/roles"

    def list(self, *, params={}) -> List[Role]:
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
        response = self.session.get(self.base_url, params=params)
        role_data = response.json().get("Items", [])
        return [Role(**r) for r in role_data]
