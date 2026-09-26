"""Technical failure envelope at the API edge (WU-PFC-F09-1, F09).

Source: 19_NQUIRY_IMPLEMENTATION_WITH_FRONTEND_RUNNING.md section 29 ("The
system says what it actually knows. It does not falsely claim success, failure,
authority, recovery"; internal Work Unit "HTTP failure mapping");
10_FAILURE_RECOVERY_ROLLBACK.md section 4 (the four outcomes), section 14
(F-PERS); 09_DATA_EVENT_API_CONTRACTS.md section 77 (write outcomes carry the
command identity), section 78 ("5xx technical failure -> may be FAILED_PRECOMMIT
or INDETERMINATE; must not be guessed from status code alone").

`technical_failure_response` is the single mapping the API installs for every
route (`nquiry_api.main`). It uses the envelope kinds the common failure
envelope already has (`application.http_f02`), so no new wire vocabulary is
added.

Mapping (Command = any write method, Query = GET/HEAD/OPTIONS):

- `DatabaseUnavailable` / `DatabaseUrlNotConfigured`:
  503 failed_precommit DATABASE_UNAVAILABLE (both).
- `CommitRejected` (the COMMIT was answered with an error):
  409 failed_precommit COMMIT_REJECTED (both).
- `CommitOutcomeUnknown` (the connection was lost during COMMIT):
  Command 503 indeterminate COMMIT_OUTCOME_UNPROVEN;
  Query 503 failed_precommit DATABASE_UNAVAILABLE.
- Any other exception:
  Command 500 indeterminate UNEXPECTED_SERVER_FAILURE;
  Query 500 failed_precommit UNEXPECTED_SERVER_FAILURE.

For a Command, an unknown exception may have been raised after COMMIT (for
example while the response was built), so claiming FAILED_PRECOMMIT would be a
guess. It is INDETERMINATE: no blind retry, and the same Idempotency-Key
resolves it (the idempotency layer replays a committed result, 14 section 27).
A Query has no consequence, so its failure is honestly FAILED_PRECOMMIT.

Every Command envelope echoes `commandId`, the client's Idempotency-Key
(09 section 77), when one was sent.
"""

from __future__ import annotations

from persistence.engine import (
    CommitOutcomeUnknown,
    CommitRejected,
    DatabaseUnavailable,
    DatabaseUrlNotConfigured,
)

Response = tuple[int, dict[str, object]]

_QUERY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def technical_failure_response(
    exc: BaseException, *, method: str, idempotency_key: str | None
) -> Response:
    command = method.upper() not in _QUERY_METHODS
    if isinstance(exc, DatabaseUnavailable | DatabaseUrlNotConfigured):
        status, kind, reason = 503, "failed_precommit", "DATABASE_UNAVAILABLE"
    elif isinstance(exc, CommitRejected):
        status, kind, reason = 409, "failed_precommit", "COMMIT_REJECTED"
    elif isinstance(exc, CommitOutcomeUnknown):
        if command:
            status, kind, reason = 503, "indeterminate", "COMMIT_OUTCOME_UNPROVEN"
        else:
            status, kind, reason = 503, "failed_precommit", "DATABASE_UNAVAILABLE"
    elif command:
        status, kind, reason = 500, "indeterminate", "UNEXPECTED_SERVER_FAILURE"
    else:
        status, kind, reason = 500, "failed_precommit", "UNEXPECTED_SERVER_FAILURE"
    body: dict[str, object] = {"kind": kind, "reasonCode": reason}
    if command and idempotency_key:
        body["commandId"] = idempotency_key
    return status, body


__all__ = [
    "CommitOutcomeUnknown",
    "CommitRejected",
    "DatabaseUnavailable",
    "technical_failure_response",
]
