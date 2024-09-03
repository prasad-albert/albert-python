from albert.base_entity import BaseAlbertModel
from albert.base_collection import BaseCollection
from pydantic import Field
from typing import Union, List, Optional
import requests


class Location(BaseAlbertModel):
    name: str
    id: Optional[str] = Field(None, alias="albertId")
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)
    address: Optional[str] = Field(None)
    country: Optional[str] = Field(None)


class LocationCollection(BaseCollection):
    _updatable_attributes = {"latitude", "longitude", "address", "country", "name"}

    def __init__(self, client):
        """
        Initializes the LocationCollection with the provided client.

        Parameters
        ----------
        client : Any
            The Albert client instance.
        """
        super().__init__(client=client)
        self.base_url = f"{self.client.base_url}/api/v3/locations"

    def _list_generator(
        self,
        limit: int = 50,
        name: Union[List[str], str] = None,
        country: str = None,
        start_key: str = None,
    ):
        params = {"limit": limit}
        if name:
            params["name"] = name if isinstance(name, list) else [name]
        if start_key:
            params["startKey"] = start_key
        if country:
            params["country"] = country

        while True:
            response = requests.get(
                self.base_url, headers=self.client.headers, params=params
            )
            if response.status_code != 200:
                self.handle_api_error(response=response)
                break
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

    def list(self, name: Union[str, List[str]] = None, country: str = None):
        return self._list_generator(name=name, country=country)

    def get_by_id(self, id) -> Union[Location, None]:
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
        response = requests.get(url, headers=self.client.headers)
        if response.status_code != 200:
            self.handle_api_error(response=response)
        loc = response.json()
        found_company = Location(**loc)
        return found_company

    def update(self, updated_object: Location) -> Location:
        # Fetch the current object state from the server or database
        current_object = self.get_by_id(updated_object.id)

        # Generate the PATCH payload
        patch_payload = self._generate_patch_payload(
            existing=current_object, updated=updated_object
        )
        url = f"{self.base_url}/{updated_object.id}"
        response = requests.patch(url, json=patch_payload, headers=self.client.headers)
        if response.status_code == 204:
            return self.get_by_id(id=updated_object.id)
        else:
            return self.handle_api_error(response)
