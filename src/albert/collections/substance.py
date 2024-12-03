from albert.collections.base import BaseCollection
from albert.resources.substance import Substance, SubstanceResponse, SubstanceTypes
from albert.session import AlbertSession
from albert.utils.exceptions import SDKNotSupportedError


class SubstanceCollection(BaseCollection):
    """
    SubstanceCollection is a collection class for managing substances.

    Parameters
    ----------
    session : Albert
        The Albert session instance.

    Attributes
    ----------
    base_path : str
        The base URL for substance API requests.

    Methods
    -------
    create(substance: Substance) -> Substance
        Creates a new substance.
    get_by_id(substance_id: str) -> Optional[Substance]
        Retrieves a substance by its ID.
    update(substance_id: str, patch_data: dict) -> bool
        Updates a substance by its ID.
    delete(substance_id: str) -> bool
        Deletes a substance by its ID.
    list(limit: int, start_key: Optional[str]) -> Optional[List[Substance]]
        Lists substances with optional filters.
    """

    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{SubstanceCollection._api_version}/substances"

    def get_by_ids(self, cas_ids: list[str], region: str = "US") -> list[SubstanceTypes]:
        url = f"{self.base_path}"
        response = self.session.get(url, params={"casIDs": ",".join(cas_ids), "region": region})
        return SubstanceResponse.model_validate(response.json()).substances

    def get_by_id(self, cas_id: str, region: str = "US") -> SubstanceTypes:
        """
        Get a substance by its ID.

        Parameters
        ----------
        substance_id : str
            The ID of the substance to retrieve.

        Returns
        -------
        Substance | None
            The retrieved substance or None if not found.
        """
        return self.get_by_ids(cas_ids=[cas_id], region=region)[0]
