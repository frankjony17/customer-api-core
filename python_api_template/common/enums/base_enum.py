from __future__ import annotations

from enum import Enum
from typing import Any


class BaseEnum(str, Enum):
    """A custom enumeration class with metadata support."""

    def __str__(self):
        """
        Return the string representation of the enum member with the first letter capitalized.
        """
        return self.value.capitalize()

    def _generate_next_value_(name, start, count, last_values) -> str:  # type: ignore
        """
        Uses the uppercase name as the automatic value, rather than an integer

        See https://docs.python.org/3/library/enum.html#using-automatic-values
        for reference
        """
        return name.upper()

    @classmethod
    def as_dict(cls) -> dict[str, Any]:
        member_dict = {role: member.value for role, member in cls.__members__.items()}
        return member_dict

    @classmethod
    def _missing_(cls, value):
        """
        Enum have missing function which can be overridden to make enum case
        insensitive. As per documentation
        https://docs.python.org/3.11/howto/enum.html missing, a lookup function,
        used when a value is not found; may be overridden

        https://stackoverflow.com/a/68311691/295606
        """

        for member in cls:
            if member.value.upper() == value.upper():  # type: ignore
                return member
