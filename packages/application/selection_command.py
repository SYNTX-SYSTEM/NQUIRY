"""The QuestionSelection product path (WU-PFC-B3): TRN-SEL-001 / TRN-SEL-002.

The governed Command is `application.question_selection_handler.select_question`
(BND-001..007 precommit chain, BND-014 fresh-authority commit at
QUESTION_SELECTION_RIGHT `SESSION:<id>`, audit, outbox). It is not changed here.
This module is the one product entry to it, adding only what the product path
owes before the Command is decided:

- F09-2 membership precheck (no Session fact reaches a non-member);
- the Session row lock (`get_for_update`): the 04 §41 compelling cap (1 to 3)
  and the one-primary rule are cross-row facts, so concurrent selections on one
  Session serialize here instead of racing the database backstops;
- the client's expected Session version (09 §85 payload);
- `selection_blocker`, the one definition shared with the projection, evaluated
  only for an actor who holds QUESTION_SELECTION_RIGHT on this Session (anyone
  else reaches the Command and is denied by BND-005 with a recorded attempt):
  1. the Session is in QUESTION_SELECTION (03 §39);
  2. exactly one active QUESTION_SELECTION_RIGHT holder exists for the Session
     (12 §6 / AC-12-004; 05 §40: multiple bindings need a conflict policy that
     does not exist, NQ-GAP-026);
  3. TRN-SEL-002: no primary exists yet ("No conflicting primary selection ...
     unless explicit replacement semantics are authorized later", GAP-03-018);
  4. TRN-SEL-001: fewer than three compelling selections (04 §41);
  5. the same Question is not selected twice with the same type.
  Each unmet condition is `blocked`; nothing is written.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityRequest, AuthorityVerdict
from commit.coordinator import CommitUnit
from domain.question_selection import QuestionSelection, SelectionType
from domain.session import Session, SessionState
from governance.authority_binding import AuthorityClass
from persistence import inquiry_directory as directory
from persistence.question_selection_repository import SqlAlchemyQuestionSelectionRepository
from persistence.session_repository import SqlAlchemySessionVersionReader
from semantic_types.ids import QuestionId, QuestionSelectionId, SessionId, UserId, WorkspaceId

from application.composition import GovernedPorts
from application.question_selection_handler import (
    _COMMAND_TYPE_FOR_TRANSITION,
    _TRANSITION_FOR_TYPE,
    SelectQuestionPayload,
    select_question,
)
from application.session_control_handler import (
    CommandIdentity,
    SessionNotFound,
    SessionPreconditionUnmet,
    SessionVersionStale,
    deny_unless_member,
    replay_guard,
)

MAX_COMPELLING = 3
"""04 §41 AUTH-DEP-SEL-001: 1 to 3 compelling Questions per Session."""


@dataclass(frozen=True, slots=True)
class SelectInSessionResult:
    commit_unit: CommitUnit
    question_selection_id: QuestionSelectionId
    selection_type: SelectionType


def command_type_for(selection_type: SelectionType) -> str:
    return _COMMAND_TYPE_FOR_TRANSITION[_TRANSITION_FOR_TYPE[selection_type]]


def selection_holders(ports: GovernedPorts, session: Session) -> frozenset[UserId]:
    """The humans for whom QUESTION_SELECTION_RIGHT at `SESSION:<id>` is
    currently effective (raw ACTIVE rows, each confirmed by the resolver)."""
    rows = directory.list_active_bindings_at_scope(
        ports.connection,
        session.workspace_id.value,
        authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT.value,
        scope_type="SESSION",
        scope_id=session.session_id.value,
    )
    return frozenset(
        UserId(uid)
        for uid in {r.human_user_id for r in rows}
        if holds_selection_right(ports, session, UserId(uid))
    )


def holds_selection_right(ports: GovernedPorts, session: Session, user_id: UserId) -> bool:
    return (
        ports.resolver.resolve(
            AuthorityRequest(
                actor=ActorIdentity(ActorClass.HUMAN_USER, user_id),
                workspace_id=session.workspace_id,
                operation="PROJECT:QUESTION_SELECTION_RIGHT",
                required_authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT,
                scope_type="SESSION",
                scope_id=session.session_id.value,
            )
        ).verdict
        is AuthorityVerdict.GRANTED
    )


def selection_blocker(
    ports: GovernedPorts,
    session: Session,
    selections: tuple[QuestionSelection, ...],
    selection_type: SelectionType,
    question_id: QuestionId | None = None,
) -> str | None:
    """The first unmet product precondition of TRN-SEL-001/002, or None."""
    if session.state is not SessionState.QUESTION_SELECTION:
        return "SESSION_NOT_IN_QUESTION_SELECTION"
    if len(selection_holders(ports, session)) != 1:
        return "SELECTOR_NOT_UNIQUE"
    same_type = [s for s in selections if s.selection_type is selection_type]
    if selection_type is SelectionType.PRIMARY and same_type:
        return "PRIMARY_ALREADY_SELECTED"
    if selection_type is SelectionType.COMPELLING and len(same_type) >= MAX_COMPELLING:
        return "COMPELLING_LIMIT_REACHED"
    if question_id is not None and any(s.question_id == question_id for s in same_type):
        return "QUESTION_ALREADY_SELECTED"
    return None


def select_in_session(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    question_id: QuestionId,
    selection_type: SelectionType,
    expected_session_version: int,
    ident: CommandIdentity,
) -> SelectInSessionResult:
    command_type = command_type_for(selection_type)
    replay_guard(
        ports,
        workspace_id,
        command_type,
        ident,
        SelectQuestionPayload(
            session_id=str(session_id.value),
            question_id=str(question_id.value),
            selection_type=selection_type.value,
        ),
    )
    session = ports.sessions.get(session_id)
    deny_unless_member(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        operation=command_type,
        ident=ident,
    )
    if session is None:
        raise SessionNotFound(str(session_id.value))
    locked = ports.sessions.get_for_update(session_id)
    if locked is None:  # pragma: no cover -- rows are never deleted
        raise SessionNotFound(str(session_id.value))
    if locked.record_version.value != expected_session_version:
        raise SessionVersionStale(
            expected=expected_session_version,
            current=locked.record_version.value,
            current_state=locked.state.value,
        )
    repository = SqlAlchemyQuestionSelectionRepository(ports.connection)
    if actor.actor_class is ActorClass.HUMAN_USER and holds_selection_right(
        ports, locked, actor.user_id
    ):
        blocker = selection_blocker(
            ports, locked, repository.list_for_session(session_id), selection_type, question_id
        )
        if blocker is not None:
            raise SessionPreconditionUnmet(blocker)

    selection_id = QuestionSelectionId(uuid.uuid4())
    unit = select_question(
        ports.connection,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        question_id=question_id,
        selection_type=selection_type,
        question_selection_id=selection_id,
        command_id=ident.command_id,
        attempt_id=ident.attempt_id,
        correlation_id=ident.correlation_id,
        occurred_at=ident.occurred_at,
        commit_id=ident.commit_id,
        idempotency_key=ident.idempotency_key,
        workspace_repository=ports.workspaces,
        membership_repository=ports.memberships,
        session_repository=ports.sessions,
        question_repository=ports.questions,
        question_selection_repository=repository,
        authority_resolver=ports.resolver,
        command_repository=ports.commands,
        audit_repository=ports.audit,
        outbox_repository=ports.outbox,
        commit_repository=ports.commits,
        idempotency_port=ports.idempotency,
        current_version_reader=SqlAlchemySessionVersionReader(
            ports.connection, session_id=session_id
        ),
    )
    return SelectInSessionResult(
        commit_unit=unit, question_selection_id=selection_id, selection_type=selection_type
    )


__all__ = [
    "MAX_COMPELLING",
    "SelectInSessionResult",
    "command_type_for",
    "holds_selection_right",
    "select_in_session",
    "selection_blocker",
    "selection_holders",
]
