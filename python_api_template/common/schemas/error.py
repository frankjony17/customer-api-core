from pydantic import BaseModel, Field, HttpUrl


class Error(BaseModel):
    """
    A model for representing a validation error.

    Attributes:
        parameter (str): The name of the parameter that failed validation
        type (HttpUrl): A Uri reference that identifies the specific occurrence
        of the problem. It may or may not yield further information if
        dereferenced.
        message (str): The validation error message.
    """

    parameter: str | None = Field(
        None,
        alias="parameter",
        description="The name of the parameter that failed validation.",
        min_length=1,
        max_length=64,
        pattern=r"^\S(.*\S)?$",
    )

    message: str | None = Field(
        None,
        alias="message",
        description="The validation error message.",
        min_length=1,
        max_length=255,
        pattern=r"^\S(.*\S)?$",
    )

    type: HttpUrl | None = Field(
        None,
        alias="type",
        description="A Uri reference that identifies the specific occurrence of the problem. "
        "It may or may not yield further information if dereferenced.",  # noqa: E501
    )
