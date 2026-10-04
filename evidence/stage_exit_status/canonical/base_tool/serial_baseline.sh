#!/usr/bin/env bash
# ORANGE serial proof baseline (Human Authority: SERIAL PROOF BOUNDARY, 2026-09-30).
# Phases: pre | run | post. Target DB: nquiry_proof_serial_test ONLY. No xdist.
set -u
N=/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage/evidence/stage_exit_status/canonical/root
V=$N/.venv-proof313-orange
O=$N/worktrees/orange-proof-infra
P="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # proof-infrastructure root = this script's directory (lineage)
PYC=$V/orange-proof/pycache  # runtime bytecode cache (env-owned, never versioned)
OUT=${ORANGE_SERIAL_DIR:?set ORANGE_SERIAL_DIR to a NEW evidence directory (committed evidence is never overwritten)}
DB=nquiry_proof_serial_test
URL="postgresql+psycopg://nquiry:nquiry_local_dev_only@127.0.0.1:15432/$DB"
FROZEN=e0a6b3b25d4309d16d6e3db3ee0958183a279dfd
export PGPASSWORD=nquiry_local_dev_only
PSQL=(psql -h 127.0.0.1 -p 15432 -U nquiry -d "${ORANGE_CATALOG_DB:-nquiry_proof_gw0_test}" -At)  # catalog via a PROOF db only
H() { env -u PYTHONPATH -u NQUIRY_ENVIRONMENT -u NQUIRY_AI_PROVIDER -u NQUIRY_RUN_REAL_COMMIT_TESTS \
        -u COVERAGE_PROCESS_START PYTHONNOUSERSITE=1 ${ORANGE_BYTECODE_ENV:-PYTHONDONTWRITEBYTECODE=1} "$@"; }
mkdir -p "$OUT"

tree_hash() {
  (cd "$O" && find . -path ./.git -prune -o -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1)
}
inventory() {  # $1 = pre|post
  "${PSQL[@]}" -c "select datname from pg_database where datname like 'race\_%' order by 1" > "$OUT/$1_race_dbs.txt"
  "${PSQL[@]}" -c "select rolname from pg_roles where rolname like 'zz\_pkg25\_%' order by 1" > "$OUT/$1_zz_roles.txt"
  "${PSQL[@]}" -c "select datname, count(*) from pg_stat_activity where datname like 'nquiry_proof%' and pid<>pg_backend_pid() group by 1 order by 1" > "$OUT/$1_proof_conns.txt"
  echo "$1 race_dbs=$(wc -l < "$OUT/$1_race_dbs.txt") zz_roles=$(wc -l < "$OUT/$1_zz_roles.txt") proof_conns=[$(tr '\n' ' ' < "$OUT/$1_proof_conns.txt")]"
}
state() {  # $1 = pre|post
  echo "HEAD=$(git -C "$O" rev-parse HEAD)" > "$OUT/$1_tree.txt"
  echo "status_entries_incl_ignored=$(git -C "$O" status --porcelain --ignored | wc -l)" >> "$OUT/$1_tree.txt"
  echo "diff_vs_tag=$(git -C "$O" diff --quiet checkpoint-PFC-PCPG-5 && echo none || echo CHANGED)" >> "$OUT/$1_tree.txt"
  echo "content_sha256=$(tree_hash)" >> "$OUT/$1_tree.txt"
  cat "$OUT/$1_tree.txt"
  H "$V/bin/python" "$P/env_manifest.py" "$OUT/$1_env_manifest.json"
  (cd "$O" && H "$V/bin/python" -m nquiry_orange_guard) | tee "$OUT/$1_guard.txt"
  (cd "$P" && H env ORANGE_PROOF_DBS_JSON="$OUT/$1_proof_dbs.json" "$V/bin/python" verify_proof_dbs.py) > "$OUT/$1_proof_dbs.txt" 2>&1
  grep -E "::" "$OUT/$1_proof_dbs.txt"
  
}

case "${1:-}" in
  pre)
    [ -n "$(ls -A "$OUT" 2>/dev/null)" ] && { echo "REFUSED: $OUT is not empty (evidence is never overwritten)"; exit 1; }
    [[ "$(git -C "$O" rev-parse HEAD)" == "$FROZEN" ]] || { echo "REFUSED: ORANGE HEAD is not frozen"; exit 1; }
    inventory pre
    state pre
    (cd "$O" && H env DATABASE_URL="$URL" "$V/bin/python" -m pytest -p no:cacheprovider --collect-only -q) \
      > "$OUT/pre_collect_raw.txt" 2>&1
    grep "::" "$OUT/pre_collect_raw.txt" | sort > "$OUT/collected_nodeids.txt"
    echo "collected: $(wc -l < "$OUT/collected_nodeids.txt") ($(tail -1 "$OUT/pre_collect_raw.txt"))"
    ;;
  run)
    date -Iseconds > "$OUT/run_started.txt"
    (cd "$O" && H env DATABASE_URL="$URL" "$V/bin/python" -m pytest -p no:cacheprovider -rA \
        --junitxml="$OUT/junit.xml" -o junit_family=xunit2) > "$OUT/run.log" 2>&1
    echo $? > "$OUT/run_exit_code.txt"
    date -Iseconds > "$OUT/run_finished.txt"
    echo "exit=$(cat "$OUT/run_exit_code.txt")"; tail -1 "$OUT/run.log"
    ;;
  post)
    inventory post
    state post
    ;;
  *) echo "usage: $0 pre|run|post"; exit 2 ;;
esac
