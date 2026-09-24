#!/usr/bin/env bash
# REAL-STACK browser lane runner (F02 WU-02.5).
# Starts: PostgreSQL (docker compose) -> migrations -> real FastAPI (uvicorn,
# :8000) -> real Next.js dev server (:3000), then runs the real-stack
# Playwright lane (apps/web/playwright.real-stack.config.ts). No mocking.
#
# Env: PYTHON (default: python3), DATABASE_URL (default: local compose DB).
# Pass extra Playwright args after the script name, e.g. --project=desktop.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://nquiry:nquiry_local_dev_only@localhost:15432/nquiry}"
export PYTHONPATH="$ROOT/packages:$ROOT/apps/api/src:$ROOT/apps/worker/src"
LOG_DIR="${LOG_DIR:-$ROOT/apps/web/test-results/real-stack-logs}"
mkdir -p "$LOG_DIR"

cd "$ROOT"
POSTGRES_PORT="${POSTGRES_PORT:-15432}" docker compose -p nquiry up -d postgres >/dev/null
for _ in $(seq 1 60); do
  if docker compose -p nquiry exec -T postgres pg_isready -U nquiry >/dev/null 2>&1; then break; fi
  sleep 1
done
"$PYTHON" scripts/verify_migrations.py

pids=()
cleanup() { for p in "${pids[@]}"; do kill "$p" 2>/dev/null || true; done; }
trap cleanup EXIT

if ! curl -sf http://localhost:8000/healthz >/dev/null; then
  "$PYTHON" -m uvicorn nquiry_api.main:app --host 127.0.0.1 --port 8000 >"$LOG_DIR/api.log" 2>&1 &
  pids+=($!)
fi
if ! curl -sf http://localhost:3000/login >/dev/null; then
  (cd apps/web && npx next dev --port 3000 >"$LOG_DIR/web.log" 2>&1) &
  pids+=($!)
fi
for _ in $(seq 1 120); do
  if curl -sf http://localhost:8000/healthz >/dev/null && curl -sf http://localhost:3000/login >/dev/null; then break; fi
  sleep 1
done

cd apps/web
REAL_STACK_PYTHON="$PYTHON" npx playwright test --config playwright.real-stack.config.ts "$@"
