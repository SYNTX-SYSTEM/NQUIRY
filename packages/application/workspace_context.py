"""Request Workspace context.

Source: 14_IMPLEMENTATION_SEQUENCE.md PKG-01 manifest OBJECTIVE
("request Workspace context") and 11_SECURITY_PRIVACY_OBSERVABILITY.md
§7 (Identity to Workspace Resolution):

    AUTHENTICATED USER
    + REQUESTED WORKSPACE
    + CURRENT WorkspaceMembership
    + TARGET OBJECT WORKSPACE
    -> CONSISTENT WORKSPACE CONTEXT

PKG-01 SCOPE NOTE: `WorkspaceMembership` does not exist yet
(`workspace_memberships` is migration 002, PKG-02 scope). This module
therefore resolves only "AUTHENTICATED USER + REQUESTED WORKSPACE ->
proven-to-exist Workspace" — the membership-consistency half of 11 §7
is NOT checked here. That is a disclosed scope boundary, not a hidden
one: `WorkspaceContext` must not be read as "this user may act in this
Workspace" until a later package adds the membership check. PKG-01's
own prompt confirms this split: "BOUNDARIES: Prepare inputs for
BND-001 and BND-002, do not implement later boundary behavior."
"""

from __future__ import annotations

from dataclasses import dataclass

from persistence.workspace_repository import WorkspaceRecord, WorkspaceRepository
from security.identity import AuthenticatedPrincipal
from semantic_types.ids import WorkspaceId


class WorkspaceNotFoundError(LookupError):
    """Raised when the requested WorkspaceId resolves to no canonical Workspace.

    14 non-collapse: unknown/conflicting Workspace scope fails closed
    (11 §11 AC-11-004: "Unknown, missing or conflicting Workspace
    scope: DENY. No best-effort cross-Workspace fallback exists.").
    This is preparation for that DENY, not the DENY itself — no
    Boundary evaluator exists yet in this package.
    """

    def __init__(self, workspace_id: WorkspaceId) -> None:
        super().__init__(f"no canonical Workspace found for {workspace_id}")
        self.workspace_id = workspace_id


@dataclass(frozen=True, slots=True)
class WorkspaceContext:
    """A request's resolved actor + proven Workspace.

    Constructible only through `resolve_workspace_context` below: the
    `workspace` field requires a genuine `WorkspaceRecord`, not a bare
    `WorkspaceId` — you cannot forge a `WorkspaceContext` for a
    Workspace that was never actually read from canonical storage
    (mandatory adversarial test: "forged Workspace context").
    """

    principal: AuthenticatedPrincipal
    workspace: WorkspaceRecord

    def __post_init__(self) -> None:
        # Runtime enforcement, not just a type hint: a caller ignoring
        # static types (or constructing this directly instead of going
        # through `resolve_workspace_context`) still cannot forge a
        # context from a bare WorkspaceId or any other non-proof value.
        if not isinstance(self.workspace, WorkspaceRecord):
            raise TypeError(
                f"WorkspaceContext.workspace requires a genuine WorkspaceRecord, "
                f"got {type(self.workspace).__name__}"
            )
        if not isinstance(self.principal, AuthenticatedPrincipal):
            raise TypeError(
                f"WorkspaceContext.principal requires an AuthenticatedPrincipal, "
                f"got {type(self.principal).__name__}"
            )


def resolve_workspace_context(
    principal: AuthenticatedPrincipal,
    requested_workspace_id: WorkspaceId,
    workspace_repository: WorkspaceRepository,
) -> WorkspaceContext:
    """Resolve `requested_workspace_id` against canonical storage and
    pair it with `principal`.

    Raises `WorkspaceNotFoundError` if the Workspace does not exist —
    fails closed, never returns a context for an unproven Workspace.
    """
    workspace = workspace_repository.get(requested_workspace_id)
    if workspace is None:
        raise WorkspaceNotFoundError(requested_workspace_id)
    return WorkspaceContext(principal=principal, workspace=workspace)


__all__ = ["WorkspaceContext", "WorkspaceNotFoundError", "resolve_workspace_context"]
