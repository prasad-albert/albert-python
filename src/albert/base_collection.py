import requests
from albert.exceptions import (
    AlbertAPIError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    InternalServerError,
)
from enum import Enum
from typing import List
from albert.base_entity import BaseAlbertModel
import logging


class OrderBy(Enum):
    DESCENDING = "desc"
    ASCENDING = "asc"


class BaseCollection:
    """
    BaseCollection is the base class for all collection classes.

    Parameters
    ----------
    client : Albert
        The Albert client instance.

    Attributes
    ----------
    client : Albert
        The Albert client instance.
    """

    def __init__(self, client: "Albert"):
        self.client = client

    @classmethod
    def handle_api_error(cls, response: requests.Response) -> None:

        error_message = ""
        try:
            response_json = response.json()
            error_details = response_json
            error_message += f": {error_details.get('title', 'Unknown Error')}"
            error_message += f"\n {response.reason}"
        except ValueError:
            response_json = {}
            error_details = {}
            error_message += ": Unknown Error"
        error_message = f"API request failed with status code {response.status_code} \n {response.reason} \n {response_json.get("errors", None)}"
        logging.error(
            f"Failed to perform the request to {response.request.url}. \n {error_message} \n Body sent: {response.request.body}"
        )
        if response.status_code == 400:
            raise BadRequestError(error_message, error_details)
        elif response.status_code == 401:
            raise UnauthorizedError(error_message, error_details)
        elif response.status_code == 403:
            raise ForbiddenError(error_message, error_details)
        elif response.status_code == 404:
            raise NotFoundError(error_message, error_details)
        elif response.status_code == 500:
            raise InternalServerError(error_message, error_details)
        else:
            raise AlbertAPIError(error_message, error_details)
        return None

    # Class property specifying updatable attributes
    _updatable_attributes = {}

    def _generate_patch_payload(
        self, existing: BaseAlbertModel, updated: BaseAlbertModel
    ) -> dict:
        """Generates a payload for PATCH requests based on the changes. This is overriden for some clases with more compex patch formation"""
        payload = {"data": []}
        for attribute in self._updatable_attributes:
            old_value = getattr(existing, attribute, None)
            new_value = getattr(updated, attribute, None)

            # Get the serialization alias name for the attribute, if it exists
            alias = existing.model_fields[attribute].alias or attribute

            if old_value is None and new_value is not None:
                # Add new attribute
                payload["data"].append(
                    {"operation": "add", "attribute": alias, "newValue": new_value}
                )
            elif old_value is not None and new_value != old_value:
                # Update existing attribute
                payload["data"].append(
                    {
                        "operation": "update",
                        "attribute": alias,
                        "oldValue": old_value,
                        "newValue": new_value,
                    }
                )

        return payload
