import pytest
from pydantic import validate_call

from albert.utils.albertid import (
    InventoryIdType,
    LotIdType,
    TagIdType,
    UserIdType,
    ensure_block_id,
    ensure_datacolumn_id,
    ensure_datatemplate_id,
    ensure_interval_id,
    ensure_inventory_id,
    ensure_lot_id,
    ensure_parameter_id,
    ensure_paramter_group_id,
    ensure_project_id,
    ensure_project_search_id,
    ensure_propertydata_id,
    ensure_search_inventory_id,
    ensure_tag_id,
    ensure_task_id,
    ensure_unit_id,
    validate_call,
)


@pytest.mark.parametrize(
    "ensure_func,prefix,optional_code,error_msg",
    [
        (ensure_inventory_id, "INV", "A", "InventoryIdType cannot be empty"),
        (ensure_tag_id, "TAG", "", "TagIdType cannot be empty"),
        (ensure_datacolumn_id, "DAC", "", "DataColumnIdType cannot be empty"),
        (ensure_datatemplate_id, "DAT", "", "DataTemplateIdType cannot be empty"),
        (ensure_propertydata_id, "PTD", "", "PropertyDataIdType cannot be empty"),
        (ensure_block_id, "BLK", "", "BlockIdType cannot be empty"),
        (ensure_interval_id, "INT", "", "IntervalIdType cannot be empty"),
        (ensure_task_id, "TAS", "", "TaskIdType cannot be empty"),
        (ensure_project_id, "PRO", "P", "ProjectIdType cannot be empty"),
        (ensure_lot_id, "LOT", "", "LotIdType cannot be empty"),
        (ensure_parameter_id, "PRM", "", "ParameterIdType cannot be empty"),
        (ensure_paramter_group_id, "PRG", "", "ParameterGroupIdType cannot be empty"),
        (ensure_unit_id, "UNI", "", "UnitIdType cannot be empty"),
    ],
)
def test_ensure_id_functions(ensure_func, prefix, optional_code, error_msg):
    # Test with Simple ID
    assert ensure_func(f"{optional_code}123") == f"{prefix}{optional_code}123"

    # Test with prefixed ID (uppercase)
    assert ensure_func(f"{prefix}{optional_code}123") == f"{prefix}{optional_code}123"

    # Test with prefixed ID (lowercase)
    assert ensure_func(f"{prefix.lower()}{optional_code}123") == f"{prefix}{optional_code}123"

    # Test empty strings
    with pytest.raises(ValueError, match=error_msg):
        ensure_func("")
    with pytest.raises(ValueError, match=error_msg):
        ensure_func(None)

    # If there is no additional id Code, then numerical ids should be converted to a string
    if not optional_code:
        assert ensure_func(123) == f"{prefix}123"


@pytest.mark.parametrize(
    "ensure_func,prefix,optional_code,error_msg",
    [
        (ensure_search_inventory_id, "INV", "N", "SearchInventoryIdType cannot be empty"),
        (ensure_project_search_id, "PRO", "P", "ProjectSearchIdType cannot be empty"),
    ],
)
def test_ensure_search_inventory_id(ensure_func, prefix, optional_code, error_msg):
    # Test with Simple ID
    assert ensure_func(f"{optional_code}123") == f"{optional_code}123"

    # Test with prefixed ID (uppercase)
    assert ensure_func(f"{prefix}{optional_code}123") == f"{optional_code}123"

    # Test with prefixed ID (lowercase)
    assert ensure_func(f"{prefix.lower()}{optional_code}123") == f"{optional_code}123"

    # Test empty string
    with pytest.raises(ValueError, match=error_msg):
        ensure_func("")

    if not optional_code:
        assert ensure_func(123) == "123"


# Test functions with and without decorator
def test_validate_call_decorator():
    # Function with decorator
    @validate_call
    def decorated_func(inventory_id: InventoryIdType, tag_id: TagIdType):
        return inventory_id, tag_id

    # Function without decorator
    def undecorated_func(inventory_id: InventoryIdType, tag_id: TagIdType):
        return inventory_id, tag_id

    # Test decorated function
    inv_id, tag_id = decorated_func(inventory_id="A123", tag_id="456")
    assert inv_id == "INVA123"
    assert tag_id == "TAG456"

    # Test undecorated function - should not validate/transform
    inv_id, tag_id = undecorated_func(inventory_id="A123", tag_id="456")
    assert inv_id == "A123"
    assert tag_id == "456"


def test_validate_call_with_mixed_params():
    @validate_call
    def mixed_func(inventory_id: InventoryIdType, name: str, tag_id: TagIdType):
        return inventory_id, name, tag_id

    result = mixed_func(inventory_id="A123", name="test", tag_id="456")
    assert result == ("INVA123", "test", "TAG456")


def test_validate_call_with_empty_iterables():
    @validate_call
    def list_func(inventory_ids: list[InventoryIdType]):
        return inventory_ids

    result = list_func([])
    assert result == []


def test_validate_call_with_list_input():
    @validate_call
    def list_func(inventory_ids: list[InventoryIdType]):
        return inventory_ids

    result = list_func(["A123", "A456"])
    assert result == ["INVA123", "INVA456"]

    with pytest.raises(
        ValueError,
        match="InventoryIdType requires a type code e.g. 'A' for raw materials as in 'A1425'",
    ):
        list_func([123, 456])


def test_validate_call_with_union_list_and_type():
    @validate_call
    def union_list_func(inventory_ids: list[InventoryIdType] | InventoryIdType | None):
        return inventory_ids

    result = union_list_func(["A123", "A456"])
    assert result == ["INVA123", "INVA456"]

    result = union_list_func("A123")
    assert result == "INVA123"

    result = union_list_func(None)
    assert result is None


def test_validate_call_with_optional_parameter():
    @validate_call
    def optional_func(name: str, tag_id: TagIdType | None = None):
        return name, tag_id

    # Should work with None value for optional parameter
    assert optional_func("test") == ("test", None)
    assert optional_func("test", "123") == ("test", "TAG123")


def test_validate_call_with_optional_type():
    @validate_call
    def optional_func(inventory_id: InventoryIdType | None):
        return inventory_id

    assert optional_func(None) == None
    assert optional_func("A123") == "INVA123"


@pytest.mark.xfail(
    reason="This would require custom reflection code to check the annotations for multiple instances of an albertidtype prior to passing them into pydantic"
)
def test_validate_call_with_multiple_types():
    # TODO: Think about if there is a way to do this using
    # just pydantic...
    @validate_call
    def union_func(
        other_valid_id: TagIdType | None,
        inventory_id: InventoryIdType | UserIdType | None,
    ):
        return inventory_id

    # Should raise an error if multiple AlbertIdTypes are provided
    with pytest.raises(TypeError, match="match multiple AlbertIdTypes in the union"):
        union_func(inventory_id="A123", other_valid_id="456")

    with pytest.raises(TypeError, match="match multiple AlbertIdTypes in the union"):
        union_func(inventory_id=None, other_valid_id="456")

    # Show that single type with optional None is still valid
    @validate_call
    def valid_func(tag_id: TagIdType | None):
        return tag_id

    assert valid_func(None) is None
    assert valid_func("TAG123") == "TAG123"
    assert valid_func("123") == "TAG123"


def test_validate_call_required_id():
    @validate_call
    def error_func(inventory_id: InventoryIdType):
        return inventory_id

    # Should handle None
    with pytest.raises(ValueError, match="cannot be empty"):
        error_func(inventory_id=None)


def test_validate_call_with_return_types():
    @validate_call
    def return_func(inventory_id: InventoryIdType) -> InventoryIdType:
        return inventory_id

    assert return_func("A123") == "INVA123"
