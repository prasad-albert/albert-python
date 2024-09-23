from collections.abc import Generator

from albert.albert import Albert
from albert.collections.inventory import InventoryCategory
from albert.resources.inventory import CasAmount, InventoryItem
from albert.resources.units import UnitCategory


def _list_asserts(returned_list):
    for i, u in enumerate(returned_list):
        if i == 50:
            break
        assert isinstance(u, InventoryItem)
        assert isinstance(u.name, str | None)
        assert isinstance(u.id, str)


def test_simple_inventory_list(client: Albert):
    inventory = client.inventory.list()
    assert isinstance(inventory, Generator)
    _list_asserts(inventory)


def test_advanced_inventory_list(client: Albert):
    inventory = client.inventory.list(
        name="goggles",
        category=[InventoryCategory.EQUIPMENT, InventoryCategory.CONSUMABLES],
    )
    assert isinstance(inventory, Generator)
    _list_asserts(inventory)
    for i, x in enumerate(inventory):
        if i == 10:  # just check the first 10 for speed
            break
        assert "goggles" in x.name.lower()


def test_get_by_id(client: Albert):
    first_inv = next(client.inventory.list())
    inv_id = first_inv.id if first_inv.id.startswith("INV") else "INV" + first_inv.id
    get_by_id = client.inventory.get_by_id(inventory_id=inv_id)
    assert isinstance(get_by_id, InventoryItem)
    assert first_inv.name == get_by_id.name
    assert inv_id == get_by_id.id


def test_inventory_crud(client: Albert):
    # TODO: Need to do some Updates in these tests
    all_amounts = []
    for c in client.cas_numbers.list():
        this_amt = CasAmount(cas=c, min=2, max=40)
        all_amounts.append(this_amt)
        if len(all_amounts) == 3:
            break
    new_inv = InventoryItem(
        name="SDK Testing Inventory Item",
        category=InventoryCategory.RAW_MATERIALS,
        tags=["testing"],
        company="Lenore Corp.",
        cas=all_amounts,
    )

    created = client.inventory.create(inventory_item=new_inv)
    this_id = created.id
    assert this_id is not None
    assert created.unit_category.lower() == UnitCategory.MASS.value.lower()
    d = "testing SDK CRUD"
    created.description = d

    updated = client.inventory.update(updated_object=created)
    assert updated.description == d

    deleted = client.inventory.delete(inventory_id=this_id)
    assert deleted
