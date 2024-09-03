# Note: To complete


class AlbertAPIError(Exception):
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
