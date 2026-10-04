#!/usr/bin/env bash
# ORANGE governed parallel proof (Human Authority "PARALLEL PROOF EXECUTION", 2026-10-01).
# XDIST partition: 2235 nodes (serial_partition_selectors.txt deselected), -n 4 --dist load --max-worker-restart=0, gwN -> nquiry_proof_gwN_test.
# SERIAL partition: the 4 nodes of serial_partition_selectors.txt -> nquiry_proof_serial_test.
# Phases: pre | xdist | serial | post. Claim ceiling: 2235 parallel + 4 serial = 2239 coverage.
set -u
N=/home/codi/Entwicklung/nquiry
V=$N/.venv-proof313-orange
O=$N/worktrees/orange-proof-infra
P="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # proof-infrastructure root = this script's directory (lineage)
PYC=$V/orange-proof/pycache  # runtime bytecode cache (env-owned, never versioned)
export PYC  # TF-PX-05: H is serialized into `bash -c` via declare -f; an unexported PYC became an EMPTY prefix there
OUT=${ORANGE_PARALLEL_DIR:?set ORANGE_PARALLEL_DIR to a NEW evidence directory (committed evidence is never overwritten)}
FROZEN=e0a6b3b25d4309d16d6e3db3ee0958183a279dfd
BASE="postgresql+psycopg://nquiry:nquiry_local_dev_only@127.0.0.1:15432/"
mapfile -t SERIAL_SELECTORS < "$P/serial_partition_selectors.txt"
DESELECT=(); for s in "${SERIAL_SELECTORS[@]}"; do DESELECT+=(--deselect "$s"); done
export PGPASSWORD=nquiry_local_dev_only
PSQL=(psql -h 127.0.0.1 -p 15432 -U nquiry -d "${ORANGE_CATALOG_DB:-nquiry_proof_serial_test}" -At)  # catalog via a PROOF db only
H() { env -u DATABASE_URL -u PYTHONPATH -u PYTHONDONTWRITEBYTECODE -u NQUIRY_ENVIRONMENT -u NQUIRY_AI_PROVIDER \
        -u NQUIRY_RUN_REAL_COMMIT_TESTS -u COVERAGE_PROCESS_START -u ORANGE_XDIST_LANE -u ORANGE_DB_BASE \
        -u ORANGE_BINDING_EVIDENCE PYTHONNOUSERSITE=1 PYTHONPYCACHEPREFIX=$PYC "$@"; }
mkdir -p "$OUT"
stage_exit() { [ "$(tr -d '[:space:]' < "$1" 2>/dev/null)" = 0 ] && exit 0; exit 1; }  # STAGE_EXIT_STATUS: process status follows the recorded exit code (0 -> 0; nonzero, absent or garbage -> 1; raw code stays in the file)

tree_hash() { (cd "$O" && find . -path ./.git -prune -o -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1); }
inventory() {
  "${PSQL[@]}" -c "select datname from pg_database where datname like 'race\_%' order by 1" > "$OUT/$1_race_dbs.txt"
  "${PSQL[@]}" -c "select rolname from pg_roles where rolname like 'zz\_pkg25\_%' order by 1" > "$OUT/$1_zz_roles.txt"
  "${PSQL[@]}" -c "select datname, count(*) from pg_stat_activity where datname like 'nquiry_proof%' and pid<>pg_backend_pid() group by 1 order by 1" > "$OUT/$1_proof_conns.txt"
  echo "$1 race_dbs=$(wc -l < "$OUT/$1_race_dbs.txt") zz_roles=$(wc -l < "$OUT/$1_zz_roles.txt") proof_conns=[$(tr '\n' ' ' < "$OUT/$1_proof_conns.txt")]"
}
state() {
  { echo "HEAD=$(git -C "$O" rev-parse HEAD)"
    echo "status_entries_incl_ignored=$(git -C "$O" status --porcelain --ignored | wc -l)"
    echo "diff_vs_tag=$(git -C "$O" diff --quiet checkpoint-PFC-PCPG-5 && echo none || echo CHANGED)"
    echo "content_sha256=$(tree_hash)"; } > "$OUT/$1_tree.txt"
  cat "$OUT/$1_tree.txt"
  H "$V/bin/python" "$P/env_manifest.py" "$OUT/$1_env_manifest.json"
  (cd "$O" && H "$V/bin/python" -m nquiry_orange_guard) | tee "$OUT/$1_guard.txt"
  (cd "$P" && H env ORANGE_PROOF_DBS_JSON="$OUT/$1_proof_dbs.json" "$V/bin/python" verify_proof_dbs.py) > "$OUT/$1_proof_dbs.txt" 2>&1
  grep -E "::" "$OUT/$1_proof_dbs.txt"; 
}
timed() {  # $1 = label, rest = command
  local label=$1; shift
  date +%s.%N > "$OUT/${label}_t0"; date -Iseconds > "$OUT/${label}_started.txt"
  "$@"; local rc=$?
  date +%s.%N > "$OUT/${label}_t1"; date -Iseconds > "$OUT/${label}_finished.txt"
  echo "$rc" > "$OUT/${label}_exit_code.txt"
  echo "$label exit=$rc wall=$(echo "$(cat "$OUT/${label}_t1") - $(cat "$OUT/${label}_t0")" | bc) s"
}

case "${1:-}" in
  pre)
    [ -n "$(ls -A "$OUT" 2>/dev/null)" ] && { echo "REFUSED: $OUT is not empty (evidence is never overwritten)"; exit 1; }
    [[ "$(git -C "$O" rev-parse HEAD)" == "$FROZEN" ]] || { echo "REFUSED: ORANGE HEAD is not frozen"; exit 1; }
    inventory pre; state pre
    ORANGE_PARTITION_DIR="$OUT/partition" bash "$P/partition.sh"
    grep -E "test_direct_write.py|test_http_dispatch_real_connection_lifecycle.py" "$OUT/partition/full_nodeids.txt" > "$OUT/declared_skips.txt"
    echo "declared skips: $(wc -l < "$OUT/declared_skips.txt")"
    ;;
  xdist)
    mkdir -p "$OUT/binding"
    timed xdist bash -c "cd '$O' && $(declare -f H); H env ORANGE_XDIST_LANE=1 ORANGE_DB_BASE='$BASE' \
        ORANGE_BINDING_EVIDENCE='$OUT/binding' '$V/bin/python' -m pytest -p no:cacheprovider \
        -n 4 --dist load --max-worker-restart=0 $(printf "'%s' " "${DESELECT[@]}") -rA \
        --junitxml='$OUT/xdist_junit.xml' -o junit_family=xunit2 > '$OUT/xdist_run.log' 2>&1"
    tail -1 "$OUT/xdist_run.log"
    stage_exit "$OUT/xdist_exit_code.txt"  # STAGE_EXIT_STATUS
    ;;
  serial)
    timed serial bash -c "cd '$O' && $(declare -f H); H env DATABASE_URL='${BASE}nquiry_proof_serial_test' \
        '$V/bin/python' -m pytest -p no:cacheprovider $(printf "'%s' " "${SERIAL_SELECTORS[@]}") -rA \
        --junitxml='$OUT/serial_junit.xml' -o junit_family=xunit2 > '$OUT/serial_run.log' 2>&1"
    tail -1 "$OUT/serial_run.log"
    stage_exit "$OUT/serial_exit_code.txt"  # STAGE_EXIT_STATUS
    ;;
  post)
    inventory post; state post
    ;;
  *) echo "usage: $0 pre|xdist|serial|post"; exit 2 ;;
esac
