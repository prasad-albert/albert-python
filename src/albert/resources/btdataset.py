from pydantic import Field

from albert.resources.base import BaseResource, EntityLink


class BTDataset(BaseResource):
    name: str
    id: str | None = Field(default=None, alias="albertId")
    key: str | None = Field(default=None)
    file_name: str | None = Field(default=None, alias="fileName")
    report: EntityLink | None = Field(default=None, alias="Report")
