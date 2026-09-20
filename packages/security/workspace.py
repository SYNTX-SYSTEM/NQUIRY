"""Workspace RLS context: the "trusted server adapter" port.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 8's own
`[IMPLEMENTATION CHOICE]`: "PostgreSQL RLS is enabled for Workspace-keyed
protected tables using transaction-local Workspace context set only by
trusted server adapter. RLS is defense-in-depth and is never used as
the authority oracle."; 11_SECURITY_PRIVACY_OBSERVABILITY.md section 11
(AC-11-004, Workspace Isolation Law), section 15 ("Canonical Database
Privilege Architecture" -- "Database-level permission is a necessary
infrastructure capability for the approved path. It is never sufficient
legitimacy").

WHY THIS FILE IS A PORT ONLY, NEVER THE CONCRETE ADAPTER
--------------------------------------------------------------------
14 section 3.1 gives `security` exactly one allowed dependency:
`semantic_types` -- not `persistence`, not `sqlalchemy`. The concrete
adapter that actually issues `SELECT set_config(...)` against a real
connection lives in `persistence.workspace_rls_context` (this
package's own disclosed `persistence -> security` extension, the same
one-directional pattern `persistence -> audit`/`persistence -> command`
already established).

WHY "RLS SUCCESS NEVER GRANTS DOMAIN AUTHORITY" (THIS PACKAGE'S OWN
AUTHORITY LINE) IS A STRUCTURAL FACT, NOT A RUNTIME PROMISE
--------------------------------------------------------------------
`set_workspace_context`/`clear_workspace_context` below return `None`
and raise on failure -- there is no method anywhere on this Protocol
that could hand back an authority token, a BoundaryProof, or any
authorization-shaped value. Calling this port successfully proves only
that a session-local Postgres setting was changed; it says nothing
about whether the caller genuinely belongs to that Workspace. That
verification remains BND-002/003's own job (06 section 8), performed
BEFORE this adapter is ever called with a workspace_id, never by this
adapter itself.

WHY THIS IS EXPLICITLY DISCLOSED AS A DEFENSE-IN-DEPTH LAYER, NOT A
REPLACEMENT FOR BND-002
--------------------------------------------------------------------
This package's own BOUNDARIES line states it plainly: "BND-002 remains
semantic enforcement in addition to RLS." A connection is free to call
`set_workspace_context` with ANY syntactically valid `WorkspaceId` --
nothing in this port (or in the RLS policies it drives) verifies actual
membership. RLS therefore defends against ACCIDENTAL cross-Workspace
leakage (an application bug that forgets a `WHERE workspace_id = ...`
clause, or a connection whose context was never set at all -- see
`WORKSPACE_CONTEXT_SETTING`'s own fail-closed default below), not
against a caller who has already been handed this port and chooses to
lie to it. Proving this limitation honestly, rather than hiding it, is
this package's own mandatory "RLS bypass assumption" adversarial
attack -- see `tests/security/test_workspace.py`.

WHY CLEARING USES AN EMPTY STRING, NOT SQL NULL
--------------------------------------------------------------------
PostgreSQL's `set_config(name, value, is_local)` requires a `text`
`value` argument -- it cannot be used to set a GUC to SQL NULL
directly. The RLS policies this package's own migration creates treat
an empty string identically to "never set" via
`NULLIF(current_setting('app.workspace_id', true), '')::uuid`, which
evaluates to `NULL` either way -- and `workspace_id = NULL` is never
`true` in a `USING`/`WITH CHECK` clause, so both states are equally
fail-closed (zero rows), never fail-open.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from semantic_types.ids import WorkspaceId

WORKSPACE_CONTEXT_SETTING = "app.workspace_id"
"""The Postgres GUC name this package's own RLS policies read via
`current_setting('app.workspace_id', true)`. Unset (or cleared) reads
back as `NULL`, which every policy treats as "no Workspace resolved" --
fail-closed, not "see everything"."""


@runtime_checkable
class WorkspaceContextPort(Protocol):
    """The one "trusted server adapter" 14's own `[IMPLEMENTATION CHOICE]`
    names. A concrete adapter sets this ONLY after BND-002/003 have
    already resolved and verified the caller's own effective Workspace
    -- never from an unverified client claim.
    """

    def set_workspace_context(self, workspace_id: WorkspaceId) -> None:
        """Sets `WORKSPACE_CONTEXT_SETTING` for the remainder of the
        CURRENT transaction only (14's own "transaction-local")."""
        ...

    def clear_workspace_context(self) -> None:
        """Resets `WORKSPACE_CONTEXT_SETTING` to its fail-closed
        (unresolved) state for the remainder of the current
        transaction."""
        ...


__all__ = ["WORKSPACE_CONTEXT_SETTING", "WorkspaceContextPort"]
