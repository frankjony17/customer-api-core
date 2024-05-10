"""
catch cases where the database schema as defined in migration files and the
schema as defined in SQLAlchemy models have diverged. This might happen if a
change is made in the models but the corresponding migration script is not
created or if a migration script is created but the models are not updated
accordingly.
"""

from typing import Any

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Connection

from python_api_template.internal.db import metadata
from python_api_template.internal.db.database import DatabaseSessionManager


def do_compare_metadata(connection: Connection):
    def include_name(name: str, type_: str, parent_names: dict[str, Any]) -> bool:
        """Filter only current sql schema tables"""
        if type_ == "schema":
            return name in ["template_core"]
        else:
            return True

    context = MigrationContext.configure(
        connection,
        opts={
            "compare_type": True,
            "include_schemas": True,
            "include_name": include_name,
            "version_table_schema": "template_core",
        },
    )
    return compare_metadata(context, metadata)


async def test_migrations_in_sync_with_models(
    sessionmanager_for_tests: DatabaseSessionManager,
):
    async with sessionmanager_for_tests.connect() as connection:
        diff = await connection.run_sync(do_compare_metadata)
        assert not diff
