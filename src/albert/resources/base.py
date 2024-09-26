from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

from albert.session import AlbertSession
from albert.utils.exceptions import AlbertException


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
    status: Status | None = Field(default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        exclude={"session"},
        arbitrary_types_allowed=True,
        validate_assignment=True,
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

    @model_validator(mode="before")
    def ensure_enum_values(cls, data: dict[str, Any]) -> dict[str, Any]:
        """populate_by_name=True blocks the setting of enum values by name. This method allows for that."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, Enum):
                    data[key] = value.value
                if isinstance(value, list):
                    data[key] = [v.value if isinstance(v, Enum) else v for v in value]
        return data

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


class BaseEntityLink(BaseModel):
    id: str
    name: str | None = Field(default=None, exclude=True)


class EntityLinkConvertible:
    def to_entity_link(self) -> BaseEntityLink:
        if hasattr(self, "id"):
            return BaseEntityLink(id=self.id)
        return AlbertException(
            "`id` is required to create an entity link. Ensure the linked object is registered."
        )
