from enum import Enum

from pydantic import Field

from albert.resources.base import BaseAlbertModel


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
    id: str | None = Field(None, alias="albertId")

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
