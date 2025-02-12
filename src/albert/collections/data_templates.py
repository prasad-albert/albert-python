from collections.abc import Iterator

from albert.collections.base import BaseCollection, OrderBy
from albert.resources.data_templates import DataColumnValue, DataTemplate
from albert.resources.identifiers import DataTemplateId
from albert.session import AlbertSession
from albert.utils.logging import logger
from albert.utils.pagination import AlbertPaginator, PaginationMode


class DataTemplateCollection(BaseCollection):
    _api_version = "v3"
    _updatable_attributes = {"name", "description", "metadata"}

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{DataTemplateCollection._api_version}/datatemplates"

    def create(self, *, data_template: DataTemplate) -> DataTemplate:
        response = self.session.post(
            self.base_path,
            json=data_template.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return DataTemplate(**response.json())

    def get_by_id(self, *, id: DataTemplateId) -> DataTemplate:
        response = self.session.get(f"{self.base_path}/{id}")
        return DataTemplate(**response.json())

    def get_by_ids(self, *, ids: list[str]) -> list[DataTemplate]:
        url = f"{self.base_path}/ids"
        batches = [ids[i : i + 250] for i in range(0, len(ids), 250)]
        return [
            DataTemplate(**item)
            for batch in batches
            for item in self.session.get(url, params={"id": batch}).json()["Items"]
        ]

    def get_by_name(self, *, name: str) -> DataTemplate | None:
        hits = list(self.list(name=name))
        for h in hits:
            if h.name.lower() == name.lower():
                return h
        return None

    def add_data_columns(
        self, *, data_template_id: str, data_columns: list[DataColumnValue]
    ) -> DataTemplate:
        payload = {
            "DataColumns": [
                x.model_dump(mode="json", by_alias=True, exclude_none=True) for x in data_columns
            ]
        }
        self.session.put(
            f"{self.base_path}/{data_template_id}/datacolumns",
            json=payload,
        )
        return self.get_by_id(id=data_template_id)

    def list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        order_by: OrderBy = OrderBy.DESCENDING,
        name: str | None = None,
        user_id: str | None = None,
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
        Iterator[DataTemplate]
            An iterator of DataTemplate objects.
        """

        def deserialize(items: list[dict]) -> list[DataTemplate]:
            return self.get_by_ids(ids=[x["albertId"] for x in items])

        params = {
            "limit": limit,
            "offset": offset,
            "order": OrderBy(order_by).value if order_by else None,
            "text": name,
            "userId": user_id,
        }

        return AlbertPaginator(
            mode=PaginationMode.OFFSET,
            path=f"{self.base_path}/search",
            session=self.session,
            deserialize=deserialize,
            params=params,
        )

    def update(self, *, data_template: DataTemplate) -> DataTemplate:
        existing = self.get_by_id(id=data_template.id)
        base_payload = self._generate_patch_payload(existing=existing, updated=data_template)
        payload = base_payload.model_dump(mode="json", by_alias=True)
        _updatable_attributes_special = {"tags", "data_column_values"}
        for attribute in _updatable_attributes_special:
            old_value = getattr(existing, attribute)
            new_value = getattr(data_template, attribute)
            if attribute == "tags":
                if (old_value is None or old_value == []) and new_value is not None:
                    for t in new_value:
                        payload["data"].append(
                            {
                                "operation": "add",
                                "attribute": "tagId",
                                "newValue": t.id,  # This will be a CasAmount Object,
                                "entityId": t.id,
                            }
                        )
                else:
                    if old_value is None:  # pragma: no cover
                        old_value = []
                    if new_value is None:  # pragma: no cover
                        new_value = []
                    old_set = {obj.id for obj in old_value}
                    new_set = {obj.id for obj in new_value}

                    # Find what's in set 1 but not in set 2
                    to_del = old_set - new_set

                    # Find what's in set 2 but not in set 1
                    to_add = new_set - old_set

                    for id in to_add:
                        payload["data"].append(
                            {
                                "operation": "add",
                                "attribute": "tagId",
                                "newValue": id,
                            }
                        )
                    for id in to_del:
                        payload["data"].append(
                            {
                                "operation": "delete",
                                "attribute": "tagId",
                                "oldValue": id,
                            }
                        )
            elif attribute == "data_column_values":
                # Do the update by column
                to_remove = set([x.data_column_id for x in old_value]) - set(
                    [x.data_column_id for x in new_value]
                )
                to_add = set([x.data_column_id for x in new_value]) - set(
                    [x.data_column_id for x in old_value]
                )
                to_update = set([x.data_column_id for x in new_value]) & set(
                    [x.data_column_id for x in old_value]
                )
                if len(to_remove) > 0:
                    logger.error(
                        "Data Columns cannot be Removed from a Data Template. Set to hidden instead and retry."
                    )
                if len(to_add) > 0:
                    new_dcs = [x for x in new_value if x.data_column_id in to_add]
                    self.add_data_columns(data_template_id=data_template.id, data_columns=new_dcs)
                for dc_id in to_update:
                    actions = []
                    old_dc_val = next(x for x in old_value if x.data_column_id == dc_id)
                    new_dc_val = next(x for x in new_value if x.data_column_id == dc_id)
                    # do hidden last because it can change the column sequence.
                    if old_dc_val.unit != new_dc_val.unit:
                        payload["data"].append(
                            {
                                "operation": "update",
                                "attribute": "unit",
                                "newValue": new_dc_val.unit.id,
                                "oldValue": old_dc_val.unit.id,
                                "colId": old_dc_val.column_sequence,
                            }
                        )
                    if old_dc_val.hidden != new_dc_val.hidden:
                        actions.append(
                            {
                                "operation": "update",
                                "attribute": "hidden",
                                "newValue": new_dc_val.hidden,
                                "oldValue": old_dc_val.hidden,
                            }
                        )
                    if len(actions) > 0:
                        payload["data"].append(
                            {
                                "actions": actions,
                                "attribute": "datacolumn",
                                "colId": old_dc_val.column_sequence,
                            }
                        )
        if len(payload["data"]) > 0:
            url = f"{self.base_path}/{existing.id}"
            self.session.patch(url, json=payload)
        return self.get_by_id(id=existing.id)  # always do this in case columns were added

    def delete(self, *, id: str) -> None:
        self.session.delete(f"{self.base_path}/{id}")
