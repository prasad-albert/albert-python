import logging
from typing import Any

from pydantic import Field, model_validator

from albert.resources.base import BaseAlbertModel
from albert.resources.serialization import SerializeAsEntityLink
from albert.resources.tags import Tag


class BaseTaggedEntity(BaseAlbertModel):
    """
    BaseTaggedEntity is a Pydantic model that includes functionality for handling tags.
    This BaseModel is in its own module so that it can utilize Tags

    Attributes
    ----------
    tags : Optional[List[Union[Tag,str]]]
        A list of Tag objects or strings representing tags.

    Methods
    -------
    convert_tags(values: Dict[str, Any]) -> Dict[str, Any]
        Converts tag strings to Tag objects.
    """

    tags: list[SerializeAsEntityLink[Tag]] | None = Field(None)

    @model_validator(mode="before")
    @classmethod
    def convert_tags(cls, data: dict[str, Any]) -> dict[str, Any]:
        tags = data.get("tags")
        if not tags:
            tags = data.get("Tags")
        if tags:
            new_tags = []
            for t in tags:
                if isinstance(t, Tag):
                    new_tags.append(t)
                elif isinstance(t, str):
                    new_tags.append(Tag.from_string(t))
                elif isinstance(t, dict):
                    new_tags.append(Tag(**t))
                else:
                    # We do not expect this else to be hit because tags should only be Tag or str
                    logging.warning(f"Unexpected value for Tag. {t} of type {type(t)}")
                    pass
            data["tags"] = new_tags
        return data
