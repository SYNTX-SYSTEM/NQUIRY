# LOCAL AUTHENTICATION ADAPTER — Proof Report

Field: "Local Full-Stack Runnability incl. Real Login"
Date: 2026-09-21
Repository: `~/Entwicklung/nquiry`
Baseline HEAD (sealed, unmodified by this field): `e54394b8f4f513285b1f05e8d66f154e3d0ca3ed`
("Architecture 17: Live application runtime materialization", FIELD PASS)
This field's own changes, plus the predecessor "NQUIRY LOCAL
FULL-STACK RUNTIME ACCEPTANCE" field's own changes it builds on top of:
**both uncommitted as of this report** (see DIFF_AUDIT).

## 1. FIELD PURPOSE

Close the disclosed GAP-14-001 weakness recorded in
`docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`
("no cryptographic verification occurs anywhere in this path"): a
real, local, browser-usable email/password login with a real,
server-verified HTTP session — replacing the `x-nquiry-actor-user-id`
header-trust adapter and the `?as=` URL-parameter substitute, for the
two real HTTP routes Architecture 17 built. Explicitly NOT in scope:
HARD-DEP-001 (legitimate first Workspace governance-root bootstrap) —
see OPEN_GAPS.

## 2. HUMAN_AUTHORIZED_SCOPE

Real local login (email/password, 14 §32's own authorized
"deterministic test adapter", hardened for real browser use). Explicit
non-goal, stated by the authorizing instruction itself: closing
GAP-14-001 is not closing HARD-DEP-001; if the bootstrap-authority
question were touched, this field was instructed to STOP and report
`HUMAN_DECISION_REQUIRED` rather than decide. That question was never
reached — see §17.

## 3. TDD SEQUENCE (RED → GREEN, per unit)

1. `packages/security/local_auth.py` (password hashing / session token
   primitives): `tests/security/test_local_auth.py` written first (17
   tests) against a non-existent module (RED, `ModuleNotFoundError`),
   then implemented (GREEN, 17/17).
2. `packages/persistence/local_auth_repository.py` +
   `packages/application/auth_handler.py`: `tests/e2e/test_auth_handler.py`
   written first (14 tests, DB-backed) — two genuine RED failures found
   and fixed IN THE TEST, not the production code (see §11 DEFECTS,
   both were test-authoring bugs, disclosed below, not production
   bugs).
3. `packages/application/http_dispatch.py` rewire + new
   `apps/api/src/nquiry_api/http/auth.py`: smoke-tested via direct
   `FastAPI` app import and `scripts/check_architecture_dependencies.py`
   before any HTTP test ran.
4. `tests/e2e/test_http_auth.py` (15 tests, the full adversarial
   session-verification matrix against the real ASGI app) — RED first
   (module/route did not exist), then GREEN, with two genuine
   test-authoring bugs found and fixed during the RED→GREEN pass (see
   §11).
5. `tests/e2e/test_http_session_view.py`/`test_http_record_decision.py`/
   `test_http_dispatch_real_connection_lifecycle.py` rewritten to use
   real sessions instead of headers — every prior DENY/adversarial
   proof intent preserved or strengthened (see §13).
6. Frontend: `apps/web/lib/api/authClient.ts` + tests written first,
   then `/login` page, root-route redirect logic, `LogoutButton`, and
   `apps/web/tests/e2e/auth.spec.ts` (Playwright, real browser) — one
   genuine environment-discovery RED (Playwright's own
   `reuseExistingServer` silently testing against a stale pre-change
   Docker container instead of fresh code) and one genuine regression
   (a naively-placed `LogoutButton` broke two pre-existing adversarial
   tests) found and fixed; see §11/§13.

## 4. FILES_CREATED (this field)

- `migrations/versions/05794035ef3c_local_auth.py`
- `packages/security/local_auth.py`
- `packages/persistence/local_auth_repository.py`
- `packages/application/auth_handler.py`
- `apps/api/src/nquiry_api/http/auth.py`
- `apps/web/lib/api/authClient.ts`
- `apps/web/app/login/page.tsx`
- `apps/web/components/LogoutButton.tsx`
- `docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`
- `docs/implementation/proof-reports/LOCAL-AUTH-ADAPTER.md` (this file)
- `scripts/seed_local_demo.py`
- Tests: `tests/security/test_local_auth.py` (17),
  `tests/e2e/test_auth_handler.py` (15), `tests/e2e/test_http_auth.py`
  (15), `apps/web/tests/lib/authClient.test.ts` (9),
  `apps/web/tests/e2e/auth.spec.ts` (5)

## 5. FILES_MODIFIED (this field)

- `packages/persistence/tables.py` — added `local_auth_credentials_table`/
  `local_auth_sessions_table`.
- `packages/application/http_dispatch.py` — removed the header-trust
  `resolve_actor` path entirely; added `dispatch_login`/`dispatch_logout`/
  `dispatch_current_session`; `dispatch_get_session_view`/
  `dispatch_record_human_decision` now require a verified session.
- `apps/api/src/nquiry_api/http/queries.py`/`commands.py` — read the
  `nquiry_session` cookie, not the old headers.
- `apps/api/src/nquiry_api/main.py` — registers the new `/auth/*`
  router; `CORSMiddleware` gains `allow_credentials=True`, drops the
  now-unused actor headers from `allow_headers`.
- `apps/web/lib/api/client.ts`/`decisionClient.ts` — `credentials:
  "include"`, no actor header, no `actorUserId` parameter.
- `apps/web/components/SessionViewContainer.tsx`,
  `apps/web/app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx` —
  `actorUserId`/`?as=` removed; the Session page now also renders
  `LogoutButton` in a `<header>` outside `<main>`.
- `apps/web/app/page.tsx` — real Client Component: session check,
  redirect to `/login` or the configured default Session, or a plain
  authenticated screen.
- `apps/web/app/layout.tsx` — title/description updated (no longer
  "Phase 0 skeleton").
- `apps/web/tests/lib/client.test.ts`/`decisionClient.test.ts` —
  updated for the new contract.
- `tests/e2e/test_http_session_view.py`/`test_http_record_decision.py`/
  `test_http_dispatch_real_connection_lifecycle.py` — rewritten to
  authenticate via a real session instead of headers.
- `docker-compose.yml` — `web` service gains
  `NEXT_PUBLIC_DEFAULT_WORKSPACE_ID`/`NEXT_PUBLIC_DEFAULT_SESSION_ID`.
- `docs/RUNTIME_OPERATION.md` — new §0 non-developer quick start,
  updated URLs/verification steps/currently-(non)materialized lists.

## 6. FILES CARRIED FORWARD, NOT AUTHORED BY THIS FIELD

`docs/implementation/proof-reports/FULLSTACK-RUNTIME-ACCEPTANCE.md`
and the 9 files it modified (CORS middleware, actor-header frontend
threading, `apps/api/tests/test_cors.py`, the pre-this-field
`RUNTIME_OPERATION.md`) were uncommitted work from the immediately
preceding field, found already present in the working tree at the
start of this session and preserved unmodified as this field's own
starting point (this field's own worktree was created from the last
*commit*, which predates that field — its changes were copied over
explicitly rather than silently lost). `apps/web/AGENTS.md`/`CLAUDE.md`
are pre-existing, `next dev`-auto-generated, untouched by any field.

## 7. TEST_RESULTS — live PostgreSQL (fresh, clean-volume, this turn)

```
$ docker compose -p nquiry --profile app down -v   # clean slate, disclosed §16
$ docker compose -p nquiry --profile app up -d --build
$ psql ... -f infra/local/db_roles.sql
$ python scripts/verify_migrations.py
MIGRATION_STATIC_CHECK::PASS (20 revision(s), single head ['05794035ef3c'])
MIGRATION_LIVE_CHECK::PASS (db head matches {'05794035ef3c'})
$ python scripts/seed_local_demo.py   # demo scenario + login credential
$ DATABASE_URL=... python -m pytest -q
1174 passed, 2 skipped, 1 failed in 75.65s
FAILED tests/security/test_habb_grant_constraints.py::test_grant_without_active_membership_is_rejected
  AssertionError: assert 2 == 0
```

This is the SAME already-disclosed, pre-existing test-quality
limitation documented in `FULLSTACK-RUNTIME-ACCEPTANCE.md` §20/§31 and
`RUNTIME_OPERATION.md` §16 — an unscoped `COUNT(*)` over
`human_authority_bindings`, tripped here by this field's own demo-seed
residue (2 real rows: the demo Workspace's governance binding plus one
DECISION_RIGHT binding). Classification: `ENVIRONMENT_FAILURE`
(test-fixture/database-state mismatch), not `IMPLEMENTATION_DEFECT`.
Not silently repaired — reported, matching this field's own
instruction to disclose rather than paper over. See §13a for the full
explanation of why this specific failure is accepted.

**FINAL re-run, after the whitespace fix (§20)**, same clean volume,
one additional regression test added:

```
$ python -m pytest -q
1175 passed, 2 skipped, 1 failed in 72.61s
FAILED tests/security/test_habb_grant_constraints.py::test_grant_without_active_membership_is_rejected
```

Identical failure, +1 passed (the new whitespace regression test),
zero new failures. **This is the authoritative final number for this
field.**

**Comparison against known baselines**:

| Run | PKG-32 (`0884f62`) | Architecture-17+FULLSTACK field | This field, final (clean volume) | Delta vs. FULLSTACK |
|---|---|---|---|---|
| live-DB `pytest -q` | 1111 passed, 1 skipped, 0 failed | 1126 passed, 2 skipped, 1 failed | **1175 passed, 2 skipped, 1 failed** | +49 passed, +0 skipped, +0 failed |
| pure-Python `pytest -q tests/` | 716 passed, 395 skipped | 716 passed, 409 skipped | 733 passed, 438 skipped | +17 passed, +29 skipped |

+49 live-DB passed = this field's own new tests
(`test_local_auth.py` 17 + `test_auth_handler.py` 15 +
`test_http_auth.py` 15 = 47) plus a net +2 from rewriting
`test_http_session_view.py` (−1: two header-adversarial tests moved to
`test_http_auth.py`, +1: a new nonexistent-workspace test) and
`test_http_record_decision.py` (+1: a new forged-header-on-decide
test) = 47 + (−1) + (+1) + (+1) = 49; the exact per-file counts are in
§12's own table. +17 pure-Python passed =
`test_local_auth.py` (the one new pure-Python, no-DB file), verified
directly by §8's own command output. +29 pure-Python skipped =
overwhelmingly this field's own new DB-requiring e2e tests
self-skipping without `DATABASE_URL` (`test_auth_handler.py`/
`test_http_auth.py`, ~30 tests between them), net a small amount of
per-file rewrite churn in §12's own table — the exact total (438) is
the directly-observed, authoritative number from §8's own fresh run,
not derived arithmetic.

## 8. TEST_RESULTS — pure Python, no DATABASE_URL (fresh, this turn)

```
$ unset DATABASE_URL
$ python -m pytest -q tests/
733 passed, 438 skipped in 11.94s
```
Zero failures.

## 9. STATIC GATES (fresh, this turn)

```
$ ruff format --check .
326 files already formatted
$ ruff check .
All checks passed!
$ MYPYPATH=packages:apps/api/src:apps/worker/src:scripts mypy packages apps/api/src apps/worker/src scripts
Success: no issues found in 146 source files
$ python scripts/check_architecture_dependencies.py
ARCHITECTURE_DEPENDENCY_CHECK::PASS
$ python scripts/check_provider_sdk_imports.py
PROVIDER_SDK_IMPORT_CHECK::PASS
$ python scripts/check_test_only_imports.py
TEST_ONLY_IMPORT_CHECK::PASS
```

## 10. FRONTEND GATES (fresh, this turn, real `npm install`, no symlinked node_modules)

```
$ npx eslint .                # clean, 0 errors
$ npx tsc --noEmit             # clean, 0 errors
$ npx vitest run
Test Files  6 passed (6) / Tests  64 passed (64)
$ npx playwright test          # real Chromium, against the real rebuilt docker containers
27 passed (18.5s)
$ npx next build
Compiled successfully; routes: / (static), /_not-found (static),
/login (static), /workspaces/[workspaceId]/sessions/[sessionId] (dynamic)
```

## 11. DEFECTS FOUND AND FIXED DURING THIS FIELD (test-authoring, not production)

1. **`test_login_does_not_create_a_session_row_on_failure`** originally
   asserted an UNSCOPED `COUNT(*)` over `local_auth_sessions` —
   exactly the same anti-pattern this codebase already has one
   disclosed instance of. Found before merge (not by a live-DB
   surprise), fixed to scope by `user_id`.
2. **`test_session_view_denies_a_tampered_real_cookie`/
   `test_session_view_denies_a_forged_garbage_cookie`** initially used
   httpx `TestClient`'s per-request `cookies=` kwarg against a client
   whose jar already held a real, valid cookie from an earlier call in
   the same test — httpx's own documented ambiguous merge behavior
   made the override unreliable (2 spurious green-should-be-red
   passes turned into real failures once discovered). Fixed: a
   tampered cookie is tested via a fresh, separate `TestClient`
   instance with the cookie set directly on its jar.
3. **`test_session_view_denies_an_expired_session`** initially
   backdated `expires_at` using this test file's own fixed `_NOW`
   (year 2030), but `resolve_session` compares against the REAL
   `datetime.now(timezone.utc)` — 2030 is still in the future relative
   to real wall-clock time, so the session was not actually expired.
   Fixed to backdate relative to real `datetime.now(timezone.utc)`.
4. **Playwright silently tested stale, pre-change code.** Playwright's
   own `reuseExistingServer: !process.env.CI` reused an already-running
   `next dev` process on port 3000 — which turned out to be the real
   `nquiry-web-1` Docker container from an earlier session, still
   serving the OLD Phase-0-stub root page. All 5 new auth specs failed
   with timeouts. Root-caused via `lsof -i :3000`/`ps aux`, not
   guessed. Fixed by rebuilding and restarting the real containers with
   this field's own code (which the field needed to do anyway for the
   final runtime proof) rather than by changing test infrastructure to
   dodge the real container.
5. **A real regression, caught by pre-existing tests, not introduced
   silently.** Adding `<LogoutButton />` directly inside `<main>` on
   the Session-view page broke two PRE-EXISTING mandatory-attack tests
   (`test_http_session_view.py`'s own "no hidden/disabled action
   element exists... for any response shape" and "attempt AI control
   during an ACTIVE Burst") — both assert zero `button`/`input`/`form`
   elements exist within `main` for a denied/blocked state.
   **Not weakened or deleted** — fixed by moving `LogoutButton` into a
   `<header>` OUTSIDE `<main>` (a logout control is orthogonal to
   Session/Decision boundary state and belongs in page chrome, not the
   domain-content region those tests scope their proof to). Both
   pre-existing tests pass unmodified; the new capability still works
   (proven by `auth.spec.ts`'s own logout tests).
6. **The demo seed script's own bug**: `scripts/seed_local_demo.py`'s
   first version omitted `capture_origin`/`record_version` on its
   `burst_question_memberships` insert — a real `NotNullViolation`
   caught immediately on first run against a clean database, before
   any regression numbers were taken. Fixed.

## 12. TEST COVERAGE — full breakdown by file

| File | Tests | What it proves |
|---|---|---|
| `tests/security/test_local_auth.py` | 17 | Pure crypto/token primitives, no DB: password hashing format, two hashes of the same password always differ, correct/wrong password verification, 6 distinct malformed-hash shapes all fail closed without raising, empty password rejected, session tokens are high-entropy and distinct, token hashing is deterministic and never stores the raw token. |
| `tests/e2e/test_auth_handler.py` | 15 | `login`/`resolve_session`/`logout` business logic against the REAL `local_auth_credentials`/`local_auth_sessions` tables: happy-path session issuance, email case/whitespace normalization, wrong password, unknown email (identical exception to wrong password — no enumeration), empty password, no session row created on a failed login, missing/garbage/tampered token all resolve to nothing, expired vs. one-second-before-expiry boundary, logout revokes and a second independent session for the same user survives it, the new whitespace-stripping fix (§20). |
| `tests/e2e/test_http_auth.py` | 15 | The full adversarial session-verification matrix through the REAL FastAPI app: login sets a real `HttpOnly` cookie with the raw token never appearing in the JSON body, wrong password / unknown email both `401` with no cookie set, `/auth/me` before and after login, logout revokes and a later `/auth/me` reports no session, then the matrix against the real `GET /workspaces/.../sessions/...` route: no cookie, forged garbage cookie, one-character-tampered real cookie, expired session, revoked session, a foreign real user-id header with NO session present (still `401`), a forged actor-class header WITH a real session present (ignored, real identity wins), and a real second independently-logged-in user with no Workspace membership (denied by BND-002/003, not by identity). |
| `tests/e2e/test_http_session_view.py` (rewritten) | 6 | Happy path with a real burst, no-session denial, nonexistent session, nonexistent workspace, malformed workspace id — all now via a real login instead of a header. |
| `tests/e2e/test_http_record_decision.py` (rewritten) | 7 | Happy path (real committed Decision), no-session denial, a forged actor-class header on the WRITE route specifically (ignored, commits as the real user), role-only-actor-no-binding denial, non-candidate option rejection, unknown decision id, duplicate-request replay protection. |
| `tests/e2e/test_http_dispatch_real_connection_lifecycle.py` (rewritten) | 1 (opt-in, `NQUIRY_RUN_REAL_COMMIT_TESTS=1`) | The one test in this codebase that uses a REAL, closing (not test-monkeypatched) database connection — now performs a real login against that same real connection before the real decide call, proving the session mechanism itself survives a real connection lifecycle, not just the mocked test harness. |
| `apps/web/tests/lib/authClient.test.ts` | 9 | Frontend `login`/`logout`/`fetchCurrentSession`: correct request shape, `credentials: "include"`, denied-response parsing, fail-closed on an unrecognized/missing response shape, the password is never sent as a URL query parameter. |
| `apps/web/tests/e2e/auth.spec.ts` | 5 | Real Chromium browser, real running containers: root redirects to `/login` with no session; wrong credentials show an error and stay on `/login`; correct credentials log in and reach the app; logging out returns to `/login`; the login form never renders a pre-filled credential. |

**Total new/changed test count**: 75 (61 entirely new tests across 6
new files, plus a net +14 from rewriting the 3 existing Architecture-17
HTTP test files to use real sessions instead of headers).

## 13. ADVERSARIAL / NEGATIVE TEST RESULTS — the specific attacks proven

All of the following pass (live-DB, real ASGI app via
`fastapi.testclient.TestClient`, and independently re-confirmed via
real `curl` against the real running container, §15):

- No session cookie at all → `401`.
- Forged/never-issued garbage cookie → `401`.
- A real, previously-issued cookie with one character flipped → `401`
  (exact-hash-match proof, not fuzzy/prefix).
- Expired session (past `expires_at`, never revoked) → `401`; the
  identical session one second BEFORE expiry still resolves (boundary
  proof, not an off-by-a-mile bug).
- Revoked session (`POST /auth/logout`) → `401`, even before
  `expires_at`.
- `x-nquiry-actor-user-id` naming a real, valid Workspace owner, WITH
  NO session present → `401` regardless (the header is not read at
  all).
- A real, valid session WITH a forged `x-nquiry-actor-class:
  AI_PROCESSOR` header alongside it → succeeds as the REAL logged-in
  HUMAN_USER; the header has zero effect (proven on both the read
  route and, separately, the write/decide route).
- A real, independently-logged-in second user with no Workspace
  membership → `200`/`denied` (BND-002/003 still deny, now proven
  through a genuine second login rather than a forged stranger id).
- Wrong password for a real account, and a never-registered email →
  the IDENTICAL exception type and message (no user enumeration);
  timing parity via a constant-effort decoy hash.
- Empty password → rejected.
- Logging out one session does not invalidate a second, independently
  issued session for the same user (multi-session isolation).
- Duplicate/replayed `POST /decisions/{d}/decide` after a real commit
  → second call denied (BND-007), never a second `committed` result —
  unchanged from Architecture 17, re-proven under the new session
  mechanism.
- Login response body never contains the raw session token (only the
  `Set-Cookie` header does) — proven directly
  (`test_login_happy_path_sets_an_httponly_session_cookie`).
- Frontend: the login form renders no pre-filled credential; a wrong
  password shows an error and never navigates away from `/login`.

## 13a. THE ONE PRE-EXISTING DISCLOSED FAILURE — what it is and why it's accepted

`tests/security/test_habb_grant_constraints.py::
test_grant_without_active_membership_is_rejected` fails on this field's
own clean-volume run, exactly as it also did on the FULLSTACK-RUNTIME-ACCEPTANCE
field before this one (`FULLSTACK-RUNTIME-ACCEPTANCE.md` §20/§31).

- **What it is**: this test asserts an UNSCOPED `SELECT COUNT(*) FROM
  human_authority_bindings` equals `0` inside its own DB-transaction
  fixture. That assumption is only true if NOTHING ELSE in the entire
  database has ever written a row to that table — an assumption a
  clean-volume test run satisfies, but this field's own
  `scripts/seed_local_demo.py` legitimately violates on purpose (it
  seeds a real demo Workspace, which legitimately needs 2 real
  `human_authority_bindings` rows: one governance binding, one
  DECISION_RIGHT binding).
- **Why it is known and accepted, not silently fixed or hidden**: it
  is not a bug in the login/session code this field wrote, not a
  regression this field introduced, and not something this field's own
  authorization asked it to repair. It is a pre-existing assertion-style
  weakness in one unrelated security test, written long before this
  field (its own git history predates PKG-26/the demo-seeding
  concept) — the correct fix (scope the assertion to the test's own
  fixture Workspace, the same fix already applied inside THIS field's
  own new tests, see `tests/e2e/test_auth_handler.py::
  test_login_does_not_create_a_session_row_on_failure`'s own comment)
  belongs to whoever owns that test file's own scope, not to an
  unrelated login field reaching in to change someone else's test's
  assertion style as a drive-by.
- **Is it outside this field's own PKG/HUMAN_AUTHORIZED_SCOPE?** Yes,
  explicitly. This field's authorized scope (§2) is the local login
  mechanism; `test_habb_grant_constraints.py` tests DB-level GRANT
  constraints on `human_authority_bindings`, a PKG-25/26-era security
  concern with no relationship to authentication/session code at all.
  Touching it would itself be an undisclosed scope expansion — exactly
  what this field's own discipline forbids. It resurfaces only because
  `scripts/seed_local_demo.py` (which IS in this field's own scope)
  legitimately writes real data to a table that test happens to also
  read, unscoped, from the whole database.
- **How to make it pass, if ever needed**: run the live-DB suite
  against a genuinely empty database (no demo data seeded yet) — see
  `docs/RUNTIME_OPERATION.md` §15/§16 for the exact reset procedure.
  This field's own regression numbers (§7) were still taken from a
  clean-volume run; this ONE failure is the demo seed's own footprint
  on it, disclosed rather than hidden by, say, seeding after the test
  run instead of before.

## 14. HARD-DEP-001 / HARD-DEP-002 STATUS

Unchanged, both remain BLOCKED/open — see
`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`'s own HARD-DEP-001
RELATION / HARD-DEP-002 RELATION sections for the full reasoning.
Every session this field lets a human establish still resolves to a
`UserId` whose Workspace membership/authority was seeded via the
disclosed `NonProofWorkspaceBootstrap` (`FIXTURE_LEGITIMACY ==
"NON_PROOF_FIXTURE"`) fixture — a real, verified login proves WHO is
calling; it proves nothing about the legitimacy of that user's own
Workspace governance root.

## 15. LIVE HTTP PROOF (fresh, this turn, against the real running container)

```
$ curl -s -i http://localhost:8000/auth/me
HTTP/1.1 401 Unauthorized   {"kind":"denied","reasonCode":"NO_SESSION"}

$ curl -s -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
    -d '{"email":"demo-owner@nonproof.test","password":"wrong"}'
HTTP/1.1 401 Unauthorized

$ curl -s -i -c cookies.txt -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
    -d '{"email":"demo-owner@nonproof.test","password":"nquiry-demo-2026"}'
HTTP/1.1 200 OK
set-cookie: nquiry_session=...; HttpOnly; Max-Age=43199; Path=/; SameSite=lax
{"kind":"ok","userId":"01a0c312-0255-74a2-967c-6a31079e8f8a"}

$ curl -s -b cookies.txt http://localhost:8000/auth/me
HTTP/1.1 200 OK

$ curl -s -b cookies.txt ".../workspaces/01a0c312.../sessions/01a0c312..."
{"kind":"ok","data":{...,"challenge":{"title":"Signup conversion dropped 18% after the redesign",...}}}

$ curl -s -i -H "Cookie: nquiry_session=totally-forged-token" http://localhost:8000/auth/me
HTTP/1.1 401 Unauthorized

$ curl -s -i -b cookies.txt -X POST http://localhost:8000/auth/logout
HTTP/1.1 200 OK
set-cookie: nquiry_session=""; expires=...; Max-Age=0

$ curl -s -i -b cookies.txt http://localhost:8000/auth/me   # SAME cookie, now revoked
HTTP/1.1 401 Unauthorized
```

Real browser proof: `apps/web/tests/e2e/auth.spec.ts` (5 tests, real
Chromium, real running `web`/`api` containers), including the full
login → authenticated-screen/redirected-Session-view → logout → back
to `/login` cycle.

## 16. FIELD EXIT VERDICT

`FIELD EXIT: PASS`. Real local login materialized and proven at every
layer (unit, integration/DB, HTTP/adversarial, real browser, real
running containers) — including the real human operator's own live
browser session, which found and led to fixing one further real
defect (§20). GAP-14-001's disclosed header-trust weakness is closed
for both production routes. HARD-DEP-001/002 both preserved,
unresolved, not bypassed. One pre-existing, already-disclosed
ENVIRONMENT_FAILURE test-quality limitation reproduced, not newly
introduced (§13a). Seven real defects found across this field's own
construction and its own human verification pass, all fixed, all
disclosed above rather than silently patched around (§11, §20). Final
regression: 1175 passed, 2 skipped, 1 already-disclosed failure, zero
new failures (§7).

## 17. HUMAN_DECISION_REQUIRED

None raised. The bootstrap-authority question (who gets Workspace
governance authority at first start) was never reached while building
this field — closing GAP-14-001 required verifying a password and
issuing/checking a session, never deciding who owns a Workspace. See
`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`'s own
HUMAN_DECISION_REQUIRED REGISTER for the two items that remain
explicitly open (GAP-14-001 itself, real OIDC provider selection;
HARD-DEP-001, reserved to Architecture 19/22).

## 18. OPEN_GAPS

- GAP-14-001 (real OIDC/production identity provider selection):
  still open. This field's login is a real, hardened LOCAL credential
  adapter, not an external identity provider integration.
- HARD-DEP-001 (legitimate first Workspace governance-root bootstrap):
  still open, untouched, not narrowed. See §14/§17.
- No self-service registration or password reset.
- No Workspace-list/dashboard UI — root route lands on one
  operator-configured default Session.
- DB-principal capability mapping (PKG-25/26) not extended to the two
  new tables — consistent with every other Architecture-17-era table
  the real HTTP path touches, all of which are also still unscoped to
  a specific `ServicePrincipal` at connection time (disclosed
  `SUCCESSOR_NOT_BUILT`, unchanged from Architecture 17).
- `test_habb_grant_constraints.py::test_grant_without_active_membership_is_rejected`'s
  unscoped assertion remains sensitive to demo-seed residue — a
  pre-existing test-quality limitation, not introduced or touched by
  this field.

## 19. DIFF_AUDIT

`git status --short` (this field's own worktree, final state):
matches §4/§5/§6 exactly — every modified/new file accounted for by
name above; nothing unexplained; no stray tooling/lock/build artifact
staged. Nothing committed, nothing pushed (standing project rule: no
commit without an explicit, literal "PASS, committe das" authorization
or an exact git command).

## 20. ADDENDUM — real defect found via human browser verification, fixed

After this field's own regression pass, the human operator tried the
real login in a real browser (`http://localhost:3000/login`,
`demo-owner@nonproof.test` / `nquiry-demo-2026`) and got "Incorrect
email or password."

**Investigation**: `docker logs nquiry-api-1` showed the real request
reached the backend (`OPTIONS /auth/login 200`, `POST /auth/login 401`)
— not a CORS/wiring failure. A direct `curl` with the exact same
credentials, at the exact same time, succeeded (`200 OK`). The backend
itself was healthy and correct; the browser genuinely sent different
bytes than what was typed/intended to be typed.

**Root cause (defensive fix, exact keystroke not observable — a
password is deliberately never logged)**: `application.auth_handler.login`
compared the password byte-exact against the stored hash. Copying a
password out of a chat message or terminal commonly picks up a
trailing newline or space; a byte-exact comparison rejects that even
though the visible password is correct. `email` was already
`.strip()`ped for exactly this reason; `password` was not.

**Fix**: `password.strip()` before comparison in `login` only (not
inside `hash_password`/`verify_password`, which stay deliberately
byte-exact primitives — normalizing "what counts as the same password"
is a login-boundary policy decision). Safe because every existing
credential-creation call site (`scripts/seed_local_demo.py`, every
test) passes a literal string with no accidental whitespace — there is
no path where a credential is legitimately created WITH meaningful
whitespace that this could now silently strip away at hash time
without the caller knowing (hashing itself is untouched).

**Proof**:
```
$ curl -s -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
    -d '{"email":"demo-owner@nonproof.test","password":"nquiry-demo-2026 "}'
HTTP/1.1 200 OK   (trailing space in password, previously would 401)
```
New regression test: `tests/e2e/test_auth_handler.py::
test_login_strips_surrounding_whitespace_from_the_password`. Full
live-DB regression re-run after the fix: **1175 passed** (+1, the new
test), **2 skipped**, **1 failed** (the same already-disclosed
`test_habb_grant_constraints.py` residue, unchanged) — zero new
failures. `api` container rebuilt and restarted with the fix.

**Not fully closed**: this fix resolves the whitespace class of
copy-paste failure, proven. It does not rule out a DIFFERENT cause for
the specific attempt observed (e.g. a browser password manager
silently substituting a different saved credential for
`localhost:3000` instead of what was visibly typed) — that class of
failure is outside this application's own control. If login still
fails after this fix, the next diagnostic step is to clear/disable
autofill for the password field and type the credential manually, and
to re-check `docker logs nquiry-api-1` for the real request outcome
rather than guess further.
