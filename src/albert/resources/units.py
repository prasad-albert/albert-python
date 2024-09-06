from typing import Optional, List, Any
from pydantic import Field, PrivateAttr

from albert.resources.base import BaseAlbertModel
from enum import Enum


class UnitCategory(str, Enum):
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
    def verified(self)->bool:
        return self._verified
