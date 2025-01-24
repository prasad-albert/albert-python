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
    ensure_parameter_id,
    ensure_paramter_group_id,
    ensure_project_id,
    ensure_project_search_id,
    ensure_propertydata_id,
    ensure_search_inventory_id,
    ensure_tag_id,
    ensure_task_id,
    ensure_unit_id,
    validate_albert_id_types,
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


def test_validate_albert_id_types_with_empty_iterables():
    @validate_albert_id_types
    def list_func(inventory_ids: list[InventoryIdType]):
        return inventory_ids

    result = list_func([])
    assert result == []


def test_validate_albert_id_types_with_list_input():
    @validate_albert_id_types
    def list_func(inventory_ids: list[InventoryIdType]):
        return inventory_ids

    result = list_func([123, 456])
    assert result == ["INV123", "INV456"]


def test_validate_albert_id_types_with_union_list_and_type():
    @validate_albert_id_types
    def union_list_func(inventory_ids: list[InventoryIdType] | InventoryIdType | None):
        return inventory_ids

    result = union_list_func([123, 456])
    assert result == ["INV123", "INV456"]

    result = union_list_func(123)
    assert result == "INV123"

    result = union_list_func(None)
    assert result is None


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


def test_validate_on_primitive_unions():
    @validate_albert_id_types
    def test_func(param: str | None):
        return param

    assert test_func("abc") == "abc"

    assert test_func(None) == None


def test_validate_albert_id_types_with_multiple_types():
    @validate_albert_id_types
    def union_func(
        other_valid_id: TagIdType | None,
        inventory_id: InventoryIdType | UserIdType | None,
    ):
        return inventory_id

    # Should raise an error if multiple AlbertIdTypes are provided
    with pytest.raises(TypeError, match="matches multiple types in the union"):
        union_func(inventory_id="123", other_valid_id="456")

    with pytest.raises(TypeError, match="matches multiple types in the union"):
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

    # Should handle None
    with pytest.raises(TypeError, match="is not an optional parameter"):
        error_func(inventory_id=None)
