import pytest

from albert import Albert
from albert.resources.companies import Company  # Ensure correct import of Company model


@pytest.fixture(scope="module")
def client():
    return Albert()


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


@pytest.fixture(scope="function")
def seeded_companies(client: Albert):
    """
    Fixture to seed companies before the test and delete them after.

    Parameters
    ----------
    client : Albert
        The Albert SDK client instance.

    Returns
    -------
    List[Company]
        The list of seeded Company objects.
    """
    # Seed the companies
    seeded = []
    for company in generate_company_seeds():
        created_company = client.companies.create(company=company)
        seeded.append(created_company)

    yield seeded  # Provide the seeded companies to the test

    # Teardown - delete the seeded companies after the test
    for company in seeded:
        client.companies.delete(id=company.id)
