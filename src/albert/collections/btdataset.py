from albert.collections.base import BaseCollection
from albert.resources.btdataset import BTDataset
from albert.session import AlbertSession
from albert.utils.pagination import ListIterator


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
        """
        Create a new Breakthrough dataset.

        Parameters
        ----------
        dataset : BTDataset
            The dataset record to create.

        Returns
        -------
        BTDataset
            The created Breakthrough dataset.
        """
        response = self.session.post(
            self.base_path,
            json=dataset.model_dump(by_alias=True, exclude_none=True),
        )
        return BTDataset(**response.json())

    def get_by_id(self, *, id: str) -> BTDataset:
        """
        Get a Breakthrough dataset by ID.

        Parameters
        ----------
        id : str
            The Albert ID of the dataset.

        Returns
        -------
        BTDataset
            The retrived Breakthrough dataset.
        """
        response = self.session.get(f"{self.base_path}/{id}")
        return BTDataset(**response.json())

    def list(
        self,
        *,
        limit: int = 100,
        name: str | None = None,
        created_by: str | None = None,
        start_key: str | None = None,
    ) -> ListIterator[BTDataset]:
        params = {"limit": limit, "name": name, "createdBy": created_by, "startKey": start_key}
        return ListIterator(
            path=self.base_path,
            session=self.session,
            resource_cls=BTDataset,
            params=params,
        )

    def update(self, *, dataset: BTDataset) -> BTDataset:
        path = f"{self.base_path}/{dataset.id}"
        patch = self._generate_patch_payload(
            existing=self.get_by_id(id=dataset.id),
            updated=dataset,
        )
        self.session.patch(path, json=patch)
        return self.get_by_id(id=dataset.id)
