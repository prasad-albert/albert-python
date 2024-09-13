from pydantic import Field

from albert.resources.base import BaseSessionModel
from albert.resources.sheets import Sheet


class Worksheet(BaseSessionModel):
    sheets: list[Sheet] = Field(alias="Sheets")
    project_name: str | None = Field(default=None, alias="projectName")
    sheets_enabled: bool = Field(default=True, alias="sheetEnabled")
    project_id: str = Field(alias="projectId")
