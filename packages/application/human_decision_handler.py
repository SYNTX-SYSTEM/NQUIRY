"""Human Decision: OpenDecisionConsideration and RecordHumanDecision --
the second fully governed, end-to-end production Command path in this
codebase (after PKG-14's `SelectQuestion`).

Source: 14_IMPLEMENTATION_SEQUENCE.md section 12 (COMMAND REGISTRY:
`RecordHumanDecision` row -- "DECISION_RIGHT | human creates Decision |
exact consumed Evidence set if used | 001-007,013,014,015 |
UNDER_CONSIDERATION -> DECIDED"), section 21 (HUMAN DECISION: "The
human creates the Decision the AI was never authorized to make. A
DECIDED Decision still does not equal executed downstream transition.
Downstream transition is separately authorized and revalidated.");
03_STATE_AND_TRANSITION_ARCHITECTURE.md section 35-37 (Decision State
Architecture, TRN-DEC-001/002, "Decision Does Not Equal Authorized
Execution"); 04_AUTHORITY_AND_DECISION_RIGHTS.md section 49-50
(AUTH-DEP-DEC-001/002 -- exact AUTHORITY SCOPE text).

WHY BOTH COMMANDS ARE THIS PACKAGE'S SCOPE
------------------------------------------------------------------------
See `domain.decision`'s own module docstring: 14 section 46's own
PKG-15 manifest entry reads "PUBLIC INTERFACES: Decision commands"
(plural), and no other package in the 32-package DAG is ever assigned
`CMD_OPEN_DECISION_CONSIDERATION`/TRN-DEC-001.

WHY `DECISION_RIGHT` IS CHECKED AT TWO DIFFERENT SCOPES DEPENDING ON
THE COMMAND
------------------------------------------------------------------------
04 section 49 (AUTH-DEP-DEC-001) states "AUTHORITY SCOPE: Specific
Decision/Challenge" for OPEN -- read literally: since no Decision
exists yet at that point (TRN-DEC-001's own "CURRENT STATE: Decision
absent"), the only object that genuinely exists to scope against is
the Challenge, so `scope_type="CHALLENGE"`, `scope_id=challenge_id.value`.
04 section 50 (AUTH-DEP-DEC-002) states "AUTHORITY SCOPE: Specific
Decision" for RECORD, unhedged, and by then the Decision genuinely
exists: `scope_type="DECISION"`, `scope_id=decision_id.value`. Neither
row carries 12 section 7's own bootstrap-ordering hedge (contrast
`SESSION_CONTROL_RIGHT`'s row) -- this is the third distinct,
literally-read authority-scope convention this codebase materializes
(after WORKSPACE for Burst/Session-control, SESSION for
QuestionSelection), each one following 04's own unhedged text rather
than a single copied convention.

WHY `OpenDecisionConsideration` LOOKS UP ANY EXISTING DECISION BY ITS
OWN (CALLER-SUPPLIED) `decision_id` BEFORE BUILDING THE BND-007 INPUT
------------------------------------------------------------------------
A brand-new `decision_id` naturally resolves to `current_state=None`
(state-eligible for OPEN). But `domain.decision.DecisionTransitionVerdict`
also names `DENIED_DECISION_ALREADY_EXISTS` (mirroring
`BurstTransitionVerdict`'s own precedent) for the case where a caller
retries `OpenDecisionConsideration` against a `decision_id` that
already resolved to a real, already-`UNDER_CONSIDERATION` row --
proven defense-in-depth alongside (not instead of) PKG-11's own
idempotency mechanism.

WHY THE NEWLY CREATED DECISION'S OWN REF GOES IN `relation_refs`, NOT
`target_refs`, FOR OPEN -- BUT DOES GO IN `target_refs` FOR RECORD
------------------------------------------------------------------------
See `domain.decision`'s own module docstring for the full reasoning:
AC-09-001's freshness contract cannot apply to a row that does not yet
exist, regardless of Decision's own `CANONICAL_DOMAIN_OBJECT`
representation label.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from audit.models import AuditRepository
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.bnd_003_membership import Bnd003Input, Bnd003MembershipEvaluator
from boundaries.bnd_004_role_context import Bnd004Input, Bnd004RoleContextEvaluator
from boundaries.bnd_005_human_authority import Bnd005HumanAuthorityEvaluator, Bnd005Input
from boundaries.bnd_006_human_decision import Bnd006HumanDecisionEvaluator, Bnd006Input
from boundaries.bnd_007_state_transition import Bnd007Input, Bnd007StateTransitionEvaluator
from boundaries.bnd_014_commit import Bnd014CommitEvaluator
from boundaries.registry import BoundaryChainResult, BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult
from command.envelope import CommandEnvelope, CommandOutcome, compute_payload_fingerprint
from commit.coordinator import (
    CommitCoordinator,
    CommitRepository,
    CommitUnit,
    CurrentVersionReader,
    FailureInjectionPort,
    MutationOutcome,
    StaleVersionConflict,
)
from commit.idempotency import (
    IdempotencyAlreadyCommitted,
    IdempotencyDecision,
    IdempotencyPort,
    decide_idempotency_action,
)
from domain.decision import (
    Decision,
    DecisionOperation,
    DecisionState,
    challenge_target_ref,
    decision_target_ref,
    resolve_decision_transition_to_state,
)
from events.outbox import OutboxRepository
from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole
from persistence.challenge_repository import ChallengeRepository
from persistence.command_repository import CommandRepository
from persistence.decision_repository import DecisionConflict, DecisionRepository
from persistence.membership_repository import MembershipRepository
from persistence.workspace_repository import WorkspaceRepository
from semantic_types.ids import (
    AttemptId,
    ChallengeId,
    CommandId,
    CommitId,
    CorrelationId,
    DecisionId,
    EvidenceSetId,
    QuestionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion

_ACCEPTED_DECISION_ROLES = frozenset(
    {WorkspaceRole.OWNER, WorkspaceRole.FACILITATOR, WorkspaceRole.CONTRIBUTOR}
)
"""06 section 10's own named DENY example ("Observer/Viewer mutation"),
reused from `application.question_selection_handler`'s own precedent
(PKG-14) -- a rights-gated operation still excludes a pure-observer
role.
"""

_PRECOMMIT_CHAIN = (
    BoundaryId.BND_001,
    BoundaryId.BND_002,
    BoundaryId.BND_003,
    BoundaryId.BND_004,
    BoundaryId.BND_005,
    BoundaryId.BND_006,
    BoundaryId.BND_007,
)


@dataclass(frozen=True, slots=True)
class OpenDecisionConsiderationPayload:
    """The concrete Command payload for `OpenDecisionConsideration`."""

    challenge_id: str
    decision_question_text: str | None
    options: tuple[str, ...]
    criteria: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RecordHumanDecisionPayload:
    """The concrete Command payload for `RecordHumanDecision`."""

    decision_id: str
    selected_option: str
    rationale: str | None
    confidence: str | None


class HumanDecisionDenied(Exception):
    """The PRECOMMIT boundary chain (BND-001..007) did not reach ALLOW.
    No CommitUnit was ever created. Distinct from
    `commit.coordinator.CommitDenied`, which wraps a single BND-014
    `BoundaryProof`, not a whole chain result.
    """

    def __init__(self, chain_result: BoundaryChainResult) -> None:
        self.chain_result = chain_result
        super().__init__(
            f"HumanDecisionDenied: {chain_result.result.value} at "
            f"{chain_result.terminal_boundary_id}"
        )


class SelectedOptionNotCandidate(Exception):
    """Raised when `selected_option` is not among the Decision's own
    recorded `options` (only checked when `options` is non-empty --
    03/09 do not mandate a non-empty options list, so an empty list
    imposes no further constraint on `selected_option`'s content).
    """


def _raise_if_already_committed(
    idempotency_port: IdempotencyPort, envelope: CommandEnvelope
) -> None:
    """Short-circuits BEFORE the precommit boundary chain runs, but
    only for the one 14 section 27 disposition where that ordering
    genuinely matters: `RETURN_COMMITTED_RESULT`.

    Both `OpenDecisionConsideration` and `RecordHumanDecision` route
    through `boundaries.bnd_007_state_transition`'s own fresh,
    uncached state-topology check on every attempt -- by design, 14
    section 27's own "FAILED_PRECOMMIT -> ... full fresh boundaries"
    rule. But unlike PKG-14's QuestionSelection (whose own BND-007
    check depends only on Session/Question state, neither of which a
    successful QuestionSelection commit ever changes), this package's
    BND-007 check depends directly on the Decision's OWN state -- the
    exact fact a successful commit just changed. A genuine retry of an
    already-COMMITTED request would therefore see the Decision already
    advanced (UNDER_CONSIDERATION for a re-sent OPEN, or DECIDED for a
    re-sent RECORD) and be denied by BND-007 as an "illegal"/"already
    exists" transition -- a false negative, since 14 section 27's own
    rule for this case is unconditional: "same identity COMMITTED ->
    return prior committed result", no re-authorization implied. Every
    OTHER disposition (`PROCEED_NEW`, `RETURN_IN_PROGRESS_NO_EXECUTION`,
    `REJECT_PAYLOAD_COLLISION`, `PROCEED_FRESH_ATTEMPT_AFTER_FAILED_PRECOMMIT`,
    `BLOCK_INDETERMINATE_NO_BLIND_RETRY`) is safe to let flow through
    the normal fresh-boundaries-then-`idempotency_port.begin()`
    pipeline unchanged, because none of them corresponds to a state
    that has already, successfully changed -- `begin()` (called only
    after boundaries ALLOW, see this module's own top-level docstring)
    re-derives and acts on the identical decision itself.
    """
    if envelope.idempotency_key is None:
        return
    existing = idempotency_port.get(
        workspace_id=envelope.workspace_scope_ref,
        command_type=envelope.command_type,
        idempotency_key=envelope.idempotency_key,
    )
    decision = decide_idempotency_action(
        existing=existing,
        requested_command_id=envelope.command_id,
        requested_payload_fingerprint=compute_payload_fingerprint(envelope.payload),
    )
    if decision is IdempotencyDecision.RETURN_COMMITTED_RESULT:
        assert existing is not None  # only reachable when a record was found
        raise IdempotencyAlreadyCommitted(existing)


def _build_registry(
    *,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    authority_resolver: AuthorityResolver,
) -> BoundaryRegistry:
    # See `application.question_selection_handler._build_registry`'s
    # own comment: the pre-existing `BoundaryEvaluator` Protocol
    # variance limitation (PKG-08) applies identically here.
    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd002WorkspaceEvaluator(workspace_repository))  # type: ignore[arg-type]
    registry.register(Bnd003MembershipEvaluator(membership_repository))  # type: ignore[arg-type]
    registry.register(Bnd004RoleContextEvaluator(membership_repository))  # type: ignore[arg-type]
    registry.register(Bnd005HumanAuthorityEvaluator(authority_resolver))  # type: ignore[arg-type]
    registry.register(Bnd006HumanDecisionEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd007StateTransitionEvaluator())  # type: ignore[arg-type]
    return registry


class _CreateDecisionMutation:
    """Wraps the real `DecisionRepository.create` for
    `OpenDecisionConsideration`. Any exception (composite FK violation,
    primary-key collision) propagates through
    `CommitCoordinator._commit_inner`'s own generic rollback handling
    as `CommitFailedPrecommit`.
    """

    def __init__(self, repository: DecisionRepository, *, decision: Decision) -> None:
        self._repository = repository
        self._decision = decision

    def apply(self) -> MutationOutcome:
        self._repository.create(self._decision)
        relation_ref = decision_target_ref(self._decision.decision_id)
        return MutationOutcome(
            state_before_ref=None,
            state_after_ref=DecisionState.UNDER_CONSIDERATION.value,
            relation_refs=(relation_ref,),
        )


class _RecordDecisionMutation:
    """Wraps the real `DecisionRepository.record_decision` for
    `RecordHumanDecision`. `DecisionConflict` (a genuine 0-row-affected
    guarded UPDATE) is translated to `StaleVersionConflict`, the
    vocabulary `CommitCoordinator` itself understands -- mirrors
    `application.question_selection_handler`'s own
    `_CreateSelectionMutation` counterpart pattern, and PKG-13's own
    `_BurstStartMutation` before that.
    """

    def __init__(
        self,
        repository: DecisionRepository,
        *,
        decision_id: DecisionId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        decided_by_user_id: UserId,
        selected_option: str,
        rationale: str | None,
        confidence: str | None,
        decided_at: datetime,
    ) -> None:
        self._repository = repository
        self._decision_id = decision_id
        self._workspace_id = workspace_id
        self._expected_record_version = expected_record_version
        self._decided_by_user_id = decided_by_user_id
        self._selected_option = selected_option
        self._rationale = rationale
        self._confidence = confidence
        self._decided_at = decided_at

    def apply(self) -> MutationOutcome:
        try:
            self._repository.record_decision(
                decision_id=self._decision_id,
                workspace_id=self._workspace_id,
                expected_record_version=self._expected_record_version,
                decided_by_user_id=self._decided_by_user_id,
                selected_option=self._selected_option,
                rationale=self._rationale,
                confidence=self._confidence,
                decided_at=self._decided_at,
            )
        except DecisionConflict as exc:
            raise StaleVersionConflict(str(exc)) from exc
        return MutationOutcome(
            state_before_ref=DecisionState.UNDER_CONSIDERATION.value,
            state_after_ref=DecisionState.DECIDED.value,
        )


def open_decision_consideration(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    challenge_id: ChallengeId,
    decision_id: DecisionId,
    decision_question_ref: QuestionId | None,
    decision_question_text: str | None,
    options: tuple[str, ...],
    criteria: tuple[str, ...],
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    idempotency_key: str | None,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    challenge_repository: ChallengeRepository,
    decision_repository: DecisionRepository,
    authority_resolver: AuthorityResolver,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    idempotency_port: IdempotencyPort,
    current_version_reader: CurrentVersionReader,
    failure_injector: FailureInjectionPort | None = None,
) -> CommitUnit:
    """TRN-DEC-001: Decision absent -> UNDER_CONSIDERATION."""
    challenge = challenge_repository.get(challenge_id)
    existing_decision = decision_repository.get(decision_id)
    resolved_object_workspace_ids = (challenge.workspace_id,) if challenge is not None else ()

    context = BoundaryContext(
        workspace_id=workspace_id,
        operation=DecisionOperation.OPEN_DECISION_CONSIDERATION.value,
        actor=actor,
        correlation_id=correlation_id,
        evaluated_at=occurred_at,
    )

    boundary_inputs: dict[BoundaryId, object] = {
        BoundaryId.BND_001: Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=context,
            required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
        ),
        BoundaryId.BND_002: Bnd002Input(
            boundary_id=BoundaryId.BND_002,
            context=context,
            resolved_object_workspace_ids=resolved_object_workspace_ids,
        ),
        BoundaryId.BND_003: Bnd003Input(boundary_id=BoundaryId.BND_003, context=context),
    }
    membership = (
        membership_repository.get_current_membership(workspace_id, actor.user_id)
        if resolved_object_workspace_ids
        else None
    )
    if membership is not None:
        boundary_inputs[BoundaryId.BND_004] = Bnd004Input(
            boundary_id=BoundaryId.BND_004,
            context=context,
            membership_id=membership.id,
            accepted_roles=_ACCEPTED_DECISION_ROLES,
        )
        boundary_inputs[BoundaryId.BND_005] = Bnd005Input(
            boundary_id=BoundaryId.BND_005,
            context=context,
            required_authority_class=AuthorityClass.DECISION_RIGHT,
            scope_type="CHALLENGE",
            scope_id=challenge_id.value,
        )
        boundary_inputs[BoundaryId.BND_006] = Bnd006Input(
            boundary_id=BoundaryId.BND_006,
            context=context,
            decision_origin=actor.actor_class,
        )
    if challenge is not None:
        resolution = resolve_decision_transition_to_state(
            current_state=existing_decision.state if existing_decision is not None else None,
            target_state=DecisionState.UNDER_CONSIDERATION,
        )
        boundary_inputs[BoundaryId.BND_007] = Bnd007Input(
            boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
        )

    challenge_ref = challenge_target_ref(challenge_id)
    envelope = CommandEnvelope(
        command_id=command_id,
        command_type="CMD_OPEN_DECISION_CONSIDERATION",
        command_contract_version=ContractVersion("1.0"),
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        requested_at=occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=(challenge_ref,),
        expected_versions={
            challenge_ref: challenge.record_version
            if challenge is not None
            else RecordVersion.initial()
        },
        payload=OpenDecisionConsiderationPayload(
            challenge_id=str(challenge_id.value),
            decision_question_text=decision_question_text,
            options=options,
            criteria=criteria,
        ),
        idempotency_key=idempotency_key,
    )
    command_repository.record_attempt(envelope, received_at=occurred_at)
    _raise_if_already_committed(idempotency_port, envelope)

    registry = _build_registry(
        workspace_repository=workspace_repository,
        membership_repository=membership_repository,
        authority_resolver=authority_resolver,
    )
    chain_result = evaluate_chain(registry, _PRECOMMIT_CHAIN, boundary_inputs, context)  # type: ignore[arg-type]
    if chain_result.result is not BoundaryResult.ALLOW:
        command_repository.record_outcome(
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=occurred_at,
        )
        raise HumanDecisionDenied(chain_result)

    bnd005_proof = _find_proof(chain_result.proofs, BoundaryId.BND_005)
    binding_id = (
        bnd005_proof.authority_proof.binding_id
        if bnd005_proof is not None and bnd005_proof.authority_proof is not None
        else None
    )
    if binding_id is None:
        raise HumanDecisionDenied(chain_result)

    if idempotency_key is not None:
        idempotency_port.begin(envelope, seen_at=occurred_at)

    decision = Decision(
        decision_id=decision_id,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        decision_question_ref=decision_question_ref,
        decision_question_text=decision_question_text,
        options=options,
        criteria=criteria,
        selected_option=None,
        rationale=None,
        confidence=None,
        state=DecisionState.UNDER_CONSIDERATION,
        opened_by_user_id=actor.user_id,
        decision_authority_binding_id=binding_id,
        decided_by_user_id=None,
        created_at=occurred_at,
        decided_at=None,
        record_version=RecordVersion.initial(),
        provenance_ref=None,
    )

    coordinator = CommitCoordinator(
        connection,
        bnd014_evaluator=Bnd014CommitEvaluator(authority_resolver),
        command_repository=command_repository,
        audit_repository=audit_repository,
        outbox_repository=outbox_repository,
        commit_repository=commit_repository,
        idempotency_port=idempotency_port,
        failure_injector=failure_injector,
    )
    mutation = _CreateDecisionMutation(decision_repository, decision=decision)
    return coordinator.commit(
        envelope=envelope,
        actor=actor,
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        authority_scope_type="CHALLENGE",
        authority_scope_id=challenge_id.value,
        upstream_chain_result=chain_result.result,
        current_version_reader=current_version_reader,
        mutation=mutation,
        occurred_at=occurred_at,
        commit_id=commit_id,
    )


def record_human_decision(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    decision_id: DecisionId,
    selected_option: str,
    rationale: str | None,
    confidence: str | None,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    idempotency_key: str | None,
    evidence_set_ref: EvidenceSetId | None,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    decision_repository: DecisionRepository,
    authority_resolver: AuthorityResolver,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    idempotency_port: IdempotencyPort,
    current_version_reader: CurrentVersionReader,
    failure_injector: FailureInjectionPort | None = None,
) -> CommitUnit:
    """TRN-DEC-002: UNDER_CONSIDERATION -> DECIDED."""
    decision = decision_repository.get(decision_id)
    resolved_object_workspace_ids = (decision.workspace_id,) if decision is not None else ()

    context = BoundaryContext(
        workspace_id=workspace_id,
        operation=DecisionOperation.RECORD_HUMAN_DECISION.value,
        actor=actor,
        correlation_id=correlation_id,
        evaluated_at=occurred_at,
    )

    boundary_inputs: dict[BoundaryId, object] = {
        BoundaryId.BND_001: Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=context,
            required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
        ),
        BoundaryId.BND_002: Bnd002Input(
            boundary_id=BoundaryId.BND_002,
            context=context,
            resolved_object_workspace_ids=resolved_object_workspace_ids,
        ),
        BoundaryId.BND_003: Bnd003Input(boundary_id=BoundaryId.BND_003, context=context),
    }
    membership = (
        membership_repository.get_current_membership(workspace_id, actor.user_id)
        if resolved_object_workspace_ids
        else None
    )
    if membership is not None:
        boundary_inputs[BoundaryId.BND_004] = Bnd004Input(
            boundary_id=BoundaryId.BND_004,
            context=context,
            membership_id=membership.id,
            accepted_roles=_ACCEPTED_DECISION_ROLES,
        )
        boundary_inputs[BoundaryId.BND_005] = Bnd005Input(
            boundary_id=BoundaryId.BND_005,
            context=context,
            required_authority_class=AuthorityClass.DECISION_RIGHT,
            scope_type="DECISION",
            scope_id=decision_id.value,
        )
        boundary_inputs[BoundaryId.BND_006] = Bnd006Input(
            boundary_id=BoundaryId.BND_006,
            context=context,
            decision_origin=actor.actor_class,
        )
    if decision is not None:
        resolution = resolve_decision_transition_to_state(
            current_state=decision.state, target_state=DecisionState.DECIDED
        )
        boundary_inputs[BoundaryId.BND_007] = Bnd007Input(
            boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
        )

    decision_ref = decision_target_ref(decision_id)
    envelope = CommandEnvelope(
        command_id=command_id,
        command_type="CMD_RECORD_HUMAN_DECISION",
        command_contract_version=ContractVersion("1.0"),
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        requested_at=occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=(decision_ref,),
        expected_versions={
            decision_ref: decision.record_version
            if decision is not None
            else RecordVersion.initial()
        },
        payload=RecordHumanDecisionPayload(
            decision_id=str(decision_id.value),
            selected_option=selected_option,
            rationale=rationale,
            confidence=confidence,
        ),
        evidence_set_ref=evidence_set_ref,
        idempotency_key=idempotency_key,
    )
    command_repository.record_attempt(envelope, received_at=occurred_at)
    _raise_if_already_committed(idempotency_port, envelope)

    registry = _build_registry(
        workspace_repository=workspace_repository,
        membership_repository=membership_repository,
        authority_resolver=authority_resolver,
    )
    chain_result = evaluate_chain(registry, _PRECOMMIT_CHAIN, boundary_inputs, context)  # type: ignore[arg-type]
    if chain_result.result is not BoundaryResult.ALLOW:
        command_repository.record_outcome(
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=occurred_at,
        )
        raise HumanDecisionDenied(chain_result)

    assert decision is not None  # BND-007 only ALLOWs when a Decision was resolved above.

    # 04 section 50 DENY CONDITION: "Selected option not explicitly
    # human-adopted" -- the narrowest structural reading available
    # without inventing a sufficiency algorithm: when candidate options
    # were recorded at OPEN time, the human's selection must be one of
    # them.
    if decision.options and selected_option not in decision.options:
        raise SelectedOptionNotCandidate(
            f"selected_option {selected_option!r} is not among the Decision's own "
            f"options {decision.options!r}"
        )

    if idempotency_key is not None:
        idempotency_port.begin(envelope, seen_at=occurred_at)

    coordinator = CommitCoordinator(
        connection,
        bnd014_evaluator=Bnd014CommitEvaluator(authority_resolver),
        command_repository=command_repository,
        audit_repository=audit_repository,
        outbox_repository=outbox_repository,
        commit_repository=commit_repository,
        idempotency_port=idempotency_port,
        failure_injector=failure_injector,
    )
    mutation = _RecordDecisionMutation(
        decision_repository,
        decision_id=decision_id,
        workspace_id=workspace_id,
        expected_record_version=decision.record_version,
        decided_by_user_id=actor.user_id,
        selected_option=selected_option,
        rationale=rationale,
        confidence=confidence,
        decided_at=occurred_at,
    )
    return coordinator.commit(
        envelope=envelope,
        actor=actor,
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        authority_scope_type="DECISION",
        authority_scope_id=decision_id.value,
        upstream_chain_result=chain_result.result,
        current_version_reader=current_version_reader,
        mutation=mutation,
        occurred_at=occurred_at,
        commit_id=commit_id,
    )


def _find_proof(proofs: tuple[BoundaryProof, ...], boundary_id: BoundaryId) -> BoundaryProof | None:
    for proof in proofs:
        if proof.boundary_id is boundary_id:
            return proof
    return None


__all__ = [
    "OpenDecisionConsiderationPayload",
    "RecordHumanDecisionPayload",
    "HumanDecisionDenied",
    "SelectedOptionNotCandidate",
    "open_decision_consideration",
    "record_human_decision",
]
