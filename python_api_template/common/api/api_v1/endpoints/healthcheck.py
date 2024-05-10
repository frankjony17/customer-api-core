from fastapi import APIRouter, HTTPException, status
from loguru import logger


from python_api_template.common.enums.health_check_status import HealthCheckStatus
from python_api_template.common.schemas.health_check_v1 import HealthCheckV1
from python_api_template.common.schemas.problem_details_v1 import ProblemDetailsV1
from python_api_template.dependencies import AsyncSessionDependency, TokenDependency
from python_api_template.internal.db.database import perform_db_healthcheck

router = APIRouter()


@router.get(
    "/",
    responses={
        200: {
            "model": HealthCheckV1,
            "description": "States that this API is healthy, even if with converns.",
        },
        401: {"model": ProblemDetailsV1, "description": "Unauthorized"},
        403: {"model": ProblemDetailsV1, "description": "Forbidden"},
        500: {"model": ProblemDetailsV1, "description": "Internal error"},
    },
    tags=["Common"],
    summary="Health status of this API",
    response_model_by_alias=True,
)
async def get_healthcheck(
    async_session: AsyncSessionDependency,
    token_api_key: TokenDependency,
) -> HealthCheckV1:
    """
    Health status of this API. If It is healthy with degradation, for example
    without a working cache, but properly delivering responses, it should return
    status 200 with response body field `status` of `warn`.
    This is so that simple balancers and gateways keep the service in operation,
    while more advanced ones may reduce the load on the faulty one.
    """

    if not token_api_key.sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ProblemDetailsV1(
                title="Unauthorized",
                detail="Unauthorized",
                status=status.HTTP_401_UNAUTHORIZED,
            ).model_dump(exclude_unset=True),
        )

    if token_api_key.sub == "forbidden":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ProblemDetailsV1(
                title="Forbidden",
                detail="Forbidden",
                status=status.HTTP_403_FORBIDDEN,
            ).model_dump(exclude_unset=True),
        )

    is_db_healthy = await perform_db_healthcheck(async_session)

    if is_db_healthy:
        logger.info("Health check passed.")
        return HealthCheckV1(status=HealthCheckStatus.PASS, output="Service is healthy")

    logger.warning("DB health check failed.")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=ProblemDetailsV1(
            title="DB health check failed",
            detail="DB health check failed",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).model_dump(exclude_unset=True),
    )
