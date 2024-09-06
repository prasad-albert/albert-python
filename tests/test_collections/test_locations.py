import pytest

from albert.albert import Albert
from albert.collections.locations import Location


@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    for i, c in enumerate(returned_list):
        if i == 30:
            break
        assert isinstance(c, Location)
        assert isinstance(c.name, str)
        assert c.id.startswith("LOC")


def test_simple_list(client):
    simple_loc_list = client.locations.list()
    _list_asserts(simple_loc_list)
