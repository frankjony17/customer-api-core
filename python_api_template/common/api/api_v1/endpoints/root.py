from fastapi import APIRouter

from python_api_template.common.schemas.problem_details_v1 import ProblemDetailsV1

router = APIRouter()


@router.get(
    "/",
    responses={
        200: {
            "description": "Welcome to the FastAPI Template API. "
            "For more information, read the documentation in /docs or /redoc"
        },
        400: {"model": ProblemDetailsV1, "description": "Bad Request"},
        401: {"model": ProblemDetailsV1, "description": "Unauthorized"},
        403: {"model": ProblemDetailsV1, "description": "Forbidden"},
        404: {"model": ProblemDetailsV1, "description": "Not found"},
        406: {"model": ProblemDetailsV1, "description": "Not acceptable"},
        429: {"model": ProblemDetailsV1, "description": "Too many requests"},
        500: {"model": ProblemDetailsV1, "description": "Internal error"},
    },
    tags=["Common"],
    summary="Home page for this API",
    response_model_by_alias=True,
    include_in_schema=False,
)
async def start_welcome():
    """Welcome to the sqlalchemy events"""
    return (
        "Welcome to the FastAPI Template API."
        " For more information, read the documentation in /docs or /redoc"
    )
