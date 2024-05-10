from pydantic import BaseModel, Field

from ..enums import HealthCheckStatus


class HealthCheckV1(BaseModel):
    """
    Health Check for HTTP APIs.

    Attributes:
        status (HealthCheckStatus): Indicates whether the service status is
        acceptable or not.
        - PASS: The service is healthy
        - FAIL: The service is unhealthy
        - WARN: The service is healthy but has some concerns

        output (str, optional): Output message of the health check
    """

    status: HealthCheckStatus = Field(
        default=...,
        alias="status",
        description="Indicates whether the service status is acceptable or not",
    )

    output: str | None = Field(
        default=None,
        alias="output",
        min_length=1,
        max_length=255,
        pattern=r"^\S(.*\S)?$",
        description="Output message of the health check",
    )
