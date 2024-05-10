from .base_enum import BaseEnum


class SortOrder(BaseEnum):
    """
    Order of the items listed

    - asc: Ascending order
    - desc: Descending order
    """

    ASC = "asc"
    DESC = "desc"


class SortKey(BaseEnum):
    """
    Key to sort by

    - created_at: Created at
    - updated_at: Updated at
    """

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
