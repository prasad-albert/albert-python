import os
from albert.albert_session import AlbertSession
from albert.collections.projects import ProjectCollection
from albert.collections.inventory import InventoryCollection
from albert.collections.lots import LotCollection
from albert.collections.companies import CompanyCollection
from albert.collections.tags import TagCollection
from albert.collections.units import UnitCollection
from albert.collections.cas import CasCollection
from albert.collections.un_numbers import UnNumberCollection
from albert.collections.users import UserCollection
from albert.collections.locations import LocationCollection
from albert.collections.roles import RoleCollection
from albert.collections.worksheets import WorksheetCollection
import re

def get_version_from_pyproject():
    # Define the path to your __version__.py file
    version_file_path = os.path.join(
        os.path.dirname(__file__), "..", "__version__.py"
    )

    # Read the content of __version__.py
    with open(version_file_path, "r") as f:
        version_file_content = f.read()

    # Use a regular expression to find the version string
    version_match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', version_file_content, re.MULTILINE)

    if version_match:
        return version_match.group(1)
    else:
        raise ValueError("Version not found in __version__.py")


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
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.bearer_token}",
                "User-Agent": f"albert-SDK V.{get_version_from_pyproject()}",
            }
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
