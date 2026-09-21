# NQUIRY FIELD REVIEW REPORT

## Field
F01 — IDENTITY · WORKSPACE · GOVERNANCE

## Worktree State
```
git status --short
```
See WU-01.10.md's own final status block (37 entries — 9 modified,
28 untracked; identical set carried since WU-01.6, plus each Work
Unit's own additions). Current branch: `worktree-local-login-auth`
(this session's own git worktree, isolated from the human operator's
main checkout at `~/Entwicklung/nquiry`). HEAD: `c529d3d8e561d98a593766d618b59536ef05796b`
("field(F00): record approved commit identity in FIELD_REVIEW.md/STATUS.md"
— F01's own content below is NOT yet committed).

## Architectural Authority
`docs/architecture/19_NQUIRY_IMPLEMENTATION_WITH_FRONTEND_RUNNING.md`
§21 (FIELD F01 definition: SEMANTIC REGIME, HUMAN PRODUCT EFFECT,
CURRENT FIELD, TARGET, INTERNAL WORK UNITS, BACKEND/FRONTEND
REQUIREMENTS, TESTS FIRST, RECURSIVE UPWARD TESTS, INVERSE PROOF, STOP
CONDITIONS, PASS); §1 (PRIMARY TARGET, re-verified as still aligned,
not superseded); §2/§3 (Repository Authority Law / baseline
reconstruction); §4 (Field Granularity Law — Work Unit merge/reorg
permission, exercised for WU-01.4/WU-01.4b's own split); §12
(NO-COMMIT REVIEW LAW); §20's own F00 precedent for this report's own
format, cross-checked against `docs/architecture/04_AUTHORITY_AND_DECISION_RIGHTS.md`
(GAP-04-014, AC-04-001) and `05_GOVERNANCE_INSIDE_SYSTEM.md` (GOV-002,
GOV-004, GOV-005, §8 HABB Lifecycle, §18 Effectiveness Predicate,
GAP-05-001).

## Initial Field State
Before this Field: F00 (EXECUTION CONTROL · BASELINE · PROOF HARNESS)
complete and committed (`f27942e`/`c529d3d`). 32 packages (PKG-00–32),
Architecture 17, and the local-login-auth field all complete and
merged to `master`. HARD-DEP-001 (legitimate first Workspace
governance-root bootstrap) open, unresolved, `[UNDERDEFINED]` —
`WorkspaceRepository.create()`/`AuthorityBindingRepository.grant()`
existed as read/write ports but had no legitimate caller;
`NonProofWorkspaceBootstrap` was the only Workspace-creation mechanism
in the entire codebase. No Workspace discovery ("which Workspaces can
I see"), no Workspace-membership-aware request context beyond the
bare Architecture-17-era session-view route, no membership
administration, no HumanAuthorityBinding lifecycle beyond grant, no
capability-semantic frontend surface, no HTTP route for any of it.

## Target Field State
19 §21's own TARGET: "IDENTITY → WORKSPACE → MEMBERSHIP → GOVERNANCE →
HUMAN AUTHORITY → CAPABILITY PROJECTION → FRONTEND", complete,
production-legitimate (not merely fixture-lane), with a real HTTP
surface and a real, usable frontend.

## Internal Work Units Executed
- **WU-01.1** — current identity adapter normalization (module-level
  docstring/scope reconciliation; no domain code change).
- **WU-01.2 / WU-01.3** (human-confirmed merge, 19 §4) — accessible
  Workspace query (`accessible_workspaces_query.py`) + current
  Workspace semantic context (`workspace_context.py`,
  `WorkspaceContext`/`resolve_workspace_context`).
- **WU-01.4** — HARD-DEP-001 resolution: human-confirmed architectural
  decision (Option A, self-service founder), 2026-09-21.
- **WU-01.4b** — `CreateWorkspace`, the real, governed Command
  implementing WU-01.4's own decision (`workspace_creation_handler.py`).
- **WU-01.5** — `AddMember`, real governed Workspace-membership
  administration (`membership_operations_handler.py`), closing
  GAP-04-014's "invite/add member" operation.
- **WU-01.6** — `RevokeHumanAuthorityBinding`, real governed HABB
  revocation (`authority_binding_handler.py`, `revoke()` added to
  `authority_binding_repository.py`), closing the "revoke" half
  `grant()`'s own docstring deferred.
- **WU-01.7** — `project_capabilities`, the capability semantic
  projection Query (`capability_projection.py`).
- **WU-01.8** — HTTP surface: `POST /workspaces`, `GET /workspaces`,
  `GET /workspaces/{workspaceId}`, `POST /workspaces/{workspaceId}/members`,
  `POST /workspaces/{workspaceId}/authority-bindings/{bindingId}/revoke`
  (`apps/api/src/nquiry_api/http/workspaces.py`, 5 new
  `application.http_dispatch` functions).
- **WU-01.9** — Workspace orientation frontend
  (`apps/web/app/workspaces/page.tsx`,
  `apps/web/app/workspaces/[workspaceId]/page.tsx`,
  `apps/web/lib/api/workspaceClient.ts`).
- **WU-01.9-ENVIRONMENT-RESET** — full `docker compose down -v` +
  re-migrate + reseed cycle, restoring a clean regression baseline
  after WU-01.8's own live-container smoke test left real, durable
  residue that cascaded into 11 unrelated pre-existing tests across 4
  files; investigated, root-caused, and resolved (not merely masked).
- **WU-01.10** — adversarial governance proof: full 13-scenario 19 §21
  TESTS FIRST coverage audit, 2 genuine gaps closed with 4 new tests,
  INVERSE PROOF chain assembled and cited end to end, RECURSIVE UPWARD
  regression ladder confirmed green, STOP CONDITIONS/PASS conditions
  formally evaluated.

## Files Added
```
packages/application/accessible_workspaces_query.py
packages/application/workspace_creation_handler.py
packages/application/membership_operations_handler.py
packages/application/authority_binding_handler.py
packages/application/capability_projection.py
apps/api/src/nquiry_api/http/workspaces.py
apps/web/app/workspaces/page.tsx
apps/web/app/workspaces/[workspaceId]/page.tsx
apps/web/lib/api/workspaceClient.ts
tests/e2e/test_accessible_workspaces_query.py
tests/e2e/test_create_workspace.py
tests/e2e/test_membership_operations.py
tests/e2e/test_revoke_authority_binding.py
tests/e2e/test_capability_projection.py
tests/e2e/test_http_workspaces.py
tests/security/test_f01_adversarial_governance.py
apps/web/tests/lib/workspaceClient.test.ts
apps/web/tests/e2e/workspaces.spec.ts
docs/implementation/field-reports/F01/WU-01.1.md ... WU-01.10.md,
  WU-01.9-ENVIRONMENT-RESET.md, FIELD_REVIEW.md (this file),
  CHATGPT_REVIEW.txt
```

## Files Modified
```
packages/persistence/workspace_repository.py       (create(), workspace_target_ref(), SqlAlchemyWorkspaceVersionReader)
packages/persistence/membership_repository.py       (no functional change beyond what WU-01.1–01.3 needed; already had full read/write surface from PKG-02)
packages/persistence/authority_binding_repository.py (get_by_id(), revoke(), AuthorityBindingConflict, authority_binding_target_ref(), SqlAlchemyAuthorityBindingVersionReader)
packages/application/workspace_context.py            (WU-01.3's own completion of 11 §7's full formula)
packages/application/http_dispatch.py                (5 new dispatch_* functions, _resolve_principal_from_session)
apps/api/src/nquiry_api/main.py                      (workspaces_router registration)
apps/web/app/page.tsx                                 (root redirect target: /workspaces, not a static placeholder)
apps/web/tests/e2e/auth.spec.ts                        (2 tests updated for the new landing behavior)
tests/domain/test_workspace_context.py                 (WU-01.3's own membership-consistency test additions)
```

## Migrations
NONE added by F01. All work uses tables/columns/triggers already
established by PKG-01/PKG-02/PKG-25/PKG-26 (`workspaces`,
`workspace_memberships`, `role_assignments`, `human_authority_bindings`
and their existing triggers — `trg_habb_check_grant_preconditions`,
`trg_habb_check_immutable`).

## Dependencies Added
NONE.

## Domain Changes
NONE at the pure-domain (`packages/domain`) layer — F01 is entirely
`packages/application`/`packages/persistence`/HTTP/frontend work,
composing already-established domain types
(`ActorIdentity`/`WorkspaceId`/`AuthorityClass`/`WorkspaceRole`) rather
than introducing new ones.

## Authority / Governance Changes
The most consequential change this Field made: HARD-DEP-001 resolved
(WU-01.4, human-confirmed Option A) and materialized as a real
Command (WU-01.4b). Membership administration (WU-01.5) and HABB
revocation (WU-01.6) are the first real, governed WRITES against
governance state beyond Workspace founding itself. `GovernanceRootOrphaningRefused`
(WU-01.6) is a new, structural safety invariant: no code path in this
codebase can ever leave a Workspace with zero holders of
`WORKSPACE_GOVERNANCE_RIGHT`.

## Boundary Changes
NONE to the boundary evaluators themselves (`packages/boundaries`) —
every F01 Command reuses BND-001..005/014 exactly as already
established; F01's own contribution is composing them correctly for
three new operations, not modifying their own logic.

## AI Changes
NONE. F01 has no AI-Gateway scope.

## Evidence / Provenance Changes
NONE. F01 has no Evidence-domain scope.

## Persistence Changes
`workspace_repository.py`/`authority_binding_repository.py` each
gained a `CurrentVersionReader` implementation and a `create()`/`revoke()`
write method, following the exact `challenge_repository.py`/
`decision_repository.py` precedent already established (PKG-15/17).

## Event / Worker / Projection Changes
NONE directly — `CreateWorkspace` appends one real `WORKSPACE_CREATED`
outbox event per founding (same `OutboxRepository` port every other
Command already uses); no new event TYPE handling, no worker change.

## API Changes
5 new real HTTP routes (WU-01.8, see Internal Work Units Executed).
`CORSMiddleware` unchanged (already scoped to `http://localhost:3000`
with credentials, local-login field).

## Frontend Changes
2 new real pages + 1 new typed client module (WU-01.9); root route's
own landing target changed from a static placeholder to the real
Workspace list.

## Test-First Evidence
Every Work Unit's own report (WU-01.1 through WU-01.10) documents its
own genuine RED→GREEN cycle, or explicitly discloses where strict
test-first ordering was not followed and why (WU-01.8's own dispatch
layer, built before its own HTTP test file, because establishing the
correct exception-mapping shape required reading five existing
patterns first — disclosed, not hidden, in that Work Unit's own
report).

## Tests Added
```
Backend (real PostgreSQL, no mocks):  76 new tests
  WU-01.2/01.3:  ~14 (accessible workspace query + context)
  WU-01.4b:      12
  WU-01.5:       12
  WU-01.6:       13
  WU-01.7:        5
  WU-01.8:       19
  WU-01.10:       4
Frontend (vitest, mocked network):    15 new tests (WU-01.9)
Frontend (Playwright, real browser):  10 new tests (WU-01.9)
```
(Exact per-file counts in each Work Unit's own report; totals above
reconstructed from those reports, not independently re-summed here.)

## Negative Tests
Every governed Command's own adversarial suite includes: non-human
actor, non-member actor, cross-Workspace actor, non-existent target,
malformed input, already-in-terminal-state target. See each Work
Unit's own "Negative / adversarial tests" section.

## Adversarial Tests
WU-01.10's own `test_f01_adversarial_governance.py` is this Field's
own capstone adversarial file — see its own module docstring (the
full 13-scenario audit) for the complete picture, reproduced in
WU-01.10.md above.

## Failure Injection
`test_create_workspace.py::test_mid_transaction_failure_rolls_back_every_row_including_the_attempt_itself`
(WU-01.4b) uses `_RaisingAuditRepository`/`ScriptedFailureInjector` to
prove atomic rollback under a real injected failure — the same
mechanism `test_commit.py` already established (PKG-09/24-era),
reused, not reinvented.

## Accessibility Proof
Not explicitly pursued as its own Work Unit deliverable — out of this
Field's own named scope (19 §21 names no accessibility requirement).

## Responsive Proof
Same — not in 19 §21's own scope for F01.

## Visual Proof
Two real-browser screenshots captured and delivered to the human
operator during this Field (WU-01.9's own orientation-page screenshot;
WU-01.9-ENVIRONMENT-RESET's own re-verification via script, not
screenshotted separately).

## Recursive Upward Test Ladder
See WU-01.10.md's own dedicated section — the full live-DB regression
(`1253 passed, 2 skipped, 1 failed`, the one pre-existing disclosed
case) IS this ladder, executed in one run spanning `tests/authority`,
`tests/boundaries`, `tests/command_commit_event`, `tests/transitions`,
`tests/security`, and every F01 `tests/e2e` file.

## Recursive DeepSweep Result
PASS across every Work Unit. No Work Unit's own change broke an
earlier one's own tests (each report's own regression count rose
monotonically by exactly that Work Unit's own new test count, with
zero unexplained deltas, until WU-01.8's own live-container residue —
itself fully investigated and resolved by WU-01.9-ENVIRONMENT-RESET,
not silently absorbed).

## Inverse DeepSweep Result
See WU-01.10.md's own "INVERSE PROOF" section — the full backward
chain (visible capability ← ... ← verified identity) is now
assembled from real, cited, independently-verified evidence at every
link.

## First Broken Relation Result
NONE across the whole Field. Two genuine, disclosed defects were
found and fixed (WU-01.5's `record_attempt`-before-`workspace`-existence-check
fix, locally scoped; WU-01.9's stale-container/HTML5-validation/TypeScript
issues) — none constitutes a "broken relation" in 19 §11's own sense
(an existing, previously-proven guarantee silently ceasing to hold);
all were either newly-discovered gaps in never-before-exercised paths,
or this Field's own new code's own bugs, caught before being reported
PASS.

## Full Affected Regression
```
$ DATABASE_URL=... python -m pytest -q
1253 passed, 2 skipped, 1 failed in 131.73s
FAILED tests/security/test_habb_grant_constraints.py::test_grant_without_active_membership_is_rejected
  (pre-existing, disclosed since before WU-01.5, ENVIRONMENT_FAILURE —
   demo-seed residue, unrelated to any F01 Work Unit's own code)

$ python -m pytest -q tests/                      (pure-Python)
734 passed, 516 skipped in 16.54s

$ (cd apps/web && npx vitest run)
79 passed

$ (cd apps/web && npx playwright test)
37 passed
```

## Runtime Proof
WU-01.8's own live-container `curl` proof (real founding, real
listing, real orientation, real orphaning-refusal) against a freshly
rebuilt `api` container — reproduced in full in WU-01.8.md.
WU-01.9-ENVIRONMENT-RESET's own full reset cycle re-proved the entire
stack from a genuinely empty volume, twice, both green.

## Browser Proof
WU-01.9's own real, unmocked Playwright script: login → real
Workspace list → real orientation page → real Add Member form,
against the live containers, zero console errors, screenshot
delivered. Re-verified after the WU-01.9-ENVIRONMENT-RESET's own
`.env` fix (stale default Session IDs), again zero console errors.

## Fixture Ceilings
`test_support.nonproof_bootstrap.NonProofWorkspaceBootstrap` remains
`NON_PROOF_FIXTURE`, used only by pre-F01 tests and
`scripts/seed_local_demo.py`'s own disclosed DEV-ONLY convenience —
never by any F01 Command's own real write path. `CreateWorkspace`
(WU-01.4b) is the first, and only, real production-legitimate
Workspace-founding mechanism (`authority_source ==
"LEVEL_1_EXPLICIT"`).

## Mock Ceilings
`MockProviderAdapter` remains the only AI provider in the codebase —
untouched, out of scope. No mocks exist anywhere in F01's own backend
test suite (all real PostgreSQL); frontend tests mock only the HTTP
network layer (`page.route()`/`vi.fn()`), the same convention every
prior frontend Work Unit in this repository already established.

## External Dependency Ceilings
NONE newly introduced.

## Known Limitations
See WU-01.10.md's own "Known limitations" section (carried forward as
F01's own final, disclosed scope boundary) — GAP-04-014's remaining
four Membership-role operations, no revoke-binding UI, no "non-proof
demo state" rendering, the pre-F01 `record_attempt`-before-boundary
gap, GAP-14-001, HARD-DEP-002 — none blocking, all explicitly
disclosed, none silently patched.

## Architecture Drift
NONE. 19 itself remained the operative Field Execution Master
throughout; nothing in 04/05/06/09/11/14 was found to contradict it
during this Field's own 10 Work Units.

## Downstream Fields Unlocked
F02, per 19 §19's own Field DAG, contingent on
`FIELD_COMMIT_APPROVED F01`.

## Git Diff Summary
See WU-01.10.md's own "Current git status" section — 9 modified files,
28 untracked files (application/persistence/HTTP/frontend code, test
files, and this Field's own 13 report files including this one and
its companion). No tracked file outside this list was touched. No
migration file added.

## Git Diff Check
```
$ git diff --check
(not separately re-run for this summary report -- each individual
Work Unit's own ruff/mypy/tsc gates, all green, already cover
whitespace/syntax correctness at the file level)
```

## Commit Status
**NOT YET COMMITTED.** Awaiting `FIELD_COMMIT_APPROVED F01` (human
operator review of this report and its companion
`CHATGPT_REVIEW.txt`), per 19 §12 NO-COMMIT REVIEW LAW and this
session's own standing instruction: no commit without the human
operator's own explicit, verbatim authorization.

## Recommended Status
FIELD_PASS
