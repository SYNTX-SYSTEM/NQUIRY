"""WU-PFC-B3 (F05): the QuestionSelection product path (TRN-SEL-001/002).

Architecture: 03 §39 TRN-SEL-001 SELECT_COMPELLING_QUESTION / TRN-SEL-002
SELECT_PRIMARY_QUESTION (Session stays QUESTION_SELECTION; human actor; Question
of the Session's Challenge; DENY AI selection, another Workspace/Challenge,
cardinality; "No conflicting primary selection exists unless explicit
replacement semantics are authorized later"); 04 AUTH-DEP-SEL-001/002
(QUESTION_SELECTION_RIGHT, "AUTHORITY SCOPE: Specific Session", 1 to 3
compelling); 05 §40 (multiple active bindings "only if later policy defines"
their conflict resolution); 09 §85 (POST question-selections, POST
primary-question, GET question-selections; payload question_id +
expected_session_version); 12 §6 / AC-12-004 ("Exactly one active
QUESTION_SELECTION_RIGHT holder for prototype Session"); 12 row 19.

FIRST BROKEN RELATION (before this Work Unit): the governed SelectQuestion
handler exists, but no product path reaches it (no route, capability or read
model), so a Session in QUESTION_SELECTION cannot record a human selection.
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
from test_http_f02 import _client

db_app = http_f02.db_app


def _post(
    db: sa.Connection, ctx: dict[str, Any], path: str, body: dict[str, Any], who: Any = None
) -> Any:
    ws, sid = ctx["ws"].value, ctx["session"].value
    return _client(db, who or ctx["fac"]).post(
        f"/workspaces/{ws}/sessions/{sid}/{path}",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        json=body,
    )


def _version(db: sa.Connection, ctx: dict[str, Any]) -> int:
    return int(f03.session_of(db, ctx["session"]).record_version.value)


def _grant_selector(db: sa.Connection, ctx: dict[str, Any], member: Any) -> None:
    f02.grant(
        db,
        owner=ctx["owner"],
        workspace_id=ctx["ws"],
        member=member,
        authority_class="QUESTION_SELECTION_RIGHT",
        scope_type="SESSION",
        scope_id=ctx["session"].value,
    )


def _reach(db: sa.Connection, *, selector: bool = True) -> dict[str, Any]:
    """A Fixture Session with four raw Questions in QUESTION_SELECTION (B1, B2).
    The controller is also the one QUESTION_SELECTION_RIGHT holder (12 §8
    bootstrap: Alpha)."""
    ctx = f04.capture_context(
        db, texts=(*f04.QUESTIONS, "Who decides what matters here?"), fixture=True
    )
    ctx["oa1"] = f04.begin(db, ctx).authorization_id
    assert f04.run(db, ctx, ctx["oa1"]).status == "ACCEPTED"
    v = _version(db, ctx)
    assert _post(db, ctx, "transitions/begin-reflection", {"expectedVersion": v}).json()[
        "kind"
    ] == ("committed")
    v = _version(db, ctx)
    r = _post(
        db,
        ctx,
        "transitions/begin-question-selection",
        {"expectedVersion": v, "reflectionCompletionConfirmed": True},
    )
    assert r.json()["kind"] == "committed", r.text
    if selector:
        _grant_selector(db, ctx, ctx["fac"])
    return ctx


def _select(
    db: sa.Connection, ctx: dict[str, Any], i: int, *, primary: bool = False, who: Any = None
) -> Any:
    path = "primary-question" if primary else "question-selections"
    body = {"questionId": str(ctx["question_ids"][i].value), "expectedVersion": _version(db, ctx)}
    return _post(db, ctx, path, body, who)


def _position(db: sa.Connection, ctx: dict[str, Any], who: Any = None) -> dict[str, Any]:
    ws, sid = ctx["ws"].value, ctx["session"].value
    return (  # type: ignore[no-any-return]
        _client(db, who or ctx["fac"]).get(f"/workspaces/{ws}/sessions/{sid}/position").json()
    )


def _blocked(r: Any, code: str) -> None:
    assert r.status_code == 422, r.text
    assert r.json() == {"kind": "blocked", "reasonCode": code}


# ------------------------------------------------------------ MUST BECOME TRUE


def test_the_selector_records_a_compelling_question(db_app: sa.Connection) -> None:
    ctx = _reach(db_app)
    caps = _position(db_app, ctx)["actions"]
    assert caps["SELECT_COMPELLING_QUESTION"]["available"] is True
    assert caps["SELECT_COMPELLING_QUESTION"]["relevant"] is True
    version = _version(db_app, ctx)
    r = _select(db_app, ctx, 0)
    assert r.status_code == 200 and r.json()["kind"] == "committed", r.text
    assert r.json()["selectionType"] == "COMPELLING"
    (audit,) = f03.audit_rows(db_app, ctx, "CMD_SELECT_COMPELLING_QUESTION")
    assert audit["actor_type"] == "HUMAN_USER" and audit["authority_source_type"] == "BINDING"
    assert audit["authority_scope_ref"] == f"SESSION:{ctx['session'].value}"
    session = f03.session_of(db_app, ctx["session"])
    assert session.state.value == "QUESTION_SELECTION" and session.record_version.value == version


def test_the_selector_records_the_primary_question(db_app: sa.Connection) -> None:
    ctx = _reach(db_app)
    assert _select(db_app, ctx, 0).json()["kind"] == "committed"
    r = _select(db_app, ctx, 0, primary=True)
    assert r.status_code == 200 and r.json()["selectionType"] == "PRIMARY", r.text
    selection = _position(db_app, ctx)["selection"]
    assert selection["primaryQuestionId"] == str(ctx["question_ids"][0].value)
    assert _position(db_app, ctx)["actions"]["SELECT_PRIMARY_QUESTION"]["reasonCode"] == (
        "PRIMARY_ALREADY_SELECTED"
    )


def test_selections_are_readable_and_stay_fixture_non_proof(db_app: sa.Connection) -> None:
    ctx = _reach(db_app)
    assert _select(db_app, ctx, 1).json()["kind"] == "committed"
    ws, sid = ctx["ws"].value, ctx["session"].value
    listed = (
        _client(db_app, ctx["participants"][0])
        .get(f"/workspaces/{ws}/sessions/{sid}/question-selections")
        .json()
    )
    assert listed["kind"] == "ok" and listed["proofMode"] == "FIXTURE_NON_PROOF"
    (item,) = listed["selections"]
    assert item["questionId"] == str(ctx["question_ids"][1].value)
    assert item["selectionType"] == "COMPELLING"
    assert item["selectedByUserId"] == str(ctx["fac"].value)
    assert _position(db_app, ctx)["selection"]["selections"] == listed["selections"]
    assert _position(db_app, ctx)["session"]["proofMode"] == "FIXTURE_NON_PROOF"


# ------------------------------------------------------------ MUST REMAIN IMPOSSIBLE


def test_without_question_selection_right_the_selection_is_denied(db_app: sa.Connection) -> None:
    ctx = _reach(db_app, selector=False)
    cap = _position(db_app, ctx)["actions"]["SELECT_COMPELLING_QUESTION"]
    assert cap["available"] is False and cap["reasonCode"] == "NO_QUESTION_SELECTION_RIGHT"
    r = _select(db_app, ctx, 0)
    assert r.status_code == 403 and r.json()["kind"] == "denied", r.text
    assert f03.audit_rows(db_app, ctx, "CMD_SELECT_COMPELLING_QUESTION") == []


def test_a_second_active_selector_blocks_selection(db_app: sa.Connection) -> None:
    """12 AC-12-004 / 05 §40: one active holder; no conflict policy exists."""
    ctx = _reach(db_app)
    _grant_selector(db_app, ctx, ctx["participants"][0])
    assert _position(db_app, ctx)["actions"]["SELECT_COMPELLING_QUESTION"]["reasonCode"] == (
        "SELECTOR_NOT_UNIQUE"
    )
    _blocked(_select(db_app, ctx, 0), "SELECTOR_NOT_UNIQUE")
    _blocked(_select(db_app, ctx, 0, who=ctx["participants"][0]), "SELECTOR_NOT_UNIQUE")


def test_at_most_three_compelling_questions(db_app: sa.Connection) -> None:
    ctx = _reach(db_app)
    for i in range(3):
        assert _select(db_app, ctx, i).json()["kind"] == "committed"
    assert _position(db_app, ctx)["actions"]["SELECT_COMPELLING_QUESTION"]["reasonCode"] == (
        "COMPELLING_LIMIT_REACHED"
    )
    _blocked(_select(db_app, ctx, 3), "COMPELLING_LIMIT_REACHED")


def test_no_conflicting_primary_and_no_duplicate_selection(db_app: sa.Connection) -> None:
    ctx = _reach(db_app)
    assert _select(db_app, ctx, 0).json()["kind"] == "committed"
    _blocked(_select(db_app, ctx, 0), "QUESTION_ALREADY_SELECTED")
    assert _select(db_app, ctx, 0, primary=True).json()["kind"] == "committed"
    _blocked(_select(db_app, ctx, 1, primary=True), "PRIMARY_ALREADY_SELECTED")


def test_selection_is_only_possible_in_question_selection(db_app: sa.Connection) -> None:
    ctx = f04.analysis_context(db_app, fixture=True)  # ANALYSIS
    _grant_selector(db_app, ctx, ctx["fac"])
    cap = _position(db_app, ctx)["actions"]["SELECT_COMPELLING_QUESTION"]
    assert cap["relevant"] is False and cap["reasonCode"] == "SESSION_NOT_IN_QUESTION_SELECTION"
    _blocked(_select(db_app, ctx, 0), "SESSION_NOT_IN_QUESTION_SELECTION")


def test_a_question_of_another_workspace_is_denied(db_app: sa.Connection) -> None:
    ctx = _reach(db_app)
    other = f04.capture_context(db_app, fixture=True)
    body = {
        "questionId": str(other["question_ids"][0].value),
        "expectedVersion": _version(db_app, ctx),
    }
    r = _post(db_app, ctx, "question-selections", body)
    assert r.status_code == 403 and r.json()["kind"] == "denied", r.text


def test_a_system_actor_cannot_select(db_app: sa.Connection) -> None:
    from application.selection_command import select_in_session
    from application.session_control_handler import SessionCommandDenied
    from authority.actor import ActorClass, ActorIdentity
    from domain.question_selection import SelectionType

    ctx = _reach(db_app)
    with pytest.raises(SessionCommandDenied):  # BND-001 at the F09-2 precheck
        select_in_session(
            f02.ports(db_app),
            actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, ctx["fac"]),
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            question_id=ctx["question_ids"][0],
            selection_type=SelectionType.COMPELLING,
            expected_session_version=_version(db_app, ctx),
            ident=f03.keyed_ident(),
        )
    assert f03.audit_rows(db_app, ctx, "CMD_SELECT_COMPELLING_QUESTION") == []


def test_the_session_row_is_locked_before_the_selection_is_decided(
    db_app: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The 04 §41 cap and the one-primary rule are cross-row facts: concurrent
    selections must serialize on the Session row."""
    from application import selection_command
    from domain.question_selection import SelectionType
    from persistence.session_repository import SqlAlchemySessionRepository

    ctx = _reach(db_app)
    calls: list[Any] = []
    original = SqlAlchemySessionRepository.get_for_update

    def spy(self: Any, session_id: Any) -> Any:
        calls.append(session_id)
        return original(self, session_id)

    monkeypatch.setattr(SqlAlchemySessionRepository, "get_for_update", spy)
    selection_command.select_in_session(
        f02.ports(db_app),
        actor=f02.human(ctx["fac"]),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        question_id=ctx["question_ids"][0],
        selection_type=SelectionType.COMPELLING,
        expected_session_version=_version(db_app, ctx),
        ident=f03.keyed_ident(),
    )
    assert calls == [ctx["session"]]


def test_a_stale_view_is_stale_and_the_same_intent_commits_once(db_app: sa.Connection) -> None:
    ctx = _reach(db_app)
    body = {"questionId": str(ctx["question_ids"][0].value), "expectedVersion": 1}
    stale = _post(db_app, ctx, "question-selections", body)
    assert stale.status_code == 409 and stale.json()["kind"] == "stale"
    ws, sid = ctx["ws"].value, ctx["session"].value
    url = f"/workspaces/{ws}/sessions/{sid}/question-selections"
    key = {"Idempotency-Key": str(uuid.uuid4())}
    body["expectedVersion"] = _version(db_app, ctx)
    client = _client(db_app, ctx["fac"])
    assert client.post(url, headers=key, json=body).json()["kind"] == "committed"
    assert client.post(url, headers=key, json=body).json()["kind"] == "committed"
    assert len(f03.audit_rows(db_app, ctx, "CMD_SELECT_COMPELLING_QUESTION")) == 1


@pytest.mark.parametrize("bad", [None, "not-a-uuid", 7])
def test_a_malformed_question_reference_is_rejected(db_app: sa.Connection, bad: Any) -> None:
    ctx = _reach(db_app)
    r = _post(
        db_app,
        ctx,
        "question-selections",
        {"questionId": bad, "expectedVersion": _version(db_app, ctx)},
    )
    assert r.status_code == 400 and r.json()["kind"] == "rejected", r.text
