"""WU-PFC-B4 (F05): the Five-Why ImpactChain product path under HD-26.

Architecture: 02 §28 (canonical aggregate anchored to the selected Question;
each answer an owned ordered node); 03 §5 (anchored in QUESTION_SELECTION),
§40 (complete = exactly the five ordered answer nodes; "No AI may fill missing
answers"); 09 §48 (fields), §63 (CMD_CREATE_IMPACT_CHAIN,
CMD_APPEND_IMPACT_CHAIN_NODE), §86 (the anchor is the current primary; levels
ordered; no duplicate level; a human actor).

Human Authority HD-26 / NQ-DEC-054: the QUESTION_SELECTION_RIGHT holder who
selected the current primary Question is the sole author (Option A);
SESSION_CONTROL_RIGHT and PARTICIPATION confer nothing; AI nothing; nodes are
append-only (S1(i)); one chain per current primary (S2(i)); levels strictly
successive; every node keeps author, level, capture time, chain, Session and
primary anchor; Fixture Sessions stay FIXTURE_NON_PROOF.

FIRST BROKEN RELATION (before this Work Unit): no ImpactChain exists anywhere
(no table, Command, route or view), so TRN-SESS-009's "complete five-level
ImpactChain" can never be proven.
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
ANSWERS = (
    "Customers who leave early never see the value.",
    "Without the value they do not renew.",
    "Renewals fund the product.",
    "Without funding the team cannot improve onboarding.",
    "So the first month decides whether we survive.",
)


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


def _in_selection(db: sa.Connection) -> dict[str, Any]:
    """A Fixture Session in QUESTION_SELECTION (B1, B2); no selector yet."""
    ctx = f04.analysis_context(db, fixture=True)
    assert f04.run(db, ctx, ctx["oa1"]).status == "ACCEPTED"
    body = {"expectedVersion": _version(db, ctx)}
    assert _post(db, ctx, "transitions/begin-reflection", body).json()["kind"] == "committed"
    body = {"expectedVersion": _version(db, ctx), "reflectionCompletionConfirmed": True}
    r = _post(db, ctx, "transitions/begin-question-selection", body)
    assert r.json()["kind"] == "committed", r.text
    return ctx


def _select_primary(db: sa.Connection, ctx: dict[str, Any], who: Any) -> None:
    body = {"questionId": str(ctx["question_ids"][0].value), "expectedVersion": _version(db, ctx)}
    assert _post(db, ctx, "question-selections", body, who).json()["kind"] == "committed"
    assert _post(db, ctx, "primary-question", body, who).json()["kind"] == "committed"


def _reach(db: sa.Connection) -> dict[str, Any]:
    """The Facilitator (controller) is the one selector and selected the primary."""
    ctx = _in_selection(db)
    _grant_selector(db, ctx, ctx["fac"])
    _select_primary(db, ctx, ctx["fac"])
    return ctx


def _create(db: sa.Connection, ctx: dict[str, Any], who: Any = None) -> Any:
    return _post(db, ctx, "impact-chain", {"expectedVersion": _version(db, ctx)}, who)


def _chain(db: sa.Connection, ctx: dict[str, Any], who: Any = None) -> dict[str, Any]:
    ws, sid = ctx["ws"].value, ctx["session"].value
    return (  # type: ignore[no-any-return]
        _client(db, who or ctx["fac"]).get(f"/workspaces/{ws}/sessions/{sid}/impact-chain").json()
    )


def _append(
    db: sa.Connection, ctx: dict[str, Any], level: int, answer: Any = None, who: Any = None
) -> Any:
    body = {
        "expectedChainVersion": _chain(db, ctx)["version"],
        "level": level,
        "answer": ANSWERS[level - 1] if answer is None and level <= 5 else answer,
    }
    return _post(db, ctx, "impact-chain/nodes", body, who)


def _position(db: sa.Connection, ctx: dict[str, Any], who: Any = None) -> dict[str, Any]:
    ws, sid = ctx["ws"].value, ctx["session"].value
    return (  # type: ignore[no-any-return]
        _client(db, who or ctx["fac"]).get(f"/workspaces/{ws}/sessions/{sid}/position").json()
    )


def _blocked(r: Any, code: str) -> None:
    assert r.status_code == 422, r.text
    assert r.json() == {"kind": "blocked", "reasonCode": code}


def _denied(r: Any, code: str | None = None) -> None:
    assert r.status_code == 403 and r.json()["kind"] == "denied", r.text
    if code is not None:
        assert r.json()["reasonCode"] == code


# ------------------------------------------------------------ MUST BECOME TRUE


def test_the_primary_selector_creates_the_chain_and_appends_five_successive_levels(
    db_app: sa.Connection,
) -> None:
    ctx = _reach(db_app)
    caps = _position(db_app, ctx)["actions"]
    assert caps["CREATE_IMPACT_CHAIN"]["available"] is True
    assert caps["CREATE_IMPACT_CHAIN"]["relevant"] is True
    r = _create(db_app, ctx)
    assert r.status_code == 200 and r.json()["kind"] == "committed", r.text
    assert _position(db_app, ctx)["actions"]["APPEND_IMPACT_CHAIN_NODE"]["available"] is True
    for level in range(1, 6):
        r = _append(db_app, ctx, level)
        assert r.status_code == 200 and r.json()["kind"] == "committed", r.text
        assert r.json()["level"] == level and r.json()["complete"] is (level == 5)
    chain = _chain(db_app, ctx)
    assert chain["kind"] == "ok" and chain["complete"] is True and chain["nextLevel"] is None
    assert [n["level"] for n in chain["levels"]] == [1, 2, 3, 4, 5]
    assert [n["answer"] for n in chain["levels"]] == list(ANSWERS)
    assert chain["primaryQuestionId"] == str(ctx["question_ids"][0].value)
    assert _position(db_app, ctx)["actions"]["APPEND_IMPACT_CHAIN_NODE"]["reasonCode"] == (
        "IMPACT_CHAIN_COMPLETE"
    )
    assert f03.session_of(db_app, ctx["session"]).state.value == "QUESTION_SELECTION"


def test_every_node_keeps_its_full_provenance_and_the_audit_names_the_binding(
    db_app: sa.Connection,
) -> None:
    ctx = _reach(db_app)
    chain_id = _create(db_app, ctx).json()["impactChainId"]
    assert _append(db_app, ctx, 1).json()["kind"] == "committed"
    (node,) = db_app.execute(
        sa.text("SELECT * FROM impact_chain_nodes WHERE impact_chain_id = :c"), {"c": chain_id}
    ).mappings()
    assert str(node["impact_chain_id"]) == chain_id and node["level"] == 1
    assert node["author_user_id"] == ctx["fac"].value
    assert node["session_id"] == ctx["session"].value
    assert node["selected_question_id"] == ctx["question_ids"][0].value
    assert node["captured_at"] is not None and node["answer_content"] == ANSWERS[0]
    for command in ("CMD_CREATE_IMPACT_CHAIN", "CMD_APPEND_IMPACT_CHAIN_NODE"):
        (audit,) = f03.audit_rows(db_app, ctx, command)
        assert audit["actor_type"] == "HUMAN_USER" and audit["authority_source_type"] == "BINDING"
        assert audit["authority_scope_ref"] == f"SESSION:{ctx['session'].value}"
    events = db_app.execute(
        sa.text(
            "SELECT event_type, payload FROM committed_events WHERE aggregate_ref = :r "
            "ORDER BY aggregate_version_after_commit"
        ),
        {"r": f"impact_chain:{chain_id}"},
    ).all()
    assert [e.event_type for e in events] == ["IMPACT_CHAIN_CREATED", "IMPACT_CHAIN_NODE_APPENDED"]
    assert events[1].payload["level"] == 1 and events[1].payload["fixture"] is True
    assert ANSWERS[0] not in str(events[1].payload)  # free text never enters an Event


def test_a_fixture_chain_stays_fixture_non_proof(db_app: sa.Connection) -> None:
    ctx = _reach(db_app)
    assert _create(db_app, ctx).json()["kind"] == "committed"
    assert _chain(db_app, ctx)["proofMode"] == "FIXTURE_NON_PROOF"
    assert _position(db_app, ctx)["impactChain"]["proofMode"] == "FIXTURE_NON_PROOF"


# ------------------------------------------------------------ MUST REMAIN IMPOSSIBLE


def test_session_control_alone_confers_no_authoring(db_app: sa.Connection) -> None:
    """HD-26 rule 3: the controller who is not the selector cannot author."""
    ctx = _in_selection(db_app)
    selector = ctx["participants"][0]
    _grant_selector(db_app, ctx, selector)
    _select_primary(db_app, ctx, selector)
    cap = _position(db_app, ctx)["actions"]["CREATE_IMPACT_CHAIN"]
    assert cap["available"] is False and cap["reasonCode"] == "NO_QUESTION_SELECTION_RIGHT"
    _denied(_create(db_app, ctx))  # the Facilitator: controller, no selection right
    assert _create(db_app, ctx, selector).json()["kind"] == "committed"
    _denied(_append(db_app, ctx, 1))


def test_participation_alone_confers_no_authoring(db_app: sa.Connection) -> None:
    """HD-26 rule 4."""
    ctx = _reach(db_app)
    participant = ctx["participants"][1]
    _denied(_create(db_app, ctx, participant))
    assert _create(db_app, ctx).json()["kind"] == "committed"
    _denied(_append(db_app, ctx, 1, who=participant))


def test_a_selection_right_holder_who_did_not_select_the_primary_cannot_author(
    db_app: sa.Connection,
) -> None:
    """HD-26: the holder "who selected the current Primary Question"."""
    ctx = _in_selection(db_app)
    selector = ctx["participants"][0]
    _grant_selector(db_app, ctx, selector)
    _select_primary(db_app, ctx, selector)
    _grant_selector(db_app, ctx, ctx["fac"])  # a second holder, not the selector
    cap = _position(db_app, ctx)["actions"]["CREATE_IMPACT_CHAIN"]
    assert cap["reasonCode"] == "NOT_PRIMARY_QUESTION_SELECTOR"
    _denied(_create(db_app, ctx), "NOT_PRIMARY_QUESTION_SELECTOR")
    assert _create(db_app, ctx, selector).json()["kind"] == "committed"
    _denied(_append(db_app, ctx, 1), "NOT_PRIMARY_QUESTION_SELECTOR")


def test_a_system_actor_cannot_create_or_append(db_app: sa.Connection) -> None:
    """HD-26 rule 5: no AI or system authority of any kind."""
    from application.impact_chain_handler import append_impact_chain_node, create_impact_chain
    from application.session_control_handler import SessionCommandDenied
    from authority.actor import ActorClass, ActorIdentity

    ctx = _reach(db_app)
    system = ActorIdentity(ActorClass.SYSTEM_SERVICE, ctx["fac"])
    with pytest.raises(SessionCommandDenied):
        create_impact_chain(
            f02.ports(db_app),
            actor=system,
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            expected_session_version=_version(db_app, ctx),
            ident=f03.keyed_ident(),
        )
    assert _create(db_app, ctx).json()["kind"] == "committed"
    with pytest.raises(SessionCommandDenied):
        append_impact_chain_node(
            f02.ports(db_app),
            actor=system,
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            expected_chain_version=1,
            level=1,
            answer_content="generated",
            ident=f03.keyed_ident(),
        )
    assert _chain(db_app, ctx)["levels"] == []


def test_no_chain_without_a_primary_question(db_app: sa.Connection) -> None:
    ctx = _in_selection(db_app)
    _grant_selector(db_app, ctx, ctx["fac"])
    assert _position(db_app, ctx)["actions"]["CREATE_IMPACT_CHAIN"]["reasonCode"] == (
        "NO_PRIMARY_QUESTION"
    )
    _blocked(_create(db_app, ctx), "NO_PRIMARY_QUESTION")


def test_exactly_one_chain_per_primary_question(db_app: sa.Connection) -> None:
    """S2(i)."""
    ctx = _reach(db_app)
    assert _create(db_app, ctx).json()["kind"] == "committed"
    _blocked(_create(db_app, ctx), "IMPACT_CHAIN_ALREADY_EXISTS")


def test_levels_are_strictly_successive(db_app: sa.Connection) -> None:
    ctx = _reach(db_app)
    assert _create(db_app, ctx).json()["kind"] == "committed"
    _blocked(_append(db_app, ctx, 2), "LEVEL_NOT_SUCCESSIVE")
    assert _append(db_app, ctx, 1).json()["kind"] == "committed"
    _blocked(_append(db_app, ctx, 1, answer="Again."), "LEVEL_NOT_SUCCESSIVE")
    _blocked(_append(db_app, ctx, 3), "LEVEL_NOT_SUCCESSIVE")


@pytest.mark.parametrize(
    ("level", "answer", "code"),
    [
        (6, "Beyond five.", "LEVEL_OUT_OF_RANGE"),
        (0, "Level zero.", "LEVEL_OUT_OF_RANGE"),
        (True, "Boolean level.", "LEVEL_OUT_OF_RANGE"),
        (1, "   ", "ANSWER_REQUIRED"),
        (1, None, "ANSWER_REQUIRED"),
        (1, "x" * 2001, "ANSWER_TOO_LONG"),
    ],
)
def test_malformed_input_is_rejected(
    db_app: sa.Connection, level: Any, answer: Any, code: str
) -> None:
    ctx = _reach(db_app)
    assert _create(db_app, ctx).json()["kind"] == "committed"
    body = {"expectedChainVersion": 1, "level": level, "answer": answer}
    r = _post(db_app, ctx, "impact-chain/nodes", body)
    assert r.status_code == 400 and r.json() == {"kind": "rejected", "reasonCode": code}, r.text


def test_nodes_are_append_only_and_the_anchor_is_immutable_in_the_database(
    db_app: sa.Connection,
) -> None:
    """S1(i): no stored answer may be edited, overwritten or replaced."""
    ctx = _reach(db_app)
    chain_id = _create(db_app, ctx).json()["impactChainId"]
    assert _append(db_app, ctx, 1).json()["kind"] == "committed"
    for statement in (
        "UPDATE impact_chain_nodes SET answer_content = 'rewritten' WHERE impact_chain_id = :c",
        "DELETE FROM impact_chain_nodes WHERE impact_chain_id = :c",
        "UPDATE impact_chains SET selected_question_id = gen_random_uuid() WHERE id = :c",
        "UPDATE impact_chains SET record_version = record_version + 2 WHERE id = :c",
        "DELETE FROM impact_chains WHERE id = :c",
    ):
        with pytest.raises(sa.exc.DBAPIError), db_app.begin_nested():
            db_app.execute(sa.text(statement), {"c": chain_id})


def test_the_database_refuses_a_skipped_level_and_a_foreign_author(db_app: sa.Connection) -> None:
    ctx = _reach(db_app)
    chain_id = _create(db_app, ctx).json()["impactChainId"]
    row = {
        "c": chain_id,
        "w": ctx["ws"].value,
        "s": ctx["session"].value,
        "q": ctx["question_ids"][0].value,
    }
    insert = (
        "INSERT INTO impact_chain_nodes (id, workspace_id, impact_chain_id, session_id, "
        "selected_question_id, level, answer_content, author_user_id, captured_at) "
        "VALUES (gen_random_uuid(), :w, :c, :s, :q, :lvl, 'text', :a, now())"
    )
    for level, author in ((2, ctx["fac"].value), (1, ctx["participants"][0].value)):
        with pytest.raises(sa.exc.DBAPIError), db_app.begin_nested():
            db_app.execute(sa.text(insert), {**row, "lvl": level, "a": author})


def test_the_chain_belongs_to_question_selection(db_app: sa.Connection) -> None:
    ctx = f04.analysis_context(db_app, fixture=True)  # ANALYSIS
    _grant_selector(db_app, ctx, ctx["fac"])
    cap = _position(db_app, ctx)["actions"]["CREATE_IMPACT_CHAIN"]
    assert cap["relevant"] is False and cap["reasonCode"] == "SESSION_NOT_IN_QUESTION_SELECTION"
    _blocked(_create(db_app, ctx), "SESSION_NOT_IN_QUESTION_SELECTION")


def test_a_stale_chain_version_is_stale_and_the_same_intent_commits_once(
    db_app: sa.Connection,
) -> None:
    ctx = _reach(db_app)
    assert _create(db_app, ctx).json()["kind"] == "committed"
    body = {"expectedChainVersion": 7, "level": 1, "answer": ANSWERS[0]}
    stale = _post(db_app, ctx, "impact-chain/nodes", body)
    assert stale.status_code == 409 and stale.json()["kind"] == "stale", stale.text
    ws, sid = ctx["ws"].value, ctx["session"].value
    url = f"/workspaces/{ws}/sessions/{sid}/impact-chain/nodes"
    key = {"Idempotency-Key": str(uuid.uuid4())}
    body["expectedChainVersion"] = 1
    client = _client(db_app, ctx["fac"])
    assert client.post(url, headers=key, json=body).json()["kind"] == "committed"
    assert client.post(url, headers=key, json=body).json()["kind"] == "committed"
    assert len(_chain(db_app, ctx)["levels"]) == 1
