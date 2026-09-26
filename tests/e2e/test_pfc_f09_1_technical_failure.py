"""WU-PFC-F09-1 (F09): the system says what it actually knows under technical failure.

Architecture: 19 §29 (F09: "The system says what it actually knows. It does not
falsely claim success, failure, authority, recovery"; internal Work Units
"failure taxonomy", "HTTP failure mapping", "INDETERMINATE handling"; TESTS
FIRST "DB unavailable before operation", "DB uncertainty around commit");
10 §4 (only DENIED / FAILED_PRECOMMIT / COMMITTED / INDETERMINATE), §4.2
(FAILED_PRECOMMIT: canonical consequence proven absent), §4.4 (INDETERMINATE:
cannot prove; block blind retry; preserve command identity), §14 (F-PERS:
"failure before any CommitUnit mutation / proven abort -> FAILED_PRECOMMIT;
uncertain commit -> INDETERMINATE; a database exception by itself does not
establish which result occurred"); 09 §77 (write outcomes carry command_id),
§78 ("5xx technical failure -> may be FAILED_PRECOMMIT or INDETERMINATE; must
not be guessed from status code alone").

FIRST BROKEN RELATION (before this Work Unit): a database failure escapes every
route as a bare plain-text 500 (no envelope), and the worker's delivery loop
dies on its first database error. The request transaction's COMMIT outcome is
never distinguished: an uncertain commit and a proven abort look identical.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient

_UNREACHABLE = "postgresql+psycopg://nquiry:x@127.0.0.1:1/none"


def _engine_module() -> Any:
    import persistence.engine as engine

    return engine


@pytest.fixture
def unreachable_db(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _engine_module()
    monkeypatch.setattr(engine, "_engine", sa.create_engine(_UNREACHABLE, pool_pre_ping=True))


@pytest.fixture
def real_engine(monkeypatch: pytest.MonkeyPatch) -> sa.Engine:
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL not set; this test needs a live PostgreSQL")
    e = sa.create_engine(url)
    monkeypatch.setattr(_engine_module(), "_engine", e)
    return e


def _client() -> TestClient:
    from nquiry_api.main import app

    return TestClient(app, raise_server_exceptions=False)


# ------------------------------------------------------------ the engine knows


def test_engine_reports_an_unreachable_database_as_unavailable(unreachable_db: None) -> None:
    engine = _engine_module()
    with pytest.raises(engine.DatabaseUnavailable), engine.connect():
        pass


def test_engine_reports_a_rejected_commit_as_proven_abort(real_engine: sa.Engine) -> None:
    """A deferred constraint fails at COMMIT: the server answered, the
    transaction is aborted, nothing persisted (10 §14 "proven abort")."""
    engine = _engine_module()
    with pytest.raises(engine.CommitRejected), engine.connect() as c:
        c.execute(
            sa.text(
                "CREATE TEMP TABLE f09_deferred (x int, CONSTRAINT f09_u UNIQUE (x) "
                "DEFERRABLE INITIALLY DEFERRED) ON COMMIT DROP"
            )
        )
        c.execute(sa.text("INSERT INTO f09_deferred VALUES (1), (1)"))


def test_engine_reports_a_lost_commit_as_outcome_unknown(real_engine: sa.Engine) -> None:
    """The connection fails while COMMIT is in flight: whether it committed
    cannot be proven (10 §14 "uncertain commit")."""
    from sqlalchemy import event

    engine = _engine_module()

    def lost(_conn: Any) -> None:
        raise sa.exc.OperationalError("COMMIT", {}, Exception("server closed the connection"))

    event.listen(real_engine, "commit", lost)
    try:
        with pytest.raises(engine.CommitOutcomeUnknown), engine.connect() as c:
            c.execute(sa.text("SELECT 1"))
    finally:
        event.remove(real_engine, "commit", lost)


def test_engine_success_and_body_failure_keep_their_semantics(real_engine: sa.Engine) -> None:
    engine = _engine_module()
    with engine.connect() as c:
        assert c.execute(sa.text("SELECT 41 + 1")).scalar_one() == 42
    with pytest.raises(ZeroDivisionError), engine.connect() as c:
        c.execute(sa.text("SELECT 1"))
        _ = 1 / 0  # a failure inside the transaction propagates unchanged (rolled back)


# ------------------------------------------------------------ the API edge says it


def test_command_with_database_unavailable_is_failed_precommit(unreachable_db: None) -> None:
    key = str(uuid.uuid4())
    r = _client().post(
        f"/workspaces/{uuid.uuid4()}/challenges",
        headers={"Idempotency-Key": key},
        json={"title": "T"},
    )
    assert r.status_code == 503
    assert r.json() == {
        "kind": "failed_precommit",
        "reasonCode": "DATABASE_UNAVAILABLE",
        "commandId": key,
    }


def test_query_with_database_unavailable_is_failed_precommit(unreachable_db: None) -> None:
    r = _client().get(f"/workspaces/{uuid.uuid4()}/overview")
    assert r.status_code == 503
    assert r.json() == {"kind": "failed_precommit", "reasonCode": "DATABASE_UNAVAILABLE"}


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/workspaces", {"name": "W"}),  # http_dispatch (older) route family
        ("/auth/login", {"email": "a@example.org", "password": "p"}),  # auth route family
    ],
)
def test_every_route_family_maps_database_unavailable(
    unreachable_db: None, path: str, body: dict[str, str]
) -> None:
    key = str(uuid.uuid4())
    r = _client().post(path, headers={"Idempotency-Key": key}, json=body)
    assert r.status_code == 503, r.text
    assert r.json() == {
        "kind": "failed_precommit",
        "reasonCode": "DATABASE_UNAVAILABLE",
        "commandId": key,
    }


def test_command_with_uncertain_commit_is_indeterminate_with_its_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import application.http_f02 as http_f02

    engine = _engine_module()

    @contextmanager
    def commit_lost() -> Iterator[Any]:
        raise engine.CommitOutcomeUnknown("connection lost during COMMIT")
        yield  # pragma: no cover

    monkeypatch.setattr(http_f02, "connect", commit_lost)
    key = str(uuid.uuid4())
    r = _client().post(
        f"/workspaces/{uuid.uuid4()}/challenges",
        headers={"Idempotency-Key": key},
        json={"title": "T"},
    )
    assert r.status_code == 503
    assert r.json() == {
        "kind": "indeterminate",
        "reasonCode": "COMMIT_OUTCOME_UNPROVEN",
        "commandId": key,
    }


def test_command_with_rejected_commit_is_failed_precommit(monkeypatch: pytest.MonkeyPatch) -> None:
    import application.http_f02 as http_f02

    engine = _engine_module()

    @contextmanager
    def commit_rejected() -> Iterator[Any]:
        raise engine.CommitRejected("deferred constraint violated at COMMIT")
        yield  # pragma: no cover

    monkeypatch.setattr(http_f02, "connect", commit_rejected)
    key = str(uuid.uuid4())
    r = _client().post(
        f"/workspaces/{uuid.uuid4()}/challenges",
        headers={"Idempotency-Key": key},
        json={"title": "T"},
    )
    assert r.status_code == 409
    assert r.json() == {
        "kind": "failed_precommit",
        "reasonCode": "COMMIT_REJECTED",
        "commandId": key,
    }


def test_unexpected_failure_never_claims_success_or_a_proven_outcome(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unknown exception may have happened after COMMIT (e.g. while building
    the response): a Command cannot claim FAILED_PRECOMMIT, a Query can (it has
    no consequence)."""
    import application.http_f02 as http_f02

    def boom(**_kw: Any) -> Any:
        raise RuntimeError("unexpected")

    monkeypatch.setattr(http_f02, "dispatch_create_challenge", boom)
    monkeypatch.setattr(http_f02, "dispatch_workspace_overview", boom)
    import nquiry_api.http.inquiry as inquiry_routes

    monkeypatch.setattr(inquiry_routes, "dispatch_create_challenge", boom)
    monkeypatch.setattr(inquiry_routes, "dispatch_workspace_overview", boom)
    key = str(uuid.uuid4())
    c = _client()
    command = c.post(
        f"/workspaces/{uuid.uuid4()}/challenges",
        headers={"Idempotency-Key": key},
        json={"title": "T"},
    )
    assert command.status_code == 500
    assert command.json() == {
        "kind": "indeterminate",
        "reasonCode": "UNEXPECTED_SERVER_FAILURE",
        "commandId": key,
    }
    query = c.get(f"/workspaces/{uuid.uuid4()}/overview")
    assert query.status_code == 500
    assert query.json() == {"kind": "failed_precommit", "reasonCode": "UNEXPECTED_SERVER_FAILURE"}


# ------------------------------------------------------------ the worker survives


def _worker(*args: str, url: str) -> subprocess.Popen[str]:
    root = Path(__file__).resolve().parents[2]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(root / p) for p in ("packages", "apps/worker/src"))
    env["DATABASE_URL"] = url
    return subprocess.Popen(
        [sys.executable, "-m", "nquiry_worker", *args],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def test_worker_once_reports_an_unavailable_database_and_fails_the_pass() -> None:
    p = _worker("--once", url=_UNREACHABLE)
    _, err = p.communicate(timeout=60)
    assert p.returncode == 3
    assert "DATABASE_UNAVAILABLE" in err


def test_worker_loop_survives_a_database_outage_and_stops_gracefully() -> None:
    p = _worker("--interval", "0.2", url=_UNREACHABLE)
    time.sleep(2.5)
    p.send_signal(signal.SIGTERM)
    _, err = p.communicate(timeout=30)
    assert p.returncode == 0, err
    assert err.count("DATABASE_UNAVAILABLE") >= 2  # it kept trying, pass after pass
    assert "stopped" in err
