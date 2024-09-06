from enum import Enum
from albert.resources.base_resource import BaseAlbertModel
from pydantic import Field
from typing import Optional


class WGK(str, Enum):
    ONE = "1"
    TWO = "2"
    THREE = "3"


class CasCategory(str, Enum):
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
    def from_string(cls, *, number: str) -> "Cas":
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
