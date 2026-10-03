"""WITNESS ONLY (never part of the product): the PCPG-5 consumer, verbatim from
checkpoint-PFC-PCPG-5 tests/e2e/test_pfc_f09_1_technical_failure.py (the
fixed 2.5 s window), run against the successor worker. It shows whether a
load condition is effective, i.e. strong enough to break the old relation."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

_UNREACHABLE = "postgresql+psycopg://nquiry:x@127.0.0.1:1/none"


def _worker(*args: str, url: str) -> subprocess.Popen[str]:
    root = Path(os.environ["SWU_ROOT"])
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(root / p) for p in ("packages", "apps/worker/src"))
    env["DATABASE_URL"] = url
    return subprocess.Popen(
        [sys.executable, "-m", "nquiry_worker", *args],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def test_worker_loop_survives_a_database_outage_and_stops_gracefully() -> None:
    p = _worker("--interval", "0.2", url=_UNREACHABLE)
    time.sleep(2.5)
    p.send_signal(signal.SIGTERM)
    _, err = p.communicate(timeout=30)
    assert p.returncode == 0, err
    assert err.count("DATABASE_UNAVAILABLE") >= 2  # it kept trying, pass after pass
    assert "stopped" in err
