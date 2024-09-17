import logging
from collections.abc import Generator, Iterator

from albert.albert_session import AlbertSession
from albert.collections.base import BaseCollection, OrderBy
from albert.resources.tags import Tag


class TagCollection(BaseCollection):
    """
    TagCollection is a collection class for managing tag entities.

    Parameters
    ----------
    session : AlbertSession
        The Albert session instance.

    Attributes
    ----------
    base_url : str
        The base URL for tag API requests.
    tag_cache : dict
        A cache of tag objects.

    Methods
    -------
    list(limit=50, order_by=OrderBy.DESCENDING, name=None, exact_match=True)
        Lists tag entities with optional filters.
    tag_exists(tag, exact_match=True) -> bool
        Checks if a tag exists by its name.
    create(tag) -> Tag
        Creates a new tag entity.
    get_by_id(tag_id) -> Tag
        Retrieves a tag by its ID.
    get_by_tag(tag, exact_match=True) -> Tag
        Retrieves a tag by its name.
    delete(tag_id) -> bool
        Deletes a tag by its ID.
    rename(old_name, new_name) -> Optional[Tag]
        Renames an existing tag entity.
    """

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the TagCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.tag_cache = {}
        self.base_url = "/api/v3/tags"

    def _remove_from_cache_by_id(self, *, id: str):
        name = None
        for k, v in self.tag_cache.items():
            if v.id == id:
                name = k
                break
        if name:
            del self.tag_cache[name]

    def _list_generator(
        self,
        *,
        limit: int = 50,
        order_by: OrderBy = OrderBy.DESCENDING,
        name: str | list[str] = None,
        exact_match: bool = True,
        start_key: str | None = None,
    ) -> Generator[Tag, None, None]:
        """
        Lists tag entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of tags to return, by default 50.
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING.
        name : Union[str, None], optional
            The name of the tag to filter by, by default None.
        exact_match : bool, optional
            Whether to match the name exactly, by default True.
        start_key : Optional[str], optional
            The starting point for the next set of results, by default None.

        Returns
        -------
        Generator
            A generator of Tag objects.
        """
        params = {"limit": limit, "orderBy": order_by.value}
        if name:
            params["name"] = name if isinstance(name, list) else [name]
            params["exactMatch"] = str(exact_match).lower()
        if start_key:
            params["startKey"] = start_key

        while True:
            response = self.session.get(self.base_url, params=params)
            tags_data = response.json().get("Items", [])
            if not tags_data or tags_data == []:
                break
            for t in tags_data:
                this_tag = Tag(**t)
                self.tag_cache[this_tag.tag] = this_tag
                yield this_tag
            start_key = response.json().get("lastKey")
            if not start_key:
                break
            params["startKey"] = start_key

    def list(
        self,
        *,
        order_by: OrderBy = OrderBy.DESCENDING,
        name: str | list[str] = None,
        exact_match: bool = True,
    ) -> Iterator[Tag]:
        """
        Lists tag entities with optional filters.

        Parameters
        ----------
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING.
        name : Union[str, None], optional
            The name of the tag to filter by, by default None.
        exact_match : bool, optional
            Whether to match the name exactly, by default True.

        Returns
        -------
        Generator
            A generator of Tag objects.
        """
        return self._list_generator(order_by=order_by, name=name, exact_match=exact_match)

    def tag_exists(self, *, tag: str, exact_match: bool = True) -> bool:
        """
        Checks if a tag exists by its name.

        Parameters
        ----------
        tag : str
            The name of the tag to check.
        exact_match : bool, optional
            Whether to match the name exactly, by default True.

        Returns
        -------
        bool
            True if the tag exists, False otherwise.
        """
        if tag.lower() in self.tag_cache:
            return True
        params = {"limit": "2", "name": [tag], "exactMatch": str(exact_match).lower()}

        response = self.session.get(self.base_url, params=params)
        tags = response.json().get("Items", [])
        for t in tags:
            found_tag = Tag(**t)
            self.tag_cache[found_tag.tag.lower()] = found_tag
        return len(tags) > 0

    def create(self, *, tag: str | Tag) -> Tag:
        """
        Creates a new tag entity if the given tag does not exist.

        Parameters
        ----------
        tag : Union[str, Tag]
            The tag name or Tag object to create.

        Returns
        -------
        Tag
            The created Tag object or the existing Tag object of it already exists.
        """
        if isinstance(tag, str):
            tag = Tag(tag=tag)
        if self.tag_exists(tag=tag.tag):
            existing_tag = self.tag_cache[tag.tag.lower()]
            logging.warning(f"Tag {existing_tag.tag} already exists with id {existing_tag.id}")
            return existing_tag
        payload = {"name": tag.tag}
        response = self.session.post(self.base_url, json=payload)
        tag = Tag(**response.json())
        self.tag_cache[tag.tag.lower()] = tag
        return tag

    def get_by_id(self, *, tag_id: str) -> Tag | None:
        """
        Retrieves a tag by its ID of None if not found.

        Parameters
        ----------
        tag_id : str
            The ID of the tag to retrieve.

        Returns
        -------
        Tag
            The Tag object if found, None otherwise.
        """
        url = f"{self.base_url}/{tag_id}"
        response = self.session.get(url)
        tag = Tag(**response.json())
        self.tag_cache[tag.tag] = tag
        return tag

    def get_by_tag(self, *, tag: str, exact_match: bool = True) -> Tag | None:
        """
        Retrieves a tag by its name of None if not found.

        Parameters
        ----------
        tag : str
            The name of the tag to retrieve.
        exact_match : bool, optional
            Whether to match the name exactly, by default True.

        Returns
        -------
        Tag
            The Tag object if found, None otherwise.
        """
        if tag in self.tag_cache:
            return self.tag_cache[tag]
        found = self.list(name=tag, exact_match=exact_match)
        return next(found, None)

    def delete(self, *, tag_id: str) -> bool:
        """
        Deletes a tag by its ID.

        Parameters
        ----------
        tag_id : str
            The ID of the tag to delete.

        Returns
        -------
        bool
            True if the tag was successfully deleted, False otherwise.
        """
        url = f"{self.base_url}/{tag_id}"
        self.session.delete(url)
        self._remove_from_cache_by_id(id=tag_id)
        return True

    def rename(self, *, old_name: str, new_name: str) -> Tag | None:
        """
        Renames an existing tag entity.

        Parameters
        ----------
        old_name : str
            The current name of the tag.
        new_name : str
            The new name of the tag.

        Returns
        -------
        Optional[Tag]
            The renamed Tag object if successful, None otherwise.
        """
        found_tag = self.get_by_tag(tag=old_name, exact_match=True)

        if not found_tag:
            logging.error(f'Tag "{old_name}" not found.')
            return None
        tag_id = found_tag.id
        payload = [
            {
                "data": [
                    {
                        "operation": "update",
                        "attribute": "name",
                        "oldValue": old_name,
                        "newValue": new_name,
                    }
                ],
                "id": tag_id,
            }
        ]
        self.session.patch(self.base_url, json=payload)
        self._remove_from_cache_by_id(id=tag_id)
        updated_tag = self.get_by_id(tag_id=tag_id)
        self.tag_cache[updated_tag.tag] = updated_tag
        return updated_tag
