from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from albert.session import AlbertSession


class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AuditFields(BaseModel):
    by: str = Field(None)
    by_name: str | None = Field(None, alias="byName")
    at: datetime | None = Field(None)


class BaseAlbertModel(BaseModel):
    _created: AuditFields | None = PrivateAttr(default=None)
    _updated: AuditFields | None = PrivateAttr(default=None)
    status: Status | None = Field(default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        exclude={"session"},
        arbitrary_types_allowed=True,
    )

    def __init__(self, **data: Any):
        """
        Initialize a Base resource instance.
        """
        super().__init__(**data)
        if "Created" in data:
            self._created = AuditFields(**data["Created"])
        if "Updated" in data:
            self._updated = AuditFields(**data["Updated"])

    @property
    def created(self) -> AuditFields | None:
        return self._created

    @property
    def updated(self) -> AuditFields | None:
        return self._updated


class BaseSessionModel(BaseAlbertModel):
    session: AlbertSession | None = Field(
        default=None,
        description=(
            "Albert session for accessing the Albert API. "
            "The session is included as an optional field to allow for models of this type "
            "to be created independently from calls to the API."
        ),
    )

    def to_entity_link(self):
        if hasattr(self, "id"):
            this_link = BaseEntityLink(id=self.id)
            if hasattr(self, "name"):
                this_link.name = self.name
            return this_link
        else:
            ValueError(
                "`id` is required to create an entity link. Ensure the linked object is registered."
            )


class BaseEntityLink(BaseAlbertModel):
    id: str
    name: str | None = Field(default=None)
