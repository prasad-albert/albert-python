from pydantic import Field

from albert.resources.base import BaseResource, EntityLinkConvertible
from albert.resources.locations import Location
from albert.resources.serialization import SerializeAsEntityLink


class StorageLocation(BaseResource, EntityLinkConvertible):
    id: str | None = Field(alias="albertId", default=None)
    name: str = Field(alias="name", min_length=2, max_length=255)
    location: SerializeAsEntityLink[Location] = Field(alias="Location")
