from collections.abc import Iterator

from albert.collections.base import BaseCollection, OrderBy
from albert.resources.projects import Project
from albert.session import AlbertSession
from albert.utils.pagination import AlbertPaginator, PaginationMode


class ProjectCollection(BaseCollection):
    """
    ProjectCollection is a collection class for managing project entities.

    Parameters
    ----------
    session : AlbertSession
        The Albert session instance.

    Attributes
    ----------
    base_path : str
        The base URL for project API requests.

    Methods
    -------
    create(project: Project) -> Optional[str]
        Creates a new project.
    get_by_id(project_id: str) -> Optional[dict]
        Retrieves a project by its ID.
    update(project_id: str, patch_data: dict) -> bool
        Updates a project by its ID.
    delete(project_id: str) -> bool
        Deletes a project by its ID.
    list(name: Optional[List[str]], category: Optional[str], order_by: OrderBy, exact_match: bool) -> Generator
        Lists projects with optional filters.
    """

    _api_version = "v3"
    _updatable_attributes = {"description", "grid", "metadata"}

    def __init__(self, *, session: AlbertSession):
        """
        Initialize a ProjectCollection object.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_path = f"/api/{ProjectCollection._api_version}/projects"

    def create(self, *, project: Project) -> Project:
        """
        Create a new project.

        Parameters
        ----------
        project : Project
            The project to create.

        Returns
        -------
        Optional[Project]
            The created project object if successful, None otherwise.
        """
        response = self.session.post(
            self.base_path, json=project.model_dump(by_alias=True, exclude_unset=True, mode="json")
        )
        return Project(**response.json())

    def get_by_id(self, *, id: str) -> Project:
        """
        Retrieve a project by its ID.

        Parameters
        ----------
        id : str
            The ID of the project to retrieve.

        Returns
        -------
        Project
            The project object if found
        """
        url = f"{self.base_path}/{id}"
        response = self.session.get(url)

        return Project(**response.json())

    def update(self, *, project: Project) -> Project:
        """
        TO DO: This needs some more custom patch logic
        """
        existing_project = self.get_by_id(id=project.id)
        patch_data = self._generate_patch_payload(existing=existing_project, updated=project)
        url = f"{self.base_path}/{project.id}"

        self.session.patch(url, json=patch_data.model_dump(mode="json", by_alias=True))

        return self.get_by_id(id=project.id)

    def delete(self, *, id: str) -> None:
        """
        Delete a project by its ID.

        Parameters
        ----------
        id : str
            The ID of the project to delete.

        Returns
        -------
        None
        """
        url = f"{self.base_path}/{id}"
        self.session.delete(url)

    def list(
        self,
        *,
        limit: int = 50,
        start_key: str | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Iterator[Project]:
        """
        List projects with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of items to retrieve per request (default is 50).
        start_key : Union[str, None], optional
            The start key for pagination.
        name : Optional[List[str]], optional
            The name filter for the projects.
        order_by : OrderBy, optional
            The order in which to retrieve items (default is OrderBy.DESCENDING).
        exact_match : bool, optional
            Whether to match names exactly (default is False).

        Returns
        ------
        Iterator[Project]
            An iterator of Project resources.
        """
        params = {"limit": limit, "orderBy": order_by.value, "startKey": start_key}
        return AlbertPaginator(
            mode=PaginationMode.KEY,
            path=self.base_path,
            session=self.session,
            params=params,
            deserialize=lambda items: [Project(**item) for item in items],
        )
