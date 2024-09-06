from albert.resources.base import BaseAlbertModel
from pydantic import Field
from typing import Optional


class Location(BaseAlbertModel):
    name: str
    id: Optional[str] = Field(None, alias="albertId")
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)
    address: Optional[str] = Field(None)
    country: Optional[str] = Field(None)
