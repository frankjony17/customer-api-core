from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from python_api_template.internal.db.database import sessionmanager
from python_api_template.internal.config.gunicorn import log_data
from python_api_template.internal.config.settings import global_settings


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    sessionmanager.init(
        global_settings.app.db_url, global_settings.postgres.max_pool_size
    )
    logger.info(f"[+] {log_data}")
    yield  # This yield separates startup and shutdown logic
    logger.info("[*] Application shutdown")
    await sessionmanager.close()
