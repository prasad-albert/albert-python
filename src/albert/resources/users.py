from albert.resources.base_resource import BaseAlbertModel
from typing import Union, Optional, List
from pydantic import Field
from albert.collections.locations import Location
from albert.collections.roles import Role


class User(BaseAlbertModel):
    """Represents a User on the Albert Platform"""

    id: Optional[str] = Field(None, alias="albertId")
    name: str
    location: Optional[Union[str, Location]] = Field(None)
    email: str = Field(default=None, alias="email")
    roles: List[Role] = Field(default=[])
