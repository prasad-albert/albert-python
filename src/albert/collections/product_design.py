from albert.collections.base import BaseCollection
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

    def get_unpacked_formula(self, *, formula_ids: list[str]) -> UnpackedProductDesign:
        """
        Get unpacked formula by formula id

        Parameters
        ----------
        formula_ids : list[str]
            The formula ids to get unpacked formula for

        Returns
        -------
        UnpackedProductDesign
            The unpacked formula
        """
        url = f"{self.base_path}/PREDICTION/unpack"
        response = self.session.get(url, params={"formulaId": formula_ids})
        return [UnpackedProductDesign(**x) for x in response.json()]
