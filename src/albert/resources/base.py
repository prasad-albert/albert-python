from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

from albert.session import AlbertSession


class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class SecurityClass(str, Enum):
    SHARED = "shared"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    PRIVATE = "private"
    PUBLIC = "public"


class AuditFields(BaseModel):
    by: str = Field(None)
    by_name: str | None = Field(None, alias="byName")
    at: datetime | None = Field(None)


class BaseAlbertModel(BaseModel):
    _created: AuditFields | None = PrivateAttr(default=None)
    _updated: AuditFields | None = PrivateAttr(default=None)
    _status: Status | None = PrivateAttr(default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        exclude={"session"},
        arbitrary_types_allowed=True,
    )

    @model_validator(mode="before")
    @classmethod
    def initialize_private_attrs(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Initialize private attributes from the incoming data dictionary before the model is fully constructed.
        """
        if "Created" in data:
            data["_created"] = AuditFields(**data["Created"])
        if "Updated" in data:
            data["_updated"] = AuditFields(**data["Updated"])
        if "status" in data:
            data["_status"] = Status(data["status"])

        return data

    @property
    def created(self) -> AuditFields | None:
        return self._created

    @property
    def updated(self) -> AuditFields | None:
        return self._updated

    @property
    def status(self) -> Status | None:
        return self._status


class BaseSessionModel(BaseAlbertModel):
    session: AlbertSession | None = Field(
        default=None,
        description=(
            "Albert session for accessing the Albert API. "
            "The session is included as an optional field to allow for models of this type "
            "to be created independently from calls to the API."
        ),
    )


class BaseEntityLink(BaseAlbertModel):
    id: str
    name: str | None = Field(default=None)
