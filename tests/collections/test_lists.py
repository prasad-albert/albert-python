from albert import Albert
from albert.resources.lists import ListItem, ListItemCategory


def _list_asserts(list_items: list[ListItem]):
    found = False
    for l in list_items:
        assert isinstance(l, ListItem)
        assert isinstance(l.name, str)
        assert isinstance(l.id, str)
        found = True
    assert found


def test_basic_list(client: Albert, seeded_lists: list[ListItem]):
    list_items = client.lists.list()
    _list_asserts(list_items)
