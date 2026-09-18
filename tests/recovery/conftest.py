"""Shared fixtures for T8 recovery tests that need a real PostgreSQL instance.

Identical `SKIPPED_NO_DATABASE` convention as `tests/command_commit_event/conftest.py`,
`tests/boundaries/conftest.py`, etc.
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
            "with all migrations applied. Start one with `docker compose up -d postgres` "
            "and set DATABASE_URL."
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
