from typing import List, Optional, Dict, Any
from enum import Enum
from albert.collections.tags import Tag
from albert.collections.cas import Cas
from albert.collections.companies import Company
from pydantic import Field, model_validator, PrivateAttr
from albert.resources.tagged_base import BaseTaggedEntity
from albert.resources.base import BaseAlbertModel
from albert.collections.un_numbers import UnNumber


class InventoryCategory(str, Enum):
    RAW_MATERIALS = "RawMaterials"
    CONSUMABLES = "Consumables"
    EQUIPMENT = "Equipment"
    FORMULAS = "Formulas"


class UnitCategory(str, Enum):
    MASS = "mass"
    VOLUME = "volume"
    LENGTH = "length"
    PRESSURE = "pressure"
    UNITS = "units"


class InventoryClass(str, Enum):
    SHARED = "shared"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    PRIVATE = "private"
    PUBLIC = "public"


class CasAmount(BaseAlbertModel):
    """
    CasAmount is a Pydantic model representing an amount of a given CAS.

    Attributes
    ----------
    id : str
        The unique identifier of the CAS amount.
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

    def __init__(
        self, cas: Cas = None, min: float = None, max: float = None, **data: Any
    ):
        """
        CasAmount is a Pydantic model representing an amount of a given Cas.

        Attributes
        ----------
        cas : Cas oject
            The Cas Object albert.entity.cas.Cas
        min : float
            The minimum amount of the given cas in the formulation.
        max : float
            The maximum amount of the given cas in the formulation.
        """

        if cas:
            # Initialize with a Cas object
            super().__init__(id=cas.id, min=min, max=max, **data)
            self._cas = cas
        else:
            # Initialize with id, min, and max (for deserialization)
            super().__init__(**data)
            self._cas = None


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
    inventory_class : Optional[InventoryClass]
        The class of the inventory item.
    id : Optional[str]
        The Albert ID of the inventory item.
    company : Optional[Company]
        The company associated with the inventory item.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    category: InventoryCategory
    unit_category: UnitCategory = Field(default=None, alias="unitCategory")
    inventory_class: Optional[InventoryClass] = Field(default=None, alias="class")
    id: Optional[str] = Field(None, alias="albertId")
    company: Optional[Company] = Field(default=None, alias="Company")
    tags: Optional[List[Tag]] = Field(default=[], alias="Tags")
    formula_id: Optional[str] = Field(default=None, alias="formulaId")
    project_id: Optional[str] = Field(default=None, alias="parentId")
    # alias: Optional[str] = Field(default=None)
    cas: Optional[List[CasAmount]] = Field(default=None, alias="Cas")
    _task_config: Optional[List[Dict]] = PrivateAttr(
        default=None
    )  # Read only: comes from task generation
    _symbols: Optional[List[Dict]] = PrivateAttr(
        default=None
    )  # read only: comes from attachments
    _un_number: Optional[UnNumber] = PrivateAttr(
        default=None
    )  # Read only: Comes from attachments
    _acls: Optional[List[Dict]] = PrivateAttr(default=None)  # read only
    _metadata: Optional[List[Dict]] = PrivateAttr(default=None)  # read only
    _minimum: Optional[List[Dict[str, Any]]] = PrivateAttr(default=None)  # To do

    def __init__(self, **data: Any):
        """
        Initalize an an inventory item.

        Attributes
        ----------
        name : str
            The name of the inventory item.
        description : Optional[str]
            The description of the inventory item.
        category : InventoryCategory
            The category of the inventory item.
        unit_category : Optional[UnitCategory]
            The unit category of the inventory item.
        tags : Optional[List[Union[Tag,str]]]
            The tags associated with the inventory item.
        cas : Optional[str]
            The CAS number of the inventory item.
        inventory_class : Optional[InventoryClass]
            The class of the inventory item.
        id : Optional[str]
            The Albert ID of the inventory item.
        company : Optional[Company]
            The company associated with the inventory item.
        """

        super().__init__(**data)
        # handle aliases on private attributes
        if "ACL" in data:
            self._acls = data["ACL"]
        if "Metadata" in data:
            self._metadata = data["Metadata"]
        if "unNumber" in data:
            self._un_number = data["unNumber"]
        if "Symbols" in data:
            self._symbols = data["Symbols"]
        if "TaskConfig" in data:
            self._task_config = data["TaskConfig"]
        if "Minimum" in data:
            self._minimum = data["Minimum"]

    @model_validator(mode="before")
    @classmethod
    def set_unit_category(cls, values: Dict[str, Any]) -> Dict[str, Any]:
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
                values["unit_category"] = UnitCategory.MASS.value
            elif category in (
                InventoryCategory.EQUIPMENT,
                InventoryCategory.EQUIPMENT.value,
                InventoryCategory.CONSUMABLES,
                InventoryCategory.CONSUMABLES.value,
            ):
                values["unit_category"] = UnitCategory.UNITS.value
        return values

    @model_validator(mode="before")
    @classmethod
    def convert_company(cls, data: Dict[str, Any]) -> Dict[str, Any]:
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
        company = data.get("company", data.get("Company", None))
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
    def ensure_formula_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
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
        category_raw = data.get("category", None)
        category = (
            category_raw
            if category_raw is None or isinstance(category_raw, str)
            else category_raw.value
        )
        if category == "Formulas":
            this_project = data.get("project_id", None)
            if not this_project:
                # Some on platform formulas somehow don't have a project_id so check if its already on platform
                if not data.get("albertId", None):
                    raise AttributeError(
                        "A project_id must be supplied for all formulas."
                    )
        return data

    def _to_create_api(self):
        """
        Convert the model to a dictionary suitable for API creation requests.

        Returns
        -------
        Dict[str, Any]
            A dictionary representation of the model suitable for API requests.
        """
        dumped_model = self.model_dump(by_alias=True, exclude_none=True)
        if "Company" in dumped_model:
            if "albertId" in dumped_model["Company"]:
                dumped_model["Company"] = {"id": dumped_model["Company"]["albertId"]}
        if "Tags" in dumped_model:
            new_tags = []
            for t in dumped_model["Tags"]:
                if "albertId" in t:
                    new_tags.append({"id": t["albertId"]})
        if len(new_tags) > 0:
            dumped_model["Tags"] = new_tags
        else:
            del dumped_model["Tags"]
        return dumped_model
