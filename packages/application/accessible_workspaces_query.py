"""ListAccessibleWorkspaces: the read-only "which Workspaces can I see"
Query (F01 WU-01.2, closing 19 §21's own disclosed CURRENT FIELD gap:
"Workspace discovery -> incomplete"; the "authenticate -> see
accessible Workspaces" step of that Field's own HUMAN PRODUCT EFFECT
list).

WHY ONLY BND-001 (IDENTITY), NOT BND-002/003 TOO
--------------------------------------------------------------------
`session_view_query.GetSession` (Architecture 17) established the
minimal read-side boundary chain for a Query that already targets one
specific Workspace: BND-001 (identity) + BND-002 (Workspace exists) +
BND-003 (current membership in THAT Workspace) -- see its own
docstring for the full reasoning on why a Query stops there and never
reaches BND-004+.

This Query is structurally different: there is no single target
Workspace to check BND-002/003 against -- discovering which Workspaces
the actor may see is the whole point, exactly the same reason
`workspace_creation_handler.create_workspace` found BND-002/003
inapplicable to a Workspace that does not yet exist (there, the target
was too new; here, there is no one target at all). BND-001 alone
(identity plausibility) is therefore the complete, non-invented
boundary chain for this Query -- reusing BND-002/003 here would mean
picking an arbitrary single Workspace to check them against, which
this Query has no textual mandate to do.

WHY THIS RETURNS RAW `WorkspaceRecord`s, NOT A NEW VIEW TYPE
--------------------------------------------------------------------
09/14 name no dedicated "AccessibleWorkspace" projection type for this
Query, and `WorkspaceRecord` (`persistence.workspace_repository`)
already carries everything 19 §21's own FRONTEND REQUIREMENTS line
needs at this layer ("Render separately: authenticated / member /
authorized / governance-capable / non-proof demo state" is a frontend
rendering concern, built from this Query's plain result plus a
separate per-Workspace context call -- not something this Query must
itself encode).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from persistence.membership_repository import MembershipRepository
from persistence.workspace_repository import WorkspaceRecord, WorkspaceRepository
from semantic_types.ids import CorrelationId, WorkspaceId


class AccessibleWorkspacesDenied(Exception):
    """BND-001 denied the actor. Fails closed -- no repository is ever
    queried on this path."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


def list_accessible_workspaces(
    actor: ActorIdentity,
    *,
    correlation_id: CorrelationId,
    occurred_at: datetime,
    membership_repository: MembershipRepository,
    workspace_repository: WorkspaceRepository,
) -> tuple[WorkspaceRecord, ...]:
    """Every Workspace `actor` currently holds ACTIVE membership in,
    oldest membership first. Raises `AccessibleWorkspacesDenied` if
    BND-001 denies. Returns an empty tuple (never denies) for a real,
    verified human with zero memberships -- "no accessible Workspaces
    yet" is a legitimate, non-adversarial state, not a denial."""
    # `workspace_id` is required by `BoundaryContext` (06 §4's shared
    # request-context shape) but there is no single target Workspace
    # for this Query -- a fresh, never-persisted placeholder is used
    # purely for audit-trail shape; BND-001 never reads it (see
    # `Bnd001IdentityEvaluator.evaluate`, which only inspects
    # `context.actor.actor_class`).
    placeholder_workspace_id = WorkspaceId(uuid.uuid4())
    context = BoundaryContext(
        workspace_id=placeholder_workspace_id,
        operation="ListAccessibleWorkspaces",
        actor=actor,
        correlation_id=correlation_id,
        evaluated_at=occurred_at,
    )
    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
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
        raise AccessibleWorkspacesDenied(
            terminal.reason_code if terminal is not None else "BND_001_DENIED"
        )

    memberships = membership_repository.list_active_memberships_for_user(actor.user_id)
    workspaces: list[WorkspaceRecord] = []
    for membership in memberships:
        record = workspace_repository.get(membership.workspace_id)
        assert record is not None  # workspace_memberships.workspace_id FK is ondelete=RESTRICT
        workspaces.append(record)
    return tuple(workspaces)


__all__ = ["AccessibleWorkspacesDenied", "list_accessible_workspaces"]
