"""F04 HTTP dispatch: begin analysis and the controller RETRY / RECOVERY requests.

Same common failure envelope as `application.http_f02`. The difference is the
multi-transaction orchestration (pre-implementation binding PI-2):

1. T1: the human Command (CMD_BEGIN_ANALYSIS or a request) in ONE request
   transaction, committed and durable before anything else happens.
2. Only if T1 freshly COMMITTED (not on an idempotent replay: rule 5 allows
   execution only right after the authorizing commit), the system executes the
   new operation authorization in its own transactions (`analysis_system`):
   T2a EXECUTE → provider call outside any transaction → T2b+T3 ACCEPT (and, for
   an accepted analysis, the clustering run).
3. A canonical reread of the position in a fresh transaction.

The response carries the committed Command and the run outcome as SEPARATE
facts (`kind = committed` + `analysis`): a failed or unavailable run never makes
the committed transition look failed.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import RequestCase
from persistence.engine import connect
from semantic_types.ids import SessionId, WorkspaceId

from application import session_control_handler as control
from application.analysis_begin_handler import begin_analysis
from application.analysis_request_handler import (
    REQUEST_COMMAND,
    RequestCaseMismatch,
    request_operation,
)
from application.analysis_runtime import AnalysisRuntime, runtime_from_environment
from application.analysis_system import RunOutcome, run_authorized_operation
from application.composition import GovernedPorts
from application.http_f02 import (
    Response,
    _actor,
    _command_outcome,
    _ident,
    _Rejected,
    _rejected,
    _uuid,
    _with_actor,
    dispatch_session_position,
)

_runtime: AnalysisRuntime | None = None


def configure_runtime(runtime: AnalysisRuntime) -> None:
    """Called once at API startup with the validated runtime (F1)."""
    global _runtime
    _runtime = runtime


def current_runtime() -> AnalysisRuntime:
    global _runtime
    if _runtime is None:
        _runtime = runtime_from_environment()
    return _runtime


@contextmanager
def transaction_uow() -> Iterator[GovernedPorts]:
    """One real database transaction per call (PI-2)."""
    with connect() as connection:
        yield GovernedPorts(connection)


def _version(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise _Rejected("EXPECTED_VERSION_REQUIRED")
    return value


def _run_after_commit(session_id: SessionId, authorization_id: uuid.UUID) -> dict[str, object]:
    try:
        outcome: RunOutcome = run_authorized_operation(
            transaction_uow,
            session_id=session_id,
            authorization_id=authorization_id,
            runtime=current_runtime(),
            now=lambda: datetime.now(timezone.utc),
        )
    except Exception as exc:  # noqa: BLE001 -- the committed Command stands; the run is reported
        return {"status": "INDETERMINATE", "reasonCode": f"SYSTEM_RUN_ERROR:{type(exc).__name__}"}
    return outcome.to_json()


def _finish(
    result: Response,
    holder: dict[str, Any],
    *,
    session_token: str | None,
    workspace_id: str,
    session_id: str,
) -> Response:
    status, body = result
    if status != 200:
        return result
    if "authorization_id" in holder:
        body["analysis"] = _run_after_commit(holder["session_id"], holder["authorization_id"])
    else:
        body["analysis"] = None
    position_status, position = dispatch_session_position(
        session_token=session_token, workspace_id=workspace_id, session_id=session_id
    )
    body["position"] = position if position_status == 200 else None
    return status, body


def dispatch_begin_analysis(
    *,
    session_token: str | None,
    idempotency_key: str | None,
    workspace_id: str,
    session_id: str,
    expected_version: object,
) -> Response:
    """CMD_BEGIN_ANALYSIS (TRN-SESS-006), then the OA-1 run (HD-16)."""
    holder: dict[str, Any] = {}

    def work(ports: GovernedPorts, principal: Any) -> Response:
        ws = WorkspaceId(_uuid(workspace_id, "workspace_id"))
        sid = SessionId(_uuid(session_id, "session_id"))
        version = _version(expected_version)
        ident = _ident(idempotency_key)

        def run() -> Response:
            try:
                result = begin_analysis(
                    ports,
                    actor=_actor(principal),
                    workspace_id=ws,
                    session_id=sid,
                    expected_session_version=version,
                    ident=ident,
                )
            except control.IdempotentReplay:
                return 200, {"kind": "committed", "replayed": True}
            holder["session_id"], holder["authorization_id"] = sid, result.authorization_id
            return 200, {
                "kind": "committed",
                "replayed": False,
                "commandType": "CMD_BEGIN_ANALYSIS",
                "commitId": str(result.commit_unit.commit_id.value),
                "authorizationId": str(result.authorization_id),
            }

        return _command_outcome(run)

    return _finish(
        _with_actor(session_token, work),
        holder,
        session_token=session_token,
        workspace_id=workspace_id,
        session_id=session_id,
    )


def dispatch_request_operation(
    *,
    session_token: str | None,
    idempotency_key: str | None,
    workspace_id: str,
    session_id: str,
    operation: AIOperationId,
    expected_version: object,
    case: object,
) -> Response:
    """CMD_REQUEST_QUESTION_ANALYSIS / CMD_REQUEST_QUESTION_CLUSTERING (RETRY or
    RECOVERY), then the new OA's run."""
    holder: dict[str, Any] = {}

    def work(ports: GovernedPorts, principal: Any) -> Response:
        ws = WorkspaceId(_uuid(workspace_id, "workspace_id"))
        sid = SessionId(_uuid(session_id, "session_id"))
        version = _version(expected_version)
        try:
            request_case = RequestCase(case)
        except ValueError as exc:
            raise _Rejected("REQUEST_CASE_REQUIRED") from exc
        ident = _ident(idempotency_key)

        def run() -> Response:
            try:
                result = request_operation(
                    ports,
                    ai_operation_id=operation,
                    actor=_actor(principal),
                    workspace_id=ws,
                    session_id=sid,
                    expected_session_version=version,
                    case=request_case,
                    ident=ident,
                )
            except control.IdempotentReplay:
                return 200, {"kind": "committed", "replayed": True}
            except RequestCaseMismatch as exc:
                # E18 / K20: input that disagrees with persisted state.
                return _rejected(exc.reason_code)
            holder["session_id"], holder["authorization_id"] = sid, result.authorization_id
            return 200, {
                "kind": "committed",
                "replayed": False,
                "commandType": REQUEST_COMMAND[operation],
                "case": request_case.value,
                "commitId": str(result.commit_unit.commit_id.value),
                "authorizationId": str(result.authorization_id),
            }

        return _command_outcome(run)

    return _finish(
        _with_actor(session_token, work),
        holder,
        session_token=session_token,
        workspace_id=workspace_id,
        session_id=session_id,
    )


def dispatch_request_analysis(**kwargs: Any) -> Response:
    """CMD_REQUEST_QUESTION_ANALYSIS (OA-2)."""
    return dispatch_request_operation(operation=AIOperationId.AIOP_001, **kwargs)


def dispatch_request_clustering(**kwargs: Any) -> Response:
    """CMD_REQUEST_QUESTION_CLUSTERING (OA-4)."""
    return dispatch_request_operation(operation=AIOperationId.AIOP_002, **kwargs)


__all__ = [
    "dispatch_request_analysis",
    "dispatch_request_clustering",
    "configure_runtime",
    "current_runtime",
    "dispatch_begin_analysis",
    "dispatch_request_operation",
    "transaction_uow",
]
