"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) HTTP dispatch — R-01/R-02 only
(Architecture 26, FBR-PCPG-1).

`apps/api/src/nquiry_api/http/pcpg.py` is a thin adapter, same discipline as
every other route file (14 §3.1). This module wires the real producer
(`application.pcpg_observation.observe`) to the existing session-cookie
identity and the existing common failure envelope — nothing here evaluates a
boundary, resolves authority or touches persistence directly.

This is a QUERY, not a Command (09; `01_INVARIANTS.md` I-18): side-effect-free,
no Idempotency-Key, no canonical write, `kind: "ok"` on success — the SAME
envelope `inquiry_queries` already answers with, not a new top-level kind
(I-20: no parallel result vocabulary).
"""

from __future__ import annotations

from typing import Any

from semantic_types.ids import SessionId, WorkspaceId

from application import pcpg_observation as pcpg
from application.composition import GovernedPorts
from application.http_f02 import Response, _denied, _rejected, _uuid, _with_actor
from application.inquiry_queries import QueryDenied, QueryNotFound


def _result_body(result: pcpg.ObservationIngressResult) -> dict[str, object]:
    return {
        "kind": "ok",
        "field": "PRE_CALL_PROMPT_GOVERNANCE",
        "workspace": {
            "workspaceId": str(result.workspace_id.value),
            "name": result.workspace_name,
        },
        "session": (
            None if result.session_id is None else {"sessionId": str(result.session_id.value)}
        ),
        "rawIntent": result.raw_intent,
        "rawIntentLength": result.raw_intent_length,
        "rawIntentDigestSha256": result.raw_intent_digest_sha256,
        "declaredPurpose": result.declared_purpose,
        "observedAt": result.observed_at.isoformat(),
        # Honest about what this Work Unit does NOT produce (FBR-PCPG-2..5
        # pending, `00_FIELD.md` §12): no semantic observation, no delta, no
        # capability value exists yet. Fabricating one here (even "false")
        # would claim a producer this Field does not have.
        "governanceObservation": None,
    }


def dispatch_submit_observation(
    *,
    session_token: str | None,
    workspace_id: str,
    raw_intent: object,
    session_id: str | None,
    declared_purpose: object,
) -> Response:
    def work(ports: GovernedPorts, principal: Any) -> Response:
        ws = WorkspaceId(_uuid(workspace_id, "workspace_id"))
        sid = SessionId(_uuid(session_id, "session_id")) if session_id else None
        if not isinstance(raw_intent, str):
            return _rejected("RAW_INTENT_REQUIRED")
        if declared_purpose is not None and not isinstance(declared_purpose, str):
            return _rejected("DECLARED_PURPOSE_INVALID")

        try:
            result = pcpg.observe(
                ports,
                principal,
                workspace_id=ws,
                raw_intent=raw_intent,
                session_id=sid,
                declared_purpose=declared_purpose,
                now=ports.clock.now(),
            )
        except pcpg.ObservationInputRejected as exc:
            return _rejected(exc.reason_code)
        except QueryDenied as exc:
            return _denied(exc.reason_code)
        except QueryNotFound as exc:
            return 404, {"kind": "not_found", "reasonCode": exc.reason_code}
        return 200, _result_body(result)

    return _with_actor(session_token, work)


__all__ = ["dispatch_submit_observation"]
