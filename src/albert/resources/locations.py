
from pydantic import Field

from albert.resources.base import BaseAlbertModel


class Location(BaseAlbertModel):
    name: str
    id: str | None = Field(None, alias="albertId")
    latitude: float | None = Field(None)
    longitude: float | None = Field(None)
    address: str | None = Field(None)
    country: str | None = Field(None)
