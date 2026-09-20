"""FastAPI application entrypoint.

ARCHITECTURE 17 UPDATE: `http/commands.py`/`http/queries.py` are now
real (`POST /decisions/{decisionId}/decide`, `GET /workspaces/{w}/
sessions/{s}`) -- see `docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`.
Both dispatch through `packages/application.http_dispatch` only; this
module still never touches persistence/authority/boundaries directly
(14 §3.1 forbidden dependencies for `apps/api`, enforced by
`scripts/check_architecture_dependencies.py`'s own `nquiry_api` entry).

PKG-27 ADDITION: `/healthz` emits one real `ObservationContext` through
`LocalOtelObservationSink` per request -- still the only
UNCONDITIONALLY-instrumented call site; the two real routes below get
their own observability through `application.http_dispatch`'s own
correlation-id construction (see that module).
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI
from observability.context import LocalOtelObservationSink, ObservationContext
from semantic_types.ids import CorrelationId

from nquiry_api.http import commands as commands_router
from nquiry_api.http import queries as queries_router

app = FastAPI(
    title="nquiry-api",
    version="0.0.0",
    description="NQUIRY architectural prototype API — Architecture 17 runtime materialization.",
)
app.include_router(queries_router.router)
app.include_router(commands_router.router)

_observation_sink = LocalOtelObservationSink(tracer_name="nquiry.api")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness probe. Infrastructure-level only; not a Query (14 §13)."""
    _observation_sink.emit(
        ObservationContext(
            correlation_id=CorrelationId(uuid.uuid4()),
            operation="healthz",
        )
    )
    return {"status": "ok", "phase": "0"}
