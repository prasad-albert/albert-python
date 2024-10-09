from collections.abc import Generator

from albert.collections.base import BaseCollection
from albert.resources.lists import ListItem, ListItemCategory
from albert.session import AlbertSession


class ListsCollection(BaseCollection):
    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the TagCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_path = f"/api/{ListsCollection._api_version}/lists"

    def _list_generator(
        self,
        *,
        limit: int = 100,
        # order_by: OrderBy = OrderBy.DESCENDING,
        names: list[str] = None,
        category: ListItemCategory = None,
        list_type: str = None,
        start_key: str = None,
    ) -> Generator[ListItem, None, None]:
        """
        Generates a list of list entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of list entities to return.
        order_by : OrderBy, optional
            The order in which to return list entities.
        name : str, optional
            The name of the list entity to retrieve.
        exact_match : bool, optional
            Whether to perform an exact match on the list name.

        Yields
        ------
        List
            A list entity.
        """
        params = {
            "limit": limit,
            # "order": order_by.value,
            "startKey": start_key,
            "name": names,
            "category": category,
            "listType": list_type,
        }
        params = {k: v for k, v in params.items() if v is not None}
        while True:
            response = self.session.get(self.base_path, params=params)
            response_json = response.json()
            items = response_json.get("Items", [])
            if items == []:
                break
            for list_data in items:
                yield ListItem(**list_data)
            start_key = response_json.get("lastKey")
            if not start_key or len(items) < limit:
                break
            params["startKey"] = start_key

    def list(
        self,
        *,
        limit: int = 100,
        # order_by: OrderBy = OrderBy.DESCENDING,
        names: list[str] = None,
        category: ListItemCategory = None,
        list_type: str = None,
    ) -> list[ListItem]:
        """
        Lists list entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of list entities to return.
        order_by : OrderBy, optional
            The order in which to return list entities.
        name : str, optional
            The name of the list entity to retrieve.
        exact_match : bool, optional
            Whether to perform an exact match on the list name.

        Returns
        -------
        List
            A list of list entities.
        """
        if isinstance(names, str):
            names = [names]
        if isinstance(category, ListItemCategory):
            category = category.value
        return list(
            self._list_generator(limit=limit, names=names, category=category, list_type=list_type)
        )

    def get_by_id(self, *, id: str) -> ListItem:
        """
        Retrieves a list entity by its ID.

        Parameters
        ----------
        id : str
            The ID of the list entity to retrieve.

        Returns
        -------
        List
            A list entity.
        """
        response = self.session.get(f"{self.base_path}/{id}")
        return ListItem(**response.json())

    def create(self, *, list_item: ListItem) -> ListItem:
        """
        Creates a list entity.

        Parameters
        ----------
        list_item : ListItem
            The list entity to create.

        Returns
        -------
        List
            The created list entity.
        """
        response = self.session.post(
            self.base_path, json=list_item.model_dump(by_alias=True, exclude_none=True)
        )
        return ListItem(**response.json())

    def get_matching_item(self, *, name: str, list_type):
        for list_item in self.list(names=[name], list_type=list_type):
            if list_item.name.lower() == name.lower():
                return list_item
        return None
