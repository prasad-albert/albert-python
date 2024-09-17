from collections.abc import Generator, Iterator

from albert.collections.base import BaseCollection, OrderBy
from albert.collections.companies import CompanyCollection
from albert.collections.tags import TagCollection
from albert.resources.projects import Project
from albert.session import AlbertSession


class ProjectCollection(BaseCollection):
    """
    ProjectCollection is a collection class for managing project entities.

    Parameters
    ----------
    session : AlbertSession
        The Albert session instance.

    Attributes
    ----------
    base_url : str
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

    def __init__(self, *, session: AlbertSession):
        """
        Initialize a ProjectCollection object.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_url = "/api/v3/projects"

    def create(self, *, project: Project) -> Project | None:
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
        all_tags = []
        tag_collection = TagCollection(session=self.session)
        for t in project.tags:
            if t.id is None:
                t = tag_collection.create(t)
            all_tags.append(t)
        project.tags = all_tags
        if project.company and project.company.id is None:
            company_collection = CompanyCollection(session=self.session)
            project.company = company_collection.create(project.company)
        response = self.session.post(self.base_url, json=project.to_dict())

        return Project(**response.json())

    def get_by_id(self, *, project_id: str) -> Project:
        """
        Retrieve a project by its ID.

        Parameters
        ----------
        project_id : str
            The ID of the project to retrieve.

        Returns
        -------
        Project
            The project object if found
        """
        url = f"{self.base_url}/{project_id}"
        response = self.session.get(url)

        return Project(**response.json())

    def update(self, *, project_id: str, patch_data: dict) -> bool:
        """
        Update a project by its ID.

        Parameters
        ----------
        project_id : str
            The ID of the project to update.
        patch_data : dict
            The patch data to update the project with.

        Returns
        -------
        bool
            True if the update was successful, False otherwise.
        """
        url = f"{self.base_url}/{project_id}"

        self.session.patch(url, json=patch_data)

        return True

    def delete(self, *, project_id: str) -> bool:
        """
        Delete a project by its ID.

        Parameters
        ----------
        project_id : str
            The ID of the project to delete.

        Returns
        -------
        bool
            True if the deletion was successful
        """
        url = f"{self.base_url}/{project_id}"

        self.session.delete(url)

        return True

    def _list_generator(
        self,
        *,
        limit: int = 50,
        start_key: str = None,
        name: list[str] | None = None,
        category: str | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
        exact_match: bool = False,
    ) -> Generator[Project, None, None]:
        """
        Generator for listing projects with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of items to retrieve per request (default is 50).
        start_key : Union[str, None], optional
            The start key for pagination.
        name : Optional[List[str]], optional
            The name filter for the projects.
        category : Optional[str], optional
            The category filter for the projects.
        order_by : OrderBy, optional
            The order in which to retrieve items (default is OrderBy.DESCENDING).
        exact_match : bool, optional
            Whether to match names exactly (default is False).

        Yields
        ------
        Project
            The next project in the generator.
        """
        params = {
            "limit": str(limit),
            "orderBy": order_by.value,
            "exactMatch": str(exact_match).lower(),
        }
        if start_key:
            params["startKey"] = start_key
        if name:
            params["name"] = ",".join(name)
        if category:
            params["category"] = category
        while True:
            response = self.session.get(self.base_url, params=params)

            raw_projects = response.json().get("Items", [])
            if not raw_projects or raw_projects == []:
                break
            for x in raw_projects:
                yield Project(**x)
            start_key = response.json().get("lastKey")
            if not start_key or len(raw_projects) < limit:
                break
            params["startKey"] = start_key

    def list(
        self,
        *,
        name: list[str] | None = None,
        category: str | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
        exact_match: bool = False,
    ) -> Iterator[Project]:
        """
        List projects with optional filters.

        Parameters
        ----------
        name : Optional[List[str]], optional
            The name filter for the projects.
        category : Optional[str], optional
            The category filter for the projects.
        order_by : OrderBy, optional
            The order in which to retrieve items (default is OrderBy.DESCENDING).
        exact_match : bool, optional
            Whether to match names exactly (default is False).

        Returns
        -------
        Generator
            A generator yielding projects that match the filters.
        """
        return self._list_generator(
            name=name, category=category, order_by=order_by, exact_match=exact_match
        )
