"""SWU-PX-03 (SF-PX-03 FIXED_TIME_WINDOW_NOT_EXECUTION_LOAD_INVARIANT): observe
a worker subprocess instead of assuming its state from elapsed time.

Before this Work Unit the worker-loop test slept 2.5 s and then sent SIGTERM.
That assumed the worker had imported, installed its stop handlers and run two
passes in that time. Under machine load or a cold start it had not: SIGTERM
met the default disposition (returncode -15, empty stderr).

`WorkerProcess` drains stdout and stderr on reader threads, so a full pipe can
never block the worker. A test then waits for observable stderr lines: the
worker's explicit readiness line (printed only after both stop handlers are
installed) and its pass reports. Every wait has a deadline, which is ONLY a
fail / no-hang bound. Reaching it is a test failure with a diagnostic, never a
readiness proof. Nothing is retried. `close()` always kills and reaps the
process and joins the reader threads, so no process or thread outlives a test.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from types import TracebackType

READY_LINE = "nquiry_worker: ready."
STOPPED_LINE = "nquiry_worker: stopped."
UNAVAILABLE = "DATABASE_UNAVAILABLE"

# Fail / no-hang bound only (the sibling `--once` test allows 60 s as well).
FAIL_BOUND_SECONDS = 60.0

_ROOT = Path(__file__).resolve().parents[2]


class NotObserved(AssertionError):
    """An awaited worker state was not observed: a bounded test failure."""


def worker_env(url: str) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(_ROOT / p) for p in ("packages", "apps/worker/src"))
    env["DATABASE_URL"] = url
    return env


def gated_worker_argv(*args: str, delay: float = 0.0, gated: bool = False) -> list[str]:
    """`python -m nquiry_worker *args`, started late on purpose (falsifiers only).

    `delay` sleeps before the worker module is even imported (delayed startup).
    `gated` blocks on stdin until the test writes a byte, so the stop handlers
    cannot be installed before the test says so (deterministic, no timing)."""
    code = (
        "import runpy, sys, time\n"
        f"time.sleep({delay!r})\n"
        f"if {gated!r}:\n"
        "    sys.stdin.buffer.read(1)\n"
        f"sys.argv = ['nquiry_worker', *{list(args)!r}]\n"
        "runpy.run_module('nquiry_worker', run_name='__main__', alter_sys=True)\n"
    )
    return [sys.executable, "-c", code]


class WorkerProcess:
    def __init__(self, argv: Sequence[str], *, url: str) -> None:
        self._cond = threading.Condition()
        self._lines: list[str] = []
        self._eof = False
        self.proc = subprocess.Popen(
            list(argv),
            env=worker_env(url),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._readers = [
            threading.Thread(target=self._pump_stderr, daemon=True),
            threading.Thread(target=self._drain_stdout, daemon=True),
        ]
        for reader in self._readers:
            reader.start()

    def _pump_stderr(self) -> None:
        assert self.proc.stderr is not None
        for line in self.proc.stderr:
            with self._cond:
                self._lines.append(line.rstrip("\n"))
                self._cond.notify_all()
        with self._cond:
            self._eof = True
            self._cond.notify_all()

    def _drain_stdout(self) -> None:
        assert self.proc.stdout is not None
        self.proc.stdout.read()

    def stderr_text(self) -> str:
        with self._cond:
            return "\n".join(self._lines)

    def wait_until(
        self,
        observed: Callable[[str], bool],
        what: str,
        bound: float = FAIL_BOUND_SECONDS,
    ) -> float:
        """Block until `observed(stderr so far)` holds. Returns the seconds it
        took. Raises `NotObserved` at once if the worker exits first, or when
        the fail bound is reached (no hang, no retry)."""
        start = time.monotonic()
        deadline = start + bound
        with self._cond:
            while not observed("\n".join(self._lines)):
                if self._eof:
                    raise NotObserved(
                        f"worker exited before {what} was observed "
                        f"(returncode={self.proc.wait()}); stderr={self._lines!r}"
                    )
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise NotObserved(
                        f"{what} not observed within the {bound:g} s fail bound "
                        f"(fail / no-hang bound, not a readiness proof); stderr={self._lines!r}"
                    )
                self._cond.wait(remaining)
        return time.monotonic() - start

    def wait_ready(self, bound: float = FAIL_BOUND_SECONDS) -> float:
        return self.wait_until(lambda err: READY_LINE in err.splitlines(), "readiness", bound)

    def wait_unavailable_passes(self, count: int, bound: float = FAIL_BOUND_SECONDS) -> float:
        return self.wait_until(
            lambda err: err.count(UNAVAILABLE) >= count,
            f"{count} {UNAVAILABLE} pass reports",
            bound,
        )

    def open_gate(self) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write("\n")
        self.proc.stdin.flush()

    def stop(
        self, sig: signal.Signals = signal.SIGTERM, bound: float = FAIL_BOUND_SECONDS
    ) -> tuple[int, str]:
        """Send `sig`, then wait (bounded) for exit and the end of stderr."""
        self.proc.send_signal(sig)
        try:
            returncode = self.proc.wait(timeout=bound)
        except subprocess.TimeoutExpired as exc:
            raise NotObserved(
                f"worker did not exit within the {bound:g} s fail bound after {sig.name}; "
                f"stderr={self.stderr_text()!r}"
            ) from exc
        for reader in self._readers:
            reader.join(timeout=bound)
        return returncode, self.stderr_text()

    def close(self) -> None:
        """Deterministic cleanup: kill if still running, reap, join, close.

        The pipes are closed only once both readers have ended. Closing a pipe
        a reader still blocks on would wait for that reader's lock (a hang). A
        reader that outlives the bound is therefore a bounded failure."""
        if self.proc.poll() is None:
            self.proc.kill()
        self.proc.wait(timeout=FAIL_BOUND_SECONDS)
        for reader in self._readers:
            reader.join(timeout=FAIL_BOUND_SECONDS)
        if self.readers_alive():
            raise NotObserved(
                f"worker output still open {FAIL_BOUND_SECONDS:g} s after cleanup "
                f"(process {self.proc.pid} not reaped?)"
            )
        for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            if stream is not None:
                stream.close()

    def readers_alive(self) -> bool:
        return any(reader.is_alive() for reader in self._readers)

    def __enter__(self) -> WorkerProcess:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


def start_worker(*args: str, url: str) -> WorkerProcess:
    return WorkerProcess([sys.executable, "-m", "nquiry_worker", *args], url=url)
