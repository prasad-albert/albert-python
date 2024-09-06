from collections.abc import Generator, Iterator

from albert.albert_session import AlbertSession
from albert.collections.base import BaseCollection
from albert.resources.locations import Location


class LocationCollection(BaseCollection):
    _updatable_attributes = {"latitude", "longitude", "address", "country", "name"}

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the LocationCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_url = "/api/v3/locations"

    def _list_generator(
        self,
        *,
        limit: int = 50,
        name: list[str] | str = None,
        country: str = None,
        start_key: str = None,
    ) -> Generator[Location, None, None]:
        params = {"limit": limit}
        if name:
            params["name"] = name if isinstance(name, list) else [name]
        if start_key:
            params["startKey"] = start_key
        if country:
            params["country"] = country

        while True:
            response = self.session.get(self.base_url, params=params)
            loc_data = response.json().get("Items", [])
            if not loc_data or loc_data == []:
                break
            for l in loc_data:
                this_loc = Location(**l)
                yield this_loc
            start_key = response.json().get("lastKey")
            if not start_key:
                break
            params["startKey"] = start_key

    def list(
        self, *, name: str | list[str] = None, country: str = None
    ) -> Iterator[Location]:
        return self._list_generator(name=name, country=country)

    def get_by_id(self, *, id: str) -> Location | None:
        """
        Retrieves a location by its ID.

        Parameters
        ----------
        id : str
            The ID of the location to retrieve.

        Returns
        -------
        Union[Location, None]
            The Location object if found, None otherwise.
        """
        url = f"{self.base_url}/{id}"
        response = self.session.get(url)
        loc = response.json()
        found_company = Location(**loc)
        return found_company

    def update(self, *, updated_object: Location) -> Location:
        # Fetch the current object state from the server or database
        current_object = self.get_by_id(updated_object.id)

        # Generate the PATCH payload
        patch_payload = self._generate_patch_payload(
            existing=current_object, updated=updated_object
        )
        url = f"{self.base_url}/{updated_object.id}"
        response = self.session.patch(url, json=patch_payload)
        return self.get_by_id(id=updated_object.id)
