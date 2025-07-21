"""
Tests for the FullAnalyticalReport resource and related functionality.
"""

import pandas as pd
import pytest

from albert.client import Albert
from albert.resources.reports import (
    ColumnState,
    FilterModel,
    FilterState,
    FullAnalyticalReport,
)


def test_create_full_analytical_report():
    """Test creating a FullAnalyticalReport instance."""
    report = FullAnalyticalReport(
        report_type_id="RET22",
        name="Test Report",
        description="A test analytical report",
        project_id="PRO123",
    )

    assert report.report_type_id == "RET22"
    assert report.name == "Test Report"
    assert report.description == "A test analytical report"
    assert report.project_id == "PRO123"
    assert report.id is None  # Read-only field


def test_full_analytical_report_with_column_states():
    """Test FullAnalyticalReport with column states."""
    column_states = [
        ColumnState(col_id="column1", row_group=True, row_group_index=0, agg_func="sum"),
        ColumnState(col_id="column2", pivot=True, pivot_index=0),
    ]

    report = FullAnalyticalReport(
        report_type_id="RET22", name="Test Report", column_state=column_states
    )

    assert len(report.column_state) == 2
    assert report.column_state[0].col_id == "column1"
    assert report.column_state[0].row_group is True
    assert report.column_state[1].col_id == "column2"
    assert report.column_state[1].pivot is True


def test_get_raw_dataframe():
    """Test getting raw data as DataFrame."""
    report_data = [
        {"id": 1, "name": "Item 1", "value": 100},
        {"id": 2, "name": "Item 2", "value": 200},
    ]

    report = FullAnalyticalReport(report_type_id="RET22", name="Test Report", report=report_data)

    df = report.get_raw_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["id", "name", "value"]


def test_get_filtered_dataframe():
    """Test getting filtered data as DataFrame."""
    report_data = [
        {"id": 1, "name": "Item 1", "category": "A"},
        {"id": 2, "name": "Item 2", "category": "B"},
        {"id": 3, "name": "Item 3", "category": "A"},
    ]

    filter_state = FilterState(filter_models=[FilterModel(filter_type="set", values=["A"])])

    report = FullAnalyticalReport(
        report_type_id="RET22",
        name="Test Report",
        report=report_data,
        filter_state={"category": filter_state},
    )

    df = report.get_filtered_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2  # Only items with category "A"
    assert all(df["category"] == "A")


def test_report_without_data_raises_error():
    """Test that methods raise error when report data is not available."""
    report = FullAnalyticalReport(report_type_id="RET22", name="Test Report")

    with pytest.raises(ValueError, match="Report data is not available"):
        report.get_raw_dataframe()

    with pytest.raises(ValueError, match="Report data is not available"):
        report.get_filtered_dataframe()


def test_model_validation():
    """Test model validation for required fields."""
    with pytest.raises(ValueError):
        FullAnalyticalReport()  # Missing required fields

    with pytest.raises(ValueError):
        FullAnalyticalReport(
            report_type_id="RET22",
            name="",  # Empty name should fail validation
        )


def test_field_aliases():
    """Test that field aliases work correctly."""
    report = FullAnalyticalReport(
        reportTypeId="RET22",  # Using alias
        name="Test Report",
    )

    assert report.report_type_id == "RET22"


def test_optional_fields():
    """Test that optional fields can be omitted."""
    report = FullAnalyticalReport(report_type_id="RET22", name="Test Report")

    assert report.description is None
    assert report.project_id is None
    assert report.column_state == []
    assert report.chart_model_state == []


def test_get_full_report(client: Albert):
    """Test getting a full report by ID."""
    # This test would require a real report ID to work
    # For now, we'll test the method exists and handles errors properly
    with pytest.raises(Exception):  # Should raise some exception for invalid ID
        client.reports.get_full_report(report_id="INVALID_ID")


def test_create_report(client: Albert):
    """Test creating a new report."""
    new_report = FullAnalyticalReport(
        report_type_id="RET22", name="Test API Report", description="Created via API test"
    )

    # This test would require proper API setup
    # For now, we'll test that the method exists
    assert hasattr(client.reports, "create_report")


def test_delete_report(client: Albert):
    """Test deleting a report."""
    # This test would require a real report ID to work
    # For now, we'll test the method exists
    assert hasattr(client.reports, "delete_report")


def test_get_analytics_report_table(client: Albert):
    """Test getting analytics report table."""
    # This test would require a real report ID to work
    # For now, we'll test the method exists
    assert hasattr(client.reports, "get_analytics_report_table")


def test_report_collection_methods_exist(client: Albert):
    """Test that all expected report collection methods exist."""
    expected_methods = [
        "get_report",
        "get_analytics_report",
        "get_datascience_report",
        "get_analytics_report_table",
        "get_full_report",
        "create_report",
        "delete_report",
    ]

    for method_name in expected_methods:
        assert hasattr(client.reports, method_name), f"Method {method_name} not found"


def test_full_analytical_report_serialization():
    """Test that FullAnalyticalReport can be serialized and deserialized."""
    original_report = FullAnalyticalReport(
        report_type_id="RET22",
        name="Serialization Test",
        description="Test serialization",
        project_id="PRO123",
        column_state=[ColumnState(col_id="test_col", row_group=True, row_group_index=0)],
    )

    # Serialize to dict
    report_dict = original_report.model_dump()

    # Deserialize back to object
    deserialized_report = FullAnalyticalReport(**report_dict)

    assert deserialized_report.report_type_id == original_report.report_type_id
    assert deserialized_report.name == original_report.name
    assert deserialized_report.description == original_report.description
    assert deserialized_report.project_id == original_report.project_id
    assert len(deserialized_report.column_state) == len(original_report.column_state)
