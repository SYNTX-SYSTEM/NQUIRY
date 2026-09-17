"""Alembic environment.

PKG-00 SCOPE: empty pipeline only (14 §7, §9: "No domain tables. Local
PostgreSQL container and empty Alembic pipeline only."). `target_metadata`
stays `None` until a package that owns a table (PKG-01 onward) declares
its SQLAlchemy Core `Table` objects and this file is updated by that
package's authorized migration owner (14 §3.1: "architecture-check
configuration where this package is its authorized owner").

The connection string is read from `DATABASE_URL` only — never
hardcoded (14 §33 SECRETS AND CONFIGURATION).
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# No domain tables exist yet (Phase 0). This stays None until a later
# package introduces real schema and updates this file as its
# authorized owner.
target_metadata = None


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. See infra/local/.env.example for the local "
            "Docker Compose default; this script does not assume a hardcoded connection string."
        )
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _database_url()
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
