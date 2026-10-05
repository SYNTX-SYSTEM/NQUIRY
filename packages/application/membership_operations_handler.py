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
    StaleVersionConflict,
)
from commit.idempotency import IdempotencyPort
from events.contracts import EventFacts
from events.outbox import OutboxRepository
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import WorkspaceRole
from persistence.authority_binding_repository import (
    AuthorityBindingConflict,
    AuthorityBindingRepository,
)
from persistence.command_repository import CommandRepository
from persistence.membership_repository import (
    MembershipConflict,
    MembershipRepository,
    membership_target_ref,
)
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
            event=EventFacts(
                aggregate_ref=f"workspace_membership:{self._membership_id}",
                payload={
                    "membership_id": str(self._membership_id),
                    "member_user_id": str(self._new_member_user_id.value),
                    "role_assignment_id": str(self._role_assignment_id),
                    "role": self._role.value,
                },
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


# ---------------------------------------------------------------------------
# WU-AUTHZ-01 (2026-10-05): the two successors 05 already specifies —
# GOV-003 REVOKE_MEMBERSHIP and GOV-004 ASSIGN_ROLE (change of the current
# role). Same gate as add_member (BND-001..005: Owner role AND
# WORKSPACE_GOVERNANCE_RIGHT, proven fresh), same coordinator, one CommitUnit
# each (09 §102.1 membership revocation bundle; 05 GOV-020 cleanup).
# ---------------------------------------------------------------------------


class MembershipNotFound(Exception):
    """The target has no ACTIVE membership in this Workspace (never a member,
    or already revoked). Raised only after the chain ALLOWed, so a non-root
    learns nothing about who is a member."""


class GovernanceRootNotRemovable(Exception):
    """05 §12 "target is not the sole Workspace governance root", §14, and
    L752 "Owner self-removal is denied until owner succession is explicitly
    architected" (GAP-05-001): the Workspace owner, a holder of an ACTIVE
    WORKSPACE_GOVERNANCE_RIGHT, or a current Owner-role member is not
    removable and its role is not changeable through these commands."""


class RoleUnchanged(ValueError):
    """The requested role is the member's current role: nothing to change."""


@dataclass(frozen=True, slots=True)
class RevokeMembershipPayload:
    member_user_id: str


@dataclass(frozen=True, slots=True)
class ChangeMemberRolePayload:
    member_user_id: str
    role: str


class _RevokeMembershipMutation:
    """One SAVEPOINT: current role ended, every ACTIVE binding of the member in
    this Workspace revoked (05 GOV-020, 09 §102.1 — the same logical bundle),
    then the membership ACTIVE → REVOKED with its version advanced. A stale
    binding or membership version raises `StaleVersionConflict` (the whole
    bundle rolls back: partial cleanup never commits)."""

    def __init__(
        self,
        membership_repository: MembershipRepository,
        binding_repository: AuthorityBindingRepository,
        *,
        workspace_id: WorkspaceId,
        membership_id: uuid.UUID,
        membership_version: RecordVersion,
        member_user_id: UserId,
        revoked_by_user_id: UserId,
        occurred_at: datetime,
    ) -> None:
        self._memberships = membership_repository
        self._bindings = binding_repository
        self._workspace_id = workspace_id
        self._membership_id = membership_id
        self._membership_version = membership_version
        self._member_user_id = member_user_id
        self._revoked_by = revoked_by_user_id
        self._occurred_at = occurred_at

    def apply(self) -> MutationOutcome:
        relation_refs: list[str] = [membership_target_ref(self._membership_id)]
        role = self._memberships.get_current_role(self._membership_id)
        if role is not None:
            self._memberships.revoke_role(role.id, revoked_at=self._occurred_at)
            relation_refs.append(f"role_assignment:{role.id}")
        revoked_bindings = 0
        for binding in self._bindings.list_current_bindings(
            self._workspace_id, self._member_user_id
        ):
            if binding.state is not AuthorityBindingState.ACTIVE:
                continue
            try:
                self._bindings.revoke(
                    binding.id,
                    expected_record_version=binding.record_version,
                    revoked_by_user_id=self._revoked_by,
                    revoked_at=self._occurred_at,
                )
            except AuthorityBindingConflict as exc:
                raise StaleVersionConflict(str(exc)) from exc
            relation_refs.append(f"authority_binding:{binding.id.value}")
            revoked_bindings += 1
        try:
            self._memberships.revoke_membership(
                self._membership_id,
                expected_record_version=self._membership_version,
                revoked_at=self._occurred_at,
            )
        except MembershipConflict as exc:
            raise StaleVersionConflict(str(exc)) from exc
        return MutationOutcome(
            state_before_ref="ACTIVE",
            state_after_ref="REVOKED",
            relation_refs=tuple(relation_refs),
            event=EventFacts(
                aggregate_ref=membership_target_ref(self._membership_id),
                payload={
                    "membership_id": str(self._membership_id),
                    "member_user_id": str(self._member_user_id.value),
                    "revoked_role_assignment_id": "" if role is None else str(role.id),
                    "revoked_binding_count": revoked_bindings,
                },
            ),
        )


class _ChangeMemberRoleMutation:
    """05 §13 change model: the prior role assignment ends and a new one is
    inserted (history preserved; `uq_role_assignments_active_per_membership`
    enforces the order); the membership aggregate's version advances."""

    def __init__(
        self,
        membership_repository: MembershipRepository,
        *,
        workspace_id: WorkspaceId,
        membership_id: uuid.UUID,
        membership_version: RecordVersion,
        member_user_id: UserId,
        previous_role_assignment_id: uuid.UUID,
        previous_role: WorkspaceRole,
        role_assignment_id: uuid.UUID,
        role: WorkspaceRole,
        granted_by_user_id: UserId,
        occurred_at: datetime,
    ) -> None:
        self._memberships = membership_repository
        self._workspace_id = workspace_id
        self._membership_id = membership_id
        self._membership_version = membership_version
        self._member_user_id = member_user_id
        self._previous_id = previous_role_assignment_id
        self._previous_role = previous_role
        self._role_assignment_id = role_assignment_id
        self._role = role
        self._granted_by = granted_by_user_id
        self._occurred_at = occurred_at

    def apply(self) -> MutationOutcome:
        if not self._memberships.revoke_role(self._previous_id, revoked_at=self._occurred_at):
            raise StaleVersionConflict(f"role assignment {self._previous_id} is no longer current")
        self._memberships.assign_role(
            self._role_assignment_id,
            workspace_id=self._workspace_id,
            membership_id=self._membership_id,
            role=self._role,
            granted_by_user_id=self._granted_by,
            granted_at=self._occurred_at,
        )
        try:
            self._memberships.touch_membership(
                self._membership_id, expected_record_version=self._membership_version
            )
        except MembershipConflict as exc:
            raise StaleVersionConflict(str(exc)) from exc
        return MutationOutcome(
            state_before_ref=self._previous_role.value,
            state_after_ref=self._role.value,
            relation_refs=(
                f"role_assignment:{self._previous_id}",
                f"role_assignment:{self._role_assignment_id}",
            ),
            event=EventFacts(
                aggregate_ref=membership_target_ref(self._membership_id),
                payload={
                    "membership_id": str(self._membership_id),
                    "member_user_id": str(self._member_user_id.value),
                    "previous_role_assignment_id": str(self._previous_id),
                    "previous_role": self._previous_role.value,
                    "role_assignment_id": str(self._role_assignment_id),
                    "role": self._role.value,
                },
            ),
        )


def _governance_root_gate(
    *,
    workspace: Any,
    membership_repository: MembershipRepository,
    binding_repository: AuthorityBindingRepository,
    target_membership: Any,
    member_user_id: UserId,
) -> None:
    """GOV-003 / §14: the governance root is neither removable nor
    re-labelled (GAP-05-001 undefined succession). Three independent facts,
    any one of which refuses: the Workspace's `owner_id`, an ACTIVE
    WORKSPACE_GOVERNANCE_RIGHT, the current Owner role."""
    if workspace.owner_id == member_user_id:
        raise GovernanceRootNotRemovable()
    for binding in binding_repository.list_current_bindings(workspace.id, member_user_id):
        if (
            binding.state is AuthorityBindingState.ACTIVE
            and binding.authority_class is AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT
        ):
            raise GovernanceRootNotRemovable()
    role = membership_repository.get_current_role(target_membership.id)
    if role is not None and role.role is WorkspaceRole.OWNER:
        raise GovernanceRootNotRemovable()


def _governance_precommit(
    *,
    connection: Any,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    operation: str,
    command_type: str,
    payload: object,
    target_ref: str,
    expected_version: RecordVersion,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    idempotency_key: str | None,
    workspace: Any,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    authority_resolver: AuthorityResolver,
    command_repository: CommandRepository,
    denied: type[Exception],
) -> tuple[CommandEnvelope, BoundaryChainResult]:
    """The add_member gate, factored for the successors: BND-001/002 precheck
    for a Workspace that does not exist (never a `commands` row for it), then
    the envelope, `record_attempt` and the BND-001..005 chain (Owner role AND
    WORKSPACE_GOVERNANCE_RIGHT)."""
    context = BoundaryContext(
        workspace_id=workspace_id,
        operation=operation,
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
        precheck_inputs: dict[BoundaryId, object] = {
            BoundaryId.BND_001: Bnd001Input(
                boundary_id=BoundaryId.BND_001,
                context=context,
                required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
            ),
            BoundaryId.BND_002: Bnd002Input(
                boundary_id=BoundaryId.BND_002, context=context, resolved_object_workspace_ids=()
            ),
        }
        precheck = evaluate_chain(
            registry,
            (BoundaryId.BND_001, BoundaryId.BND_002),
            precheck_inputs,  # type: ignore[arg-type]
            context,
        )
        raise denied(precheck)
    boundary_inputs: dict[BoundaryId, object] = {
        BoundaryId.BND_001: Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=context,
            required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
        ),
        BoundaryId.BND_002: Bnd002Input(
            boundary_id=BoundaryId.BND_002,
            context=context,
            resolved_object_workspace_ids=(workspace.id,),
        ),
        BoundaryId.BND_003: Bnd003Input(boundary_id=BoundaryId.BND_003, context=context),
    }
    actor_membership = membership_repository.get_current_membership(workspace_id, actor.user_id)
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
        target_refs=(target_ref,),
        expected_versions={target_ref: expected_version},
        payload=payload,
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
        raise denied(chain_result)
    bnd005_proof = _find_proof(chain_result.proofs, BoundaryId.BND_005)
    if bnd005_proof is None or bnd005_proof.authority_proof is None:
        raise denied(chain_result)
    return envelope, chain_result


def revoke_membership(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    member_user_id: UserId,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    idempotency_key: str | None,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    binding_repository: AuthorityBindingRepository,
    authority_resolver: AuthorityResolver,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    idempotency_port: IdempotencyPort,
    current_version_reader: CurrentVersionReader,
    failure_injector: FailureInjectionPort | None = None,
) -> CommitUnit:
    """05 GOV-003 REVOKE_MEMBERSHIP by the governance root. Raises
    `AddMemberDenied` (the same gate), then — only after ALLOW —
    `MembershipNotFound` or `GovernanceRootNotRemovable`."""
    workspace = workspace_repository.get(workspace_id)
    target = (
        membership_repository.get_current_membership(workspace_id, member_user_id)
        if workspace is not None
        else None
    )
    # the target's membership version is the commit target; a missing target is
    # resolved after the gate (no disclosure), with the Workspace as the stale-checked ref
    target_ref = (
        membership_target_ref(target.id)
        if target is not None
        else workspace_target_ref(workspace_id)
    )
    expected = (
        target.record_version
        if target is not None
        else (workspace.record_version if workspace is not None else RecordVersion.initial())
    )
    envelope, chain_result = _governance_precommit(
        connection=connection,
        actor=actor,
        workspace_id=workspace_id,
        operation="RevokeMembership",
        command_type="CMD_REVOKE_MEMBERSHIP",
        payload=RevokeMembershipPayload(member_user_id=str(member_user_id.value)),
        target_ref=target_ref,
        expected_version=expected,
        command_id=command_id,
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        occurred_at=occurred_at,
        idempotency_key=idempotency_key,
        workspace=workspace,
        workspace_repository=workspace_repository,
        membership_repository=membership_repository,
        authority_resolver=authority_resolver,
        command_repository=command_repository,
        denied=AddMemberDenied,
    )
    assert workspace is not None
    if target is None:
        command_repository.record_outcome(
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=occurred_at,
        )
        raise MembershipNotFound()
    try:
        _governance_root_gate(
            workspace=workspace,
            membership_repository=membership_repository,
            binding_repository=binding_repository,
            target_membership=target,
            member_user_id=member_user_id,
        )
    except GovernanceRootNotRemovable:
        command_repository.record_outcome(
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=occurred_at,
        )
        raise
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
    mutation = _RevokeMembershipMutation(
        membership_repository,
        binding_repository,
        workspace_id=workspace_id,
        membership_id=target.id,
        membership_version=target.record_version,
        member_user_id=member_user_id,
        revoked_by_user_id=actor.user_id,
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


def change_member_role(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    member_user_id: UserId,
    role: WorkspaceRole,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    idempotency_key: str | None,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    binding_repository: AuthorityBindingRepository,
    authority_resolver: AuthorityResolver,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    idempotency_port: IdempotencyPort,
    current_version_reader: CurrentVersionReader,
    failure_injector: FailureInjectionPort | None = None,
) -> CommitUnit:
    """05 GOV-004 ASSIGN_ROLE as a change of the member's current role. The
    assignable set is add_member's (`OwnerRoleNotAssignable` otherwise, before
    any boundary); after ALLOW: `MembershipNotFound`, `GovernanceRootNotRemovable`
    (§14: the root's role is not re-labelled), `RoleUnchanged`."""
    if role not in _ASSIGNABLE_ROLES:
        raise OwnerRoleNotAssignable()
    workspace = workspace_repository.get(workspace_id)
    target = (
        membership_repository.get_current_membership(workspace_id, member_user_id)
        if workspace is not None
        else None
    )
    target_ref = (
        membership_target_ref(target.id)
        if target is not None
        else workspace_target_ref(workspace_id)
    )
    expected = (
        target.record_version
        if target is not None
        else (workspace.record_version if workspace is not None else RecordVersion.initial())
    )
    envelope, chain_result = _governance_precommit(
        connection=connection,
        actor=actor,
        workspace_id=workspace_id,
        operation="ChangeMemberRole",
        command_type="CMD_CHANGE_MEMBER_ROLE",
        payload=ChangeMemberRolePayload(member_user_id=str(member_user_id.value), role=role.value),
        target_ref=target_ref,
        expected_version=expected,
        command_id=command_id,
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        occurred_at=occurred_at,
        idempotency_key=idempotency_key,
        workspace=workspace,
        workspace_repository=workspace_repository,
        membership_repository=membership_repository,
        authority_resolver=authority_resolver,
        command_repository=command_repository,
        denied=AddMemberDenied,
    )
    assert workspace is not None

    def _deny() -> None:
        command_repository.record_outcome(
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=occurred_at,
        )

    if target is None:
        _deny()
        raise MembershipNotFound()
    try:
        _governance_root_gate(
            workspace=workspace,
            membership_repository=membership_repository,
            binding_repository=binding_repository,
            target_membership=target,
            member_user_id=member_user_id,
        )
    except GovernanceRootNotRemovable:
        _deny()
        raise
    current = membership_repository.get_current_role(target.id)
    if current is None:
        _deny()
        raise MembershipNotFound()  # an ACTIVE membership always has a current role (GOV-004)
    if current.role is role:
        _deny()
        raise RoleUnchanged(role.value)
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
    mutation = _ChangeMemberRoleMutation(
        membership_repository,
        workspace_id=workspace_id,
        membership_id=target.id,
        membership_version=target.record_version,
        member_user_id=member_user_id,
        previous_role_assignment_id=current.id,
        previous_role=current.role,
        role_assignment_id=uuid.uuid4(),
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
    "ChangeMemberRolePayload",
    "GovernanceRootNotRemovable",
    "MembershipNotFound",
    "RevokeMembershipPayload",
    "RoleUnchanged",
    "add_member",
    "change_member_role",
    "revoke_membership",
]
