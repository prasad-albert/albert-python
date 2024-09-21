import pandas as pd
import pytest

from albert.albert import Albert
from albert.collections.worksheets import WorksheetCollection
from albert.resources.sheets import Column, Sheet
from albert.resources.worksheets import Worksheet


# NOTE: Once we have the Project Module done, these should be made dynamically.
@pytest.fixture(scope="module")
def project(client: Albert):
    return client.projects.get_by_id(project_id="P015")


# NOTE: Once we have the Project Module done, these should be made dynamically.
@pytest.fixture(scope="module")
def worksheet(client: Albert):
    collection = WorksheetCollection(session=client.session)
    wksht = collection.get_by_project_id(project_id="P015")
    return wksht


@pytest.fixture(scope="module")
def sheet(worksheet: Worksheet) -> Sheet:
    for s in worksheet.sheets:
        if s.name == "test":
            return s


def test_get_worksheet(worksheet: Worksheet):
    assert isinstance(worksheet, Worksheet)
    has_sheet = False
    for s in worksheet.sheets:
        has_sheet = True
        assert isinstance(s, Sheet)
    assert has_sheet


def test_get_test_sheet(sheet: Sheet):
    assert isinstance(sheet, Sheet)
    sheet.rename(new_name="test renamed")
    assert sheet.name == "test renamed"
    sheet.rename(new_name="test")
    assert sheet.name == "test"
    assert isinstance(sheet.grid, pd.DataFrame)


def test_crud_empty_column(sheet: Sheet):
    new_col = sheet.add_blank_column(name="my cool new column")
    assert isinstance(new_col, Column)
    assert new_col.column_id.startswith("COL")

    renamed_column = new_col.rename(new_name="My renamed column")
    assert new_col.column_id == renamed_column.column_id
    assert renamed_column.name == "My renamed column"

    assert sheet.delete_column(column_id=new_col.column_id)


# Because you cannot delete Formulation Columns, We will need to mock this test.
# def test_crud_formulation_column(sheet):
#     new_col = sheet.add_formulation_columns(formulation_names=["my cool formulation"])[0]
