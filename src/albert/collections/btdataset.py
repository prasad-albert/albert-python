from albert.collections.base import BaseCollection
from albert.resources.btdataset import BTDataset
from albert.session import AlbertSession


class BTDatasetCollection(BaseCollection):
    """
    BTDatasetCollection is a collection class for managing Breakthrough dataset entities.

    Parameters
    ----------
    session : AlbertSession
        The Albert session instance.

    Attributes
    ----------
    base_path : str
        The base path for btdataset API requests.
    """

    _updatable_attributes = {"name", "key", "file_name", "report"}
    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        """
        Initialize the BTDatasetCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_path = f"/api/{BTDatasetCollection._api_version}/btdataset"

    def create(self, *, dataset: BTDataset) -> BTDataset:
        response = self.session.post(
            self.base_path,
            json=dataset.model_dump(by_alias=True, exclude_none=True),
        )
        return BTDataset(**response.json())

    def get(self, *, dataset_id: str) -> BTDataset:
        response = self.session.get(f"{self.base_path}/{dataset_id}")
        return BTDataset(**response.json())
