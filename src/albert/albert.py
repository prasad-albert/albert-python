import os

from albert.collections.cas import CasCollection
from albert.collections.companies import CompanyCollection
from albert.collections.inventory import InventoryCollection
from albert.collections.locations import LocationCollection
from albert.collections.lots import LotCollection
from albert.collections.projects import ProjectCollection
from albert.collections.roles import RoleCollection
from albert.collections.tags import TagCollection
from albert.collections.un_numbers import UnNumberCollection
from albert.collections.units import UnitCollection
from albert.collections.users import UserCollection
from albert.collections.worksheets import WorksheetCollection
from albert.session import AlbertSession


class Albert:
    """
    Albert is the main client class for interacting with the Albert API.

    Parameters
    ----------
    base_url : str, optional
        The base URL of the Albert API (default is "https://dev.albertinventdev.com").
    token : str, optional
        The token for authentication (default is retrieved from environment variable "ALBERT_TOKEN").
    client_id: str, optional
        The client ID for programmatic authentication (default is retrieved from environment variable "ALBERT_CLIENT_ID").
    client_secret: str, optional
        The client secret key for programmatic authentication (default is retrieved from environment variable "ALBERT_CLIENT_SECRET").

    Attributes
    ----------
    session : AlbertSession
        The session for API requests, with a base URL set.
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
        *,
        base_url: str | None = None,
        token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        self.session = AlbertSession(
            base_url=base_url or os.getenv("ALBERT_BASE_URL") or "https://app.albertinvent.com",
            token=token or os.getenv("ALBERT_TOKEN"),
            client_id=client_id or os.getenv("ALBERT_CLIENT_ID"),
            client_secret=client_secret or os.getenv("ALBERT_CLIENT_SECRET"),
        )

    @property
    def projects(self) -> ProjectCollection:
        return ProjectCollection(session=self.session)

    @property
    def tags(self) -> TagCollection:
        return TagCollection(session=self.session)

    @property
    def inventory(self) -> InventoryCollection:
        return InventoryCollection(session=self.session)

    @property
    def companies(self) -> CompanyCollection:
        return CompanyCollection(session=self.session)

    @property
    def lots(self) -> LotCollection:
        return LotCollection(session=self.session)

    @property
    def units(self) -> UnitCollection:
        return UnitCollection(session=self.session)

    @property
    def cas_numbers(self) -> CasCollection:
        return CasCollection(session=self.session)

    @property
    def un_numbers(self) -> UnNumberCollection:
        return UnNumberCollection(session=self.session)

    @property
    def users(self) -> UserCollection:
        return UserCollection(session=self.session)

    @property
    def locations(self) -> LocationCollection:
        return LocationCollection(session=self.session)

    @property
    def roles(self) -> RoleCollection:
        return RoleCollection(session=self.session)

    @property
    def worksheets(self) -> WorksheetCollection:
        return WorksheetCollection(session=self.session)
