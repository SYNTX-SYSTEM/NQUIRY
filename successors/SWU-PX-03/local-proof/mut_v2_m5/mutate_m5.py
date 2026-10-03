"""SWU-PX-03 local mutation run: each mutant is applied to a COPY of the successor tree."""
import os, shutil, subprocess, sys, pathlib
SRC = pathlib.Path(os.path.expanduser("~/Entwicklung/nquiry/worktrees/swu-px-03"))
S = pathlib.Path(sys.argv[1]); PY = os.path.expanduser("~/Entwicklung/nquiry/.venv-swu-px-03/bin/python")
MAIN = "apps/worker/src/nquiry_worker/__main__.py"; SUP = "tests/e2e/worker_readiness_support.py"
T = "tests/e2e/test_swu_px_03_worker_readiness.py::"; N = "tests/e2e/test_pfc_f09_1_technical_failure.py::test_worker_loop_survives_a_database_outage_and_stops_gracefully"
INSTALL = "    signal.signal(signal.SIGTERM, _request_stop)\n    signal.signal(signal.SIGINT, _request_stop)\n"
READY = '    print("nquiry_worker: ready.", file=sys.stderr, flush=True)\n'
MUTANTS = [
  ("M1_readiness_before_handler_installation", MAIN, INSTALL + READY, READY + INSTALL,
   [T+"test_readiness_is_announced_only_after_both_stop_handlers_are_installed"]),
  ("M2_readiness_signal_removed", MAIN, READY, "",
   [N, T+"test_a_stop_right_after_readiness_is_graceful"]),
  ("M3_sigint_handler_not_installed", MAIN, "    signal.signal(signal.SIGINT, _request_stop)\n", "",
   [T+"test_readiness_is_announced_only_after_both_stop_handlers_are_installed", T+"test_a_stop_right_after_readiness_is_graceful"]),
  ("M4_wait_ignores_early_exit", SUP, "                if self._eof:\n", "                if False:\n",
   [T+"test_a_worker_that_exits_before_readiness_fails_at_once"]),
  ("M5_cleanup_does_not_kill", SUP, "            self.proc.kill()\n        self.proc.wait(timeout=FAIL_BOUND_SECONDS)\n", "            pass\n",
   [T+"test_cleanup_reaps_a_running_worker_and_its_readers"]),
]
results = []
for name, rel, old, new, sel in [m for m in MUTANTS if m[0].startswith('M5')]:
    dst = S / "mutants" / name
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(SRC, dst, ignore=shutil.ignore_patterns(".git"))
    p = dst / rel; s = p.read_text(); assert s.count(old) == 1, name
    p.write_text(s.replace(old, new))
    env = {k: v for k, v in os.environ.items() if k not in ("DATABASE_URL", "PYTHONPATH")}
    env.update(PYTHONNOUSERSITE="1", PYTHONPYCACHEPREFIX=str(S / "pyc-mut"))
    r = subprocess.run([PY, "-m", "pytest", "-p", "no:cacheprovider", "-q", "-rfE", *sel],
                       cwd=dst, env=env, capture_output=True, text=True, timeout=900)
    (S / f"{name}.log").write_text(r.stdout + r.stderr)
    summary = [l for l in r.stdout.splitlines() if l.startswith(("FAILED", "ERROR")) or " in " in l and ("passed" in l or "failed" in l)]
    killed = r.returncode == 1 and not any(" passed" in l and "failed" not in l for l in summary[-1:])
    results.append((name, r.returncode, "KILLED" if r.returncode == 1 else "SURVIVED"))
    print(f"== {name}: exit={r.returncode} -> {'KILLED' if r.returncode == 1 else 'SURVIVED'}")
    for l in summary: print("   ", l[:230])
    swept = []
    for proc in pathlib.Path("/proc").iterdir():
        if proc.name.isdigit():
            try:
                if str(dst).encode() in (proc / "environ").read_bytes():
                    os.kill(int(proc.name), 9); swept.append(int(proc.name))
            except OSError:
                pass
    print(f"    residue_swept_after_mutant={swept}")
    shutil.rmtree(dst)
print("MUTATION_RESULT::" + ("PASS" if all(k == "KILLED" for *_, k in results) else "FAIL"), f"({sum(k=='KILLED' for *_,k in results)}/{len(results)} killed)")
