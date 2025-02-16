from pydantic import validate_call

from albert.collections.base import BaseCollection
from albert.resources.identifiers import InventoryId
from albert.resources.product_design import UnpackedProductDesign
from albert.session import AlbertSession


class ProductDesignCollection(BaseCollection):
    _updatable_attributes = {"notes", "description", "smiles"}
    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the CasCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_path = f"/api/{ProductDesignCollection._api_version}/productdesign"

    @validate_call
    def get_unpacked_product(self, *, inventory_ids: list[InventoryId]) -> UnpackedProductDesign:
        """
        Get unpacked product by inventory IDs

        Parameters
        ----------
        inventory_ids : list[InventoryId]
            The inventory ids to get unpacked formula for

        Returns
        -------
        list[UnpackedProductDesign]
            The unpacked product/formula
        """
        url = f"{self.base_path}/PREDICTION/unpack"
        response = self.session.get(url, params={"formulaId": inventory_ids})
        return [UnpackedProductDesign(**x) for x in response.json()]
