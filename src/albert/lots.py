from typing import Optional, List, Dict
from pydantic import Field, PrivateAttr
from datetime import date, datetime
from albert.base_entity import BaseAlbertModel
from enum import Enum


import requests
from typing import List, Optional, Dict, Any
from albert.base_collection import BaseCollection
from albert.inventory import InventoryCategory



class LotStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    QUARANTINED = "quarantined"


class Lot(BaseAlbertModel):
    id: Optional[str] = Field(None, alias="albertId")
    inventory_id: str = Field(alias="parentId")
    task_id: Optional[str] = Field(default=None, alias="taskId")

    expiration_date: Optional[datetime] = Field(None, alias="expirationDate")
    notes: Optional[str] = None
    manufacturer_lot_number: Optional[str] = Field(None, alias="manufacturerLotNumber")
    # location: Optional[Location] = {} #need to make Location Class
    # storageLocation: Optional[StorageLocation] = {} #need to make StorageLocation Class
    pack_size: Optional[float] = Field(None, alias="packSize")
    initial_quantity: float = Field(
        ge=0, alias="initialQuantity"
    )  # requires the field to be greater than or equal to 0
    cost: float = Field(ge=0)  # requires the field to be greater than or equal to 0
    # owner: Optional[List[Owner]] # Need to make Owner Class (User should work)
    lot_number: Optional[str] = Field(None, alias="lotNumber")
    inventory_on_hand: float = Field(ge=0, alias="inventoryOnHand")
    task_completion_date: Optional[datetime] = Field(None, alias="taskCompletionDate")
    external_barcode_id: Optional[str] = Field(None, alias="externalBarcodeId")
    _has_notes: bool = PrivateAttr(default=None)
    _notes: str = PrivateAttr(default=None)
    _has_attachments: bool = PrivateAttr(default=None)
    _parent_name: str = PrivateAttr(default=None)
    _parent_unit: str = PrivateAttr(default=None)
    _parent_category: InventoryCategory = PrivateAttr(default=None)
    _barcode_id: str = PrivateAttr(default=None)
    _metadata: Optional[Any] = PrivateAttr(None)

    _status: Optional[LotStatus] = PrivateAttr(
        default=None
    )  # because quarantined is an allowed Lot status, we need to extend the normal status

    def __init__(self, **data: Any):
        super().__init__(**data)
        if "hasAttachments" in data:
            if data["hasAttachments"] == "1":
                self._has_attachments = True
            elif data["hasAttachments"] == "2":
                self._has_attachments == False
            else:
                print(
                    f"Unknown response for hasAttachments given: {data['hasAttachments']}"
                )
                pass
        if "hasNotes" in data:
            if data["hasNotes"] == "1":
                self._has_notes = True
            elif data["hasNotes"] == "2":
                self._has_notes == False
            else:
                print(f"Unknown response for hasNotes given: {data['hasNotes']}")
                pass
        if "parentName" in data:
            self._parent_name = data["parentName"]
        if "parentUnit" in data:
            self._parent_unit = data["parentUnit"]
        if "parentIdCategory" in data:
            self._parent_category = data["parentIdCategory"]
        if "status" in data:
            self._status = LotStatus(data["status"])

        if "Metadata" in data:
            self._metadata = data["Metadata"]
        if "notes" in data:
            self._notes = data["notes"]
        if "barcodeId" in data:
            self._barcode_id = data["barcodeId"]

    @property
    def has_notes(self) -> bool:
        return self._has_notes

    @property
    def has_attachments(self) -> bool:
        return self._has_attachments

    @property
    def metadata(self) -> str:
        return self._metadata

    @property
    def notes(self) -> str:
        return self._notes

    @property
    def barcode_id(self) -> str:
        return self._barcode_id


class LotCollection(BaseCollection):

    def __init__(self, session):
        super().__init__(session=session)
        self.base_url = "/api/v3/lots"

    def create(self, lots: List[Lot]) -> List[Lot]:
        payload = [lot.model_dump(by_alias=True, exclude_none=True) for lot in lots]
        response = self.session.post(
            self.base_url, json=payload)
        
        return [
            self._rehydrate_lot(lot)
            for lot in response.json().get("CreatedLots", [])
        ]
       
    def get_by_id(self, lot_id: str) -> Lot:
        url = f"{self.base_url}/{lot_id}"
        response = self.session.get(url)
        
        return Lot(**response.json())

    # def update(self, lot_id: str, patch_data: Dict[str, Any]) -> bool:
    #     """TODO: Follow pattern for other Update methods. This will need a custom Patch creation method."""
    #     url = f"{self.base_url}/{lot_id}"
    #     response = self.session.patch(url, json=patch_data)
    #     
    #     return lot_id


    def delete(self, lot_id: str) -> bool:
        url = f"{self.base_url}/{lot_id}"
        response = self.session.delete(url)
        
        return True


# TODO: Add generator logic
# def list(
#     self,
#     limit: int = 50,
#     start_key: Optional[str] = None,
#     inventory_id: Optional[str] = None,
#     barCodeId: Optional[str] = None,
#     isZeroed: Optional[bool] = None,
#     inventoryOnHand: Optional[str] = None,
#     locationName: Optional[str] = None,
# ) -> List[Lot]:
#     params = {
#         "limit": str(limit),
#     }
#     if start_key:
#         params["startKey"] = start_key
#     if inventory_id:
#         params["parentId"] = inventory_id
#     if barCodeId:
#         params["barCodeId"] = barCodeId
#     if isZeroed is not None:
#         params["isZeroed"] = str(isZeroed).lower()
#     if inventoryOnHand:
#         params["inventoryOnHand"] = inventoryOnHand
#     if locationName:
#         params["locationName"] = locationName

#     response = self.session.get(
#         self.base_url, params=params
#     )
#     
#    
#     lots = response.json().get("Items", [])
#     return [Lot(**x) for x in lots]
