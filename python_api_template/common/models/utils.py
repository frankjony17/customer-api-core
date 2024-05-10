import re
import uuid
from typing import Annotated

str_3 = Annotated[str, 3]
str_36 = Annotated[str, 36]
str_255 = Annotated[str, 255]

# Default naming convention for all indexes and constraints
# See why this is important and how it would save your time:
# https://alembic.sqlalchemy.org/en/latest/naming.html
CONVENTION = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}


def camel_to_snake(case: str) -> str:
    case = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", case)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", case).lower()


def generate_uuid_str() -> str:
    """
    Generates a unique identifier using Python's built-in uuid library.

    Returns:
        str: A string representation of a version 4 UUID.
    """
    return str(uuid.uuid4())


def generate_uuid() -> uuid.UUID:
    """
    Generates a unique identifier using Python's built-in uuid library.

    Returns:
        str: A string representation of a version 4 UUID.
    """
    return uuid.uuid4()
