from typing import Any

from pydantic import Field

from albert.resources.base import BaseResource, EntityLinkConvertible


class Role(BaseResource, EntityLinkConvertible):
    id: str = Field(alias="albertId")
    name: str
    policies: list[Any] | None = Field(default=None)
    tenant: str
