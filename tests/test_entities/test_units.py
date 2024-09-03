from albert.entity.units import Unit, UnitCollection, UnitCategory
from albert.albert import Albert
from albert.base_collection import OrderBy
import pytest
from typing import Generator


@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    for i, u in enumerate(returned_list):
        if i == 100:
            break
        assert isinstance(u, Unit)
        assert isinstance(u.name, str)
        assert isinstance(u.id, str)
        assert u.id.startswith("UNI")


def test_simple_units_list(client):
    simple_list = client.units.list()
    assert isinstance(simple_list, Generator)
    _list_asserts(simple_list)


def test_advanced_units_list(client):
    adv_list = client.units.list(
        name="gram",
        category=UnitCategory.MASS,
        order_by=OrderBy.ASCENDING,
        exact_match=True,
        verified=True,
    )
    assert isinstance(adv_list, Generator)
    for u in adv_list:
        assert "gram" in u.name.lower()
    _list_asserts(adv_list)


def test_get_unit_by(client):
    unit = client.units.get_by_name("gram")
    assert isinstance(unit, Unit)

    by_id = client.units.get_by_id(unit.id)
    assert isinstance(by_id, Unit)
    assert by_id.name.lower() == "gram"


def test_unit_exists(client):
    assert client.units.unit_exists("gram")
    assert not client.units.unit_exists(
        "totally nonesense unit no one should be using!662378393278932y5r"
    )


def test_unit_crud(client):
    new_unit = Unit(
        name="SDK Test Unit",
        symbol="x",
        synonums=["kfnehiuow", "hbfuiewhbuewf89fy89b"],
        category=UnitCategory.MASS,
    )
    created_unit = client.units.create(new_unit)
    assert isinstance(created_unit, Unit)
    assert created_unit.name == "SDK Test Unit"
    assert created_unit.id is not None

    created_unit.symbol = "y"
    updated_unit = client.units.update(updated_unit=created_unit)
    assert isinstance(updated_unit, Unit)
    assert updated_unit.id == created_unit.id
    assert updated_unit.symbol == "y"

    deleted = client.units.delete(updated_unit.id)
    assert deleted
    assert not client.units.unit_exists(name=updated_unit.name)
