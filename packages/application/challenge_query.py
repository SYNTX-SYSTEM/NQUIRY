"""GetChallenge: the read-only, standalone Challenge Query (F02
WU-02.1 -- the "read" half; `create_challenge`,
`application.challenge_creation_handler`, is the "create" half of the
same Work Unit).

`docs/architecture/14_IMPLEMENTATION_SEQUENCE.md` §13's own QUERY
REGISTRY names no standalone `GetChallenge` row at all — the closest
siblings it does name (`GetSession`, `GetBurst`, `GetAIAnalysis`) all
carry the identical "Workspace scoped" rule (never "read authorized",
the stricter rule §13 reserves for `GetDecision`/`GetQuestionSelection`
specifically) — this Query mirrors that rule and
`application.session_view_query.get_session_view`'s own established
implementation exactly: the minimal BND-001 (identity) + BND-002
(Workspace) + BND-003 (membership) read chain, no `AuthorityResolver`
resolution at all (that module's own docstring already gives the full
"do not invent a read-Right" reasoning, equally true here).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.bnd_003_membership import Bnd003Input, Bnd003MembershipEvaluator
from boundaries.registry import BoundaryChainResult, BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId
from domain.challenge import Challenge
from persistence.challenge_repository import ChallengeRepository
from persistence.membership_repository import MembershipRepository
from persistence.workspace_repository import WorkspaceRepository
from semantic_types.ids import ChallengeId, CorrelationId, WorkspaceId

_READ_CHAIN = (BoundaryId.BND_001, BoundaryId.BND_002, BoundaryId.BND_003)


@dataclass(frozen=True, slots=True)
class ChallengeViewData:
    challenge: Challenge


@dataclass(frozen=True, slots=True)
class ChallengeViewDenied:
    chain_result: BoundaryChainResult


@dataclass(frozen=True, slots=True)
class ChallengeViewNotFound:
    """The Challenge itself does not exist. Distinct from `Denied` —
    06's own boundary vocabulary has no DENY reason for "no such
    object", mirrors `session_view_query.SessionViewNotFound`'s own
    identical precedent."""

    challenge_id: ChallengeId


ChallengeViewResult = ChallengeViewData | ChallengeViewDenied | ChallengeViewNotFound


def _build_registry(
    *, workspace_repository: WorkspaceRepository, membership_repository: MembershipRepository
) -> BoundaryRegistry:
    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd002WorkspaceEvaluator(workspace_repository))  # type: ignore[arg-type]
    registry.register(Bnd003MembershipEvaluator(membership_repository))  # type: ignore[arg-type]
    return registry


def get_challenge(
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    challenge_id: ChallengeId,
    correlation_id: CorrelationId,
    challenge_repository: ChallengeRepository,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
) -> ChallengeViewResult:
    """Read one Challenge. Returns `ChallengeViewNotFound` if it does
    not exist (checked before the boundary chain — mirrors
    `get_session_view`'s own identical precedent: existence must be
    known before BND-002 can even resolve the real Workspace the
    object belongs to), `ChallengeViewDenied` if BND-001/002/003 do not
    ALLOW, `ChallengeViewData` otherwise. Never raises for either
    failure mode."""
    challenge = challenge_repository.get(challenge_id)
    if challenge is None:
        return ChallengeViewNotFound(challenge_id)

    context = BoundaryContext(
        workspace_id=workspace_id,
        operation="GetChallenge",
        actor=actor,
        correlation_id=correlation_id,
        evaluated_at=datetime.now(timezone.utc),
    )
    boundary_inputs = {
        BoundaryId.BND_001: Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=context,
            required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
        ),
        BoundaryId.BND_002: Bnd002Input(
            boundary_id=BoundaryId.BND_002,
            context=context,
            resolved_object_workspace_ids=(challenge.workspace_id,),
        ),
        BoundaryId.BND_003: Bnd003Input(boundary_id=BoundaryId.BND_003, context=context),
    }
    registry = _build_registry(
        workspace_repository=workspace_repository, membership_repository=membership_repository
    )
    chain_result = evaluate_chain(registry, _READ_CHAIN, boundary_inputs, context)  # type: ignore[arg-type]
    if not chain_result.is_allowed:
        return ChallengeViewDenied(chain_result)

    return ChallengeViewData(challenge=challenge)


__all__ = [
    "ChallengeViewData",
    "ChallengeViewDenied",
    "ChallengeViewNotFound",
    "ChallengeViewResult",
    "get_challenge",
]
