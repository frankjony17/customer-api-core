from datetime import date

from loguru import logger
from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from ..enums.example_status import ExampleStatusEnum


class BaseExampleSchema(BaseModel):
    """
    Some model representing [entity],
     providing details on name, date, number, status, and boolean flag.
    """

    example_name: str = Field(description="The name associated with the entity.")
    example_date: date = Field(
        description="The date associated with the entity in ISO 8601 format (YYYY-MM-DD).",
        alias="example_date",  # Assuming you intended to use 'alias'
    )
    example_number: int | None = Field(
        default=None,
        description="An example number between 1 and 12, inclusive.",
        le=12,
        ge=1,
    )
    example_status: ExampleStatusEnum = Field(
        description="The status of the entity, represented by predefined status values.",
        alias="example_status",
    )
    example_boolean: bool | None = Field(
        default=None,
        description="A boolean flag associated with the entity.",
    )

    # Example of a custom validator
    @field_validator("example_date")
    def validate_date(cls, value: date, info: ValidationInfo):
        # You can add custom validation logic for example_date here
        example_status = info.data.get("example_status")
        logger.info("Validating date", example_status)
        return value
