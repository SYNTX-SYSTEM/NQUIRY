"""F02 read side: Workspace members, Challenges, Challenge detail and Session
position, each with SERVER capability projections (WU-02.9).

A capability projection presents currently resolved authority. It is not
authority itself (20 §13: `SERVER CAPABILITY → UI AFFORDANCE`), and every
Command re-resolves at execution time (BND-005 + BND-014). The UI only
renders `available` / `reasonCode` / `reason` from here and never computes
authority itself.

Every query first proves identity + Workspace membership through
`resolve_workspace_context` (BND-001/002/003 semantics). A non-member or
unknown Workspace gets `denied`. Every object read afterwards is checked
against that Workspace, so a foreign id is `not_found`, never a
cross-Workspace read.

Shared precondition logic comes from `application.session_control_handler`
(`prepare_burst_blocker`, `open_question_generation_blocker`,
`method_setup_blocker`), so the affordance and the Command use one
definition.
"""

from __future__ import annotations

import uuid

from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityRequest, AuthorityVerdict
from boundaries.participation_right import resolve_participation_right
from domain.burst import BurstState
from domain.session import SessionState
from domain.session_transitions import SessionTransitionId, resolve_session_transition
from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole
from persistence import inquiry_directory as directory
from persistence.session_participation_repository import SqlAlchemySessionParticipationRepository
from security.identity import AuthenticatedPrincipal
from semantic_types.ids import ChallengeId, SessionId, WorkspaceId

from application.burst_capture_handler import capture_blocker
from application.burst_completion_handler import complete_burst_blocker
from application.composition import GovernedPorts
from application.frozen_set import verify_frozen_set
from application.session_control_handler import (
    method_setup_blocker,
    open_question_generation_blocker,
    prepare_burst_blocker,
)
from application.workspace_context import (
    NotAWorkspaceMemberError,
    WorkspaceContext,
    WorkspaceNotFoundError,
    resolve_workspace_context,
)

SESSION_PHASES = [s.value for s in SessionState]
_PRE_GENERATION = frozenset(
    {SessionState.DRAFT, SessionState.SETUP, SessionState.CHALLENGE_CAPTURE}
)

_REASONS = {
    "NO_SESSION_CONTROL": (
        "Requires SESSION_CONTROL_RIGHT for this Session (scope SESSION:{scope}). "
        "Only the Workspace governance root can grant it."
    ),
    "NO_CHALLENGE_SESSION_CONTROL": (
        "Opening a Session requires SESSION_CONTROL_RIGHT for this Challenge "
        "(scope CHALLENGE:{scope}). Only the Workspace governance root can grant it."
    ),
    "NOT_FACILITATOR": (
        "Creating a Challenge requires the Facilitator role in this Workspace "
        "(AUTH-DEP-CH-001). Your role: {scope}."
    ),
    "NOT_GOVERNANCE_ROOT": "Only the holder of WORKSPACE_GOVERNANCE_RIGHT can grant authority.",
    "STATE_NOT_ELIGIBLE": "Not available while the Session is in {scope}.",
    "SESSION_NOT_PRE_GENERATION": (
        "A protected Burst can only be prepared before question generation."
    ),
    "BURST_ALREADY_EXISTS": "This Session already has its protected Burst.",
    "BURST_ABSENT": "Prepare the protected Burst first.",
    "BURST_NOT_PREPARED": "The protected Burst is not in PREPARED state.",
    "BURST_START_NOT_ELIGIBLE": "The protected Burst cannot start from its current state.",
    "CHALLENGE_CONTEXT_INCOMPLETE": "The Challenge needs a title before question generation.",
    "NO_SESSION_PARTICIPANT": (
        "Admit at least one participant before question generation opens (HD-8)."
    ),
    "METHOD_SETUP_MISSING": "The Session's method setup is missing.",
    "NO_CANDIDATES": "Every active member is already a participant.",
    "SESSION_CLOSED": "The Session is closed.",
    # F03
    "NOT_A_PARTICIPANT": (
        "Only a participant admitted by the Session controller can submit questions. "
        "A Workspace role, Ownership or Session control does not grant this."
    ),
    "SESSION_NOT_QUESTION_GENERATION": (
        "Questions can only be captured while the Session is in QUESTION_GENERATION (now: {scope})."
    ),
    "BURST_NOT_ACTIVE": "The protected Burst is not ACTIVE (now: {scope}).",
    "BURST_MODE_NOT_HUMAN_ONLY": "Only a HUMAN_ONLY Burst accepts captured questions.",
    "NO_CAPTURED_QUESTIONS": "No question has been captured yet; a Burst cannot close empty.",
    "UNRESOLVED_CAPTURE": (
        "A capture write is still unresolved. The Burst cannot close until it is resolved."
    ),
}

# 12 §5 / 01: the Burst is "approximately four minutes". PRESENTATION guidance
# only (HD-11): nothing is scheduled and nothing happens when it is exceeded.
BURST_GUIDANCE_SECONDS = 240


def _question_json(row: directory.CapturedQuestionRow) -> dict[str, object]:
    return {
        "questionId": str(row.question_id),
        "originalText": row.original_text,
        "origin": row.origin,
        "captureOrigin": row.capture_origin,
        "authorUserId": None if row.author_user_id is None else str(row.author_user_id),
        "authorName": row.author_name,
        "capturedOrder": row.captured_order,
        "capturedAt": row.captured_at.isoformat(),
    }


def _cap(available: bool, code: str | None = None, scope: str = "") -> dict[str, object]:
    if available:
        return {"available": True, "reasonCode": None, "reason": None}
    assert code is not None  # noqa: S101
    key = code.split(":", 1)[0]
    detail = code.split(":", 1)[1] if ":" in code else scope
    template = _REASONS.get(key, key)
    return {
        "available": False,
        "reasonCode": code,
        "reason": template.format(scope=detail or scope),
    }


class QueryDenied(Exception):
    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


class QueryNotFound(Exception):
    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


def _context(
    ports: GovernedPorts, principal: AuthenticatedPrincipal, workspace_id: WorkspaceId
) -> WorkspaceContext:
    try:
        return resolve_workspace_context(
            principal, workspace_id, ports.workspaces, ports.memberships
        )
    except WorkspaceNotFoundError as exc:
        raise QueryDenied("WORKSPACE_NOT_ACCESSIBLE") from exc
    except NotAWorkspaceMemberError as exc:
        raise QueryDenied("WORKSPACE_NOT_ACCESSIBLE") from exc


def _holds(
    ports: GovernedPorts,
    context: WorkspaceContext,
    authority_class: AuthorityClass,
    scope_type: str,
    scope_id: uuid.UUID,
) -> bool:
    return (
        ports.resolver.resolve(
            AuthorityRequest(
                actor=ActorIdentity(ActorClass.HUMAN_USER, context.principal.user_id),
                workspace_id=context.workspace.id,
                operation=f"PROJECT:{authority_class.value}",
                required_authority_class=authority_class,
                scope_type=scope_type,
                scope_id=scope_id,
            )
        ).verdict
        is AuthorityVerdict.GRANTED
    )


def _role(ports: GovernedPorts, context: WorkspaceContext) -> WorkspaceRole | None:
    role = ports.memberships.get_current_role(context.membership.id)
    return None if role is None or role.revoked_at is not None else role.role


def _workspace_json(ports: GovernedPorts, context: WorkspaceContext) -> dict[str, object]:
    ws = context.workspace.id.value
    return {
        "workspaceId": str(ws),
        "name": context.workspace.name,
        # Reconstructable provenance, not a guess: False means the Workspace
        # was seeded by the NON_PROOF fixture (no governed founding exists).
        "governedFounding": directory.has_governed_founding(ports.connection, ws),
    }


def _members_json(members: tuple[directory.MemberRow, ...]) -> list[dict[str, object]]:
    return [
        {"userId": str(m.user_id), "name": m.name, "email": m.email, "role": m.role}
        for m in members
    ]


def _binding_json(b: directory.BindingRow) -> dict[str, object]:
    return {
        "bindingId": str(b.binding_id),
        "holderUserId": str(b.human_user_id),
        "holderName": b.human_name,
        "authorityClass": b.authority_class,
        "scope": f"{b.scope_type}:{b.scope_id}",
        "grantedByUserId": str(b.granted_by_user_id),
        "grantedByName": b.granted_by_name,
        "grantedAt": b.granted_at.isoformat(),
    }


def workspace_overview(
    ports: GovernedPorts, principal: AuthenticatedPrincipal, workspace_id: WorkspaceId
) -> dict[str, object]:
    """Members + Challenges + capabilities (create Challenge, govern)."""
    context = _context(ports, principal, workspace_id)
    ws = context.workspace.id.value
    role = _role(ports, context)
    governance_root = _holds(
        ports, context, AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT, "WORKSPACE", ws
    )
    return {
        "kind": "ok",
        "workspace": _workspace_json(ports, context),
        "viewer": {
            "userId": str(context.principal.user_id.value),
            "role": role.value if role is not None else None,
            "isGovernanceRoot": governance_root,
        },
        "members": _members_json(directory.list_members(ports.connection, ws)),
        "challenges": [
            {
                "challengeId": str(c.challenge_id),
                "title": c.title,
                "description": c.description,
                "createdAt": c.created_at.isoformat(),
            }
            for c in directory.list_challenges(ports.connection, ws)
        ],
        "capabilities": {
            "createChallenge": _cap(
                role is WorkspaceRole.FACILITATOR, "NOT_FACILITATOR", role.value if role else "none"
            ),
            "addMember": _cap(governance_root, "NOT_GOVERNANCE_ROOT"),
        },
    }


def challenge_detail(
    ports: GovernedPorts,
    principal: AuthenticatedPrincipal,
    workspace_id: WorkspaceId,
    challenge_id: ChallengeId,
) -> dict[str, object]:
    context = _context(ports, principal, workspace_id)
    challenge = ports.challenges.get(challenge_id)
    if challenge is None or challenge.workspace_id != context.workspace.id:
        raise QueryNotFound("CHALLENGE_NOT_FOUND")
    ws = context.workspace.id.value
    can_open = _holds(
        ports, context, AuthorityClass.SESSION_CONTROL_RIGHT, "CHALLENGE", challenge_id.value
    )
    governance_root = _holds(
        ports, context, AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT, "WORKSPACE", ws
    )
    controllers = directory.list_active_bindings_at_scope(
        ports.connection,
        ws,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT.value,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    return {
        "kind": "ok",
        "workspace": _workspace_json(ports, context),
        "challenge": {
            "challengeId": str(challenge_id.value),
            "title": challenge.title,
            "description": challenge.description,
            "createdAt": challenge.created_at.isoformat(),
            "context": challenge.context,
            "desiredOutcome": challenge.desired_outcome,
            "constraints": challenge.constraints,
            "stakeholders": challenge.stakeholders,
        },
        "sessions": [
            {
                "sessionId": str(s.session_id),
                "state": s.state,
                "version": s.record_version,
                "createdAt": s.created_at.isoformat(),
            }
            for s in directory.list_sessions(ports.connection, ws, challenge_id.value)
        ],
        "sessionControllers": [_binding_json(b) for b in controllers],
        "members": _members_json(directory.list_members(ports.connection, ws)),
        "capabilities": {
            "openSession": _cap(can_open, "NO_CHALLENGE_SESSION_CONTROL", str(challenge_id.value)),
            "grantSessionControl": _cap(governance_root, "NOT_GOVERNANCE_ROOT"),
        },
    }


def _transition_cap(
    is_controller: bool, session_state: SessionState, transition_id: SessionTransitionId, scope: str
) -> dict[str, object]:
    if not is_controller:
        return _cap(False, "NO_SESSION_CONTROL", scope)
    if not resolve_session_transition(
        current_state=session_state, transition_id=transition_id
    ).is_state_eligible:
        return _cap(False, f"STATE_NOT_ELIGIBLE:{session_state.value}")
    return _cap(True)


def _question_set(
    ports: GovernedPorts,
    context: WorkspaceContext,
    burst: object | None,
    viewer_id: uuid.UUID,
    is_controller: bool,
    captured_count: int | None,
) -> dict[str, object]:
    """HD-13 / NQ-DEC-041, filtered ON THE SERVER: while the Burst is ACTIVE a
    participant is served only their own Questions and the controller only a
    count; after completion every Session member is served the full frozen set
    with authors. Nobody is served a Question they are not entitled to."""
    from domain.burst import QuestionBurst

    empty: dict[str, object] = {
        "visibility": "NONE",
        "mine": [],
        "capturedCount": None,
        "frozen": None,
    }
    if not isinstance(burst, QuestionBurst):
        return empty
    ws = context.workspace.id.value
    if burst.state is BurstState.ACTIVE:
        mine = directory.list_captured_questions(
            ports.connection, ws, burst.burst_id.value, only_author=viewer_id
        )
        return {
            "visibility": "OWN_ONLY_WHILE_ACTIVE",
            "mine": [_question_json(q) for q in mine],
            "capturedCount": captured_count if is_controller else None,
            "frozen": None,
        }
    if burst.state is BurstState.COMPLETED:
        rows = directory.list_captured_questions(ports.connection, ws, burst.burst_id.value)
        verification = verify_frozen_set(ports, burst)
        return {
            "visibility": "FULL_FROZEN_SET",
            "mine": [],
            "capturedCount": None,
            "frozen": {
                "fingerprint": burst.frozen_membership_fingerprint,
                "verified": verification.matches,
                "memberCount": verification.member_count,
                "completedAt": burst.completed_at.isoformat() if burst.completed_at else None,
                "questions": [_question_json(q) for q in rows],
            },
        }
    return empty


def session_position(
    ports: GovernedPorts,
    principal: AuthenticatedPrincipal,
    workspace_id: WorkspaceId,
    session_id: SessionId,
) -> dict[str, object]:
    context = _context(ports, principal, workspace_id)
    session = ports.sessions.get(session_id)
    if session is None or session.workspace_id != context.workspace.id:
        raise QueryNotFound("SESSION_NOT_FOUND")
    ws = context.workspace.id.value
    sid = session_id.value
    scope = str(sid)
    challenge = ports.challenges.get(session.challenge_id)
    burst = ports.bursts.get_by_session(session_id)
    participants = SqlAlchemySessionParticipationRepository(ports.connection).list_current(
        session_id
    )
    members = directory.list_members(ports.connection, ws)
    is_controller = _holds(ports, context, AuthorityClass.SESSION_CONTROL_RIGHT, "SESSION", sid)
    governance_root = _holds(
        ports, context, AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT, "WORKSPACE", ws
    )
    controllers = directory.list_active_bindings_at_scope(
        ports.connection,
        ws,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT.value,
        scope_type="SESSION",
        scope_id=sid,
    )
    established = directory.session_state_established_by(
        ports.connection, ws, sid, session.state.value
    )

    current_index = SESSION_PHASES.index(session.state.value)
    participant_ids = {p.user_id.value for p in participants}
    admit_candidates = [m for m in members if m.user_id not in participant_ids]

    def blocked_or(code: str | None) -> dict[str, object]:
        if not is_controller:
            return _cap(False, "NO_SESSION_CONTROL", scope)
        return _cap(code is None, code)

    setup_blocker = method_setup_blocker(session)

    # ---- F03: capture / completion capabilities and the Question set (HD-13)
    viewer_id = context.principal.user_id
    viewer_participation = resolve_participation_right(
        participation_repository=ports.participations,
        membership_repository=ports.memberships,
        actor=ActorIdentity(ActorClass.HUMAN_USER, viewer_id),
        workspace_id=context.workspace.id,
        session_id=sid,
    )
    capture_state_blocker = capture_blocker(session, burst)
    if not viewer_participation.granted:
        capture_cap = _cap(False, "NOT_A_PARTICIPANT")
    elif capture_state_blocker is not None:
        capture_cap = _cap(False, capture_state_blocker)
    else:
        capture_cap = _cap(True)
    captured_count: int | None = None
    unresolved_capture = False
    if burst is not None and is_controller:
        captured_count = directory.count_captured_questions(
            ports.connection, ws, burst.burst_id.value
        )
        if burst.state is BurstState.ACTIVE:
            unresolved_capture = bool(
                ports.commands.list_unresolved_for_target(
                    workspace_id=context.workspace.id,
                    command_type="CMD_CAPTURE_BURST_QUESTION",
                    target_ref=f"burst:{burst.burst_id.value}",
                )
            )
    complete_code = complete_burst_blocker(
        session.state,
        None if burst is None else burst.state,
        unresolved_capture=unresolved_capture,
        member_count=captured_count if is_controller else None,
    )

    actions = {
        "BEGIN_SETUP": _transition_cap(
            is_controller, session.state, SessionTransitionId.TRN_SESS_002, scope
        ),
        "BEGIN_CHALLENGE_CAPTURE": (
            _transition_cap(is_controller, session.state, SessionTransitionId.TRN_SESS_003, scope)
            if setup_blocker is None or not is_controller
            else _cap(False, setup_blocker)
        ),
        "PREPARE_BURST": blocked_or(prepare_burst_blocker(session, burst)),
        "ADMIT_PARTICIPANT": blocked_or(
            "SESSION_CLOSED"
            if session.state is SessionState.CLOSED
            else ("NO_CANDIDATES" if not admit_candidates else None)
        ),
        "OPEN_QUESTION_GENERATION": blocked_or(
            open_question_generation_blocker(
                session, burst, challenge.title if challenge else None, len(participants)
            )
        ),
        "GRANT_SESSION_CONTROL": _cap(governance_root, "NOT_GOVERNANCE_ROOT"),
        "CAPTURE_QUESTION": capture_cap,
        "COMPLETE_BURST": blocked_or(complete_code),
    }
    # `relevant`: does the action belong to the Session's CURRENT phase in
    # the 03 topology (independent of who is looking)? Computed here so the
    # UI never re-derives topology; `available` still carries authority.
    relevant = {
        "BEGIN_SETUP": session.state is SessionState.DRAFT,
        "BEGIN_CHALLENGE_CAPTURE": session.state is SessionState.SETUP,
        "PREPARE_BURST": session.state in _PRE_GENERATION and burst is None,
        "OPEN_QUESTION_GENERATION": session.state is SessionState.CHALLENGE_CAPTURE,
        "ADMIT_PARTICIPANT": session.state is not SessionState.CLOSED,
        "GRANT_SESSION_CONTROL": True,
        "CAPTURE_QUESTION": session.state is SessionState.QUESTION_GENERATION,
        "COMPLETE_BURST": session.state is SessionState.QUESTION_GENERATION,
    }
    for name, cap in actions.items():
        cap["relevant"] = relevant[name]
    role = _role(ports, context)
    question_set = _question_set(
        ports, context, burst, viewer_id.value, is_controller, captured_count
    )
    return {
        "kind": "ok",
        "serverNow": ports.clock.now().isoformat(),
        "workspace": _workspace_json(ports, context),
        "challenge": {
            "challengeId": str(session.challenge_id.value),
            "title": challenge.title if challenge else None,
            "description": challenge.description if challenge else None,
        },
        "session": {
            "sessionId": scope,
            "state": session.state.value,
            "version": session.record_version.value,
            "method": f"{session.applied_method_key} {session.applied_method_version.value}",
            "createdAt": session.created_at.isoformat(),
        },
        "phases": [
            {
                "state": phase,
                "status": "done"
                if i < current_index
                else ("current" if i == current_index else "upcoming"),
            }
            for i, phase in enumerate(SESSION_PHASES)
        ],
        "burst": None
        if burst is None
        else {
            "burstId": str(burst.burst_id.value),
            "state": burst.state.value,
            "mode": burst.mode.value,
            "version": burst.record_version.value,
            "startedAt": burst.started_at.isoformat() if burst.started_at else None,
            "completedAt": burst.completed_at.isoformat() if burst.completed_at else None,
            "guidanceSeconds": BURST_GUIDANCE_SECONDS,
            "guidanceIsAuthoritative": False,
        },
        "questionSet": question_set,
        "participants": [
            {
                "userId": str(p.user_id.value),
                "name": p.user_name,
                "joinedAt": p.joined_at.isoformat(),
                "admittedByUserId": str(p.admitted_by_user_id.value),
            }
            for p in participants
        ],
        "sessionControllers": [_binding_json(b) for b in controllers],
        "establishedBy": None
        if established is None
        else {
            "commandType": established.command_type,
            "actorName": established.actor_name,
            "occurredAt": established.occurred_at.isoformat(),
            "commitId": str(established.commit_id),
            "authoritySourceType": established.authority_source_type,
            "authoritySourceRef": str(established.authority_source_ref),
            "authorityScopeRef": established.authority_scope_ref,
        },
        "viewer": {
            "userId": str(context.principal.user_id.value),
            "role": role.value if role is not None else None,
            "isSessionController": is_controller,
            "isGovernanceRoot": governance_root,
        },
        "actions": actions,
        "admitCandidates": [{"userId": str(m.user_id), "name": m.name} for m in admit_candidates],
        "grantCandidates": [{"userId": str(m.user_id), "name": m.name} for m in members],
    }


__all__ = [
    "QueryDenied",
    "QueryNotFound",
    "challenge_detail",
    "session_position",
    "workspace_overview",
]
