import pandas as pd
import pytest

from albert import Albert
from albert.collections.worksheets import WorksheetCollection
from albert.resources.sheets import CellColor, Column, Component, DesignType, Row
from albert.resources.worksheets import Sheet, Worksheet
from albert.utils.exceptions import AlbertException


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


def test_add_formulation(sheet: Sheet, seeded_inventory):
    components = [
        Component(inventory_item=seeded_inventory[0], amount=66),
        Component(inventory_item=seeded_inventory[1], amount=34),
    ]
    # Note: A new column with the same name is going to be created every time this test is run.
    new_col = sheet.add_formulation(
        formulation_name="TEST my cool formulation", components=components
    )
    assert isinstance(new_col, Column)

    components_updated = [
        Component(inventory_item=seeded_inventory[0], amount=33),
        Component(inventory_item=seeded_inventory[1], amount=67),
    ]

    new_col = sheet.add_formulation(
        formulation_name="TEST my cool formulation", components=components_updated
    )
    assert isinstance(new_col, Column)

    for cell in new_col.cells:
        if cell.type == "INV":
            assert cell.value in ["33", "67"]
        elif cell.type == "TOT":
            assert cell.value == "100"


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


########################## ROWS ##########################


def test_add_and_remove_blank_rows(sheet: Sheet):
    new_row = sheet.add_blank_row(row_name="TEST app Design", design=DesignType.APPS)
    assert isinstance(new_row, Row)
    assert sheet.delete_row(row_id=new_row.row_id, design_id=sheet.app_design.id)

    new_row = sheet.add_blank_row(row_name="TEST products Design", design=DesignType.PRODUCTS)
    assert isinstance(new_row, Row)
    assert sheet.delete_row(row_id=new_row.row_id, design_id=sheet.product_design.id)

    # You cannot add a blank row to results design
    with pytest.raises(AlbertException):
        new_row = sheet.add_blank_row(row_name="TEST results Design", design=DesignType.RESULTS)
