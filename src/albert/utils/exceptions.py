from http.client import responses
from typing import Any

import requests

from albert.utils.logging import logger


class AlbertException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class AlbertAPIError(AlbertException):
    """Base class for all API-related errors."""

    def __init__(self, status_code: int, error: dict[str, Any] | None = None):
        message = f"API request failed with status code {status_code}: {responses[status_code]}"
        if error is not None:
            if url := error.get("url"):
                message = f"{message}\nPath: {url}"
            if messages := error.get("errors"):
                message = f"{message}\nDetails: {messages}"
        super().__init__(message)


class BadRequestError(AlbertAPIError):
    """Exception raised for a 400 Bad Request response."""

    def __init__(self, error: dict[str, Any] | None = None):
        super().__init__(400, error)


class UnauthorizedError(AlbertAPIError):
    """Exception raised for a 401 Unauthorized response."""

    def __init__(self, error: dict[str, Any] | None = None):
        super().__init__(401, error)


class ForbiddenError(AlbertAPIError):
    """Exception raised for a 403 Forbidden response."""

    def __init__(self, error: dict[str, Any] | None = None):
        super().__init__(403, error)


class NotFoundError(AlbertAPIError):
    """Exception raised for a 404 Not Found response."""

    def __init__(self, error: dict[str, Any] | None = None):
        super().__init__(404, error)


class InternalServerError(AlbertAPIError):
    """Exception raised for a 500 Internal Server Error response."""

    def __init__(self, error: dict[str, Any] | None = None):
        super().__init__(500, error)


def handle_api_error(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        try:
            # TODO: Parse the error as a structured type since the shape is always the same
            error_json = response.json()
        except ValueError:
            error_json = None

        logger.debug(
            f"Request to {response.request.url} failed with status {response.status_code}. "
            f"Response: {response.text}"
            f"Body: {response.request.body}"
        )

        # Raise specific exceptions based on status code
        if response.status_code == 400:
            albert_error = BadRequestError(error_json)
        elif response.status_code == 401:
            albert_error = UnauthorizedError(error_json)
        elif response.status_code == 403:
            albert_error = ForbiddenError(error_json)
        elif response.status_code == 404:
            albert_error = NotFoundError(error_json)
        elif response.status_code == 500:
            albert_error = InternalServerError(error_json)
        else:
            albert_error = AlbertAPIError(response.status_code, error_json)

        raise albert_error from e
