from datetime import date, datetime

from pydantic import ConfigDict, field_validator

from python_api_template.example.schemas.base_example import BaseExampleSchema


class CreateExampleSchema(BaseExampleSchema):
    @staticmethod
    def parse_date(value: str | None):
        if not value:
            return None
        try:
            if isinstance(value, datetime):
                return value
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            pass
        raise ValueError("Invalid date format")

    @field_validator("example_date", mode="before")
    @classmethod
    def parse_period_start_date(cls, value: str | None):
        return cls.parse_date(value)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "example_name": "Some name",
                    "example_date": str(date.today()),
                    "example_number": 14,
                    "example_status": "A",
                    "example_boolean": True,
                }
            ]
        }
    )
