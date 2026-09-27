"""WU-PFC-B5 (F05): TRN-SESS-009 BEGIN_INVESTIGATION.

Architecture: 03 TRN-SESS-009 (QUESTION_SELECTION -> INVESTIGATION; at least
one compelling selection; exactly one primary; "For the Question Burst method,
the five-level ImpactChain is complete"; DENY "Only AI recommendation exists /
No primary Question exists / ImpactChain incomplete / Authority denied";
FAILURE "Session remains QUESTION_SELECTION"); 03 §40.3, §47.7; 04
AUTH-DEP-SESS-009 (HUMAN_USER, SESSION_CONTROL_RIGHT at the specific Session;
"Selection was created by valid Question Selection Authority"; AUDIT "Link
transition authority to selection authority evidence"); HD-26 / NQ-DEC-054
(completion = exactly levels 1..5 in successive order; no confirmation after
level 5); HD-24 (Fixture stays FIXTURE_NON_PROOF).

FIRST BROKEN RELATION (before this Work Unit): TRN-SESS-009 exists only in the
domain topology; nothing realizes it, so no Session can reach INVESTIGATION.
"""

from __future__ import annotations

import uuid
from typing import Any

import f02_support as f02
import f03_support as f03
import pytest
import sqlalchemy as sa
import test_http_f02 as http_f02
import test_pfc_b4_impact_chain as b4
from test_http_f02 import _client

db_app = http_f02.db_app


def _begin(db: sa.Connection, ctx: dict[str, Any], who: Any = None, **extra: Any) -> Any:
    body = {"expectedVersion": b4._version(db, ctx), **extra}
    return b4._post(db, ctx, "transitions/begin-investigation", body, who)


def _complete_chain(db: sa.Connection, ctx: dict[str, Any], upto: int = 5) -> None:
    assert b4._create(db, ctx).json()["kind"] == "committed"
    for level in range(1, upto + 1):
        assert b4._append(db, ctx, level).json()["kind"] == "committed"


def _state(db: sa.Connection, ctx: dict[str, Any]) -> str:
    return str(f03.session_of(db, ctx["session"]).state.value)


def _blocked(r: Any, code: str) -> None:
    assert r.status_code == 422, r.text
    assert r.json() == {"kind": "blocked", "reasonCode": code}


# ------------------------------------------------------------ MUST BECOME TRUE


def test_the_controller_begins_investigation_after_selection_and_a_complete_chain(
    db_app: sa.Connection,
) -> None:
    ctx = b4._reach(db_app)
    _complete_chain(db_app, ctx)
    cap = b4._position(db_app, ctx)["actions"]["BEGIN_INVESTIGATION"]
    assert cap["available"] is True and cap["relevant"] is True
    r = _begin(db_app, ctx)
    assert r.status_code == 200 and r.json()["kind"] == "committed", r.text
    assert _state(db_app, ctx) == "INVESTIGATION"
    position = b4._position(db_app, ctx)
    assert position["session"]["proofMode"] == "FIXTURE_NON_PROOF"
    assert position["investigation"]["primaryQuestionId"] == str(ctx["question_ids"][0].value)
    assert position["investigation"]["impactChainId"] == b4._chain(db_app, ctx)["impactChainId"]
    assert position["impactChain"]["complete"] is True  # the chain stays readable


def test_the_transition_is_linked_to_the_selection_authority_evidence(
    db_app: sa.Connection,
) -> None:
    ctx = b4._reach(db_app)
    _complete_chain(db_app, ctx)
    assert _begin(db_app, ctx).json()["kind"] == "committed"
    (audit,) = f03.audit_rows(db_app, ctx, "CMD_BEGIN_INVESTIGATION")
    assert audit["actor_type"] == "HUMAN_USER" and audit["authority_source_type"] == "BINDING"
    assert audit["authority_scope_ref"] == f"SESSION:{ctx['session'].value}"
    selections = db_app.execute(
        sa.text(
            "SELECT id, human_authority_binding_id FROM question_selections WHERE session_id = :s"
        ),
        {"s": ctx["session"].value},
    ).all()
    (unit,) = db_app.execute(
        sa.text("SELECT relation_refs FROM commit_units WHERE id = :c"),
        {"c": audit["commit_id"]},
    ).scalars()
    for selection_id, binding_id in selections:
        assert f"question_selection:{selection_id}" in unit
        assert f"authority_binding:{binding_id}" in unit
    payload = db_app.execute(
        sa.text(
            "SELECT payload FROM committed_events WHERE aggregate_ref = :r "
            "AND event_type = 'SESSION_INVESTIGATION'"
        ),
        {"r": f"session:{ctx['session'].value}"},
    ).scalar_one()
    assert payload["previous_state"] == "QUESTION_SELECTION" and payload["state"] == "INVESTIGATION"
    assert payload["compelling_count"] == 1 and payload["fixture"] is True


# ------------------------------------------------------------ MUST REMAIN IMPOSSIBLE


@pytest.mark.parametrize("upto", [0, 4])
def test_an_incomplete_chain_keeps_the_session_in_question_selection(
    db_app: sa.Connection, upto: int
) -> None:
    ctx = b4._reach(db_app)
    _complete_chain(db_app, ctx, upto)
    cap = b4._position(db_app, ctx)["actions"]["BEGIN_INVESTIGATION"]
    assert cap["available"] is False and cap["reasonCode"] == "IMPACT_CHAIN_INCOMPLETE"
    _blocked(_begin(db_app, ctx), "IMPACT_CHAIN_INCOMPLETE")
    assert _state(db_app, ctx) == "QUESTION_SELECTION"


def test_no_chain_at_all_keeps_the_session_in_question_selection(db_app: sa.Connection) -> None:
    ctx = b4._reach(db_app)
    _blocked(_begin(db_app, ctx), "IMPACT_CHAIN_INCOMPLETE")


def test_no_selection_and_no_primary_keep_the_session_in_question_selection(
    db_app: sa.Connection,
) -> None:
    ctx = b4._in_selection(db_app)
    b4._grant_selector(db_app, ctx, ctx["fac"])
    _blocked(_begin(db_app, ctx), "NO_COMPELLING_QUESTION_SELECTED")
    body = {
        "questionId": str(ctx["question_ids"][0].value),
        "expectedVersion": b4._version(db_app, ctx),
    }
    assert b4._post(db_app, ctx, "question-selections", body).json()["kind"] == "committed"
    _blocked(_begin(db_app, ctx), "NO_PRIMARY_QUESTION")


def test_a_selection_not_made_under_selection_authority_blocks(db_app: sa.Connection) -> None:
    """04 AUTH-DEP-SESS-009: "Selection was created by valid Question Selection
    Authority". A selection row whose binding is the controller's
    SESSION_CONTROL_RIGHT (never a selection right) cannot carry the Session."""
    ctx = b4._reach(db_app)
    _complete_chain(db_app, ctx)
    control = db_app.execute(
        sa.text(
            "SELECT id FROM human_authority_bindings WHERE workspace_id = :w "
            "AND authority_class = 'SESSION_CONTROL_RIGHT' AND scope_type = 'SESSION' "
            "AND scope_id = :s"
        ),
        {"w": ctx["ws"].value, "s": ctx["session"].value},
    ).scalar_one()
    db_app.execute(
        sa.text(
            "INSERT INTO question_selections (id, workspace_id, session_id, question_id, "
            "selection_type, selected_by_user_id, human_authority_binding_id, selected_at, "
            "record_version) VALUES (gen_random_uuid(), :w, :s, :q, 'COMPELLING', :u, :b, "
            "now(), 1)"
        ),
        {
            "w": ctx["ws"].value,
            "s": ctx["session"].value,
            "q": ctx["question_ids"][1].value,
            "u": ctx["fac"].value,
            "b": control,
        },
    )
    _blocked(_begin(db_app, ctx), "SELECTION_AUTHORITY_INVALID")
    assert _state(db_app, ctx) == "QUESTION_SELECTION"


@pytest.mark.parametrize("who", ["owner", "participant"])
def test_only_the_session_controller_may_begin_investigation(
    db_app: sa.Connection, who: str
) -> None:
    ctx = b4._reach(db_app)
    _complete_chain(db_app, ctx)
    actor = ctx["owner"] if who == "owner" else ctx["participants"][0]
    r = _begin(db_app, ctx, who=actor)
    assert r.status_code == 403 and r.json()["kind"] == "denied", r.text
    assert _state(db_app, ctx) == "QUESTION_SELECTION"


def test_the_selector_without_session_control_cannot_begin_investigation(
    db_app: sa.Connection,
) -> None:
    """The selection right is not the operation authority (04 AUTH-DEP-SESS-009)."""
    ctx = b4._in_selection(db_app)
    selector = ctx["participants"][0]
    b4._grant_selector(db_app, ctx, selector)
    b4._select_primary(db_app, ctx, selector)
    assert b4._create(db_app, ctx, selector).json()["kind"] == "committed"
    for level in range(1, 6):
        assert b4._append(db_app, ctx, level, who=selector).json()["kind"] == "committed"
    r = _begin(db_app, ctx, who=selector)
    assert r.status_code == 403 and r.json()["kind"] == "denied", r.text
    assert _begin(db_app, ctx).json()["kind"] == "committed"  # the controller


def test_a_system_actor_cannot_begin_investigation(db_app: sa.Connection) -> None:
    from application.investigation_handler import begin_investigation
    from application.session_control_handler import SessionCommandDenied
    from authority.actor import ActorClass, ActorIdentity

    ctx = b4._reach(db_app)
    _complete_chain(db_app, ctx)
    with pytest.raises(SessionCommandDenied):
        begin_investigation(
            f02.ports(db_app),
            actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, ctx["fac"]),
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            expected_session_version=b4._version(db_app, ctx),
            ident=f03.keyed_ident(),
        )
    assert _state(db_app, ctx) == "QUESTION_SELECTION"


def test_no_selection_or_chain_change_after_investigation_begins(db_app: sa.Connection) -> None:
    ctx = b4._reach(db_app)
    _complete_chain(db_app, ctx)
    assert _begin(db_app, ctx).json()["kind"] == "committed"
    body = {
        "questionId": str(ctx["question_ids"][1].value),
        "expectedVersion": b4._version(db_app, ctx),
    }
    b4._blocked(
        b4._post(db_app, ctx, "question-selections", body), "SESSION_NOT_IN_QUESTION_SELECTION"
    )
    cap = b4._position(db_app, ctx)["actions"]["BEGIN_INVESTIGATION"]
    assert cap["relevant"] is False and cap["reasonCode"] == "SESSION_NOT_IN_QUESTION_SELECTION"


def test_a_stale_view_is_stale_and_the_same_intent_commits_once(db_app: sa.Connection) -> None:
    ctx = b4._reach(db_app)
    _complete_chain(db_app, ctx)
    stale = _begin(db_app, ctx, expectedVersion=1)
    assert stale.status_code == 409 and stale.json()["kind"] == "stale"
    ws, sid = ctx["ws"].value, ctx["session"].value
    url = f"/workspaces/{ws}/sessions/{sid}/transitions/begin-investigation"
    key = {"Idempotency-Key": str(uuid.uuid4())}
    body = {"expectedVersion": b4._version(db_app, ctx)}
    client = _client(db_app, ctx["fac"])
    assert client.post(url, headers=key, json=body).json()["kind"] == "committed"
    assert client.post(url, headers=key, json=body).json()["kind"] == "committed"
    assert len(f03.audit_rows(db_app, ctx, "CMD_BEGIN_INVESTIGATION")) == 1
