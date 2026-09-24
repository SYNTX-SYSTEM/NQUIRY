#!/usr/bin/env bash
# Runs INSIDE the `nquiry-sf01` runner container. `localhost` here is this
# container's private network namespace: API :8000 and web :3000 are this
# tree's own processes, and the database is the isolated `postgres` service.
#
# Sequence: DB principals → migrations → real FastAPI → real Next.js → the
# whole real-stack Playwright lane (F02 regression + SF-01 proof), desktop and
# mobile. Extra Playwright arguments pass through.
set -euo pipefail
cd /repo

: "${DATABASE_URL:?DATABASE_URL must point at the isolated postgres service}"
export PYTHONPATH="/repo/packages:/repo/apps/api/src:/repo/apps/worker/src"
OUT_DIR="/repo/apps/web/test-results"
LOG_DIR="$OUT_DIR/sf01-real-stack-logs"
mkdir -p "$LOG_DIR"
# Proof output is a bind mount owned by the host user (the host wrapper creates
# it). This container runs as root, so hand everything written here back to the
# mount's owner on exit. Otherwise other lanes cannot clean `test-results/`.
OUT_OWNER="$(stat -c '%u:%g' "$OUT_DIR")"
release_output() { chown -R "$OUT_OWNER" "$OUT_DIR" 2>/dev/null || true; }

for _ in $(seq 1 60); do
  if pg_isready -h postgres -U nquiry >/dev/null 2>&1; then break; fi
  sleep 1
done
PGPASSWORD=nquiry_local_dev_only psql -h postgres -U nquiry -d nquiry -v ON_ERROR_STOP=1 -q -f infra/local/db_roles.sql
python scripts/verify_migrations.py

python -m uvicorn nquiry_api.main:app --host 127.0.0.1 --port 8000 >"$LOG_DIR/api.log" 2>&1 &
API_PID=$!
(cd apps/web && npx next dev --port 3000 >"$LOG_DIR/web.log" 2>&1) &
WEB_PID=$!
trap 'kill "$API_PID" "$WEB_PID" 2>/dev/null || true; release_output' EXIT

for _ in $(seq 1 180); do
  if curl -sf http://localhost:8000/healthz >/dev/null && curl -sf http://localhost:3000/login >/dev/null; then break; fi
  sleep 1
done

cd apps/web
REAL_STACK_PYTHON=python npx playwright test --config playwright.real-stack.config.ts "$@"
