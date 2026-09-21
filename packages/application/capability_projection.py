"""CapabilityProjection: "authenticate -> see accessible Workspaces ->
establish or enter legitimate Workspace context -> hold membership ->
receive/revoke governed rights -> see actual available capabilities"
(F01 WU-01.7) — the last step of that 19 §21 HUMAN PRODUCT EFFECT
chain, and its own explicit FRONTEND REQUIREMENTS line: "Render
separately: authenticated / member / authorized / governance-capable /
non-proof demo state".

WHAT THIS FILE DOES AND DOES NOT DO
--------------------------------------------------------------------
"authenticated" and "member" are already proven by the caller simply
POSSESSING a real `application.workspace_context.WorkspaceContext` —
`resolve_workspace_context` (F01 WU-01.3) cannot be constructed without
a real `AuthenticatedPrincipal` and a real, current ACTIVE membership,
and `WorkspaceContext.__post_init__` enforces this at runtime, not
merely via a type hint. This module therefore takes an
ALREADY-RESOLVED `WorkspaceContext` as its one required input — it
never re-derives, re-checks, or could be tricked into skipping either
of those two facts.

`project_capabilities` below closes the remaining two: "authorized"
(does this principal currently hold ANY ACTIVE HumanAuthorityBinding
in this Workspace at all) and "governance-capable" (does one of those
bindings specifically carry `WORKSPACE_GOVERNANCE_RIGHT`). Both are
raw projections of `AuthorityBindingRepository.list_current_bindings`
— never a re-implementation of `authority.resolver.AuthorityResolver`
(14 §16 non-collapse: authority resolution is that module's one job).
Reading `list_current_bindings` directly here — rather than calling
`AuthorityResolver.resolve()` once per candidate `AuthorityClass` — is
architecturally sound specifically BECAUSE the caller already holds a
genuine `WorkspaceContext`: that same module's own docstring warns
`list_current_bindings` does not itself cross-check membership
effectiveness (05 AC-05-004), but `WorkspaceContext` has ALREADY proven
ACTIVE membership before this function is ever called — the
effectiveness gap that warning describes is closed by construction
here, not ignored.

"non-proof demo state" (19 §21's own fifth rendering category) is
explicitly OUT OF SCOPE: no schema column or repository fact exists
anywhere in this codebase marking a `workspaces` row as
fixture-sourced versus legitimately founded (F01 WU-01.4's own Option
A resolution makes every NEW Workspace legitimate by construction; a
`NonProofWorkspaceBootstrap`-seeded demo Workspace is distinguishable
only by how it was created, a fact this repository does not persist).
Inventing such a marker now, with no textual mandate, would be exactly
the kind of undirected new capability 19 §2/§4 forbid — disclosed here
as a real, known gap for whoever builds the demo/production
distinction a later Field may need, not silently faked.

`role` (from `MembershipRepository.get_current_role`) is exposed
alongside the two boolean capability fields for frontend display, but
is never itself treated as, or substituted for, a capability —
`governance_capable`/`authorized` are always computed from the real
`HumanAuthorityBinding` facts alone (19 §21 BACKEND REQUIREMENTS: "No:
... role = right", the identical non-collapse rule
`membership_operations_handler.add_member` already established for the
write side).
"""

from __future__ import annotations

from dataclasses import dataclass

from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole
from persistence.authority_binding_repository import AuthorityBindingRepository
from persistence.membership_repository import MembershipRepository

from application.workspace_context import WorkspaceContext


@dataclass(frozen=True, slots=True)
class CapabilityProjection:
    """A pure projection of already-proven facts (`WorkspaceContext`'s
    own membership, plus the real, currently-ACTIVE
    `HumanAuthorityBinding` rows for the same principal/Workspace) —
    never itself a source of new authority. Constructible only through
    `project_capabilities` below.
    """

    role: WorkspaceRole
    held_authority_classes: frozenset[AuthorityClass]
    authorized: bool
    governance_capable: bool


def project_capabilities(
    context: WorkspaceContext,
    *,
    membership_repository: MembershipRepository,
    authority_binding_repository: AuthorityBindingRepository,
) -> CapabilityProjection:
    """Project `context.principal`'s currently-available capabilities
    in `context.workspace`. `context` must be a genuine
    `WorkspaceContext` (see module docstring for why this alone already
    proves "authenticated" and "member") — this function performs no
    further identity or membership verification of its own.
    """
    role_assignment = membership_repository.get_current_role(context.membership.id)
    assert role_assignment is not None  # 05 GOV-004: exactly one current role per ACTIVE membership

    bindings = authority_binding_repository.list_current_bindings(
        context.workspace.id, context.principal.user_id
    )
    held_authority_classes = frozenset(binding.authority_class for binding in bindings)

    return CapabilityProjection(
        role=role_assignment.role,
        held_authority_classes=held_authority_classes,
        authorized=bool(held_authority_classes),
        governance_capable=AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT in held_authority_classes,
    )


__all__ = ["CapabilityProjection", "project_capabilities"]
