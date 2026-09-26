"""SelectQuestion: the first fully governed, end-to-end production
Command path in this codebase.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 12 (COMMAND REGISTRY:
`SelectQuestion` row -- "QUESTION_SELECTION_RIGHT | human selection act
| 001-007,014,015 | QuestionSelection relation"), section 14 (COMMAND
PROCESSOR -- the exact pipeline this function materializes literally:
RECEIVE COMMAND -> ... -> RUN PRECOMMIT BOUNDARIES -> VALIDATE EXPECTED
VERSIONS -> BUILD MUTATION PLAN -> ENTER COMMIT COORDINATOR -> BND-014
FRESH RELOAD -> ... -> COMMIT); 09_DATA_EVENT_API_CONTRACTS.md section
62 (`CMD_SELECT_COMPELLING_QUESTION`/`CMD_SELECT_PRIMARY_QUESTION`, TRN
refs); 03_STATE_AND_TRANSITION_ARCHITECTURE.md section 39 (TRN-SEL-001/
002); 04_AUTHORITY_AND_DECISION_RIGHTS.md section 41-42 (AUTH-DEP-SEL-001/
002 -- AUTHORITY SCOPE: "Specific Session").

WHY THIS IS THE FIRST PACKAGE TO WIRE `boundaries.evaluate_chain` AND
`commit.coordinator.CommitCoordinator` INTO A REAL PRODUCTION CALLER
------------------------------------------------------------------------
Every BND-001..008/014 evaluator (PKG-09/PKG-13) and `CommitCoordinator`
itself (PKG-13) have existed since their own packages landed, but no
earlier package built a concrete Command with a real handler to invoke
them (14 assigns no concrete Command to PKG-08/09/10/11/12/13 --
"generic engine now, concrete instances later" was each of those
packages' own explicit scope boundary). 14's own COMMAND REGISTRY names
`SelectQuestion` as the first row with a genuinely concrete
`Primary boundaries` list AND an assigned canonical effect this build
phase can materialize (Phase 5, all of Phase 4's machinery already
verified) -- this module is exactly that materialization, not an
invented shortcut past the packages that built the pieces it composes.

WHY `QUESTION_SELECTION_RIGHT` IS CHECKED AT `scope_type="SESSION"`
(UNLIKE `SESSION_CONTROL_RIGHT`'S OWN `"WORKSPACE"` WORKAROUND)
------------------------------------------------------------------------
04 section 41/42 (AUTH-DEP-SEL-001/002) both state, unhedged: "AUTHORITY
SCOPE: Specific Session." This differs from `SESSION_CONTROL_RIGHT`'s
own 04 section 35-39 wording (also nominally "Specific Session"), which
`domain.burst_transitions`'s own module docstring reads as
WORKSPACE-scoped in this prototype specifically because 12 section 8.1's
bootstrap sequence grants that right *before* any Session exists --
12 section 7's own Authority Profile table adds an explicit hedge for
that one row ("... where upstream assigns it"). `QUESTION_SELECTION_RIGHT`'s
own 12 section 7 row carries no such hedge, and by the time
`select_question` ever runs a Session genuinely already exists (Session
creation is itself an earlier step in 12 section 28's own happy path,
step 3, versus QuestionSelection's step 19) -- there is no bootstrap-
ordering tension here forcing a workaround. This module therefore reads
04's scope statement literally: `scope_type="SESSION"`,
`scope_id=session_id.value`.

WHY "QUESTION BELONGS TO SESSION'S CHALLENGE" IS A BND-007 CONCERN,
NOT A SEPARATE PRECONDITION
------------------------------------------------------------------------
06 section 13's own VALIDATION list for BND-007 includes "cross-object
state invariant valid" -- exactly the cross-object fact 04 section 41's
own AUTHORITY PRECONDITIONS name ("Question belongs to Session
Challenge"). `domain.question_selection.resolve_selection_transition`
checks it directly, alongside the Session-state precondition, rather
than this handler inventing a second, ad hoc gate outside the boundary
chain. The Workspace half of the same DENY condition ("Question belongs
to another Workspace") is BND-002's own job -- not duplicated here.

WHY A MISSING SESSION/QUESTION PRODUCES `resolved_object_workspace_ids
= ()`, NOT A SEPARATE "NOT FOUND" ERROR PATH
------------------------------------------------------------------------
`boundaries.bnd_002_workspace.Bnd002WorkspaceEvaluator` already DENYs
with `UNRESOLVED_WORKSPACE_NO_OBJECTS` when given an empty tuple (06
section 8's own EVIDENCE REQUIREMENT: "SYSTEM_PROOF of object-to-Workspace
resolution" -- a claim about an object that does not exist cannot be
proven). Reusing that existing, already-tested evaluator for "Session or
Question does not exist" is the honest generalization of what it
already checks, not a new boundary invented for this package.

WHY `IdempotencyPort.begin()` IS CALLED ONLY AFTER THE PRECOMMIT
BOUNDARY CHAIN ALLOWS, NEVER BEFORE
------------------------------------------------------------------------
`commit.idempotency.IdempotencyOutcome` has no `DENIED` member (PKG-11's
own design: "an idempotency record only ever exists once execution has
genuinely begun"). 14 section 27's own rule 1 ("new request -> create
command/attempt") is grouped with the OTHER dispatch-time facts, but
06 section 4's own canonical request path places BND-001..007 *before*
BND-014/commit coordination, and idempotency is not itself one of the
18 named boundaries. A request denied by BND-001..007 must therefore
never create an `IdempotencyRecord` at all -- `record_attempt` (which
has no such vocabulary gap, since `CommandOutcome.DENIED` exists) runs
first and unconditionally; `idempotency_port.begin()` runs only on the
boundary chain's own ALLOW path, immediately before entering
`CommitCoordinator`, mirroring PKG-13's own test helper's placement
(`_begin_idempotency_if_needed`, called right before `_build_coordinator`).
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
from command.envelope import CommandEnvelope, CommandOutcome
from commit.coordinator import (
    CommitCoordinator,
    CommitRepository,
    CommitUnit,
    CurrentVersionReader,
    FailureInjectionPort,
    MutationOutcome,
)
from commit.idempotency import IdempotencyPort
from domain.question_selection import (
    QuestionSelection,
    SelectionOperation,
    SelectionTransitionId,
    SelectionType,
    resolve_selection_transition,
    session_target_ref,
)
from events.contracts import EventFacts
from events.outbox import OutboxRepository
from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole
from persistence.command_repository import CommandRepository
from persistence.membership_repository import MembershipRepository
from persistence.question_repository import QuestionRepository
from persistence.question_selection_repository import QuestionSelectionRepository
from persistence.session_repository import SessionRepository
from persistence.workspace_repository import WorkspaceRepository
from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    QuestionId,
    QuestionSelectionId,
    SessionId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion

_ACCEPTED_SELECTOR_ROLES = frozenset(
    {WorkspaceRole.OWNER, WorkspaceRole.FACILITATOR, WorkspaceRole.CONTRIBUTOR}
)
"""06 section 10's own named DENY example ("Observer/Viewer mutation") --
QuestionSelection is a mutation, so a pure-observer role is excluded
even though the operation is otherwise rights-gated, not role-gated."""

_PRECOMMIT_CHAIN = (
    BoundaryId.BND_001,
    BoundaryId.BND_002,
    BoundaryId.BND_003,
    BoundaryId.BND_004,
    BoundaryId.BND_005,
    BoundaryId.BND_006,
    BoundaryId.BND_007,
)

_TRANSITION_FOR_TYPE = {
    SelectionType.COMPELLING: SelectionTransitionId.TRN_SEL_001,
    SelectionType.PRIMARY: SelectionTransitionId.TRN_SEL_002,
}

_COMMAND_TYPE_FOR_TRANSITION = {
    SelectionTransitionId.TRN_SEL_001: "CMD_SELECT_COMPELLING_QUESTION",
    SelectionTransitionId.TRN_SEL_002: "CMD_SELECT_PRIMARY_QUESTION",
}


@dataclass(frozen=True, slots=True)
class SelectQuestionPayload:
    """The one concrete Command payload this package introduces (14
    PKG-10's own `CommandEnvelope.payload: object` -- "raw dictionaries
    are rejected", no concrete contract assigned to that package).
    """

    session_id: str
    question_id: str
    selection_type: str


class SelectQuestionDenied(Exception):
    """The PRECOMMIT boundary chain (BND-001..007) did not reach ALLOW.
    No CommitUnit was ever created; `command_repository.record_outcome`
    already recorded `CommandOutcome.DENIED` before this is raised.
    Distinct from `commit.coordinator.CommitDenied`, which wraps a
    single BND-014 `BoundaryProof`, not a whole chain result.
    """

    def __init__(self, chain_result: BoundaryChainResult) -> None:
        self.chain_result = chain_result
        super().__init__(
            f"SelectQuestionDenied: {chain_result.result.value} at "
            f"{chain_result.terminal_boundary_id}"
        )


def _build_registry(
    *,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    authority_resolver: AuthorityResolver,
) -> BoundaryRegistry:
    # `BoundaryEvaluator.evaluate`'s own `boundary_input: BoundaryInput` is
    # necessarily narrowed by every concrete evaluator to its own
    # `BndNNNInput` type (06 gives each boundary a different INPUT list --
    # `boundaries.types`'s own module docstring). mypy's Protocol variance
    # check flags this as unsound in the general case; `evaluate_chain`'s
    # own contract (only ever calling an evaluator with the exact
    # `BndNNNInput` the caller placed at that `BoundaryId` in
    # `boundary_inputs`) is what makes it safe in practice. The existing
    # test suite already carries the identical, disclosed `type: ignore`
    # for this (see `tests/command_commit_event/test_commit.py`'s own
    # `_build_coordinator` helper) -- this is the first production module
    # to hit it, not a new problem.
    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd002WorkspaceEvaluator(workspace_repository))  # type: ignore[arg-type]
    registry.register(Bnd003MembershipEvaluator(membership_repository))  # type: ignore[arg-type]
    registry.register(Bnd004RoleContextEvaluator(membership_repository))  # type: ignore[arg-type]
    registry.register(Bnd005HumanAuthorityEvaluator(authority_resolver))  # type: ignore[arg-type]
    registry.register(Bnd006HumanDecisionEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd007StateTransitionEvaluator())  # type: ignore[arg-type]
    return registry


def _find_proof(proofs: tuple[BoundaryProof, ...], boundary_id: BoundaryId) -> BoundaryProof | None:
    for proof in proofs:
        if proof.boundary_id is boundary_id:
            return proof
    return None


class _CreateSelectionMutation:
    """Wraps the real `QuestionSelectionRepository.create` (this
    package). Any exception it raises (composite FK violation, the
    literal-duplicate UNIQUE constraint, the partial-unique "one
    PRIMARY" index, or the compelling-cardinality trigger) propagates
    through `CommitCoordinator._commit_inner`'s own generic rollback
    handling as `CommitFailedPrecommit` -- see
    `persistence.question_selection_repository`'s own module docstring
    for why no translation layer is added here.
    """

    def __init__(
        self, repository: QuestionSelectionRepository, *, selection: QuestionSelection
    ) -> None:
        self._repository = repository
        self._selection = selection

    def apply(self) -> MutationOutcome:
        self._repository.create(self._selection)
        relation_ref = f"question_selection:{self._selection.question_selection_id.value}"
        return MutationOutcome(
            state_before_ref=None,
            state_after_ref=self._selection.selection_type.value,
            relation_refs=(relation_ref,),
            event=EventFacts(
                aggregate_ref=relation_ref,
                payload={
                    "question_selection_id": str(self._selection.question_selection_id.value),
                    "session_id": str(self._selection.session_id.value),
                    "question_id": str(self._selection.question_id.value),
                    "selection_type": self._selection.selection_type.value,
                },
            ),
        )


def select_question(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    question_id: QuestionId,
    selection_type: SelectionType,
    question_selection_id: QuestionSelectionId,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    idempotency_key: str | None,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    session_repository: SessionRepository,
    question_repository: QuestionRepository,
    question_selection_repository: QuestionSelectionRepository,
    authority_resolver: AuthorityResolver,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    idempotency_port: IdempotencyPort,
    current_version_reader: CurrentVersionReader,
    failure_injector: FailureInjectionPort | None = None,
) -> CommitUnit:
    """Materializes 14 section 14's COMMAND PROCESSOR pipeline for
    `SelectQuestion` end to end. Raises `SelectQuestionDenied` if the
    precommit boundary chain (BND-001..007) does not reach ALLOW;
    otherwise delegates to `CommitCoordinator.commit`, whose own
    `CommitDenied`/`CommitFailedPrecommit`/`CommitIndeterminate`
    propagate unmodified.
    """
    transition_id = _TRANSITION_FOR_TYPE[selection_type]
    operation = SelectionOperation.SELECT_COMPELLING_QUESTION
    if transition_id is SelectionTransitionId.TRN_SEL_002:
        operation = SelectionOperation.SELECT_PRIMARY_QUESTION

    session = session_repository.get(session_id)
    question = question_repository.get(question_id)
    resolved_object_workspace_ids = (
        (session.workspace_id, question.workspace_id)
        if session is not None and question is not None
        else ()
    )

    context = BoundaryContext(
        workspace_id=workspace_id,
        operation=operation.value,
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
            accepted_roles=_ACCEPTED_SELECTOR_ROLES,
        )
        boundary_inputs[BoundaryId.BND_005] = Bnd005Input(
            boundary_id=BoundaryId.BND_005,
            context=context,
            required_authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT,
            scope_type="SESSION",
            scope_id=session_id.value,
        )
        boundary_inputs[BoundaryId.BND_006] = Bnd006Input(
            boundary_id=BoundaryId.BND_006,
            context=context,
            decision_origin=actor.actor_class,
        )
    if session is not None and question is not None:
        resolution = resolve_selection_transition(
            transition_id=transition_id,
            current_session_state=session.state,
            session_challenge_id=session.challenge_id,
            question_challenge_id=question.challenge_id,
        )
        boundary_inputs[BoundaryId.BND_007] = Bnd007Input(
            boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
        )

    envelope = _build_envelope(
        command_id=command_id,
        command_type=_COMMAND_TYPE_FOR_TRANSITION[transition_id],
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        occurred_at=occurred_at,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        session_record_version=session.record_version if session is not None else None,
        selection_type=selection_type,
        question_id=question_id,
        idempotency_key=idempotency_key,
    )
    command_repository.record_attempt(envelope, received_at=occurred_at)

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
        raise SelectQuestionDenied(chain_result)

    assert session is not None  # BND-007 only ALLOWs when both were resolved above.

    bnd005_proof = _find_proof(chain_result.proofs, BoundaryId.BND_005)
    human_authority_binding_id = (
        bnd005_proof.authority_proof.binding_id
        if bnd005_proof is not None and bnd005_proof.authority_proof is not None
        else None
    )
    if human_authority_binding_id is None:
        # Defensive: BND-005 ALLOWed, so a granting binding was proven
        # to exist -- this branch is unreachable in practice, kept as a
        # fail-closed guard rather than constructing a QuestionSelection
        # with a fabricated binding reference.
        raise SelectQuestionDenied(chain_result)

    if idempotency_key is not None:
        idempotency_port.begin(envelope, seen_at=occurred_at)

    selection = QuestionSelection(
        question_selection_id=question_selection_id,
        workspace_id=workspace_id,
        session_id=session_id,
        question_id=question_id,
        selection_type=selection_type,
        selected_by_user_id=actor.user_id,
        human_authority_binding_id=human_authority_binding_id,
        selected_at=occurred_at,
        record_version=RecordVersion.initial(),
    )

    bnd014_evaluator = Bnd014CommitEvaluator(authority_resolver)
    coordinator = CommitCoordinator(
        connection,
        bnd014_evaluator=bnd014_evaluator,
        command_repository=command_repository,
        audit_repository=audit_repository,
        outbox_repository=outbox_repository,
        commit_repository=commit_repository,
        idempotency_port=idempotency_port,
        failure_injector=failure_injector,
    )
    mutation = _CreateSelectionMutation(question_selection_repository, selection=selection)
    return coordinator.commit(
        envelope=envelope,
        actor=actor,
        required_authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT,
        authority_scope_type="SESSION",
        authority_scope_id=session_id.value,
        upstream_chain_result=chain_result.result,
        current_version_reader=current_version_reader,
        mutation=mutation,
        occurred_at=occurred_at,
        commit_id=commit_id,
    )


def _build_envelope(
    *,
    command_id: CommandId,
    command_type: str,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    session_record_version: RecordVersion | None,
    selection_type: SelectionType,
    question_id: QuestionId,
    idempotency_key: str | None,
) -> CommandEnvelope:
    session_ref = session_target_ref(session_id)
    # When the Session was not found, there is no real version to name
    # as "expected" -- `RecordVersion.initial()` is used only so the
    # envelope itself remains well-formed; BND-002 has already denied
    # (empty `resolved_object_workspace_ids`) by the time this envelope
    # is ever passed to CommitCoordinator, so this value is never
    # actually compared against a live row in that case.
    expected_version = (
        session_record_version if session_record_version is not None else RecordVersion.initial()
    )
    return CommandEnvelope(
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
        expected_versions={session_ref: expected_version},
        payload=SelectQuestionPayload(
            session_id=str(session_id.value),
            question_id=str(question_id.value),
            selection_type=selection_type.value,
        ),
        idempotency_key=idempotency_key,
    )


__all__ = [
    "SelectQuestionPayload",
    "SelectQuestionDenied",
    "select_question",
]
