from albert.collections.base import BaseCollection
from albert.resources.btinsight import BTInsight, BTInsightCategory
from albert.session import AlbertSession
from albert.utils.pagination import ListIterator


class BTInsightCollection(BaseCollection):
    """
    BTInsightCollection is a collection class for managing Breakthrough insight entities.

    Parameters
    ----------
    session : AlbertSession
        The Albert session instance.

    Attributes
    ----------
    base_path : str
        The base path for BTInsight API requests.
    """

    _updatable_attributes = {
        "name",
        "state",
        "dataset_id",
        "model_session_id",
        "output_key",
        "start_time",
        "end_time",
        "total_time",
        "registry",
        "tags",
    }
    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        """
        Initialize the BTInsightCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_path = f"/api/{BTInsightCollection._api_version}/btinsight"

    def create(self, *, insight: BTInsight) -> BTInsight:
        """
        Create a new Breakthrough insight.

        Parameters
        ----------
        insight : BTInsight
            The dataset record to create.

        Returns
        -------
        BTInsight
            The created Breakthrough insight.
        """
        response = self.session.post(
            self.base_path,
            json=insight.model_dump(by_alias=True, exclude_none=True),
        )
        return BTInsight(**response.json())

    def get_by_id(self, *, id: str) -> BTInsight:
        """
        Get a Breakthrough insight by ID.

        Parameters
        ----------
        id : str
            The Albert ID of the insight.

        Returns
        -------
        BTInsight
            The retrived Breakthrough insight.
        """
        response = self.session.get(f"{self.base_path}/{id}")
        return BTInsight(**response.json())

    def list(
        self,
        *,
        limit: int = 100,
        name: str | None = None,
        created_by: str | None = None,
        category: BTInsightCategory | None = None,
        start_key: str | None = None,
    ) -> ListIterator[BTInsight]:
        params = {
            "limit": limit,
            "name": name,
            "createdBy": created_by,
            "category": category.value if category else None,
            "startKey": start_key,
        }
        return ListIterator(
            path=self.base_path,
            session=self.session,
            resource_cls=BTInsight,
            params=params,
        )

    def update(self, *, dataset: BTInsight) -> BTInsight:
        path = f"{self.base_path}/{dataset.id}"
        patch = self._generate_patch_payload(
            existing=self.get_by_id(id=dataset.id),
            updated=dataset,
        )
        self.session.patch(path, json=patch)
        return self.get_by_id(id=dataset.id)
