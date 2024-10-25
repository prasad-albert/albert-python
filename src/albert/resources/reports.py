from typing import Any

from pydantic import Field

from albert.resources.base import BaseResource

ReportItem = list[dict[str, Any]] | dict[str, Any] | None


class Report(BaseResource):
    id: str = Field(..., alias="reportTypeId")
    report_type: str = Field(..., alias="reportType")
    category: str
    items: list[ReportItem] = Field(..., alias="Items")
