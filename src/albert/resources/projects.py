from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, PrivateAttr, field_serializer, model_validator

from albert.resources.acls import ACL
from albert.resources.base import BaseAlbertModel, BaseEntityLink, EntityLinkConvertible
from albert.resources.locations import Location
from albert.resources.serialization import serialize_to_entity_link_list


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


class Metadata(BaseModel):
    adpNumber: str | None = Field(default=None, min_length=1, max_length=255)
    segment: str | None = Field(default=None, min_length=1, max_length=255)
    applications: list[BaseEntityLink] | None = Field(default_factory=list, max_length=20)
    technologies: list[BaseEntityLink] | None = Field(default_factory=list, max_length=20)
    sub_categories: list[BaseEntityLink] | None = Field(default_factory=list, max_length=20)
    adpType: list[BaseEntityLink] | None = Field(default_factory=list, max_length=20)


class Project(BaseAlbertModel, EntityLinkConvertible):
    description: str = Field(min_length=1, max_length=2000)
    locations: list[Location | BaseEntityLink] | None = Field(
        default=None, min_length=1, max_length=20, alias="Locations"
    )
    project_class: ProjectClass | None = Field(default=None, alias="class")
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
    metadata: Metadata | None = Field(alias="Metadata", default=None)
    _state: State | None = PrivateAttr(default=None)

    locations_serializer = field_serializer("locations")(serialize_to_entity_link_list)

    def __init__(self, **data: Any):
        super().__init__(**data)
        if "state" in data:
            self._state = data["state"]

    @property
    def state(self):
        return self._state

    @model_validator(mode="before")
    @classmethod
    def set_default_class(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
            Set the default project class to PRIVATE if none is provided.

        #     Parameters
        #     ----------
        #     values : Dict[str, Any]
        #         A dictionary of field values.

            Returns
            -------
            Dict[str, Any]
                Updated field values with a default project class if not provided.
        """
        if "project_class" not in values or values["project_class"] is None:
            values["project_class"] = ProjectClass.PRIVATE
        return values
