import pytest
from albert import Albert
from albert.resources.units import Unit, UnitCategory

@pytest.fixture(scope="module")
def client():
    return Albert()


def generate_unit_seeds() -> list[Unit]:
    """
    Generates a list of Unit seed objects for testing without IDs.

    Returns
    -------
    List[Unit]
        A list of Unit objects with different permutations.
    """

    return [
        # Basic unit with length category
        Unit(
            name="Meter",
            symbol="m",
            synonyms=["Metre"],
            category=UnitCategory.LENGTH,
            verified=True
        ),
        
        # Unit with mass category
        Unit(
            name="Kilogram",
            symbol="kg",
            category=UnitCategory.MASS,
            verified=True
        ),
        
        # Unit with temperature category and synonyms
        Unit(
            name="Celsius",
            symbol="°C",
            synonyms=["Centigrade"],
            category=UnitCategory.TEMPERATURE,
            verified=False
        ),
        
        # Unit with energy category
        Unit(
            name="Joule",
            symbol="J",
            category=UnitCategory.ENERGY,
            verified=True
        ),
        
        # Unit with volume category
        Unit(
            name="Liter",
            symbol="L",
            synonyms=["Litre"],
            category=UnitCategory.VOLUME,
            verified=True
        )
    ]


@pytest.fixture(scope="function")
def seeded_units(client: Albert):
    """
    Fixture to seed units before the test and delete them after.

    Parameters
    ----------
    client : Albert
        The Albert SDK client instance.

    Returns
    -------
    List[Unit]
        The list of seeded Unit objects.
    """
    # Seed the units
    seeded = []
    for unit in generate_unit_seeds():
        created_unit = client.units.create(unit=unit)
        seeded.append(created_unit)

    yield seeded  # Provide the seeded units to the test

    # Teardown - delete the seeded units after the test
    for unit in seeded:
        client.units.delete(unit_id=unit.id)
