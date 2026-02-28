import asyncio
from sqlalchemy import pool
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

from src.app.config.settings import settings
from src.app.common.base import Base
from src.app.features.auction.models import *

config = context.config
target_metadata = Base.metadata

# Use sync URL for Alembic (replace asyncpg with postgresql)
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgresql+asyncpg"):
    sync_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
else:
    sync_url = DATABASE_URL

config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(sync_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
