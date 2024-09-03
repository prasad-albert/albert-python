from typing import Optional, List, Any, Union, Generator
from pydantic import Field, PrivateAttr
import requests
from albert.base_collection import BaseCollection, OrderBy
from albert.base_entity import BaseAlbertModel
from enum import Enum


class UnitCategory(Enum):
    """
    UnitCategory is an enumeration of possible unit categories.

    Attributes
    ----------
    LENGTH : str
        Represents length units.
    VOLUME : str
        Represents volume units.
    LIQUID_VOLUME : str
        Represents liquid volume units.
    ANGLES : str
        Represents angle units.
    TIME : str
        Represents time units.
    FREQUENCY : str
        Represents frequency units.
    MASS : str
        Represents mass units.
    CURRENT : str
        Represents electric current units.
    TEMPERATURE : str
        Represents temperature units.
    AMOUNT : str
        Represents amount of substance units.
    LUMINOSITY : str
        Represents luminous intensity units.
    FORCE : str
        Represents force units.
    ENERGY : str
        Represents energy units.
    POWER : str
        Represents power units.
    PRESSURE : str
        Represents pressure units.
    ELECTRICITY_AND_MAGNETISM : str
        Represents electricity and magnetism units.
    OTHER : str
        Represents other units.
    WEIGHT : str
        Represents weight units.
    """

    LENGTH = "Length"
    VOLUME = "Volume"
    LIQUID_VOLUME = "Liquid volume"
    ANGLES = "Angles"
    TIME = "Time"
    FREQUENCY = "Frequency"
    MASS = "Mass"
    CURRENT = "Electric current"
    TEMPERATURE = "Temperature"
    AMOUNT = "Amount of substance"
    LUMINOSITY = "Luminous intensity"
    FORCE = "Force"
    ENERGY = "Energy"
    POWER = "Power"
    PRESSURE = "Pressure"
    ELECTRICITY_AND_MAGNETISM = "Electricity and magnetism"
    OTHER = "Other"
    WEIGHT = "Weight"
    AREA = "Area"
    SURFACE_AREA = "Surface Area"
    BINARY = "Binary"
    CAPACITANCE = "Capacitance"
    SPEED = "Speed"
    ELECTRICAL_CONDUCTIVITY = "Electrical conductivity"
    ELECTRICAL_PERMITTIVITY = "Electrical permitivitty"
    DENSITY = "Density"
    RESISTANCE = "Resistance"


class Unit(BaseAlbertModel):
    """
    Unit is a Pydantic model representing a unit entity.

    Attributes
    ----------
    id : Optional[str]
        The Albert ID of the unit.
    name : str
        The name of the unit.
    symbol : Optional[str]
        The symbol of the unit.
    synonyms : Optional[List[str]]
        The list of synonyms for the unit.
    category : UnitCategory
        The category of the unit.
    verified : Optional[bool]
        Whether the unit is verified.
    status : Optional[Status]
        The status of the unit.
    """

    id: Optional[str] = Field(None, alias="albertId")
    name: str
    symbol: Optional[str] = Field(None)
    synonyms: Optional[List[str]] = Field(default=[], alias="Synonyms")
    category: Optional[UnitCategory] = Field(None)
    _verified: Optional[bool] = PrivateAttr(default=False)

    def __init__(self, **data: Any):
        """
        Initialize a Unit instance.

        Parameters
        ----------
        id : Optional[str]
            The Albert ID of the unit.
        name : str
            The name of the unit.
        symbol : Optional[str]
            The symbol of the unit.
        synonyms : Optional[List[str]]
            The list of synonyms for the unit.
        category : Optional[str]
            The category of the unit.
        verified : Optional[bool]
            Whether the unit is verified.
        status : Optional[str]
            The status of the unit.
        """
        super().__init__(**data)
        if "verified" in data:
            self._verified = bool(data["verified"])

    @property
    def verified(self):
        return self._verified


class UnitCollection(BaseCollection):
    """
    UnitCollection is a collection class for managing unit entities.

    Parameters
    ----------
    client : Any
        The Albert client instance.

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

    def __init__(self, client):
        """
        Initializes the UnitCollection with the provided client.

        Parameters
        ----------
        client : Any
            The Albert client instance.
        """
        super().__init__(client=client)
        self.base_url = f"{self.client.base_url}/api/v3/units"
        self.unit_cache = {}

    def _remove_from_cache_by_id(self, id):
        name = None
        for k, v in self.unit_cache.items():
            if v.id == id:
                name = k
                break
        if name:
            del self.unit_cache[name]

    def create(self, unit: Unit) -> Unit:
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
        if self.unit_exists(unit.name):
            return self.unit_cache[unit.name]
        response = requests.post(
            self.base_url,
            json=unit.model_dump(by_alias=True, exclude_unset=True),
            headers=self.client.headers,
        )
        if response.status_code == 201:
            this_unit = Unit(**response.json())
            self.unit_cache[this_unit.name] = this_unit
            return this_unit
        else:
            return self.handle_api_error(response)

    def get_by_id(self, unit_id: str) -> Unit:
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
        response = requests.get(url, headers=self.client.headers)
        if response.status_code == 200:
            this_unit = Unit(**response.json())
            self.unit_cache[this_unit.name] = this_unit
            return this_unit
        else:
            return self.handle_api_error(response)

    def update(self, updated_unit: Unit) -> Unit:
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
        original_unit = self.get_by_id(unit_id)
        patch_data = self._generate_patch_payload(original_unit, updated_unit)
        url = f"{self.base_url}/{unit_id}"
        response = requests.patch(url, json=patch_data, headers=self.client.headers)
        if response.status_code == 204:
            updated_unit = self.get_by_id(unit_id=unit_id)
            self._remove_from_cache_by_id(unit_id)
            self.unit_cache[updated_unit.name] = updated_unit
            return updated_unit
        else:
            return self.handle_api_error(response)

    def delete(self, unit_id: str) -> bool:
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
        response = requests.delete(url, headers=self.client.headers)
        if response.status_code == 204:
            self._remove_from_cache_by_id(unit_id)
            return True
        else:
            return self.handle_api_error(response)

    def list(
        self,
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
        Generator[Unit]
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
        Generator[Unit]
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
            response = requests.get(
                self.base_url, headers=self.client.headers, params=params
            )
            if response.status_code == 200:
                # found_units = []
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
            else:
                return self.handle_api_error(response)
            params["startKey"] = start_key

    def get_by_name(self, name: str, exact_match: bool = False) -> Optional[Unit]:
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
        found = self.list(name=name, exact_match=True)
        return next(found, None)

    def unit_exists(self, name: str, exact_match: bool = True) -> bool:
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
        if self.get_by_name(name, exact_match):
            return True
        return False
