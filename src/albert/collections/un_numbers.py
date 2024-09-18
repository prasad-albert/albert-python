from collections.abc import Generator, Iterator

from albert.collections.base import BaseCollection
from albert.resources.un_numbers import UnNumber
from albert.session import AlbertSession


class UnNumberCollection(BaseCollection):
    """
    UnNumberCollection is a collection class for managing UN Numbers.

    Note
    ----
    Creating UN Numbers is not supported via the SDK, as UN Numbers are highly controlled by Albert.
    """

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_url = "/api/v3/unnumbers"

    def create(self) -> None:
        """
        This method is not implemented as UN Numbers cannot be created through the SDK.
        """
        raise NotImplementedError()

    def get_by_id(self, *, un_number_id: str) -> UnNumber | None:
        url = f"{self.base_url}/{un_number_id}"
        response = self.session.get(url)
        return UnNumber(**response.json())

    def _list_generator(
        self,
        *,
        name: str = None,
        start_key: str | None = None,
        exact_match: bool | None = None,
    ) -> Generator[UnNumber, None, None]:
        params = {}
        if start_key:
            params["startKey"] = start_key
        if name:
            params["name"] = name
            if exact_match:
                params["exactMatch"] = str(exact_match).lower()
        while True:
            response = self.session.get(self.base_url, params=params)
            un_numbers = response.json().get("Items", [])
            if not un_numbers or un_numbers == []:
                break
            for x in un_numbers:
                yield UnNumber(**x)
            start_key = response.json().get("lastKey")
            if not start_key:
                break
            params["startKey"] = start_key

    def list(
        self,
        *,
        name: str = None,
        exact_match: bool | None = None,
    ) -> Iterator[UnNumber]:
        return self._list_generator(name=name, exact_match=exact_match)

    def get_by_name(self, *, name: str) -> UnNumber:
        found = self.list(exact_match=True, name=name)
        return next(found, None)
