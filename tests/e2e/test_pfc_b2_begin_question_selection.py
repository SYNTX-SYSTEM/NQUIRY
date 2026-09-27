"""WU-PFC-B2 (F05): TRN-SESS-008 BEGIN_QUESTION_SELECTION under HD-25 / NQ-DEC-053.

Architecture: 03 TRN-SESS-008 (REFLECTION -> QUESTION_SELECTION; "Reflection
phase has been explicitly completed according to later contract"; "No AI output
may create the selection transition by itself"; REQUIRED EVIDENCE "SYSTEM_PROOF
of Reflection phase completion"; "Reflection response persistence is not
required by 03"; FAILURE "Session remains REFLECTION"); 03 §52 GAP-03-007; 04
AUTH-DEP-SESS-008 (SESSION_CONTROL_RIGHT; "No selection decision occurs merely
by opening the phase"; DENY "Only UI navigation. Only AI output."; SYSTEM-DERIVED
not enabled; AUDIT "Record controller authority and completion proof basis").

Human Authority HD-25 (2026-09-27): completion = explicit human procedural
confirmation by the SESSION_CONTROL_RIGHT holder; zero responses allowed; no
separate Reflection-complete state or transition; carried by
CMD_BEGIN_QUESTION_SELECTION; a request without the explicit confirmation is
refused; the basis is audited as HUMAN_PROCEDURAL_CONFIRMATION; Fixture Sessions
keep FIXTURE_NON_PROOF in QUESTION_SELECTION.

FIRST BROKEN RELATION (before this Work Unit): TRN-SESS-008 exists only in the
domain topology; nothing realizes it, so a Session in REFLECTION cannot move on.
"""

from __future__ import annotations

import uuid
from typing import Any

import f02_support as f02
import f03_support as f03
import f04_support as f04
import pytest
import sqlalchemy as sa
import test_http_f02 as http_f02
from persistence.tables import sessions_table
from test_http_f02 import _client

db_app = http_f02.db_app
BASIS = "HUMAN_PROCEDURAL_CONFIRMATION"


def _in_reflection(db: sa.Connection) -> dict[str, Any]:
    ctx = f04.analysis_context(db, fixture=True)
    assert f04.run(db, ctx, ctx["oa1"]).status == "ACCEPTED"
    r = _post(db, ctx, "begin-reflection", {})
    assert r.json()["kind"] == "committed", r.text
    return ctx


def _version(db: sa.Connection, ctx: dict[str, Any]) -> int:
    return int(f03.session_of(db, ctx["session"]).record_version.value)


def _state(db: sa.Connection, ctx: dict[str, Any]) -> str:
    return str(
        db.execute(
            sa.select(sessions_table.c.state).where(sessions_table.c.id == ctx["session"].value)
        ).scalar_one()
    )


def _post(
    db: sa.Connection, ctx: dict[str, Any], action: str, extra: dict[str, Any], who: Any = None
) -> Any:
    body = {"expectedVersion": _version(db, ctx), **extra}
    ws, sid = ctx["ws"].value, ctx["session"].value
    return _client(db, who or ctx["fac"]).post(
        f"/workspaces/{ws}/sessions/{sid}/transitions/{action}",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        json=body,
    )


def _begin(db: sa.Connection, ctx: dict[str, Any], who: Any = None, **extra: Any) -> Any:
    return _post(db, ctx, "begin-question-selection", extra, who)


def _position(db: sa.Connection, ctx: dict[str, Any]) -> dict[str, Any]:
    ws, sid = ctx["ws"].value, ctx["session"].value
    return _client(db, ctx["fac"]).get(f"/workspaces/{ws}/sessions/{sid}/position").json()  # type: ignore[no-any-return]


# ------------------------------------------------------------ MUST BECOME TRUE


def test_explicit_confirmation_moves_the_session_into_question_selection(
    db_app: sa.Connection,
) -> None:
    ctx = _in_reflection(db_app)
    cap = _position(db_app, ctx)["actions"]["BEGIN_QUESTION_SELECTION"]
    assert cap["available"] is True and cap["relevant"] is True
    assert cap["requiresReflectionCompletionConfirmation"] is True
    r = _begin(db_app, ctx, reflectionCompletionConfirmed=True)
    assert r.status_code == 200 and r.json()["kind"] == "committed", r.text
    assert r.json()["reflectionCompletionBasis"] == BASIS
    assert _state(db_app, ctx) == "QUESTION_SELECTION"


def test_zero_reflection_responses_are_enough(db_app: sa.Connection) -> None:
    """HD-25 (C-c): no response exists anywhere, and none is asked for."""
    ctx = _in_reflection(db_app)
    assert _begin(db_app, ctx, reflectionCompletionConfirmed=True).json()["kind"] == "committed"


def test_the_completion_basis_is_audited_and_committed(db_app: sa.Connection) -> None:
    ctx = _in_reflection(db_app)
    assert _begin(db_app, ctx, reflectionCompletionConfirmed=True).json()["kind"] == "committed"
    (audit,) = f03.audit_rows(db_app, ctx, "CMD_BEGIN_QUESTION_SELECTION")
    assert audit["authority_source_type"] == "BINDING" and audit["actor_type"] == "HUMAN_USER"
    assert audit["authority_scope_ref"] == f"SESSION:{ctx['session'].value}"
    assert f"reflection_completion:{BASIS}" in audit["state_after_ref"]
    payload = db_app.execute(
        sa.text(
            "SELECT payload FROM committed_events WHERE aggregate_ref = :r "
            "AND event_type = 'SESSION_QUESTION_SELECTION'"
        ),
        {"r": f"session:{ctx['session'].value}"},
    ).scalar_one()
    assert payload["reflection_completion_basis"] == BASIS
    assert payload["previous_state"] == "REFLECTION" and payload["state"] == "QUESTION_SELECTION"
    assert payload["fixture"] is True


def test_a_fixture_session_keeps_fixture_non_proof_in_question_selection(
    db_app: sa.Connection,
) -> None:
    ctx = _in_reflection(db_app)
    assert _begin(db_app, ctx, reflectionCompletionConfirmed=True).json()["kind"] == "committed"
    position = _position(db_app, ctx)
    assert position["session"]["state"] == "QUESTION_SELECTION"
    assert position["session"]["fixture"] is True
    assert position["session"]["proofMode"] == "FIXTURE_NON_PROOF"
    assert position["reflection"]["proofClass"] == "MOCK_NON_PROOF"
    assert position["reflection"]["isRealProviderProof"] is False
    assert position["reflectionCompletion"] == {"basis": BASIS}


# ------------------------------------------------------------ MUST REMAIN IMPOSSIBLE


@pytest.mark.parametrize(
    "extra",
    [{}, {"reflectionCompletionConfirmed": False}, {"reflectionCompletionConfirmed": None}],
)
def test_without_explicit_confirmation_the_session_remains_in_reflection(
    db_app: sa.Connection, extra: dict[str, Any]
) -> None:
    ctx = _in_reflection(db_app)
    version = _version(db_app, ctx)
    r = _begin(db_app, ctx, **extra)
    assert r.status_code == 422, r.text
    assert r.json() == {"kind": "blocked", "reasonCode": "REFLECTION_COMPLETION_NOT_CONFIRMED"}
    assert _state(db_app, ctx) == "REFLECTION" and _version(db_app, ctx) == version


@pytest.mark.parametrize("bad", ["true", 1, "yes"])
def test_a_non_boolean_confirmation_is_refused(db_app: sa.Connection, bad: Any) -> None:
    ctx = _in_reflection(db_app)
    r = _begin(db_app, ctx, reflectionCompletionConfirmed=bad)
    assert r.status_code == 400 and r.json()["kind"] == "rejected"
    assert _state(db_app, ctx) == "REFLECTION"


@pytest.mark.parametrize("who", ["owner", "participant"])
def test_only_the_session_controller_may_confirm(db_app: sa.Connection, who: str) -> None:
    ctx = _in_reflection(db_app)
    actor = ctx["owner"] if who == "owner" else ctx["participants"][0]
    r = _begin(db_app, ctx, who=actor, reflectionCompletionConfirmed=True)
    assert r.status_code == 403 and r.json()["kind"] == "denied", r.text
    assert _state(db_app, ctx) == "REFLECTION"


def test_system_derived_completion_stays_unavailable(db_app: sa.Connection) -> None:
    from application.reflection_handler import begin_question_selection
    from application.session_control_handler import SessionCommandDenied
    from authority.actor import ActorClass, ActorIdentity

    ctx = _in_reflection(db_app)
    with pytest.raises(SessionCommandDenied):
        begin_question_selection(
            f02.ports(db_app),
            actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, ctx["fac"]),
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            expected_session_version=_version(db_app, ctx),
            reflection_completion_confirmed=True,
            ident=f03.keyed_ident(),
        )
    assert _state(db_app, ctx) == "REFLECTION"


def test_it_is_only_legal_from_reflection(db_app: sa.Connection) -> None:
    ctx = f04.analysis_context(db_app, fixture=True)  # still ANALYSIS
    cap = _position(db_app, ctx)["actions"]["BEGIN_QUESTION_SELECTION"]
    assert cap["available"] is False and cap["relevant"] is False
    assert cap["reasonCode"] == "SESSION_NOT_IN_REFLECTION"
    r = _begin(db_app, ctx, reflectionCompletionConfirmed=True)
    assert r.status_code == 422 and r.json()["reasonCode"] == "SESSION_NOT_IN_REFLECTION"
    assert _state(db_app, ctx) == "ANALYSIS"


def test_no_separate_reflection_complete_state_or_transition_exists() -> None:
    from domain.session import SessionState
    from domain.session_transitions import SessionTransitionId

    assert not any("COMPLETE" in s.name and "REFLECTION" in s.name for s in SessionState)
    assert not any("REFLECTION_COMPLETE" in t.name for t in SessionTransitionId)


def test_a_stale_view_is_answered_as_stale_and_the_same_intent_commits_once(
    db_app: sa.Connection,
) -> None:
    ctx = _in_reflection(db_app)
    stale = _begin(db_app, ctx, expectedVersion=1, reflectionCompletionConfirmed=True)
    assert stale.status_code == 409 and stale.json()["kind"] == "stale"
    ws, sid = ctx["ws"].value, ctx["session"].value
    url = f"/workspaces/{ws}/sessions/{sid}/transitions/begin-question-selection"
    key = {"Idempotency-Key": str(uuid.uuid4())}
    body = {"expectedVersion": _version(db_app, ctx), "reflectionCompletionConfirmed": True}
    client = _client(db_app, ctx["fac"])
    assert client.post(url, headers=key, json=body).json()["kind"] == "committed"
    assert client.post(url, headers=key, json=body).json()["kind"] == "committed"
    assert len(f03.audit_rows(db_app, ctx, "CMD_BEGIN_QUESTION_SELECTION")) == 1
