#!/usr/bin/env bash
# ORANGE proof databases: canonical NQUIRY sequence (createdb -> db_roles.sql -> verify_migrations.py)
# Human Authority (2026-09-30): create nquiry_proof_serial_test; migrate gw0..gw3 independently.
# Success = the literal MIGRATION_LIVE_CHECK::PASS line, never exit code 0 alone.
set -u
N=/home/codi/Entwicklung/nquiry
V=$N/.venv-proof313-orange
O=$N/worktrees/orange-proof-infra
P="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # proof-infrastructure root (lineage)
OUT=${ORANGE_DB_OUT:-$P/evidence/db_$(date +%Y%m%dT%H%M%S)}
mkdir -p "$OUT"
EXPECTED_HEAD=e8c2a5f1b7d4
ALLOW=(nquiry_proof_serial_test nquiry_proof_gw0_test nquiry_proof_gw1_test nquiry_proof_gw2_test nquiry_proof_gw3_test)
export PGPASSWORD=nquiry_local_dev_only
PGC=(-h 127.0.0.1 -p 15432 -U nquiry)

allowed() { local d; for d in "${ALLOW[@]}"; do [[ "$1" == "$d" ]] && return 0; done; return 1; }
url() { echo "postgresql+psycopg://nquiry:nquiry_local_dev_only@127.0.0.1:15432/$1"; }

migrate() {
  local db=$1
  allowed "$db" || { echo "REFUSED: $db not in allowlist"; return 1; }
  local log="$OUT/verify_migrations_$db.log"
  ( cd "$O" && env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 DATABASE_URL="$(url "$db")" \
      "$V/bin/python" scripts/verify_migrations.py ) > "$log" 2>&1
  local rc=$?
  cat "$log"
  if grep -q "^MIGRATION_LIVE_CHECK::PASS (db head matches {'$EXPECTED_HEAD'})" "$log" && [[ $rc -eq 0 ]]; then
    echo "RESULT $db: PASS (rc=$rc, literal PASS line, head $EXPECTED_HEAD)"
  else
    echo "RESULT $db: FAIL (rc=$rc)"; return 1
  fi
}

case "${1:-}" in
  create-serial)
    db=nquiry_proof_serial_test
    allowed "$db" || exit 1
    if [[ -n "$(psql "${PGC[@]}" -d postgres -Atc "select 1 from pg_database where datname='$db'")" ]]; then
      echo "REFUSED: $db already exists"; exit 1; fi
    createdb "${PGC[@]}" "$db" && echo "createdb $db: OK"
    psql "${PGC[@]}" -d "$db" -v ON_ERROR_STOP=1 -q -f "$O/infra/local/db_roles.sql" && echo "db_roles.sql on $db: OK"
    ;;
  migrate) shift; rc=0; for db in "$@"; do migrate "$db" || rc=1; done; exit $rc ;;
  *) echo "usage: $0 create-serial | migrate <db>..."; exit 2 ;;
esac
