from enum import Enum
from typing import Any

from pydantic import Field

from albert.resources.base import BaseResource
from albert.resources.identifiers import BTDatasetId, BTModelId, BTModelSessionId
from albert.utils.types import BaseAlbertModel


class BTModelType(str, Enum):
    SESSION = "Session"
    DETACHED = "Detached"


class BTModelCategory(str, Enum):
    USER_MODEL = "userModel"
    ALBERT_MODEL = "albertModel"


class BTModelState(str, Enum):
    QUEUED = "Queued"
    BUILDING_MODELS = "Building Models"
    GENERATING_CANDIDATES = "Generating Candidates"
    COMPLETE = "Complete"
    ERROR = "Error"


class BTModelRegistry(BaseAlbertModel):
    build_logs: dict[str, Any] | None = Field(None, alias="BuildLogs")
    metrics: dict[str, Any] | None = Field(None, alias="Metrics")


class BTModelSession(BaseResource, protected_namespaces=()):
    name: str
    category: BTModelCategory
    id: BTModelSessionId | None = Field(default=None)
    dataset_id: BTDatasetId = Field(..., alias="datasetId")
    default_model: str | None = Field(default=None, alias="defaultModel")
    total_time: str | None = Field(default=None, alias="totalTime")
    model_count: int | None = Field(default=None, alias="modelCount")
    target: list[str] | None = Field(default=None)
    registry: BTModelRegistry | None = Field(default=None, alias="Registry")
    albert_model_details: dict[str, Any] | None = Field(default=None, alias="albertModelDetails")
    flag: bool = Field(default=False)


class BTModel(BaseResource, protected_namespaces=()):
    name: str
    id: BTModelId | None = Field(default=None)
    dataset_id: BTDatasetId | None = Field(default=None, alias="datasetId")
    parent_id: BTModelSessionId | None = Field(default=None, alias="parentId")
    metadata: dict[str, Any] | None = Field(default=None, alias="Metadata")
    type: BTModelType | None = Field(default=None)
    state: BTModelState | None = Field(default=None)
    target: list[str] | None = Field(default=None)
    start_time: str | None = Field(default=None, alias="startTime")
    end_time: str | None = Field(default=None, alias="endTime")
    total_time: str | None = Field(default=None, alias="totalTime")
    model_binary_key: str | None = Field(default=None, alias="modelBinaryKey")
    flag: bool = Field(default=False)
