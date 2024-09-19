from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator

from albert.resources.base import BaseAlbertModel, BaseEntityLink
from albert.resources.inventory import InventoryCategory
from albert.resources.sheets import DesignType
from albert.resources.tagged_base import BaseTaggedEntity


class DataTemplateInventory(BaseEntityLink):
    batch_size: float | None = Field(default=None, alias="batchSize")
    sheet: list[BaseEntityLink] | None = Field(default=None)
    category: InventoryCategory | None = Field(default=None)


class DesignLink(BaseEntityLink):
    type: DesignType


class TemplateCategory(str, Enum):
    PROPERTY_LIST = "Property Task"
    PROPERTY = "Property"
    BATCH = "Batch"
    SHEET = "Sheet"
    NOTEBOOK = "Notebook"
    GENERAL = "General"
    QC_BATCH = "BatchWithQC"


class GeneralData(BaseTaggedEntity):
    category: Literal[TemplateCategory.GENERAL]


class Priority(str, Enum):
    LOW = "Low"
    HIGH = "High"


class JobStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    QUEUED = "queued"


class SamInput(BaseAlbertModel):
    value: str | None = Field(alias="Value", default=None)
    unit: str | None = Field(alias="Unit", default=None)
    name: str = Field(alias="Name")


class SamConfig(BaseAlbertModel):
    configuration_name: str = Field(alias="configurationName")
    configurationId: str
    machineId: str | None = Field(default=None)
    input: list[SamInput] | None = Field(default=None)
    job_status: JobStatus | None = Field(default=None, alias="status")

    @model_validator(mode="before")
    @classmethod
    def rename_status(cls, data: dict[str, Any]) -> dict[str, Any]:
        if "status" in data:
            # avoids trying to set status on BaseAlbertModel
            data["job_status"] = data["status"]
            data.pop("status")
        return data


class Workflow(BaseAlbertModel):
    id: str
    name: str
    sam_config: list[SamConfig] | None = Field(
        default=None, alias="SamConfig"
    )  # Some workflows may have SamConfig


class Block(BaseTaggedEntity):
    workflow: list[Workflow] = Field(default=None, alias="Workflow")
    datatemplate: list[BaseEntityLink] | None = Field(default=None, alias="Datatemplate")


class QCBatchData(BaseTaggedEntity):
    category: Literal[TemplateCategory.QC_BATCH]
    project: BaseEntityLink | None = Field(alias="Project", default=None)
    inventories: list[DataTemplateInventory] | None = Field(default=None, alias="Inventories")
    workflow: list[BaseEntityLink] = Field(default=None, alias="Workflow")
    location: BaseEntityLink | None = Field(alias="Location", default=None)
    batch_size_unit: str = Field(alias="batchSizeUnit", default=None)
    priority: Priority  # enum?!
    name: str | None = Field(default=None)


class BatchData(BaseTaggedEntity):
    category: Literal[TemplateCategory.BATCH]
    assigned_to: BaseEntityLink | None = Field(alias="AssignedTo", default=None)
    project: BaseEntityLink | None = Field(alias="Project", default=None)
    name: str | None = Field(default=None)
    location: BaseEntityLink | None = Field(alias="Location", default=None)
    batch_size_unit: str = Field(alias="batchSizeUnit", default=None)
    inventories: list[DataTemplateInventory] | None = Field(default=None, alias="Inventories")
    priority: Priority  # enum?!
    workflow: list[BaseEntityLink] = Field(default=None, alias="Workflow")


class PropertyData(BaseTaggedEntity):
    category: Literal[TemplateCategory.PROPERTY]
    name: str | None = Field(default=None)
    blocks: list[Block] = Field(default=[], alias="Blocks")  # Needs to be it's own class
    priority: Priority  # enum?!
    location: BaseEntityLink | None = Field(alias="Location", default=None)
    assigned_to: BaseEntityLink | None = Field(alias="AssignedTo", default=None)
    project: BaseEntityLink | None = Field(alias="Project", default=None)
    inventories: list[DataTemplateInventory] | None = Field(default=None, alias="Inventories")
    due_date: str | None = Field(alias="dueDate", default=None)


class SheetData(BaseTaggedEntity):
    category: Literal[TemplateCategory.SHEET]
    designs: list[DesignLink] = Field(default=None, alias="Designs")
    formula_info: list = Field(default=[], alias="FormulaInfo")
    task_rows: list[BaseEntityLink] = Field(default=[], alias="TaskRows")


class NotebookData(BaseTaggedEntity):
    category: Literal[TemplateCategory.NOTEBOOK]


CustomTemplateData = Annotated[
    PropertyData | BatchData | SheetData | NotebookData | QCBatchData | GeneralData,
    Field(discriminator="category"),
]


class ACLType(str, Enum):
    TEAM = "team"
    MEMBER = "member"
    OWNER = "owner"


class TeamACL(BaseAlbertModel):
    type: Literal[ACLType.TEAM]
    id: str
    fgc: str


class OwnerACL(BaseAlbertModel):
    type: Literal[ACLType.OWNER]
    id: str


class MemberACL(BaseAlbertModel):
    type: Literal[ACLType.MEMBER]
    id: str
    fgc: str


ACLEntry = Annotated[TeamACL | OwnerACL | MemberACL, Field(discriminator="type")]


# NOTE: Unsure if this will be re-used elsewhere and may need to be moved somewhere more general.
class ACL(BaseAlbertModel):
    fgclist: list[ACLEntry] = Field(default=None)
    acl_class: str = Field(alias="class")


class CustomTemplate(BaseTaggedEntity):
    id: str = Field(alias="albertId")
    name: str
    category: TemplateCategory = Field(default=TemplateCategory.GENERAL)
    metadata: dict | None = Field(default=None, alias="Metadata")
    data: None | CustomTemplateData = Field(default=None, alias="Data")
    team: list[TeamACL] | None = Field(default=[])
    acl: ACL | None = Field(default=[], alias="ACL")

    @model_validator(mode="before")
    @classmethod
    def add_missing_category(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Initialize private attributes from the incoming data dictionary before the model is fully constructed.
        """

        if "Data" in data and "category" in data and "category" not in data["Data"]:
            data["Data"]["category"] = data["category"]
        return data
