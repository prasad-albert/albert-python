from albert.collections.base import BaseCollection
from albert.resources.workflows import Workflow
from albert.session import AlbertSession
from albert.utils.exceptions import ForbiddenError, NotFoundError


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

    def _list_generator(self, *, limit=50, start_key=None):
        params = {"limit": limit, "startKey": start_key}
        params = {k: v for k, v in params.items() if v is not None}
        while True:
            response = self.session.get(self.base_path, params=params)
            data = response.json().get("Items", [])
            if not data or data == []:
                break
            for x in data:
                try:  # listed items are not fully hydrated, so do a full get
                    yield self.get_by_id(x["albertId"])
                except (NotFoundError, ForbiddenError):
                    # sometimes that full get can cause issues with ACLs
                    continue
            start_key = response.json().get("lastKey")
            if not start_key:  # start key is tested here but not on init
                break
            params["startKey"] = start_key

    def list(self):
        return self._list_generator()

    def get_by_id(self, id):
        response = self.session.get(f"{self.base_path}/{id}")
        return Workflow(**response.json())

    def create(self, workflow: Workflow):
        response = self.session.post(
            self.base_path, json=workflow.model_dump(by_alias=True, exclude_none=True)
        )
        return Workflow(**response.json())
