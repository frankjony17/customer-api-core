import asyncio
import traceback
from contextvars import ContextVar
from typing import Any
from enum import Enum

from loguru import logger
from sqlalchemy import Connection, create_engine, engine_from_config, pool, text
from sqlalchemy.schema import SchemaItem
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory


from python_api_template.internal.config.logger import set_up_logger
from python_api_template.internal.config.settings import global_settings
from python_api_template.internal.db import BaseOrmModel

from logging.config import fileConfig


ctx_var: ContextVar[dict[str, Any]] = ContextVar("ctx_var")


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    set_up_logger()


# Interpret the config file for Python logging.
# This line sets up loggers basically.
db_url = config.get_main_option("sqlalchemy.url") or global_settings.app.db_url
config.set_main_option("sqlalchemy.url", db_url)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = BaseOrmModel.metadata

DB_SCHEMA = global_settings.postgres.db_schema
EXCLUDE_TABLES = global_settings.postgres.exclude_tables


class SQLAlchemyObjTypeEnum(Enum):
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    INDEX = "index"
    UNIQUE_CONSTRAINT = "unique_constraint"
    FOREIGN_KEY_CONSTRAINT = "foreign_key_constraint"


def filter_db_objects(
    object: SchemaItem,
    name: str | None,
    type_: str,
    flag: bool,
    related_object: SchemaItem | None,
) -> bool:
    """
    Filter database objects based on specific criteria.
    Ignores tables created by other applications or certain database extensions.
    """
    if type_ == SQLAlchemyObjTypeEnum.TABLE:
        return name not in EXCLUDE_TABLES

    if (
        type_ == SQLAlchemyObjTypeEnum.INDEX
        and name is not None
        and name.startswith("idx")
        and name.endswith("geom")
    ):
        return False

    return True


def log_migration_details(context):
    # Check if 'destination_rev' is available in the context
    if "destination_rev" not in context._proxy.context_opts:
        logger.info(
            "[++] 'destination_rev' not available in the context, skipping log."
        )
        return
    script = ScriptDirectory.from_config(context.config)
    rev = context.get_revision_argument()
    if rev is None:
        logger.info("[++] No migration required")
        return
    # Special handling for "-1" to indicate moving back to the base state
    if rev == "-1":
        logger.info("[++] Migrating back to the base state (before any migrations).")
        return
    revision = script.get_revision(rev)
    if revision is not None:
        logger.info(f"[++] Applying migration: {revision.revision} - {revision.doc}")
    else:
        logger.info("[++] Revision not found.")


def do_run_migrations(connection: Connection):
    try:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=filter_db_objects,
            compare_type=True,
            dialect_opts={"paramstyle": "named"},
        )
        with context.begin_transaction():
            # Check if the schema exists and create it if it doesn't
            schema_check = text(
                "SELECT schema_name FROM information_schema.schemata "
                f"WHERE schema_name = '{DB_SCHEMA}'"
            )
            if not connection.execute(schema_check).fetchone():
                context.execute(f"CREATE SCHEMA {DB_SCHEMA}")

            # Set the search path to the schema
            context.execute(f"SET search_path TO {DB_SCHEMA}")
            logger.info("[+] Start running migrations")
            # log_migration_details(context)
            context.run_migrations()
            logger.info("[+] Migrations performed successfully")
    except AttributeError:
        context_data = ctx_var.get()
        with EnvironmentContext(
            config=context_data["config"],
            script=context_data["script"],
            **context_data["opts"],
        ):
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_object=filter_db_objects,
                compare_type=True,
                dialect_opts={"paramstyle": "named"},
            )
            with context.begin_transaction():
                # Check if the schema exists and create it if it doesn't
                schema_check = text(
                    "SELECT schema_name FROM information_schema.schemata "
                    f"WHERE schema_name = '{DB_SCHEMA}'"
                )
                if not connection.execute(schema_check).fetchone():
                    context.execute(f"CREATE SCHEMA {DB_SCHEMA}")

                # Set the search path to the schema
                context.execute(f"SET search_path TO {DB_SCHEMA}")
                logger.info("[+] Start running migrations")
                # log_migration_details(context)
                context.run_migrations()
                logger.info("[+] Migrations performed successfully")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        include_object=filter_db_objects,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section, {})

    if db_url.startswith("postgresql+psycopg://"):
        engine = create_engine(db_url)
        with engine.begin() as conn:
            do_run_migrations(conn)
        conn.close()

    else:
        connectable = AsyncEngine(
            engine_from_config(
                configuration,
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()


async def run_migration_task():
    try:
        await run_migrations_online()
    except Exception as exc:
        stack_trace = traceback.format_exc()
        logger.error(f"An error occurred during migration: {exc}\n{stack_trace}")
        raise


def run_migrations():
    # Check if an event loop is running
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running event loop
        loop = None

    if loop and loop.is_running():
        from tests import conftest

        ctx_var.set(
            {
                "config": context.config,
                "script": context.script,
                "opts": context._proxy.context_opts,  # type: ignore
            }
        )
        # If there's a running loop, e.g., pytest-asyncio, create a new task for the migration
        conftest.MIGRATION_TASK = loop.create_task(run_migration_task())

        def handle_exception(task: asyncio.Task[None]) -> None:
            exception = task.exception()
            if exception:
                logger.error(f"Migration task raised an exception: {exception}")

        conftest.MIGRATION_TASK.add_done_callback(handle_exception)

    else:
        # No running loop, so we create a new one and run the migrations
        asyncio.run(run_migrations_online())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations()
