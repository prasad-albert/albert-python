from enum import Enum

from pydantic import Field

from albert.collections.locations import Location
from albert.collections.roles import Role
from albert.resources.base import BaseAlbertModel, BaseEntityLink


class UserClass(str, Enum):
    GUEST = ("guest",)
    STANDARD = "standard"
    TRUSTED = "trusted"
    PRIVILEGED = "privileged"
    ADMIN = "admin"


class UserMetadata(BaseAlbertModel):
    sbu: str | None = Field(alias="SBU", default=None)


class User(BaseAlbertModel):
    """Represents a User on the Albert Platform"""

    id: str | None = Field(None, alias="albertId")
    name: str
    location: str | Location | BaseEntityLink | None = Field(None, alias="Location")
    email: str = Field(default=None, alias="email")
    roles: list[Role] | list[BaseEntityLink] = Field(
        max_length=1, default_factory=list, alias="Roles"
    )
    user_class: UserClass = Field(default=UserClass.STANDARD, alias="userClass")
    metadata: UserMetadata | None = Field(default=None, alias="Metadata")
