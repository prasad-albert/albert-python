import pytest

from albert.resources.inventory import InventoryCategory, InventoryItem, InventoryMinimum
from albert.utils.exceptions import AlbertException


def test_inventory_minimum(seeded_locations):
    with pytest.raises(AlbertException):
        InventoryMinimum(
            minimum=0,
        )

    with pytest.raises(AlbertException):
        InventoryMinimum(
            minimum=0,
            location=seeded_locations[0],
            id=seeded_locations[0].id,
        )


def test_inventory_item_private_attributes(seeded_inventory: list[InventoryItem]):
    assert seeded_inventory[0].formula_id == None
    assert seeded_inventory[0].project_id == None


def test_formula_requirements():
    with pytest.raises(AttributeError):
        InventoryItem(
            name="Test",
            description="Test",
            category=InventoryCategory.FORMULAS,
        )
