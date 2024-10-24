from enum import Enum
from typing import Any

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

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Default to exclude_unset=True so the old value is dropped when not expliclty passed."""
        kwargs.setdefault("exclude_unset", True)
        return super().model_dump(**kwargs)
