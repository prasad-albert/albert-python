from pydantic import Field

from albert.resources.base import BaseResource


class DataColumn(BaseResource):
    name: str
    defalt: bool = False
    id: str = Field(None, alias="albertId")
