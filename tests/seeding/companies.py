from albert.resources.companies import Company


def generate_company_seeds() -> list[Company]:
    """
    Generates a list of Company seed objects for testing without IDs.

    Returns
    -------
    List[Company]
        A list of Company objects with different permutations.
    """

    return [
        # Basic company with name only
        Company(name="Acme Corporation"),
        # Company with a full name and additional private attribute (distance)
        Company(name="Globex Corporation"),
        # Another company
        Company(name="Initech"),
        # One more company with a distance attribute
        Company(name="Umbrella Corp"),
    ]
