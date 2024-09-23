from typing import Any

from albert.resources.base import BaseEntityLink, EntityLinkConvertible


def serialize_to_entity_link(value: Any) -> BaseEntityLink | Any:
    if isinstance(value, EntityLinkConvertible):
        return value.to_entity_link()
    return value


def serialize_to_entity_link_list(value: Any) -> list[BaseEntityLink] | Any:
    if isinstance(value, list):
        return [x.to_entity_link() if isinstance(x, EntityLinkConvertible) else x for x in value]
    return value
