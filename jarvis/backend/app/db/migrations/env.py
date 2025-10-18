from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from ...core.settings import settings
from ..base import Base
from .. import models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url.replace("postgresql://", "postgresql+asyncpg://"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations() -> None:
    asyncio.run(run_migrations_online())


run_migrations()
