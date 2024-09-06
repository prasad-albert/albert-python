import logging
from collections.abc import Generator, Iterator

from albert.albert_session import AlbertSession
from albert.collections.base import BaseCollection
from albert.resources.companies import Company


class CompanyCollection(BaseCollection):
    """
    CompanyCollection is a collection class for managing company entities.

    Parameters
    ----------
    session : AlbertSession
        The Albert session instance.

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

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the CompanyCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_url = "/api/v3/companies"
        self.company_cache = {}

    def _remove_from_cache_by_id(self, *, id: str):
        name = None
        for k, v in self.company_cache.items():
            if v.id == id:
                name = k
                break
        if name:
            del self.company_cache[name]

    def _list_generator(
        self,
        *,
        limit: int = 50,
        name: str | list[str] = None,
        exact_match: bool = True,
        start_key: str | None = None,
    ) -> Generator[Company, None, None]:
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
            params["name"] = name if isinstance(name, list) else [name]
            params["exactMatch"] = str(exact_match).lower()
        if start_key:
            params["startKey"] = start_key
        while True:
            response = self.session.get(self.base_url, params=params)

            company_data = response.json().get("Items", [])
            if not company_data or company_data == []:
                break

            for company in company_data:
                this_company = Company(**company)
                self.company_cache[this_company.name] = this_company
                yield this_company
            start_key = response.json().get("lastKey")
            if not start_key or len(company_data) < limit:
                break
            params["startKey"] = start_key

    def list(
        self, *, name: str | list[str] = None, exact_match: bool = False
    ) -> Iterator[Company]:
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
        Iterator[Company]
            A generator that yields Company.
        """
        return self._list_generator(name=name, exact_match=exact_match)

    def company_exists(self, *, name: str, exact_match: bool = True) -> bool:
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

    def get_by_id(self, *, id: str) -> Company | None:
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
        response = self.session.get(url)
        company = response.json()
        found_company = Company(**company)
        self.company_cache[found_company.name] = found_company
        return found_company

    def get_by_name(self, *, name: str, exact_match: bool = True) -> Company | None:
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
        found = self.list(name=name, exact_match=exact_match)
        return next(found, None)

    def create(self, *, company: str | Company, check_if_exists: bool = True) -> Company:
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
            logging.warning(f"Company {company.name} already exists with id {company.id}.")
            return company

        payload = company.model_dump(by_alias=True, exclude_unset=True)
        response = self.session.post(self.base_url, json=payload)
        this_company = Company(**response.json())
        self.company_cache[this_company.name] = this_company
        return this_company

    def delete(self, *, id: str) -> bool:
        url = f"{self.base_url}/{id}"
        response = self.session.delete(url)
        self._remove_from_cache_by_id(id=id)
        return True

    def rename(self, *, old_name: str, new_name: str) -> Company | None:
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
        company = self.get_by_name(name=old_name, exact_match=True)
        if not company:
            logging.error(f'Company "{old_name}" not found.')
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
        response = self.session.patch(endpoint, json=payload)
        updated_company = self.get_by_id(id=company_id)
        self._remove_from_cache_by_id(id=updated_company.id)
        self.company_cache[updated_company.name] = updated_company
        return updated_company

    def update(self, *, updated_object: Company) -> Company:
        # Fetch the current object state from the server or database
        current_object = self.get_by_id(id=updated_object.id)

        # Generate the PATCH payload
        patch_payload = self._generate_patch_payload(
            existing=current_object, updated=updated_object
        )
        url = f"{self.base_url}/{updated_object.id}"
        response = self.session.patch(url, json=patch_payload)
        updated_company = self.get_by_id(cas_id=updated_object.id)
        self._remove_from_cache_by_id(id=updated_object.id)
        self.company_cache[updated_company.id] = updated_company
        return updated_company
