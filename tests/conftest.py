from asyncio import Task
from contextlib import ExitStack
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from yarl import URL

from python_api_template.internal.db import BaseOrmModel
from python_api_template.internal.db.database import (
    DatabaseSessionManager,
    get_async_session,
    sessionmanager,
)
from python_api_template.internal.db.utils import (
    alembic_config_from_url,
    alembic_create_all,
    alembic_drop_all,
    tmp_database_url,
)
from python_api_template.internal.config.settings import global_settings
from python_api_template.main import init_app

MIGRATION_TASK: Task[None] | None = None


@pytest.fixture(autouse=True)
def anyio_backend() -> tuple[str, dict[str, Any]]:
    """
    Configure anyio pytest backend to test with asyncio event loop only.
    This fixture automatically applies to all tests in the session
    """
    return "asyncio", {"use_uvloop": True}


@pytest.fixture(scope="session")
def postgres_url() -> URL:
    """Provides base PostgreSQL URL for creating temporary databases."""
    return URL(global_settings.postgres.url.unicode_string())


@pytest.fixture()
async def empty_postgres(postgres_url: URL):
    """
    Creates empty temporary database.
    """
    async with tmp_database_url(postgres_url, "empty-pytest") as tmp_url:
        yield tmp_url


@pytest.fixture(scope="session")
async def migrated_postgres_template(postgres_url: URL):
    """
    Creates temporary database and applies migrations.

    Has "session" scope, so is called only once per tests run.
    """
    async with tmp_database_url(postgres_url, "template") as tmp_url:
        alembic_config = alembic_config_from_url(tmp_url)
        # sometimes we have so called data-migrations.
        # they can call different db-related functions etc..
        # so we modify our settings
        global_settings.app.postgres_url = tmp_url

        # It is important to always close the connections at the end of such migrations,
        # or we will get errors like `source database is being accessed by other users`

        alembic_drop_all(alembic_config)
        await MIGRATION_TASK

        alembic_create_all(alembic_config)
        await MIGRATION_TASK

        yield tmp_url


@pytest.fixture
async def migrated_postgres(postgres_url: URL, migrated_postgres_template: str):
    """
    Quickly creates clean migrated database using temporary database as base.
    Use this fixture in tests that require migrated database.
    """
    template_db = URL(migrated_postgres_template).name
    async with tmp_database_url(
        postgres_url, "pytest", template=template_db
    ) as tmp_url:
        yield tmp_url


# TODO: for now, sessionmanager is a true singleton, so yielding sessionmanager seems redundant
@pytest.fixture
async def sessionmanager_for_tests(migrated_postgres: str):
    sessionmanager.init(
        db_url=migrated_postgres, pool_size=global_settings.postgres.max_pool_size
    )
    # We can add other inits (e.g., redis)
    yield sessionmanager
    await sessionmanager.close()


@pytest.fixture(autouse=True)
async def session_override(
    app: FastAPI, sessionmanager_for_tests: DatabaseSessionManager
):
    async def get_async_db_override():
        async with sessionmanager_for_tests.session() as session:
            yield session

    app.dependency_overrides[get_async_session] = get_async_db_override


@pytest.fixture
async def session(sessionmanager_for_tests: DatabaseSessionManager):
    async with sessionmanager_for_tests.session() as session:
        yield session

    # Clean tables after each test. I tried:
    # 1. Create new database using an empty `migrated_postgres_template` as template
    # (postgres could copy whole db structure)
    # 2. Do TRUNCATE after each test.
    # 3. Do DELETE after each test.
    # 4. DELETE FROM.
    # DELETE FROM is the fastest
    # https://www.lob.com/blog/truncate-vs-delete-efficiently-clearing-data-from-a-postgres-table
    # BUT DELETE FROM query does not reset any AUTO_INCREMENT counter
    async with sessionmanager_for_tests.connect() as conn:
        for table in reversed(BaseOrmModel.metadata.sorted_tables):
            # Clean tables in such order that tables which depend on another go first
            await conn.execute(table.delete())
        await conn.commit()


@pytest.fixture
def app():
    with ExitStack():
        yield init_app(init_db=False)


@pytest.fixture
async def api_client(app: FastAPI):
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url=f"http://test{global_settings.app.api_v1_str}",
    ) as client:
        yield client
