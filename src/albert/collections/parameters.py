from albert.collections.base import BaseCollection
from albert.resources.parameters import Parameter
from albert.session import AlbertSession


class ParameterCollection(BaseCollection):
    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{ParameterCollection._api_version}/parameters"

    def get_by_id(self, *, id: str) -> Parameter:
        url = f"{self.base_path}/{id}"
        response = self.session.get(url)

        return Parameter(**response.json())
