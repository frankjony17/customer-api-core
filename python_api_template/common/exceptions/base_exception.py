from typing import Any

from fastapi import HTTPException
from loguru import logger

from .enums import Severity

LOG_METHODS = {
    Severity.ERROR: logger.error,
    Severity.WARNING: logger.warning,
    Severity.INFO: logger.info,
    Severity.DEBUG: logger.debug,
}


def add_url_to_detail(detail: str, url: str) -> str:
    return f"{detail} URL=[{url}]"


class APIError(HTTPException):
    """
    APIError class represents a custom HTTP exception that extends
    the base HTTPException class.

    Attributes:
        status_code (int): The HTTP status code associated with the exception.
        detail (Any): Any data to be sent to the client in the `detail` key
        of the JSON response.
        severity (str): The severity level of the exception. Defaults to
        "error".

    Methods:
        __init__(self, status_code: int, detail: Any, severity: str = "error"):
            Initializes a new instance of the BaseHTTPException class.
            Sets the status_code, detail, and severity attributes.
            Logs the exception details based on the severity level.
            Calls the base class constructor with the status_code and detail.

    Note:
        This class is designed to be used as a base class for specific HTTP
        exception types.
    """

    def __init__(
        self,
        status_code: int,
        detail: Any,
        name: str = "API Error",
        url: str | None = None,
        severity: Severity = Severity.ERROR,
    ) -> None:
        self.name = name
        self.url = url
        self.severity = severity
        super().__init__(status_code=status_code, detail=detail)
