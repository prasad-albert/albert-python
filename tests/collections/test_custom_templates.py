from collections.abc import Generator

import pytest

from albert.albert import Albert
from albert.resources.custom_templates import CustomTemplate, CustomTemplateData


# from albert.resources.inventory import CasAmount, InventoryItem
# from albert.resources.units import UnitCategory
def _list_asserts(returned_list):
    # found = False
    for i, u in enumerate(returned_list):
        if i == 50:
            break
        assert isinstance(u, CustomTemplate)
        # found = True
        if hasattr(u, "data"):
            for d in u.data:
                assert isinstance(d, CustomTemplateData)
    # assert found #None of test yet to check :(


@pytest.fixture(scope="module")
def client():
    return Albert()


def test_basics(client: Albert):
    list_response = client.templates.list()
    assert isinstance(list_response, Generator)
    _list_asserts(list_response)
