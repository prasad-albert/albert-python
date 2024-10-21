from enum import Enum

from albert.resources.base import BaseResource
from albert.resources.serialization import BaseEntityLink
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

    def _generate_metadata_diff(
        self,
        existing_metadata: dict[str, str | list[BaseEntityLink] | BaseEntityLink],
        updated_metadata: dict[str, str | list[BaseEntityLink] | BaseEntityLink],
    ):
        payload = []
        for key, value in existing_metadata.items():
            if key not in updated_metadata:
                if isinstance(value, str):
                    payload.append(
                        {
                            "attribute": f"Metadata.{key}",
                            "operation": "delete",
                            "oldValue": value,
                        }
                    )
                elif isinstance(value, list):
                    for v in value:
                        payload.append(
                            {
                                "attribute": f"Metadata.{key}",
                                "operation": "delete",
                                "oldValue": v.id,
                            }
                        )
                else:
                    payload.append(
                        {
                            "attribute": f"Metadata.{key}",
                            "operation": "delete",
                            "oldValue": value.id,
                        }
                    )
            elif value != updated_metadata[key]:
                if isinstance(value, str):
                    payload.append(
                        {
                            "attribute": f"Metadata.{key}",
                            "operation": "update",
                            "oldValue": value,
                            "newValue": updated_metadata[key],
                        }
                    )
                elif isinstance(value, list):
                    existing_id = {v.id for v in value}
                    updated_id = {v.id for v in updated_metadata[key]}
                    to_add = updated_id - existing_id
                    to_remove = existing_id - updated_id

                    for v in to_add:
                        payload.append(
                            {
                                "attribute": f"Metadata.{key}",
                                "operation": "add",
                                "newValue": v,
                            }
                        )
                    for v in to_remove:
                        payload.append(
                            {
                                "attribute": f"Metadata.{key}",
                                "operation": "delete",
                                "oldValue": v,
                            }
                        )
                else:
                    payload.append(
                        {
                            "attribute": f"Metadata.{key}",
                            "operation": "update",
                            "oldValue": value.id,
                            "newValue": updated_metadata[key].id,
                        }
                    )
        for key, value in updated_metadata.items():
            if key not in existing_metadata:
                if isinstance(value, str):
                    payload.append(
                        {
                            "attribute": f"Metadata.{key}",
                            "operation": "add",
                            "newValue": value,
                        }
                    )
                elif isinstance(value, list):
                    for v in value:
                        payload.append(
                            {
                                "attribute": f"Metadata.{key}",
                                "operation": "add",
                                "newValue": v.id,
                            }
                        )
                else:
                    payload.append(
                        {
                            "attribute": f"Metadata.{key}",
                            "operation": "add",
                            "newValue": value.id,
                        }
                    )
        return payload

    def _generate_patch_payload(self, *, existing: BaseResource, updated: BaseResource) -> dict:
        """Generates a payload for PATCH requests based on the changes. This is overriden for some clases with more compex patch formation"""
        payload = {"data": []}
        for attribute in self._updatable_attributes:
            old_value = getattr(existing, attribute, None)
            new_value = getattr(updated, attribute, None)
            if attribute == "metadata":
                payload["data"].extend(
                    self._generate_metadata_diff(
                        existing_metadata=old_value, updated_metadata=new_value
                    )
                )
            else:
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
