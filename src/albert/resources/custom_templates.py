import logging
from enum import Enum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from albert.resources.base import BaseAlbertModel


class TemplateCategory(str, Enum):
    PROPERTY_LIST = "Property Task"
    PROPERTY = "Property"
    BATCH = "Batch"
    SHEET = "Sheet"
    NOTEBOOK = "Notebook"
    GENERAL = "General"


class GeneralData(BaseAlbertModel):
    category: Literal[TemplateCategory.GENERAL]


class BatchData(BaseAlbertModel):
    category: Literal[TemplateCategory.BATCH]


class PropertyData(BaseAlbertModel):
    category: Literal[TemplateCategory.PROPERTY]


class SheetData(BaseAlbertModel):
    category: Literal[TemplateCategory.SHEET]


class NotebookData(BaseAlbertModel):
    category: Literal[TemplateCategory.NOTEBOOK]


CustomTemplateData = Annotated[
    PropertyData | BatchData | SheetData | NotebookData | GeneralData,
    Field(discriminator="category"),
]


class CustomTemplate(BaseAlbertModel):
    id: str = Field(alias="albertId")
    name: str
    category: TemplateCategory = Field(default=TemplateCategory.GENERAL)
    metadata: dict | None = Field(default=None, alias="Metadata")
    data: None | CustomTemplateData = Field(default=None, alias="Data")

    # # Custom root validator to handle fallback to GeneralData when category is missing
    # @model_validator(mode="before")
    # def set_general_data_as_fallback(cls, values):
    #     data = values.get("Data")
    #     print("1")
    #     print(data)
    #     # Check if the "category" field is missing in "Data"
    #     if not data or data and "category" not in data:
    #         # If "category" is missing, fallback to GeneralData
    #         values["Data"]["category"] = TemplateCategory.GENERAL.value
    #     return values
