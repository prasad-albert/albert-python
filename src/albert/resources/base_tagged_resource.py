from pydantic import Field, model_validator
from typing import Any, Dict, Optional, Union, List
from albert.resources.tags import Tag
from albert.resources.base_resource import BaseAlbertModel
import logging


class BaseTaggedEntity(BaseAlbertModel):
    """
    BaseTaggedEntity is a Pydantic model that includes functionality for handling tags.

    Attributes
    ----------
    tags : Optional[List[Union[Tag,str]]]
        A list of Tag objects or strings representing tags.

    Methods
    -------
    convert_tags(values: Dict[str, Any]) -> Dict[str, Any]
        Converts tag strings to Tag objects.
    """

    tags: Optional[List[Union[Tag, str]]] = Field(None)

    @model_validator(mode="before")
    @classmethod
    def convert_tags(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        tags = data.get("tags", None)
        if tags:
            new_tags = []
            for t in tags:
                if isinstance(t, Tag):
                    new_tags.append(t)
                elif isinstance(t, str):
                    new_tags.append(Tag.from_string(t))
                else:
                    # We do not expect this else to be hit because tags should only be Tag or str
                    logging.warning(f"Unexpected value for Tag. {t} of type {type(t)}")
                    pass
            data["tags"] = new_tags
        return data
