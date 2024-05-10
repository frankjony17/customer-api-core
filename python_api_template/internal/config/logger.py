from __future__ import annotations
import logging
import sys
from typing import Any

from gunicorn import glogging  # type: ignore[import]
from loguru import logger
import loguru
from .settings import global_settings


class LoggerLevelFilter:
    def __init__(self, level: str):
        self.level = level

    def __call__(self, record: loguru.Record):
        levelno = logger.level(self.level).no
        return record["level"].no >= levelno


# format string for Loguru loggers
LOGURU_FORMAT = (
    "<green>{time:HH:mm:ss.SSSSSS!UTC}</green> | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)


class InterceptHandler(logging.Handler):
    """Handler for intercepting records and outputting to loguru."""

    def emit(self, record: logging.LogRecord):
        """Intercepts log messages.
        Intercepts log records sent to the handler, adds additional context to
        the records, and outputs the record to the default loguru logger.

        :param: record: The log record
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2

        while frame.f_code.co_filename == logging.__file__:
            if frame.f_back:
                frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class Logger(glogging.Logger):
    """Implements and overrides the gunicorn logging interface.

    This class inherits from the standard gunicorn logger and overrides it by
    replacing the handlers with `InterceptHandler` in order to route the
    gunicorn logs to loguru.
    """

    def __init__(self, cfg: dict[str, Any]):
        super().__init__(cfg)
        logging.getLogger("gunicorn.error").handlers = [InterceptHandler()]
        logging.getLogger("gunicorn.access").handlers = [InterceptHandler()]


def set_up_logger() -> None:
    """
    Set custom logger configurations. Add sinks to record logs in specific
    files. Create levels for Response and Latency where each level has a name,
    a severity number (larger is more severe), and a color."""
    try:
        # Redirect SQLAlchemy logs
        # logging.getLogger("sqlalchemy.engine").handlers = [InterceptHandler()]
        logging.getLogger("sqlalchemy.pool").handlers = [InterceptHandler()]
        logging.getLogger("sqlalchemy.engine.Engine").handlers = [InterceptHandler()]

        # Redirect Alembic logs
        logging.getLogger("alembic.runtime.migration").handlers = [InterceptHandler()]
        # logging.getLogger("alembic").handlers = [InterceptHandler()]
        # logger.level("RESPONSE", no=15, color="<green><bold>")
        # logger.level("LATENCY", no=15, color="<blue><bold>")

    except TypeError as err:
        logger.warning(f"Level already exists: {err}")

    logger.remove()  # Remove all handlers added so far, including the default one.
    environment = global_settings.app.environment
    if environment in ["development", "testing"]:
        level_filter = LoggerLevelFilter("DEBUG")
    else:
        level_filter = LoggerLevelFilter("WARNING")

    logger.add(sys.stdout, filter=level_filter, format=LOGURU_FORMAT, colorize=True)
