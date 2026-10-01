"""SWU-PX-03: falsifiers for the worker readiness relation (SF-PX-03
FIXED_TIME_WINDOW_NOT_EXECUTION_LOAD_INVARIANT).

Relation under proof:

    WORKER PROCESS START
    -> SIGTERM and SIGINT handlers actually installed
    -> explicit readiness observable (`nquiry_worker: ready.`)
    -> required DATABASE_UNAVAILABLE passes observed
    -> SIGTERM -> graceful stop -> returncode 0 + "stopped"

Not: sleep N seconds -> assume the worker is ready.

Each falsifier proves the relation holds where the old fixed window broke
(delayed startup, CPU contention, a slow failing database), or proves the
parts it depends on: the ordering of readiness after handler installation, the
non-graceful outcome before it, the bounded failure when readiness never
comes, and the cleanup that leaves no process behind. The `delay` and the
CPU / database load below are injected conditions of a falsifier. They are
never a readiness assumption.
"""

from __future__ import annotations

import contextlib
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from worker_readiness_support import (
    READY_LINE,
    STOPPED_LINE,
    NotObserved,
    WorkerProcess,
    gated_worker_argv,
    start_worker,
)

_UNREACHABLE = "postgresql+psycopg://nquiry:x@127.0.0.1:1/none"
_OLD_FIXED_WINDOW_SECONDS = 2.5  # the PCPG-5 consumer's assumption, reproduced only as a witness


def _children() -> set[int]:
    """PIDs whose parent is this process (zombies included: an unreaped child
    is residue too)."""
    me = str(os.getpid())
    found: set[int] = set()
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text()
        except OSError:
            continue
        # pid (comm) state ppid ...: comm may contain spaces, split after ')'
        if stat.rsplit(")", 1)[1].split()[1] == me:
            found.add(int(entry.name))
    return found


@pytest.fixture(autouse=True)
def no_process_residue() -> Iterator[None]:
    if not Path("/proc/self/stat").exists():
        pytest.skip("process-residue accounting needs /proc (Linux)")
    before = _children()
    yield
    residue = _children() - before
    for pid in residue:  # reap first: a failing test must not leak a process either
        with contextlib.suppress(ProcessLookupError):
            os.kill(pid, signal.SIGKILL)
        with contextlib.suppress(ChildProcessError):
            os.waitpid(pid, 0)
    assert residue == set(), f"child processes outlived the test: {sorted(residue)}"


def _assert_graceful(returncode: int, err: str, *, passes: int) -> None:
    assert returncode == 0, err
    assert err.count("DATABASE_UNAVAILABLE") >= passes
    assert "stopped" in err


def _graceful_cycle(w: WorkerProcess) -> tuple[float, int, str]:
    ready_after = w.wait_ready()
    w.wait_unavailable_passes(2)
    returncode, err = w.stop(signal.SIGTERM)
    return ready_after, returncode, err


# ------------------------------------------------------------ producer ordering


def test_readiness_is_announced_only_after_both_stop_handlers_are_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deterministic, in-process: the ready line follows the installation of
    BOTH handlers, and both handlers request a graceful stop."""
    import nquiry_worker.__main__ as worker

    events: list[tuple[str, Any]] = []

    def install(signum: int, handler: Any) -> None:
        events.append(("handler", signum))
        assert handler is worker._request_stop

    class _Stderr:
        def write(self, text: str) -> int:
            if text.strip():
                events.append(("stderr", text.strip()))
            return len(text)

        def flush(self) -> None:
            return None

    monkeypatch.setenv("DATABASE_URL", _UNREACHABLE)
    monkeypatch.setattr(
        worker,
        "signal",
        SimpleNamespace(signal=install, SIGTERM=signal.SIGTERM, SIGINT=signal.SIGINT),
    )
    monkeypatch.setattr(worker, "_one_pass", lambda _backoff: None)
    monkeypatch.setattr(worker.sys, "stderr", _Stderr())

    assert worker.main(["--once"]) == 0

    ready = events.index(("stderr", READY_LINE))
    term = events.index(("handler", signal.SIGTERM))
    intr = events.index(("handler", signal.SIGINT))
    assert term < ready and intr < ready, events


# ------------------------------------------------------------ before readiness


def test_sigterm_before_handler_installation_is_not_a_graceful_stop() -> None:
    """The worker is held before it can import or install anything. A SIGTERM
    now meets the default disposition: no readiness, no graceful stop. This is
    what readiness protects against (the published SF-PX-03 signature)."""
    with WorkerProcess(gated_worker_argv("--interval", "0.2", gated=True), url=_UNREACHABLE) as w:
        returncode, err = w.stop(signal.SIGTERM)
    assert returncode == -signal.SIGTERM
    assert READY_LINE not in err
    assert STOPPED_LINE not in err


def test_the_old_fixed_window_consumer_fails_when_startup_outlasts_it() -> None:
    """Witness for SF-PX-03: the PCPG-5 consumer (sleep 2.5 s, then SIGTERM)
    against a worker whose startup has not finished stops it non-gracefully.
    Deterministic: the gate is never opened."""
    with WorkerProcess(gated_worker_argv("--interval", "0.2", gated=True), url=_UNREACHABLE) as w:
        time.sleep(_OLD_FIXED_WINDOW_SECONDS)
        returncode, err = w.stop(signal.SIGTERM)
    assert returncode == -signal.SIGTERM
    assert err == ""


# ------------------------------------------------------------ readiness reached


@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGINT], ids=["SIGTERM", "SIGINT"])
def test_a_stop_right_after_readiness_is_graceful(sig: signal.Signals) -> None:
    """Readiness is sufficient on its own: a stop sent the moment the line is
    observed, before any pass is awaited, is graceful for both handlers."""
    with start_worker("--interval", "0.2", url=_UNREACHABLE) as w:
        w.wait_ready()
        returncode, err = w.stop(sig)
    assert returncode == 0, err
    assert "stopped" in err


def test_readiness_reached_then_passes_then_graceful_stop() -> None:
    with start_worker("--interval", "0.2", url=_UNREACHABLE) as w:
        _, returncode, err = _graceful_cycle(w)
    _assert_graceful(returncode, err, passes=2)
    lines = err.splitlines()
    assert lines.index(READY_LINE) < next(
        i for i, line in enumerate(lines) if "DATABASE_UNAVAILABLE" in line
    )


def test_delayed_startup_beyond_the_old_window_still_stops_gracefully() -> None:
    """Startup is delayed past the old 2.5 s window before the worker module is
    even imported. The consumer waits for readiness, not for time."""
    delay = 2 * _OLD_FIXED_WINDOW_SECONDS
    argv = gated_worker_argv("--interval", "0.2", delay=delay)
    with WorkerProcess(argv, url=_UNREACHABLE) as w:
        ready_after, returncode, err = _graceful_cycle(w)
    assert ready_after >= delay
    _assert_graceful(returncode, err, passes=2)


# ------------------------------------------------------------ under contention


@pytest.fixture
def cpu_contention() -> Iterator[int]:
    """One busy process per CPU (the machine saturated) for the duration of
    the test, then killed and reaped deterministically. Heavier and longer
    contention belongs to the out-of-suite load-contention proof, not to a
    suite that may share the machine."""
    hogs = [
        subprocess.Popen([sys.executable, "-c", "while True: pass"])
        for _ in range(os.cpu_count() or 1)
    ]
    try:
        yield len(hogs)
    finally:
        for hog in hogs:
            hog.kill()
        for hog in hogs:
            hog.wait()


def test_high_cpu_contention_does_not_change_the_outcome(cpu_contention: int) -> None:
    with start_worker("--interval", "0.2", url=_UNREACHABLE) as w:
        _, returncode, err = _graceful_cycle(w)
    _assert_graceful(returncode, err, passes=2)


@pytest.fixture
def slow_failing_database() -> Iterator[str]:
    """The relevant database contention: the worker's database is unreachable
    by design, so contention means its failure arrives slowly. A local listener
    accepts every connection, holds it, then closes it without a word."""
    hold = 1.0
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(16)
    server.settimeout(0.1)
    stop = threading.Event()
    held: list[threading.Thread] = []

    def serve_one(conn: socket.socket) -> None:
        with conn:
            stop.wait(hold)

    def accept_loop() -> None:
        while not stop.is_set():
            try:
                conn, _ = server.accept()
            except TimeoutError:
                continue
            t = threading.Thread(target=serve_one, args=(conn,), daemon=True)
            held.append(t)
            t.start()

    acceptor = threading.Thread(target=accept_loop, daemon=True)
    acceptor.start()
    try:
        yield f"postgresql+psycopg://nquiry:x@127.0.0.1:{server.getsockname()[1]}/none"
    finally:
        stop.set()
        acceptor.join()
        for t in held:
            t.join()
        server.close()


def test_a_slowly_failing_database_does_not_change_the_outcome(
    slow_failing_database: str,
) -> None:
    with start_worker("--interval", "0.2", url=slow_failing_database) as w:
        w.wait_ready()
        two_passes = w.wait_unavailable_passes(2)
        returncode, err = w.stop(signal.SIGTERM)
    # each failing pass was held by the listener: contention was real
    assert two_passes >= 1.0
    _assert_graceful(returncode, err, passes=2)


# ------------------------------------------------------------ readiness never reached


def test_readiness_never_reached_fails_at_the_bound_with_a_diagnostic() -> None:
    bound = 1.0
    with WorkerProcess(gated_worker_argv("--interval", "0.2", gated=True), url=_UNREACHABLE) as w:
        started = time.monotonic()
        with pytest.raises(NotObserved, match="readiness not observed within the 1 s fail bound"):
            w.wait_ready(bound=bound)
        waited = time.monotonic() - started
    assert bound <= waited < bound + 5.0  # bounded: a failure, never a hang


def test_a_worker_that_exits_before_readiness_fails_at_once() -> None:
    """No database configured: the worker refuses to start (exit 2). The wait
    fails at once with the exit status. It does not sit out the bound."""
    with start_worker("--interval", "0.2", url="") as w:
        started = time.monotonic()
        with pytest.raises(NotObserved, match=r"exited before readiness .*returncode=2"):
            w.wait_ready()
        assert time.monotonic() - started < 30.0


# ------------------------------------------------------------ cleanup


def test_cleanup_reaps_a_running_worker_and_its_readers() -> None:
    """A test that fails between start and stop still leaves nothing behind:
    leaving the context kills, reaps and joins (residue checked by the
    autouse fixture)."""
    with pytest.raises(RuntimeError, match="test body failed"):  # noqa: SIM117
        with start_worker("--interval", "0.2", url=_UNREACHABLE) as w:
            w.wait_ready()
            raise RuntimeError("test body failed")
    assert w.proc.returncode == -signal.SIGKILL
    assert not w.readers_alive()
    assert w.proc.stderr is not None and w.proc.stderr.closed


def test_cleanup_is_idempotent_after_a_graceful_stop() -> None:
    with start_worker("--interval", "0.2", url=_UNREACHABLE) as w:
        w.wait_ready()
        returncode, _ = w.stop(signal.SIGTERM)
        w.close()
    assert returncode == 0
    assert not w.readers_alive()
