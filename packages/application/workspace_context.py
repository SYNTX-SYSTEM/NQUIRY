"""Request Workspace context.

Source: 14_IMPLEMENTATION_SEQUENCE.md PKG-01 manifest OBJECTIVE
("request Workspace context") and 11_SECURITY_PRIVACY_OBSERVABILITY.md
§7 (Identity to Workspace Resolution):

    AUTHENTICATED USER
    + REQUESTED WORKSPACE
    + CURRENT WorkspaceMembership
    + TARGET OBJECT WORKSPACE
    -> CONSISTENT WORKSPACE CONTEXT

PKG-01 SCOPE NOTE, CLOSED AT F01 WU-01.3: `WorkspaceMembership` did not
exist yet at PKG-01 (`workspace_memberships` was migration 002, PKG-02
scope), so this module originally resolved only "AUTHENTICATED USER +
REQUESTED WORKSPACE -> proven-to-exist Workspace" — the
membership-consistency half of 11 §7 was NOT checked, a disclosed scope
boundary, not a hidden one. `MembershipRepository` is now real (PKG-02),
so `resolve_workspace_context` below completes 11 §7's full formula:
"AUTHENTICATED USER + REQUESTED WORKSPACE + CURRENT WorkspaceMembership
+ TARGET OBJECT WORKSPACE -> CONSISTENT WORKSPACE CONTEXT". A
`WorkspaceContext` now proves both facts at once — a Workspace exists
AND the principal currently holds ACTIVE membership in it — never one
without the other; see `NotAWorkspaceMemberError` below for the second
half's own mandatory adversarial attack ("cross-Workspace isolation",
19 §21 TESTS FIRST).
"""

from __future__ import annotations

from dataclasses import dataclass

from persistence.membership_repository import MembershipRecord, MembershipRepository
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


class NotAWorkspaceMemberError(LookupError):
    """Raised when the requested Workspace exists but `principal` holds
    no ACTIVE membership in it. Mandatory adversarial attack:
    "cross-Workspace isolation" (19 §21 TESTS FIRST) — a real Workspace
    existing is never sufficient to resolve a context for a principal
    who is not a member of it (11 §11 AC-11-004, same fail-closed
    posture as `WorkspaceNotFoundError`)."""

    def __init__(self, workspace_id: WorkspaceId) -> None:
        super().__init__(f"no ACTIVE membership found for {workspace_id}")
        self.workspace_id = workspace_id


@dataclass(frozen=True, slots=True)
class WorkspaceContext:
    """A request's resolved actor + proven Workspace + proven current
    membership.

    Constructible only through `resolve_workspace_context` below: the
    `workspace`/`membership` fields require a genuine `WorkspaceRecord`/
    `MembershipRecord`, not bare IDs — you cannot forge a
    `WorkspaceContext` for a Workspace or membership that was never
    actually read from canonical storage (mandatory adversarial test:
    "forged Workspace context").
    """

    principal: AuthenticatedPrincipal
    workspace: WorkspaceRecord
    membership: MembershipRecord

    def __post_init__(self) -> None:
        # Runtime enforcement, not just a type hint: a caller ignoring
        # static types (or constructing this directly instead of going
        # through `resolve_workspace_context`) still cannot forge a
        # context from a bare ID or any other non-proof value.
        if not isinstance(self.workspace, WorkspaceRecord):
            raise TypeError(
                f"WorkspaceContext.workspace requires a genuine WorkspaceRecord, "
                f"got {type(self.workspace).__name__}"
            )
        if not isinstance(self.membership, MembershipRecord):
            raise TypeError(
                f"WorkspaceContext.membership requires a genuine MembershipRecord, "
                f"got {type(self.membership).__name__}"
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
    membership_repository: MembershipRepository,
) -> WorkspaceContext:
    """Resolve `requested_workspace_id` against canonical storage,
    confirm `principal` currently holds ACTIVE membership in it, and
    pair both proofs with `principal`.

    Raises `WorkspaceNotFoundError` if the Workspace does not exist, or
    `NotAWorkspaceMemberError` if it exists but `principal` is not a
    current member — fails closed either way, never returns a context
    for an unproven Workspace or an unproven membership.
    """
    workspace = workspace_repository.get(requested_workspace_id)
    if workspace is None:
        raise WorkspaceNotFoundError(requested_workspace_id)
    membership = membership_repository.get_current_membership(
        requested_workspace_id, principal.user_id
    )
    if membership is None:
        raise NotAWorkspaceMemberError(requested_workspace_id)
    return WorkspaceContext(principal=principal, workspace=workspace, membership=membership)


__all__ = [
    "WorkspaceContext",
    "WorkspaceNotFoundError",
    "NotAWorkspaceMemberError",
    "resolve_workspace_context",
]
