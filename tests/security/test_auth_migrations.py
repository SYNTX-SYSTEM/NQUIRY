"""T9: the AUTH Field's migrations preserve existing authentication data
(24 §22.4, §28.2, §28.3, §28.9; §39.5 "migration up/down").

Each test builds its own scratch database, walks the real Alembic revisions
step by step with rows of the predecessor shape in place, and drops the
database afterwards. The shared test database is never downgraded.
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest
import sqlalchemy as sa

ROOT = Path(__file__).resolve().parents[2]
_WU02 = "f1a7c3d9b2e4"
_WU03 = "a2c4e6f8b1d3"
_WU04 = "b3d5f7a9c2e6"
_CREATED = datetime(2029, 6, 1, 12, 0, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"


class _Scratch:
    def __init__(self, url: sa.URL) -> None:
        self.url = url
        self.engine = sa.create_engine(url)

    def alembic(self, *args: str) -> None:
        subprocess.run(
            [sys.executable, "-m", "alembic", "-c", "migrations/alembic.ini", *args],
            cwd=ROOT,
            env={**os.environ, "DATABASE_URL": self.url.render_as_string(hide_password=False)},
            check=True,
            capture_output=True,
        )

    def scalar(self, statement: str, **params: object) -> object:
        with self.engine.connect() as connection:
            return connection.execute(sa.text(statement), params).scalar_one()


@pytest.fixture
def scratch() -> Iterator[_Scratch]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; this test builds a scratch PostgreSQL database.")
    base = sa.make_url(database_url)
    name = f"{base.database}_mig_{uuid.uuid4().hex[:10]}"
    admin = sa.create_engine(base, isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(sa.text(f'CREATE DATABASE "{name}"'))
    database = _Scratch(base.set(database=name))
    try:
        yield database
    finally:
        database.engine.dispose()
        with admin.connect() as connection:
            connection.execute(sa.text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        admin.dispose()


def _predecessor_credential(database: _Scratch, *, email: str) -> tuple[uuid.UUID, uuid.UUID, str]:
    """A user and a credential exactly as the predecessor (18) wrote them."""
    from security.local_auth import hash_password

    user_id, credential_id, password_hash = uuid.uuid4(), uuid.uuid4(), hash_password(_PASSWORD)
    with database.engine.begin() as connection:
        connection.execute(
            sa.text(
                "INSERT INTO users (id, email, name, record_version, created_at, updated_at) "
                "VALUES (:id, :email, 'Predecessor', 1, :at, :at)"
            ),
            {"id": user_id, "email": email, "at": _CREATED},
        )
        connection.execute(
            sa.text(
                "INSERT INTO local_auth_credentials "
                "(id, user_id, password_hash, created_at, updated_at) "
                "VALUES (:id, :user_id, :hash, :at, :at)"
            ),
            {"id": credential_id, "user_id": user_id, "hash": password_hash, "at": _CREATED},
        )
    return user_id, credential_id, password_hash


def test_existing_credentials_become_local_password_methods_and_keep_logging_in(
    scratch: _Scratch,
) -> None:
    scratch.alembic("upgrade", _WU02)
    first = _predecessor_credential(scratch, email="first@example.test")
    second = _predecessor_credential(scratch, email="second@example.test")
    with scratch.engine.begin() as connection:  # an identity with no credential
        connection.execute(
            sa.text(
                "INSERT INTO users (id, email, name, record_version, created_at, updated_at) "
                "VALUES (:id, 'none@example.test', 'No Credential', 1, :at, :at)"
            ),
            {"id": uuid.uuid4(), "at": _CREATED},
        )

    scratch.alembic("upgrade", _WU03)

    assert scratch.scalar("SELECT count(*) FROM authentication_methods") == 2
    for user_id, credential_id, password_hash in (first, second):
        with scratch.engine.connect() as connection:
            row = (
                connection.execute(
                    sa.text(
                        "SELECT c.password_hash, c.created_at AS credential_created_at, "
                        "c.user_id AS credential_user, m.user_id AS method_user, "
                        "m.method_type, m.status, m.created_at, m.provenance_ref "
                        "FROM local_auth_credentials c JOIN authentication_methods m "
                        "ON m.id = c.authentication_method_id WHERE c.id = :id"
                    ),
                    {"id": credential_id},
                )
                .mappings()
                .one()
            )
        assert row["password_hash"] == password_hash
        assert row["credential_user"] == row["method_user"] == user_id
        assert (row["method_type"], row["status"]) == ("LOCAL_PASSWORD", "ACTIVE")
        assert row["created_at"] == row["credential_created_at"] == _CREATED
        assert row["provenance_ref"] == f"migration:{_WU03}:local-credential:{credential_id}"
        assert _PASSWORD not in row["provenance_ref"]

    scratch.alembic("downgrade", _WU02)

    assert scratch.scalar("SELECT count(*) FROM authentication_methods") == 0
    assert scratch.scalar("SELECT count(*) FROM local_auth_credentials") == 2
    assert (
        scratch.scalar(
            "SELECT count(*) FROM information_schema.columns WHERE table_name = "
            "'local_auth_credentials' AND column_name = 'authentication_method_id'"
        )
        == 0
    )
    assert (
        scratch.scalar(
            "SELECT password_hash FROM local_auth_credentials WHERE id = :id", id=first[1]
        )
        == first[2]
    )

    scratch.alembic("upgrade", "head")

    from application.auth_handler import InvalidCredentials, login
    from persistence.local_auth_repository import (
        SqlAlchemyLocalCredentialRepository,
        SqlAlchemyLocalSessionRepository,
    )

    with scratch.engine.begin() as connection:
        repositories = {
            "credential_repository": SqlAlchemyLocalCredentialRepository(connection),
            "session_repository": SqlAlchemyLocalSessionRepository(connection),
            "now": datetime(2030, 1, 1, tzinfo=timezone.utc),
        }
        assert login("first@example.test", _PASSWORD, **repositories).user_id.value == first[0]
        assert login("second@example.test", _PASSWORD, **repositories).user_id.value == second[0]
        with pytest.raises(InvalidCredentials):
            login("none@example.test", _PASSWORD, **repositories)


def test_a_fresh_database_reaches_head_and_steps_back_to_the_predecessor_schema(
    scratch: _Scratch,
) -> None:
    scratch.alembic("upgrade", "head")
    assert scratch.scalar("SELECT to_regclass('authentication_methods')::text") is not None
    scratch.alembic("downgrade", "e8c2a5f1b7d4")
    assert scratch.scalar("SELECT to_regclass('authentication_methods')::text IS NULL") is True
    assert scratch.scalar("SELECT to_regclass('local_auth_credentials')::text") is not None
    assert scratch.scalar("SELECT version_num FROM alembic_version") == "e8c2a5f1b7d4"


def _predecessor_session(
    database: _Scratch, *, user_id: uuid.UUID, revoked: bool
) -> tuple[uuid.UUID, str]:
    """A session exactly as the predecessor (18) wrote it. Returns (id, raw token)."""
    from security.local_auth import generate_session_token, hash_session_token

    session_id, token = uuid.uuid4(), generate_session_token()
    with database.engine.begin() as connection:
        connection.execute(
            sa.text(
                "INSERT INTO local_auth_sessions "
                "(id, user_id, session_token_hash, issued_at, expires_at, revoked_at) "
                "VALUES (:id, :user_id, :hash, :issued, :expires, :revoked)"
            ),
            {
                "id": session_id,
                "user_id": user_id,
                "hash": hash_session_token(token),
                "issued": _CREATED,
                "expires": datetime(2031, 1, 1, tzinfo=timezone.utc),
                "revoked": _CREATED if revoked else None,
            },
        )
    return session_id, token


def test_existing_sessions_are_attributed_not_invalidated(scratch: _Scratch) -> None:
    """24 §28.3: a session that authenticated before the migration still does
    afterwards, and is now traceable to the method that produced it."""
    scratch.alembic("upgrade", _WU02)
    user_id, credential_id, _ = _predecessor_credential(scratch, email="live@example.test")
    orphan_id = uuid.uuid4()
    with scratch.engine.begin() as connection:
        connection.execute(
            sa.text(
                "INSERT INTO users (id, email, name, record_version, created_at, updated_at) "
                "VALUES (:id, 'orphan@example.test', 'No Credential', 1, :at, :at)"
            ),
            {"id": orphan_id, "at": _CREATED},
        )
    live_id, live_token = _predecessor_session(scratch, user_id=user_id, revoked=False)
    revoked_id, revoked_token = _predecessor_session(scratch, user_id=user_id, revoked=True)
    orphan_session_id, _ = _predecessor_session(scratch, user_id=orphan_id, revoked=False)

    def session(session_id: uuid.UUID) -> sa.RowMapping:
        with scratch.engine.connect() as connection:
            return (
                connection.execute(
                    sa.text("SELECT * FROM local_auth_sessions WHERE id = :id"), {"id": session_id}
                )
                .mappings()
                .one()
            )

    before = {key: session(key) for key in (live_id, revoked_id, orphan_session_id)}

    scratch.alembic("upgrade", _WU04)

    method_id = scratch.scalar(
        "SELECT authentication_method_id FROM local_auth_credentials WHERE id = :id",
        id=credential_id,
    )
    live, revoked, orphan = session(live_id), session(revoked_id), session(orphan_session_id)
    assert live["authentication_method_id"] == revoked["authentication_method_id"] == method_id
    assert live["proof_provenance"] is None and live["revoked_reason"] is None
    assert revoked["revoked_reason"] == "LOGOUT" and revoked["revoked_at"] == _CREATED
    assert orphan["authentication_method_id"] is None
    assert orphan["proof_provenance"] == f"migration:{_WU04}:no-local-credential"
    for key, after in ((live_id, live), (revoked_id, revoked), (orphan_session_id, orphan)):
        for column in ("user_id", "session_token_hash", "issued_at", "expires_at", "revoked_at"):
            assert after[column] == before[key][column], (key, column)

    scratch.alembic("upgrade", "head")

    from application.auth_handler import resolve_session
    from persistence.local_auth_repository import SqlAlchemyLocalSessionRepository

    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    with scratch.engine.connect() as connection:
        repository = SqlAlchemyLocalSessionRepository(connection)
        principal = resolve_session(live_token, session_repository=repository, now=now)
        assert principal is not None and principal.user_id.value == user_id
        assert principal.authentication_time == _CREATED
        assert resolve_session(revoked_token, session_repository=repository, now=now) is None

    scratch.alembic("downgrade", _WU03)

    assert scratch.scalar("SELECT count(*) FROM local_auth_sessions") == 3
    assert (
        scratch.scalar(
            "SELECT count(*) FROM information_schema.columns WHERE table_name = "
            "'local_auth_sessions' AND column_name IN "
            "('authentication_method_id', 'proof_provenance', 'revoked_reason')"
        )
        == 0
    )
    assert session(live_id)["session_token_hash"] == before[live_id]["session_token_hash"]
