import pandas as pd
import pytest

from albert.albert import Albert
from albert.collections.worksheets import WorksheetCollection
from albert.resources.projects import Project
from albert.resources.sheets import Column, Sheet
from albert.resources.worksheets import Worksheet
from albert.utils.exceptions import NotFoundError


def test_get_worksheet(worksheet: Worksheet):
    assert isinstance(worksheet, Worksheet)
    assert isinstance(worksheet.project_id, str)
