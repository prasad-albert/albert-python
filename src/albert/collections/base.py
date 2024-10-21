from enum import Enum

from albert.resources.base import BaseResource
from albert.session import AlbertSession


class OrderBy(str, Enum):
    DESCENDING = "desc"
    ASCENDING = "asc"


class BaseCollection:
    """
    BaseCollection is the base class for all collection classes.

    Parameters
    ----------
    session : AlbertSession
        The Albert API Session instance.

    """

    def __init__(self, *, session: AlbertSession):
        self.session = session

    # Class property specifying updatable attributes
    _updatable_attributes = {}

    def _generate_patch_payload(self, *, existing: BaseResource, updated: BaseResource) -> dict:
        """Generates a payload for PATCH requests based on the changes. This is overriden for some clases with more compex patch formation"""
        payload = {"data": []}
        for attribute in self._updatable_attributes:
            old_value = getattr(existing, attribute, None)
            new_value = getattr(updated, attribute, None)

            # Get the serialization alias name for the attribute, if it exists
            alias = existing.model_fields[attribute].alias or attribute

            if old_value is None and new_value is not None:
                # Add new attribute
                payload["data"].append(
                    {"operation": "add", "attribute": alias, "newValue": str(new_value)}
                )
            elif old_value is not None and new_value != old_value:
                # Update existing attribute
                payload["data"].append(
                    {
                        "operation": "update",
                        "attribute": alias,
                        "oldValue": str(old_value),
                        "newValue": str(new_value),
                    }
                )

        return payload
