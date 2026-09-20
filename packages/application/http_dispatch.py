"""HTTP-facing dispatch: the ONE place in this codebase where a real,
running `apps/api` request is translated into calls against the real
`packages/application` Command/Query handlers, real `persistence`
repository construction, and a real runtime database connection.

Architecture 17 materialization. Lives in `packages/application`, not
`apps/api/src/nquiry_api`, because 14 §3.1's own forbidden-dependency
matrix (enforced by `scripts/check_architecture_dependencies.py`)
restricts `nquiry_api` to `{application, observability, semantic_types}`
only -- it may not import `persistence`, `authority`, `boundaries`,
`security`, `commit`, or `sqlalchemy`/any DB driver at all.
`application` is the one package 14 already authorizes to import every
one of those (see its own, already-established `INTERNAL_ALLOWED`
entry), so this module is the necessary, architecture-permitted
composition root -- `apps/api/src/nquiry_api/http/*.py` calls only the
functions below, passing and receiving plain JSON-serializable
primitives (`str`/`dict`), never a domain/authority-shaped object.

WHY EVERY FUNCTION HERE RETURNS A PLAIN `dict[str, object]`, NEVER A
DOMAIN TYPE
--------------------------------------------------------------------
`apps/web/lib/api/types.ts`'s own `SessionReadResult`/
`DecisionActionResult` discriminated unions are the authoritative wire
contract (camelCase JSON keys, transcribed verbatim from the real
Python domain types -- see that file's own docstring). Returning a
plain dict keyed exactly as that contract requires, built once here,
keeps `apps/api/src/nquiry_api/http/*.py` a genuine thin adapter (14
§3.1: "HTTP must remain an adapter") -- it does no field-name
translation of its own, just `JSONResponse(dispatch_result)`.

IDENTITY (NOT AUTHORITY) RESOLUTION
--------------------------------------------------------------------
`resolve_actor` below is the deterministic, GAP-14-001-disclosed
identity adapter 14 §2.1 authorizes ("pluggable OIDC adapter plus
deterministic test adapter [IMPLEMENTATION CHOICE]"). It resolves WHO
is calling (a real `security.identity.AuthenticatedPrincipal`) and
WHICH `authority.actor.ActorClass` they claim to be (BND-001's own
identity-boundary input) from two bare, cryptographically-unverified
request claims. Real domain Authority is never touched here -- it is
resolved fresh, per request, by `authority.resolver.AuthorityResolver`
inside `application.session_view_query.get_session_view` /
`application.human_decision_handler.record_human_decision` exactly as
it already was for every predecessor package's own pure-Python test
caller. A forged `actor_class_claim` of `AI_PROCESSOR` gains nothing
beyond a documented, provable BND-001 DENY -- see
`tests/e2e/test_http_session_view.py::
test_ai_actor_claim_is_denied_before_touching_any_session_data` and
its Decision-side sibling.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from boundaries.registry import BoundaryChainResult
from commit.coordinator import CommitDenied, CommitFailedPrecommit, CommitIndeterminate
from commit.idempotency import SqlAlchemyIdempotencyRepository
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.burst_repository import SqlAlchemyBurstRepository
from persistence.challenge_repository import SqlAlchemyChallengeRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.decision_repository import (
    SqlAlchemyDecisionRepository,
    SqlAlchemyDecisionVersionReader,
)
from persistence.engine import connect
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.question_repository import SqlAlchemyQuestionRepository
from persistence.session_repository import SqlAlchemySessionRepository
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository
from security.identity import AuthenticatedPrincipal, ExternalCredential
from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    DecisionId,
    SessionId,
    WorkspaceId,
)

from application.human_decision_handler import (
    HumanDecisionDenied,
    SelectedOptionNotCandidate,
    record_human_decision,
)
from application.session_view_query import (
    SessionViewData,
    SessionViewDenied,
    SessionViewNotFound,
    get_session_view,
)

ACTOR_USER_ID_HEADER = "x-nquiry-actor-user-id"
ACTOR_CLASS_HEADER = "x-nquiry-actor-class"
_ISSUER_REF = "nquiry-deterministic-dev-adapter"
_ACTOR_CLASS_BY_VALUE: dict[str, ActorClass] = {c.value: c for c in ActorClass}
_STALE_VERSION_MODULE_NAME = "commit.coordinator"


class MissingActorClaimError(ValueError):
    """No `x-nquiry-actor-user-id` header/claim present. Fails closed."""


class MalformedActorClaimError(ValueError):
    """The claimed subject is not a UUID, or the claimed actor class is
    outside `ActorClass`'s own closed vocabulary. Fails closed."""


def resolve_actor(
    *, actor_user_id_claim: str | None, actor_class_claim: str | None
) -> tuple[ActorIdentity, AuthenticatedPrincipal]:
    if not actor_user_id_claim:
        raise MissingActorClaimError(f"request carries no {ACTOR_USER_ID_HEADER!r} claim")
    try:
        user_uuid = uuid.UUID(actor_user_id_claim)
    except ValueError as exc:
        raise MalformedActorClaimError(
            f"{ACTOR_USER_ID_HEADER!r} must be a UUID, got {actor_user_id_claim!r}"
        ) from exc
    class_value = actor_class_claim or ActorClass.HUMAN_USER.value
    if class_value not in _ACTOR_CLASS_BY_VALUE:
        raise MalformedActorClaimError(
            f"{ACTOR_CLASS_HEADER!r} must be one of {sorted(_ACTOR_CLASS_BY_VALUE)}, "
            f"got {class_value!r}"
        )
    actor_class = _ACTOR_CLASS_BY_VALUE[class_value]

    from semantic_types.ids import UserId

    user_id = UserId(user_uuid)
    credential = ExternalCredential(
        subject=actor_user_id_claim,
        issuer_ref=_ISSUER_REF,
        session_ref=f"dev-session:{actor_user_id_claim}",
        authentication_time=datetime.now(timezone.utc),
    )
    principal = AuthenticatedPrincipal(
        user_id=user_id,
        authentication_session_ref=credential.session_ref,
        authentication_time=credential.authentication_time,
        issuer_ref=credential.issuer_ref,
    )
    return ActorIdentity(actor_class, user_id), principal


def _chain_denied_body(chain_result: BoundaryChainResult) -> dict[str, object]:
    terminal = chain_result.proofs[-1] if chain_result.proofs else None
    return {
        "kind": "denied",
        "result": chain_result.result.value,
        "reasonCode": terminal.reason_code if terminal is not None else "NO_BOUNDARY_EVALUATED",
    }


def _decision_view_body(decision: Any) -> dict[str, object]:
    return {
        "decisionId": str(decision.decision_id.value),
        "challengeId": str(decision.challenge_id.value),
        "decisionQuestionRef": (
            str(decision.decision_question_ref.value)
            if decision.decision_question_ref is not None
            else None
        ),
        "decisionQuestionText": decision.decision_question_text,
        "options": list(decision.options),
        "criteria": list(decision.criteria),
        "selectedOption": decision.selected_option,
        "rationale": decision.rationale,
        "confidence": decision.confidence,
        "state": decision.state.value,
        "decidedByUserId": (
            str(decision.decided_by_user_id.value) if decision.decided_by_user_id else None
        ),
        "decisionAuthorityBindingId": str(decision.decision_authority_binding_id.value),
        "aiRecommendationConsumedRef": (
            str(decision.provenance_ref) if decision.provenance_ref is not None else None
        ),
        "decidedAt": decision.decided_at.isoformat() if decision.decided_at is not None else None,
    }


def dispatch_get_session_view(
    *,
    actor_user_id_claim: str | None,
    actor_class_claim: str | None,
    workspace_id_str: str,
    session_id_str: str,
) -> dict[str, object]:
    """`GET /workspaces/{workspaceId}/sessions/{sessionId}`
    (`apps/web/lib/api/client.ts::fetchSessionView`'s own exact
    contract). Returns a plain dict shaped exactly as
    `SessionReadResult` (`types.ts`)."""
    actor, _principal = resolve_actor(
        actor_user_id_claim=actor_user_id_claim, actor_class_claim=actor_class_claim
    )
    workspace_id = WorkspaceId(uuid.UUID(workspace_id_str))
    session_id = SessionId(uuid.UUID(session_id_str))

    with connect() as connection:
        result = get_session_view(
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            correlation_id=CorrelationId(uuid.uuid4()),
            session_repository=SqlAlchemySessionRepository(connection),
            challenge_repository=SqlAlchemyChallengeRepository(connection),
            burst_repository=SqlAlchemyBurstRepository(connection),
            question_repository=SqlAlchemyQuestionRepository(connection),
            decision_repository=SqlAlchemyDecisionRepository(connection),
            workspace_repository=SqlAlchemyWorkspaceRepository(connection),
            membership_repository=SqlAlchemyMembershipRepository(connection),
        )

    if isinstance(result, SessionViewNotFound):
        return {"kind": "denied", "result": "DENY", "reasonCode": "SESSION_NOT_FOUND"}
    if isinstance(result, SessionViewDenied):
        return _chain_denied_body(result.chain_result)

    assert isinstance(result, SessionViewData)  # noqa: S101 -- exhaustive union narrowing
    decision_view = _decision_view_body(result.decision) if result.decision is not None else None
    burst_view = (
        {
            "burstId": str(result.burst.burst_id.value),
            "sessionId": str(result.burst.session_id.value),
            "state": result.burst.state.value,
            "mode": result.burst.mode.value,
            "questions": [
                {
                    "questionId": str(q.question_id.value),
                    "originalText": q.original_text,
                    "origin": q.origin.value,
                }
                for q in result.burst_questions
            ],
        }
        if result.burst is not None
        else None
    )
    return {
        "kind": "ok",
        "data": {
            "workspaceId": str(result.workspace_id.value),
            "challenge": {
                "challengeId": str(result.challenge.challenge_id.value),
                "workspaceId": str(result.challenge.workspace_id.value),
                "title": result.challenge.title,
                "description": result.challenge.description,
            },
            "session": {
                "sessionId": str(result.session.session_id.value),
                "challengeId": str(result.session.challenge_id.value),
                "workspaceId": str(result.session.workspace_id.value),
                "state": result.session.state.value,
            },
            "burst": burst_view,
            "decision": decision_view,
            "aiRecommendation": None,
        },
    }


def dispatch_record_human_decision(
    *,
    actor_user_id_claim: str | None,
    actor_class_claim: str | None,
    decision_id_str: str,
    selected_option: str,
    rationale: str | None,
    confidence: str | None,
) -> dict[str, object]:
    """`POST /decisions/{decisionId}/decide`
    (`apps/web/lib/api/decisionClient.ts::recordHumanDecision`'s own
    exact contract). Returns a plain dict shaped exactly as
    `DecisionActionResult` (`types.ts`)."""
    actor, _principal = resolve_actor(
        actor_user_id_claim=actor_user_id_claim, actor_class_claim=actor_class_claim
    )
    decision_id = DecisionId(uuid.UUID(decision_id_str))
    correlation_id = CorrelationId(uuid.uuid4())
    now = datetime.now(timezone.utc)

    with connect() as connection:
        decision_repository = SqlAlchemyDecisionRepository(connection)
        existing = decision_repository.get(decision_id)
        if existing is None:
            return {"kind": "rejected", "reasonCode": "DECISION_NOT_FOUND"}
        workspace_id = existing.workspace_id

        try:
            record_human_decision(
                connection,
                actor=actor,
                workspace_id=workspace_id,
                decision_id=decision_id,
                selected_option=selected_option,
                rationale=rationale,
                confidence=confidence,
                command_id=CommandId(uuid.uuid4()),
                attempt_id=AttemptId(uuid.uuid4()),
                correlation_id=correlation_id,
                occurred_at=now,
                commit_id=CommitId(uuid.uuid4()),
                idempotency_key=None,
                evidence_set_ref=None,
                workspace_repository=SqlAlchemyWorkspaceRepository(connection),
                membership_repository=SqlAlchemyMembershipRepository(connection),
                decision_repository=decision_repository,
                authority_resolver=AuthorityResolver(
                    SqlAlchemyMembershipRepository(connection),
                    SqlAlchemyAuthorityBindingRepository(connection),
                    _RealClock(),
                ),
                command_repository=SqlAlchemyCommandRepository(connection),
                audit_repository=SqlAlchemyAuditRepository(connection),
                outbox_repository=SqlAlchemyOutboxRepository(connection),
                commit_repository=SqlAlchemyCommitRepository(connection),
                idempotency_port=SqlAlchemyIdempotencyRepository(connection),
                current_version_reader=SqlAlchemyDecisionVersionReader(
                    connection, decision_id=decision_id
                ),
            )
        except HumanDecisionDenied as exc:
            return _chain_denied_body(exc.chain_result)
        except SelectedOptionNotCandidate as exc:
            return {"kind": "rejected", "reasonCode": f"SELECTED_OPTION_NOT_CANDIDATE:{exc}"}
        except CommitDenied as exc:
            return _chain_denied_body(
                BoundaryChainResult(
                    result=exc.boundary_proof.result,
                    proofs=(exc.boundary_proof,),
                    terminal_boundary_id=exc.boundary_proof.boundary_id,
                )
            )
        except CommitFailedPrecommit as exc:
            return {"kind": "rejected", "reasonCode": f"FAILED_PRECOMMIT:{exc.reason}"}
        except CommitIndeterminate as exc:
            return {"kind": "indeterminate", "blockedTargetRef": str(exc.commit_id.value)}

        decided = decision_repository.get(decision_id)
        assert decided is not None  # noqa: S101 -- just committed inside the same transaction
        return {"kind": "committed", "decision": _decision_view_body(decided)}


class _RealClock:
    """`semantic_types.clock.Clock` port, real wall-clock -- `application`
    may import `semantic_types` directly (always allowed); this
    private shim avoids depending on `test_support.clock.FixedClock`
    (test-only, import-guarded) for a real runtime call path."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


__all__ = [
    "ACTOR_USER_ID_HEADER",
    "ACTOR_CLASS_HEADER",
    "MissingActorClaimError",
    "MalformedActorClaimError",
    "resolve_actor",
    "dispatch_get_session_view",
    "dispatch_record_human_decision",
]
