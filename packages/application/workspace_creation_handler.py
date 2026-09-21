"""CreateWorkspace: the real, governed "self-service founder" Workspace
creation Command that closes HARD-DEP-001 for this prototype's own
scope (14 §36's own API map already named
`POST /v1/workspaces -> CreateWorkspace`, "BLOCKED in legitimate proof
runtime by HARD-DEP-001").

[HUMAN-CONFIRMED ARCHITECTURAL DECISION, F01 WU-01.4, 2026-09-21]
Any real, verified human may create a Workspace and becomes its own
governance root at the moment of creation, via this real governed
Command -- not a raw DB insert, not first-login-implies-owner as a
side effect. Ungated self-service for now (no invite/approval gate),
but the eligibility check is a named, replaceable port
(`WorkspaceCreationEligibilityChecker`), never a hardcoded always-true
buried inside this function, so a future gate can be added without
re-architecting this Command. Full reasoning:
`docs/implementation/field-reports/F01/WU-01.4.md`.

WHY THIS COMMAND DOES NOT CALL `commit.coordinator.CommitCoordinator`
--------------------------------------------------------------------
Identical structural reason to `application.recovery_handler`'s own
disclosed precedent (PKG-24): `CommitCoordinator.commit()`
hard-requires `required_authority_class`/`authority_scope_type`/
`authority_scope_id` -- the actor must ALREADY hold the authority being
checked, BEFORE the mutation runs. For CreateWorkspace this is
circular by construction: the actor does not yet hold
`WORKSPACE_GOVERNANCE_RIGHT` for a Workspace that does not exist yet --
that binding is this Command's own OUTPUT, not its precondition.
Passing it as `required_authority_class` would either deny every real
founder (nothing could ever found a Workspace) or require some other
actor to already hold it (begging the exact HARD-DEP-001 question).
This Command therefore performs its own governed write: BND-001 only
(identity) -- BND-002/003/004 are structurally inapplicable to
creating the very Workspace they would check membership/role against
(`Bnd002WorkspaceEvaluator` itself calls `WorkspaceRepository.get`,
which would correctly DENY "workspace not found" for a not-yet-created
one) -- then the named eligibility check, then a real atomic
transaction (`connection.begin_nested()`, the identical SAVEPOINT
`CommitCoordinator` already uses internally) writing `workspaces`,
`commands`/`command_attempts`, `workspace_memberships`,
`role_assignments`, `human_authority_bindings`, `commit_units`,
`audit_events`, and `outbox_events` -- the first four through the
newly added write methods on `WorkspaceRepository`/`MembershipRepository`/
`AuthorityBindingRepository` (14 §3.1/§4 forbids `application` from
importing `sqlalchemy` directly; those three repositories, in
`persistence`, are where the actual inserts live), the rest through
the same `CommitRepository`/`AuditRepository`/`OutboxRepository` ports
every other governed Command already uses.

WHY `command_repository.record_attempt` RUNS *INSIDE* THE SAVEPOINT
HERE, UNLIKE EVERY OTHER GOVERNED COMMAND IN THIS CODEBASE
--------------------------------------------------------------------
Every other handler (`human_decision_handler`, `question_selection_handler`)
calls `record_attempt` BEFORE its mutation, so a `commands` row exists
even for an attempt that goes on to fail -- a genuine "this was tried"
audit trail regardless of outcome. That ordering is impossible here:
`commands.workspace_id` carries a real, non-deferrable foreign key to
`workspaces.id` (`fk_commands_workspace`), and for THIS Command the
Workspace named by that FK does not exist until this Command's own
write creates it. Writing `commands` first would violate the FK;
writing it after committing `workspaces` separately would break
atomicity (a founder row could exist with no matching audit trail, or
vice versa, if the process died between the two). The only fix that
invents no schema change is to bring `workspaces` into existence FIRST
within the SAVEPOINT, then write `commands`/`command_attempts` against
the now-real row, all inside one atomic unit.

CONSEQUENCE, DISCLOSED HONESTLY: a FAILED founding attempt leaves NO
`commands`/`command_attempts` row at all -- not a `FAILED_PRECOMMIT`
one, none. This is not a swallowed error (the exception still
propagates to the caller uncaught); it is the schema's own FK
correctly refusing to let an operational record reference a canonical
record that was never actually brought into being. Every other
governed Command's "failed attempts are still recorded" property holds
for every Command whose target pre-exists; it cannot hold, by
construction, for the one Command whose target is its own output. See
`docs/implementation/field-reports/F01/WU-01.4b.md`'s own First Broken
Relation section.

WHY `authority_source="LEVEL_1_EXPLICIT"`, NEVER
`FIXTURE_LEGITIMACY`/`"NON_PROOF_FIXTURE"`
--------------------------------------------------------------------
04 §9's own vocabulary for direct, explicit human-established
authority -- exactly what a real founding act is. This is the one
field that structurally, permanently distinguishes a
`HumanAuthorityBinding` this Command created from one
`test_support.nonproof_bootstrap.NonProofWorkspaceBootstrap` created
(`authority_source == "NON_PROOF_FIXTURE"`) -- a real query can always
tell the two apart. `CreateWorkspaceResult` (below) also structurally
carries no `fixture_legitimacy` field at all, unlike
`NonProofWorkspaceBootstrapResult`, so a caller holding one can never
mistake it for the other.

WHY THE FOUNDER'S OWN BINDING IS SELF-GRANTED
(`granted_by_user_id == human_user_id`)
--------------------------------------------------------------------
Honest, not a workaround: nothing else could plausibly grant the FIRST
binding a genuinely new founder holds -- by definition no other holder
of `WORKSPACE_GOVERNANCE_RIGHT` for this not-yet-existing Workspace
could have granted it. `NonProofWorkspaceBootstrap` already
established this identical "root grants itself" shape for the fixture
lane, with its own disclosed honesty about why (12 §8.2: "seed_owner =
authority" is a refused shortcut for a FIXTURE precisely because
nothing legitimizes it there); this Command makes the same shape real,
legitimized by BND-001 (a real verified identity) plus the human
operator's own explicit Option-A decision, not by fiat.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from audit.models import AuditEvent, AuditRepository
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from command.envelope import CommandEnvelope, CommandOutcome
from commit.coordinator import CommitOutcome, CommitRepository, CommitUnit
from events.outbox import DeliveryStatus, OutboxRecord, OutboxRepository
from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole
from persistence.authority_binding_repository import AuthorityBindingRepository
from persistence.command_repository import CommandRepository
from persistence.membership_repository import MembershipRepository
from persistence.workspace_repository import WorkspaceRepository, workspace_target_ref
from semantic_types.ids import (
    AttemptId,
    AuditEventId,
    AuthorityBindingId,
    CommandId,
    CommitId,
    CorrelationId,
    EventId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion


@dataclass(frozen=True, slots=True)
class CreateWorkspacePayload:
    """The one concrete Command payload this Command introduces (09
    section 9: "raw dictionaries are rejected at public consequential
    boundaries" -- mirrors `question_selection_handler.SelectQuestionPayload`'s
    own precedent for a package-local payload contract).
    """

    workspace_name: str


class WorkspaceCreationDenied(Exception):
    """BND-001 denied the actor, or the eligibility checker denied this
    specific attempt. Fails closed -- no Workspace row is ever written
    on this path."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class WorkspaceCreationEligibility:
    allowed: bool
    reason_code: str


@runtime_checkable
class WorkspaceCreationEligibilityChecker(Protocol):
    """Named, replaceable eligibility step -- the human operator's own
    explicit constraint on this Command (WU-01.4): today's policy
    (anyone real may found a Workspace) must never be hardcoded so
    deep that a future invite/approval gate would require
    re-architecting this Command. A future concrete implementation
    (allowlist, invite code, admin approval queue) implements this
    exact Protocol and is swapped in at the composition root
    (`application.http_dispatch`) -- `create_workspace` itself never
    changes to add one."""

    def check(self, actor: ActorIdentity) -> WorkspaceCreationEligibility: ...


class AllowAllWorkspaceCreationEligibilityChecker:
    """The current, human-confirmed policy: ungated self-service. Every
    real, verified human (already proven by BND-001, evaluated before
    this checker ever runs) is eligible."""

    def check(self, actor: ActorIdentity) -> WorkspaceCreationEligibility:
        return WorkspaceCreationEligibility(allowed=True, reason_code="UNGATED_SELF_SERVICE")


@dataclass(frozen=True, slots=True)
class CreateWorkspaceResult:
    """Deliberately carries NO `fixture_legitimacy` field -- unlike
    `test_support.nonproof_bootstrap.NonProofWorkspaceBootstrapResult`,
    whose own `fixture_legitimacy` field exists precisely to mark
    non-proof output. This type's own shape is the structural proof
    that a caller holding one can never mistake it for the other."""

    workspace_id: WorkspaceId
    owner_user_id: UserId
    membership_id: uuid.UUID
    governance_binding_id: AuthorityBindingId


def create_workspace(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_name: str,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    eligibility_checker: WorkspaceCreationEligibilityChecker,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    authority_binding_repository: AuthorityBindingRepository,
) -> CreateWorkspaceResult:
    """Real, governed Workspace creation. Raises `WorkspaceCreationDenied`
    (fails closed, writes nothing) if BND-001 or the eligibility
    checker denies. Raises `ValueError` for a malformed
    `workspace_name`, before any boundary is even evaluated."""
    if not workspace_name or not workspace_name.strip():
        raise ValueError("workspace_name must be non-empty")

    workspace_id = WorkspaceId(uuid.uuid4())

    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
    context = BoundaryContext(
        workspace_id=workspace_id,
        operation="CreateWorkspace",
        actor=actor,
        correlation_id=correlation_id,
        evaluated_at=occurred_at,
    )
    boundary_inputs: dict[BoundaryId, object] = {
        BoundaryId.BND_001: Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=context,
            required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
        )
    }
    chain_result = evaluate_chain(registry, [BoundaryId.BND_001], boundary_inputs, context)  # type: ignore[arg-type]
    if chain_result.result is not BoundaryResult.ALLOW:
        terminal = chain_result.proofs[-1] if chain_result.proofs else None
        raise WorkspaceCreationDenied(
            terminal.reason_code if terminal is not None else "BND_001_DENIED"
        )

    eligibility = eligibility_checker.check(actor)
    if not eligibility.allowed:
        raise WorkspaceCreationDenied(eligibility.reason_code)

    target_ref = workspace_target_ref(workspace_id)
    envelope = CommandEnvelope(
        command_id=command_id,
        command_type="CMD_CREATE_WORKSPACE",
        command_contract_version=ContractVersion("1.0"),
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        requested_at=occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=(target_ref,),
        # `workspace_id` was just generated and names a record that does
        # not exist yet -- `RecordVersion.initial()` is the established
        # "target may not exist yet" convention (mirrors
        # `application.question_selection_handler._build_envelope`'s own
        # identical comment), matching the `record_version=1` this
        # Command's own write below gives the new `workspaces` row.
        expected_versions={target_ref: RecordVersion.initial()},
        payload=CreateWorkspacePayload(workspace_name=workspace_name),
    )

    owner_user_id = actor.user_id
    membership_id = uuid.uuid4()
    governance_binding_id = AuthorityBindingId(uuid.uuid4())
    audit_event_id = AuditEventId(uuid.uuid4())
    outbox_id = uuid.uuid4()

    with connection.begin_nested():
        workspace_repository.create(
            workspace_id,
            name=workspace_name,
            owner_id=owner_user_id,
            created_at=occurred_at,
        )
        # Only now does a real `workspaces` row exist for
        # `fk_commands_workspace` to reference -- see module docstring.
        command_repository.record_attempt(envelope, received_at=occurred_at)
        membership_repository.create_membership(
            membership_id,
            workspace_id=workspace_id,
            user_id=owner_user_id,
            created_at=occurred_at,
        )
        membership_repository.assign_role(
            uuid.uuid4(),
            workspace_id=workspace_id,
            membership_id=membership_id,
            role=WorkspaceRole.OWNER,
            granted_by_user_id=owner_user_id,
            granted_at=occurred_at,
        )
        authority_binding_repository.grant(
            governance_binding_id,
            workspace_id=workspace_id,
            human_user_id=owner_user_id,
            authority_class=AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=owner_user_id,
            granted_at=occurred_at,
        )

        commit_unit = CommitUnit(
            commit_id=commit_id,
            command_id=command_id,
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            target_refs=(target_ref,),
            relation_refs=(),
            governance_refs=(f"authority_binding:{governance_binding_id.value}",),
            audit_event_ids=(audit_event_id,),
            outbox_ids=(outbox_id,),
            committed_at=occurred_at,
            outcome=CommitOutcome.COMMITTED,
        )
        commit_repository.append(commit_unit)

        audit_repository.append(
            AuditEvent(
                audit_event_id=audit_event_id,
                event_type="CMD_CREATE_WORKSPACE_COMMITTED",
                event_schema_version=ContractVersion("1.0"),
                workspace_id=workspace_id,
                occurred_at=occurred_at,
                actor_type=actor.actor_class.value,
                actor_id=str(actor.user_id.value),
                command_type=envelope.command_type,
                command_id=command_id,
                commit_id=commit_id,
                correlation_id=correlation_id,
                target_refs=(target_ref,),
                authority_source_ref=governance_binding_id.value,
                result=CommitOutcome.COMMITTED.value,
            )
        )

        outbox_repository.append(
            OutboxRecord(
                outbox_id=outbox_id,
                event_id=EventId(uuid.uuid4()),
                workspace_id=workspace_id,
                commit_id=commit_id,
                event_type="WORKSPACE_CREATED",
                created_at=occurred_at,
                delivery_status=DeliveryStatus.PENDING,
                delivery_attempt_count=0,
            )
        )
        # No `except` here: any exception at any point inside this
        # SAVEPOINT (including from `record_attempt` itself, e.g. a
        # replayed `attempt_id`) rolls the entire block back atomically
        # -- `workspaces` included. See module docstring for why a
        # failed founding attempt correctly leaves no `commands` row to
        # attach a `FAILED_PRECOMMIT` outcome to.

    command_repository.record_outcome(
        attempt_id=attempt_id,
        workspace_id=workspace_id,
        outcome=CommandOutcome.COMMITTED,
        completed_at=occurred_at,
        commit_id=commit_id,
    )

    return CreateWorkspaceResult(
        workspace_id=workspace_id,
        owner_user_id=owner_user_id,
        membership_id=membership_id,
        governance_binding_id=governance_binding_id,
    )


__all__ = [
    "CreateWorkspacePayload",
    "WorkspaceCreationDenied",
    "WorkspaceCreationEligibility",
    "WorkspaceCreationEligibilityChecker",
    "AllowAllWorkspaceCreationEligibilityChecker",
    "CreateWorkspaceResult",
    "create_workspace",
]
