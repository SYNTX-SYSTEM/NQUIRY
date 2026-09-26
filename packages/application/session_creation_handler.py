"""CreateSession: TRN-SESS-001 ("Session absent -> DRAFT") -- the
"create" half of F02 WU-02.3, "Session create/read". The "read" half,
`GetSession`, already exists (`application.session_view_query`,
Architecture 17, already committed to master) -- this Work Unit's own
new scope is exactly the write side.

Source: `docs/architecture/04_AUTHORITY_AND_DECISION_RIGHTS.md`
AUTH-DEP-SESS-001 ("Create Session"): "OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT. AUTHORITY SCOPE: Target Challenge within one
Workspace. AUTHORITY PRECONDITIONS: Valid HumanAuthorityBinding for
SESSION_CONTROL_RIGHT. Challenge exists. Workspace scope valid."
`docs/architecture/03_STATE_AND_TRANSITION_ARCHITECTURE.md` §15's own
TRN-SESS-001 contract (transcribed in `domain.session_transitions`):
`from_state=None`, `to_state=DRAFT`.

WHY THIS COMMAND USES `commit.coordinator.CommitCoordinator`, UNLIKE
`CreateChallenge`
--------------------------------------------------------------------
`CreateChallenge` (F02 WU-02.1) hand-rolls its own atomic write because
AUTH-DEP-CH-001 names no `HumanAuthorityBinding` at all -- there is
structurally no `AuthorityClass` to hand `CommitCoordinator`.
`CreateSession` is the opposite case: AUTH-DEP-SESS-001 names a real,
checkable authority (`SESSION_CONTROL_RIGHT`, scope
`CHALLENGE:challenge_id`), so `CommitCoordinator` is both usable and
required, exactly mirroring `application.human_decision_handler.open_decision_consideration`'s
own shape for the structurally identical case (a new child object,
gated by a real `HumanAuthorityBinding` scoped to its parent
Challenge) -- this module follows that precedent directly rather than
`CreateChallenge`'s.

WHY THIS COMMAND'S OWN PRECOMMIT CHAIN OMITS BND-007 (STATE TRANSITION)
--------------------------------------------------------------------
Session, unlike Challenge, has a real state vocabulary and a real
topology evaluator (`domain.session_transitions.resolve_session_transition_to_state`)
-- so omitting BND-007 here is not "Session has no state" (WU-02.1's
own reasoning for `CreateChallenge`) but a distinct, textually-grounded
one: TRN-SESS-001's own `TransitionSpec.required_boundary_dependencies`
in `domain.session_transitions` is exactly `(IDENTITY, WORKSPACE,
AUTHORITY, AUDIT)` -- 03 §15's own verbatim per-transition list,
DELIBERATELY omitting `STATE_TRANSITION` (TRN-SESS-002, "Begin Setup",
the very next transition, explicitly INCLUDES it). This is 03's own
textual signal, read literally rather than defaulted to
`open_decision_consideration`'s own chain shape (which DOES include
BND-007 for `OpenDecisionConsideration`, because `domain.decision`
exposes no equivalent explicit per-transition dependency list to read
this distinction from in the first place). A brand-new Session's own
`state` is hardcoded to `INITIAL_SESSION_STATE` by this Command itself
(never caller-supplied), so there is no illegitimate-target-state risk
BND-007 would catch here that this Command's own hardcoding does not
already prevent by construction -- the identical reasoning
`domain.session.INITIAL_SESSION_STATE`'s own docstring already gives
("a caller-supplied target state cannot be smuggled in at creation
time").

WHY THIS COMMAND DOES NOT NEED `human_decision_handler`'s OWN
"RAISE IF ALREADY COMMITTED BEFORE BOUNDARIES" SPECIAL CASE
--------------------------------------------------------------------
`human_decision_handler._raise_if_already_committed`'s own docstring
explains its ONE reason for existing: `OpenDecisionConsideration`'s
BND-007 check depends on the SAME Decision's own state, so a retried,
already-COMMITTED request would see that state already advanced and be
wrongly DENIED by the normal chain. `CreateSession` runs no BND-007 at
all (see above), so this failure mode cannot occur here -- the normal
`idempotency_port.begin()` placement (after boundaries ALLOW, mirroring
`AddMember`/`GrantHumanAuthorityBinding`'s own placement) is sufficient.

WHY `Session` CARRIES NO `authority_binding_id` FIELD, UNLIKE `Decision`
--------------------------------------------------------------------
`domain.decision.Decision.decision_authority_binding_id` exists because
09's own Decision data contract names it. 09 §27's own Session data
contract names no equivalent field -- `domain.session.Session`'s own
field list (verified directly, not assumed) has none either. This
Command therefore does not extract `BoundaryProof.authority_proof.binding_id`
the way `open_decision_consideration` does for `Decision` -- there is
nowhere on `Session` to put it. AUTH-DEP-SESS-001's own "AUDIT
REQUIREMENT: Record controller binding and scope" is still satisfied:
`CommitCoordinator._commit_inner`'s own unconditional
`AuditEvent.authority_source_ref` fallback (real binding id when one
exists) already records it on the durable audit trail, the identical
mechanism every other `CommitCoordinator`-based Command in this
codebase already relies on for the same requirement.
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
from boundaries.bnd_014_commit import Bnd014CommitEvaluator
from boundaries.registry import BoundaryChainResult, BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
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
from domain.decision import challenge_target_ref
from domain.question_selection import session_target_ref
from domain.session import INITIAL_SESSION_STATE, Session
from events.contracts import EventFacts
from events.outbox import OutboxRepository
from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole
from persistence.challenge_repository import ChallengeRepository
from persistence.command_repository import CommandRepository
from persistence.membership_repository import MembershipRepository
from persistence.session_repository import SessionRepository
from persistence.workspace_repository import WorkspaceRepository
from semantic_types.ids import (
    AttemptId,
    ChallengeId,
    CommandId,
    CommitId,
    CorrelationId,
    SessionId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, MethodVersion, RecordVersion

_PRECOMMIT_CHAIN = (
    BoundaryId.BND_001,
    BoundaryId.BND_002,
    BoundaryId.BND_003,
    BoundaryId.BND_004,
    BoundaryId.BND_005,
)

_ACCEPTED_SESSION_CONTROLLER_ROLES = frozenset(
    {WorkspaceRole.OWNER, WorkspaceRole.FACILITATOR, WorkspaceRole.CONTRIBUTOR}
)
"""Mirrors `human_decision_handler._ACCEPTED_DECISION_ROLES` exactly:
06 §10's own named DENY example is "Observer/Viewer mutation", and
`governance.membership.WorkspaceRole` currently has no such role at
all (OWNER/FACILITATOR/CONTRIBUTOR only) -- this accepts every role
the closed vocabulary presently defines. BND-004 here is deliberately
NOT the substantive gate (that is BND-005's job, the real
`SESSION_CONTROL_RIGHT` binding check) -- it is the same forward-looking
"not a read-only role" floor `human_decision_handler` already
established for the identical authority-binding-gated shape."""


class CreateSessionDenied(Exception):
    """The PRECOMMIT boundary chain (BND-001..005) did not reach
    ALLOW. No Session row was ever written;
    `command_repository.record_outcome` already recorded
    `CommandOutcome.DENIED` before this is raised."""

    def __init__(self, chain_result: BoundaryChainResult) -> None:
        self.chain_result = chain_result
        super().__init__(chain_result.result.value)


@dataclass(frozen=True, slots=True)
class CreateSessionPayload:
    """The one concrete Command payload this Command introduces (09
    §9), mirroring `human_decision_handler.OpenDecisionConsiderationPayload`'s
    own precedent."""

    challenge_id: str
    applied_method_key: str
    applied_method_version: str


class _CreateSessionMutation:
    """Wraps the real `SessionRepository.create` for `CreateSession`.
    Mirrors `human_decision_handler._CreateDecisionMutation`'s own
    shape exactly -- the Session value is already fully constructed by
    the time this runs."""

    def __init__(self, repository: SessionRepository, *, session: Session) -> None:
        self._repository = repository
        self._session = session

    def apply(self) -> MutationOutcome:
        self._repository.create(self._session)
        return MutationOutcome(
            state_before_ref=None,
            # F02 WU-02.9: same `session:<STATE>` form every Session
            # transition records, so the committed event that established
            # the current state is exactly findable.
            state_after_ref=f"session:{self._session.state.value}",
            relation_refs=(session_target_ref(self._session.session_id),),
            event_type="SESSION_CREATED",
            result_ref=str(self._session.session_id.value),
            event=EventFacts(
                aggregate_ref=session_target_ref(self._session.session_id),
                payload={
                    "session_id": str(self._session.session_id.value),
                    "challenge_id": str(self._session.challenge_id.value),
                    "state": self._session.state.value,
                    "applied_method_key": self._session.applied_method_key,
                    "applied_method_version": str(self._session.applied_method_version.value),
                },
            ),
        )


def _build_registry(
    *,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    authority_resolver: AuthorityResolver,
) -> BoundaryRegistry:
    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd002WorkspaceEvaluator(workspace_repository))  # type: ignore[arg-type]
    registry.register(Bnd003MembershipEvaluator(membership_repository))  # type: ignore[arg-type]
    registry.register(Bnd004RoleContextEvaluator(membership_repository))  # type: ignore[arg-type]
    registry.register(Bnd005HumanAuthorityEvaluator(authority_resolver))  # type: ignore[arg-type]
    return registry


def create_session(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    challenge_id: ChallengeId,
    session_id: SessionId,
    applied_method_key: str,
    applied_method_version: MethodVersion,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    idempotency_key: str | None,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    challenge_repository: ChallengeRepository,
    session_repository: SessionRepository,
    authority_resolver: AuthorityResolver,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    idempotency_port: IdempotencyPort,
    current_version_reader: CurrentVersionReader,
    failure_injector: FailureInjectionPort | None = None,
) -> CommitUnit:
    """TRN-SESS-001: Session absent -> DRAFT, under `challenge_id`.
    `actor` must currently hold a real, effective `SESSION_CONTROL_RIGHT`
    `HumanAuthorityBinding` scoped to `challenge_id` (proven fresh by
    BND-005, AUTH-DEP-SESS-001). Raises `CreateSessionDenied` if the
    precommit chain does not reach ALLOW.
    """
    challenge = challenge_repository.get(challenge_id)
    resolved_object_workspace_ids = (challenge.workspace_id,) if challenge is not None else ()

    context = BoundaryContext(
        workspace_id=workspace_id,
        operation="CMD_CREATE_SESSION",
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
            accepted_roles=_ACCEPTED_SESSION_CONTROLLER_ROLES,
        )
        boundary_inputs[BoundaryId.BND_005] = Bnd005Input(
            boundary_id=BoundaryId.BND_005,
            context=context,
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            scope_type="CHALLENGE",
            scope_id=challenge_id.value,
        )

    challenge_ref = challenge_target_ref(challenge_id)
    envelope = CommandEnvelope(
        command_id=command_id,
        command_type="CMD_CREATE_SESSION",
        command_contract_version=ContractVersion("1.0"),
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        requested_at=occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=(challenge_ref,),
        created_refs=(session_target_ref(session_id),),
        expected_versions={
            challenge_ref: challenge.record_version
            if challenge is not None
            else RecordVersion.initial()
        },
        payload=CreateSessionPayload(
            challenge_id=str(challenge_id.value),
            applied_method_key=applied_method_key,
            applied_method_version=applied_method_version.value,
        ),
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
        raise CreateSessionDenied(chain_result)

    if idempotency_key is not None:
        idempotency_port.begin(envelope, seen_at=occurred_at)

    session = Session(
        session_id=session_id,
        challenge_id=challenge_id,
        workspace_id=workspace_id,
        applied_method_key=applied_method_key,
        applied_method_version=applied_method_version,
        state=INITIAL_SESSION_STATE,
        created_at=occurred_at,
        updated_at=occurred_at,
        closed_at=None,
        record_version=RecordVersion.initial(),
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
    mutation = _CreateSessionMutation(session_repository, session=session)
    return coordinator.commit(
        envelope=envelope,
        actor=actor,
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        authority_scope_type="CHALLENGE",
        authority_scope_id=challenge_id.value,
        upstream_chain_result=chain_result.result,
        current_version_reader=current_version_reader,
        mutation=mutation,
        occurred_at=occurred_at,
        commit_id=commit_id,
    )


__all__ = [
    "CreateSessionDenied",
    "CreateSessionPayload",
    "create_session",
]
