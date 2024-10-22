from collections.abc import Iterator
from typing import Generic, TypeVar

from albert.resources.base import BaseResource
from albert.session import AlbertSession

ResourceType = TypeVar("ResourceType", bound=BaseResource)


class ListIterator(Generic[ResourceType]):
    def __init__(
        self,
        *,
        path: str,
        session: AlbertSession,
        resource_cls: type[ResourceType],
        params: dict[str, str] | None = None,
        items_key: str = "Items",
    ):
        self.path = path
        self.session = session
        self.resource_cls = resource_cls
        self.params = {k: v for k, v in params.items() if v is not None}
        self.items_key = items_key

    def __iter__(self) -> Iterator[ResourceType]:
        while True:
            response = self.session.get(self.path, params=self.params)
            response_data = response.json()

            items = response_data.get(self.items_key, [])
            for item in items:
                yield self.resource_cls(**item)

            start_key = response_data.get("lastKey")
            limit = self.params.get("limit")
            if not start_key or (limit is not None and len(items) < limit):
                return
            self.params["startKey"] = start_key
