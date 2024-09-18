import logging

import requests


class AlbertException(Exception):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details


def handle_api_error(response: requests.Response) -> None:
    try:
        # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()
    except requests.HTTPError as e:
        # Log the initial error with status code and reason
        error_message = (
            f"API request failed with status code {response.status_code}: {response.reason}"
        )

        try:
            # Attempt to extract additional error details from the response JSON, if available
            response_json = response.json()
            error_details = response_json.get("errors", {})
            error_message += f"\nDetails: {response_json.get('title', 'Unknown Error')}"
        except ValueError:
            # Handle case where the response body is not JSON
            error_details = {}
            error_message += "\nDetails: No JSON body found in the response."

        # Log the complete error message including URL and request body
        logging.error(
            f"Failed to perform the request to {response.request.url}. \n{error_message}\nBody sent: {response.request.body}"
        )

        # Raise specific exceptions based on status code
        if response.status_code == 400:
            raise BadRequestError(error_message, error_details) from e
        elif response.status_code == 401:
            raise UnauthorizedError(error_message, error_details) from e
        elif response.status_code == 403:
            raise ForbiddenError(error_message, error_details) from e
        elif response.status_code == 404:
            raise NotFoundError(error_message, error_details) from e
        elif response.status_code == 500:
            raise InternalServerError(error_message, error_details) from e
        else:
            raise AlbertAPIError(error_message, error_details) from e


# Custom Exception classes for API errors


class AlbertAPIError(AlbertException):
    """Base class for all API-related errors."""

    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details


class BadRequestError(AlbertAPIError):
    """Exception raised for a 400 Bad Request response."""

    pass


class UnauthorizedError(AlbertAPIError):
    """Exception raised for a 401 Unauthorized response."""

    pass


class ForbiddenError(AlbertAPIError):
    """Exception raised for a 403 Forbidden response."""

    pass


class NotFoundError(AlbertAPIError):
    """Exception raised for a 404 Not Found response."""

    pass


class InternalServerError(AlbertAPIError):
    """Exception raised for a 500 Internal Server Error response."""

    pass
