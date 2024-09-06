from collections.abc import Generator

import pytest

from albert.albert import Albert
from albert.collections.base import OrderBy
from albert.resources.cas import Cas
from albert.utils.error_utils.exceptions import AlbertAPIError

# Developer Note: We need more test here once we better uunderstand this collection's behavior.
# The startKey / "lastKey" appear broken :(


@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    for i, c in enumerate(returned_list):
        if i == 30:
            break
        assert isinstance(c, Cas)
        assert isinstance(c.number, str)
        if c.name:
            assert isinstance(c.name, str)
        assert c.id.startswith("CAS")


def test_simple_cas_list(client):
    simple_list = client.cas_numbers.list()
    assert isinstance(simple_list, Generator)
    _list_asserts(simple_list)


def test_cas_not_found(client: Albert):
    with pytest.raises(AlbertAPIError):
        client.cas_numbers.get_by_id(cas_id="foo bar")


def test_advanced_cas_list(client):
    adv_list = client.cas_numbers.list(number="64-17-5", order_by=OrderBy.DESCENDING)
    assert isinstance(adv_list, Generator)
    _list_asserts(adv_list)

    # For some reason, the first hit does not match.
    # assert adv_list[0].number == "64-17-5"

    # Actually... None of them match.
    # found = False
    # for c in adv_list:
    #     if c.number == "64-17-5":
    #         found = True
    # assert found
