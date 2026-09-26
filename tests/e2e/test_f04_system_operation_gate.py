"""F04 WU-04.3: the SYSTEM_OPERATION effect-gate source and AI record integrity.

MUST BECOME TRUE: SYSTEM_OPERATION resolves only for the fixed F04
SYSTEM_SERVICE identity, under a persisted operation authorization whose
authorizing Command and chain root are COMMITTED Commands of this Session, while
the Session is ANALYSIS, the OA is the latest and (EXECUTE) unconsumed. Its proof
names the authorizing Command, scope `SESSION:<id>`, and the full OA.

MUST REMAIN IMPOSSIBLE: a human, AI or foreign-service SYSTEM_OPERATION; one
referencing a missing, foreign or uncommitted authorization; mutation of an
authorization, proof, manifest or accepted artifact; two generations for one
OA; execution of a superseded OA; a generation whose retry lineage or
precondition artifact differs from its OA; an authorization shape outside
§0.1 rule 2; a RETRY / RECOVERY whose case disagrees with persisted state.

FALSIFIERS: C1-C8 (C4 at DB level here; the audit row itself is proven in
WU-04.5), plus the §0.1 rule 5/8/9 persistence falsifiers. C9 is proven in
WU-04.9, once an accepted AIOP-001 artifact can exist.
"""

from __future__ import annotations

import uuid
from typing import Any

import f02_support as f02
import f03_support as f03
import f04_support as f04
import pytest
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import AuthorizationShape, OperationAuthorization, RequestCase
from ai_contracts.derived_artifact import AIDerivedArtifact, ProofClass
from ai_contracts.generation import (
    AIGeneration,
    AIGenerationStatus,
    AIValidationProof,
    AIValidationResult,
)
from ai_gateway.context import InputArtifactRef, build_context_manifest
from authority.actor import ActorClass, ActorIdentity
from authority.system_service import F04_ANALYSIS_SERVICE_ID
from boundaries.authority_source import (
    AuthoritySourceType,
    SystemOperationAuthority,
    SystemOperationPurpose,
)
from boundaries.bnd_014_commit import Bnd014Input
from boundaries.system_operation import resolve_system_operation
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from semantic_types.ids import CommandId, CorrelationId, GenerationId, UserId
from semantic_types.versions import ContractVersion, PromptVersion, RecordVersion
from sqlalchemy.exc import DBAPIError

SERVICE = ActorIdentity(ActorClass.SYSTEM_SERVICE, F04_ANALYSIS_SERVICE_ID)


def _execute(ctx: dict[str, Any], oa: uuid.UUID | None = None) -> SystemOperationAuthority:
    return SystemOperationAuthority(
        session_id=ctx["session"].value,
        operation_authorization_id=oa or ctx["oa1"],
        purpose=SystemOperationPurpose.EXECUTE,
    )


def _resolve(db: sa.Connection, ctx: dict[str, Any], actor: ActorIdentity = SERVICE, **kw: Any):  # type: ignore[no-untyped-def]
    return resolve_system_operation(
        reader=f02.ports(db).system_operations,
        actor=actor,
        workspace_id=kw.pop("workspace_id", ctx["ws"]),
        authority=kw.pop("authority", _execute(ctx)),
    )


def _generation(
    db: sa.Connection,
    ctx: dict[str, Any],
    oa: OperationAuthorization,
    *,
    retry_of: GenerationId | None = None,
    precondition: uuid.UUID | None = None,
) -> AIGeneration:
    """Operational record write (the Gateway's REQUESTED row), carrying OA."""
    generation = AIGeneration(
        ai_generation_id=GenerationId(uuid.uuid4()),
        workspace_id=ctx["ws"],
        ai_operation_id=oa.ai_operation_id,
        ai_operation_contract_version=ContractVersion("1.0"),
        prompt_version=PromptVersion("1.0"),
        model="mock-model-v1",
        provider="mock",
        status=AIGenerationStatus.REQUESTED,
        requested_at=f02.NOW,
        correlation_id=CorrelationId(uuid.uuid4()),
        record_version=RecordVersion.initial(),
        session_id=ctx["session"],
        operation_authorization_id=oa.authorization_id,
        authorizing_command_id=oa.authorizing_command_id,
        retry_of_generation_id=retry_of if retry_of is not None else oa.retry_of_generation_id,
        precondition_artifact_ref=(
            precondition if precondition is not None else oa.precondition_artifact_ref
        ),
    )
    f02.ports(db).ai_records.create_generation(generation)
    return generation


def _fail(db: sa.Connection, ctx: dict[str, Any], generation: AIGeneration) -> None:
    records = f02.ports(db).ai_records
    records.update_generation_status(
        ai_generation_id=generation.ai_generation_id,
        workspace_id=ctx["ws"],
        expected_record_version=RecordVersion(1),
        new_status=AIGenerationStatus.RUNNING,
    )
    records.update_generation_status(
        ai_generation_id=generation.ai_generation_id,
        workspace_id=ctx["ws"],
        expected_record_version=RecordVersion(2),
        new_status=AIGenerationStatus.FAILED,
        failure_code="PROVIDER_TIMEOUT",
    )


def _oa(db: sa.Connection, oa_id: uuid.UUID) -> OperationAuthorization:
    found = f02.ports(db).ai_authorizations.get(oa_id)
    assert found is not None
    return found


def _request_oa(
    db: sa.Connection,
    ctx: dict[str, Any],
    predecessor: OperationAuthorization,
    case: RequestCase,
    retry_of: GenerationId | None,
) -> OperationAuthorization:
    """An OA-2 row written at DB level, authorized by a request Command row that
    never committed (the request handler itself is WU-04.5)."""
    oa = OperationAuthorization(
        authorization_id=uuid.uuid4(),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        ai_operation_id=AIOperationId.AIOP_001,
        shape=AuthorizationShape.OA_2,
        authorizing_command_id=_fresh_command(db, ctx),
        sequence_no=predecessor.sequence_no + 1,
        chain_root_command_id=predecessor.chain_root_command_id,
        created_at=f02.NOW,
        request_case=case,
        supersedes_authorization_id=predecessor.authorization_id,
        retry_of_generation_id=retry_of,
    )
    f02.ports(db).ai_authorizations.create(oa)
    return oa


def _fresh_command(db: sa.Connection, ctx: dict[str, Any]) -> CommandId:
    from persistence.tables import commands_table

    command_id = uuid.uuid4()
    db.execute(
        sa.insert(commands_table).values(
            id=command_id,
            workspace_id=ctx["ws"].value,
            command_type="CMD_REQUEST_QUESTION_ANALYSIS",
            contract_version="1.0",
            payload_fingerprint="attack",
            created_at=f02.NOW,
            target_refs=[f"session:{ctx['session'].value}"],
        )
    )
    return CommandId(command_id)


def _raises_db(db: sa.Connection, statement: Any, params: dict[str, Any] | None = None) -> str:
    with pytest.raises(DBAPIError) as exc, db.begin_nested():
        if callable(statement):
            statement()
        else:
            db.execute(statement, params or {})
    return str(exc.value)


# ---------------------------------------------------------------- resolution


def test_system_operation_resolves_for_the_service_on_a_current_oa1(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    resolution = _resolve(db_connection, ctx)
    assert resolution.granted, resolution.reason_code
    source = resolution.source
    assert source is not None
    assert source.source_type is AuthoritySourceType.SYSTEM_OPERATION
    assert source.source_ref == ctx["begin_command"].value
    assert source.scope_ref == f"SESSION:{ctx['session'].value}"
    assert source.detail.startswith("OA-1|AIOP-001|EXECUTE|OA:")


def test_c1_human_actor_is_denied(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    resolution = _resolve(db_connection, ctx, f02.human(ctx["fac"]))
    assert not resolution.granted
    assert resolution.reason_code == "SYSTEM_OPERATION_ACTOR_NOT_SYSTEM_SERVICE:HUMAN_USER"


def test_c2_ai_processor_and_foreign_service_are_denied(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    ai = ActorIdentity(ActorClass.AI_PROCESSOR, F04_ANALYSIS_SERVICE_ID)
    assert _resolve(db_connection, ctx, ai).reason_code.endswith("AI_PROCESSOR")
    other = ActorIdentity(ActorClass.SYSTEM_SERVICE, UserId(uuid.uuid4()))
    assert (
        _resolve(db_connection, ctx, other).reason_code
        == "SYSTEM_OPERATION_SERVICE_IDENTITY_UNKNOWN"
    )


def test_c3_missing_foreign_or_uncommitted_authorization_is_denied(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    missing = _resolve(db_connection, ctx, authority=_execute(ctx, uuid.uuid4()))
    assert missing.reason_code == "SYSTEM_OPERATION_AUTHORIZATION_NOT_FOUND"

    other = f04.analysis_context(db_connection)
    foreign = _resolve(db_connection, ctx, authority=_execute(ctx, other["oa1"]))
    assert foreign.reason_code == "SYSTEM_OPERATION_FOREIGN_SCOPE"
    cross_ws = _resolve(db_connection, other, workspace_id=ctx["ws"])
    assert cross_ws.reason_code == "SYSTEM_OPERATION_FOREIGN_SCOPE"

    # An authorization whose authorizing Command never COMMITTED (a request
    # command row with no committed attempt), for this Session.
    oa1 = _oa(db_connection, ctx["oa1"])
    _fail(db_connection, ctx, _generation(db_connection, ctx, oa1))
    first = f02.ports(db_connection).ai_records.get_generation_for_authorization(ctx["oa1"])
    assert first is not None
    uncommitted = _request_oa(db_connection, ctx, oa1, RequestCase.RETRY, first.ai_generation_id)
    denied = _resolve(db_connection, ctx, authority=_execute(ctx, uncommitted.authorization_id))
    assert denied.reason_code == "SYSTEM_OPERATION_AUTHORIZING_COMMAND_NOT_COMMITTED"


def test_c3_session_not_analysis_is_denied(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    db_connection.execute(sa.text("ALTER TABLE sessions DISABLE TRIGGER USER"))
    db_connection.execute(
        sa.text("UPDATE sessions SET state = 'QUESTION_CAPTURE' WHERE id = :s"),
        {"s": ctx["session"].value},
    )
    db_connection.execute(sa.text("ALTER TABLE sessions ENABLE TRIGGER USER"))
    assert (
        _resolve(db_connection, ctx).reason_code
        == "SYSTEM_OPERATION_SESSION_NOT_ANALYSIS:QUESTION_CAPTURE"
    )


def test_bnd014_denies_system_operation_for_a_human_and_allows_the_service(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    evaluator = f02.ports(db_connection).bnd014()

    def evaluate(actor: ActorIdentity) -> Any:
        context = BoundaryContext(
            workspace_id=ctx["ws"],
            operation="CMD_AI_QUESTION_ANALYSIS",
            actor=actor,
            correlation_id=CorrelationId(uuid.uuid4()),
            evaluated_at=f02.NOW,
        )
        return evaluator.evaluate(
            Bnd014Input(
                boundary_id=BoundaryId.BND_014,
                context=context,
                expected_versions={},
                current_versions={},
                upstream_chain_result=BoundaryResult.ALLOW,
                authority=_execute(ctx),
            ),
            context,
        )

    assert evaluate(f02.human(ctx["fac"])).result is BoundaryResult.DENY
    allowed = evaluate(SERVICE)
    assert allowed.result is BoundaryResult.ALLOW
    assert allowed.authority_source.source_type is AuthoritySourceType.SYSTEM_OPERATION


# ------------------------------------------------------------ persistence


def test_c4_audit_check_accepts_system_operation_and_refuses_unknown(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    row = f03.audit_rows(db_connection, ctx, "CMD_BEGIN_ANALYSIS")[0]
    template = dict(row)
    from persistence.tables import audit_events_table as a

    def insert(source_type: str) -> None:
        values = dict(template, id=uuid.uuid4(), authority_source_type=source_type)
        db_connection.execute(sa.insert(a).values(**values))

    with db_connection.begin_nested() as sp:
        insert("SYSTEM_OPERATION")
        sp.rollback()
    message = _raises_db(db_connection, lambda: insert("SYSTEM_DERIVED"))
    assert "ck_audit_events_authority_source_type" in message


def test_operation_authorization_rows_are_immutable(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    assert "rejected" in _raises_db(
        db_connection,
        sa.text("UPDATE ai_operation_authorizations SET sequence_no = 9 WHERE id = :i"),
        {"i": ctx["oa1"]},
    )
    assert "rejected" in _raises_db(
        db_connection,
        sa.text("DELETE FROM ai_operation_authorizations WHERE id = :i"),
        {"i": ctx["oa1"]},
    )


def test_c8_second_generation_for_the_same_oa_is_refused(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    oa1 = _oa(db_connection, ctx["oa1"])
    first = _generation(db_connection, ctx, oa1)
    _fail(db_connection, ctx, first)  # terminal, so only the OA uniqueness can refuse
    message = _raises_db(db_connection, lambda: _generation(db_connection, ctx, oa1))
    assert "uq_ai_generations_operation_authorization" in message
    assert _resolve(db_connection, ctx).reason_code == "SYSTEM_OPERATION_ALREADY_CONSUMED"


def test_one_non_terminal_generation_per_session_operation(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    oa1 = _oa(db_connection, ctx["oa1"])
    _generation(db_connection, ctx, oa1)  # REQUESTED, never terminal
    # RECOVERY is illegal here (OA-1 is consumed); force the row shape at DB
    # level to prove the partial unique index is independent of the trigger.
    command = _fresh_command(db_connection, ctx)
    db_connection.execute(sa.text("ALTER TABLE ai_operation_authorizations DISABLE TRIGGER USER"))
    oa2 = OperationAuthorization(
        authorization_id=uuid.uuid4(),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        ai_operation_id=AIOperationId.AIOP_001,
        shape=AuthorizationShape.OA_2,
        authorizing_command_id=command,
        sequence_no=2,
        chain_root_command_id=oa1.chain_root_command_id,
        created_at=f02.NOW,
        request_case=RequestCase.RECOVERY,
        supersedes_authorization_id=oa1.authorization_id,
    )
    f02.ports(db_connection).ai_authorizations.create(oa2)
    db_connection.execute(sa.text("ALTER TABLE ai_operation_authorizations ENABLE TRIGGER USER"))
    message = _raises_db(db_connection, lambda: _generation(db_connection, ctx, oa2))
    assert "uq_ai_generations_one_non_terminal_per_session_operation" in message


def test_superseded_oa_can_never_execute(db_connection: sa.Connection) -> None:
    """E11 / rule 5 at persistence: OA-1 unconsumed, RECOVERY supersedes it."""
    ctx = f04.analysis_context(db_connection)
    oa1 = _oa(db_connection, ctx["oa1"])
    _request_oa(db_connection, ctx, oa1, RequestCase.RECOVERY, None)
    assert _resolve(db_connection, ctx).reason_code == "SYSTEM_OPERATION_SUPERSEDED"
    message = _raises_db(db_connection, lambda: _generation(db_connection, ctx, oa1))
    assert "superseded operation authorization can never execute" in message


def test_request_case_must_match_persisted_state(db_connection: sa.Connection) -> None:
    """E18 / rule 9 at persistence."""
    ctx = f04.analysis_context(db_connection)
    oa1 = _oa(db_connection, ctx["oa1"])
    # RETRY while the latest OA is unconsumed -> refused
    assert "RETRY requires" in _raises_db(
        db_connection,
        lambda: _request_oa(db_connection, ctx, oa1, RequestCase.RETRY, GenerationId(uuid.uuid4())),
    )
    # RECOVERY while the latest OA is consumed by a failed generation -> refused
    _fail(db_connection, ctx, _generation(db_connection, ctx, oa1))
    assert "RECOVERY requires" in _raises_db(
        db_connection, lambda: _request_oa(db_connection, ctx, oa1, RequestCase.RECOVERY, None)
    )


def test_generation_lineage_must_equal_its_oa(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    oa1 = _oa(db_connection, ctx["oa1"])
    first = _generation(db_connection, ctx, oa1)
    _fail(db_connection, ctx, first)
    oa2 = _request_oa(db_connection, ctx, oa1, RequestCase.RETRY, first.ai_generation_id)
    assert "generation provenance must equal" in _raises_db(
        db_connection,
        lambda: _generation(db_connection, ctx, oa2, retry_of=GenerationId(uuid.uuid4())),
    )


def test_oa_shape_outside_rule_2_is_refused(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    # OA-1 shape claiming AIOP-002 (bypassing the Python shape check)
    message = _raises_db(
        db_connection,
        sa.text(
            "INSERT INTO ai_operation_authorizations (id, workspace_id, session_id, "
            "ai_operation_id, shape, authorizing_command_id, sequence_no, chain_root_command_id, "
            "created_at) VALUES (:i, :w, :s, 'AIOP-002', 'OA-1', :c, 1, :c, now())"
        ),
        {
            "i": uuid.uuid4(),
            "w": ctx["ws"].value,
            "s": ctx["session"].value,
            "c": ctx["begin_command"].value,
        },
    )
    assert "ck_ai_operation_authorizations_shape" in message
    # a second OA-1 for the Session
    message = _raises_db(
        db_connection,
        sa.text(
            "INSERT INTO ai_operation_authorizations (id, workspace_id, session_id, "
            "ai_operation_id, shape, authorizing_command_id, sequence_no, chain_root_command_id, "
            "created_at) VALUES (:i, :w, :s, 'AIOP-001', 'OA-1', :c, 1, :c, now())"
        ),
        {
            "i": uuid.uuid4(),
            "w": ctx["ws"].value,
            "s": ctx["session"].value,
            "c": ctx["begin_command"].value,
        },
    )
    assert "uq_ai_operation_authorizations" in message


def test_c5_c6_c7_proof_manifest_artifact_are_immutable(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    ports = f02.ports(db_connection)
    manifest = build_context_manifest(
        ai_context_manifest_id=uuid.uuid4(),
        workspace_id=ctx["ws"],
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=ContractVersion("1.0"),
        requesting_actor_ref="SYSTEM_SERVICE:test",
        input_artifact_refs_with_versions=(
            InputArtifactRef(artifact_ref="question:x", content_digest="d" * 64),
        ),
        source_classifications=("HUMAN",),
        assembled_at=f02.NOW,
    )
    ports.ai_records.create_context_manifest(manifest)
    oa1 = _oa(db_connection, ctx["oa1"])
    generation = _generation(db_connection, ctx, oa1)
    proof = AIValidationProof(
        ai_validation_proof_id=uuid.uuid4(),
        ai_generation_id=generation.ai_generation_id,
        ai_operation_id=AIOperationId.AIOP_001,
        contract_version=ContractVersion("1.0"),
        validator_version=ContractVersion("1.0"),
        validation_result=AIValidationResult.REJECTED,
        validated_at=f02.NOW,
        output_fingerprint="f" * 64,
    )
    ports.ai_records.create_validation_proof(proof, workspace_id=ctx["ws"])
    # C5
    for stmt in (
        "UPDATE ai_validation_proofs SET validation_result = 'VALIDATED' WHERE id = :i",
        "DELETE FROM ai_validation_proofs WHERE id = :i",
    ):
        assert "rejected" in _raises_db(
            db_connection, sa.text(stmt), {"i": proof.ai_validation_proof_id}
        )
    second = AIValidationProof(**{**_fields(proof), "ai_validation_proof_id": uuid.uuid4()})
    assert "uq_ai_validation_proofs_generation" in _raises_db(
        db_connection,
        lambda: ports.ai_records.create_validation_proof(second, workspace_id=ctx["ws"]),
    )
    # C6
    for stmt in (
        "UPDATE ai_context_manifests SET context_fingerprint = 'x' WHERE id = :i",
        "DELETE FROM ai_context_manifests WHERE id = :i",
    ):
        assert "rejected" in _raises_db(
            db_connection, sa.text(stmt), {"i": manifest.ai_context_manifest_id}
        )
    # C7, on a GENUINELY accepted artifact (independent review R1: an accepted
    # artifact can only be born from a VALIDATED proof over its exact bytes, so
    # a fabricated one on this REJECTED-proof generation is itself refused).
    forged = AIDerivedArtifact(
        ai_derived_artifact_id=uuid.uuid4(),
        workspace_id=ctx["ws"],
        ai_generation_id=generation.ai_generation_id,
        ai_operation_id=AIOperationId.AIOP_001,
        content="{}",
        content_fingerprint="c" * 64,
        created_at=f02.NOW,
        record_version=RecordVersion.initial(),
        session_id=ctx["session"],
        accepted_by_command_id=CommandId(ctx["begin_command"].value),
        proof_class=ProofClass.MOCK_NON_PROOF,
    )
    assert "accepted artifact must be the validated output" in _raises_db(
        db_connection, lambda: ports.ai_records.create_derived_artifact(forged)
    )
    accepted_ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, accepted_ctx, accepted_ctx["oa1"], follow_up=False)
    (accepted,) = f04.artifacts(db_connection, accepted_ctx, "AIOP-001")
    for stmt in (
        "UPDATE ai_derived_artifacts SET content = 'forged' WHERE id = :i",
        "DELETE FROM ai_derived_artifacts WHERE id = :i",
    ):
        assert "rejected" in _raises_db(db_connection, sa.text(stmt), {"i": accepted["id"]})


def test_generation_oa_fields_are_identity_immutable(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    generation = _generation(db_connection, ctx, _oa(db_connection, ctx["oa1"]))
    for column in ("authorizing_command_id", "operation_authorization_id", "session_id"):
        assert "identity fields are immutable" in _raises_db(
            db_connection,
            sa.text(f"UPDATE ai_generations SET {column} = NULL WHERE id = :i"),
            {"i": generation.ai_generation_id.value},
        )


def _fields(proof: AIValidationProof) -> dict[str, Any]:
    return {name: getattr(proof, name) for name in proof.__dataclass_fields__}
