"""Burst operations: read-only readiness compositor.

Source: 14_IMPLEMENTATION_SEQUENCE.md PKG-07 manifest PUBLIC_INTERFACES
("Burst operations") and AUTHORITY ("Session control authority
referenced, not bypassed").

WHY THIS MODULE NEVER WRITES
--------------------------------
14 §3.1: `application`'s "Canonical write" column reads "no direct
write". PKG-01's own established precedent (recorded in
`scripts/check_architecture_dependencies.py`'s `INTERNAL_ALLOWED["application"]`
comment) is explicit: "application can read via persistence but never
write through it (writes stay commit-only)." `commit` -- the exclusive
governed writer 14 §3.1 assigns Phase-4 machinery to -- does not exist
yet. This module therefore composes exactly two *read* operations
(current Burst state, supplied by the caller -- see `current_state`
below -- and current authority via `AuthorityResolver.resolve`, itself
read-only) plus a pure domain computation
(`resolve_burst_transition_by_operation_name`), and returns a verdict
describing whether a proposed operation *would* be legitimate right
now -- it never calls `BurstRepository.start`/`pause`/`resume`/
`complete`/`add_member` itself. Those methods remain real, tested, and
entirely unwired from production, the identical disclosed pattern
PKG-06 established for `QuestionRepository.create_root`/`create_derived`.

F02 HD-1 SUPERSESSION: the WORKSPACE-scope choice described below was
the PKG-07 reading. The human operator's HD-1 decision (16 §41 REC-002)
fixes Session control authority at `SESSION:<session_id>`; this
compositor now resolves exactly that scope.

F02 WU-02.12 STATUS: this compositor is still read-only and still NOT
wired into production. The governed Burst path is
`application.session_control_handler` (CMD_PREPARE_BURST; Burst START
inside the TRN-SESS-004 bundle), which commits through the
CommitCoordinator. The prototype authority for Burst control is HD-9
(16 §41 REC-009): Session-scoped `SESSION_CONTROL_RIGHT`, as an explicit
prototype narrowing of 04 §36-39 / 05 §20. The PKG-07 text below ("`commit`
... does not exist yet", WORKSPACE scope) is historical.

WHY `AuthorityResolver` IS CALLED FOR REAL HERE (UNLIKE PKG-05/06)
----------------------------------------------------------------------
PKG-07's own coding prompt AUTHORITY line -- "Session control authority
referenced, not bypassed" -- is a materially different instruction from
PKG-05/06's deferred-authority stance, and `PKG-03` is a required
predecessor specifically so this resolution can happen. See
`domain.burst_transitions`'s module docstring for why every check uses
`scope_type="WORKSPACE"` (not `"SESSION"` or `"QuestionBurst"`,
despite 04 §35-39's own per-transition wording) -- the prototype's own
bootstrap sequence (12 §8.1) never produces any other scope shape for
`SESSION_CONTROL_RIGHT`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from authority.actor import ActorIdentity
from authority.resolver import AuthorityRequest, AuthorityResolver, AuthorityVerdict
from domain.burst import BurstState
from domain.burst_transitions import (
    BurstOperation,
    BurstTransitionVerdict,
    resolve_burst_transition_by_operation_name,
)
from governance.authority_binding import AuthorityClass
from persistence.authority_binding_repository import AuthorityBindingRepository
from persistence.membership_repository import MembershipRepository
from semantic_types.clock import Clock
from semantic_types.ids import SessionId, WorkspaceId


class BurstOperationOutcome(Enum):
    """The combined verdict this compositor produces. Deliberately
    never spelled `COMMITTED`/`FAILED_PRECOMMIT`/`INDETERMINATE` (03
    §8's vocabulary) -- this module makes no commit at all, and
    reusing that vocabulary here would misrepresent what actually
    happened.
    """

    READY = "READY"
    """Both the domain transition and current authority check pass.
    Still not a guarantee anything will be written -- no CommitUnit
    exists to make that guarantee, and a concurrent writer could
    invalidate this verdict before any caller acts on it (14 §16:
    resolution is only ever current as of the moment it was computed).
    """

    DENIED_TRANSITION = "DENIED_TRANSITION"
    """The requested operation is not state-eligible from the Burst's
    current state (or the Burst does/doesn't exist as required) --
    see `resolution.transition_verdict`."""

    DENIED_AUTHORITY = "DENIED_AUTHORITY"
    """The actor does not currently, effectively hold
    `SESSION_CONTROL_RIGHT` at `SESSION:<session_id>` (HD-1; the PKG-07
    reading was "at this Workspace") -- see `resolution.authority_verdict`."""

    DENIED_BOTH = "DENIED_BOTH"
    """Both checks failed."""

    UNRESOLVED_AUTHORITY = "UNRESOLVED_AUTHORITY"
    """`AuthorityResolver` itself could not resolve cleanly (ambiguous
    active bindings) -- treated as refusal, never as success (14 §16:
    `UNRESOLVED` is fail-closed)."""


@dataclass(frozen=True, slots=True)
class BurstOperationReadinessResult:
    outcome: BurstOperationOutcome
    transition_verdict: BurstTransitionVerdict
    authority_verdict: AuthorityVerdict

    @property
    def is_ready(self) -> bool:
        return self.outcome is BurstOperationOutcome.READY


def check_burst_operation_readiness(
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    operation: BurstOperation,
    current_state: BurstState | None,
    membership_repository: MembershipRepository,
    authority_binding_repository: AuthorityBindingRepository,
    clock: Clock,
) -> BurstOperationReadinessResult:
    """Compose domain transition eligibility with a real, current
    authority resolution. Read-only: no write of any kind occurs here.

    `current_state` is the Burst's state as already read by the
    caller (typically via `BurstRepository.get(...).state`, or `None`
    for `PREPARE_BURST` against an absent Burst) -- this function does
    not itself fetch it, keeping this module a pure compositor over
    an already-resolved input plus the one genuinely stateful read
    (`AuthorityResolver.resolve`, which by its own design re-reads
    live on every call and must not be cached, see `authority.resolver`'s
    module docstring).
    """
    transition = resolve_burst_transition_by_operation_name(
        current_state=current_state, operation_name=operation.value
    )

    resolver = AuthorityResolver(membership_repository, authority_binding_repository, clock)
    authority_request = AuthorityRequest(
        actor=actor,
        workspace_id=workspace_id,
        operation=operation.value,
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        # F02 HD-1 (16 §41 REC-002): Session control authority is
        # SESSION-scoped. The PKG-07 WORKSPACE-scope reading below
        # ("WHY BURST AUTHORITY RESOLVES ... AT WORKSPACE") is superseded.
        scope_type="SESSION",
        scope_id=session_id.value,
    )
    authority = resolver.resolve(authority_request)

    transition_ok = transition.is_state_eligible
    if authority.verdict is AuthorityVerdict.GRANTED:
        outcome = (
            BurstOperationOutcome.READY
            if transition_ok
            else BurstOperationOutcome.DENIED_TRANSITION
        )
    elif authority.verdict is AuthorityVerdict.UNRESOLVED:
        outcome = BurstOperationOutcome.UNRESOLVED_AUTHORITY
    elif not transition_ok:
        outcome = BurstOperationOutcome.DENIED_BOTH
    else:
        outcome = BurstOperationOutcome.DENIED_AUTHORITY

    return BurstOperationReadinessResult(
        outcome=outcome, transition_verdict=transition.verdict, authority_verdict=authority.verdict
    )


__all__ = [
    "BurstOperationOutcome",
    "BurstOperationReadinessResult",
    "check_burst_operation_readiness",
]
