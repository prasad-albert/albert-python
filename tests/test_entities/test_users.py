from albert.entity.users import User, UserCollection
import pytest
from albert.albert import Albert
from typing import Generator
from albert.entity.roles import Role
from albert.entity.locations import Location


@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    found = False
    for i, u in enumerate(returned_list):
        found = True
        if i == 30:
            break
        assert isinstance(u, User)
        assert isinstance(u.name, str)
        assert isinstance(u.id, str)
        assert u.id.startswith("USR")
    assert found  # make sure at least one was returned


def test_simple_users_list(client):
    simple_user_list = client.users.list()
    assert isinstance(simple_user_list, Generator)
    _list_asserts(simple_user_list)


def test_advanced_users_list(client):
    adv_list = client.users.list(text="Lenore", search_email=False, search_name=True)
    assert isinstance(adv_list, Generator)
    _list_asserts(adv_list)
    found = False

    # Check something reasonable was found near the top
    adv_list = client.users.list(text="Lenore", search_email=False, search_name=True)
    for i, u in enumerate(adv_list):
        if i == 20:
            break
        if "lenore" in u.name.lower():
            found = True
            break
    assert found


def test_user_get(client):
    first_hit = next(client.users.list("Lenore"))
    user_from_get = client.users.get_by_id(first_hit.id)
    assert user_from_get.id == first_hit.id
    assert isinstance(user_from_get, User)


def test_user_crud(client):
    existing_role = Role(id="ROL95", tenant="TEN1", name="Myrole")
    existing_loc = Location(
        name="(D123) Duesseldorf, Germany",
        id="LOC1375",
        latitude=21.67752,
        longitude=5.737409,
        address="Quadpro 11, 40589 Düsseldorf, Germany",
        country="DE",
    )
    test_user = User(
        name="Fake User SDK Testing",
        email="faux_person@albertinvent.com",
        roles=[existing_role],
        location=existing_loc,
    )
    registered_user = client.users.create(test_user)
    assert isinstance(registered_user, User)
    assert registered_user.name == test_user.name
    assert registered_user.id

    deleted = client.users.delete(registered_user.id)
    assert deleted
