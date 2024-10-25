from collections.abc import Generator, Iterator

from albert.collections.base import BaseCollection, OrderBy
from albert.resources.data_templates import DataTemplate
from albert.session import AlbertSession
from albert.utils.exceptions import ForbiddenError, InternalServerError
from albert.utils.logging import logger
from albert.utils.pagination import SearchPaginator


class DataTemplateCollection(BaseCollection):
    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{DataTemplateCollection._api_version}/datatemplates"

    # def _list_generator(
    #     self,
    #     *,
    #     limit: int = 25,
    #     offset: int | None = None,
    #     name: str | None = None,
    #     order_by: OrderBy = OrderBy.DESCENDING,
    # ) -> Generator[DataTemplate, None, None]:
    #     """NOTE: WE could add more allowed filters here, but for now, this is all we need."""
    #     params = {
    #         "sortBy": "createdAt",
    #         "order": order_by.value,
    #         "limit": str(limit),
    #     }
    #     if offset:  # pragma: no cover
    #         params["offset"] = offset
    #     if name:
    #         params["text"] = name
    #     while True:
    #         response = self.session.get(self.base_path + "/search", params=params)
    #         response_data = response.json()

    #         raw_dts = response_data.get("Items", [])
    #         start_offset = response_data.get("offset")
    #         params["offset"] = int(start_offset) + int(limit)
    #         for item in raw_dts:
    #             yield DataTemplate(**item)
    #         if not raw_dts or raw_dts == [] or len(raw_dts) < limit:
    #             break

    def list(
        self,
        *,
        order_by: OrderBy = OrderBy.DESCENDING,
        name: str = None,
        limit: int = 25,
        offset: int = 0,
    ) -> SearchPaginator[DataTemplate]:
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

        def deserialize(data: dict) -> DataTemplate | None:
            id = data["albertId"]
            try:
                return self.get_by_id(id=id)
            except (ForbiddenError, InternalServerError) as e:
                logger.warning(f"Error fetching Data Template '{id}': {e}")
                return None

        params = {
            "limit": limit,
            "offset": offset,
            "order": OrderBy(order_by).value if order_by else None,
            "text": name,
        }
        params = {k: v for k, v in params.items() if v is not None}

        return SearchPaginator(
            path=f"{self.base_path}/search",
            session=self.session,
            deserialize=deserialize,
            params=params,
        )

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
