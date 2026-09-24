"""CreateChallenge: the real, governed "Facilitator creates a
Challenge" Command (F02 WU-02.1).

Source: `docs/architecture/04_AUTHORITY_AND_DECISION_RIGHTS.md`
AUTH-DEP-CH-001 ("Create Challenge"): "ROLE: Facilitator. ...
AUTHORITY PRECONDITIONS: Authenticated identity. Active Workspace
membership. Facilitator role valid in target Workspace." No
`HumanAuthorityBinding` is named anywhere in that spec — §84's own
closure text confirms this is deliberate, not an oversight: "Challenge
creation: CLOSED. Facilitator has source authority." `docs/domain/
challenge.py`'s own module docstring explains why there is no
BND-007-style transition evaluator either: Challenge has no `status`
field at all (GAP-02-012/GAP-03-013, deliberately not materialized) —
creation is "existential ABSENT -> PRESENT" (03 §12.3, TRN-CH-001), not
a transition among named states.

HUMAN-CONFIRMED, 2026-09-22: a Workspace's own founder (always `Owner`,
never simultaneously `Facilitator` — the schema enforces exactly one
role per person per Workspace) CANNOT create a Challenge in their own
Workspace unless a SECOND, real member is separately granted the
Facilitator role via `AddMember` (F01 WU-01.5). Presented to the human
operator as a real architectural question before this file was
written; decision: implement AUTH-DEP-CH-001 exactly as specified — a
deliberate separation of governance (Owner) from operational
facilitation (Facilitator), not a bug, not silently patched with an
invented Owner exception ("No implicit Owner/Facilitator substitution"
is repeated verbatim across 04/05).

F02 WU-02.6 (HD-6): ROLE-SOURCED AUTHORITY THROUGH THE SINGLE EFFECT GATE
--------------------------------------------------------------------
AUTH-DEP-CH-001 names a ROLE right (Facilitator), not an `AuthorityClass`.
Until WU-02.6 that meant `CommitCoordinator` could not express it, and this
Command hand-rolled its own SAVEPOINT and audit row. The audit row's
`authority_source_ref` was a fresh `uuid.uuid4()` that pointed at nothing.
The operator's HD-6 decision (16 §41 REC-004) closed both: the Command now
commits through `CommitCoordinator` with a typed
`boundaries.authority_source.RoleAuthority`. At commit time BND-014
re-reads the actor's CURRENT ACTIVE membership and CURRENT role
(`ROLE_NOT_ACCEPTED`/`ROLE_NO_ACTIVE_MEMBERSHIP` deny) and records the real
`role_assignments.id` as provenance. The new Challenge is recorded as a
created ref.

WHY THE OPTIMISTIC-CONCURRENCY TARGET IS THE WORKSPACE, NOT THE NEW
CHALLENGE
--------------------------------------------------------------------
F02 WU-02.0's own module docstring already disclosed the real defect
this exact mistake produced there (`GrantHumanAuthorityBinding`'s
first draft versioned against its own brand-new row and got a genuine
`STALE_VERSION` denial on every real attempt). This Command applies
that lesson from the start: a NEW child row under an ALREADY-EXISTING
Workspace is versioned against the Workspace itself
(`persistence.workspace_repository.workspace_target_ref`) — the
general pattern this codebase has now established repeatedly: version
a creation against the parent, never against the row being created.
Unlike a `CommitCoordinator`-based Command, this Command reads the
CURRENT Workspace version itself (immediately before the SAVEPOINT,
the same "freshness immediately before commit" BND-014 itself would
otherwise provide) and compares it explicitly — the identical
STALE_VERSION protection, hand-rolled for the identical reason the
rest of this Command is hand-rolled.

IDEMPOTENT RETRY RETURNS THE EXISTING CHALLENGE
--------------------------------------------------------------------
`idempotency_port.begin()` runs after the precommit chain ALLOWs. On
`IdempotencyAlreadyCommitted` this Command loads the Challenge named by
the record's `result_ref` and returns the same `CreateChallengeResult`
a fresh call would. `result_ref` holds the Challenge id because the
mutation sets `MutationOutcome.result_ref` (F02 WU-02.6), and
`CommitCoordinator` stores that value instead of the commit id. Every
other `IdempotencyLifecycleError` propagates to the caller (14 §27).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from audit.models import AuditRepository
from authority.actor import ActorClass, ActorIdentity
from boundaries.authority_source import RoleAuthority
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.bnd_003_membership import Bnd003Input, Bnd003MembershipEvaluator
from boundaries.bnd_004_role_context import Bnd004Input, Bnd004RoleContextEvaluator
from boundaries.bnd_014_commit import Bnd014CommitEvaluator
from boundaries.registry import BoundaryChainResult, BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from command.envelope import CommandEnvelope, CommandOutcome
from commit.coordinator import (
    CommitCoordinator,
    CommitRepository,
    CurrentVersionReader,
    MutationOutcome,
)
from commit.idempotency import IdempotencyAlreadyCommitted, IdempotencyPort
from events.outbox import OutboxRepository
from governance.membership import WorkspaceRole
from persistence.challenge_repository import ChallengeRepository
from persistence.command_repository import CommandRepository
from persistence.membership_repository import MembershipRepository
from persistence.workspace_repository import (
    SqlAlchemyWorkspaceVersionReader,
    WorkspaceRepository,
    workspace_target_ref,
)
from semantic_types.ids import (
    AttemptId,
    ChallengeId,
    CommandId,
    CommitId,
    CorrelationId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion

_PRECOMMIT_CHAIN = (
    BoundaryId.BND_001,
    BoundaryId.BND_002,
    BoundaryId.BND_003,
    BoundaryId.BND_004,
)

_CHALLENGE_CREATOR_ROLES = frozenset({WorkspaceRole.FACILITATOR})


class ChallengeCreationDenied(Exception):
    """The PRECOMMIT boundary chain (BND-001..004) did not reach
    ALLOW. No Challenge row was ever written;
    `command_repository.record_outcome` already recorded
    `CommandOutcome.DENIED` before this is raised."""

    def __init__(self, chain_result: BoundaryChainResult) -> None:
        self.chain_result = chain_result
        super().__init__(chain_result.result.value)


@dataclass(frozen=True, slots=True)
class CreateChallengePayload:
    """The one concrete Command payload this Command introduces (09
    §9), mirroring `workspace_creation_handler.CreateWorkspacePayload`'s
    own precedent."""

    title: str
    description: str | None
    context: str | None
    desired_outcome: str | None
    constraints: str | None
    stakeholders: str | None


@dataclass(frozen=True, slots=True)
class CreateChallengeResult:
    """Mirrors `workspace_creation_handler.CreateWorkspaceResult`'s own
    precedent: a small, typed result carrying real IDs, not a raw
    `CommitUnit` (this Command's own hand-rolled write path constructs
    and appends a `CommitUnit` internally, the identical durable audit
    record every other Command produces, but does not return it
    directly — a future caller needing the `CommitUnit` itself can
    already read it back via `CommitRepository`, the same as any other
    committed operation)."""

    challenge_id: ChallengeId
    workspace_id: WorkspaceId


def _build_registry(
    *,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
) -> BoundaryRegistry:
    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd002WorkspaceEvaluator(workspace_repository))  # type: ignore[arg-type]
    registry.register(Bnd003MembershipEvaluator(membership_repository))  # type: ignore[arg-type]
    registry.register(Bnd004RoleContextEvaluator(membership_repository))  # type: ignore[arg-type]
    return registry


class _CreateChallengeMutation:
    def __init__(self, repository: ChallengeRepository, **fields: Any) -> None:
        self._repository = repository
        self._fields = fields

    def apply(self) -> MutationOutcome:
        fields = dict(self._fields)
        challenge_id: ChallengeId = fields.pop("challenge_id")
        self._repository.create(challenge_id, **fields)
        return MutationOutcome(
            state_before_ref=None,
            state_after_ref=f"challenge:{challenge_id.value}",
            event_type="CHALLENGE_CREATED",
            result_ref=str(challenge_id.value),
        )


def create_challenge(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    title: str,
    description: str | None,
    context: str | None,
    desired_outcome: str | None,
    constraints: str | None,
    stakeholders: str | None,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    idempotency_key: str | None,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    challenge_repository: ChallengeRepository,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    idempotency_port: IdempotencyPort,
    current_version_reader: CurrentVersionReader | None = None,
) -> CreateChallengeResult:
    """Create a new Challenge in `workspace_id`. `actor` must currently
    hold the `Facilitator` role there (proven fresh by BND-004) — no
    `HumanAuthorityBinding` is required (AUTH-DEP-CH-001, see module
    docstring for why BND-005 is deliberately absent from this
    Command's own precommit chain).

    Raises `ValueError` for a malformed `title`, before any boundary is
    even evaluated (mirrors `create_workspace`'s own identical
    precedent for `workspace_name`). Raises `ChallengeCreationDenied`
    if the precommit chain does not reach ALLOW. Raises
    `commit.coordinator.CommitFailedPrecommit` if the Workspace's own
    version changed between authority resolution and this Command's
    own SAVEPOINT (see module docstring for why this Command re-checks
    that itself rather than through `CommitCoordinator`/BND-014). A
    retried call with the same `idempotency_key` (and the same
    `command_id`/payload -- 14 section 27) returns the ALREADY-CREATED
    Challenge's own `CreateChallengeResult` rather than creating a
    second one (see module docstring's own "WHY IDEMPOTENT RETRY..."
    section for why this Command materializes the prior result itself
    rather than merely letting `IdempotencyAlreadyCommitted` propagate).
    """
    if not title or not title.strip():
        raise ValueError("title must be non-empty")

    workspace = workspace_repository.get(workspace_id)

    boundary_context = BoundaryContext(
        workspace_id=workspace_id,
        operation="CreateChallenge",
        actor=actor,
        correlation_id=correlation_id,
        evaluated_at=occurred_at,
    )
    registry = _build_registry(
        workspace_repository=workspace_repository,
        membership_repository=membership_repository,
    )

    if workspace is None:
        # `commands.workspace_id` carries a real, non-deferrable FK to
        # `workspaces.id` (`fk_commands_workspace`) — mirrors
        # `AddMember`/`RevokeHumanAuthorityBinding`/
        # `GrantHumanAuthorityBinding`'s own locally-fixed precheck.
        precheck_inputs: dict[BoundaryId, object] = {
            BoundaryId.BND_001: Bnd001Input(
                boundary_id=BoundaryId.BND_001,
                context=boundary_context,
                required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
            ),
            BoundaryId.BND_002: Bnd002Input(
                boundary_id=BoundaryId.BND_002,
                context=boundary_context,
                resolved_object_workspace_ids=(),
            ),
        }
        precheck_chain = (BoundaryId.BND_001, BoundaryId.BND_002)
        precheck_result = evaluate_chain(
            registry,
            precheck_chain,
            precheck_inputs,  # type: ignore[arg-type]
            boundary_context,
        )
        raise ChallengeCreationDenied(precheck_result)

    boundary_inputs: dict[BoundaryId, object] = {
        BoundaryId.BND_001: Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=boundary_context,
            required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
        ),
        BoundaryId.BND_002: Bnd002Input(
            boundary_id=BoundaryId.BND_002,
            context=boundary_context,
            resolved_object_workspace_ids=(workspace.id,),
        ),
        BoundaryId.BND_003: Bnd003Input(boundary_id=BoundaryId.BND_003, context=boundary_context),
    }
    actor_membership = membership_repository.get_current_membership(workspace_id, actor.user_id)
    if actor_membership is not None:
        boundary_inputs[BoundaryId.BND_004] = Bnd004Input(
            boundary_id=BoundaryId.BND_004,
            context=boundary_context,
            membership_id=actor_membership.id,
            accepted_roles=_CHALLENGE_CREATOR_ROLES,
        )

    target_ref = workspace_target_ref(workspace_id)
    challenge_id = ChallengeId(uuid.uuid4())
    challenge_ref = f"challenge:{challenge_id.value}"
    envelope = CommandEnvelope(
        command_id=command_id,
        command_type="CMD_CREATE_CHALLENGE",
        command_contract_version=ContractVersion("1.0"),
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        requested_at=occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=(target_ref,),
        expected_versions={target_ref: workspace.record_version},
        created_refs=(challenge_ref,),
        payload=CreateChallengePayload(
            title=title,
            description=description,
            context=context,
            desired_outcome=desired_outcome,
            constraints=constraints,
            stakeholders=stakeholders,
        ),
        idempotency_key=idempotency_key,
    )
    command_repository.record_attempt(envelope, received_at=occurred_at)

    chain_result = evaluate_chain(registry, _PRECOMMIT_CHAIN, boundary_inputs, boundary_context)  # type: ignore[arg-type]
    if chain_result.result is not BoundaryResult.ALLOW:
        command_repository.record_outcome(
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=occurred_at,
        )
        raise ChallengeCreationDenied(chain_result)

    if idempotency_key is not None:
        try:
            idempotency_port.begin(envelope, seen_at=occurred_at)
        except IdempotencyAlreadyCommitted as exc:
            existing = exc.existing
            existing_challenge = (
                challenge_repository.get(ChallengeId(uuid.UUID(existing.result_ref)))
                if existing.result_ref is not None
                else None
            )
            if existing_challenge is None:
                # `result_ref` did not resolve to a real, still-existing
                # Challenge -- fail closed rather than silently
                # fabricating a result (mirrors 06 section 19's own
                # "fail closed when validity cannot be proven").
                raise
            command_repository.record_outcome(
                attempt_id=attempt_id,
                workspace_id=workspace_id,
                outcome=CommandOutcome.COMMITTED,
                completed_at=occurred_at,
                commit_id=existing.commit_id,
            )
            return CreateChallengeResult(
                challenge_id=existing_challenge.challenge_id,
                workspace_id=existing_challenge.workspace_id,
            )

    # F02 HD-6: admitted by the single effect gate with a ROLE authority
    # source (AUTH-DEP-CH-001). BND-014 re-reads the Workspace version and
    # the actor's CURRENT Facilitator role at commit time; the audit row
    # references the real `role_assignments` row.
    coordinator = CommitCoordinator(
        connection,
        bnd014_evaluator=Bnd014CommitEvaluator(None, membership_repository=membership_repository),
        command_repository=command_repository,
        audit_repository=audit_repository,
        outbox_repository=outbox_repository,
        commit_repository=commit_repository,
        idempotency_port=idempotency_port,
    )
    coordinator.commit(
        envelope=envelope,
        actor=actor,
        authority=RoleAuthority(
            accepted_roles=_CHALLENGE_CREATOR_ROLES, operation_authority_ref="AUTH-DEP-CH-001"
        ),
        upstream_chain_result=chain_result.result,
        current_version_reader=current_version_reader
        or SqlAlchemyWorkspaceVersionReader(connection, workspace_id=workspace_id),
        mutation=_CreateChallengeMutation(
            challenge_repository,
            challenge_id=challenge_id,
            workspace_id=workspace_id,
            title=title,
            description=description,
            context=context,
            desired_outcome=desired_outcome,
            constraints=constraints,
            stakeholders=stakeholders,
            created_at=occurred_at,
        ),
        occurred_at=occurred_at,
        commit_id=commit_id,
    )

    return CreateChallengeResult(challenge_id=challenge_id, workspace_id=workspace_id)


__all__ = [
    "ChallengeCreationDenied",
    "CreateChallengePayload",
    "CreateChallengeResult",
    "create_challenge",
]
