from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from .base_example import BaseExampleSchema


class GetExampleSchema(BaseExampleSchema):
    """
    Example model with all its attributes

    Attributes:
        -----------
    """

    id: UUID | None = Field(
        default=None,
        alias="id",
        description="The unique identifier of the 'example'.",
    )
    created_at: datetime | None = Field(
        default=None,
        alias="created_at",
        description="Date and time when the 'example' "
        "was created in ISO 8601 format (YYYY-MM-DDThh:mm:ss.sssZ)",
    )
    updated_at: datetime | None = Field(
        default=None,
        alias="updated_at",
        description="Date and time when the 'example' "
        "was last updated in ISO 8601 format (YYYY-MM-DDThh:mm:ss.sssZ)",
    )

    model_config = ConfigDict(from_attributes=True)
