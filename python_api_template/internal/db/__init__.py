"""
Data structures

Add models here so Alembic could pick them up.

You may do changes in tables, then execute
`alembic revision --autogenerate --message="Your text"`
and alembic would generate new migration
in migrations/versions folder.
"""

from python_api_template.common.models.base_model import BaseOrmModel
from python_api_template.example.models import ExampleModel
from python_api_template.internal.db.database import sessionmanager, get_async_session

metadata = BaseOrmModel.metadata

__all__ = [
    "BaseOrmModel",
    "ExampleModel",
    "sessionmanager",
    "get_async_session",
    "metadata",
]
