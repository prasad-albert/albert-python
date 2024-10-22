from enum import Enum

from pydantic import Field

from albert.resources.base import BaseResource, BaseSessionResource
from albert.utils.exceptions import AlbertException


class BTModelCategory(str, Enum):
    USER_MODEL = "userModel"
    ALBERT_MODEL = "albertModel"


class BTModelState(str, Enum):
    QUEUED = "Queued"
    BUILDING_MODELS = "Building Models"
    GENERATING_CANDIDATES = "Generating Candidates"
    COMPLETE = "Complete"
    ERROR = "Error"


class BTModelSession(BaseSessionResource):
    name: str
    dataset_id: str
    category: BTModelCategory
    id: str | None = Field(default=None)
    default_model: str | None = Field(default=None, alias="defaultModel")
    total_time: str | None = Field(default=None, alias="totalTime")
    model_count: int | None = Field(default=None, alias="modelCount")
    target: list[str] | None = Field(default=None)
    flag: bool = Field(default=False)

    @property
    def models(self):
        from albert.collections.btmodel import BTModelCollection

        if self.session is None:
            raise AlbertException("Parent entity is missing a session.")
        if self.id is None:
            raise AlbertException("Parent entity is missing an Albert ID.")

        return BTModelCollection(session=self.session, parent_id=self.id)


class BTModel(BaseResource):
    name: str
    dataset_id: str
    id: str | None = Field(default=None)
    parent_id: str | None = Field(default=None, alias="parentId")
    start_time: str | None = Field(default=None, alias="startTime")
    end_time: str | None = Field(default=None, alias="endTime")
    total_time: str | None = Field(default=None, alias="totalTime")
    target: list[str] | None = Field(default=None)
    state: BTModelState | None = Field(default=None)
    flag: bool = Field(default=False)
