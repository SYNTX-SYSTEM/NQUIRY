"""ChallengeCapabilityProjection: the "Challenge semantic projection"
Work Unit (F02 WU-02.2, 19 §22).

19 §22's own INTERNAL WORK UNITS list names "Challenge semantic
projection" with no further elaboration -- unlike §21's own detailed
FRONTEND REQUIREMENTS/INVERSE PROOF text for `capability_projection.py`
(F01 WU-01.7), and 14 §13's own QUERY REGISTRY names no matching row
either (verified directly, not assumed, before writing this file).
Scope confirmed with the human operator, 2026-09-22: this Work Unit
projects the one capability semantically load-bearing at this exact
point in F02's own listed Work Unit sequence -- "can this actor create
a Session under this Challenge" (AUTH-DEP-SESS-001) -- immediately
ahead of "Session create/read" (WU-02.3, the next Work Unit). This
mirrors `capability_projection.py`'s own pattern (a pure, read-only
projection of already-proven facts, never itself a source of new
authority) scoped down from "the whole Workspace" to "one Challenge,
one candidate Command".

WHY THIS PROJECTION CALLS `AuthorityResolver.resolve()` DIRECTLY,
UNLIKE `capability_projection.project_capabilities`
--------------------------------------------------------------------
`project_capabilities` reads `AuthorityBindingRepository.list_current_bindings`
directly rather than calling `resolve()`, because its own two
capability fields (`authorized`/`governance_capable`) only ever need
"does ANY current binding of this class exist at this Workspace" --
WORKSPACE-scoped, matching every binding `list_current_bindings`
returns. This projection's own one capability field needs something
`list_current_bindings` alone cannot answer: not "does actor hold ANY
`SESSION_CONTROL_RIGHT` binding", but "does actor hold one whose scope
is PRECISELY this Challenge" (AUTH-DEP-SESS-001: "SCOPE: Target
Challenge within one Workspace") -- exactly the scope-matching
`AuthorityResolver.resolve()` already performs, and non-collapse (14
§16, this module's own precedent already warns) forbids
re-implementing a second time.

WHY `challenge.workspace_id` IS RE-CHECKED AGAINST `context.workspace.id`
--------------------------------------------------------------------
`WorkspaceContext` proves the caller is a real, currently-ACTIVE member
of ITS OWN Workspace -- it proves nothing about whatever `Challenge`
object a caller happens to pass alongside it. A caller could construct
this projection with `context` for Workspace A and a real `Challenge`
that actually belongs to Workspace B (the identical "forged Workspace"
shape WU-02.1's own
`test_forged_workspace_in_request_is_ignored_the_real_challenge_workspace_governs`
already proved against `get_challenge`) -- silently proceeding would
resolve authority against the WRONG Workspace's membership/bindings.
`ChallengeOutsideWorkspaceContext` fails this closed instead of
computing a misleading capability.
"""

from __future__ import annotations

from dataclasses import dataclass

from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityRequest, AuthorityResolver, AuthorityVerdict
from domain.challenge import Challenge
from governance.authority_binding import AuthorityClass
from semantic_types.ids import ChallengeId

from application.workspace_context import WorkspaceContext


class ChallengeOutsideWorkspaceContext(ValueError):
    """Raised when `challenge.workspace_id` does not match
    `context.workspace.id` -- see module docstring."""

    def __init__(self, challenge_id: ChallengeId) -> None:
        super().__init__(
            f"challenge {challenge_id!r} does not belong to the Workspace this context proves"
        )
        self.challenge_id = challenge_id


@dataclass(frozen=True, slots=True)
class ChallengeCapabilityProjection:
    """A pure projection of already-proven facts (`WorkspaceContext`'s
    own membership, plus a fresh `AuthorityResolver.resolve()` verdict
    for this exact Challenge) -- never itself a source of new
    authority. Constructible only through
    `project_challenge_capabilities` below.
    """

    challenge_id: ChallengeId
    can_create_session: bool


def project_challenge_capabilities(
    context: WorkspaceContext,
    challenge: Challenge,
    *,
    authority_resolver: AuthorityResolver,
) -> ChallengeCapabilityProjection:
    """Project `context.principal`'s current capability to create a
    Session under `challenge` (AUTH-DEP-SESS-001: a currently-effective
    `SESSION_CONTROL_RIGHT` `HumanAuthorityBinding` scoped to this exact
    Challenge). `context` must be a genuine `WorkspaceContext` (see
    module docstring for why this alone already proves "authenticated"
    and "member") -- this function performs no further identity or
    membership verification of its own. Raises
    `ChallengeOutsideWorkspaceContext` if `challenge` belongs to a
    different Workspace than `context` proves.
    """
    if challenge.workspace_id != context.workspace.id:
        raise ChallengeOutsideWorkspaceContext(challenge.challenge_id)

    actor = ActorIdentity(actor_class=ActorClass.HUMAN_USER, user_id=context.principal.user_id)
    resolution = authority_resolver.resolve(
        AuthorityRequest(
            actor=actor,
            workspace_id=context.workspace.id,
            operation="CMD_CREATE_SESSION",
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            scope_type="CHALLENGE",
            scope_id=challenge.challenge_id.value,
        )
    )

    return ChallengeCapabilityProjection(
        challenge_id=challenge.challenge_id,
        can_create_session=resolution.verdict is AuthorityVerdict.GRANTED,
    )


__all__ = [
    "ChallengeCapabilityProjection",
    "ChallengeOutsideWorkspaceContext",
    "project_challenge_capabilities",
]
