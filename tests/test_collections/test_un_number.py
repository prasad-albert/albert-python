from albert.collections.un_numbers import UnNumber, UnNumberCollection
from albert.albert import Albert
from albert.collections.base import OrderBy
import pytest
from typing import Generator


@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    for i, u in enumerate(returned_list):
        if i == 100:
            break
        assert isinstance(u, UnNumber)
        assert isinstance(u.un_number, str)
        assert isinstance(u.id, str)
        assert u.id.startswith("UNN")


def test_simple_un_number_list(client):
    simple_list = client.un_numbers.list()
    _list_asserts(simple_list)
    assert isinstance(simple_list, Generator)


def test_advanced_un_number_list(client):
    adv_list = client.un_numbers.list(name="56", exact_match=False)
    assert isinstance(adv_list, Generator)
    _list_asserts(adv_list)


def test_un_number_get_by(client:Albert):
    found_un = client.un_numbers.get_by_name(name="UN9006")
    assert isinstance(found_un, UnNumber)
    found_by_id = client.un_numbers.get_by_id(un_number_id=found_un.id)
    assert isinstance(found_by_id, UnNumber)
    assert found_by_id.un_number == found_un.un_number
    assert found_by_id.id == found_un.id
