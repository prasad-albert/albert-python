from typing import Annotated

from pydantic import BeforeValidator, validate_call


def with_albert_id_validation(cls):
    """Class decorator that adds validate_albert_id_types to all methods"""
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("__"):
            setattr(cls, attr_name, validate_call(attr_value))
    return cls


def _validate_coded_id(id: str | int, id_type: str) -> str:
    """Common validation for all ID types."""
    if not id:
        raise ValueError(f"{id_type} cannot be empty")
    if isinstance(id, int) or (isinstance(id, str) and id.isdigit()):
        raise ValueError(
            f"{id_type} requires a type code e.g. 'A' for raw materials as in 'A1425'"
        )
    if not isinstance(id, str):
        # Based on the type hint this should be impossible
        # but if someone ignores the hints we need to check this
        raise TypeError(f"{id_type} must be a string")
    return str(id)


def _validate_convertible_id(id: str | int, id_type: str) -> str:
    """Common validation for all ID types."""
    if not id:
        raise ValueError(f"{id_type} cannot be empty")
    if not isinstance(id, str | int):
        # Based on the type hint this should be impossible
        # but if someone ignores the hints we need to check this
        raise TypeError(f"{id_type} must be a string or integer")

    return str(id)


def ensure_block_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "BlockIdType")
    return id.upper() if id.upper().startswith("BLK") else f"BLK{id}"


BlockIdType = Annotated[str, BeforeValidator(ensure_block_id)]


def ensure_inventory_id(id: str | int) -> str:
    id = _validate_coded_id(id, "InventoryIdType")
    return id.upper() if id.upper().startswith("INV") else f"INV{id}"


InventoryIdType = Annotated[str, BeforeValidator(ensure_inventory_id)]


# NOTE: Search endpoints follow a different prefix requirement
# for certain fields. this one is for inventory IDs that are passed in
# as a filter.
def ensure_search_inventory_id(id: str | int) -> str:
    id = _validate_coded_id(id, "SearchInventoryIdType")
    if id.upper().startswith("INV"):
        id = id[3:]  # Remove INV prefix
    return id


SearchInventoryIdType = Annotated[str, BeforeValidator(ensure_search_inventory_id)]


def ensure_interval_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "IntervalIdType")
    return id.upper() if id.upper().startswith("INT") else f"INT{id}"


IntervalIdType = Annotated[str, BeforeValidator(ensure_interval_id)]


def ensure_parameter_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "ParameterIdType")
    return id.upper() if id.upper().startswith("PRM") else f"PRM{id}"


ParameterIdType = Annotated[str, BeforeValidator(ensure_parameter_id)]


def ensure_paramter_group_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "ParameterGroupIdType")
    return id.upper() if id.upper().startswith("PRG") else f"PRG{id}"


ParameterGroupIdType = Annotated[str, BeforeValidator(ensure_paramter_group_id)]


def ensure_datacolumn_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "DataColumnIdType")
    return id.upper() if id.upper().startswith("DAC") else f"DAC{id}"


DataColumnIdType = Annotated[str, BeforeValidator(ensure_datacolumn_id)]


def ensure_datatemplate_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "DataTemplateIdType")
    if id.upper().startswith("DAT"):
        return id.upper()
    elif id.upper().startswith("DT"):
        return f"DAT{id[2:]}"
    return f"DAT{id}"


DataTemplateIdType = Annotated[str, BeforeValidator(ensure_datatemplate_id)]


def ensure_propertydata_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "PropertyDataIdType")
    return id.upper() if id.upper().startswith("PTD") else f"PTD{id}"


PropertyDataIdType = Annotated[str, BeforeValidator(ensure_propertydata_id)]


def ensure_task_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "TaskIdType")
    return id.upper() if id.upper().startswith("TAS") else f"TAS{id}"


TaskIdType = Annotated[str, BeforeValidator(ensure_task_id)]


def ensure_project_id(id: str | int) -> str:
    id = _validate_coded_id(id, "ProjectIdType")
    return id.upper() if id.upper().startswith("PRO") else f"PRO{id}"


ProjectIdType = Annotated[str, BeforeValidator(ensure_project_id)]


def ensure_project_search_id(id: str | int) -> str:
    id = _validate_coded_id(id, "ProjectSearchIdType")
    if id.upper().startswith("PRO"):
        id = id[3:]  # Remove PRO prefix
    return id


SearchProjectIdType = Annotated[str, BeforeValidator(ensure_project_search_id)]


def ensure_lot_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "LotIdType")
    return id.upper() if id.upper().startswith("LOT") else f"LOT{id}"


LotIdType = Annotated[str, BeforeValidator(ensure_lot_id)]


def ensure_tag_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "TagIdType")
    return id.upper() if id.upper().startswith("TAG") else f"TAG{id}"


TagIdType = Annotated[str, BeforeValidator(ensure_tag_id)]


def ensure_user_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "UserIdType")
    return id.upper() if id.upper().startswith("USR") else f"USR{id}"


UserIdType = Annotated[str, BeforeValidator(ensure_user_id)]


def ensure_unit_id(id: str | int) -> str:
    id = _validate_convertible_id(id, "UnitIdType")
    return id.upper() if id.upper().startswith("UNI") else f"UNI{id}"


UnitIdType = Annotated[str, BeforeValidator(ensure_unit_id)]


AlbertIdType = (
    BlockIdType
    | DataColumnIdType
    | DataTemplateIdType
    | IntervalIdType
    | InventoryIdType
    | LotIdType
    | ParameterGroupIdType
    | ParameterIdType
    | ProjectIdType
    | PropertyDataIdType
    | SearchInventoryIdType
    | TagIdType
    | TaskIdType
    | UnitIdType
    | UserIdType
)
