from collections.abc import Generator, Iterator

from albert.collections.base import BaseCollection, OrderBy
from albert.resources.data_templates import DataTemplate
from albert.session import AlbertSession

# from albert.utils.exceptions import NotFoundError


class DataTemplateCollection(BaseCollection):
    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{DataTemplateCollection._api_version}/datatemplates"

    # def _list_generator(
    #     self,
    #     *,
    #     limit: int = 50,
    #     order_by: OrderBy = OrderBy.DESCENDING,
    #     name: str | list[str] = None,
    #     exact_match: bool = True,
    #     start_key: str | None = None,
    # ) -> Generator[DataTemplate, None, None]:
    #     """
    #     Lists tag entities with optional filters.

    #     Parameters
    #     ----------
    #     limit : int, optional
    #         The maximum number of tags to return, by default 50.
    #     order_by : OrderBy, optional
    #         The order by which to sort the results, by default OrderBy.DESCENDING.
    #     name : Union[str, None], optional
    #         The name of the tag to filter by, by default None.
    #     exact_match : bool, optional
    #         Whether to match the name exactly, by default True.
    #     start_key : Optional[str], optional
    #         The starting point for the next set of results, by default None.

    #     Returns
    #     -------
    #     Generator
    #         A generator of Tag objects.
    #     """
    #     params = {"limit": limit, "orderBy": order_by.value}
    #     if name:
    #         params["name"] = name if isinstance(name, list) else [name]
    #         params["exactMatch"] = str(exact_match).lower()
    #     if start_key:  # pragma: no cover
    #         params["startKey"] = start_key

    #     while True:
    #         try:
    #             response = self.session.get(f"{self.base_path}/search", params=params)
    #         except NotFoundError:
    #             break
    #         data = response.json().get("Items", [])
    #         if not data or data == []:
    #             break
    #         for t in data:
    #             this_dt = DataTemplate(**t)
    #             yield this_dt
    #         start_key = response.json().get("lastKey")
    #         if not start_key:
    #             break
    #         params["startKey"] = start_key

    def _list_generator(
        self,
        *,
        limit: int = 25,
        offset: int | None = None,
        name: str | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Generator[DataTemplate, None, None]:
        """NOTE: WE could add more allowed filters here, but for now, this is all we need."""
        params = {
            "sortBy": "createdAt",
            "order": order_by.value,
            "limit": str(limit),
        }
        if offset:  # pragma: no cover
            params["offset"] = offset
        if name:
            params["text"] = name
        while True:
            response = self.session.get(self.base_path + "/search", params=params)
            response_data = response.json()

            raw_dts = response_data.get("Items", [])
            start_offset = response_data.get("offset")
            params["offset"] = int(start_offset) + int(limit)
            for item in raw_dts:
                yield DataTemplate(**item)
            if not raw_dts or raw_dts == [] or len(raw_dts) < limit:
                break

    def list(
        self,
        *,
        order_by: OrderBy = OrderBy.DESCENDING,
        name: str = None,
    ) -> Iterator[DataTemplate]:
        """
        Lists data template entities with optional filters.

        Parameters
        ----------
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING.
        name : Union[str, None], optional
            The name of the data template to filter by, by default None.
        exact_match : bool, optional
            Whether to match the name exactly, by default True.

        Returns
        -------
        Iterator
            An iterator of DataTemplate objects.
        """
        return self._list_generator(order_by=order_by, name=name)

    def create(self, *, data_template: DataTemplate) -> DataTemplate:
        response = self.session.post(
            self.base_path,
            json=data_template.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return DataTemplate(**response.json())

    def get_by_id(self, *, id: str) -> DataTemplate:
        response = self.session.get(f"{self.base_path}/{id}")
        return DataTemplate(**response.json())

    def get_by_name(self, *, name: str) -> DataTemplate:
        hits = list(self.list(name=name))
        for h in hits:
            if h.name.lower() == name.lower():
                return h
        return None

    def update(self, *, updated_data_template: DataTemplate) -> DataTemplate:
        raise NotImplementedError("Data templates cannot be updated yet.")

    def delete(self, *, data_template_id: str) -> None:
        self.session.delete(f"{self.base_path}/{data_template_id}")
