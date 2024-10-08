from albert.resources.sheets import Cell, CellType, Column, Sheet


def test_get_cell_value():
    cell = Cell(
        column_id="TEST_COL1",
        row_id="TEST_ROW1",
        type=CellType.BLANK,
        design_id="TEST_DESIGN1",
        value="test",
    )
    assert cell.raw_value == "test"
    assert cell.color is None
