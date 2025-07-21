from typing import Any

import pandas as pd
from pydantic import Field

from albert.core.shared.identifiers import ProjectId, ReportId
from albert.core.shared.models.base import BaseResource

ReportItem = dict[str, Any] | list[dict[str, Any]] | None


class ReportInfo(BaseResource):
    report_type_id: str = Field(..., alias="reportTypeId")
    report_type: str = Field(..., alias="reportType")
    category: str
    items: list[ReportItem] = Field(..., alias="Items")


class ColumnState(BaseResource):
    """Column State Object for reports."""

    col_id: str = Field(..., alias="colId")
    row_group_index: int | None = Field(default=None, alias="rowGroupIndex")
    agg_func: str | None = Field(default=None, alias="aggFunc")
    pivot: bool = Field(default=False)
    pivot_index: int | None = Field(default=None, alias="pivotIndex")
    row_group: bool = Field(default=False, alias="rowGroup")


class FilterModel(BaseResource):
    """Filter Model Object for reports."""

    filter_type: str = Field(..., alias="filterType")
    values: list[Any] | None = Field(default=None)


class FilterState(BaseResource):
    """Filters State Object for reports."""

    filter_models: list[FilterModel] = Field(default_factory=list, alias="filterModels")


class MetadataState(BaseResource):
    """Metadata State Object for reports."""

    grouped_rows: list[str] = Field(default_factory=list, alias="groupedRows")


class ChartConfiguration(BaseResource):
    """Chart Configuration Object for reports."""

    chart_type: str = Field(..., alias="chartType")
    # Add other chart configuration fields as needed


class ChartTemplate(BaseResource):
    """Chart Template Object for reports."""

    chart_type: str = Field(..., alias="chartType")
    # Add other chart template fields as needed


class ChartModelState(BaseResource):
    """Chart State Object for reports."""

    chart_template: ChartTemplate = Field(..., alias="chartTemplate")
    chart_configuration: ChartConfiguration = Field(..., alias="chartConfiguration")


class ColumnMapping(BaseResource):
    """Column Mapping Object for reports."""

    # Add column mapping fields as needed
    pass


class FullAnalyticalReport(BaseResource):
    """A full analytical report in Albert.

    This resource represents a complete analytical report with all its configuration,
    data, and state information.

    Attributes
    ----------
    report_data_id : str | None
        Unique Identifier of the Report which is created. Read-only.
    report_type_id : str
        Type of report which will be created. Taken from reports/type API.
    report_type : str | None
        Type of report which will be created. Name taken from reports/type API.
    name : str
        Name of the report. Maximum length 500 characters.
    description : str | None
        Description of the report. Maximum length 1000 characters.
    project_id : str | None
        Project ID of the report. Not mandatory.
    project_name : str | None
        Name of the project.
    parent_id : str | None
        Parent ID of the report. Not mandatory.
    report_v2 : bool | None
        Whether this is a v2 report.
    input_data : dict[str, Any] | None
        Input data for the report.
    report_state : str | None
        Any string representing the report state.
    column_state : List[ColumnState] | None
        Column state objects.
    filter_state : FilterState | None
        Filters state object.
    meta_data_state : MetadataState | None
        Metadata state object.
    chart_model_state : List[ChartModelState] | None
        Chart state objects.
    field_mapping : List[ColumnMapping] | None
        Column mapping objects.
    source_report_id : str | None
        Report ID from which to copy states to the new report.
    created_by : str | None
        Specifies the createdBy id.
    """

    # Read-only fields
    id: ReportId | None = Field(default=None, alias="id", exclude=True, frozen=True)

    # Required fields
    report_type_id: str = Field(..., alias="reportTypeId")
    name: str = Field(..., min_length=1, max_length=500)

    # Optional fields
    report_type: str | None = Field(default=None, alias="reportType")
    description: str | None = Field(default=None, max_length=1000)
    project_id: ProjectId | None = Field(default=None, alias="projectId")
    project_name: str | None = Field(default=None, alias="projectName")
    parent_id: str | None = Field(default=None, alias="parentId")
    report_v2: bool | None = Field(default=None, alias="reportV2")
    input_data: dict[str, Any] | None = Field(default=None, alias="inputData")
    report_state: str | None = Field(default=None, alias="reportState")
    column_state: list[ColumnState] | None = Field(default_factory=list, alias="columnState")
    filter_state: FilterState | None = Field(default=None, alias="filterState")
    meta_data_state: MetadataState | None = Field(default=None, alias="metaDataState")
    chart_model_state: list[ChartModelState] | None = Field(
        default_factory=list, alias="chartModelState"
    )
    field_mapping: list[ColumnMapping] | None = Field(default_factory=list, alias="FieldMapping")
    source_report_id: ReportId | None = Field(default=None, alias="sourceReportId")
    created_by: str | None = Field(default=None, alias="createdBy")

    # Additional fields from the working code
    report: list[dict[str, Any]] | None = Field(default=None, exclude=True, frozen=True)

    # def _get_processed_data(self) -> dict[str, Any]:
    #     """
    #     Get the processed report information including raw data, operations, and metadata.

    #     Returns
    #     -------
    #     dict[str, Any]
    #         A dictionary containing the processed report information.
    #     """
    #     if not self.report:
    #         raise ValueError("Report data is not available")

    #     # This would implement the logic from the working code
    #     # For now, return a basic structure
    #     return {
    #         "raw_data": self.report,
    #         "column_states": {col.col_id: col for col in (self.column_state or [])},
    #         "filter_settings": self.filter_state,
    #         "metadata": self.meta_data_state,
    #         "chart_type": self.chart_model_state[0].chart_template.chart_type
    #         if self.chart_model_state
    #         else None,
    #         "chart_config": self.chart_model_state[0].chart_configuration
    #         if self.chart_model_state
    #         else None,
    #     }

    # def get_operations(self) -> dict[str, Any]:
    #     """
    #     Extract operations (grouping, aggregation, pivoting) from column states.

    #     Returns
    #     -------
    #     dict[str, Any]
    #         A dictionary containing grouping, aggregation, and pivoting operations.
    #     """
    #     if not self.column_state:
    #         return {"grouping": [], "aggregation": {}, "pivoting": []}

    #     # Aggregation function mapping (from the working code)
    #     agg_mapping = {"sum": "sum", "count": "count", "avg": "mean", "min": "min", "max": "max"}

    #     operations = {
    #         "grouping": [],
    #         "grouping_order": [],
    #         "aggregation": {},
    #         "pivoting": [],
    #         "pivoting_order": [],
    #     }

    #     for column_state in self.column_state:
    #         if column_state.row_group:
    #             operations["grouping"].append(column_state.col_id)
    #             operations["grouping_order"].append(column_state.row_group_index or 0)
    #         if column_state.agg_func:
    #             operations["aggregation"][column_state.col_id] = agg_mapping.get(
    #                 column_state.agg_func, column_state.agg_func
    #             )
    #         if column_state.pivot:
    #             operations["pivoting"].append(column_state.col_id)
    #             operations["pivoting_order"].append(column_state.pivot_index or 0)

    #     # Sort by order
    #     operations["grouping"] = [
    #         x
    #         for _, x in sorted(
    #             zip(operations["grouping_order"], operations["grouping"], strict=False)
    #         )
    #     ]
    #     operations["pivoting"] = [
    #         x
    #         for _, x in sorted(
    #             zip(operations["pivoting_order"], operations["pivoting"], strict=False)
    #         )
    #     ]

    #     # Remove order information
    #     del operations["grouping_order"]
    #     del operations["pivoting_order"]

    #     return operations

    def get_raw_dataframe(self) -> pd.DataFrame:
        """
        Get the raw report data as a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            The raw report data.
        """
        if not self.report:
            raise ValueError("Report data is not available")
        return pd.DataFrame(self.report)

    def get_filtered_dataframe(self) -> pd.DataFrame:
        """
        Get the filtered report data as a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            The filtered report data.
        """
        if not self.report:
            raise ValueError("Report data is not available")

        df = pd.DataFrame(self.report)

        if not self.filter_state:
            return df

        # Apply filters (simplified version from the working code)
        for column_name, filter_state in self.filter_state.items():
            if column_name not in df.columns:
                continue

            for filter_model in filter_state.filter_models:
                if not filter_model or filter_model.filter_type != "set":
                    continue

                if filter_model.values:
                    df = df[df[column_name].isin(filter_model.values)]

        return df
