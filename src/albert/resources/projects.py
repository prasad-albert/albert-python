from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, PrivateAttr

from albert.resources.acls import ACL
from albert.resources.base import BaseAlbertModel, EntityLinkConvertible
from albert.resources.locations import Location
from albert.resources.serialization import SerializeAsEntityLink


class ProjectClass(str, Enum):
    SHARED = "shared"
    PUBLIC = "public"
    CONFIDENTIAL = "confidential"
    PRIVATE = "private"


class State(str, Enum):
    NOT_STARTED = "Not Started"
    ACTIVE = "Active"
    CLOSED_SUCCESS = "Closed - Success"
    CLOSED_ARCHIVED = "Closed - Archived"


class TaskConfig(BaseModel):
    datatemplateId: str | None = None
    workflowId: str | None = None
    defaultTaskName: str | None = None
    target: str | None = None
    hidden: bool | None = False


class GridDefault(str, Enum):
    PD = "PD"
    WKS = "WKS"


class Project(BaseAlbertModel, EntityLinkConvertible):
    description: str = Field(min_length=1, max_length=2000)
    locations: list[SerializeAsEntityLink[Location]] | None = Field(
        default=None, min_length=1, max_length=20, alias="Locations"
    )
    project_class: ProjectClass | None = Field(default=ProjectClass.PRIVATE, alias="class")
    prefix: str | None = Field(default=None)
    application_engineering_inventory_ids: list[str] | None = Field(
        default=None,
        alias="appEngg",
        description="Inventory Ids to be added as application engineering",
    )
    id: str | None = Field(None, alias="albertId")
    acl: list[ACL] | None = Field(default_factory=list, alias="ACL")
    old_api_params: dict | None = None
    task_config: list[TaskConfig] | None = Field(default_factory=list)
    grid: GridDefault | None = None
    metadata: dict[str, Any] | None = Field(alias="Metadata", default=None)
    _state: State | None = PrivateAttr(default=None)

    def __init__(self, **data: Any):
        super().__init__(**data)
        if "state" in data:
            self._state = data["state"]

    @property
    def state(self):
        return self._state
