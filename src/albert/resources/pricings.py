from enum import Enum

from pydantic import Field

from albert.resources.base import BaseResource
from albert.resources.companies import Company
from albert.resources.locations import Location
from albert.resources.serialization import SerializeAsEntityLink


class LeadTimeUnit(str, Enum):
    DAYS = "Days"
    WEEKS = "Weeks"
    MONTHS = "Months"


class Pricing(BaseResource):
    id: str | None = Field(default=None, alias="albertId")
    inventory_item_id: str = Field(default=None, alias="parentId")
    company: SerializeAsEntityLink[Company] = Field(alias="Company")
    location: SerializeAsEntityLink[Location] = Field(alias="Location")
    description: str | None = Field(default=None)
    pack_size: str | None = Field(default=None, alias="packSize")
    price: float = Field(ge=0, le=9999999999)
    currency: str = Field(default="USD", alias="currency")
    fob: str = Field(default=None)
    lead_time: int | None = Field(default=None, alias="leadTime")
    lead_time_unit: LeadTimeUnit | None = Field(default=None, alias="leadTimeUnit")
    expiration_date: str | None = Field(default=None, alias="expirationDate")
