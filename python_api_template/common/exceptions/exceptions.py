from typing import Any

from fastapi import status

from .base_exception import APIError


class BadRequestError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Bad Request"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail, name=name, url=url
        )


class UnauthorizedError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Unauthorized"
        super().__init__(
            detail=detail, status_code=status.HTTP_401_UNAUTHORIZED, name=name, url=url
        )


class ForbiddenError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Forbidden"
        super().__init__(
            detail=detail, status_code=status.HTTP_403_FORBIDDEN, name=name, url=url
        )


class NotFoundError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Not Found"
        super().__init__(
            detail=detail, status_code=status.HTTP_404_NOT_FOUND, name=name, url=url
        )


class MethodNotAllowedError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Method Not Allowed"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            name=name,
            url=url,
        )


class UnprocessableEntityError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Unprocessable Entity"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            name=name,
            url=url,
        )


class TooManyRequestsError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Too Many Requests"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            name=name,
            url=url,
        )


class InternalServerError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Internal Server Error"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            name=name,
            url=url,
        )


class ServiceUnavailableError(APIError):
    """failures in external services or APIs, like a database or a third-party service"""

    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Service Unavailable"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            name=name,
            url=url,
        )


class UniqueConstraintError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Database Unique Constraint"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            name=name,
            url=url,
        )


class ForeignKeyError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Database Foreign Key Violation"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            name=name,
            url=url,
        )


class ORMError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Database or ORM Error"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            name=name,
            url=url,
        )


class PydanticError(APIError):
    def __init__(self, detail: Any = None, url: str | None = None):
        name = "Model Validation Error"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            name=name,
            url=url,
        )
