import logging
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field, PrivateAttr, model_validator

from albert.exceptions import AlbertException
from albert.resources.serialization import SerializeAsEntityLink
from albert.resources.tags import Tag
from albert.session import AlbertSession
from albert.utils.types import BaseAlbertModel


class Status(str, Enum):
    """The status of a resource"""

    ACTIVE = "active"
    INACTIVE = "inactive"


class SecurityClass(str, Enum):
    """The security class of a resource"""

    SHARED = "shared"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    PRIVATE = "private"
    PUBLIC = "public"


class AuditFields(BaseAlbertModel):
    """The audit fields for a resource"""

    by: str = Field(default=None)
    by_name: str | None = Field(default=None, alias="byName")
    at: datetime | None = Field(default=None)


class BaseResource(BaseAlbertModel):
    """The base resource for all Albert resources.

    Attributes
    ----------
    status: Status | None
        The status of the resource, optional.
    created: AuditFields | None
        Audit fields for the creation of the resource, optional.
    updated: AuditFields | None
        Audit fields for the update of the resource, optional.
    """

    status: Status | None = Field(default=None)
    created: AuditFields | None = Field(
        default=None,
        alias="Created",
        exclude=True,
        frozen=True,
    )
    updated: AuditFields | None = PrivateAttr(
        default=None,
        alias="UPdated",
        exclude=True,
        frozen=True,
    )


class BaseSessionResource(BaseResource):
    _session: AlbertSession | None = PrivateAttr(default=None)


class BaseTaggedEntity(BaseResource):
    """
    BaseTaggedEntity is a Pydantic model that includes functionality for handling tags as either Tag objects or strings.

    Attributes
    ----------
    tags : List[Tag | str] | None
        A list of Tag objects or strings representing tags.
    """

    tags: list[SerializeAsEntityLink[Tag]] | None = Field(None, alias="Tags")

    @model_validator(mode="before")  # must happen before to keep type validation
    @classmethod
    def convert_tags(cls, data: dict[str, Any]) -> dict[str, Any]:
        tags = data.get("tags")
        if not tags:
            tags = data.get("Tags")
        if tags:
            new_tags = []
            for t in tags:
                if isinstance(t, Tag):
                    new_tags.append(t)
                elif isinstance(t, str):
                    new_tags.append(Tag.from_string(t))
                elif isinstance(t, dict):
                    new_tags.append(Tag(**t))
                else:
                    # We do not expect this else to be hit because tags should only be Tag or str
                    logging.warning(f"Unexpected value for Tag. {t} of type {type(t)}")
                    continue
            data["tags"] = new_tags
        return data


class BaseEntityLink(BaseAlbertModel):
    id: str
    name: str | None = Field(default=None, exclude=True)


class EntityLinkConvertible:
    def to_entity_link(self) -> BaseEntityLink:
        if hasattr(self, "id"):
            return BaseEntityLink(id=self.id)
        return AlbertException(
            "`id` is required to create an entity link. Ensure the linked object is registered."
        )
