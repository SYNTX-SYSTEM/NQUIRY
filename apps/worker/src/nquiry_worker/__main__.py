"""Worker entrypoint: the transactional-outbox delivery loop (WU-PFC-F08-2).

Until WU-PFC-F08-2 this was the Phase-0 no-op ("no workers implemented yet").
It now runs the F08 delivery pipeline (`nquiry_worker.delivery`): each pass
selects the due outbox records, resolves each to its exact committed
EventEnvelope, applies it to the projection read models, and marks it
DELIVERED or FAILED_DELIVERY, all in one transaction per pass
(`projection.delivery.open_delivery`).

- `python -m nquiry_worker`: loop until SIGTERM/SIGINT, one pass every
  `--interval` seconds. Shutdown is graceful: the current pass completes or
  rolls back as a whole.
- `python -m nquiry_worker --once`: exactly one pass, then exit.
- `python -m nquiry_worker --diagnose`: print the delivery diagnostics of
  the whole database as JSON on stdout (read-only), then exit
  (WU-PFC-F08-3).
- Without `DATABASE_URL` the worker refuses to start (exit 2). It has no
  default connection string, matching `persistence.engine`.

PKG-27: one `ObservationContext` per startup and one per pass, through
`LocalOtelObservationSink`. Operational telemetry only, never authoritative
audit (12 section 25).
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import signal
import sys
import time
import uuid
from types import FrameType

from observability.context import LocalOtelObservationSink, ObservationContext
from projection.delivery import open_delivery
from semantic_types.clock import SystemClock
from semantic_types.ids import CorrelationId

from nquiry_worker.delivery import DEFAULT_RETRY_BACKOFF_SECONDS, run_delivery_pass

_observation_sink = LocalOtelObservationSink(tracer_name="nquiry.worker")


class _Stop:
    requested = False


def _request_stop(_signum: int, _frame: FrameType | None) -> None:
    _Stop.requested = True


def _one_pass(backoff: int) -> None:
    _observation_sink.emit(
        ObservationContext(correlation_id=CorrelationId(uuid.uuid4()), operation="delivery_pass")
    )
    with open_delivery() as ports:
        result = run_delivery_pass(ports, clock=SystemClock(), retry_backoff_seconds=backoff)
    print(
        f"nquiry_worker: delivery pass: delivered={len(result.delivered)} "
        f"failed={len(result.failed)}",
        file=sys.stderr,
        flush=True,
    )


def _diagnose() -> None:
    with open_delivery() as ports:
        report = dataclasses.asdict(ports.diagnostics(None))
    print(json.dumps(report, default=str, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nquiry_worker")
    parser.add_argument("--once", action="store_true", help="run exactly one delivery pass")
    parser.add_argument("--interval", type=float, default=5.0, help="seconds between passes")
    parser.add_argument("--retry-backoff", type=int, default=DEFAULT_RETRY_BACKOFF_SECONDS)
    parser.add_argument(
        "--diagnose", action="store_true", help="print delivery diagnostics as JSON and exit"
    )
    args = parser.parse_args(argv)

    if not os.environ.get("DATABASE_URL"):
        print("nquiry_worker: DATABASE_URL is not set; refusing to start.", file=sys.stderr)
        return 2
    if args.diagnose:
        _diagnose()
        return 0

    _observation_sink.emit(
        ObservationContext(correlation_id=CorrelationId(uuid.uuid4()), operation="worker_startup")
    )
    signal.signal(signal.SIGTERM, _request_stop)
    signal.signal(signal.SIGINT, _request_stop)
    while True:
        _one_pass(args.retry_backoff)
        if args.once:
            return 0
        deadline = time.monotonic() + args.interval
        while time.monotonic() < deadline:
            if _Stop.requested:
                print("nquiry_worker: stopped.", file=sys.stderr, flush=True)
                return 0
            time.sleep(0.1)


if __name__ == "__main__":
    raise SystemExit(main())
