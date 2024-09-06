
from pydantic import Field

from albert.collections.locations import Location
from albert.collections.roles import Role
from albert.resources.base import BaseAlbertModel


class User(BaseAlbertModel):
    """Represents a User on the Albert Platform"""

    id: str | None = Field(None, alias="albertId")
    name: str
    location: str | Location | None = Field(None)
    email: str = Field(default=None, alias="email")
    roles: list[Role] = Field(default=[])
