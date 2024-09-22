from collections.abc import Iterator
from contextlib import suppress

import pytest

from albert import Albert
from albert.collections.cas import CasCollection
from albert.collections.companies import CompanyCollection
from albert.collections.inventory import InventoryCategory
from albert.collections.locations import LocationCollection
from albert.collections.projects import ProjectCollection
from albert.collections.tags import TagCollection
from albert.collections.units import UnitCollection
from albert.resources.cas import Cas
from albert.resources.companies import Company
from albert.resources.locations import Location
from albert.resources.projects import Project
from albert.resources.tags import Tag
from albert.resources.units import Unit
from albert.utils.exceptions import NotFoundError
from tests.seeding import (
    generate_cas_seeds,
    generate_company_seeds,
    generate_location_seeds,
    generate_project_seeds,
    generate_tag_seeds,
    generate_unit_seeds,
)


@pytest.fixture(scope="session")
def client() -> Albert:
    return Albert()


@pytest.fixture(scope="session")
def cas_collection(client: Albert) -> CasCollection:
    return client.cas_numbers


@pytest.fixture(scope="session")
def location_collection(client: Albert) -> LocationCollection:
    return client.locations


@pytest.fixture(scope="session")
def project_collection(client: Albert) -> ProjectCollection:
    return client.projects


@pytest.fixture(scope="session")
def company_collection(client: Albert) -> CompanyCollection:
    return client.companies


@pytest.fixture(scope="session")
def inventory_collection(client: Albert) -> InventoryCategory:
    return client.inventory


@pytest.fixture(scope="session")
def tag_collection(client: Albert) -> TagCollection:
    return client.tags


@pytest.fixture(scope="session")
def unit_collection(client: Albert) -> UnitCollection:
    return client.units


@pytest.fixture(scope="session")
def seeded_projects(
    project_collection: ProjectCollection, seeded_locations
) -> Iterator[list[Project]]:
    # Seed the projects using seeded locations

    seeded = []

    for project in generate_project_seeds(seeded_locations=seeded_locations):
        existing = project_collection.list()
        print("***")
        print(project.description)
        for m in existing:
            print(m.description)
            if m.description.lower() == project.description.lower():
                print("DELETING EXISTING")
                project_collection.delete(project_id=m.id)
        created_project = project_collection.create(project=project)
        seeded.append(created_project)

    yield seeded  # Provide the seeded projects to the test

    # Teardown - delete the seeded projects after the test
    for project in seeded:
        with suppress(NotFoundError):
            project_collection.delete(project_id=project.id)


@pytest.fixture(scope="session")
def seeded_cas(cas_collection: CasCollection) -> Iterator[list[Cas]]:
    # Seed the CAS
    seeded = []
    for cas in generate_cas_seeds():
        created_cas = cas_collection.create(cas=cas)
        seeded.append(created_cas)

    yield seeded  # Provide the seeded CAS to the test

    # Teardown - delete the seeded CAS after the test
    for cas in seeded:
        with suppress(NotFoundError):
            cas_collection.delete(cas_id=cas.id)


@pytest.fixture(scope="session")
def seeded_companies(company_collection: CompanyCollection) -> Iterator[list[Company]]:
    # Seed the companies
    seeded = []
    for company in generate_company_seeds():
        created_company = company_collection.create(company=company)
        seeded.append(created_company)

    yield seeded  # Provide the seeded companies to the test

    # Teardown - delete the seeded companies after the test
    for company in seeded:
        with suppress(NotFoundError):
            company_collection.delete(id=company.id)


@pytest.fixture(scope="session")
def seeded_locations(location_collection: LocationCollection) -> Iterator[list[Location]]:
    # Seed the Locations
    seeded = []
    for location in generate_location_seeds():
        created_location = location_collection.create(location=location)
        seeded.append(created_location)

    yield seeded  # Provide the seeded Locations to the test

    # Teardown - delete the seeded Locations after the test
    for location in seeded:
        with suppress(NotFoundError):
            location_collection.delete(location_id=location.id)


# Example usage within a pytest fixture
@pytest.fixture(scope="session")
def seeded_tags(tag_collection: TagCollection) -> Iterator[list[Tag]]:
    # Seed the tags
    seeded = []
    for tag in generate_tag_seeds():
        created_tag = tag_collection.create(tag=tag)
        seeded.append(created_tag)

    yield seeded  # Provide the seeded tags to the test

    # Teardown - delete the seeded tags after the test
    for tag in seeded:
        with suppress(NotFoundError):
            tag_collection.delete(tag_id=tag.id)


@pytest.fixture(scope="session")
def seeded_units(unit_collection: UnitCollection) -> Iterator[list[Unit]]:
    # Seed the units
    seeded = []
    for unit in generate_unit_seeds():
        created_unit = unit_collection.create(unit=unit)
        seeded.append(created_unit)

    yield seeded  # Provide the seeded units to the test

    # Teardown - delete the seeded units after the test
    for unit in seeded:
        with suppress(NotFoundError):
            unit_collection.delete(unit_id=unit.id)
