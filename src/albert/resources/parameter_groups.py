from enum import Enum
from typing import Any

from pydantic import Field, PrivateAttr, field_serializer

from albert.resources.base import AuditFields, BaseAlbertModel, BaseEntityLink, SecurityClass
from albert.resources.parameters import Parameter
from albert.resources.serialization import serialize_to_entity_link, serialize_to_entity_link_list
from albert.resources.tagged_base import BaseTaggedEntity
from albert.resources.units import Unit
from albert.resources.users import User
from albert.utils.exceptions import AlbertException


class PGType(str, Enum):
    GENERAL = "general"
    BATCH = "batch"
    PROPERTY = "property"


class PGMetadata(BaseAlbertModel):
    standards: list[BaseEntityLink] = Field(alias="Standards")


class ParameterValue(BaseAlbertModel):
    parameter: Parameter = Field(default=None, exclude=True)
    id: str | None = Field(alias="albertId", default=None)
    _name = PrivateAttr(default=None)
    short_name: str | None = Field(alias="shortName", default=None)
    value: str | None = Field(default=None)
    unit: BaseEntityLink | Unit | None = Field(alias="Unit")
    _sequence: int | None = PrivateAttr(default=None)
    added: AuditFields | None = Field(alias="Added", default=None)

    unit_serializer = field_serializer("unit")(serialize_to_entity_link)

    def __init__(self, **data: Any):
        super().__init__(**data)
        if "name" in data:
            self._name = data["name"]
        if "sequence" in data:
            self._sequence = data["sequence"]
        if "parameter" in data:
            if "albertId" in data or "id" in data:
                AlbertException("Please provide either an id or an parameter object, not both.")
            else:
                param_id = data["parameter"].get("albertId", None)
                if param_id is None:
                    param_id = data["parameter"].get("id", None)
                if param_id is None:
                    raise AlbertException(
                        "You must first create the parameter before creating a parameter value. Your parameter object must have an id."
                    )
                data["albertId"] = param_id
                data["name"] = data["parameter"]["name"]
        elif "id" not in data and not data["parameter"]:
            AlbertException("Please provide either an id or an parameter object.")

    @property
    def name(self) -> str:
        return self._name

    @property
    def sequence(self) -> int:
        return self._sequence


class ParameterGroup(BaseTaggedEntity):
    id: str | None = Field(None, alias="albertId")
    name: str
    description: str | None = Field(default=None)
    type: PGType
    security_class: SecurityClass = Field(default=SecurityClass.RESTRICTED, alias="class")
    _verified: bool = PrivateAttr(default=False)
    acl: list[User | BaseEntityLink] | None = Field(default=None, alias="ACL")
    metadata: PGMetadata | None = Field(alias="Metadata", default=None)
    _documents: list[BaseEntityLink] = PrivateAttr(default_factory=list)
    parameters: list[ParameterValue] = Field(alias="Parameters")

    def __init__(self, **data: Any):
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
