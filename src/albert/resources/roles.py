from typing import Any

from pydantic import Field

from albert.resources.base import BaseAlbertModel


class Role(BaseAlbertModel):
    id: str = Field(alias="albertId")
    name: str
    policies: list[Any] | None = Field(None)
    tenant: str
