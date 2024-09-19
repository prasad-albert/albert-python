from collections.abc import Generator, Iterator

from albert.collections.base import BaseCollection, OrderBy
from albert.resources.parameter_groups import ParameterGroup, PGType
from albert.session import AlbertSession


class ParameterGroupCollection(BaseCollection):
    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{ParameterGroupCollection._api_version}/parametergroups"

    def get_by_id(self, *, id: str) -> ParameterGroup:
        url = f"{self.base_path}/{id}"
        response = self.session.get(url)
        return ParameterGroup(**response.json())

    def _list_generator(
        self,
        *,
        text: str | None = None,
        offset: int | None = None,
        types: list[PGType] | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
        limit: int = 25,
    ) -> Generator[ParameterGroup, None, None]:
        params = {"limit": limit, "order": order_by.value}
        if text:
            params["text"] = text
        if offset:
            params["offset"] = offset
        if types:
            params["type"] = [t.value for t in types] if isinstance(types, list) else types.value
        while True:
            response = self.session.get(self.base_path + "/search", params=params)
            pg_data = response.json().get("Items", [])
            if not pg_data or pg_data == []:
                break
            for pg in pg_data:
                yield self.get_by_id(id=pg["albertId"])
            offset = response.json().get("offset")
            if not offset:
                break
            params["offset"] = offset

    def list(
        self,
        *,
        text: str | None = None,
        types: list[PGType] | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Iterator[ParameterGroup]:
        return self._list_generator(
            text=text,
            types=types,
            order_by=order_by,
        )
