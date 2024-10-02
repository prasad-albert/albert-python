import logging
from enum import Enum
from typing import Any

from pydantic import Field, NonNegativeFloat, PrivateAttr, field_serializer

from albert.collections.inventory import InventoryCategory
from albert.resources.base import BaseAlbertModel
from albert.resources.locations import Location
from albert.resources.serialization import SerializeAsEntityLink
from albert.resources.storage_locations import StorageLocation
from albert.resources.users import User


class LotStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    QUARANTINED = "quarantined"


class Lot(BaseAlbertModel):
    id: str | None = Field(None, alias="albertId")
    inventory_id: str = Field(alias="parentId")
    task_id: str | None = Field(default=None, alias="taskId")
    notes: str | None = Field(default=None)
    expiration_date: str | None = Field(None, alias="expirationDate")
    manufacturer_lot_number: str | None = Field(None, alias="manufacturerLotNumber")
    storage_location: SerializeAsEntityLink[StorageLocation] | None = Field(
        alias="StorageLocation", default=None
    )
    pack_size: str | None = Field(None, alias="packSize")
    initial_quantity: NonNegativeFloat | None = Field(default=None, alias="initialQuantity")
    cost: NonNegativeFloat | None = Field(default=None)
    inventory_on_hand: NonNegativeFloat = Field(alias="inventoryOnHand")
    owner: list[SerializeAsEntityLink[User]] | None = Field(default=None)
    lot_number: str | None = Field(None, alias="lotNumber")
    external_barcode_id: str | None = Field(None, alias="externalBarcodeId")

    _location: SerializeAsEntityLink[Location] | None = PrivateAttr(default=None)
    _has_notes: bool | None = PrivateAttr(default=None)
    _notes: str | None = PrivateAttr(default=None)
    _has_attachments: bool | None = PrivateAttr(default=None)
    _parent_name: str | None = PrivateAttr(default=None)
    _parent_unit: str | None = PrivateAttr(default=None)
    _parent_category: InventoryCategory | None = PrivateAttr(default=None)
    _barcode_id: str | None = PrivateAttr(default=None)
    metadata: dict[str, Any] | None = Field(alias="Metadata", default=None)

    # because quarantined is an allowed Lot status, we need to extend the normal status
    _status: LotStatus | None = PrivateAttr(default=None)

    def __init__(self, **data: Any):
        super().__init__(**data)
        if "hasAttachments" in data:
            if data["hasAttachments"] == "1":
                self._has_attachments = True
            elif data["hasAttachments"] == "0":
                self._has_attachments = False
            else:
                logging.error(
                    f"Unknown response for hasAttachments given: {data['hasAttachments']}"
                )
        if "hasNotes" in data:
            if data["hasNotes"] == "1":
                self._has_notes = True
            elif data["hasNotes"] == "0":
                self._has_notes = False
            else:
                logging.error(f"Unknown response for hasNotes given: {data['hasNotes']}")
        if "parentName" in data:
            self._parent_name = data["parentName"]
        if "parentUnit" in data:
            self._parent_unit = data["parentUnit"]
        if "parentIdCategory" in data:
            self._parent_category = data["parentIdCategory"]
        if "status" in data:
            self._status = LotStatus(data["status"])
        if "Location" in data:
            self._location = data["Location"]

        if "notes" in data:
            self._notes = data["notes"]
        if "barcodeId" in data:
            self._barcode_id = data["barcodeId"]

    @field_serializer("initial_quantity", return_type=str)
    def serialize_initial_quantity(self, initial_quantity: NonNegativeFloat):
        return str(initial_quantity)

    @field_serializer("cost", return_type=str)
    def serialize_cost(self, cost: NonNegativeFloat):
        return str(cost)

    @field_serializer("inventory_on_hand", return_type=str)
    def serialize_inventory_on_hand(self, inventory_on_hand: NonNegativeFloat):
        return str(inventory_on_hand)

    @property
    def has_notes(self) -> bool:
        return self._has_notes

    @property
    def has_attachments(self) -> bool:
        return self._has_attachments

    @property
    def barcode_id(self) -> str:
        return self._barcode_id
