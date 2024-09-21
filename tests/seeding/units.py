from albert.resources.units import Unit, UnitCategory


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
            verified=True,
        ),
        # Unit with mass category
        Unit(name="Kilogram", symbol="kg", category=UnitCategory.MASS, verified=True),
        # Unit with temperature category and synonyms
        Unit(
            name="Celsius",
            symbol="°C",
            synonyms=["Centigrade"],
            category=UnitCategory.TEMPERATURE,
            verified=False,
        ),
        # Unit with energy category
        Unit(name="Joule", symbol="J", category=UnitCategory.ENERGY, verified=True),
        # Unit with volume category
        Unit(
            name="Liter",
            symbol="L",
            synonyms=["Litre"],
            category=UnitCategory.VOLUME,
            verified=True,
        ),
    ]
