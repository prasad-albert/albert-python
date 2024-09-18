import builtins
from collections.abc import Generator, Iterator

from albert.collections.base import BaseCollection, OrderBy
from albert.resources.custom_templates import CustomTemplate
from albert.session import AlbertSession


class CustomTemplatesCollection(BaseCollection):
    # _updatable_attributes = {"symbol", "synonyms", "category"}

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the UnitCollection with the provided session.

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
        """
        Lists unit entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of units to return, by default 50.
        name : Optional[str], optional
            The name of the unit to filter by, by default None.
        category : Optional[UnitCategory], optional
            The category of the unit to filter by, by default None.
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING.
        exact_match : bool, optional
            Whether to match the name exactly, by default False.
        start_key : Optional[str], optional
            The starting point for the next set of results, by default None.

        Returns
        -------
        Generator
            A generator of Unit objects.
        """
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
                # print(t["albertId"])
                try:
                    # print(t)
                    # Like InventoryItems I need to add a get here.
                    yield self.get_by_id(id=t["albertId"])
                    # yield CustomTemplate(**t)
                except:
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
        return self._list_generator(name=name)

    def get_by_id(self, *, id):
        url = f"{self.base_url}/{id}"
        response = self.session.get(url)
        # print(response.json())
        # print("----")
        template = CustomTemplate(**response.json())
        return template
