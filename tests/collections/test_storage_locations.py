from collections.abc import Generator

from albert import Albert
from albert.resources.locations import Location
from albert.resources.storage_locations import StorageLocation


def _list_asserts(returned_list):
    found = False
    for i, u in enumerate(returned_list):
        if i == 50:
            break
        assert isinstance(u, StorageLocation)
        found = True
    assert found


def test_basic_lists(client: Albert):
    list_response = client.storage_locations.list()
    assert isinstance(list_response, Generator)
    _list_asserts(list_response)


def test_advanced_list(
    client: Albert,
    seeded_storage_locations: list[StorageLocation],
    seeded_locations: list[Location],
):
    list_response = client.storage_locations.list(
        name=[seeded_storage_locations[0].name], exact_match=True
    )
    assert isinstance(list_response, Generator)
    list_response = list(list_response)
    _list_asserts(list_response)
    for sl in list_response:
        assert sl.name == seeded_locations[0].name

    list_response = client.storage_locations.list(location=seeded_locations[0])
    list_response = list(list_response)
    _list_asserts(list_response)
    for sl in list_response:
        assert sl.location == seeded_storage_locations[0].location


def test_pagination(client: Albert, seeded_storage_locations: list[StorageLocation]):
    list_response = client.storage_locations._list_generator(limit=2)
    _list_asserts(list_response)


def test_avoids_dupes(caplog, client: Albert, seeded_storage_locations: list[StorageLocation]):
    sl = seeded_storage_locations[0].model_copy(update={"id": None})

    duped = client.storage_locations.create(storage_location=sl)
    assert (
        f"Storage location with name {sl.name} already exists, returning existing." in caplog.text
    )
    assert duped.id == seeded_storage_locations[0].id
    assert duped.name == seeded_storage_locations[0].name
    assert duped.location == seeded_storage_locations[0].location


def test_update(client: Albert, seeded_storage_locations: list[StorageLocation]):
    sl = seeded_storage_locations[0]
    sl.name = "TEST - New Name"
    updated = client.storage_locations.update(storage_location=sl)
    assert updated.id == seeded_storage_locations[0].id
    assert updated.name == seeded_storage_locations[0].name
