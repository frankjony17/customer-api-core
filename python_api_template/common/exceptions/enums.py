from ..enums.base_enum import BaseEnum


class RequestMethod(BaseEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"


class Severity(BaseEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
