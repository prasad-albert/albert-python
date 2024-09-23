from typing import Any

from pydantic import Field

from albert.resources.base import BaseAlbertModel, EntityLinkConvertible


class Role(BaseAlbertModel, EntityLinkConvertible):
    id: str = Field(alias="albertId")
    name: str
    policies: list[Any] | None = Field(default=None)
    tenant: str
