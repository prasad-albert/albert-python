from albert.collections.base import BaseCollection
from albert.resources.inventory import InventoryItem
from albert.resources.property_data import (
    InventoryDataColumn,
    InventoryPropertyData,
    InventoryPropertyDataCreate,
    PropertyDataPatchDatum,
)
from albert.session import AlbertSession
from albert.utils.logging import logger
from albert.utils.patches import PatchOperation


class PropertyDataCollection(BaseCollection):
    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the CompanyCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_path = f"/api/{PropertyDataCollection._api_version}/propertydata"

    def get_properties_on_inventory(self, *, inventory_item: InventoryItem):
        response = self.session.get(
            url=f"{self.base_path}?entity=inventory&id[]={inventory_item.id}"
        )
        response_json = response.json()
        return InventoryPropertyData(**response_json[0])

    def add_properies_to_inventory(
        self, *, inventory_item: InventoryItem, properties: list[InventoryDataColumn]
    ):
        returned = []
        for p in properties:
            # Can only add one at a time.
            create_object = InventoryPropertyDataCreate(
                inventory_id=inventory_item.id, data_columns=[p]
            )
            response = self.session.post(
                self.base_path, json=create_object.model_dump(exclude_none=True, by_alias=True)
            )
            response_json = response.json()
            logger.info(response_json.get("message", None))
            returned.append(InventoryPropertyDataCreate(**response_json))
        return returned

    def update_property_on_inventory(
        self, *, inventory_item: InventoryItem, property_data: InventoryDataColumn
    ):
        existing_properties = self.get_properties_on_inventory(inventory_item=inventory_item)
        existing_value = None
        for p in existing_properties.custom_property_data:
            if p.data_column.data_column_id == property_data.data_column_id:
                existing_value = p.data_column.property_data.value
                existing_id = p.data_column.property_data.id
                break
        if existing_value is not None:
            payload = [
                PropertyDataPatchDatum(
                    operation=PatchOperation.UPDATE,
                    id=existing_id,
                    attribute="value",
                    new_value=property_data.value,
                    old_value=existing_value,
                )
            ]
        else:
            payload = [
                PropertyDataPatchDatum(
                    operation=PatchOperation.ADD,
                    id=existing_id,
                    attribute="value",
                    new_value=property_data.value,
                )
            ]

        self.session.patch(
            url=f"{self.base_path}/{inventory_item.id}",
            json=[x.model_dump(exclude_none=True, by_alias=True) for x in payload],
        )
        return self.get_properties_on_inventory(inventory_item=inventory_item)
