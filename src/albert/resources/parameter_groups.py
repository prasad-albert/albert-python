from enum import Enum

from pydantic import Field

from albert.resources.base import AuditFields, BaseAlbertModel, BaseEntityLink, SecurityClass
from albert.resources.parameters import Parameter
from albert.resources.tagged_base import BaseTaggedEntity


class PGType(str, Enum):
    GENERAL = "general"
    BATCH = "batch"
    PROPERTY = "property"


class PGMetadata(BaseAlbertModel):
    standards: list[BaseEntityLink] = Field(alias="Standards")


class ParameterValue(Parameter):
    short_name: str | None = Field(alias="shortName", default=None)
    value: str | None
    unit: BaseEntityLink | None = Field(alias="Unit")
    sequence: int


class ParameterGroup(BaseTaggedEntity):
    id: str | None = Field(None, alias="albertId")
    name: str
    description: str | None = Field(default=None)
    type: PGType
    security_class: SecurityClass = Field(default=SecurityClass.PUBLIC, alias="class")
    verified: bool = Field(default=False)
    alc: list[BaseEntityLink] = Field(alias="ACL", default=None)
    metadata: PGMetadata | None = Field(alias="Metadata", default=None)
    documents: list[BaseEntityLink] = Field(alias="Documents", frozen=True)
    parameters: list[Parameter] = Field(alias="Parameters")
    added: AuditFields | None = Field(alias="Added", default=None)
