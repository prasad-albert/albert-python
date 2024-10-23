from enum import Enum

from albert.resources.base import BaseResource
from albert.resources.serialization import BaseEntityLink
from albert.session import AlbertSession
from albert.utils.patches import PatchDatum, PatchOperation, PatchPayload


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

    # Class property specifying updatable attributes
    _updatable_attributes = {}

    def __init__(self, *, session: AlbertSession):
        self.session = session

    def _generate_metadata_diff(
        self,
        existing_metadata: dict[str, str | list[BaseEntityLink] | BaseEntityLink],
        updated_metadata: dict[str, str | list[BaseEntityLink] | BaseEntityLink],
    ) -> list[PatchDatum]:
        if existing_metadata is None:
            existing_metadata = {}
        if updated_metadata is None:
            updated_metadata = {}

        data = []
        for key, value in existing_metadata.items():
            if key not in updated_metadata:
                if isinstance(value, str):
                    data.append(
                        PatchDatum(
                            attribute=f"Metadata.{key}",
                            operation=PatchOperation.DELETE,
                            old_value=value,
                        )
                    )
                elif isinstance(value, list):
                    for v in value:
                        data.append(
                            PatchDatum(
                                attribute=f"Metadata.{key}",
                                operation=PatchOperation.DELETE,
                                old_value=v.id,
                            )
                        )
                else:
                    data.append(
                        PatchDatum(
                            attribute=f"Metadata.{key}",
                            operation=PatchOperation.DELETE,
                            old_value=value.id,
                        )
                    )
            elif value != updated_metadata[key]:
                if isinstance(value, str):
                    data.append(
                        PatchDatum(
                            attribute=f"Metadata.{key}",
                            operation=PatchOperation.UPDATE,
                            old_value=value,
                            new_value=updated_metadata[key],
                        )
                    )
                elif isinstance(value, list):
                    existing_id = {v.id for v in value}
                    updated_id = {v.id for v in updated_metadata[key]}
                    to_add = updated_id - existing_id
                    to_remove = existing_id - updated_id

                    for v in to_add:
                        data.append(
                            PatchDatum(
                                attribute=f"Metadata.{key}",
                                operation=PatchOperation.ADD,
                                new_value=v,
                            )
                        )
                    for v in to_remove:
                        data.append(
                            PatchDatum(
                                attribute=f"Metadata.{key}",
                                operation=PatchOperation.DELETE,
                                old_value=v,
                            )
                        )
                else:
                    data.append(
                        PatchDatum(
                            attribute=f"Metadata.{key}",
                            operation=PatchOperation.UPDATE,
                            old_value=value.id,
                            new_value=updated_metadata[key].id,
                        )
                    )
        for key, value in updated_metadata.items():
            if key not in existing_metadata:
                if isinstance(value, str):
                    data.append(
                        PatchDatum(
                            attribute=f"Metadata.{key}",
                            operation=PatchOperation.ADD,
                            new_value=value,
                        )
                    )
                elif isinstance(value, list):
                    for v in value:
                        data.append(
                            PatchDatum(
                                attribute=f"Metadata.{key}",
                                operation=PatchOperation.ADD,
                                new_value=v.id,
                            )
                        )
                else:
                    data.append(
                        PatchDatum(
                            attribute=f"Metadata.{key}",
                            operation=PatchOperation.ADD,
                            new_value=value.id,
                        )
                    )

        return data

    def _generate_patch_payload(
        self,
        *,
        existing: BaseResource,
        updated: BaseResource,
    ) -> PatchPayload:
        """Generate a payload for PATCH requests based on the changes.

        This is overriden for some clases with more compex patch formation.
        """
        data = []
        for attribute in self._updatable_attributes:
            old_value = getattr(existing, attribute, None)
            new_value = getattr(updated, attribute, None)
            if attribute == "metadata":
                data.extend(
                    self._generate_metadata_diff(
                        existing_metadata=old_value,
                        updated_metadata=new_value,
                    )
                )
            else:
                # Get the serialization alias name for the attribute, if it exists
                alias = existing.model_fields[attribute].alias or attribute

                if old_value is None and new_value is not None:
                    # Add new attribute
                    data.append(
                        PatchDatum(
                            operation=PatchOperation.ADD,
                            attribute=alias,
                            new_value=new_value,
                        )
                    )
                elif old_value is not None and new_value != old_value:
                    # Update existing attribute
                    data.append(
                        PatchDatum(
                            operation=PatchOperation.UPDATE,
                            attribute=alias,
                            old_value=old_value,
                            new_value=new_value,
                        )
                    )

        return PatchPayload(data=data)
