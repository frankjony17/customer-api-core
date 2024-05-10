from .base_enum import BaseEnum


class HealthCheckStatus(BaseEnum):
    """
    Indicates whether the service status is acceptable or not.

    - PASS: The service is healthy.
    - FAIL: The service is unhealthy.
    - WARN: The service is healthy, but there are some concerns.
    """

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
