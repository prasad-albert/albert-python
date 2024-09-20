from collections.abc import Generator, Iterator

from albert.collections.base import BaseCollection, OrderBy
from albert.resources.parameters import Parameter
from albert.session import AlbertSession


class ParameterCollection(BaseCollection):
    _api_version = "v3"
    _updatable_attributes = {"name"}

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{ParameterCollection._api_version}/parameters"

    def get_by_id(self, *, id: str) -> Parameter:
        url = f"{self.base_path}/{id}"
        response = self.session.get(url)

        return Parameter(**response.json())

    def _list_generator(
        self,
        *,
        limit: int = 100,
        order_by: OrderBy = OrderBy.DESCENDING,
        names: str | list[str] = None,
        exact_match: bool = True,
        start_key: str | None = None,
    ) -> Generator[Parameter, None, None]:
        params = {"limit": limit, "orderBy": order_by}
        if names:
            if isinstance(names, str):
                names = [names]
            params["names"] = names
            params["exactMatch"] = str(exact_match).lower()
        if start_key:
            params["startkey"] = start_key
        while True:
            response = self.session.get(self.base_path, params=params)
            params_data = response.json().get("Items", [])
            if not params_data or params_data == []:
                break
            for p in params_data:
                this_param = Parameter(**p)
                yield this_param
            start_key = response.json().get("lastKey")
            if not start_key:
                break
            params["startKey"] = start_key

    def list(
        self,
        *,
        order_by: OrderBy = OrderBy.DESCENDING,
        names: str | list[str] = None,
        exact_match=False,
    ) -> Iterator[Parameter]:
        return self._list_generator(order_by=order_by, names=names, exact_match=exact_match)

    def update(self, *, updated_parameter) -> Parameter:
        param_id = updated_parameter.id
        patch_params = self._generate_patch_payload(
            existing=self.get_by_id(id=param_id), updated=updated_parameter
        )
        self.session.patch(f"{self.base_path}/{param_id}", params=patch_params)
        return updated_parameter
