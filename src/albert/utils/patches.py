from enum import Enum

from pydantic import Field

from albert.utils.types import BaseAlbertModel

PatchValue = str | int | float | list | dict | BaseAlbertModel | None


class PatchOperation(str, Enum):
    ADD = "add"
    UPDATE = "update"
    DELETE = "delete"


class PatchDatum(BaseAlbertModel):
    operation: str
    attribute: str
    new_value: PatchValue = Field(..., alias="newValue")
    old_value: PatchValue = Field(default=None, alias="oldValue")


class PatchPayload(BaseAlbertModel):
    data: list[PatchDatum]
