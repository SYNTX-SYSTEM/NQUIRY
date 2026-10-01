#!/usr/bin/env bash
# ORANGE PX-1 falsifiers (environment closure). DB-free: DATABASE_URL is always unset.
# Frozen target: worktrees/orange-proof-infra == checkpoint-PFC-PCPG-5 (e0a6b3b).
set -u
N=/home/codi/Entwicklung/nquiry
V=$N/.venv-proof313-orange
O=$N/worktrees/orange-proof-infra
P="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # proof-infrastructure root (lineage)
NEG=${NEG:-$P/negative-fixtures}
PX1OUT=${ORANGE_PX1_OUT:-$P/evidence/px1_$(date +%Y%m%dT%H%M%S)}; mkdir -p "$PX1OUT"
export PYTHONDONTWRITEBYTECODE=1
H() { env -u DATABASE_URL -u PYTHONPATH -u NQUIRY_ENVIRONMENT -u NQUIRY_AI_PROVIDER -u NQUIRY_RUN_REAL_COMMIT_TESTS PYTHONNOUSERSITE=1 "$@"; }
PY=$V/bin/python
LANE="ORANGE_XDIST_LANE=1 ORANGE_DB_BASE=postgresql+psycopg://nquiry:nquiry_local_dev_only@127.0.0.1:15432/"  # xdist workers only ever run bound (guard >= 1.1.0)
cd "$O" || exit 2

echo "== P1 interpreter"
H $PY -c "import sys,platform;print(sys.executable, platform.python_version(), 'prefix', sys.prefix)"
echo "== P2 user site"
H $PY -c "import site,sys;print('ENABLE_USER_SITE',site.ENABLE_USER_SITE,'no_user_site',sys.flags.no_user_site)"
echo "== P3 test tooling + TestClient dependency origins"
H $PY -c "
import importlib.metadata as m, importlib.util as u
for d,mod in [('pytest','pytest'),('pytest-xdist','xdist'),('execnet','execnet'),('httpx','httpx'),('httpcore','httpcore'),('starlette','starlette'),('fastapi','fastapi')]:
    print(f'{d:14} {m.version(d):10} {u.find_spec(mod).origin}')
print('httpx2 installed:', u.find_spec('httpx2') is not None)"
echo "== P4 TestClient binds the tree-named httpx family (deprecated-fallback warning expected)"
H $PY -c "
import warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    import starlette.testclient as t
print('starlette.testclient.httpx =', t.httpx.__name__, t.httpx.__version__, t.httpx.__file__)
print('warnings:', sorted({type(x.message).__name__ for x in w}))"
echo "== P5 no first-party distribution, no editable finder"
H $PY -c "
import importlib.metadata as m, sys
print('nquiry dist:', [d.metadata['Name'] for d in m.distributions() if d.metadata['Name'].lower()=='nquiry'])
print('editable finders:', [f for f in map(str,sys.meta_path) if '__editable__' in f])"
echo "== P6 guard CLI"
H $PY -m nquiry_orange_guard; echo "exit=$?"
echo "== P7 five runtime-proof scripts: every import resolvable (static, not executed)"
H $PY - <<'EOF'
import ast, importlib.util, pathlib, sys
sys.path.insert(0, "tests/e2e")
bad = []
for f in sorted(pathlib.Path("tests/e2e").glob("*_runtime_proof.py")):
    mods = set()
    for n in ast.walk(ast.parse(f.read_text())):
        if isinstance(n, ast.Import): mods |= {a.name.split(".")[0] for a in n.names}
        if isinstance(n, ast.ImportFrom) and n.level == 0 and n.module: mods.add(n.module.split(".")[0])
    missing = sorted(m for m in mods if m != "__future__" and importlib.util.find_spec(m) is None)
    print(f"{f.name}: {len(mods)} imports, missing={missing}")
    bad += missing
print("RUNTIME_PROOF_SCRIPTS_IMPORTABLE::" + ("PASS" if not bad else "FAIL"))
EOF
echo "== P8 TestClient actually executes over httpx (DB-free apps/api tests, real xdist workers, governed lane)"
H env $LANE $PY -m pytest -p no:cacheprovider -n 2 -q apps/api/tests/test_health.py apps/api/tests/test_cors.py 2>&1 | tail -2; echo "exit=${PIPESTATUS[0]}"
echo "== P9 DB-free full collection of the frozen tree"
H $PY -m pytest -p no:cacheprovider --collect-only -q > "$PX1OUT/collect_orange_env.txt" 2>&1; echo "exit=$?"
tail -1 "$PX1OUT/collect_orange_env.txt"
echo "errors: $(grep -cE '^ERROR ' "$PX1OUT/collect_orange_env.txt")"

echo "== N1 PYTHONNOUSERSITE unset -> REFUSE"
env -u DATABASE_URL -u PYTHONPATH -u PYTHONNOUSERSITE $PY -m nquiry_orange_guard | head -2; echo "exit=${PIPESTATUS[0]}"
echo "== N2 master checkout packages first on PYTHONPATH -> REFUSE"
env -u DATABASE_URL PYTHONNOUSERSITE=1 PYTHONPATH=$N/packages:$N/apps/api/src $PY -m nquiry_orange_guard | head -2; echo "exit=${PIPESTATUS[0]}"
echo "== N3 foreign shadow 'domain' -> REFUSE"
env -u DATABASE_URL PYTHONNOUSERSITE=1 PYTHONPATH=$NEG/shadow $PY -m nquiry_orange_guard | head -2; echo "exit=${PIPESTATUS[0]}"
echo "== N4 master-bound .venv-proof313 interpreter -> REFUSE"
H $N/.venv-proof313/bin/python $P/guard/src/nquiry_orange_guard.py | head -2; echo "exit=${PIPESTATUS[0]}"
echo "== N5 pytest, front-inserted master finder -> REFUSE (exit 4)"
R=$(H env PYTHONPATH=$NEG/plug $PY -m pytest -p no:cacheprovider -p evil_editable -q tests/domain/test_challenge.py 2>&1); rc=$?; echo "$R" | grep -m1 REFUSED; echo "exit=$rc"
echo "== N6 poison only inside real xdist workers (governed lane) -> the IMPORT-ORIGIN GUARD refuses as collection ERROR (exit 1, never 5)"
R=$(H env $LANE PYTHONPATH=$NEG/plug $PY -m pytest -p no:cacheprovider -p evil_worker_only -n 2 -q tests/domain/test_challenge.py 2>&1); rc=$?
echo "$R" | grep -E "errors? in" | tail -1; echo "refused_by_import_origin_guard=$(echo "$R" | grep -c "ORANGE import-origin guard REFUSED") refused_by_binding=$(echo "$R" | grep -c "worker-DB binding REFUSED")"; echo "exit=$rc"
echo "== N7 guard disabled -> poison passes (the guard is what refuses)"
H env PYTHONPATH=$NEG/plug $PY -m pytest -p no:cacheprovider -p no:nquiry_orange_guard -p evil_editable --collect-only -q tests/domain/test_challenge.py 2>&1 | tail -1; echo "exit=${PIPESTATUS[0]}"
echo "== N8 master module loaded after configure -> REFUSE (exit 4)"
H env PYTHONPATH=$NEG/plug $PY -m pytest -p no:cacheprovider -p evil_late_load -q tests/domain/test_challenge.py 2>&1 | grep -m1 "loaded governance"; echo "exit=${PIPESTATUS[0]}"
echo "== CONTROL master-bound .venv-proof313 cannot collect the frozen tree"
H $N/.venv-proof313/bin/python -m pytest -p no:cacheprovider --collect-only -q 2>&1 | tail -1; echo "exit=${PIPESTATUS[0]}"
echo "== TREE ORANGE entries(incl. ignored)=$(git -C "$O" status --porcelain --ignored | wc -l) head=$(git -C "$O" rev-parse HEAD) diff-vs-tag=$(git -C "$O" diff --quiet checkpoint-PFC-PCPG-5 && echo none)"
