"""CMD_CREATE_IMPACT_CHAIN / CMD_APPEND_IMPACT_CHAIN_NODE (WU-PFC-B4).

Source: 02 §28 (ImpactChain: a canonical aggregate anchored to the selected
Question; each answer an owned ordered node); 03 §5 (anchored in
QUESTION_SELECTION before investigation), §40 (completeness is structural:
exactly the five ordered answer nodes; "No AI may fill missing answers");
09 §48 (fields), §63 (commands), §86 (server validation: the anchor is the
current primary selection, levels ordered, no duplicate level, a human actor);
Human Authority HD-26 / NQ-DEC-054.

AUTHORITY (HD-26 Option A): the holder of QUESTION_SELECTION_RIGHT who selected
the current primary Question is the sole Human Authority for its ImpactChain.
- BND-001 HUMAN_USER only (rule 5: AI has no authority of any kind here);
- BINDING QUESTION_SELECTION_RIGHT at `SESSION:<id>`, at BND-005 and fresh at
  BND-014 (SESSION_CONTROL_RIGHT and PARTICIPATION confer none: rules 3, 4);
- the actor must be the human who selected the current primary Question,
  otherwise `ContentAuthorityDenied` (NOT_PRIMARY_QUESTION_SELECTOR).

PRECONDITIONS, under the Session row lock (serializing against another append
and against BEGIN_INVESTIGATION): the Session is in QUESTION_SELECTION; a
primary Question exists; for create, no chain exists yet for it (S2(i)); for
append, the level is exactly the next successive level (1..5) of the current
primary's chain. Each unmet condition is `blocked`; nothing is written.

EFFECTS: create -> one `impact_chains` row (record_version 1), event
IMPACT_CHAIN_CREATED. Append -> one immutable node (S1(i): append-only) and the
chain's record_version + 1, event IMPACT_CHAIN_NODE_APPENDED (`complete` when
level 5 lands). No confirmation follows level 5 (rule 7): completion is the
derived structural fact (rule 8, `is_complete`). The answer text is stored
verbatim in its node and never copied into an Event (F08 payload rule).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from authority.actor import ActorIdentity
from commit.coordinator import CommitUnit, FailureInjectionPort, MutationOutcome
from domain.question_selection import QuestionSelection, SelectionType, session_target_ref
from domain.session import Session, SessionState
from events.contracts import EventFacts
from governance.authority_binding import AuthorityClass
from persistence.impact_chain_repository import (
    ImpactChain,
    ImpactChainNode,
    SqlAlchemyImpactChainRepository,
    SqlAlchemyImpactChainVersionReader,
    impact_chain_target_ref,
)
from persistence.question_selection_repository import SqlAlchemyQuestionSelectionRepository
from persistence.session_repository import SqlAlchemySessionVersionReader
from semantic_types.ids import SessionId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion

from application.composition import GovernedPorts
from application.session_control_handler import (
    CommandIdentity,
    ContentAuthorityDenied,
    SessionNotFound,
    SessionPreconditionUnmet,
    SessionVersionStale,
    _run,
    deny_unless_member,
    replay_guard,
)

CREATE_COMMAND = "CMD_CREATE_IMPACT_CHAIN"
APPEND_COMMAND = "CMD_APPEND_IMPACT_CHAIN_NODE"
LEVELS = (1, 2, 3, 4, 5)
"""03 §40.2 / 09 §48.1: the Question Burst method's five successive levels."""
ANSWER_MAX_CHARS = 2000
"""Case 2 (WU-PFC-B4): the same bound as a Burst Question (F03 HD-12)."""


@dataclass(frozen=True, slots=True)
class CreateImpactChainPayload:
    session_id: str
    expected_session_version: int


@dataclass(frozen=True, slots=True)
class AppendImpactChainNodePayload:
    session_id: str
    impact_chain_id: str
    expected_chain_version: int
    level: int
    answer_content: str


@dataclass(frozen=True, slots=True)
class ImpactChainResult:
    commit_unit: CommitUnit
    impact_chain_id: uuid.UUID
    level: int | None = None
    complete: bool = False


def primary_selection(ports: GovernedPorts, session_id: SessionId) -> QuestionSelection | None:
    for s in SqlAlchemyQuestionSelectionRepository(ports.connection).list_for_session(session_id):
        if s.selection_type is SelectionType.PRIMARY:
            return s
    return None


def current_chain(ports: GovernedPorts, session_id: SessionId) -> ImpactChain | None:
    """The chain of the CURRENT primary Question, if any (S2(i))."""
    primary = primary_selection(ports, session_id)
    if primary is None:
        return None
    return SqlAlchemyImpactChainRepository(ports.connection).get_for_anchor(
        session_id, primary.question_id
    )


def is_complete(chain: ImpactChain | None) -> bool:
    """HD-26 rule 8: exactly levels 1..5 exist in valid successive order."""
    return chain is not None and tuple(n.level for n in chain.nodes) == LEVELS


def impact_chain_blocker(
    ports: GovernedPorts, session: Session, actor_id: UserId, *, append: bool
) -> tuple[str | None, bool]:
    """The first unmet condition for `actor_id` to create (append=False) or
    append to (append=True) the current primary's chain, and whether it is a
    content-authority denial rather than a blocker. Shared by the Commands and
    the projection."""
    if session.state is not SessionState.QUESTION_SELECTION:
        return "SESSION_NOT_IN_QUESTION_SELECTION", False
    primary = primary_selection(ports, session.session_id)
    if primary is None:
        return "NO_PRIMARY_QUESTION", False
    if primary.selected_by_user_id != actor_id:
        return "NOT_PRIMARY_QUESTION_SELECTOR", True
    chain = SqlAlchemyImpactChainRepository(ports.connection).get_for_anchor(
        session.session_id, primary.question_id
    )
    if not append:
        return ("IMPACT_CHAIN_ALREADY_EXISTS", False) if chain is not None else (None, False)
    if chain is None:
        return "NO_IMPACT_CHAIN", False
    if is_complete(chain):
        return "IMPACT_CHAIN_COMPLETE", False
    return None, False


def _raise(code: str | None, denial: bool) -> None:
    if code is None:
        return
    if denial:
        raise ContentAuthorityDenied(code)
    raise SessionPreconditionUnmet(code)


def _load(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    operation: str,
    ident: CommandIdentity,
) -> Session:
    session = ports.sessions.get(session_id)
    deny_unless_member(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        operation=operation,
        ident=ident,
    )
    if session is None:
        raise SessionNotFound(str(session_id.value))
    return session


def create_impact_chain(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    ident: CommandIdentity,
    failure_injector: FailureInjectionPort | None = None,
) -> ImpactChainResult:
    payload = CreateImpactChainPayload(
        session_id=str(session_id.value), expected_session_version=expected_session_version
    )
    replay_guard(ports, workspace_id, CREATE_COMMAND, ident, payload)
    session = _load(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        operation=CREATE_COMMAND,
        ident=ident,
    )
    if session.record_version.value != expected_session_version:
        raise SessionVersionStale(
            expected=expected_session_version,
            current=session.record_version.value,
            current_state=session.state.value,
        )
    chain_id = uuid.uuid4()
    ready: dict[str, Any] = {}

    def precondition() -> None:
        fresh = ports.sessions.get_for_update(session_id)
        if fresh is None:  # pragma: no cover -- rows are never deleted
            raise SessionNotFound(str(session_id.value))
        _raise(*impact_chain_blocker(ports, fresh, actor.user_id, append=False))
        primary = primary_selection(ports, session_id)
        assert primary is not None  # noqa: S101 -- no blocker means a primary
        ready["primary"] = primary
        ready["fixture"] = fresh.fixture

    def mutate() -> MutationOutcome:
        primary: QuestionSelection = ready["primary"]
        SqlAlchemyImpactChainRepository(ports.connection).create(
            ImpactChain(
                impact_chain_id=chain_id,
                workspace_id=workspace_id,
                session_id=session_id,
                selected_question_id=primary.question_id,
                created_by_user_id=actor.user_id,
                created_at=ident.occurred_at,
                record_version=RecordVersion.initial(),
            )
        )
        ref = impact_chain_target_ref(chain_id)
        return MutationOutcome(
            state_before_ref=None,
            state_after_ref="impact_chain:CREATED",
            relation_refs=(
                ref,
                f"question_selection:{primary.question_selection_id.value}",
            ),
            event_type="IMPACT_CHAIN_CREATED",
            result_ref=str(chain_id),
            event=EventFacts(
                aggregate_ref=ref,
                payload={
                    "impact_chain_id": str(chain_id),
                    "session_id": str(session_id.value),
                    "selected_question_id": str(primary.question_id.value),
                    "created_by_user_id": str(actor.user_id.value),
                    "fixture": ready["fixture"],
                },
            ),
        )

    session_ref = session_target_ref(session_id)
    unit = _run(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        session_id=session_id,
        command_type=CREATE_COMMAND,
        payload=payload,
        ident=ident,
        resolution=None,
        target_refs=(session_ref,),
        expected_versions={session_ref: RecordVersion(expected_session_version)},
        created_refs=(impact_chain_target_ref(chain_id),),
        reader=SqlAlchemySessionVersionReader(ports.connection, session_id=session_id),
        precondition=precondition,
        mutation=mutate,
        failure_injector=failure_injector,
        authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT,
    )
    return ImpactChainResult(commit_unit=unit, impact_chain_id=chain_id)


def append_impact_chain_node(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_chain_version: int,
    level: int,
    answer_content: str,
    ident: CommandIdentity,
    failure_injector: FailureInjectionPort | None = None,
) -> ImpactChainResult:
    session = _load(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        operation=APPEND_COMMAND,
        ident=ident,
    )
    chain = current_chain(ports, session_id)
    payload = AppendImpactChainNodePayload(
        session_id=str(session_id.value),
        impact_chain_id=str(chain.impact_chain_id) if chain is not None else "",
        expected_chain_version=expected_chain_version,
        level=level,
        answer_content=answer_content,
    )
    replay_guard(ports, workspace_id, APPEND_COMMAND, ident, payload)
    if chain is None:
        raise SessionPreconditionUnmet("NO_IMPACT_CHAIN")
    if chain.record_version.value != expected_chain_version:
        raise SessionVersionStale(
            expected=expected_chain_version,
            current=chain.record_version.value,
            current_state=session.state.value,
        )
    ready: dict[str, Any] = {}

    def precondition() -> None:
        fresh = ports.sessions.get_for_update(session_id)
        if fresh is None:  # pragma: no cover -- rows are never deleted
            raise SessionNotFound(str(session_id.value))
        _raise(*impact_chain_blocker(ports, fresh, actor.user_id, append=True))
        latest = current_chain(ports, session_id)
        if latest is None or latest.impact_chain_id != chain.impact_chain_id:
            raise SessionPreconditionUnmet("IMPACT_CHAIN_NOT_CURRENT")  # pragma: no cover
        if level != latest.next_level:
            raise SessionPreconditionUnmet("LEVEL_NOT_SUCCESSIVE")
        ready["chain"] = latest
        ready["fixture"] = fresh.fixture

    node_id = uuid.uuid4()

    def mutate() -> MutationOutcome:
        latest: ImpactChain = ready["chain"]
        SqlAlchemyImpactChainRepository(ports.connection).append(
            latest,
            ImpactChainNode(
                node_id=node_id,
                level=level,
                answer_content=answer_content,
                author_user_id=actor.user_id,
                captured_at=ident.occurred_at,
            ),
        )
        complete = level == LEVELS[-1]
        ref = impact_chain_target_ref(latest.impact_chain_id)
        return MutationOutcome(
            state_before_ref=f"impact_chain:LEVELS_{level - 1}",
            state_after_ref=f"impact_chain:LEVELS_{level}" + ("|COMPLETE" if complete else ""),
            relation_refs=(ref, f"impact_chain_node:{node_id}"),
            event_type="IMPACT_CHAIN_NODE_APPENDED",
            result_ref=str(node_id),
            event=EventFacts(
                aggregate_ref=ref,
                payload={
                    "impact_chain_id": str(latest.impact_chain_id),
                    "impact_chain_node_id": str(node_id),
                    "session_id": str(session_id.value),
                    "selected_question_id": str(latest.selected_question_id.value),
                    "level": level,
                    "author_user_id": str(actor.user_id.value),
                    "complete": complete,
                    "fixture": ready["fixture"],
                },
            ),
        )

    chain_ref = impact_chain_target_ref(chain.impact_chain_id)
    unit = _run(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        session_id=session_id,
        command_type=APPEND_COMMAND,
        payload=payload,
        ident=ident,
        resolution=None,
        target_refs=(chain_ref,),
        expected_versions={chain_ref: RecordVersion(expected_chain_version)},
        created_refs=(),
        reader=SqlAlchemyImpactChainVersionReader(
            ports.connection, impact_chain_id=chain.impact_chain_id
        ),
        precondition=precondition,
        mutation=mutate,
        failure_injector=failure_injector,
        authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT,
    )
    return ImpactChainResult(
        commit_unit=unit,
        impact_chain_id=chain.impact_chain_id,
        level=level,
        complete=level == LEVELS[-1],
    )


__all__ = [
    "ANSWER_MAX_CHARS",
    "APPEND_COMMAND",
    "CREATE_COMMAND",
    "LEVELS",
    "AppendImpactChainNodePayload",
    "CreateImpactChainPayload",
    "ImpactChainResult",
    "append_impact_chain_node",
    "create_impact_chain",
    "current_chain",
    "impact_chain_blocker",
    "is_complete",
    "primary_selection",
]
