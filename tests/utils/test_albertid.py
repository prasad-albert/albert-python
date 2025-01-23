import pytest

from albert.utils.albertid import (
    InventoryIdType,
    TagIdType,
    UserIdType,
    ensure_block_id,
    ensure_datacolumn_id,
    ensure_datatemplate_id,
    ensure_interval_id,
    ensure_inventory_id,
    ensure_lot_id,
    ensure_project_id,
    ensure_propertydata_id,
    ensure_search_inventory_id,
    ensure_tag_id,
    ensure_task_id,
    validate_albert_id_types,
)


def test_ensure_inventory_id():
    # Test with and without prefix
    assert ensure_inventory_id("123") == "INV123"
    assert ensure_inventory_id("INV123") == "INV123"
    assert ensure_inventory_id("inv123") == "INV123"

    with pytest.raises(ValueError, match="Inventory ID cannot be empty"):
        ensure_inventory_id("")


def test_ensure_tag_id():
    assert ensure_tag_id("123") == "TAG123"
    assert ensure_tag_id("TAG123") == "TAG123"
    assert ensure_tag_id("tag123") == "TAG123"

    with pytest.raises(ValueError, match="Tag ID cannot be empty"):
        ensure_tag_id("")


def test_ensure_datacolumn_id():
    assert ensure_datacolumn_id("123") == "DAC123"
    assert ensure_datacolumn_id("DAC123") == "DAC123"
    assert ensure_datacolumn_id("dac123") == "DAC123"

    with pytest.raises(ValueError, match="Data column ID cannot be empty"):
        ensure_datacolumn_id("")


def test_ensure_datatemplate_id():
    assert ensure_datatemplate_id("123") == "DAT123"
    assert ensure_datatemplate_id("DAT123") == "DAT123"
    assert ensure_datatemplate_id("dat123") == "DAT123"

    with pytest.raises(ValueError, match="Data template ID cannot be empty"):
        ensure_datatemplate_id("")


def test_ensure_propertydata_id():
    assert ensure_propertydata_id("123") == "PTD123"
    assert ensure_propertydata_id("PTD123") == "PTD123"
    assert ensure_propertydata_id("ptd123") == "PTD123"

    with pytest.raises(ValueError, match="Property data ID cannot be empty"):
        ensure_propertydata_id("")


# Test functions with and without decorator
def test_validate_albert_id_types_decorator():
    # Function with decorator
    @validate_albert_id_types
    def decorated_func(inventory_id: InventoryIdType, tag_id: TagIdType):
        return inventory_id, tag_id

    # Function without decorator
    def undecorated_func(inventory_id: InventoryIdType, tag_id: TagIdType):
        return inventory_id, tag_id

    # Test decorated function
    inv_id, tag_id = decorated_func(inventory_id="123", tag_id="456")
    assert inv_id == "INV123"
    assert tag_id == "TAG456"

    # Test undecorated function - should not validate/transform
    inv_id, tag_id = undecorated_func(inventory_id="123", tag_id="456")
    assert inv_id == "123"
    assert tag_id == "456"


def test_validate_albert_id_types_with_mixed_params():
    @validate_albert_id_types
    def mixed_func(inventory_id: InventoryIdType, name: str, tag_id: TagIdType):
        return inventory_id, name, tag_id

    result = mixed_func(inventory_id="123", name="test", tag_id="456")
    assert result == ("INV123", "test", "TAG456")


def test_validate_albert_id_types_with_int_input():
    @validate_albert_id_types
    def int_func(inventory_id: InventoryIdType):
        return inventory_id

    # Should handle integer input by converting to string first
    assert int_func(inventory_id=123) == "INV123"


def test_validate_albert_id_types_with_optional_parameter():
    @validate_albert_id_types
    def optional_func(name: str, tag_id: TagIdType | None = None):
        return name, tag_id

    # Should work with None value for optional parameter
    assert optional_func("test") == ("test", None)
    assert optional_func("test", "123") == ("test", "TAG123")


def test_validate_albert_id_types_with_union_type():
    @validate_albert_id_types
    def union_func(inventory_id: InventoryIdType | None):
        return inventory_id

    assert union_func(None) == None
    assert union_func("123") == "INV123"


def test_validate_albert_id_types_with_multiple_types():
    @validate_albert_id_types
    def union_func(
        other_valid_id: TagIdType | None,
        inventory_id: InventoryIdType | UserIdType | None,
    ):
        return inventory_id

    # Should raise an error if multiple AlbertIdTypes are provided
    with pytest.raises(
        TypeError, match="Parameter 'inventory_id' cannot accept multiple AlbertIdTypes"
    ):
        union_func(inventory_id="123", other_valid_id="456")

    with pytest.raises(
        TypeError, match="Parameter 'inventory_id' cannot accept multiple AlbertIdTypes"
    ):
        union_func(inventory_id=None, other_valid_id="456")

    # Show that single type with optional None is still valid
    @validate_albert_id_types
    def valid_func(tag_id: TagIdType | None):
        return tag_id

    assert valid_func(None) is None
    assert valid_func("TAG123") == "TAG123"
    assert valid_func("123") == "TAG123"


def test_validate_albert_id_types_error_cases():
    @validate_albert_id_types
    def error_func(inventory_id: InventoryIdType):
        return inventory_id

    # Should handle empty string
    with pytest.raises(ValueError, match="Inventory ID cannot be empty"):
        error_func(inventory_id="")

    # Should handle None
    with pytest.raises(TypeError, match="is not an optional parameter"):
        error_func(inventory_id=None)


def test_ensure_block_id():
    assert ensure_block_id("123") == "BLK123"
    assert ensure_block_id("BLK123") == "BLK123"
    assert ensure_block_id("blk123") == "BLK123"

    with pytest.raises(ValueError, match="Block ID cannot be empty"):
        ensure_block_id("")


def test_ensure_interval_id():
    assert ensure_interval_id("123") == "INT123"
    assert ensure_interval_id("INT123") == "INT123"
    assert ensure_interval_id("int123") == "INT123"

    with pytest.raises(ValueError, match="Interval ID cannot be empty"):
        ensure_interval_id("")


def test_ensure_task_id():
    assert ensure_task_id("123") == "TAS123"
    assert ensure_task_id("TAS123") == "TAS123"
    assert ensure_task_id("tas123") == "TAS123"

    with pytest.raises(ValueError, match="Task ID cannot be empty"):
        ensure_task_id("")


def test_ensure_project_id():
    assert ensure_project_id("123") == "PRO123"
    assert ensure_project_id("PRO123") == "PRO123"
    assert ensure_project_id("pro123") == "PRO123"

    with pytest.raises(ValueError, match="Project ID cannot be empty"):
        ensure_project_id("")


def test_ensure_lot_id():
    assert ensure_lot_id("123") == "LOT123"
    assert ensure_lot_id("LOT123") == "LOT123"
    assert ensure_lot_id("lot123") == "LOT123"

    with pytest.raises(ValueError, match="Lot ID cannot be empty"):
        ensure_lot_id("")


def test_ensure_search_inventory_id():
    assert ensure_search_inventory_id("N123") == "N123"
    assert ensure_search_inventory_id("INVP123") == "P123"
    assert ensure_search_inventory_id("invZ123") == "Z123"

    with pytest.raises(ValueError, match="Search inventory ID cannot be empty"):
        ensure_search_inventory_id("")
