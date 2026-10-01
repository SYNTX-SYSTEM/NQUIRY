#!/usr/bin/env bash
# ORANGE worker<->DB binding falsifiers. Executes NO test: every run is --setup-plan (planning only)
# over the xdist partition. DB contact = the plugin's read-only identity check on gw0..gw3 only.
set -u
N=/home/codi/Entwicklung/nquiry
V=$N/.venv-proof313-orange
O=$N/worktrees/orange-proof-infra
P="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # proof-infrastructure root = this script's directory (lineage)
PYC=$V/orange-proof/pycache  # runtime bytecode cache (env-owned, never versioned)
OUT=${ORANGE_BINDING_OUT:-$P/evidence/binding_$(date +%Y%m%dT%H%M%S)}
[ -e "$OUT" ] && { echo "REFUSED: $OUT exists (evidence is never overwritten)"; exit 1; }; mkdir -p "$OUT"
BASE="postgresql+psycopg://nquiry:nquiry_local_dev_only@127.0.0.1:15432/"
mapfile -t SERIAL_SELECTORS < "$P/serial_partition_selectors.txt"
DESELECT=(); for s in "${SERIAL_SELECTORS[@]}"; do DESELECT+=(--deselect "$s"); done
H() { env -u DATABASE_URL -u PYTHONPATH -u PYTHONDONTWRITEBYTECODE -u NQUIRY_RUN_REAL_COMMIT_TESTS \
        -u ORANGE_XDIST_LANE -u ORANGE_DB_BASE PYTHONNOUSERSITE=1 PYTHONPYCACHEPREFIX=$PYC "$@"; }
plan() {  # $1 = case name, $2.. = extra env assignments then pytest args after --
  local name=$1; shift
  local envs=(); while [[ $# -gt 0 && $1 != "--" ]]; do envs+=("$1"); shift; done; shift
  (cd "$O" && H env "${envs[@]}" "$V/bin/python" -m pytest -p no:cacheprovider --setup-plan -q "$@") \
      > "$OUT/$name.txt" 2>&1
  local rc=$?
  echo "$name exit=$rc :: $(grep -m1 -oE 'REFUSED[^;]{0,150}|Different tests[^.]*|[0-9]+ (passed|skipped|errors?)[^=]*' "$OUT/$name.txt")"
}
LANE=(ORANGE_XDIST_LANE=1 ORANGE_DB_BASE=$BASE)

echo "== P1 lane on, -n 4, xdist partition: each worker bound to its own proof DB (identity verified)"
plan P1_bound "${LANE[@]}" ORANGE_BINDING_EVIDENCE=$OUT/p1 -- -n 4 "${DESELECT[@]}"
for f in "$OUT"/p1/binding_gw*.json; do python3 -c "import json,sys;d=json.load(open(sys.argv[1]));o=d['observed'];print(' ',d['workerid'],'pid',d['pid'],'->',d['database'],'| current_database',o['current_database'],'head',o['head'],'foreign',o['foreign_connections'],'nonempty',o['nonempty_tables'])" "$f"; done
python3 - "$OUT/p1" <<'EOF'
import json, pathlib, sys
d = [json.loads(p.read_text()) for p in sorted(pathlib.Path(sys.argv[1]).glob("binding_gw*.json"))]
ids = sorted(x["workerid"] for x in d); dbs = [x["database"] for x in d]; pids = {x["pid"] for x in d}
ok = ids == ["gw0","gw1","gw2","gw3"] and len(set(dbs)) == 4 and len(pids) == 4 and all(
    x["observed"]["current_database"] == x["database"] for x in d)
print("P1_DISTINCT_WORKERS_DISTINCT_DBS::" + ("PASS" if ok else "FAIL"), ids, "distinct dbs", len(set(dbs)), "distinct pids", len(pids))
EOF
echo "== N1 -n 4 WITHOUT the lane -> every worker REFUSED (no shared DATABASE_URL fallback)"
plan N1_no_lane -- -n 4 "${DESELECT[@]}"
echo "== N2 -n 5 -> gw4 REFUSED (not in allowlist)"
plan N2_five_workers "${LANE[@]}" -- -n 5 "${DESELECT[@]}"
echo "== N3 controller DATABASE_URL set (would be shared) -> controller REFUSED before any worker starts"
plan N3_controller_url "${LANE[@]}" DATABASE_URL=${BASE}nquiry_proof_serial_test -- -n 4 "${DESELECT[@]}"
echo "== N4 NQUIRY_RUN_REAL_COMMIT_TESTS=1 -> REFUSED"
plan N4_real_commit "${LANE[@]}" NQUIRY_RUN_REAL_COMMIT_TESTS=1 -- -n 4 "${DESELECT[@]}"
echo "== N5 base URL not the proof cluster -> REFUSED before any connection"
plan N5_foreign_base ORANGE_XDIST_LANE=1 ORANGE_DB_BASE=postgresql+psycopg://nquiry:x@127.0.0.1:15433/ -- -n 4 "${DESELECT[@]}"
echo "== N6 pure identity function: wrong db / wrong head / foreign connection / dirty -> each REFUSED"
(cd "$P" && H "$V/bin/python" - <<'EOF'
from nquiry_orange_workerdb import identity_problems, WORKER_DB
good = {"current_database": "nquiry_proof_gw0_test", "head": ["e8c2a5f1b7d4"], "foreign_connections": 0, "nonempty_tables": {}}
cases = {"good": good,
 "wrong_db": {**good, "current_database": "nquiry_proof_gw1_test"},
 "wrong_head": {**good, "head": ["f6b2c4d9a318"]},
 "foreign_connection": {**good, "foreign_connections": 1},
 "dirty": {**good, "nonempty_tables": {"workspaces": 1}}}
res = {k: identity_problems("nquiry_proof_gw0_test", v) for k, v in cases.items()}
ok = res["good"] == [] and all(res[k] for k in cases if k != "good")
print("N6_IDENTITY_FUNCTION::" + ("PASS" if ok else "FAIL"), {k: len(v) for k, v in res.items()})
print("MAP_INJECTIVE::" + ("PASS" if len(set(WORKER_DB.values())) == 4 else "FAIL"), WORKER_DB)
EOF
)
echo "== N7 serial mode (no xdist): plugin inert, explicit DATABASE_URL honoured, no worker binding"
plan N7_serial_inert DATABASE_URL=${BASE}nquiry_proof_serial_test -- "${SERIAL_SELECTORS[@]}"
echo "== TREE ORANGE entries=$(git -C "$O" status --porcelain --ignored | wc -l)"
