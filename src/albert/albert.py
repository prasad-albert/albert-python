import os

from albert.projects import ProjectCollection
from albert.inventory import InventoryCollection
from albert.lots import LotCollection

from albert.entity.companies import CompanyCollection
from albert.entity.tags import TagCollection
from albert.entity.units import UnitCollection
from albert.entity.cas import CasCollection
from albert.entity.un_numbers import UnNumberCollection
from albert.entity.users import UserCollection
from albert.entity.locations import LocationCollection
from albert.entity.roles import RoleCollection
from albert.worksheets import WorksheetCollection
import albert


class Albert:
    """
    Albert is the main client class for interacting with the Albert API.

    Parameters
    ----------
    base_url : str, optional
        The base URL of the Albert API (default is "https://dev.albertinventdev.com").
    bearer_token : str, optional
        The bearer token for authentication (default is retrieved from environment variable "ALBERT_BEARER_TOKEN").

    Attributes
    ----------
    base_url : str
        The base URL of the Albert API.
    bearer_token : str
        The bearer token for authentication.
    headers : dict
        The headers for API requests.
    projects : ProjectCollection
        The project collection instance.
    tags : TagCollection
        The tag collection instance.
    inventory : InventoryCollection
        The inventory collection instance.
    companies : CompanyCollection
        The company collection instance.
    """

    def __init__(
        self,
        base_url: str = "https://dev.albertinventdev.com",
        bearer_token: str = os.getenv("ALBERT_BEARER_TOKEN"),
    ):
        self.base_url = base_url
        self.bearer_token = bearer_token
        self.headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": f"albert-SDK V.{albert.__version__}",
        }

    @property
    def projects(self) -> ProjectCollection:
        return ProjectCollection(client=self)

    @property
    def tags(self) -> TagCollection:
        return TagCollection(client=self)

    @property
    def inventory(self) -> InventoryCollection:
        return InventoryCollection(client=self)

    @property
    def companies(self) -> CompanyCollection:
        return CompanyCollection(client=self)

    @property
    def lots(self) -> LotCollection:
        return LotCollection(client=self)

    @property
    def units(self) -> UnitCollection:
        return UnitCollection(client=self)

    @property
    def cas_numbers(self) -> CasCollection:
        return CasCollection(client=self)

    @property
    def un_numbers(self) -> UnNumberCollection:
        return UnNumberCollection(client=self)

    @property
    def users(self) -> UserCollection:
        return UserCollection(client=self)

    @property
    def locations(self) -> LocationCollection:
        return LocationCollection(client=self)

    @property
    def roles(self) -> RoleCollection:
        return RoleCollection(client=self)

    @property
    def worksheets(self) -> WorksheetCollection:
        return WorksheetCollection(client=self)
