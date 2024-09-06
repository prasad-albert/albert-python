from typing import Optional
from pydantic import Field
from albert.resources.base_resource import BaseAlbertModel
from enum import Enum


class TagEntity(str, Enum):
    """
    TagEntity is an enumeration of possible tag entities.

    Attributes
    ----------
    INVENTORY : str
        Represents an inventory tag entity.
    COMPANY : str
        Represents a company tag entity.
    """

    INVENTORY = "Inventory"
    COMPANY = "Company"


class Tag(BaseAlbertModel):
    """
    Tag is a Pydantic model representing a tag entity.

    Attributes
    ----------
    tag : str
        The name of the tag.
    id : Optional[str]
        The Albert ID of the tag.

    Methods
    -------
    from_string(tag: str) -> "Tag"
        Creates a Tag object from a string.
    """

    tag: str = Field(alias="name")
    id: Optional[str] = Field(None, alias="albertId")

    @classmethod
    def from_string(cls, tag: str) -> "Tag":
        """
        Creates a Tag object from a string.

        Parameters
        ----------
        tag : str
            The name of the tag.

        Returns
        -------
        Tag
            The Tag object created from the string.
        """
        return cls(tag=tag)
