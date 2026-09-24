# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.6 — Isolated real-stack environment + L7 spec (PREPARED, NOT RUN)

## Mission
Prepare L6/L7 in an environment isolated from the running F03 stack (SF01-HD-2) without touching the
contact zone. No Field PASS until it has run.

## Boundary found
The API's CORS origin is fixed to `http://localhost:3000` (`apps/api/src/nquiry_api/main.py:91`).
- `apps/api` is outside SF-01's scope, so "same stack on other host ports" would break every credentialed browser call unless the API were changed.
- Resolution (Case 2: a functionally interchangeable isolation means, changing no semantics): **network-namespace isolation**. The ports keep their numbers but are private to the SF-01 namespace; no host port is published.

## Files changed (all NEW)
- `infra/sf01/compose.yaml`
  - Project `nquiry-sf01`; own volume `sf01_postgres_data`; **no host ports**.
  - `runner` runs this tree's API (:8000), Next.js (:3000) and Chromium inside one private namespace; `postgres` is the isolated DB.
- `infra/sf01/runner.Dockerfile`
  - Python 3.13 (pyproject) + Node 22 binaries copied from the official image (no curl-to-shell).
  - `pip install .`, `npm ci` from the lockfile, Playwright Chromium.
- `infra/sf01/runner.Dockerfile.dockerignore`: Dockerfile-scoped, so no other image's build context changes.
- `infra/sf01/run-in-namespace.sh`: DB principals (`db_roles.sql`) → migrations → uvicorn → next dev → the whole real-stack lane (F02 regression + SF-01), desktop + mobile.
- `scripts/run_sf01_real_stack.sh`: host entry.
  - Guards, before anything starts: resolved project == `nquiry-sf01`, and no service publishes a port.
  - Fresh SF-01 DB per run (removes only `nquiry-sf01` volumes). Output goes to `apps/web/test-results/sf01-real-stack/` (gitignored).
- `apps/web/tests/real-stack/sf01-field.real.spec.ts` (2 tests × 2 projects; no network interception, global setup enforces it):
  - trace rebuilt identically after reload;
  - Challenge relation unavailable for the Owner, possible for the Facilitator;
  - Session relation unavailable → possible only through a real grant;
  - no Session coordinate before CreateSession;
  - commit markers after the re-read;
  - authority proof by keyboard;
  - **real transport loss** (browser offline mode): unknown consequence → last-confirmed view → manual re-read → same-intent repeat → exactly ONE Challenge;
  - axe 0 serious/critical and no overflow on every SF-01 surface;
  - reduced motion keeps meaning (malformed id → `rejected`, verified in `http/workspaces.py` → `_malformed_input_response`).

## Validation done (no containers started)
- `bash -n` on both scripts: OK.
- `docker compose -p nquiry-sf01 -f infra/sf01/compose.yaml config`: name `nquiry-sf01`, services `postgres, runner`, ports none, volume `sf01_postgres_data`.
- Running containers after this WU: only the F03 project's (`nquiry-api-1`, `nquiry-postgres-1`, `nquiry-web-1`), untouched.
- tsc and eslint clean on the new spec.

## Not yet proven (must be proven by running)
Image build, migrations on an empty DB, Chromium in the container, CORS inside the namespace, and every L7 assertion. The first run may surface environment defects; they would be fixed inside `infra/sf01/` only.

## Git state
Uncommitted.

## Result
PREPARED in this WU. Executed in WU-SF01.7: 10/10 GREEN twice (the second run on the final tree after
one application and one environment repair). The "Not yet proven" list above is now proven; see WU-SF01.7.
