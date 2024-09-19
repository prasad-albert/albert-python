import builtins
from collections.abc import Generator, Iterator

from albert.collections.base import BaseCollection
from albert.resources.custom_templates import CustomTemplate
from albert.session import AlbertSession
from albert.utils.exceptions import ForbiddenError


class CustomTemplatesCollection(BaseCollection):
    # _updatable_attributes = {"symbol", "synonyms", "category"}

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the CustomTemplatesCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_url = "/api/v3/customtemplates"

    def _list_generator(
        self,
        *,
        name: str | builtins.list[str] | None = None,
        start_key: str | None = None,
        limit: int = 50,
    ) -> Generator[CustomTemplate, None, None]:
        params = {
            "limit": limit,
        }
        if name:
            params["name"] = name if isinstance(name, list) else [name]
        if start_key:
            params["startKey"] = start_key

        while True:
            response = self.session.get(self.base_url + "/search", params=params)
            templates = response.json().get("Items", [])
            if not templates or templates == []:
                break
            for t in templates:
                try:
                    # Like InventoryItems I need to add a get here.
                    # May want to swap to lazy-load later for speed
                    yield self.get_by_id(id=t["albertId"])
                except ForbiddenError:
                    print("no access!!")
                    continue
            start_key = response.json().get("lastKey")
            if not start_key:
                break
            params["startKey"] = start_key

    def list(
        self,
        *,
        name: str | builtins.list[str] | None = None,
    ) -> Iterator[CustomTemplate]:
        """lists Custom Templates

        Parameters
        ----------
        name : str | builtins.list[str] | None, optional
            Name to search on, by default None

        Yields
        ------
        Iterator[CustomTemplate]
            An Iterator with CustomTemplate Objects
        """
        return self._list_generator(name=name)

    def get_by_id(self, *, id) -> CustomTemplate:
        """Get a Custom Template by ID

        Parameters
        ----------
        id : str
            id of the custom template

        Returns
        -------
        CustomTemplate
            The CutomTemplate with the provided ID (or None if not found)
        """
        url = f"{self.base_url}/{id}"
        response = self.session.get(url)
        template = CustomTemplate(**response.json())
        return template
