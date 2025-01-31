from typing import Annotated

from pydantic import AfterValidator, validate_call

_ALBERT_PREFIXES = {
    "BLK",
    "DAC",
    "DAT",
    "INT",
    "INV",
    "LOT",
    "PRG",
    "PRM",
    "PRO",
    "PTD",
    "TAG",
    "TAS",
    "UNI",
    "USR",
}


def with_type_validation(cls):
    """Class decorator that adds validate_call to methods specified in _type_validated_methods"""
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and attr_name in cls._type_validated_methods:
            setattr(cls, attr_name, validate_call(attr_value))
    return cls


def _validate_coded_id(id: str, id_type: str) -> str:
    """Common validation for all ID types."""
    if not id:
        raise ValueError(f"{id_type} cannot be empty")
    if id.isdigit():
        raise ValueError(
            f"{id_type} requires a type code e.g. 'A' for raw materials as in 'A1425'"
        )
    if not isinstance(id, str):
        # Based on the type hint this should be impossible
        # but if someone ignores the hints we need to check this
        raise TypeError(f"{id_type} must be a string")
    return str(id)


def _is_valid_albert_prefix(id: str) -> bool:
    """Check if the id starts with a valid Albert prefix."""
    return any(id.upper().startswith(prefix) for prefix in _ALBERT_PREFIXES)


def _ensure_albert_id(id: str, prefix: str, id_type: str) -> str:
    """Generic function to ensure Albert IDs follow the correct pattern.

    Args:
        id: The ID to validate and format
        prefix: The expected prefix (e.g. 'INV', 'PRO')
        id_type: The type name for more helpful error messages
    """
    if not id:
        raise ValueError(f"{id_type} cannot be empty")

    # Check if already has correct prefix
    if id.upper().startswith(prefix):
        return id.upper()

    # Check if has different Albert prefix
    if _is_valid_albert_prefix(id):
        raise ValueError(f"{id_type} {id} has invalid prefix. Expected: {prefix}")

    return f"{prefix}{id.upper()}"


def ensure_block_id(id: str) -> str:
    return _ensure_albert_id(id, "BLK", "BlockIdType")


BlockId = Annotated[str, AfterValidator(ensure_block_id)]


def ensure_inventory_id(id: str) -> str:
    id = _validate_coded_id(id, "InventoryIdType")
    return _ensure_albert_id(id, "INV", "InventoryIdType")


InventoryId = Annotated[str, AfterValidator(ensure_inventory_id)]


# NOTE: Search endpoints follow a different prefix requirement
# for certain fields. this one is for inventory IDs that are passed in
# as a filter.
def ensure_search_inventory_id(id: str) -> str:
    id = _validate_coded_id(id, "SearchInventoryIdType")
    if id.upper().startswith("INV"):
        id = id[3:]  # Remove INV prefix
    return id


SearchInventoryId = Annotated[str, AfterValidator(ensure_search_inventory_id)]


def ensure_interval_id(id: str) -> str:
    return _ensure_albert_id(id, "INT", "IntervalIdType")


IntervalId = Annotated[str, AfterValidator(ensure_interval_id)]


def ensure_parameter_id(id: str) -> str:
    return _ensure_albert_id(id, "PRM", "ParameterIdType")


ParameterId = Annotated[str, AfterValidator(ensure_parameter_id)]


def ensure_paramter_group_id(id: str) -> str:
    return _ensure_albert_id(id, "PRG", "ParameterGroupIdType")


ParameterGroupId = Annotated[str, AfterValidator(ensure_paramter_group_id)]


def ensure_datacolumn_id(id: str) -> str:
    return _ensure_albert_id(id, "DAC", "DataColumnIdType")


DataColumnId = Annotated[str, AfterValidator(ensure_datacolumn_id)]


def ensure_datatemplate_id(id: str) -> str:
    if id and id.upper().startswith("DT"):
        id = f"DAT{id[2:]}"  # Replace DT with DAT
    return _ensure_albert_id(id, "DAT", "DataTemplateIdType")


DataTemplateId = Annotated[str, AfterValidator(ensure_datatemplate_id)]


def ensure_propertydata_id(id: str) -> str:
    return _ensure_albert_id(id, "PTD", "PropertyDataIdType")


PropertyDataId = Annotated[str, AfterValidator(ensure_propertydata_id)]


def ensure_task_id(id: str) -> str:
    return _ensure_albert_id(id, "TAS", "TaskIdType")


TaskId = Annotated[str, AfterValidator(ensure_task_id)]


def ensure_project_id(id: str) -> str:
    return _ensure_albert_id(id, "PRO", "ProjectIdType")


ProjectId = Annotated[str, AfterValidator(ensure_project_id)]


def ensure_project_search_id(id: str) -> str:
    id = _validate_coded_id(id, "ProjectSearchIdType")
    if id.upper().startswith("PRO"):
        id = id[3:]  # Remove PRO prefix
    return id


SearchProjectId = Annotated[str, AfterValidator(ensure_project_search_id)]


def ensure_lot_id(id: str) -> str:
    return _ensure_albert_id(id, "LOT", "LotIdType")


LotId = Annotated[str, AfterValidator(ensure_lot_id)]


def ensure_tag_id(id: str) -> str:
    return _ensure_albert_id(id, "TAG", "TagIdType")


TagId = Annotated[str, AfterValidator(ensure_tag_id)]


def ensure_user_id(id: str) -> str:
    return _ensure_albert_id(id, "USR", "UserIdType")


UserIdType = Annotated[str, AfterValidator(ensure_user_id)]


def ensure_unit_id(id: str) -> str:
    return _ensure_albert_id(id, "UNI", "UnitIdType")


UnitId = Annotated[str, AfterValidator(ensure_unit_id)]


def ensure_workflow_id(id: str) -> str:
    return _ensure_albert_id(id, "WFL", "WorkflowIdType")


WorkflowId = Annotated[str, AfterValidator(ensure_workflow_id)]
