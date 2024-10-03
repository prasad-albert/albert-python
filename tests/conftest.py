import time
from collections.abc import Iterator
from contextlib import suppress

import pytest

from albert import Albert
from albert.resources.base import Status
from albert.resources.cas import Cas
from albert.resources.companies import Company
from albert.resources.inventory import InventoryItem
from albert.resources.lists import ListItem
from albert.resources.locations import Location
from albert.resources.parameters import Parameter
from albert.resources.projects import Project
from albert.resources.roles import Role
from albert.resources.tags import Tag
from albert.resources.units import Unit
from albert.resources.users import User
from albert.utils.exceptions import BadRequestError, ForbiddenError, NotFoundError
from tests.seeding import (
    generate_cas_seeds,
    generate_company_seeds,
    generate_inventory_seeds,
    generate_list_item_seeds,
    generate_location_seeds,
    generate_lot_seeds,
    generate_parameter_group_seeds,
    generate_parameter_seeds,
    generate_project_seeds,
    generate_storage_location_seeds,
    generate_tag_seeds,
    generate_unit_seeds,
    generate_user_seeds,
)


@pytest.fixture(scope="session")
def client() -> Albert:
    return Albert()


@pytest.fixture(scope="session")
def seeded_projects(client: Albert, seeded_locations) -> Iterator[list[Project]]:
    # Seed the projects using seeded locations

    seeded = []

    for project in generate_project_seeds(seeded_locations=seeded_locations):
        existing = client.projects.list()
        for m in existing:
            if m.description.lower() == project.description.lower():
                client.projects.delete(project_id=m.id)
        created_project = client.projects.create(project=project)
        seeded.append(created_project)

    yield seeded  # Provide the seeded projects to the test

    # Teardown - delete the seeded projects after the test
    with suppress(NotFoundError):
        for project in seeded:
            client.projects.delete(project_id=project.id)


@pytest.fixture(scope="session")
def seeded_cas(client: Albert) -> Iterator[list[Cas]]:
    # Seed the CAS
    seeded = []
    for cas in generate_cas_seeds():
        created_cas = client.cas_numbers.create(cas=cas)
        seeded.append(created_cas)
    time.sleep(1.5)  # avoid race condition while it populated through DBs
    yield seeded  # Provide the seeded CAS to the test

    # Teardown - delete the seeded CAS after the test
    with suppress(BadRequestError | NotFoundError):
        for cas in seeded:
            client.cas_numbers.delete(cas_id=cas.id)


@pytest.fixture(scope="session")
def seeded_companies(client: Albert) -> Iterator[list[Company]]:
    # Seed the companies
    seeded = []
    for company in generate_company_seeds():
        created_company = client.companies.create(company=company)
        seeded.append(created_company)

    yield seeded  # Provide the seeded companies to the test

    # Teardown - delete the seeded companies after the test
    # ForbiddenError is raised when trying to delete a company that has InventoryItems associated with it (may be a bug. Teams discussion ongoing)
    with suppress(NotFoundError, ForbiddenError):
        for company in seeded:
            client.companies.delete(id=company.id)


@pytest.fixture(scope="session")
def seeded_locations(client: Albert) -> Iterator[list[Location]]:
    # Seed the Locations
    seeded = []
    for location in generate_location_seeds():
        created_location = client.locations.create(location=location)
        seeded.append(created_location)

    yield seeded  # Provide the seeded Locations to the test

    # Teardown - delete the seeded Locations after the test
    with suppress(NotFoundError):
        for location in seeded:
            client.locations.delete(location_id=location.id)


@pytest.fixture(scope="session")
def seeded_storage_locations(
    client: Albert, seeded_locations: list[Location]
) -> Iterator[list[Location]]:
    seeded = []
    for storage_location in generate_storage_location_seeds(seeded_locations=seeded_locations):
        created_location = client.storage_locations.create(storage_location=storage_location)
        seeded.append(created_location)
    yield seeded

    with suppress(NotFoundError):
        for storage_location in seeded:
            client.storage_locations.delete(id=storage_location.id)


@pytest.fixture(scope="session")
def seeded_lists(
    client: Albert,
) -> Iterator[list[ListItem]]:
    seeded = []
    # Seed the lists
    for list_item in generate_list_item_seeds():
        created_list = client.lists.create(list_item=list_item)
        seeded.append(created_list)

    yield seeded
    # NOTE: There is NO delete method for lists. This is because the list Items cannot be deleted in the Albert API.


@pytest.fixture(scope="session")
def seeded_tags(client: Albert) -> Iterator[list[Tag]]:
    # Seed the tags
    seeded = []
    for tag in generate_tag_seeds():
        created_tag = client.tags.create(tag=tag)
        seeded.append(created_tag)

    yield seeded  # Provide the seeded tags to the test

    # Teardown - delete the seeded tags after the test
    with suppress(NotFoundError):
        for tag in seeded:
            client.tags.delete(tag_id=tag.id)


@pytest.fixture(scope="session")
def seeded_units(client: Albert) -> Iterator[list[Unit]]:
    # Seed the units
    seeded = []
    for unit in generate_unit_seeds():
        created_unit = client.units.create(unit=unit)
        seeded.append(created_unit)
    time.sleep(1.5)  # avoid race condition while it populated through DBs
    yield seeded  # Provide the seeded units to the test

    # Teardown - delete the seeded units after the test
    with suppress(NotFoundError):
        for unit in seeded:
            client.units.delete(unit_id=unit.id)


@pytest.fixture(scope="session")
def seeded_roles(client: Albert) -> Iterator[list[Role]]:
    # Roles are not deleted or created. We just use the existing roles.
    existing = []
    for role in client.roles.list():
        existing.append(role)

    yield existing  # Provide the seeded units to the test


@pytest.fixture(scope="session")
def seeded_users(client: Albert, seeded_roles, seeded_locations) -> Iterator[list[User]]:
    seeded = []
    # Here, seeded_roles and seeded_locations will already be lists from the respective fixtures

    for user in generate_user_seeds(seeded_roles=seeded_roles, seeded_locations=seeded_locations):
        matches = client.users.list(text=user.name)
        found = False
        for m in matches:
            if m.name == user.name:
                created_user = m
                created_user.status = Status.ACTIVE.value
                client.users.update(updated_object=created_user)
                found = True
                break
        if not found:
            created_user = client.users.create(user=user)
        seeded.append(created_user)
    time.sleep(1.5)  # avoid race condition while it populates through DBs
    yield seeded  # Provide the seeded users to the test

    # Teardown - archive/set inactive
    for user in seeded:
        user.status = Status.INACTIVE.value
        client.users.update(updated_object=user)


@pytest.fixture(scope="session")
def seeded_inventory(
    client: Albert, seeded_cas, seeded_tags, seeded_companies, seeded_locations
) -> Iterator[list[InventoryItem]]:
    seeded = []
    for inventory in generate_inventory_seeds(
        seeded_cas=seeded_cas,
        seeded_tags=seeded_tags,
        seeded_companies=seeded_companies,
        seeded_locations=seeded_locations,
    ):
        created_inventory = client.inventory.create(inventory_item=inventory)
        seeded.append(created_inventory)
    yield seeded
    for inventory in seeded:
        with suppress(NotFoundError):
            client.inventory.delete(inventory_id=inventory.id)


@pytest.fixture(scope="session")
def seeded_parameters(client: Albert) -> Iterator[list[Parameter]]:
    seeded = []
    for parameter in generate_parameter_seeds():
        created_parameter = client.parameters.create(parameter=parameter)
        seeded.append(created_parameter)
    yield seeded
    for parameter in seeded:
        with suppress(NotFoundError):
            client.parameters.delete(id=parameter.id)


@pytest.fixture(scope="session")
def seeded_parameter_groups(
    client: Albert, seeded_parameters, seeded_tags, seeded_units
) -> Iterator[list[Parameter]]:
    seeded = []
    for parameter_group in generate_parameter_group_seeds(
        seeded_parameters=seeded_parameters, seeded_tags=seeded_tags, seeded_units=seeded_units
    ):
        created_parameter_group = client.parameter_groups.create(parameter_group=parameter_group)
        seeded.append(created_parameter_group)
        time.sleep(1.5)  # avoid race condition while it populates through DBs

    yield seeded
    for parameter_group in seeded:
        with suppress(NotFoundError):
            client.parameter_groups.delete(id=parameter_group.id)


# PUT on lots is currently bugged. Teams discussion ongoing
@pytest.fixture(scope="session")
def seeded_lots(client: Albert, seeded_inventory, seeded_storage_locations, seeded_locations):
    seeded = []
    all_lots = generate_lot_seeds(
        seeded_inventory=seeded_inventory,
        seeded_storage_locations=seeded_storage_locations,
        seeded_locations=seeded_locations,
    )
    seeded = client.lots.create(lots=all_lots)
    # seeded.append(created_lot)
    yield seeded
    for lot in seeded:
        with suppress(NotFoundError):
            client.lots.delete(lot_id=lot.id)
