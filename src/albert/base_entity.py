from pydantic import BaseModel, Field, PrivateAttr, ConfigDict, model_validator
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AuditFields(BaseModel):
    by: str = Field(None)
    by_name: Optional[str] = Field(None, alias="byName")
    at: Optional[datetime] = Field(None)


class BaseAlbertModel(BaseModel):
    _created: Optional[AuditFields] = PrivateAttr(default=None)
    _updated: Optional[AuditFields] = PrivateAttr(default=None)
    _status: Optional[Status] = PrivateAttr(default=None)

    @model_validator(mode="before")
    @classmethod
    def initialize_private_attrs(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize private attributes from the incoming data dictionary before the model is fully constructed.
        """
        if "Created" in data:
            data["_created"] = AuditFields(**data["Created"])
        if "Updated" in data:
            data["_updated"] = AuditFields(**data["Updated"])
        if "status" in data:
            data["_status"] = Status(data["status"])

        return data

    @property
    def created(self) -> Optional[AuditFields]:
        return self._created

    @property
    def updated(self) -> Optional[AuditFields]:
        return self._updated

    @property
    def status(self) -> Optional[Status]:
        return self._status

    model_config = ConfigDict(
            populate_by_name=True,
            use_enum_values=True,
            exclude={"session"},
            arbitrary_types_allowed=True
        )