from enum import Enum
from typing import Any

from pydantic import Field, PrivateAttr, field_serializer

from albert.resources.base import AuditFields, BaseAlbertModel, BaseEntityLink, SecurityClass
from albert.resources.parameters import Parameter
from albert.resources.serialization import serialize_to_entity_link, serialize_to_entity_link_list
from albert.resources.tagged_base import BaseTaggedEntity
from albert.resources.units import Unit
from albert.resources.users import User


class PGType(str, Enum):
    GENERAL = "general"
    BATCH = "batch"
    PROPERTY = "property"


class PGMetadata(BaseAlbertModel):
    standards: list[BaseEntityLink] = Field(alias="Standards")


class ParameterValue(Parameter):
    short_name: str | None = Field(alias="shortName", default=None)
    value: str | None
    unit: BaseEntityLink | Unit | None = Field(alias="Unit")
    sequence: int
    added: AuditFields | None = Field(alias="Added", default=None)

    unit_serializer = field_serializer("unit")(serialize_to_entity_link)


class ParameterGroup(BaseTaggedEntity):
    id: str | None = Field(None, alias="albertId")
    name: str
    description: str | None = Field(default=None)
    type: PGType
    security_class: SecurityClass = Field(default=SecurityClass.RESTRICTED, alias="class")
    _verified: bool = PrivateAttr(default=False)
    alc: list[BaseEntityLink | User] = Field(alias="ACL", default=None)
    metadata: PGMetadata | None = Field(alias="Metadata", default=None)
    _documents: list[BaseEntityLink] = PrivateAttr(default_factory=list)
    parameters: list[ParameterValue] = Field(alias="Parameters")

    def __ini__(self, **data: Any):
        super().__init__(**data)
        if "verified" in data:
            self._verified = bool(data["verified"])
        if "Documents" in data:
            self._documents = data["Documents"]

    @property
    def verified(self) -> bool:
        return self._verified

    @property
    def documents(self) -> list[BaseEntityLink]:
        return self._documents

    acl_serializer = field_serializer("acl")(serialize_to_entity_link_list)
