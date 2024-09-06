from pydantic import Field

from albert.resources.base import BaseSessionModel
from albert.resources.sheets import Sheet


class Worksheet(BaseSessionModel):
    sheets: list[Sheet] = Field(alias="Sheets")
    project_name: str | None = Field(None, alias="projectName")
    sheets_enabled: bool = Field(True, alias="sheetEnabled")
    project_id: str = Field(alias="projectId")
