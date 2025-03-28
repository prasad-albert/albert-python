from albert.collections.base import BaseCollection
from albert.resources.notebooks import Notebook
from albert.session import AlbertSession


class NotebookCollection(BaseCollection):
    """NotebookCollection is a collection class for managing Notebook entities in the Albert platform."""

    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the NotebookCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_path = f"/api/{NotebookCollection._api_version}/notebooks"

    def get_by_id(self, *, id: str) -> Notebook:
        """Retrieve a Notebook by its ID.

        Parameters
        ----------
        id : str
            The ID of the Notebook to retrieve.

        Returns
        -------
        Notebook
            The Notebook object.
        """
        response = self.session.get(f"{self.base_path}/{id}")
        return Notebook(**response.json())

    def create(self, *, notebook: Notebook) -> Notebook:
        """Create or return notebook for the provided notebook.
        This endpoint automatically tries to find an existing notebook with the same parameter setpoints, and will either return the existing notebook or create a new one.

        Parameters
        ----------
        notebook : Notebook
            A list of Notebook objects to find or create.

        Returns
        -------
        Notebook
            A list of created or found Notebook objects.
        """
        response = self.session.post(
            url=self.base_path,
            json=notebook.model_dump(mode="json", by_alias=True, exclude_none=True),
            params={"parentId": notebook.parent_id},
        )
        return Notebook(**response.json())

    def delete(self, *, id: str) -> None:
        """
        Deletes a notebook by its ID.

        Parameters
        ----------
        id : str
            The ID of the notebook to delete.
        """
        self.session.delete(f"{self.base_path}/{id}")
