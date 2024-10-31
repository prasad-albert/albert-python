from albert.collections.base import BaseCollection, OrderBy
from albert.resources.tasks import Task
from albert.session import AlbertSession


class TaskCollection(BaseCollection):
    _api_version = "v3"
    _updatable_attributes = {"metadata"}

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{TaskCollection._api_version}/tasks"

    def create(self, *, task: Task) -> Task:
        payload = [task.model_dump(by_alias=True, exclude_none=True)]
        response = self.session.post(self.base_path, json=payload)
        print(response.json())
        return Task(**response.json())

    def delete(self, *, task_id: str) -> None:
        url = f"{self.base_path}/{task_id}"
        self.session.delete(url)
