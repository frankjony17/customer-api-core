from pydantic import BaseModel, Field


class RateLimitHeaders(BaseModel):
    rate_limit_limit: int = Field(..., alias="RateLimit-Limit.v1")
    rate_limit_remaining: int = Field(..., alias="RateLimit-Remaining.v1")
