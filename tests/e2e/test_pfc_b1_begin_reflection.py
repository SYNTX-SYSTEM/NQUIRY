"""WU-PFC-B1 (F05): TRN-SESS-007 BEGIN_REFLECTION under HD-24 / NQ-DEC-052.

Architecture: 03 TRN-SESS-007 (ANALYSIS -> REFLECTION; REQUIRED EVIDENCE
"AI_VALIDATION_PROOF that required analysis operations completed under 08
contracts" and "SYSTEM_PROOF that derived analysis did not alter raw Questions";
DENY "AI output exists but failed validation / Analysis is incomplete / Derived
output altered protected source state / Authority denied"; "AI failure does not
advance state"); 04 AUTH-DEP-SESS-007 (human controller path); 16 REC-022
(HD-20; enforcement home "proof -> generation -> provider provenance"), REC-018
(SYSTEM_DERIVED stays REQUIRE/DENY), REC-028 (HD-24).

Human Authority HD-24, rules 6-12:
6. MockProvider results for Fixture Sessions may satisfy the controlled
   development proof path required to exercise and prove the REFLECTION lifecycle.
7. Such results remain NON_PROOF and must never be represented as real provider proof.
8. For non-Fixture Sessions, HD-20 remains fully binding.
9. Real non-Fixture Sessions remain on Option 01 (blocked by HARD-DEP-002).
10. BEGIN_REFLECTION remains a Human Controller Command requiring SESSION_CONTROL_RIGHT.
11. Existing SYSTEM_DERIVED REQUIRE / DENY semantics remain unchanged.
12. Moving to Option 01 later changes only the eligible proof source.

FIRST BROKEN RELATION (before this Work Unit): TRN-SESS-007 is declared in the
domain topology, but no Command, handler, route, proof-source rule or projection
realizes it. Every Session stays in ANALYSIS.
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


def _accepted(db: sa.Connection, *, fixture: bool) -> dict[str, Any]:
    ctx = f04.analysis_context(db, fixture=fixture)
    assert f04.run(db, ctx, ctx["oa1"]).status == "ACCEPTED"
    return ctx


def _version(db: sa.Connection, ctx: dict[str, Any]) -> int:
    return int(f03.session_of(db, ctx["session"]).record_version.value)


def _state(db: sa.Connection, ctx: dict[str, Any]) -> str:
    return str(
        db.execute(
            sa.select(sessions_table.c.state).where(sessions_table.c.id == ctx["session"].value)
        ).scalar_one()
    )


def _begin(db: sa.Connection, ctx: dict[str, Any], who: Any = None, **body: Any) -> Any:
    client = _client(db, who or ctx["fac"])
    payload = {"expectedVersion": _version(db, ctx), **body}
    return client.post(
        f"/workspaces/{ctx['ws'].value}/sessions/{ctx['session'].value}/transitions/begin-reflection",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        json=payload,
    )


def _position(db: sa.Connection, ctx: dict[str, Any], who: Any = None) -> dict[str, Any]:
    r = _client(db, who or ctx["fac"]).get(
        f"/workspaces/{ctx['ws'].value}/sessions/{ctx['session'].value}/position"
    )
    return r.json()  # type: ignore[no-any-return]


# ------------------------------------------------------------ MUST BECOME TRUE (rules 6, 7, 10)


def test_a_fixture_session_enters_reflection_on_its_mock_proof_as_non_proof(
    db_app: sa.Connection,
) -> None:
    ctx = _accepted(db_app, fixture=True)
    before = _position(db_app, ctx)["actions"]["BEGIN_REFLECTION"]
    assert before["available"] is True and before["relevant"] is True
    r = _begin(db_app, ctx)
    assert r.status_code == 200 and r.json()["kind"] == "committed", r.text
    assert _state(db_app, ctx) == "REFLECTION"
    position = _position(db_app, ctx)
    assert position["session"]["state"] == "REFLECTION"
    assert position["session"]["proofMode"] == "FIXTURE_NON_PROOF"
    reflection = position["reflection"]
    assert reflection["proofClass"] == "MOCK_NON_PROOF"
    assert reflection["proofSource"] == "FIXTURE_MOCK"
    assert reflection["isRealProviderProof"] is False


def test_the_committed_event_names_the_validated_proof_and_its_non_proof_class(
    db_app: sa.Connection,
) -> None:
    ctx = _accepted(db_app, fixture=True)
    assert _begin(db_app, ctx).json()["kind"] == "committed"
    event = db_app.execute(
        sa.text(
            "SELECT payload FROM committed_events WHERE aggregate_ref = :r "
            "AND event_type = 'SESSION_REFLECTION'"
        ),
        {"r": f"session:{ctx['session'].value}"},
    ).scalar_one()
    proof = db_app.execute(
        sa.text(
            "SELECT p.id, p.validation_result, g.provider FROM ai_validation_proofs p "
            "JOIN ai_generations g ON g.id = p.ai_generation_id "
            "WHERE g.session_id = :s AND p.ai_operation_id = 'AIOP-001' "
            "AND p.validation_result = 'VALIDATED'"
        ),
        {"s": ctx["session"].value},
    ).one()
    assert event["validation_proof_id"] == str(proof.id)
    assert event["provider"] == proof.provider == "mock"
    assert event["proof_class"] == "MOCK_NON_PROOF" and event["proof_source"] == "FIXTURE_MOCK"
    assert event["fixture"] is True
    assert event["previous_state"] == "ANALYSIS" and event["state"] == "REFLECTION"


def test_the_transition_is_audited_as_a_human_binding_command(db_app: sa.Connection) -> None:
    ctx = _accepted(db_app, fixture=True)
    assert _begin(db_app, ctx).json()["kind"] == "committed"
    (audit,) = f03.audit_rows(db_app, ctx, "CMD_BEGIN_REFLECTION")
    assert audit["authority_source_type"] == "BINDING"
    assert audit["actor_type"] == "HUMAN_USER"
    assert audit["authority_scope_ref"] == f"SESSION:{ctx['session'].value}"


# ------------------------------------------------------------ MUST REMAIN IMPOSSIBLE (8, 9, 11)


def test_hd_20_a_real_session_never_enters_reflection_on_a_mock_proof(
    db_app: sa.Connection,
) -> None:
    ctx = _accepted(db_app, fixture=False)
    version = _version(db_app, ctx)
    cap = _position(db_app, ctx)["actions"]["BEGIN_REFLECTION"]
    assert (
        cap["available"] is False
        and cap["reasonCode"] == "MOCK_PROOF_NOT_ELIGIBLE_FOR_REAL_SESSION"
    )
    r = _begin(db_app, ctx)
    assert r.status_code == 422 and r.json() == {
        "kind": "blocked",
        "reasonCode": "MOCK_PROOF_NOT_ELIGIBLE_FOR_REAL_SESSION",
    }
    assert _state(db_app, ctx) == "ANALYSIS" and _version(db_app, ctx) == version


def test_an_authorized_but_unexecuted_analysis_keeps_the_session_in_analysis(
    db_app: sa.Connection,
) -> None:
    """Right after BEGIN_ANALYSIS, OA-1 is authorized and not yet run: the
    required analysis is unresolved (BND-017), so nothing may depend on it."""
    ctx = f04.analysis_context(db_app, fixture=True)
    r = _begin(db_app, ctx)
    assert r.status_code == 422 and r.json()["reasonCode"] == "ANALYSIS_IN_PROGRESS"
    assert _state(db_app, ctx) == "ANALYSIS"


def test_ai_failure_does_not_advance_the_session(db_app: sa.Connection) -> None:
    from ai_contracts.aiop import AIOperationId
    from ai_gateway.adapters.providers.mock import MockProviderOutcome

    ctx = f04.analysis_context(db_app, fixture=True)
    outcome = f04.run(
        db_app, ctx, ctx["oa1"], scripted={AIOperationId.AIOP_001: MockProviderOutcome.TIMEOUT}
    )
    assert outcome.status != "ACCEPTED"
    r = _begin(db_app, ctx)
    assert r.status_code == 422 and r.json()["reasonCode"] == "REQUIRED_ANALYSIS_NOT_COMPLETED"
    assert _state(db_app, ctx) == "ANALYSIS"


def _clustering_failed(db: sa.Connection) -> dict[str, Any]:
    from ai_contracts.aiop import AIOperationId
    from ai_gateway.adapters.providers.mock import MockProviderOutcome

    ctx = f04.analysis_context(db, fixture=True)
    scripted = {AIOperationId.AIOP_002: MockProviderOutcome.TIMEOUT}
    outcome = f04.run(db, ctx, ctx["oa1"], scripted=scripted)
    assert outcome.status == "ACCEPTED" and outcome.next is not None
    assert outcome.next.status != "ACCEPTED"
    return ctx


def test_a_failed_optional_clustering_does_not_block_reflection(db_app: sa.Connection) -> None:
    """12 §39: "Required: AIOP-001. Optional: AIOP-002." """
    ctx = _clustering_failed(db_app)
    assert _begin(db_app, ctx).json()["kind"] == "committed"
    assert _state(db_app, ctx) == "REFLECTION"


def test_an_unresolved_ai_operation_blocks_the_transition(db_app: sa.Connection) -> None:
    """BND-017: an authorized AI operation whose run has not resolved yet (here a
    controller RETRY of the clustering, authorized and not executed) blocks the
    dependent transition."""
    from ai_contracts.aiop import AIOperationId
    from ai_contracts.authorization import RequestCase

    ctx = _clustering_failed(db_app)
    f04.request(db_app, ctx, AIOperationId.AIOP_002, RequestCase.RETRY)
    r = _begin(db_app, ctx)
    assert r.status_code == 422 and r.json()["reasonCode"] == "ANALYSIS_IN_PROGRESS"
    assert _state(db_app, ctx) == "ANALYSIS"


@pytest.mark.parametrize("who", ["owner", "participant"])
def test_only_the_session_controller_may_begin_reflection(db_app: sa.Connection, who: str) -> None:
    ctx = _accepted(db_app, fixture=True)
    actor = ctx["owner"] if who == "owner" else ctx["participants"][0]
    r = _begin(db_app, ctx, who=actor)
    assert r.status_code == 403 and r.json()["kind"] == "denied", r.text
    assert _state(db_app, ctx) == "ANALYSIS"


def test_a_system_actor_cannot_begin_reflection(db_app: sa.Connection) -> None:
    """HD-24 rule 11 / REC-018: the SYSTEM_DERIVED path stays REQUIRE/DENY."""
    from application.reflection_handler import begin_reflection
    from application.session_control_handler import SessionCommandDenied
    from authority.actor import ActorClass, ActorIdentity

    ctx = _accepted(db_app, fixture=True)
    system = ActorIdentity(ActorClass.SYSTEM_SERVICE, ctx["fac"])
    with pytest.raises(SessionCommandDenied):
        begin_reflection(
            f02.ports(db_app),
            actor=system,
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            expected_session_version=_version(db_app, ctx),
            ident=f03.keyed_ident(),
        )
    assert _state(db_app, ctx) == "ANALYSIS"


def test_a_stale_view_is_answered_as_stale(db_app: sa.Connection) -> None:
    ctx = _accepted(db_app, fixture=True)
    r = _begin(db_app, ctx, expectedVersion=1)
    assert r.status_code == 409 and r.json()["kind"] == "stale"
    assert _state(db_app, ctx) == "ANALYSIS"


def test_the_same_intent_commits_once(db_app: sa.Connection) -> None:
    ctx = _accepted(db_app, fixture=True)
    client = _client(db_app, ctx["fac"])
    key = {"Idempotency-Key": str(uuid.uuid4())}
    ws, sid = ctx["ws"].value, ctx["session"].value
    url = f"/workspaces/{ws}/sessions/{sid}/transitions/begin-reflection"
    body = {"expectedVersion": _version(db_app, ctx)}
    first = client.post(url, headers=key, json=body)
    again = client.post(url, headers=key, json=body)
    assert first.json()["kind"] == "committed" and again.json()["kind"] == "committed"
    assert len(f03.audit_rows(db_app, ctx, "CMD_BEGIN_REFLECTION")) == 1


def test_reflection_is_not_reachable_twice(db_app: sa.Connection) -> None:
    ctx = _accepted(db_app, fixture=True)
    assert _begin(db_app, ctx).json()["kind"] == "committed"
    r = _begin(db_app, ctx)
    assert r.status_code == 422 and r.json()["reasonCode"] == "SESSION_NOT_IN_ANALYSIS"


# ------------------------------------------------------------ rule 12: only the proof source


def test_the_proof_source_rule_is_the_only_eligibility_decision() -> None:
    """Option 01 later = a non-empty eligible real-provider set; nothing else."""
    from application.reflection_proof import (
        FIXTURE_MOCK,
        RealProviderProofSource,
        decide_eligibility,
    )

    today = (FIXTURE_MOCK, RealProviderProofSource(frozenset()))
    option_01 = (FIXTURE_MOCK, RealProviderProofSource(frozenset({"eligible-provider"})))
    mock, real = ("mock", "MOCK_NON_PROOF"), ("eligible-provider", "PROVIDER_OUTPUT")

    def decide(sources: Any, fixture: bool, proof: tuple[str, str]) -> Any:
        return decide_eligibility(sources, fixture=fixture, provider=proof[0], proof_class=proof[1])

    assert decide(today, True, mock).source == "FIXTURE_MOCK"
    blocked = decide(today, False, mock)
    assert blocked.source is None
    assert blocked.reason == "MOCK_PROOF_NOT_ELIGIBLE_FOR_REAL_SESSION"
    not_yet = decide(today, False, real)
    assert not_yet.source is None and not_yet.reason == "NO_ELIGIBLE_PROVIDER_PROOF"
    admitted = decide(option_01, False, real)
    assert admitted.source == "ELIGIBLE_REAL_PROVIDER" and admitted.is_real_provider_proof is True
    # HD-20 holds under Option 01 too: a mock proof never admits a real Session.
    still = decide(option_01, False, mock)
    assert still.source is None
    assert still.reason == "MOCK_PROOF_NOT_ELIGIBLE_FOR_REAL_SESSION"
    # Even a misconfigured eligible set that names the mock cannot break HD-20.
    misconfigured = (FIXTURE_MOCK, RealProviderProofSource(frozenset({"mock"})))
    for proof_class in ("MOCK_NON_PROOF", "PROVIDER_OUTPUT"):
        refused = decide(misconfigured, False, ("mock", proof_class))
        assert refused.source is None and refused.is_real_provider_proof is False
    # A mock result never passes as a real proof class, not even for a Fixture Session.
    assert decide(option_01, True, ("mock", "PROVIDER_OUTPUT")).source is None
