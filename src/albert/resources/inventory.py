from enum import Enum
from typing import Any

from pydantic import Field, PrivateAttr, model_validator

from albert.collections.cas import Cas
from albert.collections.companies import Company
from albert.collections.tags import Tag
from albert.collections.un_numbers import UnNumber
from albert.resources.acls import ACL
from albert.resources.base import BaseAlbertModel, BaseEntityLink, SecurityClass
from albert.resources.locations import Location
from albert.resources.serialization import SerializeAsEntityLink
from albert.resources.tagged_base import BaseTaggedEntity
from albert.utils.exceptions import AlbertException


class InventoryCategory(str, Enum):
    RAW_MATERIALS = "RawMaterials"
    CONSUMABLES = "Consumables"
    EQUIPMENT = "Equipment"
    FORMULAS = "Formulas"


class InventoryUnitCategory(str, Enum):
    MASS = "mass"
    VOLUME = "volume"
    LENGTH = "length"
    PRESSURE = "pressure"
    UNITS = "units"


class CasAmount(BaseAlbertModel):
    """
    CasAmount is a Pydantic model representing an amount of a given CAS.

    Attributes
    ----------
    id : str
        The unique identifier of the CAS Number this amount represents.
    min : float, optional
        The minimum amount of the CAS in the formulation.
    max : float, optional
        The maximum amount of the CAS in the formulation.
    _cas : Cas
        The CAS object associated with this amount.
    """

    id: str
    min: float = Field(default=None)
    max: float = Field(default=None)

    # Define a private attribute to store the Cas object
    _cas: Cas = PrivateAttr(None)

    @model_validator(mode="before")
    def ensure_floats_and_cas(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Ensure that min and max are floats and handle the CAS object initialization.
        """

        # Ensure min and max are converted to floats if necessary
        min_val = values.get("min")
        max_val = values.get("max")

        if isinstance(min_val, int):
            values["min"] = float(min_val)
        if isinstance(max_val, int):
            values["max"] = float(max_val)

        # If a Cas object is provided, update the id field
        cas = values.get("cas")
        if cas and isinstance(cas, Cas):
            values["id"] = cas.id

        return values

    @model_validator(mode="after")
    def set_cas_private_attr(cls, values: "CasAmount"):
        """
        Set the _cas attribute after model initialization.
        """
        if hasattr(values, "cas") and isinstance(values.cas, Cas):
            values._cas = values.cas  # Set the private _cas attribute

        return values


class InventoryMinimum(BaseAlbertModel):
    """
    InventoryMinimum is a Pydantic model representing the minimum amount of an inventory item.

    Attributes
    ----------
    id : str
        The unique identifier of the minimum amount.
    min : float
        The minimum amount of the inventory item.
    max : float
        The maximum amount of the inventory item.
    """

    location: Location | None = Field(exclude=True, default=None)
    id: str = Field(default=None)
    minimum: float = Field(gt=0, lt=1000000000000000)

    @model_validator(mode="before")
    def check_id_or_location(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Ensure that either an id or a location is provided.
        """
        if not values.get("id") and not values.get("location"):
            raise AlbertException(
                "Either an id or a location must be provided for an InventoryMinimum."
            )

        if values.get("id") and values.get("location"):
            raise AlbertException(
                "Only an id or a location can be provided for an InventoryMinimum, not both."
            )

        if values.get("location"):
            values["id"] = values["location"]["id"]
            values["name"] = values["location"]["name"]

        return values


class InventoryMetadata(BaseAlbertModel):
    IDH: list[BaseEntityLink] | None = Field(
        default=None,
        description="List of IDH objects, unique items, each having an id and a name.",
    )
    RSN: str | None = Field(
        default=None, min_length=1, max_length=50, description="RSN identifier."
    )
    RSNe: str | None = Field(
        default=None, min_length=1, max_length=50, description="RSNe identifier."
    )
    INCIName: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="INCI name of the substance.",
    )
    substanceNumber: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Substance number of the inventory.",
    )
    RMFMCode: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="RMFM Code of the raw material or formula.",
    )
    productCode: str | None = Field(
        default=None,
        min_length=1,
        max_length=40,
        description="Product code of the item.",
    )
    articleNumber: str | None = Field(
        default=None,
        max_length=50,
        description="Article number associated with the item.",
    )
    uvpNumber: str | None = Field(
        default=None,
        max_length=50,
        description="UVP number associated with the item.",
    )
    CuD: str | None = Field(default=None, max_length=50, description="CuD metadata field.")
    features: str | None = Field(default=None, description="Features metadata field.")
    solubility: str | None = Field(default=None, description="Solubility metadata field.")
    potentialApplications: str | None = Field(
        default=None, description="Potential applications metadata field."
    )
    compatibility: str | None = Field(default=None, description="Compatibility metadata field.")
    packaging: str | None = Field(default=None, description="Packaging metadata field.")
    storageRecommendation: str | None = Field(
        default=None, description="Storage recommendation metadata field."
    )
    equipmentType: BaseEntityLink | None = Field(
        default=None, description="Equipment type for the inventories under Equipment category."
    )
    articleStatus: BaseEntityLink | None = Field(
        default=None, description="Article status of the inventory, with an id and name."
    )


class InventoryItem(BaseTaggedEntity):
    """
    InventoryItem is a Pydantic model representing an inventory item.

    Attributes
    ----------
    name : str
        The name of the inventory item.
    description : Optional[str]
        The description of the inventory item.
    category : InventoryCategory
        The category of the inventory item.
    project_id : Optional[str]
        Reqired for Formulas
    unit_category : Optional[UnitCategory]
        The unit category of the inventory item.
    tags : Optional[List[Union[Tag,str]]]
        The tags associated with the inventory item.
    cas : Optional[str]
        The CAS number of the inventory item.
    security_class : Optional[SecurityClass]
        The class of the inventory item.
    id : Optional[str]
        The Albert ID of the inventory item.
    company : Optional[Company]
        The company associated with the inventory item.
    """

    id: str | None = Field(None, alias="albertId")
    name: str | None = None
    description: str | None = None
    category: InventoryCategory
    unit_category: InventoryUnitCategory = Field(default=None, alias="unitCategory")
    security_class: SecurityClass | None = Field(default=None, alias="class")
    company: SerializeAsEntityLink[Company] | None = Field(default=None, alias="Company")
    minimum: list[InventoryMinimum] | None = Field(default=None)  # To do
    alias: str | None = Field(default=None)
    cas: list[CasAmount] | None = Field(default=None, alias="Cas")
    metadata: InventoryMetadata | None = Field(default=None, alias="Metadata")
    _task_config: list[dict] | None = PrivateAttr(default=None)
    _formula_id: str | None = PrivateAttr(default=None)
    _project_id: str | None = PrivateAttr(default=None)
    _symbols: list[dict] | None = PrivateAttr(default=None)  # read only: comes from attachments
    _un_number: UnNumber | None = PrivateAttr(default=None)  # Read only: Comes from attachments
    _acls: list[ACL] | None = PrivateAttr(default=None)  # read only

    def __init__(self, **data: Any):
        super().__init__(**data)
        # handle aliases on private attributes
        if "ACL" in data:
            self._acls = data["ACL"]
        if "unNumber" in data:
            self._un_number = data["unNumber"]
        if "Symbols" in data:
            self._symbols = data["Symbols"]
        if "TaskConfig" in data:
            self._task_config = data["TaskConfig"]
        if "Minimum" in data:
            self._minimum = data["Minimum"]
        if "formulaId" in data:
            self._formula_id = data["formulaId"]
        if "parentId" in data:
            self._project_id = data["parentId"]

    @model_validator(mode="before")
    @classmethod
    def set_unit_category(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Set the unit category based on the inventory category.

        Parameters
        ----------
        values : Dict[str, Any]
            A dictionary of field values.

        Returns
        -------
        Dict[str, Any]
            Updated field values with unit category set.
        """
        category = values.get("category")
        unit_category = values.get("unit_category")
        if unit_category is None:
            if category in (
                InventoryCategory.RAW_MATERIALS,
                InventoryCategory.RAW_MATERIALS.value,
                InventoryCategory.FORMULAS,
                InventoryCategory.FORMULAS.value,
            ):
                values["unit_category"] = InventoryUnitCategory.MASS.value
            elif category in (
                InventoryCategory.EQUIPMENT,
                InventoryCategory.EQUIPMENT.value,
                InventoryCategory.CONSUMABLES,
                InventoryCategory.CONSUMABLES.value,
            ):
                values["unit_category"] = InventoryUnitCategory.UNITS.value
        return values

    @model_validator(mode="before")
    @classmethod
    def convert_company(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Convert the company field to a Company object if it is a string.

        Parameters
        ----------
        data : Dict[str, Any]
            A dictionary of field values.

        Returns
        -------
        Dict[str, Any]
            Updated field values with company converted.
        """
        company = data.get("company", data.get("Company"))
        if company:
            if isinstance(company, Company):
                data["company"] = company
            elif isinstance(company, str):
                data["company"] = Company(name=company)
            else:
                pass
                # We do not expect this else to be hit because comapanies should only be Tag or str
        return data

    @model_validator(mode="before")
    @classmethod
    def ensure_formula_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Ensure required fields are present for formulas.

        Parameters
        ----------
        data : Dict[str, Any]
            A dictionary of field values.

        Returns
        -------
        Dict[str, Any]
            Updated field values with required fields ensured.

        Raises
        ------
        AttributeError
            If a required project_id is missing for formulas.
        """
        category_raw = data.get("category")
        category = (
            category_raw
            if category_raw is None or isinstance(category_raw, str)
            else category_raw.value
        )
        if category == "Formulas":
            this_project = data.get("project_id")
            if not this_project and not data.get("albertId"):
                # Some on platform formulas somehow don't have a project_id so check if its already on platform
                raise AttributeError("A project_id must be supplied for all formulas.")
        return data

    @property
    def formula_id(self) -> str | None:
        return self._formula_id

    @property
    def project_id(self) -> str | None:
        return self._project_id
