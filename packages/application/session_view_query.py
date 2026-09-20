"""GetSession: the read-only Session-view Query (14 §13 QUERY REGISTRY:
"`GetSession` | projection for display, canonical option for proof |
Workspace scoped").

Architecture 17 materialization. This is the FIRST real
`packages/application` Query handler this repository has ever built --
every predecessor package (PKG-14/15/22/24) built Commands only. It
therefore establishes, for the first time in this codebase, the actual
minimal boundary chain a read-only Query runs (BND-001 identity,
BND-002 Workspace, BND-003 membership) as distinct from the full
seven-boundary precommit chain every existing Command handler runs
(`application.human_decision_handler._PRECOMMIT_CHAIN`:
BND-001..BND-007) -- see this package's own sibling Architecture 17
document, "BOUNDARY PRESERVATION" section, for the full reasoning: a
Query "Queries cannot mutate state" (14 §13's own opening line), so
BND-004 (role-context, gates a Command's own domain-write ACCEPTED
role set), BND-005 (Decision-Right specifically), BND-006
(human-vs-AI-decision-origin), and BND-007 (state-transition
legality) are all write-consequence-specific checks with no read-side
analogue 06 defines -- reusing them here would be inventing a
"read-Right" concept 04/05/06 never name, the exact
"do not infer authority" prohibition this session's own field law
states explicitly. BND-001/002/003 remain the correct, minimal,
non-invented read-side chain: identity plausibility, Workspace scope,
and current Workspace membership -- exactly what "Workspace scoped"
(14 §13's own scope rule for this Query) requires and no more.

WHY THIS QUERY NEVER RESOLVES `AuthorityResolver` AT ALL
--------------------------------------------------------------------
`AuthorityResolver` answers "does this actor currently hold
`required_authority_class` over this scope" -- a DECISION_RIGHT/
QUESTION_SELECTION_RIGHT-shaped question. Reading a Session's own
current state is not gated by any named `AuthorityClass` anywhere in
04/05; 14 §13's own scope rule for `GetSession` says "Workspace scoped"
only, never "read authorized" (contrast `GetDecision`'s OWN scope rule,
literally "Workspace scoped/read authorized" -- a distinction 14's own
table draws deliberately). This Query therefore never imports
`authority.resolver` at all, and never claims a DECISION_RIGHT/
QUESTION_SELECTION_RIGHT check it has no textual mandate for.
"""

from __future__ import annotations

from dataclasses import dataclass

from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.bnd_003_membership import Bnd003Input, Bnd003MembershipEvaluator
from boundaries.registry import BoundaryChainResult, BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId
from domain.burst import QuestionBurst
from domain.challenge import Challenge
from domain.decision import Decision
from domain.question import Question
from domain.session import Session
from persistence.burst_repository import BurstRepository
from persistence.challenge_repository import ChallengeRepository
from persistence.decision_repository import DecisionRepository
from persistence.membership_repository import MembershipRepository
from persistence.question_repository import QuestionRepository
from persistence.session_repository import SessionRepository
from persistence.workspace_repository import WorkspaceRepository
from semantic_types.ids import CorrelationId, SessionId, WorkspaceId

_READ_CHAIN = (BoundaryId.BND_001, BoundaryId.BND_002, BoundaryId.BND_003)


@dataclass(frozen=True, slots=True)
class SessionViewData:
    """The `ok` case payload -- every real, already-committed object
    this Query's real repository reads found. `burst`/`decision` are
    `None` when honestly absent (no Burst/Decision exists yet for this
    Session/Challenge), never a placeholder value."""

    workspace_id: WorkspaceId
    challenge: Challenge
    session: Session
    burst: QuestionBurst | None
    burst_questions: tuple[Question, ...]
    decision: Decision | None


@dataclass(frozen=True, slots=True)
class SessionViewDenied:
    chain_result: BoundaryChainResult


@dataclass(frozen=True, slots=True)
class SessionViewNotFound:
    """The Session itself does not exist. Distinct from `Denied` --
    06's own boundary vocabulary has no DENY reason for "no such
    object", and fabricating one would misrepresent a structural
    absence as a boundary refusal."""

    session_id: SessionId


SessionViewResult = SessionViewData | SessionViewDenied | SessionViewNotFound


def _build_registry(
    *, workspace_repository: WorkspaceRepository, membership_repository: MembershipRepository
) -> BoundaryRegistry:
    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd002WorkspaceEvaluator(workspace_repository))  # type: ignore[arg-type]
    registry.register(Bnd003MembershipEvaluator(membership_repository))  # type: ignore[arg-type]
    return registry


def get_session_view(
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    correlation_id: CorrelationId,
    session_repository: SessionRepository,
    challenge_repository: ChallengeRepository,
    burst_repository: BurstRepository,
    question_repository: QuestionRepository,
    decision_repository: DecisionRepository,
    workspace_repository: WorkspaceRepository,
    membership_repository: MembershipRepository,
) -> SessionViewResult:
    from datetime import datetime, timezone

    session = session_repository.get(session_id)
    if session is None:
        return SessionViewNotFound(session_id)

    context = BoundaryContext(
        workspace_id=workspace_id,
        operation="GetSession",
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
            resolved_object_workspace_ids=(session.workspace_id,),
        ),
        BoundaryId.BND_003: Bnd003Input(boundary_id=BoundaryId.BND_003, context=context),
    }
    registry = _build_registry(
        workspace_repository=workspace_repository, membership_repository=membership_repository
    )
    chain_result = evaluate_chain(registry, _READ_CHAIN, boundary_inputs, context)  # type: ignore[arg-type]
    if not chain_result.is_allowed:
        return SessionViewDenied(chain_result)

    challenge = challenge_repository.get(session.challenge_id)
    if challenge is None:
        # A Session structurally requires a real Challenge FK -- this
        # branch is unreachable against real, constraint-enforced
        # storage, but this Query fails closed rather than raising if
        # it is ever reached (e.g. a caller passing a doubled-up mock).
        return SessionViewNotFound(session_id)

    burst = burst_repository.get_by_session(session_id)
    burst_questions: tuple[Question, ...] = ()
    if burst is not None:
        memberships = burst_repository.list_members(burst.burst_id)
        burst_questions = tuple(
            q
            for q in (question_repository.get(m.question_id) for m in memberships)
            if q is not None
        )
    decision = decision_repository.get_latest_by_challenge(challenge.challenge_id)

    return SessionViewData(
        workspace_id=workspace_id,
        challenge=challenge,
        session=session,
        burst=burst,
        burst_questions=burst_questions,
        decision=decision,
    )


__all__ = [
    "SessionViewData",
    "SessionViewDenied",
    "SessionViewNotFound",
    "SessionViewResult",
    "get_session_view",
]
