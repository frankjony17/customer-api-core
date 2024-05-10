import contextlib
import traceback
from typing import Any, AsyncGenerator, AsyncIterator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from python_api_template.common.exceptions.exceptions import (
    ForeignKeyError,
    ORMError,
    UniqueConstraintError,
)
from python_api_template.internal.config.settings import global_settings
from python_api_template.internal.config.utils import exc_info
from python_api_template.internal.utils.pathutils import read_file


Base = declarative_base()


def get_async_sql_engine(
    db_url: str, pool_size: int, connect_args: dict[str, Any]
) -> AsyncEngine:
    return create_async_engine(
        db_url,
        future=True,
        pool_pre_ping=True,
        echo=False,
        pool_size=pool_size,
        connect_args=connect_args,
    )


def get_async_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine, autoflush=False, class_=AsyncSession, expire_on_commit=False
    )


class DatabaseSessionManager:
    _instance = None

    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None
        self._db_url = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseSessionManager, cls).__new__(cls)
            cls._instance._engine = None
            cls._instance._sessionmaker = None
        return cls._instance

    def init(self, db_url: str, pool_size: int):
        self._db_url = db_url
        if "postgresql" in db_url:
            # These settings are needed to work with pgbouncer in transaction mode
            # because you can't use prepared statements in such case
            connect_args = {
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            }
        else:
            connect_args = {}
        self._engine = get_async_sql_engine(self._db_url, pool_size, connect_args)
        self._sessionmaker = get_async_sessionmaker(self._engine)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._sessionmaker() as session:
            try:
                yield session
            except IntegrityError as exc:
                await session.rollback()
                logger.debug(f"IntegrityError occurred: {exc.args[0]}")
                if "ForeignKeyViolation" in exc.args[0]:
                    logger.debug(
                        f"ForeignKey violation: {exc.orig.diag.message_detail} | Context: {exc.params}"  # type: ignore
                    )
                    raise ForeignKeyError(exc.args[0]) from exc
                logger.debug(
                    f"Unique constraint violation: {exc.orig.diag.message_detail} | Context: {exc.params}"  # type: ignore
                )
                raise UniqueConstraintError(exc.args[0]) from exc
            except SQLAlchemyError as exc:
                logger.debug(f"SQLAlchemyError occurred: {str(exc)}")
                logger.debug(
                    f"Error Type: {type(exc).__name__} | Session active: {session.is_active} | Stack Trace: {traceback.format_exc()}"
                )
                await session.rollback()
                raise ORMError(str(exc)) from exc
            finally:
                await session.close()


sessionmanager = DatabaseSessionManager()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmanager.session() as async_session:
        yield async_session


async def perform_db_healthcheck(async_session: AsyncSession) -> bool:
    try:
        result = await async_session.execute(text("SELECT 1;"))
        if result.scalar() == 1:
            logger.info("Performed db healthcheck with result: True")
            return True
        logger.info("Performed db healthcheck with result: False")
        return False
    except OperationalError as err:
        stacktrace = traceback.format_exception_only(*exc_info())
        raise SQLAlchemyError(stacktrace=stacktrace) from err


async def bulk_insert_data(async_session: AsyncSession, parsed_data: list[Any]):
    async with async_session.begin():
        async_session.add_all(parsed_data)
        await async_session.commit()


async def init_db(_: AsyncSession) -> None:
    data_dir = global_settings.app.data_dir
    # Iterate over all SQL files in the data directory
    for sql_file in [
        "wordform.sql",
        # "work.sql",
        # "chapter.sql",
        # "paragraph.sql",
        # "character.sql",
        # "character_work.sql",
    ]:
        # Read the content of the SQL file
        _ = read_file(data_dir / sql_file)  # type: ignore
