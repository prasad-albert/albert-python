import requests
from typing import Optional, List, Dict, Union, Any
from albert.exceptions import AlbertAPIError
from albert.base_collection import BaseCollection, OrderBy
from albert.base_entity import BaseAlbertModel
from pydantic import Field, PrivateAttr
from albert.base_entity import Status
from typing import Generator


class Company(BaseAlbertModel):
    """
    Company is a Pydantic model representing a company entity.

    Attributes
    ----------
    name : str
        The name of the company.
    id : Optional[str]
        The Albert ID of the company.
    """

    name: str
    id: Optional[str] = Field(None, alias="albertId")
    _distance: Optional[Status] = PrivateAttr(Status.ACTIVE)

    def __init__(self, **data: Any):
        """
        Initialize a Company instance.

        Parameters
        ----------
        id : Optional[str]
            The Albert ID of the company.
        name : str
            The name of the company.
        """
        super().__init__(**data)
        if "distance" in data:
            self._distance = float(data["distance"])

    @property
    def distance(self):
        return self._distance


class CompanyCollection(BaseCollection):
    """
    CompanyCollection is a collection class for managing company entities.

    Parameters
    ----------
    client : Any
        The Albert client instance.

    Attributes
    ----------
    base_url : str
        The base URL for company API requests.
    company_cache : dict
        A cache of company objects.

    Methods
    -------
    list(limit=50, order_by=OrderBy.DESCENDING, name=None, exact_match=True)
        Lists company entities with optional filters.
    get_company_id(company_name, exact_match=False)
        Retrieves the ID of a company by its name.
    company_exists(name, exact_match=True)
        Checks if a company exists by its name.
    get_by_id(id)
        Retrieves a company by its ID.
    create(company, check_if_exists=True)
        Creates a new company entity.
    rename_company(old_name, new_name)
        Renames an existing company entity.
    """

    _updatable_attributes = {"name"}

    def __init__(self, client):
        """
        Initializes the CompanyCollection with the provided client.

        Parameters
        ----------
        client : Any
            The Albert client instance.
        """
        super().__init__(client=client)
        self.base_url = f"{self.client.base_url}/api/v3/companies"
        self.company_cache = {}

    def _remove_from_cache_by_id(self, id):
        name = None
        for k, v in self.company_cache.items():
            if v.id == id:
                name = k
                break
        if name:
            del self.company_cache[name]

    def _list_generator(
        self,
        limit: int = 50,
        name: Union[str, List[str]] = None,
        exact_match=True,
        start_key: Optional[str] = None,
    ) -> Generator:
        """
        Lists company entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of companies to return, by default 50.
        name : Union[str, None], optional
            The name of the company to filter by, by default None.
        exact_match : bool, optional
            Whether to match the name exactly, by default True.

        Yields
        -------
        Generator
            A generator that yields Company.
        """
        params = {"limit": limit, "dupDetection": "false"}
        if name:
            params["name"] = name if isinstance(name, List) else [name]
            params["exactMatch"] = str(exact_match).lower()
        if start_key:
            params["startKey"] = start_key
        while True:
            companies = requests.get(
                self.base_url, headers=self.client.headers, params=params
            )

            if companies.status_code != 200:
                self.handle_api_error(companies)
                break
            company_data = companies.json().get("Items", [])
            if not company_data or company_data == []:
                break

            for company in company_data:
                this_company = Company(**company)
                self.company_cache[this_company.name] = this_company
                yield this_company
            start_key = companies.json().get("lastKey")
            if not start_key or len(company_data) < limit:
                break
            params["startKey"] = start_key

    def list(
        self, name: Union[str, List[str]] = None, exact_match=False
    ) -> List[Company]:
        """
        Lists company entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of companies to return, by default 50.
        name : Union[str, None], optional
            The name of the company to filter by, by default None.
        exact_match : bool, optional
            Whether to match the name exactly, by default True.

        Returns
        -------
        List[Company]
            A list of Company objects.
        """
        return self._list_generator(name=name, exact_match=exact_match)

    def company_exists(self, name, exact_match=True) -> bool:
        """
        Checks if a company exists by its name.

        Parameters
        ----------
        name : str
            The name of the company to check.
        exact_match : bool, optional
            Whether to match the name exactly, by default True.

        Returns
        -------
        bool
            True if the company exists, False otherwise.
        """
        if name in self.company_cache:
            return True
        companies = self.get_by_name(name=name, exact_match=exact_match)
        if companies:
            return True
        else:
            return False

    def get_by_id(self, id) -> Union[Company, None]:
        """
        Retrieves a company by its ID.

        Parameters
        ----------
        id : str
            The ID of the company to retrieve.

        Returns
        -------
        Union[Company, None]
            The Company object if found, None otherwise.
        """
        url = f"{self.base_url}/{id}"
        response = requests.get(url, headers=self.client.headers)
        if response.status_code != 200:
            self.handle_api_error(response=response)
        company = response.json()
        if response.status_code == 200:
            found_company = Company(**company)
            self.company_cache[found_company.name] = found_company
            return found_company
        elif response.status_code == 404:
            print(f"No company with id {id} found")
            return None
        else:
            self.handle_api_error(response=response)

            return None

    def get_by_name(self, name: str, exact_match: bool = True) -> Union[Company, None]:
        """
        Retrieves a company by its name.

        Parameters
        ----------
        name : str
            The name of the company to retrieve.
        exact_match : bool, optional
            Whether to match the name exactly, by default True.

        Returns
        -------
        Company
            The Company object if found, None otherwise.
        """
        if name in self.company_cache:
            return self.company_cache[name]
        found = self.list(name=name, exact_match=True)
        return next(found, None)

    def create(
        self, company: Union[str, Company], check_if_exists: bool = True
    ) -> Company:
        """
        Creates a new company entity.

        Parameters
        ----------
        company : Union[str, Company]
            The company name or Company object to create.
        check_if_exists : bool, optional
            Whether to check if the company already exists, by default True.

        Returns
        -------
        Company
            The created Company object.
        """
        if isinstance(company, str):
            company = Company(name=company)
        if check_if_exists and self.company_exists(name=company.name):
            company = self.company_cache[company.name]
            print(f"Company {company.name} already exists with id {company.id}.")
            return company

        payload = company.model_dump(by_alias=True, exclude_unset=True)
        response = requests.post(
            self.base_url, headers=self.client.headers, json=payload
        )
        if response.status_code == 201:
            this_company = Company(**response.json())
            self.company_cache[this_company.name] = this_company
            return this_company
        else:
            self.handle_api_error(response=response)
            return None

    def delete(self, id: str) -> bool:
        url = f"{self.base_url}/{id}"
        response = requests.delete(url, headers=self.client.headers)
        if response.status_code == 204:
            self._remove_from_cache_by_id(id)
            return True
        else:
            return self.handle_api_error(response)

    def rename(self, old_name: str, new_name: str) -> Optional[Company]:
        """
        Renames an existing company entity.

        Parameters
        ----------
        old_name : str
            The current name of the company.
        new_name : str
            The new name of the company.

        Returns
        -------
        Optional[Company]
            The renamed Company object if successful, None otherwise.
        """
        company = self.get_by_name(old_name, exact_match=True)
        if not company:
            print(f'Company "{old_name}" not found.')
            return None
        company_id = company.id
        endpoint = f"{self.base_url}/{company_id}"
        payload = {
            "data": [
                {
                    "operation": "update",
                    "attribute": "name",
                    "oldValue": old_name,
                    "newValue": new_name,
                }
            ]
        }
        response = requests.patch(endpoint, headers=self.client.headers, json=payload)
        if response.status_code != 204:
            self.handle_api_error(response=response)
        updated_company = self.get_by_id(company_id)
        self._remove_from_cache_by_id(updated_company.id)
        self.company_cache[updated_company.name] = updated_company
        return updated_company

    def update(self, updated_object: Company) -> Company:
        # Fetch the current object state from the server or database
        current_object = self.get_by_id(updated_object.id)

        # Generate the PATCH payload
        patch_payload = self._generate_patch_payload(
            existing=current_object, updated=updated_object
        )

        url = f"{self.base_url}/{updated_object.id}"
        response = requests.patch(url, json=patch_payload, headers=self.client.headers)
        if response.status_code == 204:
            updated_company = self.get_by_id(cas_id=updated_object.id)
            self._remove_from_cache_by_id(updated_object.id)
            self.company_cache[updated_company.id] = updated_company
            return updated_company
        else:
            return self.handle_api_error(response)
