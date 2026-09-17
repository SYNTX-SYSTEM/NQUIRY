"""AuthorityResolver: current, operation-specific authority resolution.

Source: 14_IMPLEMENTATION_SEQUENCE.md §16 (AUTHORITY RESOLVER) — the
`AuthorityResolution` verdict vocabulary (`GRANTED`/`DENIED`/
`UNRESOLVED`) and proof contents ("binding identity/version,
membership identity/version, scope, operation, target, evaluated
time/version and reason code") are taken verbatim from there.
06_BOUNDARY_ARCHITECTURE.md §11 (BND-005 HUMAN AUTHORITY BOUNDARY)
grounds the DENY reasons and the "validate current effectiveness using
05 predicate" instruction; 05_GOVERNANCE_INSIDE_SYSTEM.md §18
(HumanAuthorityBinding Effectiveness Predicate) is that predicate,
made concrete below.

THE LOAD-BEARING NON-COLLAPSE RULE OF THIS ENTIRE MODULE (14 §16,
06 §11 PROHIBITED PATH, 04 non-collapse): resolution consults *only*
`ActorIdentity.actor_class`/`user_id`, the current `MembershipRepository`
read, and the current `AuthorityBindingRepository` read for the exact
`(authority_class, scope_type, scope_id)` triple requested. It never
consults, and structurally cannot be passed, a role label, a
Workspace `owner_id`, an "authored by" relation, a request body flag,
a JWT claim, a UI state, a cache, an AI output, or a database/admin
privilege — none of those are parameters `resolve()` accepts, and none
of the two repositories used here can express them. If a future change
to this file adds a parameter or a repository call that lets any of
those inputs influence the verdict, that change is exactly the
collapse this architecture forbids — stop and re-read 04 §3, 05 §18,
06 §11 before making it.

`AuthorityResolver` never caches. Every `resolve()` call performs fresh
repository reads (14 §16: "Commit-time resolver reloads current
authoritative state") — this is what makes P-11 (stale authority
cannot survive commit) true by construction: revoke, then call
`resolve()` again, and the second call sees the revocation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from governance.authority_binding import AuthorityClass
from persistence.authority_binding_repository import AuthorityBindingRepository
from persistence.membership_repository import MembershipRepository
from semantic_types.clock import Clock
from semantic_types.ids import AuthorityBindingId, WorkspaceId
from semantic_types.versions import RecordVersion

from authority.actor import ActorClass, ActorIdentity


class AuthorityVerdict(str, Enum):
    """Exactly 14 §16's 3 outcomes. `UNRESOLVED` is fail-closed for a
    consequential operation (14 §16) — a caller must treat it exactly
    like `DENIED` for any purpose except diagnostics; this type does
    not provide a way to treat it as success.
    """

    GRANTED = "GRANTED"
    DENIED = "DENIED"
    UNRESOLVED = "UNRESOLVED"


class ResolutionReason(str, Enum):
    """Closed reason-code vocabulary. Maps directly to 06 §11 BND-005's
    DENY list, restricted to what this package alone can determine
    (BND-005's "Owner attempting implicit override" and "Facilitator
    attempting non-source decision right" both surface here as
    `NO_MATCHING_BINDING`, because this resolver never looks at role or
    ownership at all — see this module's docstring).
    """

    GRANTED_EFFECTIVE_BINDING = "GRANTED_EFFECTIVE_BINDING"
    DENIED_ACTOR_NOT_HUMAN = "DENIED_ACTOR_NOT_HUMAN"
    DENIED_NO_ACTIVE_MEMBERSHIP = "DENIED_NO_ACTIVE_MEMBERSHIP"
    DENIED_NO_MATCHING_BINDING = "DENIED_NO_MATCHING_BINDING"
    DENIED_WRONG_SCOPE = "DENIED_WRONG_SCOPE"
    UNRESOLVED_AMBIGUOUS_ACTIVE_BINDINGS = "UNRESOLVED_AMBIGUOUS_ACTIVE_BINDINGS"


@dataclass(frozen=True, slots=True)
class AuthorityRequest:
    """The exact 14 §16 input list, minus "current membership"/"current
    HABB"/"governance state" — those are not caller-supplied inputs,
    they are what `AuthorityResolver` itself reads fresh from the two
    repositories on every call (see this module's docstring on why
    that must never be cached or passed in by a caller).

    `operation` is a plain, non-empty descriptive label, not a closed
    vocabulary: no Command registry exists yet (PKG-10+) to define one,
    and 14 §16 lists "operation" only as something the *proof* must
    reference for reconstruction, not as an input the resolution
    algorithm itself branches on (05 §18's Effectiveness Predicate
    never mentions "operation").
    """

    actor: ActorIdentity
    workspace_id: WorkspaceId
    operation: str
    required_authority_class: AuthorityClass
    scope_type: str
    scope_id: uuid.UUID

    def __post_init__(self) -> None:
        if not self.operation:
            raise ValueError("AuthorityRequest.operation must be non-empty")
        if not self.scope_type:
            raise ValueError("AuthorityRequest.scope_type must be non-empty")


@dataclass(frozen=True, slots=True)
class AuthorityResolutionProof:
    """14 §16: "Proof contains binding identity/version, membership
    identity/version, scope, operation, target, evaluated time/version
    and reason code." `binding_id`/`binding_record_version`/
    `membership_id`/`membership_record_version` are `None` when no
    matching current binding/membership exists to reference (an
    honest absence, not a placeholder value).
    """

    reason: ResolutionReason
    workspace_id: WorkspaceId
    scope_type: str
    scope_id: uuid.UUID
    operation: str
    evaluated_at: datetime
    membership_id: uuid.UUID | None
    membership_record_version: RecordVersion | None
    binding_id: AuthorityBindingId | None
    binding_record_version: RecordVersion | None


@dataclass(frozen=True, slots=True)
class AuthorityResolution:
    """The complete result of one `AuthorityResolver.resolve()` call."""

    verdict: AuthorityVerdict
    proof: AuthorityResolutionProof


class AuthorityResolver:
    """Resolves whether `request.actor` currently, effectively holds
    `request.required_authority_class` over `(request.scope_type,
    request.scope_id)` in `request.workspace_id`.

    Constructed with the two PKG-02 read repositories and a `Clock`
    (PKG-00) — never with a cache, a session object, a role list, or
    anything else that could let a prior evaluation outlive the request
    that produced it.
    """

    def __init__(
        self,
        membership_repository: MembershipRepository,
        authority_binding_repository: AuthorityBindingRepository,
        clock: Clock,
    ) -> None:
        self._membership_repository = membership_repository
        self._authority_binding_repository = authority_binding_repository
        self._clock = clock

    def resolve(self, request: AuthorityRequest) -> AuthorityResolution:
        evaluated_at = self._clock.now()

        # 04 §3.3/§3.2, 05 AC-05-007: only HUMAN_USER can hold a HABB.
        # Structural DENY — no membership/binding read even attempted for
        # any other actor class (ATK-003, ATK-009, ATK-010).
        if request.actor.actor_class is not ActorClass.HUMAN_USER:
            return AuthorityResolution(
                verdict=AuthorityVerdict.DENIED,
                proof=self._proof(request, evaluated_at, ResolutionReason.DENIED_ACTOR_NOT_HUMAN),
            )

        # 05 AC-05-004: membership is authority precondition, not authority.
        membership = self._membership_repository.get_current_membership(
            request.workspace_id, request.actor.user_id
        )
        if membership is None:
            return AuthorityResolution(
                verdict=AuthorityVerdict.DENIED,
                proof=self._proof(
                    request, evaluated_at, ResolutionReason.DENIED_NO_ACTIVE_MEMBERSHIP
                ),
            )

        current_bindings = self._authority_binding_repository.list_current_bindings(
            request.workspace_id, request.actor.user_id
        )

        class_matches = [
            b for b in current_bindings if b.authority_class == request.required_authority_class
        ]
        if not class_matches:
            return AuthorityResolution(
                verdict=AuthorityVerdict.DENIED,
                proof=self._proof(
                    request,
                    evaluated_at,
                    ResolutionReason.DENIED_NO_MATCHING_BINDING,
                    membership_id=membership.id,
                    membership_record_version=membership.record_version,
                ),
            )

        scope_matches = [
            b
            for b in class_matches
            if b.scope_type == request.scope_type and b.scope_id == request.scope_id
        ]
        if not scope_matches:
            return AuthorityResolution(
                verdict=AuthorityVerdict.DENIED,
                proof=self._proof(
                    request,
                    evaluated_at,
                    ResolutionReason.DENIED_WRONG_SCOPE,
                    membership_id=membership.id,
                    membership_record_version=membership.record_version,
                ),
            )

        if len(scope_matches) > 1:
            # Data-integrity ambiguity migration 002's schema does not
            # prevent (no uniqueness constraint spans authority_class +
            # scope for human_authority_bindings): fail closed rather
            # than arbitrarily pick one (14 non-collapse: "Unknown
            # consequential semantic input fails closed").
            return AuthorityResolution(
                verdict=AuthorityVerdict.UNRESOLVED,
                proof=self._proof(
                    request,
                    evaluated_at,
                    ResolutionReason.UNRESOLVED_AMBIGUOUS_ACTIVE_BINDINGS,
                    membership_id=membership.id,
                    membership_record_version=membership.record_version,
                ),
            )

        binding = scope_matches[0]
        return AuthorityResolution(
            verdict=AuthorityVerdict.GRANTED,
            proof=self._proof(
                request,
                evaluated_at,
                ResolutionReason.GRANTED_EFFECTIVE_BINDING,
                membership_id=membership.id,
                membership_record_version=membership.record_version,
                binding_id=binding.id,
                binding_record_version=binding.record_version,
            ),
        )

    @staticmethod
    def _proof(
        request: AuthorityRequest,
        evaluated_at: datetime,
        reason: ResolutionReason,
        *,
        membership_id: uuid.UUID | None = None,
        membership_record_version: RecordVersion | None = None,
        binding_id: AuthorityBindingId | None = None,
        binding_record_version: RecordVersion | None = None,
    ) -> AuthorityResolutionProof:
        return AuthorityResolutionProof(
            reason=reason,
            workspace_id=request.workspace_id,
            scope_type=request.scope_type,
            scope_id=request.scope_id,
            operation=request.operation,
            evaluated_at=evaluated_at,
            membership_id=membership_id,
            membership_record_version=membership_record_version,
            binding_id=binding_id,
            binding_record_version=binding_record_version,
        )


__all__ = [
    "AuthorityVerdict",
    "ResolutionReason",
    "AuthorityRequest",
    "AuthorityResolutionProof",
    "AuthorityResolution",
    "AuthorityResolver",
]
