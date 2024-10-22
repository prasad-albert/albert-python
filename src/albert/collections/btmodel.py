from albert.collections.base import BaseCollection
from albert.session import AlbertSession


class BTModelSessionCollection(BaseCollection):
    """
    BTModelSessionCollection is a collection class for managing Breakthrough model session entities.

    Parameters
    ----------
    session : AlbertSession
        The Albert session instance.

    Attributes
    ----------
    base_path : str
        The base path for BTModelSession API requests.
    """

    _api_version = "v3"
    _updatable_attributes = {}


class BTModelCollection(BaseCollection):
    """
    BTModelCollection is a collection class for managing Breakthrough model entities.

    Breakthrough models are associated with a parent Breakthrough model session.

    Parameters
    ----------
    session : AlbertSession
        The Albert session instance.
    parent_id: str
        The Albert ID for the parent model session.

    Attributes
    ----------
    base_path : str
        The base path for BTModel API requests.
    """

    _updatable_attributes = {}

    def __init__(self, *, session: AlbertSession, parent_id: str):
        super().__init__(session=session)
        self.base_path = f"/api/{BTModelSessionCollection._api_version}/btmodel/{parent_id}"
