import time
from collections.abc import Generator

import pytest

from albert.albert import Albert
from albert.collections.base import OrderBy
from albert.resources.cas import Cas
from albert.utils.exceptions import AlbertAPIError


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


def test_simple_cas_list(client: Albert):
    simple_list = client.cas_numbers.list()
    assert isinstance(simple_list, Generator)
    _list_asserts(simple_list)


def test_cas_not_found(client: Albert):
    with pytest.raises(AlbertAPIError):
        client.cas_numbers.get_by_id(cas_id="foo bar")


def test_advanced_cas_list(client: Albert, seeded_cas: list[Cas]):
    number = seeded_cas[0].number
    adv_list = client.cas_numbers.list(number=number, order_by=OrderBy.DESCENDING)
    assert isinstance(adv_list, Generator)
    adv_list = list(adv_list)
    _list_asserts(adv_list)

    assert adv_list[0].number == number

    adv_list2 = client.cas_numbers.list(id=seeded_cas[0].id)
    _list_asserts(adv_list2)

    small_page = client.cas_numbers._list_generator(limit=2)
    _list_asserts(small_page)


def test_cas_exists(client: Albert, seeded_cas: list[Cas]):
    # Check if CAS exists for a seeded CAS number
    cas_number = seeded_cas[0].number
    assert client.cas_numbers.cas_exists(number=cas_number)

    # Check if CAS does not exist for a non-existent CAS number
    assert not client.cas_numbers.cas_exists(number="999-99-9xxxx")


def test_update_cas(client: Albert, seeded_cas: list[Cas]):
    # Update the description of a seeded CAS entry
    cas_to_update = seeded_cas[0]
    updated_description = "Updated CAS Description"
    cas_to_update.description = updated_description

    updated_cas = client.cas_numbers.update(updated_object=cas_to_update)

    assert updated_cas.description == updated_description


def test_create_and_delete_cas(client: Albert):
    # Create a new CAS to be deleted
    new_cas = Cas(number="987-65-4", description="Delete Test CAS")

    created_cas = client.cas_numbers.create(cas=new_cas)

    assert isinstance(created_cas, Cas)
    assert isinstance(created_cas.id, str)

    # Verify that the CAS was created
    # I was having some flakes here I think due to a race condition. This would make sence because the object probably takes a moment to get into the search db
    time.sleep(1.5)
    assert client.cas_numbers.cas_exists(number="987-65-4")

    # Delete the CAS
    deleted = client.cas_numbers.delete(cas_id=created_cas.id)
    assert deleted

    # Verify that the CAS no longer exists
    assert not client.cas_numbers.cas_exists(number="987-65-4")


def test_get_by_number(client: Albert):
    # Create a new CAS to be deleted
    new_cas = Cas(number="987-65-4", description="Delete Test CAS")
    created_cas = client.cas_numbers.create(cas=new_cas)

    # Verify that the CAS was created
    # I was having some flakes here I think due to a race condition. This would make sence because the object probably takes a moment to get into the search db
    time.sleep(1.5)
    returned_cas = client.cas_numbers.get_by_number(number="987-65-4", exact_match=True)
    assert returned_cas.id == created_cas.id
    # Delete the CAS
    deleted = client.cas_numbers.delete(cas_id=created_cas.id)
    assert deleted
