import requests
from enum import Enum
from typing import Optional, List, Any, Union, Dict, Generator
from pydantic import model_validator, Field
from albert.base_tagged_entity import BaseTaggedEntity
from albert.entity.tags import Tag
from albert.base_collection import BaseCollection, OrderBy
from albert.entity.companies import Company


class ProjectCategory(Enum):
    DEVELOPMENT = "Development"
    RESEARCH = "Research"
    PRODUCTION = "Production"


class ProjectClass(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"


class Project(BaseTaggedEntity):
    """
    Project is a Pydantic model representing a project entity.

    Attributes
    ----------
    name : str
        The name of the project.
    description : str
        The description of the project.
    category : ProjectCategory
        The category of the project.
    project_class : Optional[ProjectClass]
        The classification of the project.
    tags : List[Tag]
        The tags associated with the project.
    id : Optional[str]
        The Albert ID of the project.
    company : Optional[Company]
        The company associated with the project.
    """

    name: str
    description: str
    category: ProjectCategory
    project_class: Optional[ProjectClass] = None
    tags: List[Tag] = []
    id: Optional[str] = Field(None, alias="projectId")
    company: Optional[Company] = None

    @model_validator(mode="before")
    @classmethod
    def set_default_class(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set the default project class to PUBLIC if none is provided.

        Parameters
        ----------
        values : Dict[str, Any]
            A dictionary of field values.

        Returns
        -------
        Dict[str, Any]
            Updated field values with a default project class if not provided.
        """
        if "project_class" not in values or values["project_class"] is None:
            values["project_class"] = ProjectClass.PUBLIC
        return values


class ProjectCollection(BaseCollection):
    """
    ProjectCollection is a collection class for managing project entities.

    Parameters
    ----------
    client : Any
        The Albert client instance.

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

    def __init__(self, client):
        """
        Initialize a ProjectCollection object.

        Parameters
        ----------
        client : Any
            The Albert client instance.
        """
        super().__init__(client=client)
        self.base_url = f"{self.client.base_url}/api/v3/projects"

    def create(self, project: Project) -> Optional[Project]:
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
        for t in project.tags:
            if t.id is None:
                t = self.client.tags.create(t)
            all_tags.append(t)
        project.tags = all_tags
        if project.company and project.company.id is None:
            project.company = self.client.companies.create(project.company)
        response = requests.post(
            self.base_url, json=project.to_dict(), headers=self.client.headers
        )

        if response.status_code == 201:
            return Project(**response.json())
        else:
            return self.handle_api_error(response)

    def get_by_id(self, project_id: str) -> Optional[Project]:
        """
        Retrieve a project by its ID.

        Parameters
        ----------
        project_id : str
            The ID of the project to retrieve.

        Returns
        -------
        Optional[Project]
            The project object if found, None otherwise.
        """
        url = f"{self.base_url}/{project_id}"
        response = requests.get(url, headers=self.client.headers)
        if response.status_code == 200:
            return Project(**response.json())
        elif response.status_code == 404:
            return None  # Project not found
        else:
            return self.handle_api_error(response)

    def update(self, project_id: str, patch_data: dict) -> bool:
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

        response = requests.patch(url, json=patch_data, headers=self.client.headers)
        if response.status_code == 204:
            return True
        else:
            return self.handle_api_error(response)

    def delete(self, project_id: str) -> bool:
        """
        Delete a project by its ID.

        Parameters
        ----------
        project_id : str
            The ID of the project to delete.

        Returns
        -------
        bool
            True if the deletion was successful, False otherwise.
        """
        url = f"{self.base_url}/{project_id}"

        response = requests.delete(url, headers=self.client.headers)

        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            return False  # Project not found
        else:
            return self.handle_api_error(response)

    def _list_generator(
        self,
        limit: int = 50,
        start_key: Union[str,] = None,
        name: Optional[List[str]] = None,
        category: Optional[str] = None,
        order_by: OrderBy = OrderBy.DESCENDING,
        exact_match: bool = False,
    ) -> Generator:
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
            response = requests.get(
                self.base_url, headers=self.client.headers, params=params
            )
            if response.status_code == 200:
                raw_projects = response.json().get("Items", [])
                if not raw_projects or raw_projects == []:
                    break
                for x in raw_projects:
                    yield Project(**x)
                start_key = response.json().get("lastKey")
                if not start_key or len(raw_projects) < limit:
                    break
                params["startKey"] = start_key
            else:
                self.handle_api_error(response)
                break

    def list(
        self,
        name: Optional[List[str]] = None,
        category: Optional[str] = None,
        order_by: OrderBy = OrderBy.DESCENDING,
        exact_match: bool = False,
    ) -> Generator:
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
