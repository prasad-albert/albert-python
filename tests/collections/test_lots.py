from collections.abc import Generator

from albert.albert import Albert
from albert.resources.lots import Lot


def _list_asserts(returned_list):
    found = False
    for i, c in enumerate(returned_list):
        if i == 100:
            break
        found = True
        assert isinstance(c, Lot)
        assert isinstance(c.id, str)
        assert c.id.startswith("LOT")
    assert found


def test_simple_lot_list(
    client: Albert,
    # seeded_lots #PUT on lots currently broken, so we can't seed lots
):
    simple_list = client.lots.list()
    assert isinstance(simple_list, Generator)
    _list_asserts(simple_list)
