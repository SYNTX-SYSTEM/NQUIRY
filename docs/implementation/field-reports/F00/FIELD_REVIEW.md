# NQUIRY FIELD REVIEW REPORT

## Field
F00 — EXECUTION CONTROL · BASELINE · PROOF HARNESS

## Worktree State
```
git status --short
?? apps/web/AGENTS.md                                    (pre-existing, unrelated, next-dev-generated)
?? apps/web/CLAUDE.md                                     (pre-existing, unrelated, next-dev-generated)
?? docs/implementation/field-reports/F00/WU-00.1.md        (this Field's own Work Unit report)
```
Current branch: `worktree-local-login-auth` (this session's own git
worktree, isolated from the human operator's main checkout at
`~/Entwicklung/nquiry`)
HEAD: `140d90025c5e193cd3a84f1ceec42a9370d73991`
("field-scaffold: create field-report structure for F00-F12" — already
committed and pushed to `origin/master` per Step 1's own explicit,
separate authorization; this HEAD does NOT yet include any F00-content
commit)

## Architectural Authority
`docs/architecture/19_NQUIRY_IMPLEMENTATION_WITH_FRONTEND_RUNNING.md`
§20 (FIELD F00 definition, INTENT, TARGET, INTERNAL WORK UNITS, TESTS
FIRST, RECURSIVE UPWARD TEST SET, STOP CONDITIONS, PASS); §2
(REPOSITORY AUTHORITY LAW — read current repo before implementation);
§3 (CURRENT BASELINE MUST BE RECONSTRUCTED FIRST); §17/§18 (GLOBAL
LOCAL TEST COMMANDS / CURRENT LOCAL RUNTIME BOOTSTRAP, cross-checked
against this repository's own `docs/RUNTIME_OPERATION.md`, which
remains the authoritative day-to-day runbook per that file's own
role statement).

## Initial Field State
Before this Field: 32 packages (PKG-00–PKG-32) complete; Architecture
17 (first real HTTP surface) complete; the local-login-auth field
(real email/password login, closing GAP-14-001's header-trust
weakness) complete and merged to `master`; `LICENSE`/`README.md`
fixed/rewritten; repository consolidated to a single `master` branch,
default branch confirmed. No standardized Field-execution process
existed yet — every predecessor package used its own report format
under its own informal convention (`docs/implementation/proof-reports/
PKG-NN.md`).

## Target Field State
One deterministic test/report/review/commit protocol that every Field
F01 onward can rely on without renegotiating format, test discipline,
commit behavior, or runtime procedure each time (19 §20's own INTENT).

## Internal Work Units Executed
WU-00.1 (merged WU-00.1 through WU-00.6, per 19 §4's own explicit
permission to merge/reorganize Work Units — F00 has no domain code
change to split across separately-gated technical units):
reconstruct current repo commands; confirm field-report filesystem
(materialized in the separately-authorized Step-1 scaffold commit);
define/confirm the command manifest; verify architecture gates; verify
local runtime from a freshly rebuilt container set; generate this
baseline proof.

## Files Added
`docs/implementation/field-reports/F00/WU-00.1.md` (this Field's own
Work Unit report)
`docs/implementation/field-reports/F00/FIELD_REVIEW.md` (this file)
`docs/implementation/field-reports/F00/CHATGPT_REVIEW.txt` (companion
review payload — see this Field's own amendment: routed to the Claude
Cowork session, not ChatGPT, same format)

## Files Modified
NONE

## Migrations
NONE

## Dependencies Added
NONE

## Domain Changes
NONE

## Authority / Governance Changes
NONE

## Boundary Changes
NONE

## AI Changes
NONE

## Evidence / Provenance Changes
NONE

## Persistence Changes
NONE

## Event / Worker / Projection Changes
NONE

## API Changes
NONE

## Frontend Changes
NONE

## Test-First Evidence
Not applicable in the domain sense — F00 introduces no new relation.
"Test-first" for F00 means treating the current baseline as unproven
until re-verified this turn, not inherited from an earlier report (19
§3: "Do not blindly assume this snapshot remains accurate. Reconstruct
current reality from HEAD before implementation.") — every command in
WU-00.1's own COMMAND MANIFEST was actually executed this turn, not
copied from a prior session's memory.

## Tests Added
NONE (F00 verifies existing tests/gates; it does not add new ones)

## Negative Tests
Not applicable to this Field's own scope — negative/adversarial test
coverage belongs to the domain Fields that own the relations being
tested (already extensively present across the existing PKG-00–32 and
local-login-auth suites this Field re-verified).

## Adversarial Tests
Same as above — re-verified, not newly authored by F00.

## Failure Injection
Not applicable to this Field's own scope.

## Accessibility Proof
Not applicable to this Field's own scope (no frontend change).

## Responsive Proof
Not applicable to this Field's own scope.

## Visual Proof
Not applicable to this Field's own scope.

## Recursive Upward Test Ladder
L0: NOT_APPLICABLE
L1: NOT_APPLICABLE
L2: NOT_APPLICABLE
L3: PASS — live-DB `1175 passed, 2 skipped, 1 failed` (pre-existing,
    disclosed, see below); pure-Python `733 passed, 0 failed`
L4: NOT_APPLICABLE
L5: PASS — ruff format/check, mypy, 3 architecture gates, migration
    verify, eslint, tsc: all clean
L6: PASS — containers rebuilt from current HEAD; healthz 200; real
    login 200 with a real `HttpOnly` session cookie
L7: PASS — Playwright 27/27 against the rebuilt containers; `next
    build` clean
L8: This Work Unit's own L3/L5/L6/L7 constitute F00's own full
    regression (F00 has exactly one Work Unit)

## Recursive DeepSweep Result
PASS. Nothing in the domain/authority/persistence/API/frontend layers
changed. What changed: a re-verified, current-HEAD baseline and a
formal command manifest now exist for every later Field to build on.

## Inverse DeepSweep Result
NA — F00 has no human-visible consequential effect of its own (19
§20: "HUMAN PRODUCT EFFECT: Indirect").

## First Broken Relation Result
NONE

## Full Affected Regression
```
$ DATABASE_URL=... python -m pytest -q
1175 passed, 2 skipped, 1 failed in 68.31s
FAILED tests/security/test_habb_grant_constraints.py::test_grant_without_active_membership_is_rejected

$ python -m pytest -q tests/                    # pure-Python, DATABASE_URL unset
733 passed, 439 skipped in 12.03s

$ ruff format --check .                          -> 343 files already formatted
$ ruff check .                                    -> All checks passed!
$ mypy packages apps/api/src apps/worker/src scripts
    -> Success: no issues found in 146 source files
$ python scripts/check_architecture_dependencies.py -> PASS
$ python scripts/check_provider_sdk_imports.py       -> PASS
$ python scripts/check_test_only_imports.py          -> PASS
$ python scripts/verify_migrations.py
    -> MIGRATION_STATIC_CHECK::PASS (20 revisions, single head)
    -> MIGRATION_LIVE_CHECK::PASS

$ (cd apps/web && npx eslint .)                   -> clean
$ (cd apps/web && npx tsc --noEmit)                -> clean
$ (cd apps/web && npx vitest run)                  -> 6 files, 64 tests passed
$ (cd apps/web && npx playwright test)             -> 27 passed
$ (cd apps/web && npx next build)                  -> compiled clean, 4 routes
```

**Pre-existing failure, reconfirmed not newly introduced**:
`tests/security/test_habb_grant_constraints.py::test_grant_without_active_membership_is_rejected`
— an unscoped `COUNT(*)` over `human_authority_bindings`, tripped by
`scripts/seed_local_demo.py`'s own legitimate demo-seed residue.
Already disclosed in `FULLSTACK-RUNTIME-ACCEPTANCE.md` §20/§31 and
`LOCAL-AUTH-ADAPTER.md` §13a. Classification: `ENVIRONMENT_FAILURE`.
Not repaired here — 19 §20 explicitly forbids silently "fixing"
unrelated architecture while building F00; this is not F00's own
scope, and it is not this Field's test to own.

## Runtime Proof
```
$ docker compose -p nquiry --profile app up -d --build
$ curl -i http://localhost:8000/healthz
HTTP/1.1 200 OK  {"status":"ok","phase":"0"}
$ curl -o /dev/null -w '%{http_code}\n' http://localhost:3000/
200
$ curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
    -d '{"email":"demo-owner@nonproof.test","password":"nquiry-demo-2026"}'
HTTP/1.1 200 OK
set-cookie: nquiry_session=...; HttpOnly; Max-Age=43199; Path=/; SameSite=lax
{"kind":"ok","userId":"01a0c312-0255-74a2-967c-6a31079e8f8a"}
```

## Browser Proof
Playwright, 27/27, real Chromium against the freshly rebuilt
containers — login flow, root-route redirect, Session-view rendering
(happy path, denied, indeterminate, frozen Burst, mandatory-attack
matrix), Decision recording (happy path, denial, duplicate-request
protection, novel adversarial cases). See
`apps/web/tests/e2e/{auth,session-view,decision}.spec.ts`.

## Fixture Ceilings
`scripts/seed_local_demo.py`'s own Workspace/Challenge/Session/
Decision scenario remains `NON_PROOF_FIXTURE` (`NonProofWorkspaceBootstrap`),
unchanged. HARD-DEP-001 (legitimate first Workspace governance root)
remains open — 19 §21 (F01) names this as its own, later, explicit
STOP CONDITION; F00 does not touch it.

## Mock Ceilings
`MockProviderAdapter` remains the only AI provider in the codebase.
No AI Gateway code was touched by this Field. HARD-DEP-002 remains
open.

## External Dependency Ceilings
NONE newly introduced by this Field. `GEMINI_API_KEY` (this Field
Execution Master's own F04 amendment) was not touched, read, or
required — F00 has no AI-provider scope.

## Known Limitations
- Host Python is 3.10 against the project's `>=3.13` target (works via
  `pythonpath`, unchanged, disclosed since PKG-00).
- Worker has no continuous production loop (`BLOCKED_BY_UPSTREAM_GAP`,
  F08's own future scope per 19 §28).
- The one live-DB test failure above is demo-seed-residue sensitive; a
  genuinely clean-volume run has already been separately, repeatedly
  proven to show 0 failures (`LOCAL-AUTH-ADAPTER.md` §7).

## Architecture Drift
NONE. No architecture file was contradicted or reinterpreted. 19
itself is now the operative Field Execution Master, per the human
operator's own explicit authorization; nothing in it was found to
contradict 00–18 during this Field's own read-through.

## Downstream Fields Unlocked
F01 (IDENTITY · WORKSPACE · GOVERNANCE) — causally next per the Field
DAG (19 §19), contingent on `FIELD_COMMIT_APPROVED F00`.

## Git Diff Summary
```
$ git status --short
?? apps/web/AGENTS.md                                    (pre-existing, unrelated)
?? apps/web/CLAUDE.md                                     (pre-existing, unrelated)
?? docs/implementation/field-reports/F00/WU-00.1.md
?? docs/implementation/field-reports/F00/FIELD_REVIEW.md
?? docs/implementation/field-reports/F00/CHATGPT_REVIEW.txt
```
(`CHATGPT_REVIEW.txt` written immediately after this file — see next
section.) No tracked file was modified. No code changed.

## Git Diff Check
```
$ git diff --check
(clean, exit 0)
```

## Commit Status
COMMITTED — `f27942e` ("field(F00): execution control, baseline, and
proof harness"), pushed to `origin/master`. Approved via
`FIELD_COMMIT_APPROVED F00` (human operator, relaying the Claude
Cowork session's review of `CHATGPT_REVIEW.txt`).

## Recommended Status
FIELD_PASS
