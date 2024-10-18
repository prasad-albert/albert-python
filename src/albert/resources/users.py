from enum import Enum
from typing import Any

from pydantic import Field, EmailStr

from albert.collections.locations import Location
from albert.collections.roles import Role
from albert.resources.base import BaseAlbertModel, EntityLinkConvertible
from albert.resources.serialization import SerializeAsEntityLink


class UserClass(str, Enum):
    GUEST = "guest"
    STANDARD = "standard"
    TRUSTED = "trusted"
    PRIVILEGED = "privileged"
    ADMIN = "admin"


class User(BaseAlbertModel, EntityLinkConvertible):
    """Represents a User on the Albert Platform"""

    id: str | None = Field(None, alias="albertId")
    name: EmailStr
    location: SerializeAsEntityLink[Location] | None = Field(default=None, alias="Location")
    email: str = Field(default=None, alias="email")
    roles: list[SerializeAsEntityLink[Role]] = Field(
        max_length=1, default_factory=list, alias="Roles"
    )
    user_class: UserClass = Field(default=UserClass.STANDARD, alias="userClass")
    metadata: dict[str, Any] | None = Field(alias="Metadata", default=None)
