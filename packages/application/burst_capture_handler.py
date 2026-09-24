"""CMD_CAPTURE_BURST_QUESTION (F03 WU-03.6): TRN-Q-001 / AUTH-DEP-Q-001.

An authorized participant captures ONE human Question into the ACTIVE
HUMAN_ONLY Burst of their Session. The Question (HUMAN origin, author = the
actor, `original_text` byte-exact, `normalized_text` NULL) and its Burst
membership (order, time, actor, HUMAN) are created in ONE commit. Session and
Burst are not changed (03 TRN-Q-001: "Session remains QUESTION_GENERATION").

AUTHORITY (16 §41 REC-016 / NQ-DEC-043): the source-explicit participation
right of 04 AUTH-DEP-Q-001. It is resolved in the precommit chain (BND-005
participation evaluator) and re-resolved at commit (BND-014, PARTICIPATION
source), both from `boundaries.participation_right`. A Workspace role, a
Session-control binding, controller status, Ownership or any client claim
grants nothing here (`ROLE != AUTHORITY`, `Capability != Authority`).

ORDER OF REFUSALS (each is a distinct, non-overlapping outcome; an unauthorized
actor learns nothing about validation or state):

1. Not found / foreign Workspace / not the actor's Session -> `denied`.
2. Not an authorized participant -> `denied` (`PARTICIPATION_NOT_CURRENT`, ...).
3. Input is not `BURST_INPUT_VALID` (HD-12) -> `rejected`; nothing is stored.
4. Session not QUESTION_GENERATION, Burst absent / not ACTIVE / not HUMAN_ONLY ->
   `blocked` (a lawful precondition is unmet, e.g. a late capture after freeze).
5. `expected_burst_version` is not the current Burst version -> `stale`.
6. BND-008 (AI / actor / input contamination facts) must ALLOW.
7. BND-014 re-validates version and authority at commit.

CONCURRENCY (FBR-F03-2 / FBR-F03-6): after refusal 3, the Burst row is locked
(`FOR NO KEY UPDATE`) and Session + Burst are RE-READ under the lock. Completion
takes the same lock first, so a capture and the completion are mutually
exclusive: a capture never commits into a set whose fingerprint was already
computed, and `captured_order` is assigned without a race. The DB restates both
(freeze trigger requires ACTIVE; `UNIQUE (burst, captured_order)`).

IDEMPOTENCY: the HTTP Idempotency-Key is the Command id. The Question and
membership ids are derived from it (`uuid5`), so a retry can never create a
second Question. The payload fingerprint covers the exact text, so the same key
with another text is a collision.

NO AI: this path imports no AI gateway, calls no model and accepts no
`origin` / `author` / `mode` input. The Question's origin and author come only
from the verified actor.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass

from authority.actor import ActorClass, ActorIdentity
from boundaries.authority_source import ParticipationAuthority
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.bnd_003_membership import Bnd003Input, Bnd003MembershipEvaluator
from boundaries.bnd_005_participation import (
    Bnd005ParticipationEvaluator,
    Bnd005ParticipationInput,
)
from boundaries.bnd_008_question_burst import (
    Bnd008Input,
    Bnd008OperationCategory,
    Bnd008QuestionBurstEvaluator,
)
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from command.envelope import CommandEnvelope, CommandOutcome
from commit.coordinator import (
    CommitCoordinator,
    CommitUnit,
    FailureInjectionPort,
    MutationOutcome,
)
from domain.burst import BurstMode, BurstState, QuestionBurst
from domain.burst_input import check_burst_input
from domain.burst_membership import QuestionBurstMembership
from domain.question import Question, QuestionOrigin
from domain.session import Session, SessionState
from persistence.burst_repository import SqlAlchemyBurstVersionReader, burst_target_ref
from semantic_types.ids import (
    BurstId,
    QuestionId,
    RelationId,
    SessionId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion

from application.composition import GovernedPorts
from application.session_control_handler import (
    CommandIdentity,
    SessionCommandDenied,
    SessionNotFound,
    SessionPreconditionUnmet,
    SessionVersionStale,
    replay_guard,
)

COMMAND_TYPE = "CMD_CAPTURE_BURST_QUESTION"


class CaptureInputRejected(Exception):
    """The submitted text is not `BURST_INPUT_VALID` (HD-12, or a storage
    safeguard). It is an INPUT problem, never an authority statement: HTTP
    `rejected`. Nothing was stored, and the text was never altered."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


class BurstVersionStale(SessionVersionStale):
    """The caller's view of the Burst is not current (HTTP `stale`)."""


@dataclass(frozen=True, slots=True)
class CaptureQuestionPayload:
    session_id: str
    original_text: str
    expected_burst_version: int


@dataclass(frozen=True, slots=True)
class CaptureResult:
    commit_unit: CommitUnit
    question_id: QuestionId
    membership_id: RelationId
    captured_order: int


def capture_blocker(session: Session, burst: QuestionBurst | None) -> str | None:
    """TRN-Q-001 / AUTH-DEP-Q-001 preconditions that are neither authority nor
    input: shared by the Command and the capability projection, so the UI
    affordance can never disagree with what the Command enforces."""
    if session.state is not SessionState.QUESTION_GENERATION:
        return f"SESSION_NOT_QUESTION_GENERATION:{session.state.value}"
    if burst is None:
        return "BURST_ABSENT"
    if burst.state is not BurstState.ACTIVE:
        return f"BURST_NOT_ACTIVE:{burst.state.value}"
    if burst.mode is not BurstMode.HUMAN_ONLY:
        return f"BURST_MODE_NOT_HUMAN_ONLY:{burst.mode.value}"
    return None


class _Mutation:
    def __init__(self, fn: Callable[[], MutationOutcome]) -> None:
        self._fn = fn

    def apply(self) -> MutationOutcome:
        return self._fn()


def capture_burst_question(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    original_text: str,
    expected_burst_version: int,
    ident: CommandIdentity,
    failure_injector: FailureInjectionPort | None = None,
) -> CaptureResult:
    payload = CaptureQuestionPayload(
        session_id=str(session_id.value),
        original_text=original_text,
        expected_burst_version=expected_burst_version,
    )
    replay_guard(ports, workspace_id, COMMAND_TYPE, ident, payload)

    context = BoundaryContext(
        workspace_id=workspace_id,
        operation=COMMAND_TYPE,
        actor=actor,
        correlation_id=ident.correlation_id,
        evaluated_at=ident.occurred_at,
    )
    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd002WorkspaceEvaluator(ports.workspaces))  # type: ignore[arg-type]
    registry.register(Bnd003MembershipEvaluator(ports.memberships))  # type: ignore[arg-type]
    registry.register(
        Bnd005ParticipationEvaluator(ports.participations, ports.memberships)  # type: ignore[arg-type]
    )
    registry.register(Bnd008QuestionBurstEvaluator())  # type: ignore[arg-type]

    session = ports.sessions.get(session_id)
    workspace = ports.workspaces.get(workspace_id)
    inputs: dict[BoundaryId, object] = {
        BoundaryId.BND_001: Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=context,
            required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
        ),
        BoundaryId.BND_002: Bnd002Input(
            boundary_id=BoundaryId.BND_002,
            context=context,
            resolved_object_workspace_ids=(session.workspace_id,) if session is not None else (),
        ),
        BoundaryId.BND_003: Bnd003Input(boundary_id=BoundaryId.BND_003, context=context),
        BoundaryId.BND_005: Bnd005ParticipationInput(
            boundary_id=BoundaryId.BND_005, context=context, session_id=session_id.value
        ),
    }
    # An unknown/foreign Workspace or Session is denied by BND-001/002 without
    # recording an attempt (a `commands` row needs its Workspace, FK).
    if workspace is None or session is None:
        raise SessionCommandDenied(
            evaluate_chain(
                registry,
                (BoundaryId.BND_001, BoundaryId.BND_002),
                inputs,  # type: ignore[arg-type]
                context,
            )
        )

    unlocked_burst = ports.bursts.get_by_session(session_id)
    question_id = QuestionId(uuid.uuid5(ident.command_id.value, "question"))
    membership_id = RelationId(uuid.uuid5(ident.command_id.value, "burst_question_membership"))
    target_refs: tuple[str, ...] = ()
    expected_versions: dict[str, RecordVersion] = {}
    if unlocked_burst is not None:
        bref = burst_target_ref(unlocked_burst.burst_id)
        target_refs = (bref,)
        expected_versions = {bref: RecordVersion(expected_burst_version)}

    envelope = CommandEnvelope(
        command_id=ident.command_id,
        command_type=COMMAND_TYPE,
        command_contract_version=ContractVersion("1.0"),
        attempt_id=ident.attempt_id,
        correlation_id=ident.correlation_id,
        requested_at=ident.occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=target_refs,
        expected_versions=expected_versions,
        created_refs=(
            f"question:{question_id.value}",
            f"burst_question_membership:{membership_id.value}",
        ),
        payload=payload,
        idempotency_key=ident.idempotency_key,
    )
    ports.commands.record_attempt(envelope, received_at=ident.occurred_at)

    def refuse(failure_code: str) -> None:
        ports.commands.record_outcome(
            attempt_id=ident.attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=ident.occurred_at,
            failure_code=failure_code,
        )

    # (1)+(2) identity, Workspace, membership, participation right.
    authority_chain = evaluate_chain(
        registry,
        (BoundaryId.BND_001, BoundaryId.BND_002, BoundaryId.BND_003, BoundaryId.BND_005),
        inputs,  # type: ignore[arg-type]
        context,
    )
    if authority_chain.result is not BoundaryResult.ALLOW:
        refuse("AUTHORITY_DENIED")
        raise SessionCommandDenied(authority_chain)

    # (3) BURST_INPUT_VALID (HD-12): input, not authority; nothing is altered.
    input_check = check_burst_input(original_text)
    if not input_check.valid:
        refuse(f"INPUT_REJECTED:{input_check.reason_code}")
        raise CaptureInputRejected(input_check.reason_code or "INPUT_INVALID")

    # Lock, then RE-READ everything the preconditions depend on (FBR-F03-2).
    burst = ports.bursts.get_by_session_for_update(session_id)
    session = ports.sessions.get(session_id)
    if session is None:  # pragma: no cover -- existed a moment ago; rows are never deleted
        raise SessionNotFound(str(session_id.value))

    # (4) lawful preconditions.
    blocker = capture_blocker(session, burst)
    if blocker is not None:
        refuse("PRECONDITION_UNMET")
        raise SessionPreconditionUnmet(blocker)
    assert burst is not None  # noqa: S101 -- capture_blocker guarantees it

    # (5) the caller's view of the Burst must be current.
    if burst.record_version.value != expected_burst_version:
        refuse("STALE_VERSION")
        raise BurstVersionStale(
            expected=expected_burst_version,
            current=burst.record_version.value,
            current_state=burst.state.value,
        )

    # (6) BND-008: capture actor + input validity, established (not assumed).
    bnd008_inputs: dict[BoundaryId, object] = {
        BoundaryId.BND_008: Bnd008Input(
            boundary_id=BoundaryId.BND_008,
            context=context,
            burst_state=burst.state,
            operation_category=Bnd008OperationCategory.CAPTURE_BURST_QUESTION,
            input_check=input_check,
        )
    }
    contamination = evaluate_chain(
        registry,
        (BoundaryId.BND_008,),
        bnd008_inputs,  # type: ignore[arg-type]
        context,
    )
    if contamination.result is not BoundaryResult.ALLOW:
        refuse(
            "BND008_" + (contamination.proofs[-1].reason_code[:80] if contamination.proofs else "")
        )
        raise SessionCommandDenied(contamination)

    burst_id: BurstId = burst.burst_id
    captured_order = ports.bursts.next_captured_order(burst_id)

    def mutate() -> MutationOutcome:
        ports.questions.create_root(
            Question(
                question_id=question_id,
                challenge_id=session.challenge_id,
                workspace_id=session.workspace_id,
                original_text=original_text,  # verbatim: never trimmed, normalized or cased
                normalized_text=None,
                origin=QuestionOrigin.HUMAN,
                author_user_id=actor.user_id,
                created_at=ident.occurred_at,
                record_version=RecordVersion.initial(),
            )
        )
        ports.bursts.add_member(
            QuestionBurstMembership(
                burst_question_membership_id=membership_id,
                question_burst_id=burst_id,
                question_id=question_id,
                workspace_id=session.workspace_id,
                captured_order=captured_order,
                captured_at=ident.occurred_at,
                capture_actor_user_id=actor.user_id,
                capture_origin=QuestionOrigin.HUMAN,
                record_version=RecordVersion.initial(),
            )
        )
        return MutationOutcome(
            state_before_ref=None,
            # EC-2: deliberately NOT a `session:*` ref (capture establishes no Session state).
            state_after_ref=f"question:{question_id.value}|burst:{burst.state.value}",
            relation_refs=(f"burst_question_membership:{membership_id.value}",),
            event_type="BURST_QUESTION_CAPTURED",
            result_ref=str(question_id.value),
        )

    if ident.idempotency_key is not None:
        ports.idempotency.begin(envelope, seen_at=ident.occurred_at)

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
    unit = coordinator.commit(
        envelope=envelope,
        actor=actor,
        authority=ParticipationAuthority(session_id=session_id.value),
        upstream_chain_result=BoundaryResult.ALLOW,
        current_version_reader=SqlAlchemyBurstVersionReader(ports.connection, burst_id=burst_id),
        mutation=_Mutation(mutate),
        occurred_at=ident.occurred_at,
        commit_id=ident.commit_id,
    )
    return CaptureResult(
        commit_unit=unit,
        question_id=question_id,
        membership_id=membership_id,
        captured_order=captured_order,
    )


__all__ = [
    "COMMAND_TYPE",
    "BurstVersionStale",
    "CaptureInputRejected",
    "CaptureQuestionPayload",
    "CaptureResult",
    "capture_blocker",
    "capture_burst_question",
]
