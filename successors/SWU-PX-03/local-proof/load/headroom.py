"""SWU-PX-03: readiness latency vs the 60 s fail bound under C3 (2 x CPU busy + cold start)."""
import os, signal, subprocess, sys, tempfile
from worker_readiness_support import FAIL_BOUND_SECONDS, start_worker
hogs = [subprocess.Popen([sys.executable, "-c", "while True: pass"]) for _ in range(2 * os.cpu_count())]
try:
    for i in range(5):
        os.environ["PYTHONPYCACHEPREFIX"] = tempfile.mkdtemp(prefix="cold-"); os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        with start_worker("--interval", "0.2", url="postgresql+psycopg://nquiry:x@127.0.0.1:1/none") as w:
            ready = w.wait_ready(); passes = w.wait_unavailable_passes(2); rc, err = w.stop(signal.SIGTERM)
        print(f"sample {i}: ready_after={ready:.2f}s two_passes_after_ready={passes:.2f}s rc={rc} stopped={'stopped' in err} "
              f"headroom={FAIL_BOUND_SECONDS - ready:.1f}s load1={os.getloadavg()[0]:.1f}", flush=True)
finally:
    for h in hogs: h.kill()
    for h in hogs: h.wait()
