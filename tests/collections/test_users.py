from collections.abc import Generator

from albert.albert import Albert
from albert.collections.users import User


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


def test_simple_users_list(client: Albert):
    simple_user_list = client.users.list()
    assert isinstance(simple_user_list, Generator)
    _list_asserts(simple_user_list)


def test_advanced_users_list(client: Albert):
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

    adv_list = client.users.list(text="Lenore", search_email=True, search_name=True)
    assert isinstance(adv_list, Generator)
    _list_asserts(adv_list)


def test_user_get(client: Albert):
    first_hit = next(client.users.list(text="Lenore"))
    user_from_get = client.users.get_by_id(user_id=first_hit.id)
    assert user_from_get.id == first_hit.id
    assert isinstance(user_from_get, User)


def test_user_crud(client: Albert):
    existing_role = client.roles.list()[0]
    existing_loc = next(client.locations.list())
    test_user = User(
        name="Fake User SDK Testing",
        email="faux_person@albertinvent.com",
        roles=[existing_role],
        location=existing_loc,
    )
    registered_user = client.users.create(user=test_user)
    assert isinstance(registered_user, User)
    assert registered_user.name == test_user.name
    assert registered_user.id

    deleted = client.users.delete(user_id=registered_user.id)
    assert deleted
