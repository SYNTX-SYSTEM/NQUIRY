"""RevokeHumanAuthorityBinding: the real, governed "Workspace governance
root revokes a HumanAuthorityBinding" Command (F01 WU-01.6).

Source: `packages/persistence/authority_binding_repository.py`'s own
`grant()` docstring named exactly this scope ("revocation remains a
later Field's scope (F01 WU-01.6)"); `docs/architecture/
05_GOVERNANCE_INSIDE_SYSTEM.md` §8 (HABB Lifecycle: "ACTIVE, REVOKED
... REVOKED is terminal for that binding record") and its own
"Workspace governance root administers membership and role
assignments" closure (GAP-04-014) — the identical closure WU-01.5's
`AddMember` already materializes for membership; this Command is the
same closure for authority bindings. The Grant half of GAP-04-014
("... revoke role") is not built here either: `AddMember` already
grants a *Membership role*; this file only revokes a *HumanAuthorityBinding*
(a distinct row/lifecycle, 04 §6 vs. 05 §5) — the corresponding
"revoke role" (Membership-role administration, not authority-binding
administration) remains `SUCCESSOR_NOT_BUILT`, matching WU-01.5's own
disclosed scope boundary.

SAME PATTERN AS `membership_operations_handler.add_member` (BOTH USE
`CommitCoordinator` DIRECTLY, NOT `workspace_creation_handler`'s
hand-rolled path)
--------------------------------------------------------------------
The actor calling `revoke_human_authority_binding` already holds
`WORKSPACE_GOVERNANCE_RIGHT` over an ALREADY-EXISTING Workspace (no
circularity, unlike `CreateWorkspace`) — the identical BND-001..005
precommit chain + `CommitCoordinator.commit()` shape every other
full-chain Command in this codebase already uses.

WHY THE WORKSPACE'S OWN `WORKSPACE_GOVERNANCE_RIGHT` BINDING CAN NEVER
BE REVOKED THROUGH THIS COMMAND
--------------------------------------------------------------------
Exactly one `WORKSPACE_GOVERNANCE_RIGHT` binding exists per Workspace
today (`workspace_creation_handler.create_workspace`'s own founder
self-grant; `AddMember` refuses to grant a second one). Revoking that
one binding would leave the Workspace with NO holder of
`WORKSPACE_GOVERNANCE_RIGHT` at all — permanently un-administrable
(no further `AddMember`, no further revoke, nothing), because every
governance operation's own BND-005 gate requires a currently-ACTIVE
`WORKSPACE_GOVERNANCE_RIGHT` binding to evaluate ALLOW in the first
place. This is `docs/architecture/05_GOVERNANCE_INSIDE_SYSTEM.md`'s
own `GAP-05-001` ("Workspace Root Creation and Succession... owner
transfer and succession remain undefined"), `[UNDERDEFINED]` — the
identical unresolved gap `AddMember` already cites for refusing to
grant a second `WORKSPACE_GOVERNANCE_RIGHT` binding
(`OwnerRoleNotAssignable`). This Command refuses outright
(`GovernanceRootOrphaningRefused`) rather than inventing a succession
mechanism — the same "STOP rather than invent" discipline this whole
Field has followed since HARD-DEP-001. This is NOT itself a new
HARD-DEP or a bootstrap decision: it is a structural safety guard
against an undefined state, checked BEFORE any boundary is evaluated,
mirroring `OwnerRoleNotAssignable`'s own placement exactly.

WHY A NON-EXISTENT `workspace_id` IS DENIED *BEFORE* `record_attempt`
--------------------------------------------------------------------
Same `commands.workspace_id` FK hazard WU-01.5 discovered and fixed
locally in `add_member` (see that module's own docstring) — mirrored
here identically: `workspace is None` is evaluated via BND-001/002
alone, before any `CommandEnvelope`/`record_attempt` call, so no
`commands` row is ever attempted for a Workspace that was never real.

WHY A NON-EXISTENT (OR CROSS-WORKSPACE) `binding_id` IS ITS OWN,
SEPARATE DENIAL -- `AuthorityBindingNotFound`, NOT `RevokeAuthorityBindingDenied`
--------------------------------------------------------------------
Unlike a Decision (`human_decision_handler`'s own BND-007 naturally
fails closed when `decision is None`, because that boundary input is
then never set at all), there is no existing state-transition boundary
evaluator for a HumanAuthorityBinding's own ACTIVE/REVOKED lifecycle.
The actor-side boundary chain (BND-001..005) only proves facts about
the ACTOR and the WORKSPACE — it can legitimately reach ALLOW even
when the caller-supplied `binding_id` does not exist at all, or
belongs to a different Workspace than claimed (`06 §8` BND-002 non-
collapse: "Claimed Workspace IDs are not authoritative by
themselves" — the identical principle applied here to a claimed
binding_id). `AuthorityBindingNotFound` is therefore raised as an
explicit, separate, "Workspace-scoped not-found" class (14 §35's own
error-contract vocabulary), distinct from an authority/boundary
`DENY` — checked immediately after the boundary chain ALLOWs, before
any commit is attempted, exactly analogous to `record_human_decision`'s
own defensive `assert decision is not None` after its chain passes.
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
from events.outbox import OutboxRepository
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import WorkspaceRole
from persistence.authority_binding_repository import (
    AuthorityBindingConflict,
    AuthorityBindingRepository,
    authority_binding_target_ref,
)
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

_PRECOMMIT_CHAIN = (
    BoundaryId.BND_001,
    BoundaryId.BND_002,
    BoundaryId.BND_003,
    BoundaryId.BND_004,
    BoundaryId.BND_005,
)

_MEMBERSHIP_ADMIN_ROLES = frozenset({WorkspaceRole.OWNER})


class GovernanceRootOrphaningRefused(ValueError):
    """Raised before any boundary is evaluated. See module docstring
    ("WHY THE WORKSPACE'S OWN `WORKSPACE_GOVERNANCE_RIGHT` BINDING CAN
    NEVER BE REVOKED THROUGH THIS COMMAND")."""

    def __init__(self) -> None:
        super().__init__(
            "the Workspace's own WORKSPACE_GOVERNANCE_RIGHT binding cannot be revoked "
            "via revoke_human_authority_binding; Workspace root succession is "
            "GAP-05-001, unresolved"
        )


class AuthorityBindingNotFound(Exception):
    """`binding_id` does not resolve to a real `human_authority_bindings`
    row belonging to `workspace_id`. Raised after the actor-side
    boundary chain ALLOWs (the actor's own rights are real) but before
    any commit is attempted — see module docstring."""


class RevokeAuthorityBindingDenied(Exception):
    """The PRECOMMIT boundary chain (BND-001..005) did not reach ALLOW.
    No binding row was ever mutated; `command_repository.record_outcome`
    already recorded `CommandOutcome.DENIED` before this is raised."""

    def __init__(self, chain_result: BoundaryChainResult) -> None:
        self.chain_result = chain_result
        super().__init__(chain_result.result.value)


@dataclass(frozen=True, slots=True)
class RevokeAuthorityBindingPayload:
    """The one concrete Command payload this Command introduces (09
    §9), mirroring `membership_operations_handler.AddMemberPayload`'s
    own precedent."""

    binding_id: str


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


class _RevokeAuthorityBindingMutation:
    """Wraps the real `AuthorityBindingRepository.revoke` for
    `RevokeHumanAuthorityBinding`. `AuthorityBindingConflict` (a
    genuine 0-row-affected guarded `UPDATE`) is translated to
    `StaleVersionConflict`, the vocabulary `CommitCoordinator` itself
    understands — mirrors `human_decision_handler._RecordDecisionMutation`'s
    own counterpart pattern exactly.
    """

    def __init__(
        self,
        repository: AuthorityBindingRepository,
        *,
        binding_id: AuthorityBindingId,
        expected_record_version: RecordVersion,
        revoked_by_user_id: UserId,
        revoked_at: datetime,
    ) -> None:
        self._repository = repository
        self._binding_id = binding_id
        self._expected_record_version = expected_record_version
        self._revoked_by_user_id = revoked_by_user_id
        self._revoked_at = revoked_at

    def apply(self) -> MutationOutcome:
        try:
            self._repository.revoke(
                self._binding_id,
                expected_record_version=self._expected_record_version,
                revoked_by_user_id=self._revoked_by_user_id,
                revoked_at=self._revoked_at,
            )
        except AuthorityBindingConflict as exc:
            raise StaleVersionConflict(str(exc)) from exc
        return MutationOutcome(
            state_before_ref=AuthorityBindingState.ACTIVE.value,
            state_after_ref=AuthorityBindingState.REVOKED.value,
        )


def revoke_human_authority_binding(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    binding_id: AuthorityBindingId,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    idempotency_key: str | None,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    authority_binding_repository: AuthorityBindingRepository,
    authority_resolver: AuthorityResolver,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    idempotency_port: IdempotencyPort,
    current_version_reader: CurrentVersionReader,
    failure_injector: FailureInjectionPort | None = None,
) -> CommitUnit:
    """Revoke `binding_id` in `workspace_id`. `actor` must currently
    hold `WORKSPACE_GOVERNANCE_RIGHT` for `workspace_id` (proven fresh
    by BND-005) AND currently be an `Owner`-role member of it (proven
    fresh by BND-004) — both checks, not either alone (04/06
    non-collapse), identical to `AddMember`'s own gate.

    Raises `GovernanceRootOrphaningRefused` before any boundary
    evaluation if `binding_id` is the Workspace's own, currently-ACTIVE
    `WORKSPACE_GOVERNANCE_RIGHT` binding. Raises
    `RevokeAuthorityBindingDenied` if the precommit chain does not
    reach ALLOW. Raises `AuthorityBindingNotFound` if `binding_id` does
    not resolve to a real, same-Workspace binding once the chain has
    ALLOWed.
    """
    workspace = workspace_repository.get(workspace_id)
    binding = authority_binding_repository.get_by_id(binding_id)
    binding_belongs = binding is not None and binding.workspace_id == workspace_id

    if (
        binding_belongs
        and binding is not None
        and binding.authority_class is AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT
        and binding.state is AuthorityBindingState.ACTIVE
    ):
        raise GovernanceRootOrphaningRefused()

    context = BoundaryContext(
        workspace_id=workspace_id,
        operation="RevokeHumanAuthorityBinding",
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
        # `workspaces.id` (`fk_commands_workspace`) -- a workspace_id
        # here may never resolve to a real row at all (a forged/
        # mistyped ID). `record_attempt` cannot be called for it --
        # deny via BND-001/002 directly, mirroring `AddMember`'s own
        # locally-fixed precheck (see module docstring).
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
        raise RevokeAuthorityBindingDenied(precheck_result)

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

    target_ref = authority_binding_target_ref(binding_id)
    envelope = CommandEnvelope(
        command_id=command_id,
        command_type="CMD_REVOKE_HUMAN_AUTHORITY_BINDING",
        command_contract_version=ContractVersion("1.0"),
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        requested_at=occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=(target_ref,),
        expected_versions={
            target_ref: binding.record_version
            if binding_belongs and binding is not None
            else RecordVersion.initial()
        },
        payload=RevokeAuthorityBindingPayload(binding_id=str(binding_id.value)),
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
        raise RevokeAuthorityBindingDenied(chain_result)

    bnd005_proof = _find_proof(chain_result.proofs, BoundaryId.BND_005)
    if bnd005_proof is None or bnd005_proof.authority_proof is None:
        # Defensive: BND-005 ALLOWed, so a granting binding was proven
        # to exist -- unreachable in practice, kept as a fail-closed
        # guard rather than proceeding without a real authority proof.
        raise RevokeAuthorityBindingDenied(chain_result)

    if not binding_belongs or binding is None:
        # The actor-side chain ALLOWed on real facts about the actor
        # and the Workspace, but `binding_id` itself does not name a
        # real, same-Workspace row -- see module docstring for why this
        # is a distinct denial class, checked here rather than folded
        # into the boundary chain above.
        raise AuthorityBindingNotFound(
            f"no ACTIVE-or-otherwise binding {binding_id!r} found in workspace {workspace_id!r}"
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
    mutation = _RevokeAuthorityBindingMutation(
        authority_binding_repository,
        binding_id=binding_id,
        expected_record_version=binding.record_version,
        revoked_by_user_id=actor.user_id,
        revoked_at=occurred_at,
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


class GovernanceRightNotGrantableViaGenericGrant(ValueError):
    """Raised before any boundary is evaluated.
    `WORKSPACE_GOVERNANCE_RIGHT` can only ever be granted once, via
    `workspace_creation_handler.create_workspace`'s own founder
    self-grant (WU-01.4b) — granting a SECOND one via this generic
    Command would be the identical GAP-05-001 succession question
    `AddMember`'s own `OwnerRoleNotAssignable` and
    `RevokeHumanAuthorityBinding`'s own `GovernanceRootOrphaningRefused`
    already refuse to touch, from the opposite direction. Refused
    outright — the same "STOP rather than invent" discipline, not a
    new HARD-DEP of this Command's own making."""

    def __init__(self) -> None:
        super().__init__(
            "WORKSPACE_GOVERNANCE_RIGHT cannot be granted via grant_human_authority_binding; "
            "it is granted exactly once, by create_workspace's own founder self-grant; "
            "Workspace root succession is GAP-05-001, unresolved"
        )


class GrantAuthorityBindingDenied(Exception):
    """The PRECOMMIT boundary chain (BND-001..005) did not reach ALLOW.
    No binding row was ever written; `command_repository.record_outcome`
    already recorded `CommandOutcome.DENIED` before this is raised."""

    def __init__(self, chain_result: BoundaryChainResult) -> None:
        self.chain_result = chain_result
        super().__init__(chain_result.result.value)


@dataclass(frozen=True, slots=True)
class GrantAuthorityBindingPayload:
    """The one concrete Command payload this Command introduces (09
    §9), mirroring `RevokeAuthorityBindingPayload`'s own precedent."""

    human_user_id: str
    authority_class: str
    scope_type: str
    scope_id: str


class _GrantAuthorityBindingMutation:
    """Wraps the real `AuthorityBindingRepository.grant` for
    `GrantHumanAuthorityBinding`. `grant()` is a plain insert (no
    version-guarded UPDATE, unlike `revoke()`) — mirrors
    `membership_operations_handler._AddMemberMutation`'s own shape,
    not `_RevokeAuthorityBindingMutation`'s own exception-translation
    one."""

    def __init__(
        self,
        repository: AuthorityBindingRepository,
        *,
        binding_id: AuthorityBindingId,
        workspace_id: WorkspaceId,
        human_user_id: UserId,
        authority_class: AuthorityClass,
        scope_type: str,
        scope_id: Any,
        granted_by_user_id: UserId,
        granted_at: datetime,
    ) -> None:
        self._repository = repository
        self._binding_id = binding_id
        self._workspace_id = workspace_id
        self._human_user_id = human_user_id
        self._authority_class = authority_class
        self._scope_type = scope_type
        self._scope_id = scope_id
        self._granted_by_user_id = granted_by_user_id
        self._granted_at = granted_at

    def apply(self) -> MutationOutcome:
        self._repository.grant(
            self._binding_id,
            workspace_id=self._workspace_id,
            human_user_id=self._human_user_id,
            authority_class=self._authority_class,
            scope_type=self._scope_type,
            scope_id=self._scope_id,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=self._granted_by_user_id,
            granted_at=self._granted_at,
        )
        return MutationOutcome(
            state_before_ref=None,
            state_after_ref=AuthorityBindingState.ACTIVE.value,
        )


class GrantScopeInvalid(ValueError):
    """The requested binding scope does not name a record of this Workspace."""


_GRANTABLE_SCOPE_TYPES = frozenset({"WORKSPACE", "CHALLENGE", "SESSION", "DECISION"})


def _require_scope_in_workspace(
    connection: Any, workspace_id: WorkspaceId, scope_type: str, scope_id: Any
) -> None:
    from persistence.challenge_repository import SqlAlchemyChallengeRepository
    from persistence.decision_repository import SqlAlchemyDecisionRepository
    from persistence.session_repository import SqlAlchemySessionRepository
    from semantic_types.ids import ChallengeId, DecisionId, SessionId

    if scope_type not in _GRANTABLE_SCOPE_TYPES:
        raise GrantScopeInvalid(f"SCOPE_TYPE_NOT_GRANTABLE:{scope_type}")
    try:
        sid = scope_id if isinstance(scope_id, uuid.UUID) else uuid.UUID(str(scope_id))
    except ValueError as exc:
        raise GrantScopeInvalid("SCOPE_ID_MALFORMED") from exc
    owner: WorkspaceId | None
    if scope_type == "WORKSPACE":
        owner = workspace_id if sid == workspace_id.value else None
    elif scope_type == "CHALLENGE":
        challenge = SqlAlchemyChallengeRepository(connection).get(ChallengeId(sid))
        owner = challenge.workspace_id if challenge is not None else None
    elif scope_type == "SESSION":
        session = SqlAlchemySessionRepository(connection).get(SessionId(sid))
        owner = session.workspace_id if session is not None else None
    else:
        decision = SqlAlchemyDecisionRepository(connection).get(DecisionId(sid))
        owner = decision.workspace_id if decision is not None else None
    if owner != workspace_id:
        raise GrantScopeInvalid(f"SCOPE_NOT_IN_WORKSPACE:{scope_type}")


def grant_human_authority_binding(
    connection: Any,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    human_user_id: UserId,
    authority_class: AuthorityClass,
    scope_type: str,
    scope_id: Any,
    command_id: CommandId,
    attempt_id: AttemptId,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    commit_id: CommitId,
    idempotency_key: str | None,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
    authority_binding_repository: AuthorityBindingRepository,
    authority_resolver: AuthorityResolver,
    command_repository: CommandRepository,
    audit_repository: AuditRepository,
    outbox_repository: OutboxRepository,
    commit_repository: CommitRepository,
    idempotency_port: IdempotencyPort,
    current_version_reader: CurrentVersionReader,
    failure_injector: FailureInjectionPort | None = None,
) -> CommitUnit:
    """Grant a new, ACTIVE `HumanAuthorityBinding` for `human_user_id`
    in `workspace_id`. `actor` must currently hold
    `WORKSPACE_GOVERNANCE_RIGHT` for `workspace_id` (proven fresh by
    BND-005) AND currently be an `Owner`-role member of it (proven
    fresh by BND-004) — identical gate to `AddMember`/
    `RevokeHumanAuthorityBinding`.

    Raises `GovernanceRightNotGrantableViaGenericGrant` before any
    boundary evaluation if `authority_class` is
    `WORKSPACE_GOVERNANCE_RIGHT`. Raises `GrantAuthorityBindingDenied`
    if the precommit chain does not reach ALLOW. `human_user_id` must
    already hold ACTIVE membership in `workspace_id` — enforced by the
    real `trg_habb_check_grant_preconditions` DB trigger (05 GOV-005),
    surfacing as `CommitFailedPrecommit` if violated, the same "checked
    at two independent layers" discipline every prior mutation in this
    codebase relies on.
    """
    if authority_class is AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT:
        raise GovernanceRightNotGrantableViaGenericGrant()

    workspace = workspace_repository.get(workspace_id)

    context = BoundaryContext(
        workspace_id=workspace_id,
        operation="GrantHumanAuthorityBinding",
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
        # `workspaces.id` (`fk_commands_workspace`) — mirrors
        # `AddMember`/`RevokeHumanAuthorityBinding`'s own locally-fixed
        # precheck (see module docstring on both).
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
        raise GrantAuthorityBindingDenied(precheck_result)

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

    # F02 WU-02.7: a binding's scope must name a real record of THIS
    # Workspace (05: "Session belongs to same Workspace"). A grant for a
    # nonexistent or foreign scope is invalid input (REJECTED), not an
    # authority question, so it is refused before any attempt is recorded.
    _require_scope_in_workspace(connection, workspace_id, scope_type, scope_id)

    binding_id = AuthorityBindingId(uuid.uuid4())
    # Unlike `RevokeHumanAuthorityBinding` (which mutates an EXISTING
    # binding row and therefore versions against that row itself), this
    # Command creates a brand-new row with no prior state to protect
    # against staleness -- the optimistic-concurrency target is the
    # WORKSPACE, mirroring `AddMember`'s own identical choice exactly
    # (both Commands write new rows UNDER an already-existing
    # Workspace, versioned against that Workspace, not against the new
    # rows themselves).
    target_ref = workspace_target_ref(workspace_id)
    envelope = CommandEnvelope(
        command_id=command_id,
        command_type="CMD_GRANT_HUMAN_AUTHORITY_BINDING",
        command_contract_version=ContractVersion("1.0"),
        attempt_id=attempt_id,
        correlation_id=correlation_id,
        requested_at=occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=(target_ref,),
        expected_versions={target_ref: workspace.record_version},
        payload=GrantAuthorityBindingPayload(
            human_user_id=str(human_user_id.value),
            authority_class=authority_class.value,
            scope_type=scope_type,
            scope_id=str(scope_id),
        ),
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
        raise GrantAuthorityBindingDenied(chain_result)

    bnd005_proof = _find_proof(chain_result.proofs, BoundaryId.BND_005)
    if bnd005_proof is None or bnd005_proof.authority_proof is None:
        # Defensive: BND-005 ALLOWed, so a granting binding was proven
        # to exist -- unreachable in practice, kept as a fail-closed
        # guard rather than proceeding without a real authority proof.
        raise GrantAuthorityBindingDenied(chain_result)

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
    mutation = _GrantAuthorityBindingMutation(
        authority_binding_repository,
        binding_id=binding_id,
        workspace_id=workspace_id,
        human_user_id=human_user_id,
        authority_class=authority_class,
        scope_type=scope_type,
        scope_id=scope_id,
        granted_by_user_id=actor.user_id,
        granted_at=occurred_at,
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
    "GrantScopeInvalid",
    "GovernanceRootOrphaningRefused",
    "AuthorityBindingNotFound",
    "RevokeAuthorityBindingDenied",
    "RevokeAuthorityBindingPayload",
    "revoke_human_authority_binding",
    "GovernanceRightNotGrantableViaGenericGrant",
    "GrantAuthorityBindingDenied",
    "GrantAuthorityBindingPayload",
    "grant_human_authority_binding",
]
