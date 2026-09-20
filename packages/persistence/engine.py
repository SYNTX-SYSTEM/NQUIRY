"""Runtime database engine/connection factory.

Architecture 17 materialization: every predecessor package's own real
`sa.Connection` construction lived only in `tests/*/conftest.py`
fixtures (`sa.create_engine(os.environ["DATABASE_URL"])`) because no
production caller needed one until this package -- an HTTP request
handler is the first REAL, non-test caller in this codebase that must
obtain a live connection at runtime rather than receiving one from a
pytest fixture. This module is that construction, moved into
`persistence` (already the sole owner of every concrete SQLAlchemy
adapter, and the only layer 14 §4's forbidden-dependency matrix
permits to import the `sqlalchemy`/DB-driver group at all -- `nquiry_api`
and `application` are both explicitly forbidden from it, see
`scripts/check_architecture_dependencies.py`'s own `_DB_DRIVER` table).

One process-lifetime `Engine` (SQLAlchemy's own connection-pooling
unit) is created lazily on first use and reused -- not a new `Engine`
per request, which would defeat pooling entirely.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

import sqlalchemy as sa

_engine: sa.Engine | None = None


class DatabaseUrlNotConfigured(RuntimeError):
    """Raised when `DATABASE_URL` is not set in the process
    environment. Fails closed -- there is no default connection
    string this module will silently fall back to."""


def _get_engine() -> sa.Engine:
    global _engine
    if _engine is None:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise DatabaseUrlNotConfigured("DATABASE_URL is not set in the process environment")
        _engine = sa.create_engine(database_url, pool_pre_ping=True)
    return _engine


@contextmanager
def connect() -> Iterator[sa.Connection]:
    """One request-scoped connection, inside its own transaction,
    committed on clean exit and rolled back on any exception --
    mirrors every existing test's own `db_connection` fixture
    transaction-per-call discipline, applied to a real runtime request
    instead of a test.
    """
    engine = _get_engine()
    with engine.connect() as connection, connection.begin():
        yield connection


__all__ = ["DatabaseUrlNotConfigured", "connect"]
