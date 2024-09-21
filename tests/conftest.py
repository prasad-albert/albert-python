from collections.abc import Iterator

import pytest

from albert import Albert
from albert.resources.cas import Cas
from albert.resources.companies import Company
from albert.resources.locations import Location
from albert.resources.projects import Project
from albert.resources.tags import Tag
from albert.resources.units import Unit
from tests.seeding.cas import generate_cas_seeds
from tests.seeding.companies import generate_company_seeds
from tests.seeding.locations import generate_location_seeds
from tests.seeding.projects import generate_project_seeds
from tests.seeding.tags import generate_tag_seeds
from tests.seeding.units import generate_unit_seeds


@pytest.fixture(scope="session")
def client() -> Albert:
    return Albert()


@pytest.fixture(scope="function")
def seeded_cas(client: Albert) -> Iterator[list[Cas]]:
    # Seed the CAS
    seeded = []
    for cas in generate_cas_seeds():
        created_cas = client.cas_numbers.create(cas=cas)
        seeded.append(created_cas)

    yield seeded  # Provide the seeded CAS to the test

    # Teardown - delete the seeded CAS after the test
    for cas in seeded:
        client.cas_numbers.delete(cas_id=cas.id)


@pytest.fixture(scope="function")
def seeded_companies(client: Albert) -> Iterator[list[Company]]:
    # Seed the companies
    seeded = []
    for company in generate_company_seeds():
        created_company = client.companies.create(company=company)
        seeded.append(created_company)

    yield seeded  # Provide the seeded companies to the test

    # Teardown - delete the seeded companies after the test
    for company in seeded:
        client.companies.delete(id=company.id)


@pytest.fixture(scope="function")
def seeded_locations(client: Albert) -> Iterator[list[Location]]:
    # Seed the Locations
    seeded = []
    for location in generate_location_seeds():
        created_location = client.locations.create(location=location)
        seeded.append(created_location)

    yield seeded  # Provide the seeded Locations to the test

    # Teardown - delete the seeded Locations after the test
    for location in seeded:
        client.locations.delete(location_id=location.id)


# Example usage within a pytest fixture
@pytest.fixture(scope="function")
def seeded_tags(client: Albert) -> Iterator[list[Tag]]:
    # Seed the tags
    seeded = []
    for tag in generate_tag_seeds():
        created_tag = client.tags.create(tag=tag)
        seeded.append(created_tag)

    yield seeded  # Provide the seeded tags to the test

    # Teardown - delete the seeded tags after the test
    for tag in seeded:
        client.tags.delete(tag_id=tag.id)


@pytest.fixture(scope="function")
def seeded_units(client: Albert) -> Iterator[list[Unit]]:
    # Seed the units
    seeded = []
    for unit in generate_unit_seeds():
        created_unit = client.units.create(unit=unit)
        seeded.append(created_unit)

    yield seeded  # Provide the seeded units to the test

    # Teardown - delete the seeded units after the test
    for unit in seeded:
        client.units.delete(unit_id=unit.id)


@pytest.fixture(scope="function")
def seeded_projects(
    client: Albert,
    seeded_tags: list[Tag],
    seeded_companies: list[Company],
) -> Iterator[list[Project]]:
    # Seed the projects using seeded tags and companies
    seeded = []
    for project in generate_project_seeds(seeded_tags, seeded_companies):
        created_project = client.projects.create(project=project)
        seeded.append(created_project)

    yield seeded  # Provide the seeded projects to the test

    # Teardown - delete the seeded projects after the test
    for project in seeded:
        client.projects.delete(project_id=project.id)
