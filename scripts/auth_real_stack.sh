#!/usr/bin/env bash
# AUTH REAL-STACK lane runner (WU-AUTH-14; 24 §21.6 "proven against the real
# browser/API request contract"). Starts, against an already running
# PostgreSQL with migrations applied (DATABASE_URL):
#   real FastAPI (uvicorn) on :18460   NQUIRY_ENVIRONMENT=TEST, test provider,
#                                      capture mail, allowed origin = the web app
#   real Next.js dev server on :13470  NEXT_PUBLIC_API_BASE_URL -> the API
#   a hostile third origin on :13471   tests/real-stack/hostile/ (static)
# then runs apps/web/playwright.auth-real.config.ts and stops everything.
# Pass extra Playwright args after the script name.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
API_PORT="${AUTH_REAL_API_PORT:-18460}"
WEB_PORT="${AUTH_REAL_WEB_PORT:-13470}"
HOSTILE_PORT="${AUTH_REAL_HOSTILE_PORT:-13471}"
: "${DATABASE_URL:?DATABASE_URL must point at a migrated PostgreSQL}"
# The real stack COMMITS (identities, Workspaces, Sessions): never point it at
# the database the rolled-back pytest proof runs on. PURPLE: nquiry_purple_real.
case "$DATABASE_URL" in
  *nquiry_purple_test*|*nquiry_test*) echo "refusing: $DATABASE_URL is a pytest proof database" >&2; exit 2 ;;
esac
export DATABASE_URL
export PYTHONPATH="$ROOT/packages:$ROOT/apps/api/src:$ROOT/apps/worker/src"
LOG_DIR="${LOG_DIR:-$ROOT/apps/web/test-results/auth-real-logs}"
mkdir -p "$LOG_DIR"
cd "$ROOT"
"$PYTHON" scripts/verify_migrations.py

# Each server runs in its own process group (setsid) so that the whole
# npm -> sh -> node chain ends with it; nothing from this run survives it.
pids=()
cleanup() { for p in "${pids[@]}"; do kill -- "-$p" 2>/dev/null || kill "$p" 2>/dev/null || true; done; }
trap cleanup EXIT

NQUIRY_ENVIRONMENT=TEST \
NQUIRY_AUTH_PROVIDER_MODE=test \
NQUIRY_EMAIL_DELIVERY_MODE=capture \
NQUIRY_ALLOWED_ORIGINS="http://localhost:${WEB_PORT}" \
NQUIRY_PUBLIC_API_BASE_URL="http://localhost:${API_PORT}" \
NQUIRY_PUBLIC_WEB_BASE_URL="http://localhost:${WEB_PORT}" \
setsid "$PYTHON" -m uvicorn nquiry_api.main:app --host 127.0.0.1 --port "$API_PORT" >"$LOG_DIR/api.log" 2>&1 &
pids+=($!)
(cd apps/web && NEXT_PUBLIC_API_BASE_URL="http://localhost:${API_PORT}" exec setsid npx next dev --port "$WEB_PORT" >"$LOG_DIR/web.log" 2>&1) &
pids+=($!)
(cd apps/web/tests/real-stack/hostile && exec setsid "$PYTHON" -m http.server "$HOSTILE_PORT" --bind 127.0.0.1 >"$LOG_DIR/hostile.log" 2>&1) &
pids+=($!)
for _ in $(seq 1 120); do
  if curl -sf "http://localhost:${API_PORT}/healthz" >/dev/null \
     && curl -sf "http://localhost:${WEB_PORT}/login" >/dev/null \
     && curl -sf "http://localhost:${HOSTILE_PORT}/attack.html" >/dev/null; then break; fi
  sleep 1
done

cd apps/web
REAL_STACK_PYTHON="$PYTHON" \
REAL_STACK_API_URL="http://localhost:${API_PORT}" \
REAL_STACK_WEB_URL="http://localhost:${WEB_PORT}" \
REAL_STACK_HOSTILE_URL="http://localhost:${HOSTILE_PORT}" \
NQUIRY_ENVIRONMENT=TEST \
npx playwright test --config playwright.auth-real.config.ts "$@"
