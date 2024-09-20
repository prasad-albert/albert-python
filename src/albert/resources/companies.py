from typing import Any

from pydantic import Field, PrivateAttr

from albert.resources.base import BaseAlbertModel, Status


class Company(BaseAlbertModel):
    """
    Company is a Pydantic model representing a company entity.

    Attributes
    ----------
    name : str
        The name of the company.
    id : Optional[str]
        The Albert ID of the company.
    """

    name: str
    id: str | None = Field(None, alias="albertId")
    _distance: Status | None = PrivateAttr()

    def __init__(self, **data: Any):
        """
        Initialize a Company instance.

        Parameters
        ----------
        id : Optional[str]
            The Albert ID of the company.
        name : str
            The name of the company.
        """
        super().__init__(**data)
        if "distance" in data:
            self._distance = float(data["distance"])

    @property
    def distance(self) -> float:
        return self._distance
