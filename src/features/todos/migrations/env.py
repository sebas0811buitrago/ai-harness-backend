import os
import sys
from pathlib import Path

# Ensure src/ is on the path so module imports resolve correctly.
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from logging.config import fileConfig

import sqlalchemy as sa
from alembic import context
from sqlmodel import SQLModel

# Import all SQLModel table classes so their metadata is registered.
from features.todos.adapters.db.models import TodoRow  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def _get_url() -> str:
    url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url", "")
    # Alembic env runs sync; strip async driver prefix if present.
    return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")


def run_migrations_offline() -> None:
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = sa.create_engine(_get_url(), poolclass=sa.pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
