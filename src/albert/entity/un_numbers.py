from albert.base_entity import BaseAlbertModel
from albert.base_collection import BaseCollection
from pydantic import Field
import requests
from typing import List, Optional, Generator, Union


class UnNumber(BaseAlbertModel):
    id: str = Field(alias="albertId")
    storage_class_name: str = Field(alias="storageClassName")
    shipping_description: str = Field(alias="shippingDescription")
    storage_class_number: str = Field(alias="storageClassNumber")
    un_number: str = Field(alias="unNumber")
    un_classification: str = Field(alias="unClassification")


class UnNumberCollection(BaseCollection):
    """
    UnNumberCollection is a collection class for managing UN Numbers.

    Note
    ----
    Creating UN Numbers is not supported via the SDK, as UN Numbers are highly controlled by Albert.
    """

    def __init__(self, session):
        super().__init__(session=session)
        self.base_url = "/api/v3/unnumbers"

    def create(self) -> None:
        """
        This method is not implemented as UN Numbers cannot be created through the SDK.
        """
        raise NotImplementedError()

    def get_by_id(self, lot_id: str) -> Union[UnNumber, None]:
        url = f"{self.base_url}/{lot_id}"
        response = self.session.get(url)
        if response.status_code != 200:
            return self.handle_api_error(response)
        return UnNumber(**response.json())

    def _list_generator(
        self,
        name: str = None,
        start_key: Optional[str] = None,
        exact_match: Optional[bool] = None,
    ) -> Generator:
        params = {}
        if start_key:
            params["startKey"] = start_key
        if name:
            params["name"] = name
            if exact_match:
                params["exactMatch"] = str(exact_match).lower()
        while True:
            response = self.session.get(
                self.base_url, params=params
            )
            if response.status_code == 200:
                un_numbers = response.json().get("Items", [])
                if not un_numbers or un_numbers == []:
                    break
                for x in un_numbers:
                    yield UnNumber(**x)
                start_key = response.json().get("lastKey")
                if not start_key:
                    break
                params["startKey"] = start_key
            else:
                self.handle_api_error(response)
                break

    def list(
        self,
        name: str = None,
        exact_match: Optional[bool] = None,
    ) -> Generator:
        return self._list_generator(name=name, exact_match=exact_match)

    def get_by_name(self, name: str) -> UnNumber:
        found = self.list(exact_match=True, name=name)
        return next(found, None)
