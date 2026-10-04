#!/usr/bin/env bash
# AUTH × CYAN cross-lineage REAL-STACK lane (AUTH/CYAN-ACCOUNT-01).
#
# THIS web (apps/web of this checkout, the CYAN lineage) against the REAL PURPLE
# API served from the AUTH checkout (PURPLE_ROOT, branch auth-identity), the
# real PostgreSQL that checkout's migrations target (DATABASE_URL), a real
# browser. No mocking (the lane's global setup refuses it).
#
#   PURPLE API  :18461  NQUIRY_ENVIRONMENT=TEST · the local test issuer (24 §27.1)
#                       · SELF_REGISTRATION_ALLOWED (so PROVIDER_BOOTSTRAP is reachable)
#                       · allowed origin = this web · authentication persistence as auth_runtime
#   CYAN web    :13480  NEXT_PUBLIC_API_BASE_URL -> the API (no mount)
#
# Env: PURPLE_ROOT (required), DATABASE_URL (required; a REAL database, never a
# pytest proof database), PYTHON (default: PURPLE_ROOT/../../.venv python or
# python3). Extra arguments go to Playwright (e.g. --project=desktop).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
: "${PURPLE_ROOT:?PURPLE_ROOT must be the auth-identity checkout}"
: "${DATABASE_URL:?DATABASE_URL must point at a migrated PostgreSQL}"
case "$DATABASE_URL" in
  *nquiry_purple_test*|*nquiry_test*) echo "refusing: $DATABASE_URL is a pytest proof database" >&2; exit 2 ;;
esac
PYTHON="${PYTHON:-$([ -x "$PURPLE_ROOT/../../.venv/bin/python" ] && echo "$PURPLE_ROOT/../../.venv/bin/python" || echo python3)}"
API_PORT="${AUTH_CYAN_API_PORT:-18461}"
WEB_PORT="${AUTH_CYAN_WEB_PORT:-13480}"
LOG_DIR="${LOG_DIR:-$ROOT/apps/web/test-results/auth-cyan-real-logs}"
mkdir -p "$LOG_DIR"
export DATABASE_URL
export PYTHONPATH="$PURPLE_ROOT/packages:$PURPLE_ROOT/apps/api/src:$PURPLE_ROOT/apps/worker/src"
(cd "$PURPLE_ROOT" && "$PYTHON" scripts/verify_migrations.py)

# Each server runs in its own process group (setsid) so the whole chain ends with it.
pids=()
cleanup() { for p in "${pids[@]}"; do kill -- "-$p" 2>/dev/null || kill "$p" 2>/dev/null || true; done; }
trap cleanup EXIT

(cd "$PURPLE_ROOT" && \
NQUIRY_ENVIRONMENT=TEST \
NQUIRY_AUTH_PROVIDER_MODE=test \
NQUIRY_EMAIL_DELIVERY_MODE=capture \
NQUIRY_ACCOUNT_CREATION_POLICY=SELF_REGISTRATION_ALLOWED \
NQUIRY_ALLOWED_ORIGINS="http://localhost:${WEB_PORT}" \
NQUIRY_PUBLIC_API_BASE_URL="http://localhost:${API_PORT}" \
NQUIRY_PUBLIC_WEB_BASE_URL="http://localhost:${WEB_PORT}" \
NQUIRY_AUTH_DATABASE_URL="${AUTH_DATABASE_URL:-$(printf '%s' "$DATABASE_URL" | sed -E 's#//[^:]+:[^@]+@#//auth_runtime:auth_runtime_local_dev_only@#')}" \
exec setsid "$PYTHON" -m uvicorn nquiry_api.main:app --host 127.0.0.1 --port "$API_PORT" >"$LOG_DIR/api.log" 2>&1) &
pids+=($!)
(cd "$ROOT/apps/web" && NEXT_PUBLIC_API_BASE_URL="http://localhost:${API_PORT}" exec setsid npx next dev --port "$WEB_PORT" >"$LOG_DIR/web.log" 2>&1) &
pids+=($!)
for _ in $(seq 1 120); do
  if curl -sf "http://localhost:${API_PORT}/healthz" >/dev/null && curl -sf "http://localhost:${WEB_PORT}/login" >/dev/null; then break; fi
  sleep 1
done

cd "$ROOT/apps/web"
REAL_STACK_PYTHON="$PYTHON" \
REAL_STACK_REPO_ROOT="$PURPLE_ROOT" \
REAL_STACK_API_URL="http://localhost:${API_PORT}" \
REAL_STACK_WEB_URL="http://localhost:${WEB_PORT}" \
NQUIRY_ENVIRONMENT=TEST \
npx playwright test --config playwright.real-stack.config.ts tests/real-stack/cy09-account-security.real.spec.ts "$@"
