import os
from albert.albert_session import AlbertSession
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
try:
    import tomllib  # Python 3.11 and later
except ModuleNotFoundError:
    import tomli as tomllib  # Python 3.10 and earlier

def get_version_from_pyproject():
    # Define the path to your pyproject.toml file
    pyproject_path = os.path.join(os.path.dirname(__file__), "..", "..","pyproject.toml")

    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    # Access the version from the parsed TOML data
    version = pyproject_data["project"]["version"]
    return version

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
        base_url: str = "https://dev.albertinventdev.com",
        bearer_token: str = os.getenv("ALBERT_BEARER_TOKEN"),
    ):
        self.bearer_token = bearer_token
        self.session = AlbertSession(base_url=base_url)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": f"albert-SDK V.{get_version_from_pyproject()}",
        })

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
