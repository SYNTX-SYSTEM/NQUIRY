"""F05 HTTP dispatch: the QuestionSelection product path (WU-PFC-B3).

Same common envelope and single request transaction as `application.http_f02`.
09 §85: POST question-selections (TRN-SEL-001), POST primary-question
(TRN-SEL-002), GET question-selections.
"""

from __future__ import annotations

from typing import Any

from domain.question_selection import SelectionType
from semantic_types.ids import QuestionId, SessionId, WorkspaceId

from application import inquiry_queries as queries
from application import session_control_handler as control
from application.composition import GovernedPorts
from application.http_f02 import (
    Response,
    _actor,
    _command_outcome,
    _ident,
    _query,
    _Rejected,
    _uuid,
    _with_actor,
)
from application.http_f04 import _version


def dispatch_select_question(
    *,
    session_token: str | None,
    idempotency_key: str | None,
    workspace_id: str,
    session_id: str,
    question_id: object,
    expected_version: object,
    selection_type: str,
) -> Response:
    """CMD_SELECT_COMPELLING_QUESTION / CMD_SELECT_PRIMARY_QUESTION."""
    from application.selection_command import command_type_for, select_in_session

    def work(ports: GovernedPorts, principal: Any) -> Response:
        ws = WorkspaceId(_uuid(workspace_id, "workspace_id"))
        sid = SessionId(_uuid(session_id, "session_id"))
        if not isinstance(question_id, str):
            raise _Rejected("QUESTION_ID_REQUIRED")
        qid = QuestionId(_uuid(question_id, "question_id"))
        version = _version(expected_version)
        ident = _ident(idempotency_key)

        def run() -> Response:
            try:
                result = select_in_session(
                    ports,
                    actor=_actor(principal),
                    workspace_id=ws,
                    session_id=sid,
                    question_id=qid,
                    selection_type=SelectionType(selection_type),
                    expected_session_version=version,
                    ident=ident,
                )
            except control.IdempotentReplay:
                return 200, {"kind": "committed", "replayed": True}
            return 200, {
                "kind": "committed",
                "replayed": False,
                "commandType": command_type_for(SelectionType(selection_type)),
                "commitId": str(result.commit_unit.commit_id.value),
                "questionSelectionId": str(result.question_selection_id.value),
                "selectionType": result.selection_type.value,
            }

        return _command_outcome(run, ident)

    return _with_actor(session_token, work)


def dispatch_question_selections(
    *, session_token: str | None, workspace_id: str, session_id: str
) -> Response:
    def work(ports: GovernedPorts, principal: Any) -> Response:
        ws = WorkspaceId(_uuid(workspace_id, "workspace_id"))
        sid = SessionId(_uuid(session_id, "session_id"))
        return _query(lambda: queries.question_selections(ports, principal, ws, sid))

    return _with_actor(session_token, work)


def dispatch_create_impact_chain(
    *,
    session_token: str | None,
    idempotency_key: str | None,
    workspace_id: str,
    session_id: str,
    expected_version: object,
) -> Response:
    """CMD_CREATE_IMPACT_CHAIN (WU-PFC-B4, HD-26)."""
    from application.impact_chain_handler import create_impact_chain

    def work(ports: GovernedPorts, principal: Any) -> Response:
        ws = WorkspaceId(_uuid(workspace_id, "workspace_id"))
        sid = SessionId(_uuid(session_id, "session_id"))
        version = _version(expected_version)
        ident = _ident(idempotency_key)

        def run() -> Response:
            try:
                result = create_impact_chain(
                    ports,
                    actor=_actor(principal),
                    workspace_id=ws,
                    session_id=sid,
                    expected_session_version=version,
                    ident=ident,
                )
            except control.IdempotentReplay:
                return 200, {"kind": "committed", "replayed": True}
            return 200, {
                "kind": "committed",
                "replayed": False,
                "commandType": "CMD_CREATE_IMPACT_CHAIN",
                "commitId": str(result.commit_unit.commit_id.value),
                "impactChainId": str(result.impact_chain_id),
            }

        return _command_outcome(run, ident)

    return _with_actor(session_token, work)


def _level(value: object) -> int:
    from application.impact_chain_handler import LEVELS

    if not isinstance(value, int) or isinstance(value, bool) or value not in LEVELS:
        raise _Rejected("LEVEL_OUT_OF_RANGE")
    return value


def _answer(value: object) -> str:
    from application.impact_chain_handler import ANSWER_MAX_CHARS

    if not isinstance(value, str) or not value.strip():
        raise _Rejected("ANSWER_REQUIRED")
    if len(value) > ANSWER_MAX_CHARS:
        raise _Rejected("ANSWER_TOO_LONG")
    return value


def dispatch_append_impact_chain_node(
    *,
    session_token: str | None,
    idempotency_key: str | None,
    workspace_id: str,
    session_id: str,
    expected_chain_version: object,
    level: object,
    answer: object,
) -> Response:
    """CMD_APPEND_IMPACT_CHAIN_NODE (WU-PFC-B4, HD-26). The answer is stored
    verbatim; only a blank or oversized answer is refused as input."""
    from application.impact_chain_handler import append_impact_chain_node

    def work(ports: GovernedPorts, principal: Any) -> Response:
        ws = WorkspaceId(_uuid(workspace_id, "workspace_id"))
        sid = SessionId(_uuid(session_id, "session_id"))
        version = _version(expected_chain_version)
        lvl = _level(level)
        text = _answer(answer)
        ident = _ident(idempotency_key)

        def run() -> Response:
            try:
                result = append_impact_chain_node(
                    ports,
                    actor=_actor(principal),
                    workspace_id=ws,
                    session_id=sid,
                    expected_chain_version=version,
                    level=lvl,
                    answer_content=text,
                    ident=ident,
                )
            except control.IdempotentReplay:
                return 200, {"kind": "committed", "replayed": True}
            return 200, {
                "kind": "committed",
                "replayed": False,
                "commandType": "CMD_APPEND_IMPACT_CHAIN_NODE",
                "commitId": str(result.commit_unit.commit_id.value),
                "impactChainId": str(result.impact_chain_id),
                "level": result.level,
                "complete": result.complete,
            }

        return _command_outcome(run, ident)

    return _with_actor(session_token, work)


def dispatch_impact_chain(
    *, session_token: str | None, workspace_id: str, session_id: str
) -> Response:
    def work(ports: GovernedPorts, principal: Any) -> Response:
        ws = WorkspaceId(_uuid(workspace_id, "workspace_id"))
        sid = SessionId(_uuid(session_id, "session_id"))
        return _query(
            lambda: {
                "kind": "ok",
                **queries.session_position(ports, principal, ws, sid)["impactChain"],  # type: ignore[dict-item]
            }
        )

    return _with_actor(session_token, work)


__all__ = [
    "dispatch_append_impact_chain_node",
    "dispatch_create_impact_chain",
    "dispatch_impact_chain",
    "dispatch_question_selections",
    "dispatch_select_question",
]
