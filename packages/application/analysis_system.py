"""F04 system execution of an operation authorization (WU-04.5 / WU-04.9).

HD-16 / HD-17 / HD-23; reconstruction §0.1; pre-implementation bindings
PI-1, PI-2, PI-3.

For one operation authorization OA, IMMEDIATELY after the commit that created
it (rule 5: never later), in separate transactions (PI-2):

T2a  EXECUTE (Command CMD_AI_QUESTION_ANALYSIS / CMD_AI_QUESTION_CLUSTERING,
     actor SYSTEM_SERVICE, effect-gate source SYSTEM_OPERATION, PURPOSE EXECUTE):
     under the Session row lock: BND-001 (SYSTEM_SERVICE) → BND-002 →
     SYSTEM_OPERATION (OA current, latest, unconsumed) → verified frozen input
     → BND-008 (COMPLETED) → manifest bound to the frozen set → BND-009 →
     BND-014 SYSTEM_OPERATION. Writes the immutable manifest and the generation
     (REQUESTED → RUNNING) carrying OA. This consumes OA (rule 3).
     The durable T1 before it (BEGIN_ANALYSIS, a request, an acceptance) is
     the caller's.

     provider call through the Gateway: outside every lock and transaction.

T2b+T3 ACCEPT (Command CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT /
     CMD_ACCEPT_CLUSTERING_OUTPUT, SYSTEM_OPERATION, PURPOSE ACCEPT), only for a
     VALIDATED candidate: SYSTEM_OPERATION → BND-010 → BND-014. ONE commit
     (PI-1): generation OUTPUT_RECEIVED → VALIDATED, the persisted proof, the
     accepted artifact (MOCK_NON_PROOF for the mock), and for AIOP-001 the
     clustering authorization OA-3 = (C, AIOP-002) with X = the artifact
     (HD-23, R7); for AIOP-002 the cluster run (09 §34/35).

Otherwise a plain operational transaction records the honest terminal state:
provider timeout / error → FAILED; REJECTED output → REJECTED + proof;
INDETERMINATE validation → FAILED + proof; a VALIDATED candidate whose
acceptance was denied → FAILED (`ACCEPTANCE_DENIED:<reason>`) with the validated
output fingerprint in `failure_detail_ref` and NO proof row: a persisted
VALIDATED proof exists only with its accepted artifact (PI-1; review R2). An
INDETERMINATE commit leaves the generation RUNNING: no blind retry (BND-017; a
disclosed ceiling, P8).

After an ACCEPTED AIOP-001 artifact the system executes OA-3 at once (HD-23).
A failed or rejected AIOP-001 never creates OA-3, so no clustering can run
(K7). Nothing here changes a Session, a Question, a membership or a
fingerprint.

This is the only module that constructs the F04 SYSTEM_SERVICE actor
(PI-3; static gate).
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ai_contracts.aiop import AIOperationContract, AIOperationId
from ai_contracts.authorization import AuthorizationShape, OperationAuthorization
from ai_contracts.derived_artifact import AIDerivedArtifact, ProofClass
from ai_contracts.f04_operations import (
    AIOP_001_TOP_LEVEL,
    AIOP_002_TOP_LEVEL,
    QUESTION_ANALYSIS,
    QUESTION_CLUSTERING,
    f04_operation_registry,
)
from ai_contracts.generation import (
    AIGeneration,
    AIGenerationStatus,
    AIValidationProof,
    AIValidationResult,
)
from ai_gateway.adapters.providers.mock import MOCK_PROVIDER
from ai_gateway.context import AIContextManifest
from ai_gateway.gateway import GatewayCandidate
from authority.actor import ActorClass, ActorIdentity
from authority.system_service import F04_ANALYSIS_SERVICE_ID
from boundaries.authority_source import SystemOperationAuthority, SystemOperationPurpose
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.bnd_008_question_burst import (
    Bnd008Input,
    Bnd008OperationCategory,
    Bnd008QuestionBurstEvaluator,
)
from boundaries.bnd_009_ai_invocation import Bnd009AiInvocationEvaluator, Bnd009Input
from boundaries.bnd_010_ai_output import Bnd010AiOutputEvaluator, Bnd010Input
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.system_operation import resolve_system_operation
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from command.envelope import CommandEnvelope, CommandOutcome
from commit.coordinator import (
    CommitCoordinator,
    CommitDenied,
    CommitFailedPrecommit,
    CommitIndeterminate,
    FailureInjectionPort,
    MutationOutcome,
)
from domain.question_selection import session_target_ref
from domain.session import Session
from events.contracts import EventFacts
from persistence.question_cluster_repository import QuestionCluster
from persistence.session_repository import SqlAlchemySessionVersionReader
from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    GenerationId,
    QuestionId,
    SessionId,
)
from semantic_types.versions import ContractVersion, RecordVersion

from application.analysis_input import (
    PROMPT_VERSION,
    FrozenInput,
    FrozenInputUnavailable,
    ManifestBindingViolation,
    build_manifest,
    build_prompt,
    load_verified_frozen_input,
    verify_manifest_binding,
)
from application.analysis_runtime import AnalysisRuntime
from application.composition import GovernedPorts
from application.session_control_handler import _Mutation

UnitOfWork = Callable[[], AbstractContextManager[GovernedPorts]]
"""One call = one database transaction whose ports it yields (PI-2)."""

CONTRACTS: dict[AIOperationId, AIOperationContract] = {
    AIOperationId.AIOP_001: QUESTION_ANALYSIS,
    AIOperationId.AIOP_002: QUESTION_CLUSTERING,
}
EXECUTE_COMMAND = {
    AIOperationId.AIOP_001: "CMD_AI_QUESTION_ANALYSIS",
    AIOperationId.AIOP_002: "CMD_AI_QUESTION_CLUSTERING",
}
ACCEPT_COMMAND = {
    AIOperationId.AIOP_001: "CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT",
    AIOperationId.AIOP_002: "CMD_ACCEPT_CLUSTERING_OUTPUT",
}
_BND008_CATEGORY = {
    AIOperationId.AIOP_001: Bnd008OperationCategory.AI_ANALYSIS,
    AIOperationId.AIOP_002: Bnd008OperationCategory.AI_CLUSTER,
}
_TOP_LEVEL = {
    AIOperationId.AIOP_001: AIOP_001_TOP_LEVEL,
    AIOperationId.AIOP_002: AIOP_002_TOP_LEVEL,
}


def _service_actor() -> ActorIdentity:
    return ActorIdentity(ActorClass.SYSTEM_SERVICE, F04_ANALYSIS_SERVICE_ID)


# --------------------------------------------------------------------- outcomes


@dataclass(frozen=True)
class RunOutcome:
    """The run's outcome as a SEPARATE fact from the Command that authorized it
    (a failed run never makes BEGIN_ANALYSIS look failed)."""

    ai_operation_id: AIOperationId
    authorization_id: uuid.UUID
    status: str
    """NOT_EXECUTED | FAILED | REJECTED | ACCEPTANCE_DENIED | INDETERMINATE | ACCEPTED"""
    reason_code: str | None = None
    generation_id: uuid.UUID | None = None
    artifact_id: uuid.UUID | None = None
    next: RunOutcome | None = None
    """For an ACCEPTED AIOP-001 run: the clustering run it authorized (HD-23)."""

    def to_json(self) -> dict[str, object]:
        return {
            "operation": self.ai_operation_id.value,
            "authorizationId": str(self.authorization_id),
            "status": self.status,
            "reasonCode": self.reason_code,
            "generationId": None if self.generation_id is None else str(self.generation_id),
            "artifactId": None if self.artifact_id is None else str(self.artifact_id),
            "next": None if self.next is None else self.next.to_json(),
        }


@dataclass(frozen=True, slots=True)
class SystemOperationPayload:
    """The typed payload of every F04 system Command (09 §9)."""

    session_id: str
    operation_authorization_id: str
    purpose: str
    ai_generation_id: str | None


class _Denied(Exception):
    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True)
class _Committed:
    command_id: CommandId
    value: Any


@dataclass(frozen=True)
class _NotCommitted:
    status: str
    reason_code: str


# ----------------------------------------------------------- the system commit


def _system_commit(
    ports: GovernedPorts,
    *,
    session: Session,
    command_type: str,
    authority: SystemOperationAuthority,
    occurred_at: datetime,
    precheck: Callable[[], None],
    mutate: Callable[[CommandId], MutationOutcome],
    failure_injector: FailureInjectionPort | None = None,
) -> _Committed | _NotCommitted:
    """A governed SYSTEM_SERVICE Command. Records its attempt, runs the system
    precommit chain, then commits through BND-014 SYSTEM_OPERATION. A denial is
    recorded (not raised), so the caller's transaction keeps the record."""
    actor = _service_actor()
    workspace_id = session.workspace_id
    command_id = CommandId(uuid.uuid4())
    attempt_id = AttemptId(uuid.uuid4())
    correlation_id = CorrelationId(uuid.uuid4())
    context = BoundaryContext(
        workspace_id=workspace_id,
        operation=command_type,
        actor=actor,
        correlation_id=correlation_id,
        evaluated_at=occurred_at,
    )
    session_ref = session_target_ref(session.session_id)
    envelope = CommandEnvelope(
        command_id=command_id,
        command_type=command_type,
        command_contract_version=ContractVersion("1.0"),
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        requested_at=occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=(session_ref,),
        expected_versions={session_ref: session.record_version},
        created_refs=(),
        payload=SystemOperationPayload(
            session_id=str(session.session_id.value),
            operation_authorization_id=str(authority.operation_authorization_id),
            purpose=authority.purpose.value,
            ai_generation_id=None
            if authority.ai_generation_id is None
            else str(authority.ai_generation_id),
        ),
        idempotency_key=None,
    )
    ports.commands.record_attempt(envelope, received_at=occurred_at)

    def denied(reason_code: str) -> _NotCommitted:
        ports.commands.record_outcome(
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=occurred_at,
            failure_code=reason_code[:200],
        )
        return _NotCommitted("NOT_EXECUTED", reason_code)

    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd002WorkspaceEvaluator(ports.workspaces))  # type: ignore[arg-type]
    inputs: dict[BoundaryId, object] = {
        BoundaryId.BND_001: Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=context,
            required_actor_classes=frozenset({ActorClass.SYSTEM_SERVICE}),
        ),
        BoundaryId.BND_002: Bnd002Input(
            boundary_id=BoundaryId.BND_002,
            context=context,
            resolved_object_workspace_ids=(session.workspace_id,),
        ),
    }
    chain = evaluate_chain(
        registry,
        (BoundaryId.BND_001, BoundaryId.BND_002),
        inputs,  # type: ignore[arg-type]
        context,
    )
    if chain.result is not BoundaryResult.ALLOW:
        return denied(chain.proofs[-1].reason_code if chain.proofs else "DENIED")
    try:
        resolution = resolve_system_operation(
            reader=ports.system_operations,
            actor=actor,
            workspace_id=workspace_id,
            authority=authority,
        )
        if not resolution.granted:
            raise _Denied(resolution.reason_code)
        precheck()
    except _Denied as exc:
        return denied(exc.reason_code)

    coordinator = CommitCoordinator(
        ports.connection,
        bnd014_evaluator=ports.bnd014(),
        command_repository=ports.commands,
        audit_repository=ports.audit,
        outbox_repository=ports.outbox,
        commit_repository=ports.commits,
        idempotency_port=ports.idempotency,
        failure_injector=failure_injector,
    )
    holder: dict[str, Any] = {}

    def apply() -> MutationOutcome:
        outcome = mutate(command_id)
        holder["value"] = outcome.result_ref
        return outcome

    try:
        coordinator.commit(
            envelope=envelope,
            actor=actor,
            authority=authority,
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=SqlAlchemySessionVersionReader(
                ports.connection, session_id=session.session_id
            ),
            mutation=_Mutation(apply),
            occurred_at=occurred_at,
            commit_id=CommitId(uuid.uuid4()),
        )
    except CommitDenied as exc:
        return _NotCommitted("NOT_EXECUTED", exc.boundary_proof.reason_code)
    except CommitFailedPrecommit as exc:
        return _NotCommitted("FAILED_PRECOMMIT", exc.reason)
    except CommitIndeterminate:
        return _NotCommitted("INDETERMINATE", "COMMIT_OUTCOME_UNPROVEN")
    return _Committed(command_id, holder.get("value"))


# ------------------------------------------------------------------ T2a EXECUTE


@dataclass(frozen=True)
class _Prepared:
    generation_id: GenerationId
    frozen: FrozenInput
    manifest: AIContextManifest
    authorization: OperationAuthorization


def _execute(
    ports: GovernedPorts,
    *,
    session_id: SessionId,
    authorization_id: uuid.UUID,
    runtime: AnalysisRuntime,
    occurred_at: datetime,
    failure_injector: FailureInjectionPort | None,
) -> _Prepared | _NotCommitted:
    session = ports.sessions.get_for_update(session_id)
    oa = ports.ai_authorizations.get(authorization_id)
    if session is None or oa is None:
        return _NotCommitted("NOT_EXECUTED", "SYSTEM_OPERATION_AUTHORIZATION_NOT_FOUND")
    op = oa.ai_operation_id
    contract = CONTRACTS[op]
    assert runtime.gateway is not None  # noqa: S101 -- checked by the caller
    generation_id = GenerationId(uuid.uuid4())
    plan: dict[str, Any] = {}

    def precheck() -> None:
        try:
            frozen = load_verified_frozen_input(ports, session)
        except FrozenInputUnavailable as exc:
            raise _Denied(exc.reason_code) from exc
        actor_context = BoundaryContext(
            workspace_id=session.workspace_id,
            operation=EXECUTE_COMMAND[op],
            actor=_service_actor(),
            correlation_id=CorrelationId(uuid.uuid4()),
            evaluated_at=occurred_at,
        )
        bnd008 = Bnd008QuestionBurstEvaluator().evaluate(
            Bnd008Input(
                boundary_id=BoundaryId.BND_008,
                context=actor_context,
                burst_state=frozen.burst.state,
                operation_category=_BND008_CATEGORY[op],
            ),
            actor_context,
        )
        if bnd008.result is not BoundaryResult.ALLOW:
            raise _Denied(bnd008.reason_code)
        registered = f04_operation_registry().get(op)
        manifest = build_manifest(
            frozen,
            contract=contract,
            manifest_id=uuid.uuid4(),
            requesting_actor_ref=f"SYSTEM_SERVICE:{F04_ANALYSIS_SERVICE_ID.value}|OA:{oa.authorization_id}",
            assembled_at=occurred_at,
        )
        try:
            # D2 / D3 / D7: against a FRESH re-verification, before the provider.
            verify_manifest_binding(manifest, load_verified_frozen_input(ports, session))
        except (ManifestBindingViolation, FrozenInputUnavailable) as exc:
            raise _Denied(exc.reason_code) from exc
        bnd009 = Bnd009AiInvocationEvaluator().evaluate(
            Bnd009Input(
                boundary_id=BoundaryId.BND_009,
                context=actor_context,
                ai_operation_id=op,
                ai_operation_contract_version=contract.contract_version,
                aiop_contract_approved=registered == contract,
                context_manifest_workspace_id=manifest.workspace_id,
                burst_state=frozen.burst.state,
                frozen_set_verified=True,
            ),
            actor_context,
        )
        if bnd009.result is not BoundaryResult.ALLOW:
            raise _Denied(bnd009.reason_code)
        plan["frozen"], plan["manifest"] = frozen, manifest

    def mutate(command_id: CommandId) -> MutationOutcome:
        manifest: AIContextManifest = plan["manifest"]
        ports.ai_records.create_context_manifest(manifest)
        ports.ai_records.create_generation(
            AIGeneration(
                ai_generation_id=generation_id,
                workspace_id=session.workspace_id,
                ai_operation_id=op,
                ai_operation_contract_version=contract.contract_version,
                prompt_version=PROMPT_VERSION,
                model=runtime.gateway.model,  # type: ignore[union-attr]
                provider=runtime.gateway.provider,  # type: ignore[union-attr]
                status=AIGenerationStatus.REQUESTED,
                requested_at=occurred_at,
                correlation_id=CorrelationId(uuid.uuid4()),
                record_version=RecordVersion.initial(),
                ai_context_manifest_id=manifest.ai_context_manifest_id,
                command_id=command_id,
                retry_of_generation_id=oa.retry_of_generation_id,
                session_id=session_id,
                operation_authorization_id=oa.authorization_id,
                authorizing_command_id=oa.authorizing_command_id,
                precondition_artifact_ref=oa.precondition_artifact_ref,
            )
        )
        ports.ai_records.update_generation_status(
            ai_generation_id=generation_id,
            workspace_id=session.workspace_id,
            expected_record_version=RecordVersion.initial(),
            new_status=AIGenerationStatus.RUNNING,
            started_at=occurred_at,
        )
        return MutationOutcome(
            state_before_ref=f"ai_operation_authorization:{oa.authorization_id}:UNCONSUMED",
            state_after_ref=f"ai_generation:{generation_id.value}:RUNNING",
            relation_refs=(
                f"ai_context_manifest:{manifest.ai_context_manifest_id}",
                f"ai_generation:{generation_id.value}",
            ),
            event_type="AI_GENERATION_REQUESTED",
            result_ref=str(generation_id.value),
            event=EventFacts(
                aggregate_ref=f"ai_generation:{generation_id.value}",
                payload={
                    "ai_generation_id": str(generation_id.value),
                    "session_id": str(session_id.value),
                    "operation_authorization_id": str(oa.authorization_id),
                    "ai_context_manifest_id": str(manifest.ai_context_manifest_id),
                    "ai_operation_id": oa.ai_operation_id.value,
                    "status": AIGenerationStatus.RUNNING.value,
                },
            ),
        )

    result = _system_commit(
        ports,
        session=session,
        command_type=EXECUTE_COMMAND[op],
        authority=SystemOperationAuthority(
            session_id=session_id.value,
            operation_authorization_id=oa.authorization_id,
            purpose=SystemOperationPurpose.EXECUTE,
        ),
        occurred_at=occurred_at,
        precheck=precheck,
        mutate=mutate,
        failure_injector=failure_injector,
    )
    if isinstance(result, _NotCommitted):
        return result
    return _Prepared(generation_id, plan["frozen"], plan["manifest"], oa)


# ------------------------------------------------------------- T2b+T3 ACCEPT


def _accept(
    ports: GovernedPorts,
    *,
    session_id: SessionId,
    prepared: _Prepared,
    candidate: GatewayCandidate,
    occurred_at: datetime,
    failure_injector: FailureInjectionPort | None,
) -> _Committed | _NotCommitted:
    session = ports.sessions.get_for_update(session_id)
    assert session is not None  # noqa: S101 -- rows are never deleted
    oa = prepared.authorization
    op = oa.ai_operation_id
    validation = candidate.validation
    assert validation is not None and validation.payload is not None  # noqa: S101
    proof = validation.proof
    response = candidate.response
    assert response is not None  # noqa: S101
    artifact_id = uuid.uuid4()
    generation = ports.ai_records.get_generation(prepared.generation_id)
    assert generation is not None  # noqa: S101

    def precheck() -> None:
        context = BoundaryContext(
            workspace_id=session.workspace_id,
            operation=ACCEPT_COMMAND[op],
            actor=_service_actor(),
            correlation_id=CorrelationId(uuid.uuid4()),
            evaluated_at=occurred_at,
        )
        bnd010 = Bnd010AiOutputEvaluator().evaluate(
            Bnd010Input(
                boundary_id=BoundaryId.BND_010,
                context=context,
                # PI-1: the generation becomes VALIDATED in THIS commit, exactly
                # when the persisted proof is VALIDATED; the proof decides.
                ai_generation_status=(
                    AIGenerationStatus.VALIDATED
                    if proof.validation_result is AIValidationResult.VALIDATED
                    else generation.status
                ),
                validation_result=proof.validation_result,
                source_workspace_id=generation.workspace_id,
                ai_validation_proof_ref=str(proof.ai_validation_proof_id),
                output_fields=frozenset(validation.payload),  # type: ignore[arg-type]
                permitted_output_fields=_TOP_LEVEL[op],
            ),
            context,
        )
        if bnd010.result is not BoundaryResult.ALLOW:
            raise _Denied(bnd010.reason_code)

    def mutate(command_id: CommandId) -> MutationOutcome:
        records = ports.ai_records
        records.update_generation_status(
            ai_generation_id=generation.ai_generation_id,
            workspace_id=generation.workspace_id,
            expected_record_version=generation.record_version,
            new_status=AIGenerationStatus.OUTPUT_RECEIVED,
            output_received_at=occurred_at,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=response.latency_ms,
        )
        records.update_generation_status(
            ai_generation_id=generation.ai_generation_id,
            workspace_id=generation.workspace_id,
            expected_record_version=generation.record_version.next(),
            new_status=AIGenerationStatus.VALIDATED,
            completed_at=occurred_at,
            output_artifact_ref=artifact_id,
        )
        records.create_validation_proof(proof, workspace_id=generation.workspace_id)
        records.create_derived_artifact(
            AIDerivedArtifact(
                ai_derived_artifact_id=artifact_id,
                workspace_id=generation.workspace_id,
                ai_generation_id=generation.ai_generation_id,
                ai_operation_id=op,
                # R1 (09 §118, PI-1): the EXACT bytes the validator fingerprinted,
                # never a re-serialization, so sha256(content) = content_fingerprint
                # = proof.output_fingerprint holds on persisted records alone.
                content=response.raw_content,
                content_fingerprint=proof.output_fingerprint,
                created_at=occurred_at,
                record_version=RecordVersion.initial(),
                provenance_ref=(
                    f"generation:{generation.ai_generation_id.value}"
                    f"|manifest:{generation.ai_context_manifest_id}"
                    f"|proof:{proof.ai_validation_proof_id}|OA:{oa.authorization_id}"
                ),
                session_id=session_id,
                accepted_by_command_id=command_id,
                proof_class=(
                    ProofClass.MOCK_NON_PROOF
                    if generation.provider == MOCK_PROVIDER
                    else ProofClass.PROVIDER_OUTPUT
                ),
            )
        )
        relation_refs = [
            f"ai_derived_artifact:{artifact_id}",
            f"ai_validation_proof:{proof.ai_validation_proof_id}",
        ]
        if op is AIOperationId.AIOP_001:
            # HD-23 / R7: acceptance creates OA-3 = (C, AIOP-002), C = the
            # Command that authorized this artifact; X = this artifact.
            oa3 = uuid.uuid4()
            ports.ai_authorizations.create(
                OperationAuthorization(
                    authorization_id=oa3,
                    workspace_id=generation.workspace_id,
                    session_id=session_id,
                    ai_operation_id=AIOperationId.AIOP_002,
                    shape=AuthorizationShape.OA_3,
                    authorizing_command_id=oa.authorizing_command_id,
                    sequence_no=1,
                    chain_root_command_id=oa.chain_root_command_id,
                    created_at=occurred_at,
                    precondition_artifact_ref=artifact_id,
                )
            )
            relation_refs.append(f"ai_operation_authorization:{oa3}")
            event = "AI_OUTPUT_ACCEPTED"
        else:
            payload = validation.payload
            assert payload is not None  # noqa: S101
            ports.question_clusters.create_run(
                tuple(
                    QuestionCluster(
                        cluster_id=uuid.uuid4(),
                        workspace_id=generation.workspace_id,
                        session_id=session_id,
                        challenge_id=session.challenge_id,
                        analysis_generation_id=generation.ai_generation_id,
                        cluster_run_id=artifact_id,
                        label=cluster["label"],
                        description=cluster["description"],
                        created_at=occurred_at,
                        question_ids=tuple(
                            QuestionId(uuid.UUID(ref.split(":", 1)[1]))
                            for ref in cluster["question_refs"]
                        ),
                    )
                    for cluster in payload["clusters"]
                )
            )
            event = "QUESTION_CLUSTERS_ACCEPTED"
        return MutationOutcome(
            state_before_ref=f"ai_generation:{generation.ai_generation_id.value}:RUNNING",
            state_after_ref=(
                f"ai_generation:{generation.ai_generation_id.value}:VALIDATED"
                f"|ai_derived_artifact:{artifact_id}:ACCEPTED"
            ),
            relation_refs=tuple(relation_refs),
            event_type=event,
            result_ref=str(artifact_id),
            event=EventFacts(
                aggregate_ref=f"ai_derived_artifact:{artifact_id}",
                payload={
                    "ai_derived_artifact_id": str(artifact_id),
                    "ai_generation_id": str(generation.ai_generation_id.value),
                    "session_id": str(session_id.value),
                    "ai_operation_id": op.value,
                    "generation_status": AIGenerationStatus.VALIDATED.value,
                },
            ),
        )

    return _system_commit(
        ports,
        session=session,
        command_type=ACCEPT_COMMAND[op],
        authority=SystemOperationAuthority(
            session_id=session_id.value,
            operation_authorization_id=oa.authorization_id,
            purpose=SystemOperationPurpose.ACCEPT,
            ai_generation_id=generation.ai_generation_id.value,
        ),
        occurred_at=occurred_at,
        precheck=precheck,
        mutate=mutate,
        failure_injector=failure_injector,
    )


# ------------------------------------------------------- operational endings


def _finalize(
    ports: GovernedPorts,
    *,
    session_id: SessionId,
    generation_id: GenerationId,
    status: AIGenerationStatus,
    occurred_at: datetime,
    candidate: GatewayCandidate,
    failure_code: str | None,
    failure_detail_ref: str | None = None,
) -> None:
    """Records an honest terminal state of a generation that produced no effect.
    Operational only: no Command, no audit, nothing canonical.

    R2 (PI-1): a VALIDATED proof is never persisted here. It exists only inside
    the acceptance commit, together with the VALIDATED generation and its
    accepted artifact. REJECTED / INDETERMINATE proofs are recorded as before."""
    ports.sessions.get_for_update(session_id)
    records = ports.ai_records
    generation = records.get_generation(generation_id)
    assert generation is not None  # noqa: S101
    version = generation.record_version
    response = candidate.response
    if response is not None:
        records.update_generation_status(
            ai_generation_id=generation_id,
            workspace_id=generation.workspace_id,
            expected_record_version=version,
            new_status=AIGenerationStatus.OUTPUT_RECEIVED,
            output_received_at=occurred_at,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=response.latency_ms,
        )
        version = version.next()
    records.update_generation_status(
        ai_generation_id=generation_id,
        workspace_id=generation.workspace_id,
        expected_record_version=version,
        new_status=status,
        completed_at=occurred_at,
        failure_code=failure_code,
        failure_detail_ref=failure_detail_ref or candidate.failure_detail,
    )
    proof: AIValidationProof | None = candidate.proof
    if proof is not None and proof.validation_result is not AIValidationResult.VALIDATED:
        records.create_validation_proof(proof, workspace_id=generation.workspace_id)


# ------------------------------------------------------------------ the run


def run_authorized_operation(
    uow: UnitOfWork,
    *,
    session_id: SessionId,
    authorization_id: uuid.UUID,
    runtime: AnalysisRuntime,
    now: Callable[[], datetime],
    failure_injector: FailureInjectionPort | None = None,
    accept_failure_injector: FailureInjectionPort | None = None,
    stop_after_execute: bool = False,
    follow_up: bool = True,
) -> RunOutcome:
    """Execute OA, immediately after the commit that created it. Test-only
    knobs: `failure_injector` (T2a), `accept_failure_injector` (T2b+T3),
    `stop_after_execute` (a process stop after T2a), `follow_up=False` (a
    process stop after the acceptance commit, before OA-3 runs; P6)."""
    with uow() as ports:
        oa = ports.ai_authorizations.get(authorization_id)
    if oa is None:
        return RunOutcome(
            AIOperationId.AIOP_001,
            authorization_id,
            "NOT_EXECUTED",
            "SYSTEM_OPERATION_AUTHORIZATION_NOT_FOUND",
        )
    op = oa.ai_operation_id
    if runtime.gateway is None:
        # Honest UNAVAILABLE: nothing substituted, OA stays unconsumed (RECOVERY).
        return RunOutcome(op, authorization_id, "NOT_EXECUTED", "AI_PROVIDER_UNAVAILABLE")

    with uow() as ports:
        prepared = _execute(
            ports,
            session_id=session_id,
            authorization_id=authorization_id,
            runtime=runtime,
            occurred_at=now(),
            failure_injector=failure_injector,
        )
    if isinstance(prepared, _NotCommitted):
        return RunOutcome(op, authorization_id, prepared.status, prepared.reason_code)
    gid = prepared.generation_id
    if stop_after_execute:
        return RunOutcome(op, authorization_id, "INDETERMINATE", "PROCESS_STOPPED", gid.value)

    # Outside every lock and transaction (PI-2).
    candidate = runtime.gateway.invoke(
        contract=CONTRACTS[op],
        prompt=build_prompt(prepared.frozen, CONTRACTS[op]),
        allowed_question_refs=prepared.frozen.question_refs,
        ai_generation_id=gid,
        validated_at=now(),
        scripted_outcome=runtime.outcome_for(op),
    )

    def finish(
        status: AIGenerationStatus, code: str | None, run_status: str, detail: str | None = None
    ) -> RunOutcome:
        with uow() as ports:
            _finalize(
                ports,
                session_id=session_id,
                generation_id=gid,
                status=status,
                occurred_at=now(),
                candidate=candidate,
                failure_code=code,
                failure_detail_ref=detail,
            )
        return RunOutcome(op, authorization_id, run_status, code, gid.value)

    if candidate.failure is not None:
        return finish(AIGenerationStatus.FAILED, candidate.failure.value, "FAILED")
    proof = candidate.proof
    assert proof is not None  # noqa: S101
    if proof.validation_result is AIValidationResult.REJECTED:
        return finish(
            AIGenerationStatus.REJECTED,
            f"OUTPUT_REJECTED:{proof.validation_details_ref}"[:200],
            "REJECTED",
        )
    if proof.validation_result is AIValidationResult.INDETERMINATE:
        return finish(AIGenerationStatus.FAILED, "VALIDATION_INDETERMINATE", "FAILED")

    with uow() as ports:
        accepted = _accept(
            ports,
            session_id=session_id,
            prepared=prepared,
            candidate=candidate,
            occurred_at=now(),
            failure_injector=accept_failure_injector,
        )
    if isinstance(accepted, _NotCommitted):
        if accepted.status == "INDETERMINATE":
            return RunOutcome(
                op, authorization_id, "INDETERMINATE", accepted.reason_code, gid.value
            )
        # R2: FAILED with the validated output's fingerprint as the record; NO
        # proof row (a persisted VALIDATED proof implies an accepted artifact).
        return finish(
            AIGenerationStatus.FAILED,
            f"ACCEPTANCE_DENIED:{accepted.reason_code}"[:200],
            "ACCEPTANCE_DENIED",
            detail=f"validated_output_fingerprint:{proof.output_fingerprint}",
        )
    artifact_id = uuid.UUID(str(accepted.value))
    next_run: RunOutcome | None = None
    if op is AIOperationId.AIOP_001 and follow_up:
        with uow() as ports:
            oa3 = ports.ai_authorizations.latest(session_id, AIOperationId.AIOP_002)
        if oa3 is not None and oa3.precondition_artifact_ref == artifact_id:
            next_run = run_authorized_operation(
                uow,
                session_id=session_id,
                authorization_id=oa3.authorization_id,
                runtime=runtime,
                now=now,
            )
    return RunOutcome(op, authorization_id, "ACCEPTED", None, gid.value, artifact_id, next_run)


__all__ = ["RunOutcome", "UnitOfWork", "run_authorized_operation"]
