import multiprocessing
from functools import lru_cache
from pathlib import Path

from pydantic import (
    BaseModel,
    Field,
    PostgresDsn,
    ValidationInfo,
    computed_field,
    field_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from python_api_template.internal.config.utils import (
    find_base_path,
    get_project_info,
    is_running_in_docker,
)

ROOT = find_base_path()
POETRY_INFO, PROJECT_INFO = get_project_info(ROOT)


def set_default_host(value: str, is_in_docker: bool = False) -> str:
    if not is_in_docker:
        return "localhost"
    return value


class EnvBaseSettings(BaseSettings):
    """Class with config for all models."""

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=f"{ROOT}/.env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )


class CommonSettings(EnvBaseSettings):
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    is_running_in_docker: bool = is_running_in_docker()


class AppSettings(CommonSettings):
    """Application Settings"""

    pg_url: PostgresDsn

    @computed_field
    @property
    def postgres_url(self) -> PostgresDsn:
        return self.pg_url

    @postgres_url.setter
    def postgres_url(self, value: PostgresDsn | str):
        if isinstance(value, str):
            self.pg_url = MultiHostUrl(value)
        else:
            self.pg_url = value

    @computed_field
    @property
    def db_url(self) -> str:
        return self.postgres_url.unicode_string()

    root_path: Path = ROOT
    name: str = Field(default=POETRY_INFO["name"], validation_alias="APP_NAME")
    version: str = Field(POETRY_INFO["version"], validation_alias="APP_VERSION")
    description: str = Field(
        default=POETRY_INFO["description"], validation_alias="APP_DESCRIPTION"
    )
    contact: dict[str, str] = Field(
        default_factory=dict, validation_alias="APP_CONTACT", validate_default=True
    )
    testing: bool = Field(False, alias="TESTING")
    test_token: str = Field(default="frankjony17", alias="TEST_TOKEN")
    data_dir: Path = root_path / "data"
    api_v1_str: str = "/api/v1"
    host: str = Field("0.0.0.0", validation_alias="APP_HOST", validate_default=True)
    port: int = Field(8000, validation_alias="APP_PORT")

    @field_validator("host")
    @classmethod
    def _set_default_host(cls, v: str, info: ValidationInfo) -> str:
        is_in_docker = info.data.get("is_running_in_docker", False)
        return set_default_host(v, is_in_docker)

    @field_validator("contact", mode="before")
    @classmethod
    def parse_contact(cls, value: dict[str, str] | list[str]) -> dict[str, str]:
        if isinstance(value, list):
            if len(value) % 2 != 0:
                raise ValueError("Contact list must have an even number of elements")
            it = iter(value)
            return dict(zip(it, it))
        return value


class HttpSettings(CommonSettings):
    basic_headers: dict[str, str] = {"Content-Type": "application/json"}
    timeout: float = Field(default=30, gt=0, validation_alias="HTTP_TIMEOUT")
    max_attempts: int = Field(default=3, gt=0, validation_alias="HTTP_MAX_ATTEMPTS")
    time_sleep: float = Field(default=0.3, gt=0, validation_alias="HTTP_TIME_SLEEP")


class PostgresDatabaseSettings(CommonSettings):
    """Postgres Database Settings"""

    # This setting stores the hostname or IP address of your Postgres server.
    host: str = Field(
        "localhost", validation_alias="POSTGRES_SERVER", validate_default=True
    )
    # This setting stores the port of your Postgres server.
    port: int = Field(9002, validation_alias="POSTGRES_PORT")
    # This setting stores the username for your Postgres server.
    user: str = Field("postgres", validation_alias="POSTGRES_USER")
    # This setting stores the password for your Postgres server.
    password: str = Field("postgres", validation_alias="POSTGRES_PASSWORD")
    # This setting stores the name of your Postgres database.
    db: str = Field("app", validation_alias="POSTGRES_DB")
    db_schema: str = Field("template_core", validation_alias="POSTGRES_SCHEMA")
    max_pool_size: int = Field(
        1000 // multiprocessing.cpu_count(), validation_alias="POSTGREES_MAX_POOL_SIZE"
    )
    exclude_tables: list[str] = Field(
        default_factory=list, validation_alias="DB_EXCLUDE_TABLES"
    )

    @field_validator("host")
    @classmethod
    def _set_default_host(cls, v: str, info: ValidationInfo) -> str:
        is_in_docker = info.data.get("is_running_in_docker", False)
        return set_default_host(v, is_in_docker)

    @computed_field
    @property
    def url(self) -> PostgresDsn:
        schema = "postgresql+asyncpg"
        user = self.user
        password = self.password
        host = self.host
        port = self.port
        path = self.db or ""
        return MultiHostUrl.build(
            scheme=schema,
            username=user,
            password=password,
            host=host,
            port=port,
            path=path,
        )


class GunicornSettings(CommonSettings):
    """Gunicorn Settings"""

    host: str = Field("localhost", validation_alias="APP_HOST")
    port: int = Field(8000, validation_alias="APP_PORT")

    @computed_field
    @property
    def bind(self) -> str:
        return f"{self.host}:{self.port}"

    @computed_field
    @property
    def wsgi_app(self) -> str:
        return f"{POETRY_INFO['packages'][0]['include']}.main:app"

    worker_class: str = "uvicorn.workers.UvicornWorker"
    workers_per_core: int = Field(1, validation_alias="GUNICORN_WORKERS_PER_CORE")
    workers: int = Field(4, validation_alias="GUNICORN_WORKERS")
    keepalive: int = Field(4, validation_alias="GUNICORN_KEEPALIVE")
    graceful_timeout: int = Field(120, validation_alias="GUNICORN_GRACEFUL_TIMEOUT")
    timeout: int = Field(120, validation_alias="GUNICORN_TIMEOUT")


class Settings(BaseModel):
    """Class with project configuration settings."""

    postgres: PostgresDatabaseSettings = PostgresDatabaseSettings()  # type: ignore
    gunicorn: GunicornSettings = GunicornSettings()  # type: ignore
    http: HttpSettings = HttpSettings()  # type: ignore
    app: AppSettings = AppSettings(pg_url=postgres.url)  # type: ignore


@lru_cache
def get_settings():
    return Settings()


global_settings = get_settings()
