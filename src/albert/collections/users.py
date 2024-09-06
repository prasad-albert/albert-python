from collections.abc import Generator, Iterator

from albert.albert_session import AlbertSession
from albert.collections.base import BaseCollection
from albert.resources.users import User


class UserCollection(BaseCollection):
    def __init__(self, *, session: AlbertSession):
        """
        Initializes the UserCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_url = "/api/v3/users"

    def _list_generator(
        self,
        *,
        text: str | None = None,
        search_name: bool | None = None,
        search_email: bool | None = None,
        offset: int | None = None,
        limit: int = 50,
    ) -> Generator[User, None, None]:
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
            response = self.session.get(self.base_url + "/search", params=params)
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
        *,
        text: str | None = None,
        search_name: bool | None = None,
        search_email: bool | None = None,
    ) -> Iterator[User]:
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
        return self._list_generator(text=text, search_email=search_email, search_name=search_name)

    def get_by_id(self, *, user_id: str) -> User | None:
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
        response = self.session.get(url)
        user = User(**response.json())
        return user

    def create(self, *, user: User) -> User:
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
        response = self.session.post(self.base_url, json=payload)
        user = User(**response.json())
        return user

    def delete(self, *, user_id: str) -> bool:
        url = f"{self.base_url}/{user_id}"
        response = self.session.delete(url)
        return True
