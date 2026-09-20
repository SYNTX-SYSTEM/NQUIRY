# NQUIRY Backend Runtime Operation

Status: informational runbook, not an architecture document. Originally
described the runtime as it existed after PKG-32 (commit `0884f62`).
**UPDATE (2026-09-20, same day): superseded in part by Architecture 17**
(`docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`) and
its own implementation report
(`docs/implementation/proof-reports/ARCH-17-RUNTIME-MATERIALIZATION.md`)
— two real HTTP routes now exist and are wired to the real backend (see
section 1a below). The worker remains unwired; that part of this
document is still accurate. Read Architecture 17's own document for the
authoritative, current picture; this file keeps only a short pointer
plus the still-valid low-level "how to boot/verify" commands.

## 1. What "the backend" currently is

The repository defines the runtime in `docker-compose.yml`:

- `postgres` — always started, PostgreSQL 17.
- `api`, `worker`, `web` — started only with the `app` profile
  (`docker compose --profile app up`).

As of PKG-32 (commit `0884f62`), the real, implemented, live HTTP/worker
surface was deliberately minimal:

- The FastAPI app (`apps/api/src/nquiry_api/main.py`) exposed exactly
  one route: `GET /healthz`. `apps/api/src/nquiry_api/http/__init__.py`
  and `dispatch/__init__.py` were explicitly documented, empty extension
  points — no package from PKG-00 through PKG-32 was ever assigned the
  job of wiring a Command/Query HTTP dispatch layer. This was a real,
  disclosed architectural gap (see `docs/implementation/proof-reports/PKG-32.md`,
  KNOWN_LIMITATIONS), not a bug.

### 1a. What changed the same day (Architecture 17)

Two real routes are now wired end-to-end through the real
`packages/application` handlers, real boundary/authority chains, and
real PostgreSQL:

- `GET /workspaces/{workspaceId}/sessions/{sessionId}` (new
  `application/session_view_query.py`, the repository's first real
  Query handler)
- `POST /decisions/{decisionId}/decide` (reuses PKG-15's existing
  `record_human_decision` unmodified, via the new
  `application/http_dispatch.py` composition root)

Both use a new deterministic, non-production identity adapter
(`X-Nquiry-Actor-User-Id` / `X-Nquiry-Actor-Class` request headers,
identity only — never authority; see Architecture 17 §
AUTHENTICATION/IDENTITY RESOLUTION CONTRACT) — GAP-14-001 (real
production auth provider selection) remains open. Full detail, the
adversarial test matrix, and the complete raw proof are in
`docs/implementation/proof-reports/ARCH-17-RUNTIME-MATERIALIZATION.md`.

The worker entrypoint (`apps/worker/src/nquiry_worker/__main__.py`)
remains an explicitly documented no-op: it prints
`"nquiry_worker: Phase 0 skeleton — no workers implemented yet."` and
  exits `0`. The real worker logic that DOES exist and IS tested
  (`apps/worker/src/nquiry_worker/outbox_worker.py`,
  `projection_worker.py`, built in PKG-20/PKG-21) is exercised only by
  `tests/command_commit_event/test_outbox_worker.py` /
  `test_projection_worker.py` and friends — it is never wired into the
  actual `python -m nquiry_worker` process. Same disclosed gap class as
  the HTTP layer.

All real domain/authority/boundary/commit behavior
(`packages/application/*_handler.py` and everything underneath) is
fully implemented and fully tested, but is reachable **only** through
direct Python calls in the test suite (`tests/e2e/*`, etc.), not
through any currently-running network endpoint. This is the honest
current state of the "executable prototype" — see
`docs/implementation/proof-reports/PKG-32.md` for the full
`ARCHITECTURAL_IMPLEMENTATION_PROOF::PASS` /
`EXECUTABLE_PROTOTYPE_ACCEPTANCE::BLOCKED` reasoning (HARD-DEP-001/
HARD-DEP-002).

## 2. How to run it

```bash
cd /home/codi/Entwicklung/nquiry

# .env (already present, gitignored) must set:
#   POSTGRES_PORT=15432
# so the compose Postgres does not collide with a native/host
# PostgreSQL listening on the default 5432.

# Postgres only (Phase 0 gate: "DB starts"):
docker compose up -d postgres

# Full app stack (postgres + api + worker + web):
docker compose --profile app up -d --build

# Tear down cleanly:
docker compose --profile app down
```

Ports: Postgres → `localhost:15432` (container 5432), API →
`localhost:8000`, web → `localhost:3000`. The worker container has no
published port; it runs its one-shot no-op and exits `0` by design —
seeing it in `Exited (0)` state in `docker compose ps` output (it
won't even show as "Up") is correct, not a crash.

## 3. How to verify it's actually healthy (not just "Up")

A running container is not proof. Do all of the following:

```bash
# 1. Postgres container health (compose's own healthcheck):
docker compose ps postgres   # STATUS should say "healthy"

# 2. API liveness:
curl -sS http://localhost:8000/healthz
# -> {"status":"ok","phase":"0"}
# NOTE: this is a pure liveness probe. It does NOT check database
# connectivity -- it will return 200 even if Postgres is completely
# down (verified empirically, see section 5). Do not treat it as a
# readiness probe.

# 3. Web liveness:
curl -sS -o /dev/null -w '%{http_code}\n' http://localhost:3000/
# -> 200

# 4. Real database connectivity from INSIDE the api container
#    (the one check that actually proves network+driver+credentials
#    all work, since no HTTP route exercises this yet):
docker exec nquiry-api-1 python -c "
import psycopg
conn = psycopg.connect('postgresql://nquiry:nquiry_local_dev_only@postgres:5432/nquiry')
cur = conn.cursor()
cur.execute('SELECT version_num FROM alembic_version')
print(cur.fetchall())
"
# -> [('047bdf9bc528',)]  (must match the real migration head)

# 5. Migration state (static + live):
source .venv/bin/activate
export DATABASE_URL="postgresql+psycopg://nquiry:nquiry_local_dev_only@localhost:15432/nquiry"
python scripts/verify_migrations.py
# -> MIGRATION_STATIC_CHECK::PASS (19 revisions, single head)
# -> MIGRATION_LIVE_CHECK::PASS (db head matches)

# 6. The real proof: run the test suite against this exact database.
python -m pytest -q
# -> 1111 passed, 1 skipped (as of PKG-32; DATABASE_URL must point at
#    the docker-compose Postgres, port 15432, not any other instance)

# 7. Static gates:
ruff format --check .
ruff check .
MYPYPATH=packages:apps/api/src:apps/worker/src:scripts \
  mypy packages apps/api/src apps/worker/src scripts
python scripts/check_architecture_dependencies.py
python scripts/check_provider_sdk_imports.py
python scripts/check_test_only_imports.py
# -> all PASS
```

Environment note: this sandbox's Python is 3.10, while the project
targets 3.13 (`pyproject.toml` `requires-python = ">=3.13"`). Local
`pytest`/`mypy`/`ruff` runs rely on `pyproject.toml`'s `pythonpath`
setting (`packages`, `apps/api/src`, `apps/worker/src`, `scripts`)
rather than an editable install, which the 3.10 interpreter cannot
satisfy. The Docker images build and run under the real, pinned target
Python from their own Dockerfiles — that gap does not exist inside the
containers.

## 4. Runtime verification performed on 2026-09-20

A full, from-scratch verification pass was run against commit
`0884f62` (PKG-32, terminal package). Summary — **no defect found, no
code changed**:

- `docker compose down` / `docker compose --profile app up -d --build`
  (clean rebuild): postgres, api, worker, web all started correctly;
  worker exited `0` as designed.
- `/healthz` → 200 both before and after the restart.
- Real DB connectivity proven from inside the running `api` container
  (see command in section 3.4) — `alembic_version` matches the real
  migration head (`047bdf9bc528`), 33 tables present in `public`.
- Full test suite (`python -m pytest -q`) run three separate times
  against the freshly-restarted, real docker-compose Postgres:
  **1111 passed, 1 skipped**, identical every time.
- `ruff`, `mypy`, and all three architecture checkers: clean.
- **Adversarial check**: stopped the Postgres container mid-run and
  curled `/healthz` again — it still returned `200`. This confirms
  `/healthz` truly is DB-connectivity-blind (documented in its own
  docstring as a Phase-0 liveness probe, not a readiness probe) rather
  than silently and incorrectly reporting health it hasn't checked.
  Restarted Postgres afterward; full recovery confirmed (DB-backed
  tests immediately green again).
- Checked for a worker boot-loop risk: no `restart:` policy is set
  anywhere in `docker-compose.yml` (defaults to `no`), so the worker's
  one-shot exit is stable, not a crash-restart cycle.
- Confirmed the host's own native PostgreSQL (listening on
  `127.0.0.1:5432`) was never touched, stopped, or reconfigured; the
  compose Postgres uses the distinct `15432` host port throughout
  (`.env`: `POSTGRES_PORT=15432`).
- `git status`/`git diff --stat` before and after: identical, empty —
  zero files changed by this verification pass.

## 5. Known, disclosed gaps (as of PKG-32; see section 1a for what changed)

- ~~No HTTP Command/Query dispatch exists yet~~ **Partially resolved
  the same day by Architecture 17** — see section 1a. Only the two
  named routes exist; there is still no generic dispatch for any other
  Command/Query (that remains out of scope, disclosed in Architecture
  17's own DEFERRED CAPABILITIES).
- The worker process (`python -m nquiry_worker`) still never runs the
  real, already-built `OutboxWorker`/`ProjectionWorker` loops — those
  are proven only by their own dedicated tests. Architecture 17
  classified wiring them as `BLOCKED_BY_UPSTREAM_GAP` (no durable path
  from `OutboxRecord.commit_id` to a fully historically faithful
  `EventEnvelope` exists yet — see `events.envelope`'s own module
  docstring), not implemented.
- Both were legitimate candidates for a future package (wiring
  `packages/application` Command/Query handlers to
  `apps/api/src/nquiry_api/http/`, and wiring the two workers into
  `nquiry_worker.__main__`), but implementing either is a new
  capability decision outside a pure runtime-verification pass, and
  was not done here.
- HARD-DEP-001 (legitimate first-Workspace governance-root bootstrap)
  and HARD-DEP-002 (real AI provider eligibility) remain BLOCKED,
  exactly as documented in every predecessor package's own report and
  in `docs/architecture/16_DECISION_GAP_REGISTER.md`. Nothing in this
  runtime pass touched, weakened, or attempted to close either.
