from enum import Enum

from pydantic import Field, field_serializer

from albert.collections.locations import Location
from albert.collections.roles import Role
from albert.resources.base import BaseAlbertModel, BaseEntityLink, EntityLinkConvertible
from albert.resources.serialization import serialize_to_entity_link, serialize_to_entity_link_list


class UserClass(str, Enum):
    GUEST = "guest"
    STANDARD = "standard"
    TRUSTED = "trusted"
    PRIVILEGED = "privileged"
    ADMIN = "admin"


class UserMetadata(BaseAlbertModel):
    sbu: str | None = Field(alias="SBU", default=None)


class User(BaseAlbertModel, EntityLinkConvertible):
    """Represents a User on the Albert Platform"""

    id: str | None = Field(None, alias="albertId")
    name: str
    location: Location | BaseEntityLink | None = Field(None, alias="Location")
    email: str = Field(default=None, alias="email")
    roles: list[Role | BaseEntityLink] = Field(max_length=1, default_factory=list, alias="Roles")
    user_class: UserClass = Field(default=UserClass.STANDARD, alias="userClass")
    metadata: UserMetadata | None = Field(default=None, alias="Metadata")

    location_serializer = field_serializer("location")(serialize_to_entity_link)
    roles_serializer = field_serializer("roles")(serialize_to_entity_link_list)
