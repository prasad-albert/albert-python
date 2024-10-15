
from albert.resources.worksheets import Worksheet


def test_get_worksheet(worksheet: Worksheet):
    assert isinstance(worksheet, Worksheet)
    assert isinstance(worksheet.project_id, str)
