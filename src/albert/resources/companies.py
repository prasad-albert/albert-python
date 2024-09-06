from typing import Optional, Any
from albert.resources.base_resource import BaseAlbertModel
from pydantic import Field, PrivateAttr
from albert.resources.base_resource import Status


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
    id: Optional[str] = Field(None, alias="albertId")
    _distance: Optional[Status] = PrivateAttr(Status.ACTIVE)

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
    def distance(self):
        return self._distance
