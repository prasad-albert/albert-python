import requests

from albert.utils.logging import logger


class AlbertException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AlbertAPIError(AlbertException):
    """Base class for all API-related errors."""

    def __init__(self, message: str):
        super().__init__(message)


class BadRequestError(AlbertAPIError):
    """Exception raised for a 400 Bad Request response."""


class UnauthorizedError(AlbertAPIError):
    """Exception raised for a 401 Unauthorized response."""


class ForbiddenError(AlbertAPIError):
    """Exception raised for a 403 Forbidden response."""


class NotFoundError(AlbertAPIError):
    """Exception raised for a 404 Not Found response."""


class InternalServerError(AlbertAPIError):
    """Exception raised for a 500 Internal Server Error response."""


def handle_api_error(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        # TODO: Just enable debug logging via requests directly
        logger.debug(
            f"Request to {response.request.url} failed with status {response.status_code}. "
            f"Response: {response.text}"
            f"Body: {response.request.body}"
        )

        try:
            errors = response.json().get("errors")
        except ValueError:
            errors = None

        message = (
            f"{response.request.method} '{response.request.url}' failed with status code "
            f"{response.status_code} ({response.reason})."
        )
        message = f"{message} Errors: {errors}" if errors else message

        # Raise specific exceptions based on status code
        if response.status_code == 400:
            print(response.request.body)
            albert_error = BadRequestError(message)
        elif response.status_code == 401:
            albert_error = UnauthorizedError(message)
        elif response.status_code == 403:
            albert_error = ForbiddenError(message)
        elif response.status_code == 404:
            albert_error = NotFoundError(message)
        elif response.status_code == 500:
            albert_error = InternalServerError(message)
        else:
            albert_error = AlbertAPIError(message)

        raise albert_error from e
