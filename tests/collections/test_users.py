from collections.abc import Generator

from albert.collections.users import Status, User, UserCollection


def _list_asserts(returned_list, limit=30):
    found = False
    for i, u in enumerate(returned_list):
        found = True
        if i == limit:
            break
        assert isinstance(u, User)
        assert isinstance(u.name, str)
        assert isinstance(u.id, str)
        assert u.id.startswith("USR")
    assert found  # make sure at least one was returned


def test_simple_users_list(user_collection):
    simple_user_list = user_collection.list()
    assert isinstance(simple_user_list, Generator)
    _list_asserts(simple_user_list)


def test_advanced_users_list(user_collection: UserCollection, seeded_users: list[User]):
    # Check something reasonable was found near the top
    faux_name = seeded_users[1].name.split(" ")[0]
    adv_list = user_collection.list(text=faux_name, status=Status.ACTIVE)
    for i, u in enumerate(adv_list):
        if i == 20:
            break
        if seeded_users[1].name.lower() == u.name.lower():
            found = True
            break
    assert found

    adv_list = user_collection.list(text="testcase")
    assert isinstance(adv_list, Generator)
    _list_asserts(adv_list)

    adv_list_no_match = user_collection.list(text="h78frg279fbg92ubue9b 80fh0hnvioh")
    assert isinstance(adv_list_no_match, Generator)
    assert next(adv_list_no_match, None) is None
    short_list = user_collection._list_generator(limit=3)
    _list_asserts(short_list, limit=10)


def test_user_get(user_collection: UserCollection, seeded_users: list[User]):
    first_hit = next(user_collection.list(text=seeded_users[1].name), None)
    user_from_get = user_collection.get_by_id(user_id=first_hit.id)
    assert user_from_get.id == first_hit.id
    assert isinstance(user_from_get, User)
