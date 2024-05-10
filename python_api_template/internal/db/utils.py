import contextlib
import uuid
from argparse import Namespace
from pathlib import Path
from typing import Any, AsyncIterator

import sqlalchemy as sa
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils.functions.database import make_url  # type: ignore
from sqlalchemy_utils.functions.orm import quote  # type: ignore
from yarl import URL

from python_api_template.internal.config.settings import global_settings


def make_alembic_config(
    cmd_opts: Namespace, base_path: str | Path = global_settings.app.root_path
) -> AlembicConfig:
    """
    Creates an Alembic configuration object based on command line arguments,
    replacing relative paths with absolute paths.
    """
    # Replace the path to the alembic.ini file with an absolute path
    base_path = Path(base_path)
    config_path = Path(cmd_opts.config)
    if not config_path.is_absolute():
        cmd_opts.config = str(base_path / cmd_opts.config)  # "ROOT/alembic.ini"
    config = AlembicConfig(
        file_=cmd_opts.config,
        ini_section=cmd_opts.name,
        cmd_opts=cmd_opts,
    )
    # Replace the path to the alembic folder with an absolute path
    alembic_location = config.get_main_option("script_location")
    alembic_location_path = Path(alembic_location or "")
    if not alembic_location_path.is_absolute():
        config.set_main_option(
            "script_location", str(base_path / alembic_location_path)
        )  # "ROOT/migrations"
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", cmd_opts.pg_url)
    return config


def alembic_config_from_url(pg_url: str | None = None) -> AlembicConfig:
    """Provides python object, representing alembic.ini file."""
    cmd_options = Namespace(
        config="alembic.ini",  # Config file name
        name="alembic",  # Name of section in .ini file to use for Alembic config
        pg_url=pg_url,  # DB URI
        raiseerr=True,  # Raise a full stack trace on error
        x=None,  # Additional arguments consumed by custom env.py scripts
    )
    return make_alembic_config(cmd_opts=cmd_options)


def alembic_create_all(alembic_config: AlembicConfig):
    # Run migrations up to 'head', which should create all tables
    command.upgrade(alembic_config, "head")


def alembic_drop_all(alembic_config: AlembicConfig):
    # Downgrade migrations to 'base', which should drop all tables
    command.downgrade(alembic_config, "base")


def replace_db_url_path(db_url: str | URL, new_path: str) -> str | URL:
    """
    Replaces the path in the database URL with a new path.

    Parameters:
    - db_url (str | URL): The original database URL.
    - new_path (str): The new path to replace in the URL.

    Returns:
    - str | URL: The modified database URL with the new path.
    """
    parsed_url = URL(db_url) if isinstance(db_url, str) else db_url
    # Ensure the new path starts with a slash for proper URL formatting
    if not new_path.startswith("/"):
        new_path = "/" + new_path
    # Rebuild the URL with the new path
    modified_url = parsed_url.with_path(path=new_path)
    return str(modified_url) if isinstance(db_url, str) else modified_url


def set_url_database(url: sa.engine.url.URL, database: str | None) -> sa.engine.url.URL:
    """Set the database of an engine URL.

    :param url: A SQLAlchemy engine URL.
    :param database: New database to set.
    """
    if database is None:
        return url
    ret = url._replace(database=database)
    assert ret.database == database, ret
    return ret


@contextlib.asynccontextmanager
async def tmp_database_url(
    db_url: str | URL, suffix: str = "", **kwargs: Any
) -> AsyncIterator[str]:
    """Context manager for creating new database and deleting it on exit."""
    tmp_db_name = f"{uuid.uuid4().hex}.tests-base{suffix}"
    tmp_db_url = str(replace_db_url_path(db_url, tmp_db_name))
    await create_database_async(tmp_db_url, **kwargs)
    try:
        yield tmp_db_url
    finally:
        await drop_database_async(tmp_db_url)


# TODO: we don't need to use make_url, we can implement it using urlparse and urlunparse
# TODO: we don't need to use quote, we can implement it using f-string
# TODO: we can optimize the if-elif-else dialect_name block
async def create_database_async(
    url: str | sa.engine.url.URL, encoding: str = "utf8", template: str | None = None
) -> None:
    """
    Asynchronously creates a database.
    """
    sql_url = make_url(url)
    database = sql_url.database
    dialect_name = sql_url.get_dialect().name
    dialect_driver = sql_url.get_dialect().driver

    if dialect_name == "postgresql":
        sql_url = set_url_database(sql_url, database="postgres")
    elif dialect_name == "mssql":
        sql_url = set_url_database(sql_url, database="master")
    elif dialect_name == "cockroachdb":
        sql_url = set_url_database(sql_url, database="defaultdb")
    elif not dialect_name == "sqlite":
        sql_url = set_url_database(sql_url, database=None)

    if (dialect_name == "mssql" and dialect_driver in {"pymssql", "pyodbc"}) or (
        dialect_name == "postgresql"
        and dialect_driver in {"asyncpg", "pg8000", "psycopg2", "psycopg2cffi"}
    ):
        engine = create_async_engine(sql_url, isolation_level="AUTOCOMMIT")
    else:
        engine = create_async_engine(sql_url)

    if dialect_name == "postgresql":
        if not template:
            template = "template1"

        async with engine.begin() as conn:
            text = f"CREATE DATABASE {quote(conn, database)} ENCODING '{encoding}' TEMPLATE {quote(conn, template)}"
            await conn.execute(sa.text(text))

    elif dialect_name == "mysql":
        async with engine.begin() as conn:
            text = (
                f"CREATE DATABASE {quote(conn, database)} CHARACTER SET = '{encoding}'"
            )
            await conn.execute(sa.text(text))

    elif dialect_name == "sqlite" and database != ":memory:":
        if database:
            async with engine.begin() as conn:
                await conn.execute(sa.text("CREATE TABLE DB(id int)"))
                await conn.execute(sa.text("DROP TABLE DB"))

    else:
        async with engine.begin() as conn:
            text = f"CREATE DATABASE {quote(conn, database)}"
            await conn.execute(sa.text(text))

    await engine.dispose()


async def drop_database_async(url: str | sa.engine.url.URL) -> None:
    """
    Asynchronously drops a database.
    """
    sql_url = make_url(url)
    database = sql_url.database
    dialect_name = sql_url.get_dialect().name
    dialect_driver = sql_url.get_dialect().driver

    if dialect_name == "postgresql":
        sql_url = set_url_database(sql_url, database="postgres")
    elif dialect_name == "mssql":
        sql_url = set_url_database(sql_url, database="master")
    elif dialect_name == "cockroachdb":
        sql_url = set_url_database(sql_url, database="defaultdb")
    elif not dialect_name == "sqlite":
        sql_url = set_url_database(sql_url, database=None)

    if dialect_name == "mssql" and dialect_driver in {"pymssql", "pyodbc"}:
        engine = create_async_engine(sql_url, connect_args={"autocommit": True})
    elif dialect_name == "postgresql" and dialect_driver in {
        "asyncpg",
        "pg8000",
        "psycopg2",
        "psycopg2cffi",
    }:
        engine = create_async_engine(sql_url, isolation_level="AUTOCOMMIT")
    else:
        engine = create_async_engine(sql_url)

    if dialect_name == "sqlite" and database != ":memory:":
        if database:
            db_file = Path(database)
            if db_file.exists():
                db_file.unlink()
    elif dialect_name == "postgresql":
        async with engine.begin() as conn:
            # Disconnect all users from the database we are dropping.
            version = conn.dialect.server_version_info
            pid_column = "pid" if version and version >= (9, 2) else "procpid"
            text = """
            SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database}'
            AND {pid_column} <> pg_backend_pid();
            """.format(pid_column=pid_column, database=database)
            await conn.execute(sa.text(text))

            # Drop the database.
            text = f"DROP DATABASE {quote(conn, database)}"
            await conn.execute(sa.text(text))
    else:
        async with engine.begin() as conn:
            text = f"DROP DATABASE {quote(conn, database)}"
            await conn.execute(sa.text(text))

    await engine.dispose()
