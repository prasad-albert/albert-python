from albert.collections.base import BaseCollection, OrderBy
from albert.resources.tasks import BaseTask, BatchTask, GeneralTask, PropertyTask, TaskCategory
from albert.session import AlbertSession
from albert.utils.exceptions import ForbiddenError, InternalServerError, NotFoundError
from albert.utils.logging import logger
from albert.utils.pagination import AlbertPaginator, PaginationMode


class TaskCollection(BaseCollection):
    _api_version = "v3"
    _updatable_attributes = {"metadata"}
    # Mapping TaskCategory to the corresponding Task subclass
    category_to_class = {
        TaskCategory.PROPERTY: PropertyTask,
        TaskCategory.BATCH: BatchTask,
        TaskCategory.GENERAL: GeneralTask,
    }

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_path = f"/api/{TaskCollection._api_version}/tasks"

    def create(self, *, task: BaseTask) -> BaseTask:
        payload = [task.model_dump(by_alias=True, exclude_none=True)]
        url = f"{self.base_path}/multi?category={task.category.value}"
        if task.parent_id is not None:
            url += f"&parentId={task.parent_id}"
        response = self.session.post(url=url, json=payload)
        task_data = response.json()[0]
        task_class = self.category_to_class.get(task_data.get("category"), BaseTask)
        return task_class(**task_data)

    def delete(self, *, task_id: str) -> None:
        url = f"{self.base_path}/{task_id}"
        self.session.delete(url)

    def get_by_id(self, *, task_id: str) -> BaseTask:
        # each type of task has it's own sub-prefix. Sometimes the core "TAS" prefix is dropped on the object. This ensures both the TAS and sub prefix are present on the ID
        if not task_id.startswith("TAS"):
            task_id = f"TAS{task_id}"
        url = f"{self.base_path}/{task_id}"
        response = self.session.get(url)
        task_data = response.json()
        task_class = self.category_to_class.get(task_data.get("category"), BaseTask)
        return task_class(**task_data)

    def list(
        self,
        *,
        text: str = None,
        order: OrderBy = OrderBy.DESCENDING,
        offset: int = 0,
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
        def deserialize(data: dict) -> BaseTask | None:
            # task_class = self.category_to_class.get(data.get("category"), BaseTask)
            # return task_class(**data)
            id = data["albertId"]
            try:
                return self.get_by_id(task_id=id)
            except (ForbiddenError, InternalServerError, NotFoundError) as e:
                logger.warning(f"Error fetching Data Template '{id}': {e}")
                return None

        params = {
            "text": text,
            "order": OrderBy(order).value if order else None,
            "offset": offset,
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
        params = {k: v for k, v in params.items() if v is not None}
        return AlbertPaginator(
            mode=PaginationMode.OFFSET,
            path=f"{self.base_path}/search",
            session=self.session,
            deserialize=deserialize,
            params=params,
        )
