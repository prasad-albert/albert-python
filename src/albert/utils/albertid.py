from functools import wraps
from inspect import signature
from typing import Annotated, Union, get_args, get_origin, get_type_hints

from pydantic import BeforeValidator


def validate_albert_id_types(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get type hints and signature
        hints = get_type_hints(func, include_extras=True)
        sig = signature(func)
        bound_args = sig.bind(*args, **kwargs)

        validated_args = {}

        # Process each argument
        for param_name, value in bound_args.arguments.items():
            hint = hints.get(param_name)

            # Skip if no type hint
            if not hint:
                validated_args[param_name] = value
                continue

            # Handle Union types first
            base_type = hint
            allows_none = False
            if get_origin(hint) is Union:
                type_args = get_args(hint)
                allows_none = type(None) in type_args
                # Find all AlbertIdTypes in the Union
                albert_types = [
                    t
                    for t in type_args
                    if get_origin(t) is Annotated and t in get_args(AlbertIdType)
                ]
                if len(albert_types) > 1:
                    raise TypeError(
                        f"Parameter '{param_name}' cannot accept multiple AlbertIdTypes"
                    )
                elif albert_types:
                    base_type = albert_types[0]

            # Skip if not an Annotated type
            if get_origin(base_type) is not Annotated:
                validated_args[param_name] = value
                continue

            # Skip if not an AlbertIdType
            if base_type not in get_args(AlbertIdType):
                validated_args[param_name] = value
                continue

            # Handle None for optional parameters
            if value is None:
                if allows_none:
                    validated_args[param_name] = None
                    continue
                raise TypeError(f"{param_name} is not an optional parameter")

            # Get validators from the Annotated type
            type_args = get_args(base_type)
            validators = []
            for arg in type_args[1:]:
                if isinstance(arg, BeforeValidator):
                    validators.append(arg.func)
                elif callable(arg):
                    validators.append(arg)

            # Apply validators
            validated_value = str(value)
            for validator in validators:
                validated_value = validator(validated_value)
            validated_args[param_name] = validated_value

        return func(**validated_args)

    return wrapper


def add_albert_id_valiators(cls):
    """Class decorator that adds validate_albert_id_types to all methods"""
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("__"):
            setattr(cls, attr_name, validate_albert_id_types(attr_value))
    return cls


def _validate_convertible_id(id: str | int, id_type: str) -> None:
    """Common validation for all ID types."""
    if not id:
        raise ValueError(f"{id_type} ID cannot be empty")
    if not isinstance(id, str | int):
        # Based on the type hint this should be impossible
        # but if someone ignores the hints we need to check this
        raise TypeError(f"{id_type} ID must be a string or integer")


def ensure_block_id(id: str) -> str:
    _validate_convertible_id(id, "Block")
    return id.upper() if id.upper().startswith("BLK") else f"BLK{id}"


BlockIdType = Annotated[str, BeforeValidator(ensure_block_id)]


def ensure_inventory_id(id: str) -> str:
    _validate_convertible_id(id, "Inventory")
    return id.upper() if id.upper().startswith("INV") else f"INV{id}"


InventoryIdType = Annotated[str, BeforeValidator(ensure_inventory_id)]


# NOTE: Search endpoints follow a different prefix requirement
# for certain fields. this one is for inventory IDs that are passed in
# as a filter.
def ensure_search_inventory_id(id: str) -> str:
    _validate_convertible_id(id, "Search inventory")
    if id.upper().startswith("INV"):
        id = id[3:]  # Remove INV prefix
    return id


SearchInventoryIdType = Annotated[str, BeforeValidator(ensure_search_inventory_id)]


def ensure_interval_id(id: str) -> str:
    _validate_convertible_id(id, "Interval")
    return id.upper() if id.upper().startswith("INT") else f"INT{id}"


IntervalIdType = Annotated[str, BeforeValidator(ensure_interval_id)]


def ensure_tag_id(id: str) -> str:
    _validate_convertible_id(id, "Tag")
    return id.upper() if id.upper().startswith("TAG") else f"TAG{id}"


TagIdType = Annotated[str, BeforeValidator(ensure_tag_id)]


def ensure_datacolumn_id(id: str) -> str:
    _validate_convertible_id(id, "Data column")
    return id.upper() if id.upper().startswith("DAC") else f"DAC{id}"


DataColumnIdType = Annotated[str, BeforeValidator(ensure_datacolumn_id)]


def ensure_datatemplate_id(id: str) -> str:
    _validate_convertible_id(id, "Data template")
    return id.upper() if id.upper().startswith("DAT") else f"DAT{id}"


DataTemplateIdType = Annotated[str, BeforeValidator(ensure_datatemplate_id)]


def ensure_propertydata_id(id: str) -> str:
    _validate_convertible_id(id, "Property data")
    return id.upper() if id.upper().startswith("PTD") else f"PTD{id}"


PropertyDataIdType = Annotated[str, BeforeValidator(ensure_propertydata_id)]


def ensure_task_id(id: str) -> str:
    _validate_convertible_id(id, "Task")
    return id.upper() if id.upper().startswith("TAS") else f"TAS{id}"


TaskIdType = Annotated[str, BeforeValidator(ensure_task_id)]


def ensure_project_id(id: str) -> str:
    _validate_convertible_id(id, "Project")
    return id.upper() if id.upper().startswith("PRO") else f"PRO{id}"


ProjectIdType = Annotated[str, BeforeValidator(ensure_project_id)]


def ensure_lot_id(id: str) -> str:
    _validate_convertible_id(id, "Lot")
    return id.upper() if id.upper().startswith("LOT") else f"LOT{id}"


LotIdType = Annotated[str, BeforeValidator(ensure_lot_id)]


def ensure_user_id(id: str) -> str:
    _validate_convertible_id(id, "User")
    return id.upper() if id.upper().startswith("USR") else f"USR{id}"


UserIdType = Annotated[str, BeforeValidator(ensure_user_id)]


AlbertIdType = (
    UserIdType
    | BlockIdType
    | InventoryIdType
    | IntervalIdType
    | TagIdType
    | DataColumnIdType
    | DataTemplateIdType
    | PropertyDataIdType
    | TaskIdType
    | ProjectIdType
    | LotIdType
)
