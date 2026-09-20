"""No-op worker entrypoint for the Phase 0 skeleton.

Intentionally does nothing but report its own status and exit
successfully. Replaced by real outbox/projection/recovery worker
wiring starting Phase 4 (14 §44). This is not a placeholder pretending
success on a real task — it performs no consequential work and claims
none.

PKG-27 ADDITION: emits one real `ObservationContext` through
`LocalOtelObservationSink` per invocation -- the "...worker
instrumentation integration" 14's own PKG-27 OBJECTIVE names.
Deliberately the ONLY instrumented call site in this process:
`outbox_worker.py`/`projection_worker.py` are proven only through
their own tests, never wired into this entrypoint at all yet (this
file still calls neither) -- a real `command_id`/`event_id`/
`recovery_id`-bearing `ObservationContext` for an actual processed
batch remains that future wiring's own scope, `SUCCESSOR_NOT_BUILT`,
disclosed rather than fabricated here.
"""

from __future__ import annotations

import sys
import uuid

from observability.context import LocalOtelObservationSink, ObservationContext
from semantic_types.ids import CorrelationId

_observation_sink = LocalOtelObservationSink(tracer_name="nquiry.worker")


def main() -> int:
    _observation_sink.emit(
        ObservationContext(
            correlation_id=CorrelationId(uuid.uuid4()),
            operation="worker_startup",
        )
    )
    print("nquiry_worker: Phase 0 skeleton — no workers implemented yet.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
