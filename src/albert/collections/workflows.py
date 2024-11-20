from albert.collections.base import BaseCollection
from albert.resources.workflows import Workflow
from albert.session import AlbertSession
from albert.utils.pagination import AlbertPaginator, PaginationMode


class WorkflowCollection(BaseCollection):
    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the WorkflowCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_path = f"/api/{WorkflowCollection._api_version}/workflows"

    def create(self, *, workflow: Workflow) -> Workflow:
        response = self.session.post(
            self.base_path,
            json=workflow.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return Workflow(**response.json())

    def get_by_id(self, *, id: str) -> Workflow:
        response = self.session.get(f"{self.base_path}/{id}")
        return Workflow(**response.json())

    def get_by_ids(self, *, ids: list[str]) -> Workflow:
        response = self.session.get(f"{self.base_path}/ids", params={"id": ids})
        return [Workflow(**item) for item in response.json()["Items"]]

    def list(self, limit: int = 50) -> AlbertPaginator[Workflow]:
        def deserialize(items: list[dict]) -> list[Workflow]:
            return self.get_by_ids(ids=[x["albertId"] for x in items])

        params = {"limit": limit}
        return AlbertPaginator(
            mode=PaginationMode.KEY,
            path=self.base_path,
            params=params,
            session=self.session,
            deserialize=deserialize,
        )
