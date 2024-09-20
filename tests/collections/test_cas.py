from collections.abc import Generator

import pytest

from albert.albert import Albert
from albert.collections.base import OrderBy
from albert.resources.cas import Cas
from albert.utils.exceptions import AlbertAPIError
from tests.seeding.cas import seeded_cas

@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    found = False
    for i, c in enumerate(returned_list):
        if i == 30:
            break
        assert isinstance(c, Cas)
        assert isinstance(c.number, str)
        if c.name:
            assert isinstance(c.name, str)
        assert c.id.startswith("CAS")
        found = True
    assert found


def test_simple_cas_list(client, seeded_cas):
    simple_list = client.cas_numbers.list()
    assert isinstance(simple_list, Generator)
    _list_asserts(simple_list)


def test_cas_not_found(client: Albert, seeded_cas):
    with pytest.raises(AlbertAPIError):
        client.cas_numbers.get_by_id(cas_id="foo bar")


def test_advanced_cas_list(client: Albert, seeded_cas):
    adv_list = client.cas_numbers.list(number="64-17-5", order_by=OrderBy.DESCENDING)
    assert isinstance(adv_list, Generator)
    adv_list = list(adv_list)
    _list_asserts(adv_list)

    assert adv_list[0].number == "64-17-5"
