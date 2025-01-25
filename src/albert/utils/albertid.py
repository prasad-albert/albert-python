from collections.abc import Iterable
from functools import wraps
from inspect import signature
from types import UnionType
from typing import Annotated, Union, get_args, get_origin, get_type_hints

from pydantic import BeforeValidator


def _validate_type(param_name: str, value: any, hint: type | None) -> tuple[bool, any]:
    if not hint:
        return True, value

    origin = get_origin(hint)

    if origin is None:
        # This handles both NoneType and simple types like str, int, etc.
        if hint is type(None) and value is None:
            return True, value
        if isinstance(value, hint):
            return True, value
        return False, None

    if origin in [
        Union,
        UnionType,
    ]:  # Handle both Union syntaxes -- the first one is the GenericAlias which works
        # for all complex unions formed with the | character
        # the latter one is required to handle unions between primiatives e.g. str | None
        # doesn't have an origin of Union, it has a hint of type types.UnionType
        # Check if the value is valid for any of the Union types
        valid_flags, values = zip(
            *[_validate_type(param_name, value, t) for t in get_args(hint)], strict=True
        )
        if sum(valid_flags) > 1:
            raise TypeError(
                f"value for parameter {param_name} matches multiple types in the union - only one AlbertIdType is allowed in a union"
            )
        if any(valid_flags):
            return True, values[valid_flags.index(True)]

        return False, None

    elif issubclass(origin, Iterable):
        if not issubclass(type(value), Iterable) or isinstance(value, str | bytes):
            # If we accept iterable types but we aren't an iterable
            # then fail validation as we need another type to pass
            return False, None

        # if we accept iterable types and we are an iterable type
        # but we are empty then pass
        if len(value) == 0:
            return True, value

        valid_flags, values = zip(
            *[_validate_type(param_name, v, get_args(hint)[0]) for v in value], strict=True
        )
        if not all(valid_flags):
            raise TypeError(
                f"one or more elements of the iterable in {param_name} does not match the expected IdType"
            )
        # The zip above casts the values iterable into a tuple
        # we convert it back to the original type passed in
        return True, type(value)(values)
    elif origin is Annotated:
        if not hint in get_args(AlbertIdType):
            # skip any annoated types that aren't albertIds
            return True, value

        if value is None or (
            issubclass(type(value), Iterable) and not isinstance(value, str | bytes)
        ):
            return False, None
        # This is an AlbertIdType and we need to parse
        # and verify it is in an expected form for the
        # platform
        id_validator = None
        for arg in get_args(hint):
            if isinstance(arg, BeforeValidator):
                id_validator = arg.func

        if id_validator is None:
            raise TypeError(f"type {hint} is missing the required BeforeValidator annotation")
        # Now we format/validate the value
        return True, id_validator(value)
    else:
        # Skip any types that are not Annotated
        return True, value


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
            is_albert_id_type = [arg in get_args(AlbertIdType) for arg in get_args(hint)]

            # Do a quick check to see if there are mulitple AlbertIdType hints in the union
            if get_origin(hint) in [Union, UnionType] and sum(is_albert_id_type) > 1:
                raise TypeError(
                    f"hints for parameter {param_name} match multiple AlbertIdTypes in the union - only one AlbertIdType is allowed in a given union"
                )

            # If the value is None, check if the type hint allows None
            if value is None:
                has_albert_types = any(is_albert_id_type)
                # Check if hint is a Union type that includes None
                if get_origin(hint) in [Union, UnionType]:
                    args = get_args(hint)
                    # If no AlbertIdTypes in union, or if there are and None is allowed, accept None
                    if (has_albert_types and type(None) in args) or not has_albert_types:
                        validated_args[param_name] = None
                        continue
                # Not a Union with None, so this is invalid
                raise TypeError(f"{param_name} is not an optional parameter")

            is_valid, value = _validate_type(param_name, value, hint)
            if is_valid:
                validated_args[param_name] = value
            else:
                raise ValueError(f"parameter {param_name} of type {hint} failed validations")

        return func(**validated_args)

    return wrapper


def with_albert_id_validation(cls):
    """Class decorator that adds validate_albert_id_types to all methods"""
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("__"):
            setattr(cls, attr_name, validate_albert_id_types(attr_value))
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
