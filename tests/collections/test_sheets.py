import pandas as pd
import pytest

from albert import Albert
from albert.collections.worksheets import WorksheetCollection
from albert.resources.sheets import CellColor, Column
from albert.resources.worksheets import Sheet, Worksheet


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


########################## COLUMNS ##########################


def test_recolor_column(sheet: Sheet):
    for col in sheet.columns:
        if col.type == "Formula":
            col.recolor_cells(color=CellColor.RED)
            for c in col.cells:
                assert c.color == CellColor.RED


# Because you cannot delete Formulation Columns, We will need to mock this test.
# def test_crud_formulation_column(sheet):
#     new_col = sheet.add_formulation_columns(formulation_names=["my cool formulation"])[0]
