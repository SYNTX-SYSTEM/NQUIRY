"""SWU-PX-03 load-contention proof (out of suite). NEW = successor node, OLD = verbatim PCPG-5 consumer witness."""
import os, subprocess, sys, time, tempfile, pathlib, json
ROOT = pathlib.Path(os.path.expanduser("~/Entwicklung/nquiry/worktrees/swu-px-03"))
PY = os.path.expanduser("~/Entwicklung/nquiry/.venv-swu-px-03/bin/python")
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=False)
HERE = pathlib.Path(__file__).resolve().parent
NEW = "tests/e2e/test_pfc_f09_1_technical_failure.py::test_worker_loop_survives_a_database_outage_and_stops_gracefully"
OLD = str(HERE / "witness/test_old_fixed_window_consumer.py")
N = int(os.environ.get("LOAD_RUNS", "10"))
base_env = {k: v for k, v in os.environ.items() if k not in ("DATABASE_URL", "PYTHONPATH", "PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE")}
base_env.update(PYTHONNOUSERSITE="1", SWU_ROOT=str(ROOT))
warm_prefix = OUT / "pyc-warm"

def launch(which, cold, tag):
    env = dict(base_env)
    if cold:   # nothing cached, nothing written: every process compiles from source
        env["PYTHONPYCACHEPREFIX"] = tempfile.mkdtemp(prefix="cold-", dir=OUT); env["PYTHONDONTWRITEBYTECODE"] = "1"
    else:
        env["PYTHONPYCACHEPREFIX"] = str(warm_prefix)
    target = NEW if which == "NEW" else OLD
    log = open(OUT / f"{tag}.log", "w")
    return subprocess.Popen([PY, "-m", "pytest", "-p", "no:cacheprovider", "-q", "--rootdir", str(ROOT), target],
                            cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT), time.monotonic(), log

def foreign_suite():
    """Another lane's pytest (any interpreter but ours)."""
    for proc in pathlib.Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            argv = (proc / "cmdline").read_bytes().decode(errors="replace").split("\0")
        except OSError:
            continue
        exe = os.path.basename(argv[0]) if argv and argv[0] else ""
        is_pytest = (exe.startswith("python") and "-m" in argv and argv[argv.index("-m") + 1:argv.index("-m") + 2] == ["pytest"]) or exe in ("pytest", "py.test")
        if is_pytest and ".venv-swu-px-03" not in argv[0]:
            return f"{proc.name}: {' '.join(argv)[:120]}"
    return None

def hogs_start(k):
    return [subprocess.Popen([sys.executable, "-c", "while True: pass"]) for _ in range(k)]

def hogs_stop(hs):
    for h in hs: h.kill()
    for h in hs: h.wait()

CPU = os.cpu_count() or 1
CONDITIONS = [  # name, cold, hogs, concurrency
    ("C0_idle_warm", False, 0, 1),
    ("C1_cold_start", True, 0, 1),
    ("C2_cpu2x_warm", False, 2 * CPU, 1),
    ("C3_cpu2x_cold", True, 2 * CPU, 1),
    ("C4_cpu2x_cold_4concurrent", True, 2 * CPU, 4),
]
rows = []
# warm the warm prefix once (not measured)
for which in ("NEW", "OLD"):
    p, _, log = launch(which, False, f"warmup_{which}"); p.wait(); log.close()
for name, cold, k, conc in CONDITIONS:
    hs = hogs_start(k)
    try:
        for i in range(N if conc == 1 else max(1, N // 4)):
            f = foreign_suite()
            if f:
                hogs_stop(hs); hs = []
                (OUT / "runs.json").write_text(json.dumps(rows, indent=1))
                print(f"STOP: foreign suite running ({f}); hogs reaped; LOAD_CONTENTION_PROOF::ABORTED", flush=True)
                sys.exit(3)
            for which in ("NEW", "OLD"):
                procs = [launch(which, cold, f"{name}_{which}_{i}_{j}") for j in range(conc)]
                for j, (p, t0, log) in enumerate(procs):
                    rc = p.wait(timeout=900); dt = time.monotonic() - t0; log.close()
                    rows.append(dict(condition=name, which=which, run=f"{i}.{j}", rc=rc, seconds=round(dt, 2), load=os.getloadavg()[0]))
                    print(f"{name}\t{which}\t{i}.{j}\trc={rc}\t{dt:.1f}s\tload1={os.getloadavg()[0]:.1f}", flush=True)
    finally:
        hogs_stop(hs)
(OUT / "runs.json").write_text(json.dumps(rows, indent=1))
summary = {}
for r in rows:
    s = summary.setdefault((r["condition"], r["which"]), [0, 0]); s[0] += 1; s[1] += r["rc"] != 0
print("\nSUMMARY condition\twhich\truns\tfailures")
for (c, w), (n, f) in summary.items(): print(f"{c}\t{w}\t{n}\t{f}")
new_fail = sum(f for (c, w), (n, f) in summary.items() if w == "NEW")
old_fail = sum(f for (c, w), (n, f) in summary.items() if w == "OLD")
print(f"NEW_CONSUMER_FAILURES={new_fail}  OLD_WITNESS_FAILURES={old_fail}")
print("LOAD_CONTENTION_PROOF::" + ("PASS" if new_fail == 0 else "FAIL"))
print("LOAD_CONDITIONS_EFFECTIVE::" + ("YES (old consumer broken under load)" if old_fail else "NOT DEMONSTRATED (old consumer never broke)"))
