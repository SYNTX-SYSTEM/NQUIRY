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


__all__ = ["dispatch_question_selections", "dispatch_select_question"]
