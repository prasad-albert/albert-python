from typing import Annotated, TypeVar

from pydantic import PlainSerializer

from albert.resources.base import BaseAlbertModel, BaseEntityLink


def convert_to_entity_link(value: BaseAlbertModel | BaseEntityLink) -> BaseEntityLink:
    if isinstance(value, BaseAlbertModel):
        return value.to_entity_link()
    return value


EntityType = TypeVar("EntityType", bound=BaseAlbertModel)

SerializeAsEntityLink = Annotated[
    EntityType | BaseEntityLink,
    PlainSerializer(convert_to_entity_link),
]
"""Type representing a union of `EntityType | BaseEntityLink` that is serialized as a link."""
