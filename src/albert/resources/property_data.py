from enum import Enum
from typing import Any, Literal

from pydantic import Field, model_validator

from albert.resources.base import BaseAlbertModel, BaseResource
from albert.resources.data_templates import DataTemplate
from albert.resources.lots import Lot
from albert.resources.serialization import SerializeAsEntityLink
from albert.resources.units import Unit
from albert.resources.workflows import Workflow

########################## Supporting GET Classes ##########################


class DataEntity(str, Enum):
    TASK = "task"
    WORKFLOW = "workflow"
    INVENTORY = "inventory"


class PropertyValue(BaseAlbertModel):
    id: str | None = Field(default=None)
    value: str | None = Field(default=None)
    numeric_value: float | None = Field(default=None, alias="valueNumeric")
    string_value: str | None = Field(default=None, alias="valueString")


class Trial(BaseAlbertModel):
    trial_number: int = Field(alias="trialNo")
    void: bool = Field(default=False)
    data_columns: list[PropertyValue] = Field(alias="DataColumns")


class DataInterval(BaseAlbertModel):
    interval_combination: str = Field(alias="intervalCombination")
    void: bool = Field(default=False)
    trials: list[Trial] = Field(alias="Trials")


class TaskData(BaseAlbertModel):
    task_id: str = Field(alias="id")
    task_name: str = Field(alias="name")
    qc_task: bool | None = Field(alias="qcTask", default=None)
    initial_workflow: SerializeAsEntityLink[Workflow] = Field(alias="InitialWorkflow")
    finial_workflow: SerializeAsEntityLink[Workflow] = Field(alias="FinalWorkflow")
    data_template: SerializeAsEntityLink[DataTemplate] = Field(alias="Datatemplate")
    data: DataInterval


class DataColumn(BaseAlbertModel):
    data_column_id: str = Field(alias="id")
    data_column_name: str = Field(alias="name")
    property_data: PropertyValue = Field(alias="PropertyData")
    unit: SerializeAsEntityLink[Unit] | None = Field(alias="Unit", default=None)


class CustomData(BaseAlbertModel):
    lot: SerializeAsEntityLink[Lot] | None = Field(alias="Lot", default=None)
    data_columns: list[DataColumn] = Field(alias="DataColumns")


class InventoryInformation(BaseAlbertModel):
    inventory_id: str | None = Field(alias="id", default=None)
    lot_id: str | None = Field(alias="lotId", default=None)


################# Returned from GET /api/v3/propertydata ##################


class InventoryPropertyData(BaseResource):
    inventory_id: str = Field(alias="inventoryId")
    inventory_name: str = Field(alias="inventoryName")
    task_property_data: list[TaskData] = Field(alias="Task")
    custom_property_data: list[CustomData] = Field(alias="NoTask")


class TaskPropertyData(BaseResource):
    entity: Literal[DataEntity.TASK] = DataEntity.TASK
    parent_id: str | None = Field(None, alias="parentId")
    task_id: str | None = Field(None, alias="id")
    inventory: InventoryInformation | None = Field(alias="Inventory", default=None)
    category: DataEntity | None = Field(None)
    initial_workflow: SerializeAsEntityLink[Workflow] = Field(alias="InitialWorkflow")
    finial_workflow: SerializeAsEntityLink[Workflow] = Field(alias="FinalWorkflow")
    data_template: SerializeAsEntityLink[DataTemplate] = Field(alias="Datatemplate")
    data: DataInterval = Field(alias="Data", frozen=True)


########################## Supporting POST Classes ##########################


class TaskPropertyValue(BaseAlbertModel):
    value: str | None = Field(default=None)


class TaskDatumColumn(BaseAlbertModel):
    data_column_id: str = Field(alias="id")
    column_id: str = Field(alias="columnId")


class TaskDataColumn(TaskDatumColumn):
    value: TaskPropertyValue = Field(alias="Value")

    @model_validator(mode="before")
    def set_string_value(values: dict[str, Any]) -> dict[str, Any]:
        if "value" in values and isinstance(values["value"], str):
            values["value"] = TaskPropertyValue(value=values["value"])
        return values


class TaskTrialData(BaseAlbertModel):
    trial_number: int | None = Field(alias="trialNo", default=None)
    data_columns: list[TaskDataColumn] = Field(alias="DataColumns")


########################## Task Property POST Classes ##########################


class TaskPropertyDataCreate(BaseResource):
    entity: Literal[DataEntity.TASK] = Field(default=DataEntity.TASK)
    interval_combination: str = Field(
        alias="intervalCombination",
        examples=["default", "ROW4XROW2", "ROW2XROW2"],
        default="default",
    )
    unique_id: str | None = Field(alias="uniqueId", default=None)
    data_template: SerializeAsEntityLink[DataTemplate] = Field(
        alias="DataTemplate"
    )  # Capital T on this one
    data: list[TaskTrialData] = Field(alias="Data")


class TaskPropertyDatumCreate(BaseResource):
    entity: Literal[DataEntity.TASK] = Field(default=DataEntity.TASK)
    value: str | None = Field(default=None)
    interval_combination: str = Field(
        alias="intervalCombination",
        examples=["default", "ROW4XROW2", "ROW2XROW2"],
        default="default",
    )
    unique_id: str | None = Field(alias="uniqueId", default=None)
    data_template: SerializeAsEntityLink[DataTemplate] = Field(
        alias="DataTemplate"
    )  # Capital T on this one
    trial_number: int = Field(alias="visibleTrialNo")
    data_columns: list[TaskDatumColumn] = Field(alias="DataColumns")
