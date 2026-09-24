# NQUIRY Local Full-Stack Runtime Operation

Status: informational runbook, not an architecture document and not a
proof report. Describes HOW THE CURRENT RUNTIME ACTUALLY OPERATES,
observed and verified locally on top of sealed HEAD
`e54394b8f4f513285b1f05e8d66f154e3d0ca3ed` (Architecture 17) plus the
"NQUIRY LOCAL FULL-STACK RUNTIME ACCEPTANCE" field's CORS/actor-id
fixes and the local-login field's own real email/password login
(2026-09-21; see `docs/implementation/proof-reports/FULLSTACK-RUNTIME-ACCEPTANCE.md`
and `docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md` — neither
field is committed as of this writing). Rewritten in place (not
append-only) because this file's own role is "current reality",
distinct from `docs/architecture/*.md` ("what may exist and why") and
`docs/implementation/proof-reports/*.md` ("what was actually built and
proven, preserved as history"). If this file ever disagrees with a
proof report, the proof report is the historical record; this file is
what to trust for "how do I start it right now".

## 0. Quick start (no development background needed)

This section is written for a non-developer. It tells you the exact
commands to type and the exact web address to open, from a completely
empty database to being logged in — nothing here requires
understanding the code.

**What you need first (once per machine)**: Docker + Docker Compose
v2; Python 3.10+ with the repo's `.venv` set up (`pyproject.toml`); a
`psql` client; a gitignored `.env` file at the repo root containing
`POSTGRES_PORT=15432`. Section 1 has the full prerequisite list if
anything here is missing. **Ports used**: `3000` (the website you open
in your browser), `8000` (the backend API your browser talks to
behind the scenes), `15432` (the database — you never open this in a
browser).

**1. Start everything** (from a terminal, in the repository folder):

```bash
cd ~/Entwicklung/nquiry
env -u DATABASE_URL docker compose --profile app up -d --build
```

Wait about 15-30 seconds for the containers to finish starting.

**2. First time only (or after a database reset): prepare the
database.** A brand-new database has no tables and no accounts yet —
this step creates them. Skip straight to step 3 if you have already
done this once and the database has not been reset since.

```bash
# 2a. Create the database's internal user roles (once per fresh database):
export PGPASSWORD=nquiry_local_dev_only
psql -h localhost -p 15432 -U nquiry -d nquiry -f infra/local/db_roles.sql

# 2b. Create all the database's tables (the "migration"):
export DATABASE_URL="postgresql+psycopg://nquiry:nquiry_local_dev_only@localhost:15432/nquiry"
source .venv/bin/activate
python scripts/verify_migrations.py
# -> should print MIGRATION_STATIC_CHECK::PASS and MIGRATION_LIVE_CHECK::PASS
```

(Section 4 explains exactly what these two commands do and why they
are idempotent/safe to re-run.)

**3. Make sure there is something to log into.** Run this every time
after step 2, or any time you want to double-check the demo account
still exists:

```bash
export DATABASE_URL="postgresql+psycopg://nquiry:nquiry_local_dev_only@localhost:15432/nquiry"
source .venv/bin/activate
python scripts/seed_local_demo.py
```

This prints your login email and password at the end. Running it again
later is harmless — it will just tell you the account already exists.
The default demo login is:

```
Email:    demo-owner@nonproof.test
Password: nquiry-demo-2026
```

**4. Open your browser** and go to:

```
http://localhost:3000/
```

You will see a real login page. Enter the email and password above and
click "Log in". After logging in, you are taken straight to the demo
scenario — a Challenge ("Signup conversion dropped 18% after the
redesign"), a Session, and a Decision you can actually record (pick an
option and submit it for real — it is saved in the database).

There is a "Log out" button at the top. Logging out and re-opening
`http://localhost:3000/` will send you back to the login page — the
login is real, not decorative: without the correct password, or
without ever logging in, you cannot see the demo scenario at all
(you'll get a plain "not logged in" screen, never the Challenge/
Decision content).

**What this is NOT**: this is a local development prototype, not a
production system. The account above is a disclosed, local-only demo
credential (`scripts/seed_local_demo.py`'s own module docstring) — it
is not connected to any real company system, and the underlying
"Workspace" it logs into is explicitly marked, in the database itself,
as a non-production test fixture (see section 20 below, "HARD-DEP-001"
— this is a known, disclosed, and still-open architectural gap, not
something this login work claims to have solved).

## 0a. What the login feature actually does, and why

**The login/session/logout flow, in plain terms:**

1. You submit an email and password on `/login`.
2. The server checks the password against a securely-hashed copy
   stored in the database (never the plain password itself — even the
   people running this database cannot read your password back out of
   it, only verify a guess against the hash).
3. On success, the server creates a real database record — "this
   session token belongs to this user, valid until this time" — and
   tells your browser to remember an opaque, random token in a cookie.
   Your browser cannot read or tamper with this token in any useful
   way (`HttpOnly`); it can only send it back automatically on later
   requests.
4. Every later page you visit sends that cookie automatically. The
   server looks the token up in the database on every single request —
   if it's missing, unknown, expired, or was revoked by a logout, you
   are treated as not logged in. There is no "trust me, I'm user X"
   shortcut anywhere in this path anymore.
5. "Log out" deletes/revokes that database record for real — the
   cookie your browser still has instantly stops working, proven by an
   automated test that logs out and then tries to reuse the exact same
   cookie.

**The problem this closes (GAP-14-001):** before this work, the
application had no real login at all. The only way to open the demo
scenario in a browser was a URL trick — `?as=<some-user-id>` appended
to the address — which the server accepted completely at face value,
with **no password, no cryptographic check, nothing verifying the
claim at all**. Anyone who could see or guess that URL parameter could
claim to be any user. That was explicitly disclosed at the time as a
temporary placeholder, not a real security mechanism. This work
replaces it with the real login described above; that URL trick no
longer works at all — the two application routes that used to trust
it now require a real, verified session and silently ignore that old
parameter/header entirely (proven by automated tests that send the old
trick and confirm it has zero effect).

**What this deliberately does NOT do (HARD-DEP-001), and why:** there
are two separate questions that are easy to conflate:

- "Is the person logging in really who they claim to be?" — **this is
  what this work answers**, with a real password and a real,
  database-verified session.
- "Should that person be allowed to be the owner/administrator of a
  brand-new Workspace in the first place — who legitimately gets to
  create the very first one, and by what rule?" — **this work
  deliberately does NOT answer this**, and was explicitly instructed
  not to. The demo account this login work created is still only ever
  set up through a fixture script that is labeled, inside the database
  itself, as "not a legitimate production setup" — the same way every
  single demo/test account in this codebase has always been created.
  Answering the second question properly is reserved for a later,
  separate piece of work. Building a real login was never supposed to
  quietly settle it as a side effect, and it was checked, deliberately,
  that it did not.

## 1. Prerequisites

- Docker + Docker Compose v2 (`docker compose`, not `docker-compose`).
- Node.js 20+ and npm (for `apps/web`; used for local `npm run
  lint`/`typecheck`/`test`/`e2e`/`build` — the running `web` container
  builds its own copy inside the image and does not need these on the
  host).
- Python 3.10+ with a `.venv` at the repo root, `pip install -e .`'s
  dependencies available (see `pyproject.toml`; this sandbox's system
  Python is 3.10 against a `requires-python = ">=3.13"` target --
  `pytest`/`mypy`/`ruff` all work via `pyproject.toml`'s own
  `pythonpath` setting rather than an editable install; the Docker
  images build and run under the real, pinned 3.13 from their own
  Dockerfiles).
- `psql` client (for one-time local role setup, see section 4).

## 2. Environment setup

A gitignored `.env` at the repo root must set:

```
POSTGRES_PORT=15432
```

This is required because `docker-compose.yml`'s own `postgres` service
maps `${POSTGRES_PORT:-5432}:5432` — without this override, Compose
would try to bind the CONTAINER's Postgres to the HOST's default 5432,
which collides with any native/host-installed PostgreSQL already
listening there. `15432` is a distinct host port; the container's own
internal port is always `5432` regardless.

**Known operational hazard, discovered this field**: if `DATABASE_URL`
is exported in the SAME shell you run `docker compose up`/`down` from,
Compose's own `${DATABASE_URL:-default}` substitution (used by the
`api`/`worker` service definitions) will silently pick up your HOST-
facing value (`...@localhost:15432/...`) instead of the correct
in-network default (`...@postgres:5432/...`) — the container then
cannot reach its own database (`connection refused`, since `localhost`
inside the container means the container itself, not the host). Run
`docker compose` commands with `DATABASE_URL` unset (e.g. `env -u
DATABASE_URL docker compose ...`), and only export `DATABASE_URL` for
host-side `pytest`/`alembic`/`psql` commands.

## 3. Exact startup command

```bash
cd ~/Entwicklung/nquiry

# Postgres only (satisfies "DB starts" alone):
env -u DATABASE_URL docker compose up -d postgres

# Full stack (postgres + api + worker + web):
env -u DATABASE_URL docker compose --profile app up -d --build
```

`--build` is only required the first time, or after a code change to
`apps/api`, `apps/worker`, `apps/web`, or `packages/*` (all three
Dockerfiles `COPY` the relevant source into the image at build time —
there is no live volume mount, so an edited file on the host is NOT
visible inside a running container until the image is rebuilt).

## 4. Migration procedure

A **brand-new** Postgres volume needs its service-principal roles
created before migrations will apply (PKG-25's own 9 DB principals,
`infra/local/db_roles.sql`):

```bash
export PGPASSWORD=nquiry_local_dev_only
psql -h localhost -p 15432 -U nquiry -d nquiry -f infra/local/db_roles.sql
```

Then apply migrations to head:

```bash
source .venv/bin/activate
export DATABASE_URL="postgresql+psycopg://nquiry:nquiry_local_dev_only@localhost:15432/nquiry"
python -c "
from alembic.config import Config
from alembic import command
cfg = Config()
cfg.set_main_option('script_location', 'migrations')
cfg.set_main_option('sqlalchemy.url', '$DATABASE_URL')
command.upgrade(cfg, 'head')
"
python scripts/verify_migrations.py
# -> MIGRATION_STATIC_CHECK::PASS (20 revisions, single head)
# -> MIGRATION_LIVE_CHECK::PASS (db head matches)
```

An EXISTING volume (from a prior session) already has both; re-running
`db_roles.sql` and `upgrade head` is idempotent/no-op in that case.

## 5. Backend startup

Handled by `docker compose --profile app up -d --build api` (section
3). No separate manual step. The `api` container's own `DATABASE_URL`
is fixed by `docker-compose.yml` to the correct in-network address
(`...@postgres:5432/...`) — do not override it from the host shell
(section 2's hazard).

## 6. Frontend startup

Handled by the same `docker compose --profile app up -d --build web`
call (section 3). `apps/web` is a real Next.js 16 app (`next dev`
inside the container, per `infra/local/web.Dockerfile`) — not a static
export, not a mock. It has no build-time `NEXT_PUBLIC_API_BASE_URL`
set; `apps/web/lib/api/client.ts`'s own `DEFAULT_API_BASE_URL =
"http://localhost:8000"` is correct as-is because the actual `fetch()`
calls run in the BROWSER (client-side, by design — see that file's own
docstring for why), and the browser's own `localhost:8000` resolves
correctly against the same `docker-compose.yml` port mapping the API
container publishes.

## 7. Worker behavior

`worker` is a real service in the `app` profile (`docker-compose.yml`),
started by the same `docker compose --profile app up` call as `api`
and `web` (section 3) — no separate command. It
runs `python -m nquiry_worker`, prints `"nquiry_worker: Phase 0
skeleton — no workers implemented yet."` to stderr, and **exits 0
immediately by design** — this is correct, not a crash. No `restart:`
policy is configured (defaults to `no`), so it does not loop. The real,
tested `OutboxWorker`/`ProjectionWorker` classes exist
(`apps/worker/src/nquiry_worker/outbox_worker.py`, `projection_worker.py`)
but are not wired into this entrypoint — `BLOCKED_BY_UPSTREAM_GAP`, not
implemented, because no durable `OutboxRecord.commit_id` ->
`EventEnvelope` reconstruction mechanism exists in this codebase yet
(disclosed in those files' own docstrings since PKG-20/21).

## 8. Exact local URLs

```
Frontend root:         http://localhost:3000/            (real: -> /login, or the app if logged in)
Frontend login:         http://localhost:3000/login
Frontend Session view:  http://localhost:3000/workspaces/{workspaceId}/sessions/{sessionId}
API health:             http://localhost:8000/healthz
API login:              POST http://localhost:8000/auth/login   {"email":..., "password":...}
API current session:    GET  http://localhost:8000/auth/me
API logout:              POST http://localhost:8000/auth/logout
API Session Query:      http://localhost:8000/workspaces/{workspaceId}/sessions/{sessionId}
API Decision Command:   http://localhost:8000/decisions/{decisionId}/decide
```

**Local-login field update** (`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`):
identity now comes from a real, `HttpOnly` `nquiry_session` cookie a
real `POST /auth/login` call issues — the former `?as={actorUserId}`
query parameter (Architecture 17 + the FULLSTACK-RUNTIME-ACCEPTANCE
field's own disclosed, temporary GAP-14-001 substitute) is REMOVED. A
bare `x-nquiry-actor-user-id`/`x-nquiry-actor-class` header, with or
without any value, now has ZERO effect on either API route — only a
real, verified session matters (see that architecture document's own
adversarial test matrix for the exact proof). GAP-14-001 itself (real
OIDC provider selection) remains open; this is still a local,
deterministic credential adapter, not a production identity provider.

## 9. Health checks

```bash
docker compose ps postgres   # STATUS column should say "(healthy)"
curl http://localhost:8000/healthz   # -> {"status":"ok","phase":"0"}, HTTP 200
curl -o /dev/null -w '%{http_code}\n' http://localhost:3000/   # -> 200
```

## 10. Database connectivity verification

`/healthz` does NOT check database connectivity (see section 17). To
actually prove the API can reach Postgres:

```bash
docker exec nquiry-api-1 python -c "
import psycopg
conn = psycopg.connect('postgresql://nquiry:nquiry_local_dev_only@postgres:5432/nquiry')
cur = conn.cursor()
cur.execute('SELECT version_num FROM alembic_version')
print(cur.fetchall())
"
# -> [('047bdf9bc528',)]
```

## 11. Live HTTP verification

```bash
# Unauthenticated -> real 401, never a false success:
curl -i http://localhost:8000/workspaces/00000000-0000-0000-0000-000000000000/sessions/00000000-0000-0000-0000-000000000000
curl -i http://localhost:8000/auth/me

# Real login (seed the demo account first -- see section 13), keeping
# a cookie jar across calls:
curl -i -c /tmp/nquiry-cookies.txt -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo-owner@nonproof.test","password":"nquiry-demo-2026"}'
# -> 200, Set-Cookie: nquiry_session=...; HttpOnly; ...

# The cookie, and only the cookie, grants access:
curl -b /tmp/nquiry-cookies.txt http://localhost:8000/auth/me
curl -b /tmp/nquiry-cookies.txt http://localhost:8000/workspaces/<ws>/sessions/<session>

# A forged/garbage cookie is rejected:
curl -i -H "Cookie: nquiry_session=not-a-real-token" http://localhost:8000/auth/me
# -> 401

# Logout revokes the real session -- the SAME cookie stops working:
curl -i -b /tmp/nquiry-cookies.txt -X POST http://localhost:8000/auth/logout
curl -i -b /tmp/nquiry-cookies.txt http://localhost:8000/auth/me
# -> 401
```

## 12. Frontend verification

```bash
cd apps/web
npm install          # first time only
npm run lint          # eslint
npm run typecheck     # tsc --noEmit
npm run test           # vitest (unit)
npm run e2e             # playwright (real browser, network-mocked via page.route())
npm run build            # next build (production build)
```

To see it render for real in a browser, seed a scenario (section 13)
and open the exact Session-view URL from section 8.

## 13. Seeding a scenario to look at (and a real login for it)

There is no signup/create-Challenge UI yet. `scripts/seed_local_demo.py`
(repo-tracked, idempotent) seeds a demo Workspace/Challenge/Session/
Burst/Decision via the same disclosed `NonProofWorkspaceBootstrap`
pattern every real test in this repository already uses (HARD-DEP-001
stays open — this is not a legitimate production bootstrap, and is
never represented as one), AND creates a real local login credential
for it:

```bash
export DATABASE_URL="postgresql+psycopg://nquiry:nquiry_local_dev_only@localhost:15432/nquiry"
source .venv/bin/activate
python scripts/seed_local_demo.py
```

Safe to run more than once — it reuses the existing demo Workspace/
Session and only creates the login credential if one does not already
exist yet. Prints the login email/password and the exact Session-view
URL you land on after logging in. Set `NEXT_PUBLIC_DEFAULT_WORKSPACE_ID`/
`NEXT_PUBLIC_DEFAULT_SESSION_ID` (`docker-compose.yml`'s own `web`
service `environment:` block) to the printed ids if they ever drift
from the compose defaults (e.g. after a volume reset re-seeds with
fresh random ids), then `docker compose -p nquiry up -d web` to apply.

## 14. Shutdown procedure

```bash
env -u DATABASE_URL docker compose --profile app down
```

Leaves the Postgres named volume (`nquiry_nquiry_postgres_data`)
intact — data persists across a plain `down`/`up` cycle.

## 15. Restart procedure

```bash
env -u DATABASE_URL docker compose --profile app down
env -u DATABASE_URL docker compose --profile app up -d
```

To reset to a **genuinely empty** database (e.g. to prove
reproducibility, or to discard demo/manual-proof data — see section 16),
add `-v` to the `down` to also remove the volume, then redo section 4
(role setup + migration) before anything else will work.

## 16. Common failure modes discovered during these fields

- **"Incorrect email or password" with credentials you're sure are
  right, copy-pasted from a chat/terminal.** Real incident: found
  during this field's own human verification pass. Root cause: a
  trailing newline/space picked up by copy-paste made the password
  byte-comparison fail even though the visible password was correct —
  `login` now trims surrounding whitespace from the password (matching
  the trimming `email` already got) before comparing, so this
  specific class of failure is fixed
  (`packages/application/auth_handler.py::login`, regression test
  `tests/e2e/test_auth_handler.py::
  test_login_strips_surrounding_whitespace_from_the_password`). If
  login STILL fails after retyping the password manually (not pasted),
  suspect your browser's own saved-password autofill silently
  substituting a different stored credential for `localhost:3000` —
  clear/disable autofill for that field and check
  `docker logs nquiry-api-1` for the real request outcome
  (`OPTIONS /auth/login 200` + `POST /auth/login 401` means the
  request genuinely reached the backend with the wrong credential —
  not a CORS/networking problem).
- **`DATABASE_URL` shell-leak into `docker compose`** — see section 2.
  Symptom: real `500`s from the API, `docker logs nquiry-api-1` shows
  `connection to server at "127.0.0.1", port 15432 failed`.
- **Manual/live proof data breaking unrelated tests.** Some existing
  tests (e.g. `tests/security/test_habb_grant_constraints.py`) assert
  an UNSCOPED row count against a table. The automated `pytest`
  suite's own transactional isolation never leaves real residue on its
  own (proven repeatedly, twice-reproduced clean runs from a fresh
  volume) — but any REAL, committed HTTP proof against the live
  container (curl, a seed script, or a real browser session) does
  leave real rows, some of them permanently (see next point), and can
  make those specific unscoped-assertion tests fail until the database
  is reset (section 15). This is a known, disclosed limitation of a
  few pre-existing tests' own assertion style, not a defect in the
  runtime itself.
- **`audit_events` is genuinely append-only.** A real DB trigger
  (`trg_audit_events_reject_delete`, PKG-26, 11 §35) rejects any
  `DELETE` against it. A real commit therefore cannot be "cleaned up"
  by deleting rows — only a full volume reset (section 15, `-v`)
  actually returns to empty.
- **Browser CORS block.** A real browser loading `localhost:3000` and
  fetching `localhost:8000` is a cross-origin request under the
  browser's own same-origin policy. `curl`/`requests`/`TestClient` do
  not enforce this, and the existing Playwright E2E suite mocks the
  network layer (`page.route()`), so this was only caught by an actual
  browser hitting the actual live API. Fixed: `apps/api/src/nquiry_api/main.py`
  now configures `CORSMiddleware` allowing exactly `http://localhost:3000`.
- **DB triggers enforce real transition/initial-state rules even for
  seed scripts.** E.g. `sessions` must be `INSERT`ed as `DRAFT` (03
  TRN-SESS-001) and cannot jump straight to a later state via a raw
  `UPDATE` either (`trg_sessions_enforce_transition`) — a seed script
  must respect the same real state machine a legitimate Command would.

## 17. Liveness vs readiness

`GET /healthz` is LIVENESS ONLY — it returns `200` even if PostgreSQL
is completely unreachable (verified empirically: stop the `postgres`
container, `/healthz` still returns 200). It proves the process is
alive, nothing about the database. There is no separate readiness
endpoint in this build phase; use section 10's direct connectivity
check for actual DB-reachability proof. `HEALTHZ != DATABASE READINESS`.

## 18. Currently implemented runtime surface

(Updated by Field F02, 2026-09-24. Historical text for earlier fields is in
their proof reports.)

- `GET /healthz` — liveness only.
- Local auth: `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`
  (`18_LOCAL_AUTHENTICATION_ADAPTER.md`).
- F01 Workspace governance: `POST /workspaces` (governed founding,
  HARD-DEP-001 Option A), `GET /workspaces`, `GET /workspaces/{w}`,
  `POST /workspaces/{w}/members`,
  `POST /workspaces/{w}/authority-bindings/{b}/revoke`.
- F02 inquiry context (every Command route requires an `Idempotency-Key`
  UUID header; outcomes: `committed` / `denied` / `rejected` / `stale` /
  `blocked` / `failed_precommit` / `indeterminate` / `not_found`):
  `GET /workspaces/{w}/overview`, `POST /workspaces/{w}/challenges`,
  `GET /workspaces/{w}/challenges/{c}`,
  `POST /workspaces/{w}/challenges/{c}/sessions`,
  `POST /workspaces/{w}/authority-bindings` (grant),
  `GET /workspaces/{w}/sessions/{s}/position`,
  `POST /workspaces/{w}/sessions/{s}/transitions/begin-setup`,
  `…/transitions/begin-challenge-capture`, `…/burst` (prepare),
  `…/participants` (admit), `…/transitions/open-question-generation`.
- Architecture 17 / PKG-29: `GET /workspaces/{w}/sessions/{s}` (legacy
  Session view) and `POST /decisions/{d}/decide`.
- Outcome rules for every route (F02 WU-02.12):
  - A request body that fails the route's schema is
    `{"kind":"rejected","reasonCode":"MALFORMED_REQUEST_BODY"}` (400), never
    FastAPI's bare `{"detail":…}` 422. On F02 routes, 422 means `blocked`.
  - A proven rollback on decide / add-member / revoke is
    `{"kind":"failed_precommit","reasonCode":…}`. It is no longer folded
    into `rejected`.
  - The F01 / PKG-29 routes still answer HTTP 200 for every body `kind`;
    their outcome is the body. The status-mapped envelope applies to the F02
    routes.
  - An `Idempotency-Key` names ONE logical Command: the same Workspace,
    Command type and payload. Retrying the identical request returns
    `committed` + `replayed`. Reusing the key for a different payload,
    Session, Command type or Workspace returns `rejected`
    (`IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_COMMAND`).
- Frontend: `/login`, `/workspaces`, `/workspaces/{w}`,
  `/workspaces/{w}/challenges/{c}`, `/workspaces/{w}/sessions/{s}`
  (governed inquiry position), `/workspaces/{w}/sessions/{s}/decision`
  (PKG-29 Decision surface).
- Worker: real process, exits 0, no consequential work (F08 scope).

## 19. Currently non-materialized capabilities

- Question capture, Burst pause/resume/completion, frozen question set
  (F03). AI sensemaking (F04). Selection, Evidence, Decision re-homing
  (F05–F07).
- No production authentication provider (GAP-14-001). No self-service
  registration: additional local identities come only from the DEV-ONLY
  provisioning script (§21).
- `OutboxWorker`/`ProjectionWorker` not wired into a continuous loop.
- No readiness endpoint distinct from liveness.
- Member addition takes a raw user id (no user directory query).

## 20. HARD-DEP-001 / HARD-DEP-002 status

- **HARD-DEP-001**: RESOLVED (Option A, self-service founder), 2026-09-21,
  materialized as `CMD_CREATE_WORKSPACE` (16 §41 REC-001). Workspaces
  seeded by `scripts/seed_local_demo.py` / `NonProofWorkspaceBootstrap`
  remain NON_PROOF fixtures. The UI labels them "NON_PROOF fixture",
  derived from provenance: such a Workspace has no FOUNDING audit event.
- **HARD-DEP-002**: open (EXTERNAL_DEPENDENCY). `MockProviderAdapter` only.

## 21. Stakeholder walkthrough (F02, real governed flow)

```bash
docker compose -p nquiry --profile app up -d --build
export DATABASE_URL=postgresql+psycopg://nquiry:nquiry_local_dev_only@localhost:15432/nquiry
python scripts/verify_migrations.py
# DEV-ONLY: create two local identities. This creates NO membership, role
# or authority (F02 HD-3). The script refuses to run without the opt-in.
export NQUIRY_DEV_IDENTITY_PROVISIONING=I_UNDERSTAND_THIS_IS_DEV_ONLY
PYTHONPATH=packages python scripts/dev_provision_local_identity.py \
    --email alex@dev.local.test --name "Alex (founder)" --password "alex-dev-password"
PYTHONPATH=packages python scripts/dev_provision_local_identity.py \
    --email bea@dev.local.test --name "Bea (facilitator)" --password "bea-dev-password"
```

Then, in the browser at `http://localhost:3000/`:

1. Alex logs in and creates a Workspace (Alex becomes its governance root).
2. Alex adds Bea (paste Bea's printed `userId`) with role **Facilitator**.
3. Bea logs in, opens the Workspace, and creates a Challenge.
4. Alex opens the Challenge and grants Bea session control **for this
   Challenge**. Bea can now open a Session.
5. Alex opens the Session and grants Bea session control **for this
   Session** (nothing is inherited from the Challenge, F02 HD-1).
6. Bea: Begin setup → Begin challenge capture → Prepare protected Burst →
   admit a participant (e.g. Alex) → Open question generation. The Session
   is now in QUESTION_GENERATION and the HUMAN_ONLY Burst is ACTIVE.

Question capture itself arrives with Field F03.

## 22. Test lanes (F02)

| Lane | Command | What it proves |
|---|---|---|
| Backend, live DB | `DATABASE_URL=…/nquiry_test pytest` | Real PostgreSQL semantics. Use the **isolated `nquiry_test` database** (see below) |
| Backend, pure | `pytest` (no `DATABASE_URL`) | Pure-Python layers |
| Component contract (MOCKED browser) | `cd apps/web && npm run e2e` | UI logic against `page.route()`-fulfilled responses. **Not runtime proof**. Caution (WU-02.12): `reuseExistingServer` means that if anything already serves `:3000` (e.g. the `web` container), the lane tests **that** build, not your working tree. Rebuild the containers first, or stop `web`. |
| Real stack (REAL browser) | `PYTHON=.venv/bin/python bash scripts/run_real_stack_e2e.sh` (or `npm run e2e:real`) | Real browser → web → FastAPI → auth → PostgreSQL → governed Commands; desktop + mobile; axe; keyboard. The script starts api/web only if nothing already serves `:8000`/`:3000`, so it proves **whatever is running**. For proof of this tree, first `docker compose -p nquiry --profile app up -d --build` from it (WU-02.11/02.12 practice). |

Isolated test database (once per Postgres volume):

```bash
docker exec nquiry-postgres-1 createdb -U nquiry nquiry_test
docker exec -i nquiry-postgres-1 psql -U nquiry -d nquiry_test < infra/local/db_roles.sql
DATABASE_URL=postgresql+psycopg://nquiry:nquiry_local_dev_only@localhost:15432/nquiry_test \
    python scripts/verify_migrations.py
```

Why: the real-stack lane and the demo **commit** durable governed history
(commit units, audit, PENDING outbox events) into `nquiry`. Several
PKG-era tests assert properties of the whole outbox, such as the outbox
worker's global due-record scan. Those tests are only meaningful on a
database that no runtime writes to. On the shared `nquiry` DB, after
real-stack runs, the 4 `test_outbox_worker.py` tests fail by
construction (classified ENVIRONMENT, F02 WU-02.11).
