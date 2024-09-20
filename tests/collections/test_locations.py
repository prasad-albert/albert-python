from collections.abc import Generator

import pytest

from albert.albert import Albert
from albert.collections.locations import Location
from tests.seeding.locations import seeded_locations

@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    found = False
    for i, c in enumerate(returned_list):
        if i == 30:
            break
        assert isinstance(c, Location)
        assert isinstance(c.name, str)
        assert c.id.startswith("LOC")


def test_simple_list(client: Albert, seeded_locations):
    simple_loc_list = client.locations.list()
    assert isinstance(simple_loc_list, Generator)
    _list_asserts(simple_loc_list)


def test_get_by_id(client: Albert, seeded_locations):
    # Assuming we want to get the first seeded location by ID
    seeded_location = seeded_locations[0]
    fetched_location = client.locations.get_by_id(id=seeded_location.id)

    assert isinstance(fetched_location, Location)
    assert fetched_location.id == seeded_location.id
    assert fetched_location.name == seeded_location.name


def test_create_location(client: Albert):
    # Create a new location and check if it's created properly
    new_location = Location(
        name="New Test Location",
        latitude=40.7,
        longitude=-74.0,
        address="123 New Test St, New York, NY",
    )

    created_location = client.locations.create(location=new_location)
    assert isinstance(created_location, Location)
    assert created_location.name == "New Test Location"
    assert created_location.latitude == 40.7
    assert created_location.longitude == -74.0

    # Clean up
    client.locations.delete(location_id=created_location.id)


def test_update_location(client: Albert, seeded_locations):
    # Update the first seeded location
    seeded_location = seeded_locations[0]
    updated_location = Location(
        name="Updated Test Location",
        latitude=40.0,
        longitude=-75.0,
        address=seeded_location.address,
        id=seeded_location.id,
    )

    # Perform the update
    updated_loc = client.locations.update(updated_object=updated_location)

    assert isinstance(updated_loc, Location)
    assert updated_loc.name == "Updated Test Location"
    assert updated_loc.latitude == 40.0
    assert updated_loc.longitude == -75.0


def test_location_exists(client: Albert, seeded_locations):
    # Check if the first seeded location exists
    seeded_location = seeded_locations[0]
    exists = client.locations.location_exists(location=seeded_location)

    assert exists is not None
    assert isinstance(exists, Location)
    assert exists.name == seeded_location.name


def test_delete_location(client: Albert):
    # Create a new location to delete
    new_location = Location(
        name="Location to Delete",
        latitude=41.8,
        longitude=-87.6,
        address="456 Delete St, Chicago, IL",
    )

    created_location = client.locations.create(location=new_location)
    assert isinstance(created_location, Location)

    # Now delete it
    deleted = client.locations.delete(location_id=created_location.id)
    assert deleted is True

    # Ensure it no longer exists
    does_exist = client.locations.location_exists(location=created_location)
    assert does_exist is None
