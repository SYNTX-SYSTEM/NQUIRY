# NQUIRY LOCAL FULL-STACK RUNTIME ACCEPTANCE — Proof Report

Field: "NQUIRY LOCAL FULL-STACK RUNTIME ACCEPTANCE"
Date: 2026-09-21
Repository: `~/Entwicklung/nquiry`
Baseline HEAD (sealed, unmodified by this field): `e54394b8f4f513285b1f05e8d66f154e3d0ca3ed`
("Architecture 17: Live application runtime materialization", FIELD PASS)
This field's own changes: **uncommitted as of this report** (see §27 GIT STATUS).

## 1. FIELD PURPOSE

Prove that the sealed repository (Architecture 17 HEAD) can actually be
started locally as a real full-stack application, reachable end-to-end
by a human in a real browser — not merely pass its own test suite.
Explicitly scoped as a runtime-operationalization field: no new domain
capability, no governance/authority weakening, no change to
persistence/audit/idempotency/HARD-DEP semantics.

## 2. BASELINE

Confirmed at the start of this field and re-confirmed in this report
(fresh, this turn):

```
$ git log -1 --format='%H %s'
e54394b8f4f513285b1f05e8d66f154e3d0ca3ed Architecture 17: Live application runtime materialization (FIELD PASS)
```

## 3. FILES INSPECTED

`apps/api/src/nquiry_api/main.py`, `apps/web/lib/api/client.ts`,
`apps/web/lib/api/decisionClient.ts`, `apps/web/components/SessionViewContainer.tsx`,
`apps/web/components/DecisionSection.tsx`,
`apps/web/app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx`,
`docker-compose.yml`, `infra/local/*.Dockerfile`, `infra/local/db_roles.sql`,
`packages/application/http_dispatch.py`, `packages/test_support/nonproof_bootstrap.py`,
`packages/persistence/tables.py`, `docs/RUNTIME_OPERATION.md` (pre-existing version),
`docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`.

## 4. FILES CHANGED (this field)

- `apps/api/src/nquiry_api/main.py` — added `CORSMiddleware` (see §15–17).
- `apps/api/tests/test_cors.py` — **new**, 3 tests.
- `apps/web/lib/api/client.ts` — added optional `actorUserId` passthrough
  to `fetchSessionView` (see §14).
- `apps/web/lib/api/decisionClient.ts` — same passthrough on
  `recordHumanDecision`.
- `apps/web/components/SessionViewContainer.tsx` — threads `actorUserId`
  prop through.
- `apps/web/components/DecisionSection.tsx` — threads `actorUserId`
  prop through to the decide call.
- `apps/web/app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx` —
  reads `?as=` query param, passes as `actorUserId`.
- `apps/web/tests/lib/client.test.ts`, `apps/web/tests/lib/decisionClient.test.ts` —
  updated existing call sites, added actor-header tests.
- `docs/RUNTIME_OPERATION.md` — rewritten as the current full-stack
  runbook (this field's Phase 8 deliverable).

No file outside this list was touched. `apps/web/AGENTS.md` and
`apps/web/CLAUDE.md` (pre-existing untracked files, unrelated to this
field) remain untouched throughout.

## 5. RUNTIME TOPOLOGY

Four Docker Compose services under the `app` profile (plus `postgres`,
always available bare): `postgres:17`, `api` (uvicorn, port 8000),
`worker` (`python -m nquiry_worker`, no published port), `web`
(Next.js `next dev`, port 3000). `worker` exits 0 immediately by design
(Phase-0 stub, see §13) — a `docker compose ps` without `-a` will not
list it once exited, which is why an earlier version of this report
and of `RUNTIME_OPERATION.md` incorrectly stated no `worker` service
existed in the `app` profile; corrected 2026-09-21 after `docker
compose ps -a` showed `nquiry-worker-1 Exited (0)`. All services run
on the host's Docker daemon with published ports, no reverse proxy.

## 6. ENVIRONMENT

Host: Linux 6.8.0-138-generic. `.env` sets `POSTGRES_PORT=15432`. Python
3.10.12 (host, via `.venv`) against `pyproject.toml` targeting 3.13 —
works via that file's own `pythonpath` setting; Docker images build
under their own pinned 3.13. Node/npm per `apps/web/package.json`.

## 7. DATABASE PROOF (fresh, this turn)

```
$ docker compose ps
nquiry-postgres-1   postgres:17   Up 9 hours (healthy)   0.0.0.0:15432->5432/tcp

$ docker exec nquiry-api-1 python -c "... SELECT version_num FROM alembic_version ..."
alembic head: [('047bdf9bc528',)]
```

Live, from inside the `api` container, over the real in-network
`postgres:5432` address (not the host-facing `localhost:15432`) —
confirms both container-to-container connectivity and migration state.

## 8. MIGRATION PROOF

`047bdf9bc528` matches `scripts/verify_migrations.py`'s own single-head
check as previously established for Architecture 17 (unmodified by
this field — no new migration was authored).

## 9. API STARTUP PROOF

```
$ curl -s -o /tmp/healthz.json -w '%{http_code}\n' http://localhost:8000/healthz
200
$ cat /tmp/healthz.json
{"status":"ok","phase":"0"}
```
Fresh, this turn, against the container running with this field's
`CORSMiddleware` change baked in via a prior `--build`.

## 10. LIVE HTTP PROOF (fresh, this turn)

Authenticated session-view read:
```
$ curl -s -i "http://localhost:8000/workspaces/01a0c0d7-58a0-7ec2-8127-c15f8d9f5fea/sessions/a2f4dfbb-a247-4ed1-aa95-b4ed1323e363" \
    -H "x-nquiry-actor-user-id: 01a0c0d7-58a0-7044-9da5-79780214fbad"
HTTP/1.1 200 OK
{"kind":"ok","data":{"workspaceId":"01a0c0d7-58a0-7ec2-8127-c15f8d9f5fea",
 "challenge":{...,"title":"Signup conversion dropped 18% after the redesign",...},
 "session":{...,"state":"DRAFT"},
 "burst":{...,"state":"PREPARED","mode":"HUMAN_ONLY","questions":[3 real questions]},
 "decision":{...,"state":"UNDER_CONSIDERATION","options":[3],"criteria":[2],...}}}
```
Unauthenticated (no header) against the same URL:
```
401
```
Real boundary enforcement observed live, not reconstructed.

## 11. FRONTEND STARTUP PROOF (fresh, this turn)

```
$ curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3000/
200
```

## 12. FRONTEND/BACKEND INTEGRATION PROOF (fresh, this turn)

Real Playwright-driven Chromium load of the real Session-view URL
against the real running containers (no `page.route()` mocking):

```
url = http://localhost:3000/workspaces/01a0c0d7-58a0-7ec2-8127-c15f8d9f5fea/sessions/a2f4dfbb-a247-4ed1-aa95-b4ed1323e363?as=01a0c0d7-58a0-7044-9da5-79780214fbad
waitForSelector('[data-testid="session-view-ok"]')  -> resolved
RENDER_OK: true   (body contains "Signup conversion dropped 18%")
CONSOLE_ERRORS: []   (zero, including zero CORS errors)
```
Screenshot captured this turn: `session_view_final.png` (54144 bytes),
delivered to the user alongside this report.

This is the field's central positive claim: a real browser, with no
network mocking, loading the real frontend, calling the real backend
across a real cross-origin boundary, rendering real persisted domain
data (challenge title, 3 questions, 3 decision options, 2 criteria) —
end to end.

## 13. WORKER STATUS

Unchanged by this field. Per `RUNTIME_OPERATION.md` §7: real process,
prints its Phase-0 stub message, exits 0 by design, not wired to a
continuous loop (`BLOCKED_BY_UPSTREAM_GAP`, disclosed since PKG-20/21).

## 14. DEFECT 1 — Actor identity never reached the browser-driven frontend

**Discovered**: earlier in this field, via real browser load returning
a boundary-denied response despite a seeded, valid actor.
**Root cause**: `apps/web/lib/api/client.ts`/`decisionClient.ts` were
authored in PKG-28, before Architecture 17's `x-nquiry-actor-user-id`
identity-header contract (`application.http_dispatch.resolve_actor`)
existed — they sent no identity header at all.
**Classification**: runtime adapter wiring already authorized by
Architecture 17 (the header contract itself is pre-existing, unchanged
domain surface), not a new capability — per this field's own decision
tree. Fixed with an optional `actorUserId` parameter threaded from a
`?as=` URL query parameter, since this prototype has no login
mechanism (GAP-14-001, still open, unchanged).
**RED**: `fetchSessionView`/`recordHumanDecision` calls carried no
identity header; a real browser session against a seeded workspace
received a `401` despite valid seed data.
**GREEN**: `apps/web/tests/lib/client.test.ts`,
`apps/web/tests/lib/decisionClient.test.ts` — 32/32 passing (fresh,
this turn, `npx vitest run`, see §19); real-browser session-view load
returns `200` with full body (§10, §12).

## 15. DEFECT 2 — No CORS configuration

**Discovered**: earlier in this field, only by a REAL browser issuing a
real cross-origin request; `curl`, `requests`, `TestClient`, and the
existing Playwright E2E suite (network-mocked via `page.route()`) are
all structurally incapable of catching this, since CORS is enforced by
the browser itself.
**Root cause**: `apps/api/src/nquiry_api/main.py` configured no
`CORSMiddleware` at all.
**Fix**: `CORSMiddleware` scoped to exactly `http://localhost:3000`
(never a wildcard), allowing `GET`/`POST` and the specific headers
`Content-Type`, `x-nquiry-actor-user-id`, `x-nquiry-actor-class`.
**RED** (reproduced conceptually via the pre-fix absence of any
`Access-Control-Allow-Origin` header — the original discovery).
**GREEN** (fresh, this turn):
```
$ curl -s -i -X OPTIONS http://localhost:8000/decisions/.../decide \
    -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: content-type,x-nquiry-actor-user-id"
HTTP/1.1 200 OK
access-control-allow-methods: GET, POST
access-control-allow-headers: Accept, Accept-Language, Content-Language, Content-Type, x-nquiry-actor-class, x-nquiry-actor-user-id
access-control-allow-origin: http://localhost:3000
```
`apps/api/tests/test_cors.py` — 3/3 passing fresh, this turn (§18),
including a negative case: an unrecognized origin receives no
`Access-Control-Allow-Origin` header at all (not "allow everyone").

## 16. ROOT CAUSES — summary

Both defects share one root cause class: every prior proof method for
Architecture 17 (curl, `requests`, `TestClient`, network-mocked
Playwright) sits at a lower layer than a real browser and cannot
observe browser-enforced behavior (same-origin policy) or exercise
code paths a browser client — but no other caller — actually uses
(the frontend's own header construction). Only this field's use of a
real, unmocked, browser-driven load surfaced them.

## 17. FIXES — summary

See §14, §15. No domain/authority/persistence code was touched by
either fix; `resolve_actor`'s own semantics (identity only, never
authority — GAP-14-001) are unchanged.

## 18. REGRESSION TESTS (fresh, this turn)

```
$ DATABASE_URL=... .venv/bin/python -m pytest -q apps/api/tests/test_cors.py -v
3 passed in 1.01s
```

## 19. FRONTEND UNIT TESTS (fresh, this turn)

```
$ npx vitest run tests/lib/client.test.ts tests/lib/decisionClient.test.ts
Test Files  2 passed (2)
     Tests  32 passed (32)
```

## 20. FULL TEST RESULTS (fresh, this turn, against the LIVE demo-populated DB)

```
$ DATABASE_URL=... .venv/bin/python -m pytest -q
1 failed, 1126 passed, 2 skipped in 20.80s
FAILED tests/security/test_habb_grant_constraints.py::test_grant_without_active_membership_is_rejected
  AssertionError: assert 2 == 0   (unscoped COUNT(*) over human_authority_bindings)
```
This is the exact, already-disclosed residue hazard documented in
`RUNTIME_OPERATION.md` §16 ("manual/live proof data breaking unrelated
tests") — the demo seed script inserts a real `human_authority_bindings`
row, and this one pre-existing test asserts an unscoped, workspace-
independent row count rather than scoping to its own fixture's
workspace. **Disclosed, not hidden**: this is a known limitation of
that one test's assertion style, reproduced live in this report as
current, ongoing evidence — not a defect in the runtime or in this
field's own changes.

**Clean-volume regression** (no demo residue) was run twice earlier in
this same field, before a context-compaction event in this session,
and reported: `1127 passed, 2 skipped` (full live-DB suite, matching
Architecture 17's own `1124` baseline + this field's 3 new CORS tests)
and `716 passed, 409 skipped` (pure-Python-only run) both times,
against a database verified pristine (only `alembic_version`
non-empty) before and after. **This report does not re-claim those
exact numbers as freshly re-observed in this continuation**: a full
`docker compose down -v` was required to reproduce them again just
now, and that destructive action was declined by this session's own
safety gate (`[Irreversible Local Destruction]`) rather than attempted
around. If independent re-confirmation of the clean-volume numbers is
wanted, that specific reset needs separate, explicit authorization —
it would also require re-running the demo reseed (§13 of
`RUNTIME_OPERATION.md`) afterward to restore the browser-visible state
left running for inspection (§12/§26 below).

**Update, second verification pass (same day, see §31)**: the
pure-Python figure WAS independently re-confirmed fresh, scoped
identically to PKG-32's own convention (`unset DATABASE_URL; python -m
pytest -q tests/`, i.e. excluding `apps/api/tests/`): `716 passed, 409
skipped`, matching the number above exactly. The live-DB figure was
re-run against the current demo-populated (non-clean) database only —
see §31 for the exact comparison against PKG-32's own recorded
baseline (`1111 passed, 1 skipped`).

## 21. STATIC GATES (fresh, this turn)

```
$ npm run lint        # eslint . -> clean, 0 errors
$ npm run typecheck    # tsc --noEmit -> clean, 0 errors
```

## 22. ARCHITECTURE GATES

Unmodified by this field (no dependency-direction changes; `main.py`'s
only new import is `fastapi.middleware.cors.CORSMiddleware`, a
transport-layer FastAPI builtin, not a new cross-package dependency).
`scripts/check_architecture_dependencies.py` was not re-run fresh in
this continuation; no change in this field touches anything that gate
inspects (import graph between `apps/api`, `packages/*`).

## 23. FRONTEND GATES

`npm run e2e` (existing 22-test, network-mocked Playwright suite) and
`npm run build` (production build) were both run and passed earlier in
this same field, before compaction; not re-run fresh in this
continuation since neither is affected by the CORS/actor-id changes'
runtime behavior in a way the earlier run wouldn't already cover (the
mocked E2E suite exercises component logic, not real network/CORS
behavior; the production build doesn't touch the database or network).

## 24. KNOWN LIMITATIONS

- No login/session mechanism (GAP-14-001) — `?as=` is a disclosed,
  temporary substitute, not new authority.
- Worker not wired to a continuous loop.
- No Challenge/Session-creation UI or HTTP route.
- `test_habb_grant_constraints.py::test_grant_without_active_membership_is_rejected`'s
  unscoped assertion is sensitive to any live-DB residue (see §20) —
  a pre-existing test-quality limitation, not touched by this field.

## 25. HUMAN_DECISION_REQUIRED

None raised by this field. Both defects (§14, §15) were classified,
per the field's own explicit decision tree, as runtime-adapter wiring
already authorized by Architecture 17 — not new capability requiring
escalation.

## 26. HARD-DEP-001 / HARD-DEP-002 STATUS

Unchanged, both remain BLOCKED/open:
- **HARD-DEP-001**: the demo scenario is seeded exclusively via
  `NonProofWorkspaceBootstrap` (`FIXTURE_LEGITIMACY ==
  "NON_PROOF_FIXTURE"`), disclosed as such in `RUNTIME_OPERATION.md`
  §13 and `/tmp/seed_demo_scenario.py`'s own module docstring — never
  represented as a legitimate production bootstrap.
- **HARD-DEP-002**: no AI/provider code touched; `MockProviderAdapter`
  unchanged.

## 27. GIT STATUS (fresh, this turn)

```
$ git status --short
 M apps/api/src/nquiry_api/main.py
 M apps/web/app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx
 M apps/web/components/DecisionSection.tsx
 M apps/web/components/SessionViewContainer.tsx
 M apps/web/lib/api/client.ts
 M apps/web/lib/api/decisionClient.ts
 M apps/web/tests/lib/client.test.ts
 M apps/web/tests/lib/decisionClient.test.ts
 M docs/RUNTIME_OPERATION.md
?? apps/api/tests/test_cors.py
?? apps/web/AGENTS.md
?? apps/web/CLAUDE.md
```
Exactly the 9 modified + 1 new file this field is responsible for
(matching §4), plus the 2 pre-existing, unrelated untracked files
(confirmed untouched: not staged, not modified, not referenced by any
change in this field). This report itself is a new untracked file at
`docs/implementation/proof-reports/FULLSTACK-RUNTIME-ACCEPTANCE.md`.
**Nothing has been committed. Nothing has been pushed.**

## 28. FIELD EXIT VERDICT

`FIELD EXIT: PASS` — all 18 of the field's own exit conditions are
met: application left running and human-inspectable, exact URL
reported (§29), no unrelated files touched, nothing committed, nothing
pushed, both defects found and fixed with real RED/GREEN evidence, no
HUMAN_DECISION_REQUIRED raised, both HARD-DEPs preserved unresolved.
One caveat, fully disclosed rather than hidden: the clean-volume
twice-reproduced regression count (§20) is carried forward from
earlier in this same field rather than freshly re-observed in this
continuation, because reproducing it required a destructive volume
reset that this session's own safety gate declined without further
authorization.

## 29. EXACT BROWSER URL (verified fresh, this turn)

```
Session view:  http://localhost:3000/workspaces/01a0c0d7-58a0-7ec2-8127-c15f8d9f5fea/sessions/a2f4dfbb-a247-4ed1-aa95-b4ed1323e363?as=01a0c0d7-58a0-7044-9da5-79780214fbad
Frontend root: http://localhost:3000/
API health:    http://localhost:8000/healthz
```

## 30. RAW EVIDENCE APPENDIX

All command output quoted in §7, §9, §10, §11, §12, §15, §18, §19,
§20, §21 was captured directly in this report from commands executed
in this turn against the live, running `nquiry-postgres-1`,
`nquiry-api-1`, `nquiry-web-1` containers (each up 9+ hours at time of
this report). No output in this report was reconstructed from memory
except where §20 explicitly says so.

## 31. OPERATIONS VERIFICATION RE-RUN (2026-09-21, same day, second pass)

A second, independent operator-facing verification request was issued
the same day ("AUFGABE: Lokalen Stack starten und Erreichbarkeit
nachweisen"), asking for a fresh, from-scratch startup/health/migration
/regression proof rather than a recap of §1–§30. Executed as follows.

**Step 1 — git status**: NOT clean. Same 9 modified + 4 untracked files
as §27 (this file itself, plus its own not-yet-self-referenced entry,
is now also untracked). All accounted for; none unexpected; this
field's own work remains uncommitted by design (no commit was
authorized).

**Step 2 — startup**: all four `app`-profile services were restarted
(`docker compose --profile app restart`) to capture a genuine fresh
startup log rather than reuse the 9-hour-old one:
```
postgres-1  | database system is ready to accept connections
api-1       | INFO:     Application startup complete.
api-1       | INFO:     Uvicorn running on http://0.0.0.0:8000
worker-1    | nquiry_worker: Phase 0 skeleton — no workers implemented yet.
web-1       | ✓ Ready in 613ms
```
**Correction discovered during this pass**: §5 of this report and §7 of
`RUNTIME_OPERATION.md` previously stated no `worker` service existed in
the `app` Compose profile. This was wrong — `docker-compose.yml:43-52`
defines `worker` with `profiles: ["app"]`; it simply does not appear in
a bare `docker compose ps` once it exits 0, only in `docker compose ps
-a` (`nquiry-worker-1 Exited (0)`). Both documents have been corrected
in place (not silently — this paragraph is the disclosure).

**Step 3 — migrations**: `alembic upgrade head` (via the same
`Config`/`command.upgrade` invocation used throughout this field) ran
to completion with no new revisions applied (DB was already current);
`scripts/verify_migrations.py` output:
```
MIGRATION_STATIC_CHECK::PASS (19 revision(s), single head ['047bdf9bc528'])
MIGRATION_LIVE_CHECK::PASS (db head matches {'047bdf9bc528'})
```

**Step 4 — full test suite, exact PKG-32-convention commands, with
explicit delta**:

| Run | PKG-32 baseline (commit `0884f62`) | Current (this pass) | Delta |
|---|---|---|---|
| `python -m pytest -q` (live-DB) | 1111 passed, 1 skipped, **0 failed** | 1126 passed, 2 skipped, **1 failed** | +15 passed, +1 skipped, +1 failed |
| `unset DATABASE_URL; python -m pytest -q tests/` (pure-Python) | 716 passed, 395 skipped | 716 passed, 409 skipped | +0 passed, +14 skipped |

Explanation, not excuse:
- **+15 passed (live-DB)**: Architecture 17 added ~12 new HTTP/e2e
  tests (`test_http_session_view.py`, `test_http_record_decision.py`,
  plus repository-method tests) and this field added 3 CORS tests —
  all real, all exercised against the live DB.
- **+1 failed (live-DB), NEW since PKG-32**: `test_habb_grant_constraints
  .py::test_grant_without_active_membership_is_rejected`, an unscoped
  `COUNT(*)` assertion tripped by this field's own demo-seed residue
  (one real `human_authority_bindings` row). PKG-32 ran against a
  clean/reset database and never observed this — it is not a
  regression in the tested code, it is a pre-existing test-quality
  gap in that one assertion's scoping, only exposed once real,
  disclosed manual/demo data exists in the DB (documented in
  `RUNTIME_OPERATION.md` §16 before this pass began). **Classification:
  ENVIRONMENT_FAILURE** (test-fixture/database-state mismatch), not
  IMPLEMENTATION_DEFECT, not ARCHITECTURE_CONTRADICTION, not
  UPSTREAM_GAP — the runtime, the domain code, and the migration are
  all unaffected; only this one test's own unscoped assertion is
  sensitive to non-empty, legitimately-disclosed manual data. **Not
  silently repaired** — reported here instead, per this task's own
  instruction 8.
- **+1 skipped (live-DB) / +14 skipped (pure-Python)**: the new
  `NQUIRY_RUN_REAL_COMMIT_TESTS`-gated test
  (`test_http_dispatch_real_connection_lifecycle.py`) plus Architecture
  17's other live-DB-only e2e tests self-skip under the pure-Python,
  no-`DATABASE_URL` run (via each file's own `db_connection` fixture,
  see `tests/e2e/conftest.py:20-25` — not a pytest marker).
- **+0 passed (pure-Python)**: expected — the 3 new CORS tests live in
  `apps/api/tests/`, outside PKG-32's own `tests/`-scoped command, so
  they don't appear in this particular comparison row (they DO appear,
  and pass, in the unscoped `python -m pytest -q` run — 720 passed,
  409 skipped — reported for completeness, not as the PKG-32-comparable
  figure).

**Step 5 — health/smoke check** (fresh, post-restart):
```
$ curl -i http://localhost:8000/healthz
HTTP/1.1 200 OK
{"status":"ok","phase":"0"}
$ curl -o /dev/null -w '%{http_code}\n' ".../sessions/a2f4dfbb-...-..." -H "x-nquiry-actor-user-id: 01a0c0d7-...-...fbad"
200
```

**Step 6 — frontend**: `web` restarted cleanly, `http://localhost:3000/`
returns `200` fresh, post-restart.

**Step 7 — exact URL / access path**:
```
http://localhost:3000/workspaces/01a0c0d7-58a0-7ec2-8127-c15f8d9f5fea/sessions/a2f4dfbb-a247-4ed1-aa95-b4ed1323e363?as=01a0c0d7-58a0-7044-9da5-79780214fbad
```
What you will see: the real Session-view page — challenge title
"Signup conversion dropped 18% after the redesign", 3 real questions,
a decision card in `UNDER_CONSIDERATION` state with 3 options and 2
criteria. **No login exists** (GAP-14-001, open, unchanged) — the
`?as=<userId>` query parameter IS the entire access mechanism; the
UUID `01a0c0d7-58a0-7044-9da5-79780214fbad` is the seeded demo owner's
real, deterministic user id (not a password, not a token — the
identity-claim header `x-nquiry-actor-user-id` this query parameter
populates has zero cryptographic verification, disclosed as
GAP-14-001/`[IMPLEMENTATION CHOICE]` since Architecture 17 §2.1).
Opening `http://localhost:3000/` alone (no path) shows only the
Phase-0 stub root page, not this scenario.

**Step 8 — failures found**: exactly one (the live-DB test failure
above), classified `ENVIRONMENT_FAILURE`, disclosed rather than
repaired. No architecture decision was improvised.
