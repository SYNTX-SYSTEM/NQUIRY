"""Shared fixtures for T3 authority tests that need a real PostgreSQL instance.

14 PKG-02 TARGETED_TESTS: "For DB principals, run real local PostgreSQL
privilege tests." Skipped (not silently passed) when `DATABASE_URL` is
not set — same convention as `tests/domain/conftest.py` (PKG-01) and
`scripts/verify_migrations.py`.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
import sqlalchemy as sa


@pytest.fixture
def db_connection() -> Iterator[sa.Connection]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip(
            "DATABASE_URL not set; this test requires a live PostgreSQL 17 instance "
            "with migration 002 applied (14 PKG-02: 'run real local PostgreSQL "
            "privilege tests'). Start one with `docker compose up -d postgres` and "
            "set DATABASE_URL."
        )

    engine = sa.create_engine(database_url)
    connection = engine.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()
        engine.dispose()
