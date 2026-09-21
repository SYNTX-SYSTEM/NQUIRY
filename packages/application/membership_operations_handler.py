"""AddMember: the real, governed "Workspace governance root adds a
member" Command (F01 WU-01.5).

Source: `docs/architecture/04_AUTHORITY_AND_DECISION_RIGHTS.md`
GAP-04-014 ("AC-04-001 makes Workspace Owner the governance root. 05
must define exact operations for: invite/add member, remove member,
assign Workspace role, change role, revoke role") — CLOSED by
`docs/architecture/05_GOVERNANCE_INSIDE_SYSTEM.md`: "Workspace
governance root administers membership and role assignments." This
Command is that closure, materialized: the one and only legitimate
caller is a human who already holds `WORKSPACE_GOVERNANCE_RIGHT` for
the target Workspace (proven fresh by BND-005 on every call, never
cached).

UNLIKE `workspace_creation_handler.create_workspace`, THIS COMMAND USES
`CommitCoordinator` DIRECTLY
--------------------------------------------------------------------
`CreateWorkspace` could not use `CommitCoordinator` because the actor
did not yet hold the authority being checked (circular). That
circularity does not exist here: the actor calling `add_member`
already holds `WORKSPACE_GOVERNANCE_RIGHT` over an ALREADY-EXISTING
Workspace — exactly the shape `human_decision_handler`/
`question_selection_handler` already established. This Command
therefore follows their identical pattern: BND-001..005 precommit
chain, then `CommitCoordinator.commit()` for the real atomic write,
never a hand-rolled `connection.begin_nested()` block.

WHY THE NEW MEMBER'S ROLE CAN NEVER BE `WorkspaceRole.OWNER`
--------------------------------------------------------------------
19 §21's own BACKEND REQUIREMENTS line states plainly: "No: ... role =
right." Assigning the `Owner` role label to a second person here would
NOT grant them `WORKSPACE_GOVERNANCE_RIGHT` (that binding is
`CreateWorkspace`'s own exclusive output, WU-01.4b) — a member labeled
"Owner" without the matching binding would be exactly the misleading
role/right collapse 04/19 forbid, just inverted (a label implying
authority the row does not structurally carry). Separately, granting a
SECOND `WORKSPACE_GOVERNANCE_RIGHT` binding for the same Workspace is
`docs/architecture/05_GOVERNANCE_INSIDE_SYSTEM.md`'s own GAP-05-001
("Workspace Root Creation and Succession... owner transfer and
succession remain undefined"), `[UNDERDEFINED]`, unresolved. This
Command therefore refuses `WorkspaceRole.OWNER` outright
(`OwnerRoleNotAssignable`) rather than silently under- or
over-granting — the same "STOP rather than invent" discipline this
whole Field has followed since HARD-DEP-001.

WHY A NON-EXISTENT `workspace_id` IS DENIED *BEFORE* `record_attempt`,
NOT AFTER (A GENUINE, CODEBASE-WIDE FINDING FROM THIS WORK UNIT)
--------------------------------------------------------------------
`commands.workspace_id` carries a real, non-deferrable FK to
`workspaces.id` (`fk_commands_workspace`) -- discovered the hard way in
WU-01.4b for a target that did not exist YET. Building this Command's
own adversarial test for "non-existent Workspace" surfaced the SAME
constraint from the opposite direction: a `workspace_id` a caller
supplies that never resolves to any real row at all raises a raw,
unhandled `ForeignKeyViolation` from `record_attempt` itself, before
BND-002 ever gets a chance to translate that into a graceful `DENY`.
Neither `human_decision_handler` nor `question_selection_handler` (the
two existing full-chain Commands this module's pattern otherwise
mirrors exactly) has ever had this path exercised by a test — both
call `record_attempt` unconditionally before their own boundary chain,
and no existing test in this codebase supplies a `workspace_id` that
does not exist. This Command evaluates BND-001/002 alone, BEFORE
building the envelope or calling `record_attempt`, specifically for
the `workspace is None` case, and raises `AddMemberDenied` directly if
so — no `commands` row is ever attempted for a Workspace that was
never real. This is disclosed as a genuine, pre-existing latent gap in
the shared pattern, not fixed in the other two files (outside this
Work Unit's own scope) — see WU-01.5's own report, "First Broken
Relation".

WHY "REMOVE MEMBER" / "CHANGE ROLE" / "REVOKE ROLE" ARE NOT IN THIS
FILE
--------------------------------------------------------------------
GAP-04-014 names five operations; this Work Unit builds "invite/add
member" (the one that makes every other F01 Work Unit — WU-01.2's own
accessible-Workspace query, WU-01.3's own membership-aware context —
actually exercisable by someone other than a Workspace's own founder).
The remaining four are real, legitimate, equally-closed-by-05 scope,
disclosed here as `SUCCESSOR_NOT_BUILT` rather than rushed alongside
this one to preserve the same one-Command-at-a-time review discipline
`workspace_creation_handler` itself followed.
"""

from __future__ import annotations

import uuid
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
from events.outbox import OutboxRepository
from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole
from persistence.command_repository import CommandRepository
from persistence.membership_repository import MembershipRepository
from persistence.workspace_repository import WorkspaceRepository, workspace_target_ref
from semantic_types.ids import AttemptId, CommandId, CommitId, CorrelationId, UserId, WorkspaceId
from semantic_types.versions import ContractVersion, RecordVersion

_PRECOMMIT_CHAIN = (
    BoundaryId.BND_001,
    BoundaryId.BND_002,
    BoundaryId.BND_003,
    BoundaryId.BND_004,
    BoundaryId.BND_005,
)

_ASSIGNABLE_ROLES = frozenset({WorkspaceRole.FACILITATOR, WorkspaceRole.CONTRIBUTOR})
_MEMBERSHIP_ADMIN_ROLES = frozenset({WorkspaceRole.OWNER})


class OwnerRoleNotAssignable(ValueError):
    """Raised before any boundary is evaluated. See module docstring
    ("WHY THE NEW MEMBER'S ROLE CAN NEVER BE `WorkspaceRole.OWNER`")."""

    def __init__(self) -> None:
        super().__init__(
            "WorkspaceRole.OWNER cannot be assigned via add_member; "
            "Workspace root succession is GAP-05-001, unresolved"
        )


class AddMemberDenied(Exception):
    """The PRECOMMIT boundary chain (BND-001..005) did not reach ALLOW.
    No membership/role row was ever written; `command_repository.record_outcome`
    already recorded `CommandOutcome.DENIED` before this is raised."""

    def __init__(self, chain_result: BoundaryChainResult) -> None:
        self.chain_result = chain_result
        super().__init__(chain_result.result.value)


@dataclass(frozen=True, slots=True)
class AddMemberPayload:
    """The one concrete Command payload this Command introduces (09
    §9), mirroring `workspace_creation_handler.CreateWorkspacePayload`'s
    own precedent."""

    new_member_user_id: str
    role: str


def _find_proof(proofs: tuple[BoundaryProof, ...], boundary_id: BoundaryId) -> BoundaryProof | None:
    for proof in proofs:
        if proof.boundary_id is boundary_id:
            return proof
    return None


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


class _AddMemberMutation:
    """Wraps two real repository writes
    (`MembershipRepository.create_membership`/`.assign_role`) as one
    `MutationExecutor`. Both run inside the SAME `connection.begin_nested()`
    SAVEPOINT `CommitCoordinator._commit_inner` already opens — AC-09-006's
    "governance mutation bundles ... commit completely, or [are] treated
    as INDETERMINATE" is satisfied by construction, not by any extra
    code here: a partial write is impossible because both calls share
    one transaction. Any exception (the `uq_workspace_memberships_active_pair`
    partial-unique index rejecting an already-ACTIVE member, a
    non-existent `new_member_user_id` violating
    `fk_workspace_memberships_user`) propagates through
    `CommitCoordinator`'s own generic rollback handling as
    `CommitFailedPrecommit`, the same "checked at two independent
    layers" discipline every prior mutation in this codebase relies on.
    """

    def __init__(
        self,
        membership_repository: MembershipRepository,
        *,
        membership_id: uuid.UUID,
        role_assignment_id: uuid.UUID,
        workspace_id: WorkspaceId,
        new_member_user_id: UserId,
        role: WorkspaceRole,
        granted_by_user_id: UserId,
        occurred_at: datetime,
    ) -> None:
        self._membership_repository = membership_repository
        self._membership_id = membership_id
        self._role_assignment_id = role_assignment_id
        self._workspace_id = workspace_id
        self._new_member_user_id = new_member_user_id
        self._role = role
        self._granted_by_user_id = granted_by_user_id
        self._occurred_at = occurred_at

    def apply(self) -> MutationOutcome:
        self._membership_repository.create_membership(
            self._membership_id,
            workspace_id=self._workspace_id,
            user_id=self._new_member_user_id,
            created_at=self._occurred_at,
        )
        self._membership_repository.assign_role(
            self._role_assignment_id,
            workspace_id=self._workspace_id,
            membership_id=self._membership_id,
            role=self._role,
            granted_by_user_id=self._granted_by_user_id,
            granted_at=self._occurred_at,
        )
        return MutationOutcome(
            state_before_ref=None,
            state_after_ref=self._role.value,
            relation_refs=(
                f"membership:{self._membership_id}",
                f"role_assignment:{self._role_assignment_id}",
            ),
        )


def add_member(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    new_member_user_id: UserId,
    role: WorkspaceRole,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    idempotency_key: str | None,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    authority_resolver: AuthorityResolver,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    idempotency_port: IdempotencyPort,
    current_version_reader: CurrentVersionReader,
    failure_injector: FailureInjectionPort | None = None,
) -> CommitUnit:
    """Add `new_member_user_id` to `workspace_id` with `role`. `actor`
    must currently hold `WORKSPACE_GOVERNANCE_RIGHT` for `workspace_id`
    (proven fresh by BND-005) AND currently be an `Owner`-role member
    of it (proven fresh by BND-004) — both checks, not either alone
    (04/06 non-collapse: role and right are separately proven, never
    substituted for one another).

    Raises `OwnerRoleNotAssignable` before any boundary evaluation if
    `role is WorkspaceRole.OWNER`. Raises `AddMemberDenied` if the
    precommit chain does not reach ALLOW.
    """
    if role not in _ASSIGNABLE_ROLES:
        raise OwnerRoleNotAssignable()

    workspace = workspace_repository.get(workspace_id)
    resolved_object_workspace_ids = (workspace.id,) if workspace is not None else ()

    context = BoundaryContext(
        workspace_id=workspace_id,
        operation="AddMember",
        actor=actor,
        correlation_id=correlation_id,
        evaluated_at=occurred_at,
    )
    registry = _build_registry(
        workspace_repository=workspace_repository,
        membership_repository=membership_repository,
        authority_resolver=authority_resolver,
    )

    if workspace is None:
        # `commands.workspace_id` carries a real, non-deferrable FK to
        # `workspaces.id` (`fk_commands_workspace`) -- unlike
        # `workspace_creation_handler.create_workspace` (whose target
        # does not exist YET), a workspace_id here may never resolve
        # to a real row at all (a forged/mistyped ID). `record_attempt`
        # cannot be called for it -- deny via BND-001/002 directly,
        # before any `commands` row is even attempted.
        precheck_inputs: dict[BoundaryId, object] = {
            BoundaryId.BND_001: Bnd001Input(
                boundary_id=BoundaryId.BND_001,
                context=context,
                required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
            ),
            BoundaryId.BND_002: Bnd002Input(
                boundary_id=BoundaryId.BND_002,
                context=context,
                resolved_object_workspace_ids=(),
            ),
        }
        precheck_chain = (BoundaryId.BND_001, BoundaryId.BND_002)
        precheck_result = evaluate_chain(registry, precheck_chain, precheck_inputs, context)  # type: ignore[arg-type]
        raise AddMemberDenied(precheck_result)

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
    actor_membership = (
        membership_repository.get_current_membership(workspace_id, actor.user_id)
        if resolved_object_workspace_ids
        else None
    )
    if actor_membership is not None:
        boundary_inputs[BoundaryId.BND_004] = Bnd004Input(
            boundary_id=BoundaryId.BND_004,
            context=context,
            membership_id=actor_membership.id,
            accepted_roles=_MEMBERSHIP_ADMIN_ROLES,
        )
        boundary_inputs[BoundaryId.BND_005] = Bnd005Input(
            boundary_id=BoundaryId.BND_005,
            context=context,
            required_authority_class=AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
        )

    target_ref = workspace_target_ref(workspace_id)
    envelope = CommandEnvelope(
        command_id=command_id,
        command_type="CMD_ADD_MEMBER",
        command_contract_version=ContractVersion("1.0"),
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        requested_at=occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=(target_ref,),
        expected_versions={
            target_ref: workspace.record_version
            if workspace is not None
            else RecordVersion.initial()
        },
        payload=AddMemberPayload(new_member_user_id=str(new_member_user_id.value), role=role.value),
        idempotency_key=idempotency_key,
    )
    command_repository.record_attempt(envelope, received_at=occurred_at)

    chain_result = evaluate_chain(registry, _PRECOMMIT_CHAIN, boundary_inputs, context)  # type: ignore[arg-type]
    if chain_result.result is not BoundaryResult.ALLOW:
        command_repository.record_outcome(
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=occurred_at,
        )
        raise AddMemberDenied(chain_result)

    bnd005_proof = _find_proof(chain_result.proofs, BoundaryId.BND_005)
    if bnd005_proof is None or bnd005_proof.authority_proof is None:
        # Defensive: BND-005 ALLOWed, so a granting binding was proven
        # to exist -- unreachable in practice, kept as a fail-closed
        # guard rather than proceeding without a real authority proof.
        raise AddMemberDenied(chain_result)

    if idempotency_key is not None:
        idempotency_port.begin(envelope, seen_at=occurred_at)

    membership_id = uuid.uuid4()
    role_assignment_id = uuid.uuid4()

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
    mutation = _AddMemberMutation(
        membership_repository,
        membership_id=membership_id,
        role_assignment_id=role_assignment_id,
        workspace_id=workspace_id,
        new_member_user_id=new_member_user_id,
        role=role,
        granted_by_user_id=actor.user_id,
        occurred_at=occurred_at,
    )
    return coordinator.commit(
        envelope=envelope,
        actor=actor,
        required_authority_class=AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT,
        authority_scope_type="WORKSPACE",
        authority_scope_id=workspace_id.value,
        upstream_chain_result=chain_result.result,
        current_version_reader=current_version_reader,
        mutation=mutation,
        occurred_at=occurred_at,
        commit_id=commit_id,
    )


__all__ = [
    "OwnerRoleNotAssignable",
    "AddMemberDenied",
    "AddMemberPayload",
    "add_member",
]
