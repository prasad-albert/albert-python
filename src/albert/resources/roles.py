from albert.resources.base import BaseAlbertModel
from pydantic import Field
from typing import Any, List, Optional


class Role(BaseAlbertModel):
    id: str = Field(alias="albertId")
    name: str
    policies: Optional[List[Any]] = Field(None)
    tenant: str
