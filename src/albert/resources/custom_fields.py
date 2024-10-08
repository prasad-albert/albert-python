from enum import Enum

from pydantic import Field

from albert.resources.base import BaseAlbertModel


class FieldType(str, Enum):
    LIST = "list"
    STRING = "string"


class ServiceType(str, Enum):
    INVENTORIES = "inventories"
    LOTS = "lots"
    PROJECTS = "projects"
    TASKS = "tasks"
    USERS = "users"


class FieldCategory(str, Enum):
    BUSINESS_DEFINED = "businessDefined"
    USER_DEFINED = "userDefined"


class EntityCategory(str, Enum):
    FORMULAS = "Formulas"
    RAW_MATERIALS = "RawMaterials"
    CONSUMABLES = "Consumables"
    EQUIPMENT = "Equipment"
    PROPERTY = "Property"
    BATCH = "Batch"
    GENERAL = "General"


class UIComponent(str, Enum):
    CREATE = "create"
    DETAILS = "details"


class CustomField(BaseAlbertModel):
    name: str
    id: str | None = Field(default=None, alias="albertId")
    field_type: FieldType = Field(alias="type")
    display_name: str = Field(default=None, alias="labelName")
    searchable: bool | None = Field(default=None)
    service: ServiceType
    hidden: bool = Field(default=False)
    lookup_column: bool | None = Field(default=None, alias="lkpColumn")
    lookup_row: bool | None = Field(default=None, alias="lkpRow")
    multiselect: bool | None = Field(default=None)
    category: FieldCategory | None = Field(default=None)
    min: int | None = Field(default=None)
    max: int | None = Field(default=None)
    entity_categories: list[EntityCategory] | None = Field(default=None, alias="entityCategory")
    ui_components: list[UIComponent] | None = Field(default=None, alias="ui_Components")
