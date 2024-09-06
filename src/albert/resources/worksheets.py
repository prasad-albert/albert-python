from albert.resources.sheets import Sheet
from albert.albert_session import AlbertSession
from pydantic import Field
from typing import List, Optional
from albert.resources.base import BaseAlbertModel
from albert.resources.base import BaseSessionModel


class Worksheet(BaseSessionModel):
    sheets: List[Sheet] = Field(alias="Sheets")
    project_name: Optional[str] = Field(None, alias="projectName")
    sheets_enabled: bool = Field(True, alias="sheetEnabled")
    project_id: str = Field(alias="projectId")
