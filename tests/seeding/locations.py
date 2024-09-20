import pytest

from albert import Albert
from albert.resources.locations import Location  # Ensure correct import of Location model


@pytest.fixture(scope="module")
def client():
    return Albert()


def generate_location_seeds() -> list[Location]:
    """
    Generates a list of Location seed objects for testing without IDs.

    Returns
    -------
    List[Location]
        A list of Location objects with different permutations.
    """

    return [
        # Basic location with required fields (name, latitude, longitude, address)
        Location(
            name="Warehouse A",
            latitude=40.7,
            longitude=-74.0,
            address="123 Warehouse St, New York, NY",
        ),
        # Location with full fields including optional country
        Location(
            name="Headquarters",
            latitude=37.8,
            longitude=-122.4,
            address="123 Market St, San Francisco, CA",
            country="US",
        ),
        # Location with required fields but without the country
        Location(
            name="Remote Office",
            latitude=48.9,
            longitude=2.4,
            address="10 Office Lane, Paris",
        ),
        # Another location with all fields
        Location(
            name="Test Site",
            latitude=51.5,
            longitude=-0.1,
            address="Test Facility, London",
            country="GB",
        ),
    ]


@pytest.fixture(scope="function")
def seeded_locations(client: Albert):
    """
    Fixture to seed Locations before the test and delete them after.

    Parameters
    ----------
    client : Albert
        The Albert SDK client instance.

    Returns
    -------
    List[Location]
        The list of seeded Location objects.
    """
    # Seed the Locations
    seeded = []
    for location in generate_location_seeds():
        created_location = client.locations.create(location=location)
        seeded.append(created_location)

    yield seeded  # Provide the seeded Locations to the test

    # Teardown - delete the seeded Locations after the test
    for location in seeded:
        client.locations.delete(location_id=location.id)
