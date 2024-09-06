from enum import Enum
from typing import Any

from pydantic import Field, model_validator

from albert.resources.companies import Company
from albert.resources.tagged_base import BaseTaggedEntity
from albert.resources.tags import Tag


class ProjectCategory(str, Enum):
    DEVELOPMENT = "Development"
    RESEARCH = "Research"
    PRODUCTION = "Production"


class ProjectClass(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"


class Project(BaseTaggedEntity):
    """
    Project is a Pydantic model representing a project entity.

    Attributes
    ----------
    name : str
        The name of the project.
    description : str
        The description of the project.
    category : ProjectCategory
        The category of the project.
    project_class : Optional[ProjectClass]
        The classification of the project.
    tags : List[Tag]
        The tags associated with the project.
    id : Optional[str]
        The Albert ID of the project.
    company : Optional[Company]
        The company associated with the project.
    """

    name: str
    description: str
    category: ProjectCategory
    project_class: ProjectClass | None = None
    tags: list[Tag] = []
    id: str | None = Field(None, alias="projectId")
    company: Company | None = None

    @model_validator(mode="before")
    @classmethod
    def set_default_class(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Set the default project class to PUBLIC if none is provided.

        Parameters
        ----------
        values : Dict[str, Any]
            A dictionary of field values.

        Returns
        -------
        Dict[str, Any]
            Updated field values with a default project class if not provided.
        """
        if "project_class" not in values or values["project_class"] is None:
            values["project_class"] = ProjectClass.PUBLIC
        return values
