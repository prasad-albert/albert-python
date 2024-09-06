from collections.abc import Generator, Iterator

from albert.albert_session import AlbertSession
from albert.collections.base import BaseCollection, OrderBy
from albert.resources.base import BaseAlbertModel
from albert.resources.cas import Cas


class CasCollection(BaseCollection):
    """
    CasCollection is a collection class for managing CAS entities.

    Parameters
    ----------
    session : AlbertSession
        The Albert session instance.

    Attributes
    ----------
    base_url : str
        The base URL for CAS API self.session.
    cas_cache : dict
        A cache of CAS objects.

    Methods
    -------
    list(limit=50, start_key=None, number=None, albert_id=None, order_by=OrderBy.DESCENDING, filter=None, created_by=None, updated_by=None) -> List[Cas]
        Lists CAS entities with optional filters.
    cas_exists(number, exact_match=True) -> bool
        Checks if a CAS exists by its number.
    create(cas) -> Cas
        Creates a new CAS entity.
    get_by_id(cas_id) -> Cas
        Retrieves a CAS by its ID.
    get_by_number(number, exact_match=True) -> Optional[Cas]
        Retrieves a CAS by its number.
    delete(cas_id) -> bool
        Deletes a CAS by its ID.
    rename(old_number, new_number) -> Optional[Cas]
        Renames an existing CAS entity.
    """

    _updatable_attributes = {"notes", "description", "smiles"}

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the CasCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_url = "/api/v3/cas"
        self.cas_cache = {}

    def _remove_from_cache_by_id(self, *, id):
        name = None
        for k, v in self.cas_cache.items():
            if v.id == id:
                name = k
                break
        if name:
            del self.cas_cache[name]

    def _list_generator(
        self,
        *,
        limit: int = 50,
        start_key: str | None = None,
        number: str | None = None,
        id: str | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Generator[Cas, None, None]:
        """
        Lists CAS entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of CAS entities to return, by default 50.
        start_key : Optional[str], optional
            The primary key of the first item that this operation will evaluate.
        number : Optional[str], optional
            Fetches list of CAS by CAS number.
        id : Optional[str], optional
            Fetches list of CAS using the CAS Albert ID.
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING.

        Yields
        -------
        Generator
            A Generator of Cas objects.
        """
        params = {"limit": limit, "orderBy": order_by.value}
        if start_key:
            params["startKey"] = start_key
        if number:
            params["number"] = number
        if id:
            params["albertId"] = id
        while True:
            response = self.session.get(self.base_url, params=params)
            cas_data = response.json().get("Items", [])
            if not cas_data or cas_data == []:
                break
            for x in cas_data:
                this_cas = Cas(**x)
                self.cas_cache[this_cas.number] = this_cas
                yield this_cas
            start_key = response.json().get("lastKey")
            if not start_key:
                break
            params["startKey"] = start_key

    def list(
        self,
        *,
        number: str | None = None,
        id: str | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Iterator[Cas]:
        """
        Lists CAS entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of CAS entities to return, by default 50.
        start_key : Optional[str], optional
            The primary key of the first item that this operation will evaluate.
        number : Optional[str], optional
            Fetches list of CAS by CAS number.
        id : Optional[str], optional
            Fetches list of CAS using the CAS Albert ID.
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING.

        Returns
        -------
        Generator
            A generator of Cas objects.
        """
        return self._list_generator(number=number, order_by=order_by, id=id)

    def cas_exists(self, *, number: str, exact_match: bool = True) -> bool:
        """
        Checks if a CAS exists by its number.

        Parameters
        ----------
        number : str
            The number of the CAS to check.
        exact_match : bool, optional
            Whether to match the number exactly, by default True.

        Returns
        -------
        bool
            True if the CAS exists, False otherwise.
        """
        if number in self.cas_cache:
            return True
        cas_list = self.get_by_number(number=number, exact_match=exact_match)
        if cas_list is None:
            return False
        return len(cas_list) > 0

    def create(self, *, cas: str | Cas) -> Cas:
        """
        Creates a new CAS entity.

        Parameters
        ----------
        cas : Union[str, Cas]
            The CAS number or Cas object to create.

        Returns
        -------
        Cas
            The created Cas object.
        """
        if isinstance(cas, str):
            cas = Cas(number=cas)
        if self.cas_exists(cas.number):
            existing_cas = self.cas_cache[cas.number]
            return existing_cas
        else:
            payload = cas.model_dump(by_alias=True, exclude_unset=True)
            response = self.session.post(self.base_url, json=payload)
            cas = Cas(**response.json())
            self.cas_cache[cas.number] = cas
            return cas

    def get_by_id(self, *, cas_id: str) -> Cas:
        """
        Retrieves a CAS by its ID.

        Parameters
        ----------
        cas_id : str
            The ID of the CAS to retrieve.

        Returns
        -------
        Cas
            The Cas object if found, None otherwise.
        """
        url = f"{self.base_url}/{cas_id}"
        response = self.session.get(url)
        cas = Cas(**response.json())
        self.cas_cache[cas.number] = cas
        return cas

    def get_by_number(self, *, number: str, exact_match: bool = True) -> Cas | None:
        """
        Retrieves a CAS by its number.

        Parameters
        ----------
        number : str
            The number of the CAS to retrieve.
        exact_match : bool, optional
            Whether to match the number exactly, by default True.

        Returns
        -------
        Optional[Cas]
            The Cas object if found, None otherwise.
        """
        if number in self.cas_cache:
            return self.cas_cache[number]
        found = self.list(number=number)
        if exact_match:
            for f in found:
                if f.number == number:
                    return [f]
        return next(found, None)

    def delete(self, *, cas_id: str) -> bool:
        """
        Deletes a CAS by its ID.

        Parameters
        ----------
        cas_id : str
            The ID of the CAS to delete.

        Returns
        -------
        bool
            True if the CAS was successfully deleted, False otherwise.
        """
        url = f"{self.base_url}/{cas_id}"
        self.session.delete(url)

        self._remove_from_cache_by_id(cas_id)
        return True

    def update(self, *, updated_object: BaseAlbertModel) -> BaseAlbertModel:
        # Fetch the current object state from the server or database
        current_object = self.get_by_id(updated_object.id)

        # Generate the PATCH payload
        patch_payload = self._generate_patch_payload(
            existing=current_object, updated=updated_object
        )

        url = f"{self.base_url}/{updated_object.id}"
        self.session.patch(url, json=patch_payload)

        updated_cas = self.get_by_id(cas_id=updated_object.id)
        self._remove_from_cache_by_id(updated_object.id)
        self.cas_cache[updated_cas.number] = updated_cas
        return updated_cas
