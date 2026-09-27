"""WU-PFC-B0 (F05 prerequisite): Fixture Session identity (HD-24 / NQ-DEC-052).

Human Authority (HD-24, 2026-09-27), rules 1-5:
1. A Session may be declared a Fixture Session only at Session creation.
2. The Fixture Session marker is immutable after creation.
3. A normal Session can never be converted into a Fixture Session.
4. A Fixture Session can never be converted into a real Session.
5. Every state, read model, API representation and projection that exposes
   Session proof semantics must preserve the Fixture / NON_PROOF status.

FIRST BROKEN RELATION (before this Work Unit): the Session has no Fixture
identity at all (no field, column, Command input, event fact or projection), so
the Option 03 proof path of HD-24 has nothing to bind to.
"""

from __future__ import annotations

import uuid
from typing import Any

import f02_support as f02
import pytest
import sqlalchemy as sa
import test_http_f02 as http_f02
from persistence.tables import sessions_table
from test_http_f02 import _client

db_app = http_f02.db_app


def _create(client: Any, ctx: dict[str, Any], body: Any = None, key: str | None = None) -> Any:
    url = f"/workspaces/{ctx['ws'].value}/challenges/{ctx['challenge'].challenge_id.value}/sessions"
    headers = {"Idempotency-Key": key or str(uuid.uuid4())}
    if body is None:
        return client.post(url, headers=headers)
    return client.post(url, headers=headers, json=body)


def _row(db: sa.Connection, session_id: str) -> Any:
    return (
        db.execute(sa.select(sessions_table).where(sessions_table.c.id == uuid.UUID(session_id)))
        .mappings()
        .one()
    )


def _created(db: sa.Connection, ctx: dict[str, Any], body: Any = None) -> str:
    r = _create(_client(db, ctx["fac"]), ctx, body)
    assert r.status_code == 200 and r.json()["kind"] == "committed", r.text
    return str(r.json()["sessionId"])


def _position(db: sa.Connection, ctx: dict[str, Any], session_id: str) -> dict[str, Any]:
    r = _client(db, ctx["fac"]).get(f"/workspaces/{ctx['ws'].value}/sessions/{session_id}/position")
    assert r.status_code == 200, r.text
    return r.json()  # type: ignore[no-any-return]


# ------------------------------------------------------------ MUST BECOME TRUE


def test_a_fixture_session_is_declared_at_creation_and_projected_as_non_proof(
    db_app: sa.Connection,
) -> None:
    ctx = f02.inquiry_context(db_app)
    sid = _created(db_app, ctx, {"fixture": True})
    assert _row(db_app, sid)["fixture"] is True
    session = _position(db_app, ctx, sid)["session"]
    assert session["fixture"] is True and session["proofMode"] == "FIXTURE_NON_PROOF"
    detail = (
        _client(db_app, ctx["fac"])
        .get(f"/workspaces/{ctx['ws'].value}/challenges/{ctx['challenge'].challenge_id.value}")
        .json()
    )
    (listed,) = [s for s in detail["sessions"] if s["sessionId"] == sid]
    assert listed["fixture"] is True and listed["proofMode"] == "FIXTURE_NON_PROOF"
    legacy = _client(db_app, ctx["fac"]).get(f"/workspaces/{ctx['ws'].value}/sessions/{sid}").json()
    assert legacy["data"]["session"]["fixture"] is True


def test_a_normal_session_is_governed_by_default(db_app: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_app)
    for body in (None, {}, {"fixture": False}):
        sid = _created(db_app, ctx, body)
        assert _row(db_app, sid)["fixture"] is False
        session = _position(db_app, ctx, sid)["session"]
        assert session["fixture"] is False and session["proofMode"] == "GOVERNED"


def test_the_fixture_fact_is_part_of_the_committed_event(db_app: sa.Connection) -> None:
    from events.contracts import PRODUCTION_EVENT_CONTRACTS

    ctx = f02.inquiry_context(db_app)
    sid = _created(db_app, ctx, {"fixture": True})
    event = db_app.execute(
        sa.text(
            "SELECT payload, event_schema_version FROM committed_events "
            "WHERE aggregate_ref = :r AND event_type = 'SESSION_CREATED'"
        ),
        {"r": f"session:{sid}"},
    ).one()
    assert event.payload["fixture"] is True
    assert (
        event.event_schema_version
        == PRODUCTION_EVENT_CONTRACTS["SESSION_CREATED"].schema_version.value
    )
    assert (
        event.event_schema_version != "1.0"
    )  # the payload shape changed: the schema version moved


def test_the_session_read_model_preserves_the_fixture_status(db_app: sa.Connection) -> None:
    from nquiry_worker.delivery import run_delivery_pass
    from projection.delivery import DeliveryPorts
    from test_support.clock import FixedClock

    ctx = f02.inquiry_context(db_app)
    sid = _created(db_app, ctx, {"fixture": True})
    run_delivery_pass(DeliveryPorts(db_app), clock=FixedClock(f02.NOW))
    fixture = db_app.execute(
        sa.text("SELECT fixture FROM session_read_model WHERE session_id = :s"),
        {"s": uuid.UUID(sid)},
    ).scalar_one()
    assert fixture is True


# ------------------------------------------------------------ MUST REMAIN IMPOSSIBLE


@pytest.mark.parametrize("initial", [True, False])
def test_the_marker_is_immutable_in_both_directions(db_app: sa.Connection, initial: bool) -> None:
    ctx = f02.inquiry_context(db_app)
    sid = _created(db_app, ctx, {"fixture": initial})
    with pytest.raises(sa.exc.DBAPIError), db_app.begin_nested():
        db_app.execute(
            sa.update(sessions_table)
            .where(sessions_table.c.id == uuid.UUID(sid))
            .values(fixture=not initial)
        )
    assert _row(db_app, sid)["fixture"] is initial


@pytest.mark.parametrize("initial", [True, False])
def test_no_command_converts_a_session(db_app: sa.Connection, initial: bool) -> None:
    """A later governed Command that names `fixture` cannot change it."""
    ctx = f02.inquiry_context(db_app)
    sid = _created(db_app, ctx, {"fixture": initial})
    f02.grant(
        db_app,
        owner=ctx["owner"],
        workspace_id=ctx["ws"],
        member=ctx["fac"],
        authority_class="SESSION_CONTROL_RIGHT",
        scope_type="SESSION",
        scope_id=uuid.UUID(sid),
    )
    r = _client(db_app, ctx["fac"]).post(
        f"/workspaces/{ctx['ws'].value}/sessions/{sid}/transitions/begin-setup",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        json={"expectedVersion": 1, "fixture": not initial},
    )
    assert r.json()["kind"] == "committed", r.text
    assert _row(db_app, sid)["fixture"] is initial
    assert _position(db_app, ctx, sid)["session"]["fixture"] is initial


@pytest.mark.parametrize("bad", ["true", 1, None, {"x": 1}])
def test_a_non_boolean_declaration_is_rejected_and_nothing_is_created(
    db_app: sa.Connection, bad: Any
) -> None:
    ctx = f02.inquiry_context(db_app)
    before = db_app.execute(sa.select(sa.func.count()).select_from(sessions_table)).scalar_one()
    r = _create(_client(db_app, ctx["fac"]), ctx, {"fixture": bad})
    assert r.status_code == 400 and r.json()["kind"] == "rejected", r.text
    assert (
        db_app.execute(sa.select(sa.func.count()).select_from(sessions_table)).scalar_one()
        == before
    )


def test_the_same_intent_cannot_be_replayed_with_another_fixture_declaration(
    db_app: sa.Connection,
) -> None:
    ctx = f02.inquiry_context(db_app)
    key = str(uuid.uuid4())
    client = _client(db_app, ctx["fac"])
    first = _create(client, ctx, {"fixture": True}, key)
    assert first.json()["kind"] == "committed"
    replay = _create(client, ctx, {"fixture": True}, key)
    assert replay.json()["sessionId"] == first.json()["sessionId"]
    other = _create(client, ctx, {"fixture": False}, key)
    assert other.json()["kind"] == "rejected"
    assert _row(db_app, first.json()["sessionId"])["fixture"] is True
