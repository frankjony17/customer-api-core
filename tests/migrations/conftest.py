import pytest
from alembic.config import Config as AlembicConfig

from python_api_template.internal.db.utils import alembic_config_from_url


@pytest.fixture()
def alembic_config(empty_postgres: str) -> AlembicConfig:
    """
    Alembic configuration object, bound to temporary migrated database.
    """
    return alembic_config_from_url(empty_postgres)
