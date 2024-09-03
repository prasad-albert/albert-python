from albert.base_collection import BaseCollection
from albert.base_entity import BaseAlbertModel
import requests
from typing import Union, Generator, Optional, List
from pydantic import Field
from albert.entity.locations import Location
from albert.entity.roles import Role


class User(BaseAlbertModel):
    """Represents a User on the Albert Platform"""

    id: Optional[str] = Field(None, alias="albertId")
    name: str
    location: Optional[Union[str, Location]] = Field(None)
    email: str = Field(default=None, alias="email")
    roles: List[Role] = Field(default=[])


class UserCollection(BaseCollection):
    def __init__(self, client):
        """
        Initializes the UserCollection with the provided client.

        Parameters
        ----------
        client : Any
            The Albert client instance.
        """
        super().__init__(client=client)
        self.base_url = f"{self.client.base_url}/api/v3/users"

    def _list_generator(
        self,
        text: Optional[str] = None,
        search_name: Optional[bool] = None,
        search_email: Optional[bool] = None,
        offset: Optional[int] = None,
        limit: int = 50,
    ) -> Generator:
        params = {"limit": limit, "status": "active"}
        if text:
            fields = []
            params["text"] = text
            if search_name:
                fields.append("name")
            if search_email:
                fields.append("mail")
            if fields != []:
                params["searchFields"] = fields
            if offset:
                params["offset"] = offset
        while True:
            # status=active&limit=50&text=Lenore&searchFields=name
            response = requests.get(
                self.base_url + "/search", params=params, headers=self.client.headers
            )
            if response.status_code != 200:
                self.handle_api_error(response=response)
                break
            user_data = response.json().get("Items", [])
            if not user_data or user_data == []:
                break
            for u in user_data:
                yield User(**u)
            offset = response.json().get("offset")
            if not offset or len(user_data) < limit:
                break
            params["offset"] = offset

    def list(
        self,
        text: Optional[str] = None,
        search_name: Optional[bool] = None,
        search_email: Optional[bool] = None,
    ) -> Generator[User, None, None]:
        """Lists Users based on criteria

        Parameters
        ----------
        text : Optional[str], optional
            text to search against, by default None
        search_name : Optional[bool], optional
            Name to search against, by default None
        search_email : Optional[bool], optional
            email to search against, by default None

        Returns
        -------
        Generator
            Generator of matching Users or None
        """
        return self._list_generator(
            text=text, search_email=search_email, search_name=search_name
        )

    def get_by_id(self, user_id) -> Union[User, None]:
        """
        Retrieves a User by its ID.

        Parameters
        ----------
        user_id : str
            The ID of the user to retrieve.

        Returns
        -------
        User
            The User object if found, None otherwise.
        """
        url = f"{self.base_url}/{user_id}"
        response = requests.get(url, headers=self.client.headers)
        if response.status_code != 200:
            self.handle_api_error(response=response)
        user = User(**response.json())
        return user

    def create(self, user: User) -> User:
        """Create a new User

        Parameters
        ----------
        user : User
            The user to create

        Returns
        -------
        User
            The created User
        """

        # May need to rehydrate location?
        payload = {
            "name": user.name,
            "email": user.email,
            "Roles": [{"id": r.tenant + "#" + r.id for r in user.roles}],
            "Location": {"id": user.location.id},
            "userClass": "standard",
        }

        # build and run query
        response = requests.post(
            self.base_url, headers=self.client.headers, json=payload
        )
        if response.status_code != 201:
            self.handle_api_error(response=response)
        user = User(**response.json())
        return user

    def delete(self, user_id) -> bool:
        url = f"{self.base_url}/{user_id}"
        response = requests.delete(url, headers=self.client.headers)
        if response.status_code != 204:
            self.handle_api_error(response=response)
            return False
        return True
