from pydantic import Field, model_validator

from albert.resources.base import BaseSessionModel
from albert.resources.sheets import Sheet


class Worksheet(BaseSessionModel):
    sheets: list[Sheet] = Field(alias="Sheets")
    project_name: str | None = Field(default=None, alias="projectName")
    sheets_enabled: bool = Field(default=True, alias="sheetEnabled")
    project_id: str = Field(alias="projectId")

    @model_validator(mode="after")
    def add_session_to_sheets(self):
        if self.session is not None:
            for s in self.sheets:
                s.session = self.session
                for d in s.designs:
                    d.session = self.session
        return self
