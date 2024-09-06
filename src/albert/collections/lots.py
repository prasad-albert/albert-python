from albert.albert_session import AlbertSession
from albert.collections.base import BaseCollection
from albert.resources.lots import Lot


class LotCollection(BaseCollection):
    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_url = "/api/v3/lots"

    def create(self, *, lots: list[Lot]) -> list[Lot]:
        payload = [lot.model_dump(by_alias=True, exclude_none=True) for lot in lots]
        response = self.session.post(self.base_url, json=payload)

        return [self._rehydrate_lot(lot) for lot in response.json().get("CreatedLots", [])]

    def get_by_id(self, *, lot_id: str) -> Lot:
        url = f"{self.base_url}/{lot_id}"
        response = self.session.get(url)

        return Lot(**response.json())

    # def update(self, *, lot_id: str, patch_data: Dict[str, Any]) -> bool:
    #     """TODO: Follow pattern for other Update methods. This will need a custom Patch creation method."""
    #     url = f"{self.base_url}/{lot_id}"
    #     response = self.session.patch(url, json=patch_data)
    #
    #     return lot_id

    def delete(self, *, lot_id: str) -> bool:
        url = f"{self.base_url}/{lot_id}"
        response = self.session.delete(url)

        return True


# TODO: Add generator logic
# def list(
#     self,
# *,
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
