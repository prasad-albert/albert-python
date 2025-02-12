import json
import logging
from collections.abc import Iterator

from albert.collections.base import BaseCollection, OrderBy
from albert.resources.parameters import Parameter
from albert.session import AlbertSession
from albert.utils.pagination import AlbertPaginator, PaginationMode


class ParameterCollection(BaseCollection):
    _api_version = "v3"
    _updatable_attributes = {"name", "metadata"}

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{ParameterCollection._api_version}/parameters"

    def get_by_id(self, *, id: str) -> Parameter:
        url = f"{self.base_path}/{id}"
        response = self.session.get(url)
        return Parameter(**response.json())

    def create(self, *, parameter: Parameter) -> Parameter:
        match = next(self.list(names=parameter.name, exact_match=True), None)
        if match is not None:
            logging.warning(
                f"Parameter with name {parameter.name} already exists. Returning existing parameter."
            )
            return match
        response = self.session.post(
            self.base_path,
            json=parameter.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )
        return Parameter(**response.json())

    def delete(self, *, id: str) -> None:
        url = f"{self.base_path}/{id}"
        self.session.delete(url)

    def list(
        self,
        *,
        limit: int = 50,
        ids: list[str] | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
        names: str | list[str] = None,
        exact_match: bool = False,
        start_key: str | None = None,
    ) -> Iterator[Parameter]:
        params = {"limit": limit, "orderBy": order_by, "parameters": ids, "startKey": start_key}
        if names:
            params["name"] = [names] if isinstance(names, str) else names
            params["exactMatch"] = json.dumps(exact_match)

        return AlbertPaginator(
            mode=PaginationMode.KEY,
            path=self.base_path,
            session=self.session,
            params=params,
            deserialize=lambda items: [Parameter(**item) for item in items],
        )

    def _is_metadata_item_list(
        self, *, existing_object: Parameter, updated_object: Parameter, metadata_field: str
    ):
        if not metadata_field.startswith("Metadata."):
            return False
        else:
            metadata_field = metadata_field.split(".")[1]
        if existing_object.metadata is None:
            existing_object.metadata = {}
        if updated_object.metadata is None:
            updated_object.metadata = {}
        existing = existing_object.metadata.get(metadata_field, None)
        updated = updated_object.metadata.get(metadata_field, None)
        return isinstance(existing, list) or isinstance(updated, list)

    def update(self, *, parameter: Parameter) -> Parameter:
        existing = self.get_by_id(id=parameter.id)
        payload = self._generate_patch_payload(
            existing=existing,
            updated=parameter,
        )
        payload_dump = payload.model_dump(mode="json", by_alias=True)
        for i, change in enumerate(payload_dump["data"]):
            if not self._is_metadata_item_list(
                existing_object=existing,
                updated_object=parameter,
                metadata_field=change["attribute"],
            ):
                change["operation"] = "update"
                if "newValue" in change and change["newValue"] is None:
                    del change["newValue"]
                if "oldValue" in change and change["oldValue"] is None:
                    del change["oldValue"]
                payload_dump["data"][i] = change
        if len(payload_dump["data"]) == 0:
            return parameter
        for e in payload_dump["data"]:
            print(e)
            self.session.patch(
                f"{self.base_path}/{parameter.id}",
                json={"data": [e]},
            )
        return self.get_by_id(id=parameter.id)
