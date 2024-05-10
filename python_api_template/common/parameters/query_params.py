from pydantic import BaseModel, Field

from ..enums import SortKey, SortOrder


class SortQuery(BaseModel):
    sort_order: SortOrder | None = Field(
        None,
        validation_alias="SortOrder.v1",
        description="Sort order",
    )

    sort_key: SortKey | None = Field(
        None,
        validation_alias="SortKey.v1",
        description="Key to sort by",
    )


class PaginationQuery(BaseModel):
    skip: int | None = Field(
        0,
        validation_alias="Skip.v1",
        description="Number of items to skip",
        ge=0,
        le=1000000,
    )
    limit: int | None = Field(
        100,
        validation_alias="Limit.v1",
        description="Maximum number of items to return",
        ge=0,
        le=100,
    )
