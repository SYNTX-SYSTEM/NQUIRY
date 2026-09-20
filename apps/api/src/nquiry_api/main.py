"""FastAPI application entrypoint.

PKG-00 SCOPE: toolchain boot proof only. This module wires the FastAPI
app instance and one liveness endpoint. It must not gain a Command or
Query route until `apps/api/src/nquiry_api/http/commands.py` and
`queries.py` exist (14 §35, §36; file map in 14 §48, Phase 4+), and
those must dispatch through `packages/application`, never mutate
persistence directly (14 §3.1 forbidden dependencies for `apps/api`
controllers: "ORM session mutation, provider SDK, direct CommitUnit
internals").

PKG-27 ADDITION: `/healthz` now emits one real `ObservationContext`
through `LocalOtelObservationSink` per request -- the "app...
instrumentation integration" 14's own PKG-27 OBJECTIVE names. This is
deliberately the ONLY instrumented call site: no Command/Query/
Boundary/CommitUnit dispatch route exists anywhere in this app yet
(`http/commands.py`/`queries.py` are still unbuilt, see above) for a
richer `ObservationContext` (`command_id`/`attempt_id`/`commit_id`/
`boundary_result`/`failure_class`) to genuinely describe -- wiring
those remains that future package's own scope, `SUCCESSOR_NOT_BUILT`,
disclosed rather than fabricated here.
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI
from observability.context import LocalOtelObservationSink, ObservationContext
from semantic_types.ids import CorrelationId

app = FastAPI(
    title="nquiry-api",
    version="0.0.0",
    description="NQUIRY architectural prototype API — Phase 0 skeleton.",
)

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
