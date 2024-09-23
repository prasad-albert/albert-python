from collections.abc import Generator
from time import sleep

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


def test_create_cas(client: Albert):
    # Create a new CAS entry
    new_cas = Cas(number="123-45-6", description="Test CAS")
    created_cas = client.cas_numbers.create(cas=new_cas)

    assert isinstance(created_cas, Cas)
    assert created_cas.number == "123-45-6"
    assert created_cas.description == "Test CAS"

    # Try to create the same CAS again, should return the existing one
    existing_cas = client.cas_numbers.create(cas="123-45-6")
    assert existing_cas.id == created_cas.id
    assert existing_cas.number == "123-45-6"


def test_update_cas(cas_collection, seeded_cas: list[Cas]):
    # Update the description of a seeded CAS entry
    cas_to_update = seeded_cas[0]
    updated_description = "Updated CAS Description"
    cas_to_update.description = updated_description

    updated_cas = cas_collection.update(updated_object=cas_to_update)

    assert updated_cas.description == updated_description

    # Verify the cache has the updated object
    assert cas_collection.cas_cache[cas_to_update.number].description == updated_description


def test_delete_cas(cas_collection, client: Albert):
    # Create a new CAS to be deleted
    new_cas = Cas(number="987-65-4", description="Delete Test CAS")

    created_cas = cas_collection.create(cas=new_cas)

    # Verify that the CAS was created
    sleep(
        1
    )  # I was having some flakes here I think due to a race condition. This would make sence because the object probably takes a moment to get into the search db
    assert cas_collection.cas_exists(number="987-65-4")

    # Delete the CAS
    deleted = cas_collection.delete(cas_id=created_cas.id)
    assert deleted

    # Verify that the CAS no longer exists
    assert not cas_collection.cas_exists(number="987-65-4")


def test_get_by_number(cas_collection, client: Albert):
    # Create a new CAS to be deleted
    new_cas = Cas(number="987-65-4", description="Delete Test CAS")
    created_cas = cas_collection.create(cas=new_cas)

    # Verify that the CAS was created
    sleep(
        1
    )  # I was having some flakes here I think due to a race condition. This would make sence because the object probably takes a moment to get into the search db
    returned_cas = cas_collection.get_by_number(number="987-65-4")
    assert returned_cas.id == created_cas.id
    # Delete the CAS
    deleted = cas_collection.delete(cas_id=created_cas.id)
    assert deleted
