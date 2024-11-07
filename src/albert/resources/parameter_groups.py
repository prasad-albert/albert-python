from enum import Enum
from typing import Any

from pydantic import Field, PrivateAttr

from albert.resources.base import AuditFields, BaseEntityLink, BaseResource, SecurityClass
from albert.resources.inventory import InventoryItem
from albert.resources.parameters import Parameter, ParameterCategory
from albert.resources.serialization import SerializeAsEntityLink
from albert.resources.units import Unit
from albert.resources.users import User
from albert.utils.exceptions import AlbertException


class PGType(str, Enum):
    """The type of a parameter group"""

    GENERAL = "general"
    BATCH = "batch"
    PROPERTY = "property"


class PGMetadata(BaseResource):
    """The metadata of a parameter group"""

    standards: list[BaseEntityLink] = Field(alias="Standards")


class ParameterValue(BaseResource):
    """The value of a parameter in a parameter group.

    Attributes
    ----------
    parameter : Parameter
        The Parameter resource this value is associated with. Provide either an id or a parameter keyword argument.
    id : str | None
        The Albert ID of the Parameter resource this value is associated with. Provide either an id or a parameter keyword argument.
    category: ParameterCategory
        The category of the parameter.
    short_name : str | None
        The short name of the parameter value.
    value : str | None
        The value of the parameter. Can be a string or an InventoryItem (if, for example, the parameter is an instrumnt choice).
    unit : Unit | None
        The unit of measure for the provided parameter value.
    name : str
        The name of the parameter. Read-only.
    sequence : int
        The sequence of the parameter. Read-only.
    """

    parameter: Parameter = Field(default=None, exclude=True)
    id: str | None = Field(default=None)
    category: ParameterCategory | None = Field(default=None)
    short_name: str | None = Field(alias="shortName", default=None)
    value: str | None | SerializeAsEntityLink[InventoryItem] = Field(default=None)
    unit: SerializeAsEntityLink[Unit] | None = Field(alias="Unit", default=None)
    added: AuditFields | None = Field(alias="Added", default=None)

    _name = PrivateAttr(default=None)
    _sequence: int | None = PrivateAttr(default=None)

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._sequence = data.get("sequence")
        if parameter := data.get("parameter"):
            # Parameter object was passed
            if self.id is not None:
                raise AlbertException(
                    "Please provide either an id or an parameter object, not both."
                )
            parameter = Parameter(**parameter) if isinstance(parameter, dict) else parameter
            if parameter.id is None:
                raise AlbertException(
                    "You must first create the parameter before creating a parameter value. "
                    "Your parameter object must have an id."
                )
            self.id = parameter.id
            self.category = parameter.category
            self._name = parameter.name
        else:
            # No parameter object
            if self.id is None and "parameter" not in data:
                raise AlbertException("Please provide either an id or an parameter object.")
            self._name = data.get("name")

    @property
    def name(self) -> str:
        return self._name

    @property
    def sequence(self) -> int:
        return self._sequence


class ParameterGroup(BaseResource):
    name: str
    type: PGType
    id: str | None = Field(None, alias="albertId")
    description: str | None = Field(default=None)
    security_class: SecurityClass = Field(default=SecurityClass.RESTRICTED, alias="class")
    acl: list[SerializeAsEntityLink[User]] | None = Field(default=None, alias="ACL")
    metadata: PGMetadata | None = Field(alias="Metadata", default=None)
    parameters: list[ParameterValue] = Field(alias="Parameters")

    _verified: bool = PrivateAttr(default=False)
    _documents: list[BaseEntityLink] = PrivateAttr(default_factory=list)

    @property
    def verified(self) -> bool:
        return self._verified

    @property
    def documents(self) -> list[BaseEntityLink]:
        return self._documents
