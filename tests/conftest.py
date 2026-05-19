import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as pg:
        yield pg


@pytest.fixture(scope="session")
def sync_db_url(postgres_container: PostgresContainer) -> str:
    """psycopg2 URL used by Alembic migrations (sync)."""
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def async_db_url(sync_db_url: str) -> str:
    """asyncpg URL used by the FastAPI app (async)."""
    return sync_db_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")


@pytest.fixture(scope="session")
def run_migrations(sync_db_url: str) -> None:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", sync_db_url)
    command.upgrade(cfg, "head")


@pytest.fixture(scope="session")
def client(async_db_url: str, run_migrations: None) -> TestClient:  # type: ignore[misc]
    os.environ["DATABASE_URL"] = async_db_url

    from shared.config.settings import get_settings

    get_settings.cache_clear()

    from app.main import create_app

    with TestClient(create_app(), raise_server_exceptions=True) as client:
        yield client
