#!/usr/bin/env bash
# Runs INSIDE the nquiry-sf01-inspect runner container (runtime-only; not part of the repository).
set -euo pipefail
cd /repo
export PYTHONPATH="/repo/packages:/repo/apps/api/src:/repo/apps/worker/src"
for _ in $(seq 1 60); do pg_isready -h postgres -U nquiry >/dev/null 2>&1 && break; sleep 1; done
PGPASSWORD=nquiry_local_dev_only psql -h postgres -U nquiry -d nquiry -v ON_ERROR_STOP=1 -q -f infra/local/db_roles.sql
python scripts/verify_migrations.py
python -m uvicorn nquiry_api.main:app --host 127.0.0.1 --port 8000 >/tmp/api.log 2>&1 &
cd apps/web
NEXT_PUBLIC_API_BASE_URL="${INSPECT_ORIGIN}/api" npx next build >/tmp/web-build.log 2>&1
NEXT_PUBLIC_API_BASE_URL="${INSPECT_ORIGIN}/api" npx next start --hostname 127.0.0.1 --port 3000 >/tmp/web.log 2>&1 &
exec node /inspect/proxy.mjs
