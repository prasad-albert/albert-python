from typing import Optional, List, Union, Generator
from albert.collections.base_collection import BaseCollection, OrderBy
from albert.resources.units import Unit, UnitCategory


class UnitCollection(BaseCollection):
    """
    UnitCollection is a collection class for managing unit entities.

    Parameters
    ----------
    session : AlbertSession
        The Albert session instance.

    Attributes
    ----------
    base_url : str
        The base URL for unit API requests.

    Methods
    -------
    create(unit) -> Unit
        Creates a new unit entity.
    get_by_id(unit_id) -> Unit
        Retrieves a unit by its ID.
    update(unit_id, patch_data) -> bool
        Updates a unit entity by its ID.
    delete(unit_id) -> bool
        Deletes a unit by its ID.
    list(limit=50, name=None, category=None, order_by=OrderBy.DESCENDING, exact_match=False, start_key=None) -> List[Unit]
        Lists unit entities with optional filters.
    get_by_name(name, exact_match=False) -> Unit
        Retrieves a unit by its name.
    unit_exists(name, exact_match=True) -> bool
        Checks if a unit exists by its name.
    """

    _updatable_attributes = {"symbol", "synonyms", "category"}

    def __init__(self, *, session):
        """
        Initializes the UnitCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_url = "/api/v3/units"
        self.unit_cache = {}

    def _remove_from_cache_by_id(self, *, id):
        name = None
        for k, v in self.unit_cache.items():
            if v.id == id:
                name = k
                break
        if name:
            del self.unit_cache[name]

    def create(self, *, unit: Unit) -> Unit:
        """
        Creates a new unit entity.

        Parameters
        ----------
        unit : Unit
            The unit object to create.

        Returns
        -------
        Unit
            The created Unit object.
        """
        if self.unit_exists(name =unit.name):
            return self.unit_cache[unit.name]
        response = self.session.post(
            self.base_url, json=unit.model_dump(by_alias=True, exclude_unset=True)
        )
        this_unit = Unit(**response.json())
        self.unit_cache[this_unit.name] = this_unit
        return this_unit

    def get_by_id(self, *, unit_id: str) -> Unit:
        """
        Retrieves a unit by its ID.

        Parameters
        ----------
        unit_id : str
            The ID of the unit to retrieve.

        Returns
        -------
        Unit
            The Unit object if found, None otherwise.
        """
        url = f"{self.base_url}/{unit_id}"
        response = self.session.get(url)
        this_unit = Unit(**response.json())
        self.unit_cache[this_unit.name] = this_unit
        return this_unit

    def update(self,*, updated_unit: Unit) -> Unit:
        """
        Updates a unit entity by its ID.

        Parameters
        ----------
        updated_unit : Unit
            The updated Unit object.

        Returns
        -------
        Unit
            Returns the updated Unit
        """
        unit_id = updated_unit.id
        original_unit = self.get_by_id(unit_id=unit_id)
        patch_data = self._generate_patch_payload(
            existing=original_unit, updated=updated_unit
        )
        url = f"{self.base_url}/{unit_id}"
        response = self.session.patch(url, json=patch_data)
        updated_unit = self.get_by_id(unit_id=unit_id)
        self._remove_from_cache_by_id(id=unit_id)
        self.unit_cache[updated_unit.name] = updated_unit
        return updated_unit

    def delete(self, *, unit_id: str) -> bool:
        """
        Deletes a unit by its ID.

        Parameters
        ----------
        unit_id : str
            The ID of the unit to delete.

        Returns
        -------
        bool
            True if the unit was successfully deleted, False otherwise.
        """
        url = f"{self.base_url}/{unit_id}"
        response = self.session.delete(url)
        self._remove_from_cache_by_id(id=unit_id)
        return True

    def list(
        self,
        *,
        name: Optional[Union[str, List[str]]] = None,
        category: Optional[UnitCategory] = None,
        order_by: OrderBy = OrderBy.DESCENDING,
        exact_match: bool = False,
        verified: Optional[bool] = None,
    ) -> Generator[Unit, None, None]:
        """
        Lists unit entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of units to return, by default 50.
        name : Optional[str], optional
            The name of the unit to filter by, by default None.
        category : Optional[UnitCategory], optional
            The category of the unit to filter by, by default None.
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING.
        exact_match : bool, optional
            Whether to match the name exactly, by default False.
        start_key : Optional[str], optional
            The starting point for the next set of results, by default None.

        Returns
        -------
        Generator
            A generator of Unit objects.
        """
        return self._list_generator(
            category=category,
            verified=verified,
            order_by=order_by,
            name=name,
            exact_match=exact_match,
        )

    def _list_generator(
        self,
        *,
        name: Optional[Union[str, List[str]]] = None,
        category: Optional[UnitCategory] = None,
        order_by: OrderBy = OrderBy.DESCENDING,
        exact_match: bool = False,
        start_key: Optional[str] = None,
        verified: Optional[bool] = None,
    ) -> Generator[Unit, None, None]:
        """
        Lists unit entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of units to return, by default 50.
        name : Optional[str], optional
            The name of the unit to filter by, by default None.
        category : Optional[UnitCategory], optional
            The category of the unit to filter by, by default None.
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING.
        exact_match : bool, optional
            Whether to match the name exactly, by default False.
        start_key : Optional[str], optional
            The starting point for the next set of results, by default None.

        Returns
        -------
        Generator
            A generator of Unit objects.
        """
        params = {
            "orderBy": order_by.value,
            "exactMatch": str(exact_match).lower(),
        }
        if name:
            params["name"] = name if isinstance(name, list) else [name]
        if category:
            params["category"] = category.value
        if start_key:
            params["startKey"] = start_key
        if not verified is None:
            params["verified"] = str(verified).lower()
        while True:
            response = self.session.get(self.base_url, params=params)
            units = response.json().get("Items", [])
            if not units or units == []:
                break
            for u in units:
                this_unit = Unit(**u)
                self.unit_cache[this_unit.name] = this_unit
                yield this_unit
            start_key = response.json().get("lastKey")
            if not start_key:
                break
            params["startKey"] = start_key

    def get_by_name(self, *, name: str, exact_match: bool = False) -> Optional[Unit]:
        """
        Retrieves a unit by its name.

        Parameters
        ----------
        name : str
            The name of the unit to retrieve.
        exact_match : bool, optional
            Whether to match the name exactly, by default False.

        Returns
        -------
        Optional[Unit]
            The Unit object if found, None otherwise.
        """
        found = self.list(name=name, exact_match=exact_match)
        return next(found, None)

    def unit_exists(self,*, name: str, exact_match: bool = True) -> bool:
        """
        Checks if a unit exists by its name.

        Parameters
        ----------
        name : str
            The name of the unit to check.
        exact_match : bool, optional
            Whether to match the name exactly, by default True.

        Returns
        -------
        bool
            True if the unit exists, False otherwise.
        """
        if self.get_by_name(name=name, exact_match=exact_match):
            return True
        return False
