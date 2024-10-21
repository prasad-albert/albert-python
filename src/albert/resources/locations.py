from pydantic import Field

from albert.resources.base import BaseResource, EntityLinkConvertible


class Location(BaseResource, EntityLinkConvertible):
    name: str
    id: str | None = Field(None, alias="albertId")
    latitude: float = Field()
    longitude: float = Field()
    address: str
    country: str | None = Field(None, max_length=2, min_length=2)
