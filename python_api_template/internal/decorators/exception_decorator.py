from typing import Any, Awaitable, Callable, TypeVar
from functools import wraps
from loguru import logger
from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import NoResultFound
from fastapi import status

from python_api_template.common.exceptions.exceptions import (
    NotFoundError,
    PydanticError,
)
from python_api_template.common.schemas.validation_problem_details_v1 import (
    ValidationProblemDetailsV1,
)
from .utils.bind_arguments import bind_arguments
from .utils.format_validation_errors import format_validation_errors


T = TypeVar("T")


class ExceptionsWrapperConfig(BaseModel):
    enabled: bool = True
    log_exceptions: bool = True


def exceptions_wrapper(config: ExceptionsWrapperConfig = ExceptionsWrapperConfig()):
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapped_func(*args: Any, **kwargs: Any) -> T:
            """
            The wrapper function that is returned by the decorator. It captures the exceptions
            thrown by `func` and raises more specific exceptions instead.

            Args:
                *args: Positional arguments to be passed to `func`.
                **kwargs: Keyword arguments to be passed to `func`.

            Returns:
                Any: The result of the `func` function if it completes successfully.
            """
            try:
                return await func(*args, **kwargs)
            except NoResultFound as exc:
                kwargs_dict = await bind_arguments(func, *args, **kwargs)
                logger.debug(kwargs_dict)
                raise NotFoundError(detail=kwargs_dict) from exc
            except ValidationError as exc:
                formatted_errors = format_validation_errors(exc.errors())
                validation_details = ValidationProblemDetailsV1(
                    title="Validation Error",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Invalid query parameters combination",
                    validation_errors=formatted_errors,
                )
                raise PydanticError(
                    detail=validation_details,
                ) from exc

        return wrapped_func

    return decorator
