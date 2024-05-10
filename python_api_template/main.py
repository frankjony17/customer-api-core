import os

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware

from python_api_template.common.api.api_v1.api import api_router as common_api_router
from python_api_template.common.exceptions.exception_handlers import (
    setup_exception_handlers,
)
from python_api_template.example.api.api_v1.api import api_router as example_api_router
from python_api_template.internal.config.logger import set_up_logger
from python_api_template.internal.config.settings import global_settings
from python_api_template.lifespan import app_lifespan


def init_app(init_db: bool = True) -> FastAPI:
    # Set custom logger configurations (loguru)
    set_up_logger()
    origins = ["*"]

    # FastAPI application
    api = FastAPI(
        lifespan=app_lifespan if init_db else None,
        title=" ".join(
            name.capitalize()
            for name in global_settings.app.name.split("-")  # type: ignore
        ),
        description=global_settings.app.description,
        version=global_settings.app.version,
        contact=global_settings.app.contact,
    )

    if global_settings.app.environment != "prod":
        # allow oauth2 loop to run over http (used for local testing only)
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Instrumentator().instrument(api).expose(api, tags=["Common"])

    api.include_router(common_api_router)
    api.include_router(example_api_router, prefix=global_settings.app.api_v1_str)

    setup_exception_handlers(api)

    return api


app = init_app()
