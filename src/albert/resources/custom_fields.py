from enum import Enum

from pydantic import Field, model_validator

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
    hidden: bool | None = Field(default=None)
    lookup_column: bool | None = Field(default=None, alias="lkpColumn")
    lookup_row: bool | None = Field(default=None, alias="lkpRow")
    multiselect: bool | None = Field(default=None)
    category: FieldCategory | None = Field(default=None)
    min: int | None = Field(default=None)
    max: int | None = Field(default=None)
    entity_categories: list[EntityCategory] | None = Field(default=None, alias="entityCategory")
    ui_components: list[UIComponent] | None = Field(default=None, alias="ui_Components")

    @model_validator(mode="after")
    def confirm_field_compatability(self) -> "CustomField":
        if self.field_type == FieldType.LIST:
            if self.category is None:
                raise ValueError("Category must be set for list fields")
        elif self.field_type == FieldType.STRING:
            if self.searchable is not None:
                raise ValueError("Searchable must be None for string fields")
            if self.multiselect is not None:
                raise ValueError("Multiselect must be None for string fields")
        if self.lookup_column is not None and self.service != ServiceType.INVENTORIES:
            raise ValueError("Lookup column is only allowed for inventories")
        if self.lookup_row is not None and (
            self.service != ServiceType.INVENTORIES
            or (
                self.service == ServiceType.INVENTORIES
                and (
                    self.entity_categories is not None
                    and EntityCategory.FORMULAS not in self.entity_categories
                )
            )
        ):
            raise ValueError("Lookup row is only allowed for formulas in inventories")
        return self
