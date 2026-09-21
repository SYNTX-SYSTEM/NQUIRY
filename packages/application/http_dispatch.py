"""HTTP-facing dispatch: the ONE place in this codebase where a real,
running `apps/api` request is translated into calls against the real
`packages/application` Command/Query handlers, real `persistence`
repository construction, and a real runtime database connection.

Architecture 17 materialization, extended by the local-login field
(`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`). Lives in
`packages/application`, not `apps/api/src/nquiry_api`, because 14 §3.1's
own forbidden-dependency matrix (enforced by
`scripts/check_architecture_dependencies.py`) restricts `nquiry_api` to
`{application, observability, semantic_types}` only -- it may not
import `persistence`, `authority`, `boundaries`, `security`, `commit`,
or `sqlalchemy`/any DB driver at all. `application` is the one package
14 already authorizes to import every one of those (see its own,
already-established `INTERNAL_ALLOWED` entry), so this module is the
necessary, architecture-permitted composition root --
`apps/api/src/nquiry_api/http/*.py` calls only the functions below,
passing and receiving plain JSON-serializable primitives (`str`/`dict`),
never a domain/authority-shaped object.

WHY EVERY FUNCTION HERE RETURNS A PLAIN `dict[str, object]`, NEVER A
DOMAIN TYPE (ONE DISCLOSED EXCEPTION: `dispatch_login`)
--------------------------------------------------------------------
`apps/web/lib/api/types.ts`'s own `SessionReadResult`/
`DecisionActionResult` discriminated unions are the authoritative wire
contract (camelCase JSON keys, transcribed verbatim from the real
Python domain types -- see that file's own docstring). Returning a
plain dict keyed exactly as that contract requires, built once here,
keeps `apps/api/src/nquiry_api/http/*.py` a genuine thin adapter (14
§3.1: "HTTP must remain an adapter") -- it does no field-name
translation of its own, just `JSONResponse(dispatch_result)`.
`dispatch_login` is the one deliberate exception: the raw session token
must reach the HTTP layer so it can be set as an `HttpOnly` cookie
(`Set-Cookie`, a response HEADER), and MUST NEVER appear in the JSON
response body at all (an `HttpOnly` cookie's entire security property
is that client-side JavaScript can never read it -- putting the same
value in the JSON body would defeat that immediately). `dispatch_login`
therefore returns `LoginDispatchResult`, a small dataclass separating
`body` (safe to serialize verbatim) from `session_token`/`expires_at`
(consumed only by the HTTP layer's own `Set-Cookie` construction, never
serialized).

IDENTITY (NOT AUTHORITY) RESOLUTION -- REPLACES THE FORMER
HEADER-TRUST ADAPTER
--------------------------------------------------------------------
Architecture 17's original `resolve_actor` trusted a bare
`x-nquiry-actor-user-id`/`x-nquiry-actor-class` request header at face
value -- disclosed at the time (its own docstring: "No cryptographic
verification occurs anywhere in this path") as the GAP-14-001
`[IMPLEMENTATION CHOICE]` 14 §2.1 authorizes for that build phase. This
field closes that specific weakness for the two real, browser-facing
production routes below: `dispatch_get_session_view`/
`dispatch_record_human_decision` now resolve identity ONLY from a real,
server-verified session (`application.auth_handler.resolve_session`,
backed by the `local_auth_sessions` table a real `/auth/login` call
created) -- never from a request header. The two former header
constants/exceptions (`ACTOR_USER_ID_HEADER`/`ACTOR_CLASS_HEADER`/
`MissingActorClaimError`/`MalformedActorClaimError`) are removed
entirely, not deprecated in place -- `apps/api/src/nquiry_api/http/
queries.py`/`commands.py` no longer read those headers at all, so
supplying them has structurally ZERO effect on either route (proven by
`tests/e2e/test_http_session_view.py::
test_forged_actor_headers_have_no_effect_when_no_session_is_present`
and its sibling with a real session present but a forged header
alongside it).

A session resolved via `resolve_session` is ALWAYS
`authority.actor.ActorClass.HUMAN_USER` -- a real password login has no
mechanism to claim any other actor class (`application.auth_handler`'s
own module docstring). Real domain Authority is still never touched
here -- it is resolved fresh, per request, by
`authority.resolver.AuthorityResolver` inside
`application.session_view_query.get_session_view`/
`application.human_decision_handler.record_human_decision`, exactly as
before.

GAP-14-001 (real OIDC provider selection) remains open and untouched --
this module still never talks to an external identity provider, only
to this repository's own local, deterministic password+session adapter
(14 §32's "deterministic test adapter" half, hardened for real browser
use). HARD-DEP-001 (legitimate first Workspace governance-root
bootstrap) is untouched: nothing in this module or in `auth_handler.py`
decides who may act as a Workspace's governance root -- only WHO is
calling.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from boundaries.registry import BoundaryChainResult
from commit.coordinator import CommitDenied, CommitFailedPrecommit, CommitIndeterminate
from commit.idempotency import SqlAlchemyIdempotencyRepository
from governance.membership import WorkspaceRole
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import (
    SqlAlchemyAuthorityBindingRepository,
    SqlAlchemyAuthorityBindingVersionReader,
)
from persistence.burst_repository import SqlAlchemyBurstRepository
from persistence.challenge_repository import SqlAlchemyChallengeRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.decision_repository import (
    SqlAlchemyDecisionRepository,
    SqlAlchemyDecisionVersionReader,
)
from persistence.engine import connect
from persistence.local_auth_repository import (
    SqlAlchemyLocalCredentialRepository,
    SqlAlchemyLocalSessionRepository,
)
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.question_repository import SqlAlchemyQuestionRepository
from persistence.session_repository import SqlAlchemySessionRepository
from persistence.workspace_repository import (
    SqlAlchemyWorkspaceRepository,
    SqlAlchemyWorkspaceVersionReader,
)
from security.identity import AuthenticatedPrincipal
from semantic_types.ids import (
    AttemptId,
    AuthorityBindingId,
    CommandId,
    CommitId,
    CorrelationId,
    DecisionId,
    SessionId,
    UserId,
    WorkspaceId,
)

from application.accessible_workspaces_query import (
    AccessibleWorkspacesDenied,
    list_accessible_workspaces,
)
from application.auth_handler import InvalidCredentials, login, logout, resolve_session
from application.authority_binding_handler import (
    AuthorityBindingNotFound,
    GovernanceRootOrphaningRefused,
    RevokeAuthorityBindingDenied,
    revoke_human_authority_binding,
)
from application.capability_projection import project_capabilities
from application.human_decision_handler import (
    HumanDecisionDenied,
    SelectedOptionNotCandidate,
    record_human_decision,
)
from application.membership_operations_handler import (
    AddMemberDenied,
    OwnerRoleNotAssignable,
    add_member,
)
from application.session_view_query import (
    SessionViewData,
    SessionViewDenied,
    SessionViewNotFound,
    get_session_view,
)
from application.workspace_context import (
    NotAWorkspaceMemberError,
    WorkspaceNotFoundError,
    resolve_workspace_context,
)
from application.workspace_creation_handler import (
    AllowAllWorkspaceCreationEligibilityChecker,
    WorkspaceCreationDenied,
    create_workspace,
)

SESSION_COOKIE_NAME = "nquiry_session"
_STALE_VERSION_MODULE_NAME = "commit.coordinator"


class NoValidSessionError(ValueError):
    """No session cookie present, or it does not resolve to a real,
    unexpired, unrevoked `local_auth_sessions` row. Fails closed --
    identical HTTP treatment (401) regardless of WHICH of those was
    true, so a caller cannot distinguish "no cookie" from "expired"
    from "revoked" from "forged" (same non-enumeration principle
    `application.auth_handler.resolve_session` already applies)."""


def _resolve_actor_from_session(
    session_token: str | None, *, session_repository: Any
) -> ActorIdentity:
    principal = resolve_session(
        session_token, session_repository=session_repository, now=datetime.now(timezone.utc)
    )
    if principal is None:
        raise NoValidSessionError("no valid session")
    return ActorIdentity(ActorClass.HUMAN_USER, principal.user_id)


def _resolve_principal_from_session(
    session_token: str | None, *, session_repository: Any
) -> AuthenticatedPrincipal:
    """Same resolution as `_resolve_actor_from_session`, but returns the
    full `AuthenticatedPrincipal` rather than downgrading it to an
    `ActorIdentity` -- `application.workspace_context.resolve_workspace_context`
    (F01 WU-01.3, used by the WU-01.8 Workspace-orientation dispatch
    functions below) requires the principal shape, not the narrower one
    the two Architecture-17 routes above were built against. A separate
    function, not a signature change to `_resolve_actor_from_session`,
    to keep this Work Unit's own diff from touching Architecture-17/
    local-login-field code that already works."""
    principal = resolve_session(
        session_token, session_repository=session_repository, now=datetime.now(timezone.utc)
    )
    if principal is None:
        raise NoValidSessionError("no valid session")
    return principal


@dataclass(frozen=True, slots=True)
class LoginDispatchResult:
    """See this module's own docstring section on why `dispatch_login`
    is the one function here that does NOT return a plain dict."""

    body: dict[str, object]
    session_token: str | None
    expires_at: datetime | None


def dispatch_login(*, email: str, password: str) -> LoginDispatchResult:
    """`POST /auth/login`. Never raises on bad credentials -- returns a
    `denied` body instead, same fail-closed-but-not-500 discipline as
    every other dispatch function here."""
    with connect() as connection:
        try:
            result = login(
                email,
                password,
                credential_repository=SqlAlchemyLocalCredentialRepository(connection),
                session_repository=SqlAlchemyLocalSessionRepository(connection),
                now=datetime.now(timezone.utc),
            )
        except InvalidCredentials:
            return LoginDispatchResult(
                body={"kind": "denied", "reasonCode": "INVALID_CREDENTIALS"},
                session_token=None,
                expires_at=None,
            )
    return LoginDispatchResult(
        body={"kind": "ok", "userId": str(result.user_id.value)},
        session_token=result.session_token,
        expires_at=result.expires_at,
    )


def dispatch_logout(*, session_token: str | None) -> dict[str, object]:
    """`POST /auth/logout`. Idempotent -- a missing/unknown/already-
    revoked token is a silent no-op, never an error."""
    with connect() as connection:
        logout(
            session_token,
            session_repository=SqlAlchemyLocalSessionRepository(connection),
            now=datetime.now(timezone.utc),
        )
    return {"kind": "ok"}


def dispatch_current_session(*, session_token: str | None) -> dict[str, object]:
    """`GET /auth/me`. Used by the frontend root route to decide
    "show the login page" vs "show the real application" -- never
    raises; a missing/invalid session is a normal `denied` response,
    not a 500."""
    with connect() as connection:
        principal = resolve_session(
            session_token,
            session_repository=SqlAlchemyLocalSessionRepository(connection),
            now=datetime.now(timezone.utc),
        )
    if principal is None:
        return {"kind": "denied", "reasonCode": "NO_SESSION"}
    return {"kind": "ok", "userId": str(principal.user_id.value)}


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
    session_token: str | None,
    workspace_id_str: str,
    session_id_str: str,
) -> dict[str, object]:
    """`GET /workspaces/{workspaceId}/sessions/{sessionId}`
    (`apps/web/lib/api/client.ts::fetchSessionView`'s own exact
    contract). Returns a plain dict shaped exactly as
    `SessionReadResult` (`types.ts`). Raises `NoValidSessionError`
    (mapped to 401 by the HTTP layer) if `session_token` does not
    resolve to a real, current session -- checked BEFORE the path
    parameters are even parsed, same auth-before-input-validation
    precedence the former header-based `resolve_actor` also had."""
    with connect() as connection:
        actor = _resolve_actor_from_session(
            session_token, session_repository=SqlAlchemyLocalSessionRepository(connection)
        )
        workspace_id = WorkspaceId(uuid.UUID(workspace_id_str))
        session_id = SessionId(uuid.UUID(session_id_str))
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
    session_token: str | None,
    decision_id_str: str,
    selected_option: str,
    rationale: str | None,
    confidence: str | None,
) -> dict[str, object]:
    """`POST /decisions/{decisionId}/decide`
    (`apps/web/lib/api/decisionClient.ts::recordHumanDecision`'s own
    exact contract). Returns a plain dict shaped exactly as
    `DecisionActionResult` (`types.ts`). Raises `NoValidSessionError`
    (mapped to 401 by the HTTP layer) if `session_token` does not
    resolve to a real, current session -- checked BEFORE the decision id
    is even parsed, same auth-before-input-validation precedence the
    former header-based `resolve_actor` also had."""
    correlation_id = CorrelationId(uuid.uuid4())
    now = datetime.now(timezone.utc)

    with connect() as connection:
        actor = _resolve_actor_from_session(
            session_token, session_repository=SqlAlchemyLocalSessionRepository(connection)
        )
        decision_id = DecisionId(uuid.UUID(decision_id_str))
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


# ---------------------------------------------------------------------------
# F01 WU-01.8: HTTP surface for the Commands/Queries F01 already built
# (WU-01.4b create_workspace, WU-01.5 add_member, WU-01.6
# revoke_human_authority_binding, WU-01.2 list_accessible_workspaces,
# WU-01.3 resolve_workspace_context, WU-01.7 project_capabilities) --
# none of them had a route until now. Same thin-dispatch discipline as
# every function above: real work happens in the imported
# `application.*` functions only, this module's own job is connection/
# repository construction, session resolution, and exception ->
# JSON-shape translation.
# ---------------------------------------------------------------------------


def _workspace_record_body(record: Any) -> dict[str, object]:
    return {
        "workspaceId": str(record.id.value),
        "name": record.name,
        "ownerId": str(record.owner_id.value),
        "createdAt": record.created_at.isoformat(),
    }


def dispatch_create_workspace(
    *, session_token: str | None, workspace_name: str
) -> dict[str, object]:
    """`POST /workspaces`. Any real, verified human may found a
    Workspace (F01 WU-01.4, human-confirmed Option A) -- never raises
    for a denied attempt, returns a `denied`/`rejected` body instead,
    same fail-closed-but-not-500 discipline as every dispatch function
    above."""
    with connect() as connection:
        actor = _resolve_actor_from_session(
            session_token, session_repository=SqlAlchemyLocalSessionRepository(connection)
        )
        if not workspace_name or not workspace_name.strip():
            return {"kind": "rejected", "reasonCode": "WORKSPACE_NAME_REQUIRED"}
        try:
            result = create_workspace(
                connection,
                actor=actor,
                workspace_name=workspace_name,
                command_id=CommandId(uuid.uuid4()),
                attempt_id=AttemptId(uuid.uuid4()),
                correlation_id=CorrelationId(uuid.uuid4()),
                occurred_at=datetime.now(timezone.utc),
                commit_id=CommitId(uuid.uuid4()),
                eligibility_checker=AllowAllWorkspaceCreationEligibilityChecker(),
                command_repository=SqlAlchemyCommandRepository(connection),
                audit_repository=SqlAlchemyAuditRepository(connection),
                outbox_repository=SqlAlchemyOutboxRepository(connection),
                commit_repository=SqlAlchemyCommitRepository(connection),
                workspace_repository=SqlAlchemyWorkspaceRepository(connection),
                membership_repository=SqlAlchemyMembershipRepository(connection),
                authority_binding_repository=SqlAlchemyAuthorityBindingRepository(connection),
            )
        except WorkspaceCreationDenied as exc:
            return {"kind": "denied", "result": "DENY", "reasonCode": exc.reason_code}
    return {"kind": "ok", "workspaceId": str(result.workspace_id.value)}


def dispatch_list_accessible_workspaces(*, session_token: str | None) -> dict[str, object]:
    """`GET /workspaces`. Every Workspace the caller currently holds
    ACTIVE membership in -- an empty list is a legitimate, non-
    adversarial response (`application.accessible_workspaces_query`'s
    own docstring), never an error."""
    with connect() as connection:
        actor = _resolve_actor_from_session(
            session_token, session_repository=SqlAlchemyLocalSessionRepository(connection)
        )
        try:
            workspaces = list_accessible_workspaces(
                actor,
                correlation_id=CorrelationId(uuid.uuid4()),
                occurred_at=datetime.now(timezone.utc),
                membership_repository=SqlAlchemyMembershipRepository(connection),
                workspace_repository=SqlAlchemyWorkspaceRepository(connection),
            )
        except AccessibleWorkspacesDenied as exc:
            return {"kind": "denied", "result": "DENY", "reasonCode": exc.reason_code}
    return {"kind": "ok", "workspaces": [_workspace_record_body(w) for w in workspaces]}


def dispatch_workspace_orientation(
    *, session_token: str | None, workspace_id_str: str
) -> dict[str, object]:
    """`GET /workspaces/{workspaceId}`. Combines F01 WU-01.3
    (`resolve_workspace_context`) and WU-01.7 (`project_capabilities`)
    into the one "Workspace orientation" response 19 SS21's own
    FRONTEND REQUIREMENTS line names ("Render separately: authenticated
    / member / authorized / governance-capable / non-proof demo
    state") -- "authenticated"/"member" are implicit in ever reaching
    the `kind: ok` body at all (a real session resolved, a real
    Workspace and ACTIVE membership were proven); "non-proof demo
    state" is not represented (see `capability_projection`'s own
    module docstring for why -- no schema fact exists to project it
    from)."""
    with connect() as connection:
        principal = _resolve_principal_from_session(
            session_token, session_repository=SqlAlchemyLocalSessionRepository(connection)
        )
        workspace_id = WorkspaceId(uuid.UUID(workspace_id_str))
        workspace_repository = SqlAlchemyWorkspaceRepository(connection)
        membership_repository = SqlAlchemyMembershipRepository(connection)
        try:
            context = resolve_workspace_context(
                principal, workspace_id, workspace_repository, membership_repository
            )
        except WorkspaceNotFoundError:
            return {"kind": "denied", "result": "DENY", "reasonCode": "WORKSPACE_NOT_FOUND"}
        except NotAWorkspaceMemberError:
            return {"kind": "denied", "result": "DENY", "reasonCode": "NOT_A_WORKSPACE_MEMBER"}
        capabilities = project_capabilities(
            context,
            membership_repository=membership_repository,
            authority_binding_repository=SqlAlchemyAuthorityBindingRepository(connection),
        )
    return {
        "kind": "ok",
        "workspace": _workspace_record_body(context.workspace),
        "role": capabilities.role.value,
        "heldAuthorityClasses": sorted(c.value for c in capabilities.held_authority_classes),
        "authorized": capabilities.authorized,
        "governanceCapable": capabilities.governance_capable,
    }


def dispatch_add_member(
    *,
    session_token: str | None,
    workspace_id_str: str,
    new_member_user_id_str: str,
    role_str: str,
) -> dict[str, object]:
    """`POST /workspaces/{workspaceId}/members`. Only the Workspace's
    own governance root may call this successfully (F01 WU-01.5's own
    BND-004/005 gate); never raises for a denied/rejected attempt."""
    with connect() as connection:
        actor = _resolve_actor_from_session(
            session_token, session_repository=SqlAlchemyLocalSessionRepository(connection)
        )
        workspace_id = WorkspaceId(uuid.UUID(workspace_id_str))
        new_member_user_id = UserId(uuid.UUID(new_member_user_id_str))
        try:
            role = WorkspaceRole(role_str)
        except ValueError:
            return {"kind": "rejected", "reasonCode": f"UNKNOWN_ROLE:{role_str}"}

        try:
            add_member(
                connection,
                actor=actor,
                workspace_id=workspace_id,
                new_member_user_id=new_member_user_id,
                role=role,
                command_id=CommandId(uuid.uuid4()),
                attempt_id=AttemptId(uuid.uuid4()),
                correlation_id=CorrelationId(uuid.uuid4()),
                occurred_at=datetime.now(timezone.utc),
                commit_id=CommitId(uuid.uuid4()),
                idempotency_key=None,
                workspace_repository=SqlAlchemyWorkspaceRepository(connection),
                membership_repository=SqlAlchemyMembershipRepository(connection),
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
                current_version_reader=SqlAlchemyWorkspaceVersionReader(
                    connection, workspace_id=workspace_id
                ),
            )
        except OwnerRoleNotAssignable as exc:
            return {"kind": "rejected", "reasonCode": "OWNER_ROLE_NOT_ASSIGNABLE:" + str(exc)}
        except AddMemberDenied as exc:
            return _chain_denied_body(exc.chain_result)
        except CommitFailedPrecommit as exc:
            return {"kind": "rejected", "reasonCode": f"FAILED_PRECOMMIT:{exc.reason}"}
        except CommitIndeterminate as exc:
            return {"kind": "indeterminate", "blockedTargetRef": str(exc.commit_id.value)}
    return {"kind": "ok"}


def dispatch_revoke_authority_binding(
    *, session_token: str | None, workspace_id_str: str, binding_id_str: str
) -> dict[str, object]:
    """`POST /workspaces/{workspaceId}/authority-bindings/{bindingId}/revoke`.
    Only the Workspace's own governance root may call this successfully
    (F01 WU-01.6's own BND-004/005 gate); the Workspace's own
    `WORKSPACE_GOVERNANCE_RIGHT` binding can never be revoked through
    this route (`GovernanceRootOrphaningRefused`, GAP-05-001)."""
    with connect() as connection:
        actor = _resolve_actor_from_session(
            session_token, session_repository=SqlAlchemyLocalSessionRepository(connection)
        )
        workspace_id = WorkspaceId(uuid.UUID(workspace_id_str))
        binding_id = AuthorityBindingId(uuid.UUID(binding_id_str))
        try:
            revoke_human_authority_binding(
                connection,
                actor=actor,
                workspace_id=workspace_id,
                binding_id=binding_id,
                command_id=CommandId(uuid.uuid4()),
                attempt_id=AttemptId(uuid.uuid4()),
                correlation_id=CorrelationId(uuid.uuid4()),
                occurred_at=datetime.now(timezone.utc),
                commit_id=CommitId(uuid.uuid4()),
                idempotency_key=None,
                workspace_repository=SqlAlchemyWorkspaceRepository(connection),
                membership_repository=SqlAlchemyMembershipRepository(connection),
                authority_binding_repository=SqlAlchemyAuthorityBindingRepository(connection),
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
                current_version_reader=SqlAlchemyAuthorityBindingVersionReader(connection),
            )
        except GovernanceRootOrphaningRefused as exc:
            return {
                "kind": "rejected",
                "reasonCode": "GOVERNANCE_ROOT_ORPHANING_REFUSED:" + str(exc),
            }
        except RevokeAuthorityBindingDenied as exc:
            return _chain_denied_body(exc.chain_result)
        except AuthorityBindingNotFound:
            return {"kind": "denied", "result": "DENY", "reasonCode": "AUTHORITY_BINDING_NOT_FOUND"}
        except CommitFailedPrecommit as exc:
            return {"kind": "rejected", "reasonCode": f"FAILED_PRECOMMIT:{exc.reason}"}
        except CommitIndeterminate as exc:
            return {"kind": "indeterminate", "blockedTargetRef": str(exc.commit_id.value)}
    return {"kind": "ok"}


class _RealClock:
    """`semantic_types.clock.Clock` port, real wall-clock -- `application`
    may import `semantic_types` directly (always allowed); this
    private shim avoids depending on `test_support.clock.FixedClock`
    (test-only, import-guarded) for a real runtime call path."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


__all__ = [
    "SESSION_COOKIE_NAME",
    "NoValidSessionError",
    "LoginDispatchResult",
    "dispatch_login",
    "dispatch_logout",
    "dispatch_current_session",
    "dispatch_get_session_view",
    "dispatch_record_human_decision",
    "dispatch_create_workspace",
    "dispatch_list_accessible_workspaces",
    "dispatch_workspace_orientation",
    "dispatch_add_member",
    "dispatch_revoke_authority_binding",
]
