from typing import Optional, List, Dict, Union, Any, Generator
from pydantic import Field
import requests
from albert.base_collection import BaseCollection, OrderBy
from albert.base_entity import BaseAlbertModel
from enum import Enum


class WGK(Enum):
    ONE = "1"
    TWO = "2"
    THREE = "3"


class CasCategory(Enum):
    USER = "User"
    VERISK = "Verisk"
    TSCA_PUBLIC = "TSCA - Public"
    TSCA_PRIVATE = "TSCA - Private"
    NOT_TSCA = "not TSCA"
    EXTERNAL = "CAS linked to External Database"
    UNKNOWN = "Unknown (Trade Secret)"
    CL_INVENTORY_UPLOAD = "CL_Inventory Upload"


class Cas(BaseAlbertModel):
    """
    Cas is a Pydantic model representing a CAS entity.

    Attributes
    ----------
    number : str
        The CAS number.
    description : Optional[str]
        The description or name of the CAS.
    notes : Optional[str]
        Notes of the CAS.
    category : Optional[CasCategory]
        The category of the CAS.
    smiles : Optional[str]
        CAS SMILES notation.
    inchi_key : Optional[str]
        InChIKey of the CAS.
    iupac_name : Optional[str]
        IUPAC name of the CAS.
    name : Optional[str]
        Name of the CAS.
    id : Optional[str]
        The AlbertID of the CAS.
    # hazards : Optional[List[str]]
    #     Hazards associated with the CAS.
    # wgk : Optional[str]
    #     German Water Hazard Class (WGK) number.
    # ec_number : Optional[str]
    #     European Community (EC) number.
    # type : Optional[str]
    #     Type of the CAS.
    # classificationType : Optional[str]
    #     Classification type of the CAS.
    # order : Optional[str]
    #     CAS order.
    """

    number: str
    description: Optional[str] = None
    notes: Optional[str] = None
    category: Optional[CasCategory] = None  # To better define in docstrings
    smiles: Optional[str] = Field(None, alias="casSmiles")
    inchi_key: Optional[str] = Field(None, alias="inchiKey")
    iupac_name: Optional[str] = Field(None, alias="iUpacName")
    name: Optional[str] = None
    id: Optional[str] = Field(None, alias="albertId")

    # hazards: Optional[List[Hazard]] = None
    # wgk: Optional[WGK] = None
    # ec_number: Optional[str] = Field(None, alias="ecListNo")
    # type: Optional[str] = None
    # classification_type: Optional[str] = Field(None, alias="classificationType")
    # order: Optional[str] = None

    @property
    def status(self):
        return self._status

    @classmethod
    def from_str(cls, number: str) -> "Cas":
        """
        Creates a Cas object from a string.

        Parameters
        ----------
        number : str
            The CAS number.

        Returns
        -------
        Cas
            The Cas object created from the string.
        """
        return cls(number=number)


class CasCollection(BaseCollection):
    """
    CasCollection is a collection class for managing CAS entities.

    Parameters
    ----------
    client : Any
        The Albert client instance.

    Attributes
    ----------
    base_url : str
        The base URL for CAS API requests.
    cas_cache : dict
        A cache of CAS objects.

    Methods
    -------
    list(limit=50, start_key=None, number=None, albert_id=None, order_by=OrderBy.DESCENDING, filter=None, created_by=None, updated_by=None) -> List[Cas]
        Lists CAS entities with optional filters.
    cas_exists(number, exact_match=True) -> bool
        Checks if a CAS exists by its number.
    create(cas) -> Cas
        Creates a new CAS entity.
    get_by_id(cas_id) -> Cas
        Retrieves a CAS by its ID.
    get_by_number(number, exact_match=True) -> Optional[Cas]
        Retrieves a CAS by its number.
    delete(cas_id) -> bool
        Deletes a CAS by its ID.
    rename(old_number, new_number) -> Optional[Cas]
        Renames an existing CAS entity.
    """

    _updatable_attributes = {"notes", "description", "smiles"}

    def __init__(self, client):
        """
        Initializes the CasCollection with the provided client.

        Parameters
        ----------
        client : Any
            The Albert client instance.
        """
        super().__init__(client=client)
        self.base_url = f"{self.client.base_url}/api/v3/cas"
        self.cas_cache = {}

    def _remove_from_cache_by_id(self, id):
        name = None
        for k, v in self.cas_cache.items():
            if v.id == id:
                name = k
                break
        if name:
            del self.cas_cache[name]

    def _list_genertor(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        number: Optional[str] = None,
        id: Optional[str] = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Generator:
        """
        Lists CAS entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of CAS entities to return, by default 50.
        start_key : Optional[str], optional
            The primary key of the first item that this operation will evaluate.
        number : Optional[str], optional
            Fetches list of CAS by CAS number.
        id : Optional[str], optional
            Fetches list of CAS using the CAS Albert ID.
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING.

        Yields
        -------
        Generator
            A Generator of Cas objects.
        """
        params = {"limit": limit, "orderBy": order_by.value}
        if start_key:
            params["startKey"] = start_key
        if number:
            params["number"] = number
        if id:
            params["albertId"] = id
        while True:
            response = requests.get(
                self.base_url, headers=self.client.headers, params=params
            )
            if response.status_code != 200:
                self.handle_api_error(response=response)
                break
            cas_data = response.json().get("Items", [])
            if not cas_data or cas_data == []:
                break
            for x in cas_data:
                this_cas = Cas(**x)
                self.cas_cache[this_cas.number] = this_cas
                yield this_cas
            start_key = response.json().get("lastKey")
            if not start_key:
                break
            params["startKey"] = start_key

    def list(
        self,
        number: Optional[str] = None,
        id: Optional[str] = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Generator:
        """
        Lists CAS entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of CAS entities to return, by default 50.
        start_key : Optional[str], optional
            The primary key of the first item that this operation will evaluate.
        number : Optional[str], optional
            Fetches list of CAS by CAS number.
        id : Optional[str], optional
            Fetches list of CAS using the CAS Albert ID.
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING.

        Returns
        -------
        Generator
            A generator of Cas objects.
        """
        return self._list_genertor(number=number, order_by=order_by, id=id)

    def cas_exists(self, number: str, exact_match: bool = True) -> bool:
        """
        Checks if a CAS exists by its number.

        Parameters
        ----------
        number : str
            The number of the CAS to check.
        exact_match : bool, optional
            Whether to match the number exactly, by default True.

        Returns
        -------
        bool
            True if the CAS exists, False otherwise.
        """
        if number in self.cas_cache:
            return True
        cas_list = self.get_by_number(number=number, exact_match=exact_match)
        if cas_list is None:
            return False
        return len(cas_list) > 0

    def create(self, cas: Union[str, Cas]) -> Cas:
        """
        Creates a new CAS entity.

        Parameters
        ----------
        cas : Union[str, Cas]
            The CAS number or Cas object to create.

        Returns
        -------
        Cas
            The created Cas object.
        """
        if isinstance(cas, str):
            cas = Cas(number=cas)
        if self.cas_exists(cas.number):
            existing_cas = self.cas_cache[cas.number]
            print(f"CAS {existing_cas.number} already exists with id {existing_cas.id}")
            return existing_cas
        else:
            payload = cas.model_dump(by_alias=True, exclude_unset=True)
            response = requests.post(
                self.base_url, headers=self.client.headers, json=payload
            )
            if response.status_code != 201:
                self.handle_api_error(response=response)
            cas = Cas(**response.json())
            self.cas_cache[cas.number] = cas
            return cas

    def get_by_id(self, cas_id: str) -> Cas:
        """
        Retrieves a CAS by its ID.

        Parameters
        ----------
        cas_id : str
            The ID of the CAS to retrieve.

        Returns
        -------
        Cas
            The Cas object if found, None otherwise.
        """
        url = f"{self.base_url}/{cas_id}"
        response = requests.get(url, headers=self.client.headers)
        if response.status_code != 200:
            self.handle_api_error(response=response)
        cas = Cas(**response.json())
        self.cas_cache[cas.number] = cas
        return cas

    def get_by_number(self, number: str, exact_match: bool = True) -> Optional[Cas]:
        """
        Retrieves a CAS by its number.

        Parameters
        ----------
        number : str
            The number of the CAS to retrieve.
        exact_match : bool, optional
            Whether to match the number exactly, by default True.

        Returns
        -------
        Optional[Cas]
            The Cas object if found, None otherwise.
        """
        if number in self.cas_cache:
            return self.cas_cache[number]
        found = self.list(number=number)
        if exact_match:
            for f in found:
                if f.number == number:
                    return [f]
        return next(found, None)

    def delete(self, cas_id: str) -> bool:
        """
        Deletes a CAS by its ID.

        Parameters
        ----------
        cas_id : str
            The ID of the CAS to delete.

        Returns
        -------
        bool
            True if the CAS was successfully deleted, False otherwise.
        """
        url = f"{self.base_url}/{cas_id}"
        response = requests.delete(url, headers=self.client.headers)
        if response.status_code == 204:
            self._remove_from_cache_by_id(cas_id)
            return True
        else:
            return self.handle_api_error(response)

    def update(self, updated_object: BaseAlbertModel) -> BaseAlbertModel:
        # Fetch the current object state from the server or database
        current_object = self.get_by_id(updated_object.id)

        # Generate the PATCH payload
        patch_payload = self._generate_patch_payload(
            existing=current_object, updated=updated_object
        )

        url = f"{self.base_url}/{updated_object.id}"
        response = requests.patch(url, json=patch_payload, headers=self.client.headers)
        if response.status_code == 204:
            updated_cas = self.get_by_id(cas_id=updated_object.id)
            self._remove_from_cache_by_id(updated_object.id)
            self.cas_cache[updated_cas.number] = updated_cas
            return updated_cas
        else:
            return self.handle_api_error(response)
