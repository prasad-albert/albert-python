import logging

from pydantic import Field, model_validator

from albert.resources.base import BaseAlbertModel, BaseResource
from albert.resources.parameter_groups import ParameterGroup
from albert.resources.parameters import Parameter
from albert.resources.serialization import SerializeAsEntityLink
from albert.resources.units import Unit
from albert.utils.exceptions import AlbertException


class Interval(BaseAlbertModel):
    """A Pydantic class representing an interval."""

    value: str = Field(default=None)
    unit: SerializeAsEntityLink[Unit] = Field(default=None, alias="Unit")


class ParameterSetpoint(BaseAlbertModel):
    """A Pydantic class representing the setpoint or intervals of a parameter to use.
    For a single value, provide the value and unit. For multiple values, provide intervals.
    a parameter or parameter_id must be provided.
    """

    parameter: Parameter = Field(exclude=True, default=None)
    value: str | dict[str, str] = Field(default=None)
    unit: SerializeAsEntityLink[Unit] = Field(default=None, alias="Unit")
    parameter_id: str = Field(alias="id", default=None)
    intervals: list[Interval] = Field(default=None, alias="Intervals")

    @model_validator(mode="after")
    def check_parameter_setpoit_validity(self):
        if self.parameter:
            if self.parameter_id is not None:
                if self.parameter_id != self.parameter.id:
                    raise AlbertException(
                        "Provided parameter_id does not match the parameter's id."
                    )
            else:
                self.parameter_id = self.parameter.id
        elif self.parameter is None and self.parameter_id is None:
            raise AlbertException("Either parameter or parameter_id must be provided.")
        if self.value is not None and self.intervals is not None:
            raise AlbertException("Cannot provide both value and intervals.")
        return self


class ParameterGroupSetpoints(BaseAlbertModel):
    """A class that represents the setpoints on a parameter group."""

    parameter_group: ParameterGroup = Field(exclude=True, default=None)
    parameter_group_id: str = Field(alias="id", default=None)
    parameter_group_name: str = Field(alias="name", default=None, frozen=True, exclude=True)
    parameter_setpoints: list[ParameterSetpoint] = Field(alias="Parameters")

    @model_validator(mode="after")
    def validate_pg_setpoint(self):
        if self.parameter_group is not None:
            if self.parameter_group_id is not None:
                if self.parameter_group.id != self.parameter_group_id:
                    raise AlbertException(
                        "Provided parameter_group_id does not match the parameter_group's id."
                    )
            else:
                self.parameter_group_id = self.parameter_group.id
        return self


class Workflow(BaseResource):
    """A Pydantic Class representing a workflow in Albert.
    Workflows are combinations of Data Templates and Parameter groups and their associated setpoints.
    """

    name: str
    parameter_group_setpoints: list[ParameterGroupSetpoints] = Field(alias="ParameterGroups")
    id: str | None = Field(alias="albertId", default=None)
