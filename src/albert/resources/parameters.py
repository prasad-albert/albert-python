from enum import Enum

from pydantic import Field, PrivateAttr

from albert.resources.base import BaseResource


class ParameterCategory(str, Enum):
    NORMAL = "Normal"
    SPECIAL = "Special"


class Parameter(BaseResource):
    id: str | None = Field(alias="albertId", default=None)
    name: str
    _category: ParameterCategory | None = PrivateAttr(default=None)
    _rank: int | None = PrivateAttr(default=None)

    @property
    def category(self) -> ParameterCategory:
        return self._category

    @property
    def rank(self) -> int:
        return self._rank
