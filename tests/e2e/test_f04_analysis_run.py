"""F04 WU-04.5: authorized run → candidate → accepted artifact; RETRY / RECOVERY.

MUST BECOME TRUE: after BEGIN_ANALYSIS the system executes AT MOST one AIOP-001
run for OA-1; a VALIDATED candidate becomes exactly one accepted artifact in one
commit with VALIDATED and the persisted proof (PI-1), audited as
SYSTEM_OPERATION with ref = the OA's authorizing Command; acceptance creates
OA-3. A FAILED / REJECTED run leaves an honest terminal generation and no
artifact; the controller may RETRY (retry_of) or, when the latest OA is
unconsumed, RECOVER (no retry_of, supersession); every link is persisted.

MUST REMAIN IMPOSSIBLE: a second run per OA; execution of a superseded OA; a
request while a generation is non-terminal or after an accepted result; a
request whose case disagrees with persisted state; acceptance of REJECTED /
FAILED output; any Session / Question / membership / fingerprint change; an
artifact written by anything but the acceptance commit; AI self-invocation.

FALSIFIERS: E1-E18 (F04 reconstruction §15).
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import f02_support as f02
import f03_support as f03
import f04_support as f04
import pytest
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import RequestCase
from ai_contracts.generation import AIGenerationStatus
from ai_gateway.adapters.providers.mock import MockProviderOutcome
from application.analysis_request_handler import RequestCaseMismatch
from application.analysis_runtime import UNAVAILABLE
from application.session_control_handler import SessionCommandDenied, SessionPreconditionUnmet
from boundaries.bnd_010_ai_output import Bnd010AiOutputEvaluator, Bnd010Input
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from commit.coordinator import CommitInjectionPoint
from persistence.tables import ai_validation_proofs_table
from semantic_types.ids import CorrelationId
from test_support.failure_injector import ScriptedFailureInjector

ROOT = Path(__file__).resolve().parents[2]
A1, A2 = AIOperationId.AIOP_001, AIOperationId.AIOP_002
FAIL = {A1: MockProviderOutcome.TIMEOUT}


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    found = {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    found |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    return found


def _audits(db: sa.Connection, ctx: dict[str, Any], command_type: str) -> list[Any]:
    return f03.audit_rows(db, ctx, command_type)


def test_e1_e2_original_run_is_accepted_atomically(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    before = f04.snapshot(db_connection, ctx)
    outcome = f04.run(db_connection, ctx, ctx["oa1"], scripted={A2: MockProviderOutcome.TIMEOUT})

    assert outcome.status == "ACCEPTED", outcome
    gens = f04.generations(db_connection, ctx, "AIOP-001")
    assert len(gens) == 1  # E1: exactly one generation carries OA-1
    gen = gens[0]
    assert gen["operation_authorization_id"] == ctx["oa1"]
    assert gen["authorizing_command_id"] == ctx["begin_command"].value
    assert gen["status"] == "VALIDATED"
    assert gen["provider"] == "mock"
    assert gen["retry_of_generation_id"] is None
    proof = f04.rows(db_connection, ai_validation_proofs_table, ai_generation_id=gen["id"])
    assert [p["validation_result"] for p in proof] == ["VALIDATED"]

    arts = f04.artifacts(db_connection, ctx, "AIOP-001")
    assert len(arts) == 1
    art = arts[0]
    assert art["id"] == outcome.artifact_id == gen["output_artifact_ref"]
    assert art["proof_class"] == "MOCK_NON_PROOF"
    assert art["ai_generation_id"] == gen["id"]
    assert f"proof:{proof[0]['id']}" in art["provenance_ref"]

    # E2: SYSTEM_OPERATION audit, ref = the OA's authorizing Command (BEGIN_ANALYSIS)
    for command_type in ("CMD_AI_QUESTION_ANALYSIS", "CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT"):
        (audit,) = _audits(db_connection, ctx, command_type)
        assert audit["actor_type"] == "SYSTEM_SERVICE"
        assert audit["authority_source_type"] == "SYSTEM_OPERATION"
        assert audit["authority_source_ref"] == ctx["begin_command"].value
        assert audit["authority_scope_ref"] == f"SESSION:{ctx['session'].value}"
        assert not (audit["state_after_ref"] or "").startswith("session:")
    (accept,) = _audits(db_connection, ctx, "CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT")
    assert accept["command_id"] == art["accepted_by_command_id"]

    # acceptance created OA-3 = (BEGIN_ANALYSIS, AIOP-002) with X = the artifact
    (oa3,) = f04.authorizations(db_connection, ctx, "AIOP-002")
    assert oa3["shape"] == "OA-3"
    assert oa3["authorizing_command_id"] == ctx["begin_command"].value
    assert oa3["precondition_artifact_ref"] == art["id"]

    # E5: nothing human changed
    assert f04.snapshot(db_connection, ctx) == before


@pytest.mark.parametrize(
    ("scripted", "gen_status", "run_status"),
    [
        (MockProviderOutcome.TIMEOUT, "FAILED", "FAILED"),
        (MockProviderOutcome.PROVIDER_ERROR, "FAILED", "FAILED"),
        (MockProviderOutcome.PARTIAL_RESPONSE, "REJECTED", "REJECTED"),
        (MockProviderOutcome.NEW_QUESTION_FIELD, "REJECTED", "REJECTED"),
        (MockProviderOutcome.FOREIGN_REF, "REJECTED", "REJECTED"),
        (MockProviderOutcome.WRONG_OPERATION, "REJECTED", "REJECTED"),
    ],
)
def test_e3_failed_or_rejected_output_is_never_accepted(
    db_connection: sa.Connection,
    scripted: MockProviderOutcome,
    gen_status: str,
    run_status: str,
) -> None:
    ctx = f04.analysis_context(db_connection)
    before = f04.snapshot(db_connection, ctx)
    outcome = f04.run(db_connection, ctx, ctx["oa1"], scripted={A1: scripted})
    assert outcome.status == run_status
    (gen,) = f04.generations(db_connection, ctx)
    assert gen["status"] == gen_status
    assert f04.artifacts(db_connection, ctx) == []
    assert _audits(db_connection, ctx, "CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT") == []
    # K7: no clustering authorization, generation or cluster
    assert f04.authorizations(db_connection, ctx, "AIOP-002") == []
    proofs = f04.rows(db_connection, ai_validation_proofs_table, ai_generation_id=gen["id"])
    assert [p["validation_result"] for p in proofs] == (
        [] if gen_status == "FAILED" else ["REJECTED"]
    )
    assert f04.snapshot(db_connection, ctx) == before
    assert f03.session_of(db_connection, ctx["session"]).state.value == "ANALYSIS"


def test_e4_the_gateway_writes_nothing_and_only_f04_system_code_calls_it() -> None:
    gateway = (ROOT / "packages/ai_gateway/gateway.py").read_text()
    tree = ast.parse(gateway)
    modules = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert not any(m and m.startswith("persistence") for m in modules)
    for forbidden in ("create_derived_artifact", "create_generation", "update_generation_status"):
        assert forbidden not in gateway
    importers = sorted(
        str(p.relative_to(ROOT))
        for p in [*(ROOT / "packages").rglob("*.py"), *(ROOT / "apps").rglob("*.py")]
        if "ai_gateway" not in p.parts and "ai_gateway.gateway" in _imports(p)
    )
    assert importers == [
        "packages/application/analysis_runtime.py",
        "packages/application/analysis_system.py",
    ]


def test_e6_a_second_run_for_the_same_oa_is_refused(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted=FAIL)
    again = f04.run(db_connection, ctx, ctx["oa1"])
    assert again.status == "NOT_EXECUTED"
    assert again.reason_code == "SYSTEM_OPERATION_ALREADY_CONSUMED"
    assert len(f04.generations(db_connection, ctx)) == 1


def test_e7_e15_e16_retry_after_failure(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted=FAIL)
    (failed,) = f04.generations(db_connection, ctx)
    request = f04.request(db_connection, ctx, A1, RequestCase.RETRY)
    oa2 = f04.authorizations(db_connection, ctx, "AIOP-001")[-1]
    assert (oa2["shape"], oa2["request_case"]) == ("OA-2", "RETRY")
    assert oa2["authorizing_command_id"] == request.commit_unit.command_id.value
    assert oa2["chain_root_command_id"] == ctx["begin_command"].value  # E15
    assert oa2["supersedes_authorization_id"] == ctx["oa1"]
    assert oa2["retry_of_generation_id"] == failed["id"]
    (req_audit,) = _audits(db_connection, ctx, "CMD_REQUEST_QUESTION_ANALYSIS")
    assert req_audit["authority_source_type"] == "BINDING"

    outcome = f04.run(
        db_connection, ctx, request.authorization_id, scripted={A2: MockProviderOutcome.TIMEOUT}
    )
    assert outcome.status == "ACCEPTED"
    gens = f04.generations(db_connection, ctx, "AIOP-001")
    assert [g["status"] for g in gens] == ["FAILED", "VALIDATED"]  # the old one is not revived
    new = gens[1]
    assert new["retry_of_generation_id"] == failed["id"]
    assert new["authorizing_command_id"] == request.commit_unit.command_id.value
    (accept,) = _audits(db_connection, ctx, "CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT")
    assert accept["authority_source_ref"] == request.commit_unit.command_id.value
    # OA-3 authorized by C = the request (R7, K9)
    (oa3,) = f04.authorizations(db_connection, ctx, "AIOP-002")
    assert oa3["authorizing_command_id"] == request.commit_unit.command_id.value


def test_e8_request_after_accepted_success_is_blocked(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"])
    for case in RequestCase:
        with pytest.raises(SessionPreconditionUnmet) as exc:
            f04.request(db_connection, ctx, A1, case)
        assert exc.value.reason_code == "RESULT_ALREADY_ACCEPTED"


def test_e9_request_by_non_controller_is_denied(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted=FAIL)
    for actor in (ctx["participants"][0], ctx["owner"], ctx["outsider"]):
        with pytest.raises(SessionCommandDenied):
            f04.request(db_connection, ctx, A1, RequestCase.RETRY, actor)
    assert len(f04.authorizations(db_connection, ctx, "AIOP-001")) == 1


def test_e10_request_while_a_generation_is_non_terminal_is_blocked(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    stuck = f04.run(db_connection, ctx, ctx["oa1"], stop_after_execute=True)
    assert stuck.status == "INDETERMINATE"
    (gen,) = f04.generations(db_connection, ctx)
    assert gen["status"] == "RUNNING"
    for case in RequestCase:
        with pytest.raises(SessionPreconditionUnmet) as exc:
            f04.request(db_connection, ctx, A1, case)
        assert exc.value.reason_code == "GENERATION_IN_PROGRESS"


def test_e11_recovery_of_an_unconsumed_oa1(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    # The process stopped between the BEGIN_ANALYSIS commit and the run, or no
    # provider was available: OA-1 stays unconsumed (legal).
    assert f04.run(db_connection, ctx, ctx["oa1"], runtime=UNAVAILABLE).reason_code == (
        "AI_PROVIDER_UNAVAILABLE"
    )
    assert f04.generations(db_connection, ctx) == []
    request = f04.request(db_connection, ctx, A1, RequestCase.RECOVERY)
    oa2 = f04.authorizations(db_connection, ctx, "AIOP-001")[-1]
    assert (oa2["request_case"], oa2["supersedes_authorization_id"]) == ("RECOVERY", ctx["oa1"])
    assert oa2["retry_of_generation_id"] is None
    # the superseded OA-1 can never execute
    late = f04.run(db_connection, ctx, ctx["oa1"])
    assert (late.status, late.reason_code) == ("NOT_EXECUTED", "SYSTEM_OPERATION_SUPERSEDED")
    outcome = f04.run(
        db_connection, ctx, request.authorization_id, scripted={A2: MockProviderOutcome.TIMEOUT}
    )
    assert outcome.status == "ACCEPTED"
    (gen,) = f04.generations(db_connection, ctx, "AIOP-001")
    assert gen["retry_of_generation_id"] is None
    assert gen["operation_authorization_id"] == request.authorization_id


def test_e11_p4_repeated_recovery(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    first = f04.request(db_connection, ctx, A1, RequestCase.RECOVERY)
    second = f04.request(db_connection, ctx, A1, RequestCase.RECOVERY)
    oas = f04.authorizations(db_connection, ctx, "AIOP-001")
    assert [o["sequence_no"] for o in oas] == [1, 2, 3]
    assert oas[2]["supersedes_authorization_id"] == first.authorization_id
    assert f04.run(db_connection, ctx, first.authorization_id).reason_code == (
        "SYSTEM_OPERATION_SUPERSEDED"
    )
    assert f04.run(db_connection, ctx, second.authorization_id).status == "ACCEPTED"


def test_e17_latest_unconsumed_governs_over_an_older_failure(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted=FAIL)
    f04.request(db_connection, ctx, A1, RequestCase.RETRY)  # OA-2, never executed
    with pytest.raises(RequestCaseMismatch) as exc:
        f04.request(db_connection, ctx, A1, RequestCase.RETRY)
    assert exc.value.reason_code == "REQUEST_CASE_MISMATCH:RECOVERY"
    recovery = f04.request(db_connection, ctx, A1, RequestCase.RECOVERY)
    oa = f04.authorizations(db_connection, ctx, "AIOP-001")[-1]
    assert oa["id"] == recovery.authorization_id and oa["request_case"] == "RECOVERY"


def test_e18_case_mismatch_is_rejected(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    with pytest.raises(RequestCaseMismatch) as exc:
        f04.request(db_connection, ctx, A1, RequestCase.RETRY)  # OA-1 unconsumed
    assert exc.value.reason_code == "REQUEST_CASE_MISMATCH:RECOVERY"
    f04.run(db_connection, ctx, ctx["oa1"], scripted=FAIL)
    with pytest.raises(RequestCaseMismatch) as exc2:
        f04.request(db_connection, ctx, A1, RequestCase.RECOVERY)  # OA-1 consumed, failed
    assert exc2.value.reason_code == "REQUEST_CASE_MISMATCH:RETRY"
    assert len(f04.authorizations(db_connection, ctx, "AIOP-001")) == 1


def test_e12_run_while_session_not_analysis_is_blocked(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    db_connection.execute(sa.text("ALTER TABLE sessions DISABLE TRIGGER USER"))
    db_connection.execute(
        sa.text("UPDATE sessions SET state = 'REFLECTION' WHERE id = :s"),
        {"s": ctx["session"].value},
    )
    db_connection.execute(sa.text("ALTER TABLE sessions ENABLE TRIGGER USER"))
    outcome = f04.run(db_connection, ctx, ctx["oa1"])
    assert outcome.reason_code == "SYSTEM_OPERATION_SESSION_NOT_ANALYSIS:REFLECTION"
    assert f04.generations(db_connection, ctx) == []
    assert _audits(db_connection, ctx, "CMD_AI_QUESTION_ANALYSIS") == []  # denied, no commit


def test_e13_ai_processor_cannot_invoke(db_connection: sa.Connection) -> None:
    from authority.actor import ActorClass, ActorIdentity
    from boundaries.authority_source import SystemOperationAuthority, SystemOperationPurpose
    from boundaries.system_operation import resolve_system_operation

    ctx = f04.analysis_context(db_connection)
    resolution = resolve_system_operation(
        reader=f02.ports(db_connection).system_operations,
        actor=ActorIdentity(ActorClass.AI_PROCESSOR, ctx["fac"]),
        workspace_id=ctx["ws"],
        authority=SystemOperationAuthority(
            session_id=ctx["session"].value,
            operation_authorization_id=ctx["oa1"],
            purpose=SystemOperationPurpose.EXECUTE,
        ),
    )
    assert not resolution.granted


def test_e14_output_claiming_a_decision_is_denied_by_bnd_010() -> None:
    import uuid

    from ai_contracts.f04_operations import AIOP_001_TOP_LEVEL
    from ai_contracts.generation import AIValidationResult
    from authority.actor import ActorClass, ActorIdentity
    from semantic_types.ids import UserId, WorkspaceId

    ws = WorkspaceId(uuid.uuid4())
    context = BoundaryContext(
        workspace_id=ws,
        operation="CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT",
        actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, UserId(uuid.uuid4())),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=f02.NOW,
    )
    for claim in ("decision_status", "selected_question", "evidence", "assumption_status"):
        proof = Bnd010AiOutputEvaluator().evaluate(
            Bnd010Input(
                boundary_id=BoundaryId.BND_010,
                context=context,
                ai_generation_status=AIGenerationStatus.VALIDATED,
                validation_result=AIValidationResult.VALIDATED,
                source_workspace_id=ws,
                ai_validation_proof_ref="p",
                output_fields=AIOP_001_TOP_LEVEL | {claim},
                permitted_output_fields=AIOP_001_TOP_LEVEL,
            ),
            context,
        )
        assert proof.result is BoundaryResult.DENY
        assert proof.reason_code == f"OUTPUT_OUTSIDE_CONTRACT:{claim}"


def test_acceptance_denial_leaves_honest_failure_and_no_artifact(
    db_connection: sa.Connection,
) -> None:
    """PI-1 failure branch: a VALIDATED candidate whose acceptance commit fails
    before commit leaves no artifact, no VALIDATED generation and no VALIDATED
    proof (independent review R2)."""
    ctx = f04.analysis_context(db_connection)
    outcome = f04.run(
        db_connection,
        ctx,
        ctx["oa1"],
        accept_failure_injector=ScriptedFailureInjector(
            fire_at=CommitInjectionPoint.BEFORE_AUDIT, exception=RuntimeError("boom")
        ),
    )
    assert outcome.status == "ACCEPTANCE_DENIED"
    (gen,) = f04.generations(db_connection, ctx)
    assert gen["status"] == "FAILED"
    assert gen["failure_code"].startswith("ACCEPTANCE_DENIED:")
    assert f04.artifacts(db_connection, ctx) == []
    assert f04.authorizations(db_connection, ctx, "AIOP-002") == []
    # R2 (PI-1): no proof row. A persisted VALIDATED proof exists only with its
    # accepted artifact; the validated fingerprint is the failure's record.
    assert f04.rows(db_connection, ai_validation_proofs_table, ai_generation_id=gen["id"]) == []
    assert gen["failure_detail_ref"].startswith("validated_output_fingerprint:")
    # and RETRY is legal afterwards
    assert f04.request(db_connection, ctx, A1, RequestCase.RETRY).case is RequestCase.RETRY


def test_execute_failed_precommit_leaves_oa_unconsumed(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    outcome = f04.run(
        db_connection,
        ctx,
        ctx["oa1"],
        failure_injector=ScriptedFailureInjector(
            fire_at=CommitInjectionPoint.AFTER_FIRST_CANONICAL_MUTATION,
            exception=RuntimeError("x"),
        ),
    )
    assert outcome.status == "FAILED_PRECOMMIT"
    assert f04.generations(db_connection, ctx) == []
    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(sa.text("ai_context_manifests"))
        .where(sa.text("session_id = :s")),
        {"s": ctx["session"].value},
    ).scalar_one()
    assert count == 0
    assert f04.request(db_connection, ctx, A1, RequestCase.RECOVERY).case is RequestCase.RECOVERY
