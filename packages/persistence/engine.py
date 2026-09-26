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

import contextlib
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


class DatabaseUnavailable(RuntimeError):
    """WU-PFC-F09-1 (10 section 14: "failure before any CommitUnit mutation"):
    no connection could be obtained, so nothing was executed. Canonical
    consequence is proven absent."""


class CommitRejected(RuntimeError):
    """WU-PFC-F09-1 (10 section 14: "proven abort"): the server answered the
    COMMIT with an error (for example a deferred constraint), so the
    transaction was aborted and nothing persisted."""


class CommitOutcomeUnknown(RuntimeError):
    """WU-PFC-F09-1 (10 section 14: "uncertain commit"): the connection failed
    while COMMIT was in flight. Whether the transaction committed cannot be
    proven (10 section 4.4 INDETERMINATE)."""


@contextmanager
def connect() -> Iterator[sa.Connection]:
    """One request-scoped connection, inside its own transaction,
    committed on clean exit and rolled back on any exception --
    mirrors every existing test's own `db_connection` fixture
    transaction-per-call discipline, applied to a real runtime request
    instead of a test.

    WU-PFC-F09-1: the three technical failure points are reported as typed
    facts, because "a database exception by itself does not establish which
    result occurred" (10 section 14):
    - connecting fails: `DatabaseUnavailable`
    - the COMMIT is answered with an error: `CommitRejected` (proven abort)
    - the connection fails during COMMIT: `CommitOutcomeUnknown`
    An exception raised by the caller inside the block still propagates
    unchanged after rollback, as before.
    """
    engine = _get_engine()
    try:
        connection = engine.connect()
    except sa.exc.SQLAlchemyError as exc:
        raise DatabaseUnavailable(f"{type(exc).__name__}: {exc}") from exc
    with connection:
        transaction = connection.begin()
        try:
            yield connection
        except BaseException:
            if transaction.is_active:
                # A lost connection cannot roll back explicitly; the server
                # discards an uncommitted transaction anyway. The caller's
                # own exception is what propagates, never this one.
                with contextlib.suppress(sa.exc.SQLAlchemyError):
                    transaction.rollback()
            raise
        try:
            transaction.commit()
        except (sa.exc.IntegrityError, sa.exc.ProgrammingError, sa.exc.DataError) as exc:
            raise CommitRejected(f"{type(exc).__name__}: {exc}") from exc
        except sa.exc.SQLAlchemyError as exc:
            raise CommitOutcomeUnknown(f"{type(exc).__name__}: {exc}") from exc


__all__ = [
    "CommitOutcomeUnknown",
    "CommitRejected",
    "DatabaseUnavailable",
    "DatabaseUrlNotConfigured",
    "connect",
]
