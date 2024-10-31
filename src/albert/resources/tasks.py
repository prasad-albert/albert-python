from enum import Enum

from pydantic import Field

from albert.resources.base import BaseAlbertModel, BaseEntityLink, SecurityClass
from albert.resources.data_templates import DataTemplate
from albert.resources.locations import Location
from albert.resources.projects import Project
from albert.resources.serialization import SerializeAsEntityLink
from albert.resources.tagged_base import BaseTaggedEntity
from albert.resources.users import User
from albert.resources.workflows import Workflow


class TaskCategory(str, Enum):
    PROPERTY = "Property"
    BATCH = "Batch"
    GENERAL = "General"
    BATCH_WITH_QC = "BatchWithQC"


class BatchSizeUnit(str, Enum):
    GRAMS = "g"
    KILOGRAMS = "Kg"
    POUNDS = "lbs"


class TaskSourceType(str, Enum):
    TASK = "task"
    TEMPLATE = "template"


class TaskSource(BaseAlbertModel):
    id: str
    type: TaskSourceType


class TaskPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Target(BaseAlbertModel):
    data_column_unique_id: str | None = Field(alias="dataColumnUniqueId", default=None)
    value: str | None = Field(default=None)


class DataTemplateAndTargets(BaseAlbertModel):
    id: str
    targets: list[Target]


class InventoryInformation(BaseAlbertModel):
    """Represents the Inventory information needed for a task. For a Batch task, inventory_id and batch_size are required.
    For Property and general tasks, inventory_id and lot_id is recomended is required.

    Attributes
    ----------
    inventory_id : str
        The inventory id of the item to be used in the task.
    lot_id : str, optional
        The lot id of the item to be used in the task. Reccomended for Property and General tasks.
    batch_size : float, optional
        The batch size to make of the related InventoryItem. Required for Batch tasks.
    selected_lot : bool, read only
        Whether the lot is selected for the task. Default is None.
    """

    inventory_id: str = Field(alias="id")
    lot_id: str | None = Field(alias="lotId", default=None)
    batch_size: float | None = Field(alias="batchSize", default=None)
    selected_lot: bool | None = Field(alias="selectedLot", exclude=True, frozen=True, default=None)


class Task(BaseTaggedEntity):
    """_summary_

    Note: QCTaskData is not yet completed
    Note: SamConfig is not yet completed
    """

    name: str
    category: TaskCategory
    batch_size_unit: BatchSizeUnit | None = Field(alias="batchSizeUnit", default=None)
    parent_id: str | None = Field(alias="parentId", default=None)
    metadata: dict[str, str | list[BaseEntityLink] | BaseEntityLink] | None = Field(
        alias="Metadata", default=None
    )
    qc_task: bool | None = Field(alias="qcTask", default=None)
    batch_task_id: str | None = Field(alias="batchTaskId", default=None)
    sources: list[TaskSource] | None = Field(default=None)
    inventory_information: list[InventoryInformation] = Field(alias="Inventories", default=None)
    location: SerializeAsEntityLink[Location] | None = Field(default=None, alias="Location")
    priority: TaskPriority | None = Field(default=None)
    security_class: SecurityClass | None = Field(alias="class", default=None)
    pass_fail: bool | None = Field(alias="passOrFail", default=None)
    notes: str | None = Field(default=None)
    start_date: str | None = Field(alias="startDate", default=None)
    due_date: str | None = Field(alias="dueDate", default=None)
    result: str | None = Field(default=None)
    tagrget: str | None = Field(default=None)
    project: SerializeAsEntityLink[Project] | list[SerializeAsEntityLink[Project]] | None = Field(
        default=None, alias="Project"
    )
    assigned_to: SerializeAsEntityLink[User] | None = Field(default=None, alias="assignedTo")
    data_template: SerializeAsEntityLink[DataTemplate] | DataTemplateAndTargets | None = Field(
        default=None, alias="DataTemplate"
    )
    workflow: SerializeAsEntityLink[Workflow] | None = Field(
        alias="Workflow", default=None
    )  # Note, the swagger docs have more here that I am unfamiliar with.
    results_row_id: str | None = Field(alias="resultsRowId", default=None)
    unique_id: str | None = Field(alias="uniqueId", default=None)
