from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.utils import is_body_allowed_for_status_code
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from python_api_template.common.schemas.validation_problem_details_v1 import (
    ValidationProblemDetailsV1,
)
from python_api_template.internal.http.utils import format_validation_errors


async def http_exception_handler(
    _: Request, exc: StarletteHTTPException
) -> Response | ORJSONResponse:
    headers = getattr(exc, "headers", None)
    logger.debug("Handling HTTPException")
    logger.debug(exc.detail)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)
    return ORJSONResponse(
        {"detail": exc.detail}, status_code=exc.status_code, headers=headers
    )


async def request_validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> ORJSONResponse | ValidationProblemDetailsV1 | JSONResponse:
    logger.debug("Handling RequestValidationError\n")
    formatted_errors = format_validation_errors(exc.errors())
    validation_details = ValidationProblemDetailsV1(
        title="Validation Error",
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Invalid query parameters combination",
        validation_errors=formatted_errors,
    )

    logger.error(validation_details.model_dump_json(exclude_unset=True, indent=2))
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": jsonable_encoder(validation_details)},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Helper function to setup exception handlers for app.
    Use during app startup as follows:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            setup_exception_handlers(app)

    :param app: app object, instance of FastAPI
    :return: None
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(
        RequestValidationError, request_validation_exception_handler
    )
