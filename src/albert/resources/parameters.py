from enum import Enum

from pydantic import Field

from albert.resources.base import BaseAlbertModel


class ParameterCategory(str, Enum):
    NORMAL = "Normal"
    SPECIAL = "Special"


class Parameter(BaseAlbertModel):
    id: str | None = Field(alias="albertId")
    name: str
    category: ParameterCategory | None = Field(frozen=True, default=None)
    rank: int | None = Field(frozen=True, default=None)
