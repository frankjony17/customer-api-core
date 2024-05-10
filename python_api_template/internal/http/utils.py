from pydantic_core import ErrorDetails

from python_api_template.common.schemas.error import Error


def format_validation_errors(errors: list[ErrorDetails]) -> list[Error]:
    formatted_errors: list[Error] = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        field = field if field else None  # type: ignore
        message = error.get("msg", None)
        formatted_errors.append(Error(parameter=field, message=message, type=None))
    return formatted_errors
