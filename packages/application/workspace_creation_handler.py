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

F02 WU-02.6 (HD-6): FOUNDING THROUGH THE SINGLE EFFECT GATE
--------------------------------------------------------------------
Until F02 this Command hand-rolled its own SAVEPOINT because
`CommitCoordinator.commit()` could only express BINDING authority, and a
founder cannot already hold the `WORKSPACE_GOVERNANCE_RIGHT` it is about
to create. The operator's HD-6 decision (16 §41 REC-004) rejected the
parallel writer as permanent architecture. The effect gate now carries a
typed FOUNDING authority source (`boundaries.authority_source.
FoundingAuthority`, HARD-DEP-001 Option A):

- BND-001 (verified human) and the replaceable eligibility check run
  first, unchanged;
- `CommitCoordinator` runs BND-014 with FOUNDING authority. The audit
  row's `authority_source_type` is FOUNDING, and its ref is this
  Command's own `commands.id`. The binding the founding CREATES is
  recorded as a governance ref of the CommitUnit, never as its own
  authority source. The pre-F02 audit ref pointed at that binding, which
  was circular;
- the Workspace is a created ref (`CommandEnvelope.created_refs`), not a
  version-checked target.

Why `record_attempt` runs inside the SAVEPOINT: `commands.workspace_id`
carries a non-deferrable FK to `workspaces.id` (`fk_commands_workspace`).
For THIS Command that Workspace exists only once the mutation has run.
The coordinator therefore records the attempt right after
`mutation.apply()`, inside the same SAVEPOINT, for FOUNDING only.
Disclosed consequence (unchanged since F01 WU-01.4b): a FAILED founding
leaves no `commands` row at all, because the FK correctly refuses an
operational record for a canonical record that never came into being.

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

from audit.models import AuditRepository
from authority.actor import ActorClass, ActorIdentity
from boundaries.authority_source import FoundingAuthority
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_014_commit import Bnd014CommitEvaluator
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from command.envelope import CommandEnvelope
from commit.coordinator import CommitCoordinator, CommitRepository, MutationOutcome
from commit.idempotency import IdempotencyRecord
from events.contracts import EventFacts
from events.outbox import OutboxRepository
from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole
from persistence.authority_binding_repository import AuthorityBindingRepository
from persistence.command_repository import CommandRepository
from persistence.membership_repository import MembershipRepository
from persistence.workspace_repository import WorkspaceRepository, workspace_target_ref
from semantic_types.ids import (
    AttemptId,
    AuthorityBindingId,
    CommandId,
    CommitId,
    CorrelationId,
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


class _FoundWorkspaceMutation:
    """The founding bundle: Workspace + owner root + ACTIVE membership +
    Owner role + WORKSPACE_GOVERNANCE_RIGHT binding, as one mutation
    inside the coordinator's SAVEPOINT."""

    def __init__(
        self,
        *,
        workspace_repository: WorkspaceRepository,
        membership_repository: MembershipRepository,
        authority_binding_repository: AuthorityBindingRepository,
        workspace_id: WorkspaceId,
        workspace_name: str,
        owner_user_id: UserId,
        membership_id: uuid.UUID,
        governance_binding_id: AuthorityBindingId,
        occurred_at: datetime,
    ) -> None:
        self._workspaces = workspace_repository
        self._memberships = membership_repository
        self._bindings = authority_binding_repository
        self._workspace_id = workspace_id
        self._name = workspace_name
        self._owner = owner_user_id
        self._membership_id = membership_id
        self._binding_id = governance_binding_id
        self._at = occurred_at

    def apply(self) -> MutationOutcome:
        self._workspaces.create(
            self._workspace_id, name=self._name, owner_id=self._owner, created_at=self._at
        )
        self._memberships.create_membership(
            self._membership_id,
            workspace_id=self._workspace_id,
            user_id=self._owner,
            created_at=self._at,
        )
        self._memberships.assign_role(
            uuid.uuid4(),
            workspace_id=self._workspace_id,
            membership_id=self._membership_id,
            role=WorkspaceRole.OWNER,
            granted_by_user_id=self._owner,
            granted_at=self._at,
        )
        self._bindings.grant(
            self._binding_id,
            workspace_id=self._workspace_id,
            human_user_id=self._owner,
            authority_class=AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT,
            scope_type="WORKSPACE",
            scope_id=self._workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=self._owner,
            granted_at=self._at,
        )
        return MutationOutcome(
            state_before_ref=None,
            state_after_ref=f"workspace:{self._workspace_id.value}",
            governance_refs=(f"authority_binding:{self._binding_id.value}",),
            event_type="WORKSPACE_CREATED",
            result_ref=str(self._workspace_id.value),
            event=EventFacts(
                aggregate_ref=f"workspace:{self._workspace_id.value}",
                payload={
                    "workspace_id": str(self._workspace_id.value),
                    "owner_user_id": str(self._owner.value),
                    "governance_binding_id": str(self._binding_id.value),
                },
            ),
        )


class _NoTargetsReader:
    """Founding has no pre-existing target to version-check."""

    def read(self, target_ref: str) -> RecordVersion | None:
        raise AssertionError(f"founding has no version-checked targets, asked for {target_ref!r}")


class _NoIdempotencyForFounding:
    """Founding carries no idempotency key at this layer: an
    `idempotency_records` row is keyed by (and FK-bound to) a Workspace
    that does not exist before the founding commit. Any call is a wiring
    error."""

    def begin(self, envelope: CommandEnvelope, *, seen_at: datetime) -> IdempotencyRecord:
        raise AssertionError("founding does not use the idempotency port")

    def get(
        self, *, workspace_id: WorkspaceId, command_type: str, idempotency_key: str
    ) -> IdempotencyRecord | None:
        raise AssertionError("founding does not use the idempotency port")

    def mark_committed(
        self,
        *,
        workspace_id: WorkspaceId,
        command_type: str,
        idempotency_key: str,
        commit_id: CommitId,
        result_ref: str | None,
    ) -> None:
        raise AssertionError("founding does not use the idempotency port")

    def mark_failed_precommit(
        self, *, workspace_id: WorkspaceId, command_type: str, idempotency_key: str
    ) -> None:
        raise AssertionError("founding does not use the idempotency port")

    def mark_indeterminate(
        self, *, workspace_id: WorkspaceId, command_type: str, idempotency_key: str
    ) -> None:
        raise AssertionError("founding does not use the idempotency port")


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
        # F02 HD-6: the Workspace is CREATED by this Command -- a created
        # ref, not a version-checked target (it has no prior version).
        target_refs=(),
        expected_versions={},
        created_refs=(target_ref,),
        payload=CreateWorkspacePayload(workspace_name=workspace_name),
    )

    owner_user_id = actor.user_id
    membership_id = uuid.uuid4()
    governance_binding_id = AuthorityBindingId(uuid.uuid4())

    mutation = _FoundWorkspaceMutation(
        workspace_repository=workspace_repository,
        membership_repository=membership_repository,
        authority_binding_repository=authority_binding_repository,
        workspace_id=workspace_id,
        workspace_name=workspace_name,
        owner_user_id=owner_user_id,
        membership_id=membership_id,
        governance_binding_id=governance_binding_id,
        occurred_at=occurred_at,
    )
    # F02 HD-6: founding is admitted by the single effect gate with a
    # FOUNDING authority source (HARD-DEP-001 Option A). The coordinator
    # records the command attempt INSIDE the same SAVEPOINT, after the
    # Workspace row exists (`fk_commands_workspace`); a failed founding
    # leaves no row at all.
    coordinator = CommitCoordinator(
        connection,
        bnd014_evaluator=Bnd014CommitEvaluator(None),
        command_repository=command_repository,
        audit_repository=audit_repository,
        outbox_repository=outbox_repository,
        commit_repository=commit_repository,
        idempotency_port=_NoIdempotencyForFounding(),
    )
    coordinator.commit(
        envelope=envelope,
        actor=actor,
        authority=FoundingAuthority(eligibility_reason_code=eligibility.reason_code),
        upstream_chain_result=chain_result.result,
        current_version_reader=_NoTargetsReader(),
        mutation=mutation,
        occurred_at=occurred_at,
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
