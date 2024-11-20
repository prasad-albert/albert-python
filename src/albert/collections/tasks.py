from albert.collections.base import BaseCollection, OrderBy
from albert.resources.tasks import (
    BaseTask,
    TaskAdapter,
    TaskCategory,
)
from albert.session import AlbertSession
from albert.utils.pagination import AlbertPaginator, PaginationMode


class TaskCollection(BaseCollection):
    _api_version = "v3"
    _updatable_attributes = {"metadata"}

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{TaskCollection._api_version}/tasks"

    def create(self, *, task: BaseTask) -> BaseTask:
        payload = [task.model_dump(mode="json", by_alias=True, exclude_none=True)]
        url = f"{self.base_path}/multi?category={task.category.value}"
        if task.parent_id is not None:
            url = f"{url}&parentId={task.parent_id}"
        response = self.session.post(url=url, json=payload)
        task_data = response.json()[0]
        return TaskAdapter.validate_python(task_data)

    def delete(self, *, id: str) -> None:
        url = f"{self.base_path}/{id}"
        self.session.delete(url)

    def get_by_id(self, *, id: str) -> BaseTask:
        # each type of task has it's own sub-prefix.
        # Sometimes the core "TAS" prefix is dropped on the object.
        # This ensures both the TAS and sub prefix are present on the ID
        if not id.startswith("TAS"):
            id = f"TAS{id}"
        url = f"{self.base_path}/multi/{id}"
        response = self.session.get(url)
        return TaskAdapter.validate_python(response.json())

    def get_by_ids(self, *, ids: list[str]) -> BaseTask:
        ids = [f"TAS{x}" if not x.startswith("TAS") else x for x in ids]
        response = self.session.get(self.base_path, params={"id": ids})
        return [TaskAdapter.validate_python(x) for x in response.json()["Items"]]

    def list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        text: str = None,
        order: OrderBy = OrderBy.DESCENDING,
        sort_by: str = None,
        tags: list[str] = None,
        task_id: list[str] = None,
        linked_task: list[str] = None,
        category: TaskCategory = None,
        albert_id: list[str] = None,
        data_template: list[str] = None,
        assigned_to: list[str] = None,
        location: list[str] = None,
        priority: list[str] = None,
        status: list[str] = None,
        parameter_group: list[str] = None,
        created_by: list[str] = None,
        project_id: str = None,
    ) -> AlbertPaginator[BaseTask]:
        def deserialize(items: list[dict]) -> list[BaseTask]:
            return self.get_by_ids(ids=[x["albertId"] for x in items])

        params = {
            "limit": limit,
            "offset": offset,
            "order": OrderBy(order).value if order else None,
            "text": text,
            "sortBy": sort_by,
            "tags": tags,
            "taskId": task_id,
            "linkedTask": linked_task,
            "category": category,
            "albertId": albert_id,
            "dataTemplate": data_template,
            "assignedTo": assigned_to,
            "location": location,
            "priority": priority,
            "status": status,
            "parameterGroup": parameter_group,
            "createdBy": created_by,
            "projectId": project_id,
        }

        return AlbertPaginator(
            mode=PaginationMode.OFFSET,
            path=f"{self.base_path}/search",
            session=self.session,
            deserialize=deserialize,
            params=params,
        )
