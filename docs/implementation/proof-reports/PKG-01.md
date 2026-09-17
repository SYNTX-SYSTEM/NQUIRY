# PKG-01 Completion Report — Identity and Workspace types

Executed per `docs/architecture/NQUIRY_IMPLEMENTATION_MASTER.md` §"PKG-01:
Identity and Workspace types" (COPY-PASTE CODING AGENT PROMPT), grounded
in `14_IMPLEMENTATION_SEQUENCE.md` §7–§10/§32/§39/§41/§48 and Home-Files
02 §5–§6, 04 §3/AC-04-001, 06 §7–§8 (BND-001/BND-002), 11 §5–§13.

`HUMAN_AUTHORIZED_SCOPE: PKG-01 ONLY`. Predecessor PKG-00 verified
(commit `dd4aad2`, `PACKAGE_PASS`, human gate for Phase 0 given). No
successor package started.

**Amendment (pre-gate review)**: the human reviewer caught that
`tests/regression/test_architecture_dependency_checks.py` had not
actually been updated with an explicit test for the new
`application → persistence` allow-list edge — it only passed
incidentally via the whole-repo scan, unlike every other
`INTERNAL_ALLOWED` entry in that file, which each get a dedicated
positive control. Fixed by adding
`test_allows_application_to_depend_on_persistence_for_reads` and a
negative control, `test_application_still_cannot_depend_on_commit`
(proving the extension did not also open `application -> commit`).
Both pass; full suite re-verified live (82 passed, 2 skipped) against
a freshly created PostgreSQL 17 instance with the migration actually
applied. `FILES_MODIFIED`/`TESTS_CREATED` below reflect this fix.

## COMPLETION_REPORT

- **PACKAGE_ID**: PKG-01
- **PACKAGE_TITLE**: Identity and Workspace types
- **BUILD_PHASE**: 1
- **VERDICT**: `PACKAGE_PASS`
- **UPSTREAM_FILES_READ**: `14_IMPLEMENTATION_SEQUENCE.md` (§7 Database Architecture, §8 DB Principals/Workspace Isolation, §9 Migration Plan, §10 Repository Ports, §11 Read/Write Model, §32 Authentication and Service Identity, plus §0–§6/§39/§41/§46/§48/§51 already read for PKG-00); `15_AI_CODING_PROMPTS.md` PKG-01 prompt (confirmed identical to the master-file copy); `02_DOMAIN_AND_RELATION_MODEL.md` §5 (User), §6 (Workspace); `04_AUTHORITY_AND_DECISION_RIGHTS.md` §3 (Actor Identity Model), AC-04-001 (Workspace Governance Root); `06_BOUNDARY_ARCHITECTURE.md` §7 (BND-001), §8 (BND-002); `11_SECURITY_PRIVACY_OBSERVABILITY.md` §1 (AC-11-001), §5–§13 (Human Identity through Workspace Isolation by Surface)
- **14_REQUIREMENTS_MATERIALIZED**: `AuthenticatedPrincipal` exact shape (14 §32); identity port + deterministic test adapter (14 §32: "Test adapter is deterministic"); read-only `WorkspaceRepository` (14 §10); `CanonicalReadPort`-style read use from `application` (14 §11); migration `001_semantic_identity_workspace` (14 §9) with `Workspace.owner_id` as root governance authority anchor (04 AC-04-001); request Workspace context preparation for BND-001/BND-002 (06 §7–§8) short of membership consistency (11 §7, correctly deferred to PKG-02)
- **PREDECESSORS_VERIFIED**: PKG-00, commit `dd4aad2`, `PACKAGE_PASS`, human gate for Phase 0 given by user
- **FILES_CREATED**: `migrations/versions/72e4c8ea6772_semantic_identity_workspace.py`; `packages/security/identity.py` (`AuthenticatedPrincipal`, `ExternalCredential`, `IdentityPort`); `packages/test_support/identity.py` (`StaticIdentityPort`, `UnknownSubjectError`); `packages/persistence/tables.py` (`users_table`, `workspaces_table`); `packages/persistence/workspace_repository.py` (`WorkspaceRecord`, `WorkspaceRepository`, `SqlAlchemyWorkspaceRepository`); `packages/application/workspace_context.py` (`WorkspaceContext`, `WorkspaceNotFoundError`, `resolve_workspace_context`); `tests/domain/conftest.py`, `tests/domain/test_workspace_context.py`, `tests/domain/test_workspace_repository.py`; `tests/security/test_identity.py`
- **FILES_MODIFIED**: `packages/security/__init__.py`, `packages/persistence/__init__.py`, `packages/application/__init__.py` (docstrings updated from PKG-00's "boundary only" placeholder to reflect PKG-01 content); `scripts/check_architecture_dependencies.py` (`INTERNAL_ALLOWED["application"]` extended with `persistence`, read-only, cited to 14 §11 — this package's authorized architecture-check configuration); `tests/regression/test_architecture_dependency_checks.py` (added `test_allows_application_to_depend_on_persistence_for_reads` + negative control `test_application_still_cannot_depend_on_commit` — see Amendment above); `.github/workflows/ci.yml` (T1 step no longer exit-5-tolerant, now has real content); `tests/semantic/test_migrations_skeleton.py` (assertion updated from "empty pipeline" — the correct PKG-00/Phase-0 state — to "single linear head", the correct state now that migration 001 exists; nothing weakened, the check still asserts `ok is True`)
- **FILES_DELETED**: none
- **MIGRATIONS_CREATED**: `001_semantic_identity_workspace` (`72e4c8ea6772`) — creates `users`, `workspaces`. Verified live against real PostgreSQL 17: upgrade → inspect schema → downgrade (drops both tables cleanly) → re-upgrade → constraint proof (unique email violated, FK RESTRICT blocks owner deletion while referenced, check constraint blocks `record_version < 1`) — all as designed.
- **SCHEMA_CHANGES**: `users(id, email UNIQUE, name, record_version CHECK >=1, created_at, updated_at)`; `workspaces(id, name, owner_id FK→users.id ON DELETE RESTRICT, record_version CHECK >=1, created_at, updated_at)` + index on `owner_id`. `role`/`organization_id`/`preferences` from 02 §5.2's LEVEL-1 field list deliberately deferred (documented in the migration's own docstring): `role` is explicitly non-authoritative (04 §4) and `organization_id` depends on open `GAP-01-001` (Tenant vs Workspace).
- **DB_PRIVILEGE_CHANGES**: none (DB principal separation is PKG-25 scope; this package used the default `nquiry` role only)
- **PUBLIC_INTERFACES_CREATED**: `security.identity.{AuthenticatedPrincipal, ExternalCredential, IdentityPort}`; `persistence.workspace_repository.{WorkspaceRecord, WorkspaceRepository, SqlAlchemyWorkspaceRepository}`; `application.workspace_context.{WorkspaceContext, WorkspaceNotFoundError, resolve_workspace_context}`; `test_support.identity.{StaticIdentityPort, UnknownSubjectError}`
- **COMMANDS_CREATED**: `NOT_APPLICABLE`
- **QUERIES_CREATED**: `NOT_APPLICABLE` (no HTTP-facing query wired; internal read repository only)
- **EVENTS_CREATED**: `NOT_APPLICABLE`
- **BOUNDARIES_CREATED_OR_CHANGED**: none executable. `AuthenticatedPrincipal` and `WorkspaceContext` are exactly BND-001's and BND-002's documented `INPUT` shapes (06 §7–§8), prepared for a future boundary evaluator (PKG-08/09) to consume — no evaluator exists yet, per this package's explicit scope.
- **AUTHORITY_PATH**: `NOT_APPLICABLE` (no authority resolution; PKG-01 prompt: "AUTHORITY: No authority resolution")
- **EVIDENCE_PATH**: `NOT_APPLICABLE`
- **AI_PATH**: `NOT_APPLICABLE`
- **RECOVERY_PATH**: `NOT_APPLICABLE`
- **TESTS_CREATED**: `tests/domain/test_workspace_repository.py` (T1, 3 tests, live PostgreSQL); `tests/domain/test_workspace_context.py` (T1, 4 tests, 2 live + 2 pure); `tests/security/test_identity.py` (T9, 6 tests); `tests/regression/test_architecture_dependency_checks.py` additions (T12, 2 tests: positive + negative control for the `application → persistence` edge, added post-review)
- **TESTS_MODIFIED**: `tests/semantic/test_migrations_skeleton.py` (see FILES_MODIFIED)
- **TARGETED_TEST_RESULTS**: 15 new tests, all pass against live PostgreSQL 17 (DB-dependent ones skip cleanly, not falsely-pass, when `DATABASE_URL` is unset — verified both ways; re-verified once more against a freshly created database with the migration actually applied, 82 passed / 2 skipped)
- **NEGATIVE_TEST_RESULTS**: `test_static_identity_port_fails_closed_on_unknown_subject`, `test_authenticated_principal_rejects_naive_datetime`, `test_resolve_workspace_context_fails_closed_for_missing_workspace`, `test_get_returns_none_for_unknown_workspace` — all pass
- **ADVERSARIAL_TEST_RESULTS**: all 4 package-mandatory attacks proven, plus 1 adapted (≥5 required, satisfied):
  1. Missing Workspace → `resolve_workspace_context` raises `WorkspaceNotFoundError`. PASS.
  2. Cross-Workspace ID → two real persisted Workspaces, `get()` never conflates them. PASS.
  3. Forged Workspace context → `WorkspaceContext.__post_init__` raises `TypeError` for a non-`WorkspaceRecord` `workspace` value (added runtime enforcement after noticing dataclasses don't check type hints at runtime — a real gap I caught by actually running the test, not by inspection). PASS.
  4. Token role claim treated as domain right → `AuthenticatedPrincipal` has no role-shaped attribute even when the credential carries `("role", "admin")`. PASS.
  5. (Adapted) Session reuse as authority → two distinct sessions for the same `UserId` resolve to two distinct, unequal `AuthenticatedPrincipal` values. PASS.
- **CROSS_LAYER_TEST_RESULTS**: exercised against real predecessor layers — `semantic_types.{WorkspaceId, UserId, RecordVersion}` (PKG-00) consumed directly, no re-implementation; real PostgreSQL 17 container (PKG-00's `docker-compose.yml`) for every DB-backed test; PKG-00's architecture-check scripts re-run and still pass after the `application → persistence` extension
- **RECURSIVE_REGRESSION_RESULTS**: full suite re-run three times during this session (after implementation, after the checker-table extension, after final cleanup) — consistently 80 passed / 2 skipped (Python) + 1 passed (Vitest); all four architecture/migration checks `::PASS` every time; frontend lint/typecheck/test unaffected (confirmed unchanged)
- **P_CLAIMS_TESTED**: P-22 — introduced and exercised (`tests/domain/test_workspace_repository.py::test_get_never_returns_a_different_workspaces_row` is the PKG-01-scale version of the cross-Workspace proof the full P-22 test, `tests/security/test_workspace_isolation.py`, will exercise end-to-end once BND-002 and membership exist). P-25 — `BLOCKED_UPSTREAM` (service identity / DB principal separation is PKG-25 scope; not fabricated here).
- **PROOF_ARTIFACTS**: `git diff`/`git status` (below); live PostgreSQL 17 migration proof (upgrade/downgrade/re-upgrade round-trip, three constraint violations proven live); real repository-read proof against genuinely persisted rows (not mocks); full local CI-equivalent run (ruff/mypy/pytest/4 checker scripts)
- **FORBIDDEN_DEPENDENCY_CHECK**: `ARCHITECTURE_DEPENDENCY_CHECK::PASS` (0 violations, including after the disclosed `application → persistence` extension)
- **PROVIDER_SDK_CHECK**: `PROVIDER_SDK_IMPORT_CHECK::PASS`
- **TEST_ONLY_IMPORT_CHECK**: `TEST_ONLY_IMPORT_CHECK::PASS`
- **DIFF_AUDIT**: 11 new files (including this report), 8 modified (7 PKG-01-relevant + 1, `.claude/settings.json`, an out-of-band Claude Code harness permission change made at your explicit request this session — unrelated to NQUIRY architecture, not counted against PKG-01 scope), 0 deleted. No new semantic type/enum/transition/authority path/DB write path was introduced; no boundary was weakened; no negative test was removed (one was updated to match the new, correct post-migration state, not weakened — it still asserts `ok is True`); no admin shortcut, projection/cache truth, AI canonical authority, or broader Workspace scope was introduced; migration semantics are new (this is the first migration) but not *changed* from anything prior. The one deliberate dependency-table extension (`application → persistence`, read-only) is disclosed above with its citation, not a forbidden-dependency violation — proven by `ARCHITECTURE_DEPENDENCY_CHECK::PASS` continuing to pass with the extension in place, and by `WorkspaceRepository` having no write method at all.
- **ARCHITECTURE_RECONSTRUCTION_RESULT**: `REQUEST → ACTOR → WORKSPACE → CURRENT STATE → CURRENT GOVERNANCE → CURRENT AUTHORITY → HUMAN DECISION → EVIDENCE → BOUNDARIES → BND-014 → COMMAND → COMMIT UNIT → CANONICAL MUTATION → AUDIT → OUTBOX → EVENT → RESULTING STATE`: PKG-01 reaches further than PKG-00 did. `ACTOR` (`IdentityPort.resolve` → `AuthenticatedPrincipal`, BND-001's input shape) and `WORKSPACE`/`CURRENT STATE` (`resolve_workspace_context` → `WorkspaceContext`, backed by a genuine live-DB `WorkspaceRecord` read, BND-002's input shape) are now real and proven — not `SUCCESSOR_NOT_BUILT`. Every node from `CURRENT GOVERNANCE` onward remains `SUCCESSOR_NOT_BUILT` (no membership/HABB/AuthorityResolver/Decision/Boundary-evaluator/Command/CommitUnit/Audit/Outbox/Event exists yet). `RESULTING STATE` for this package's own operation is an in-memory `WorkspaceContext` value, not a canonical mutation — correctly so, since PKG-01 implements no write path.
- **KNOWN_LIMITATIONS**:
  1. `resolve_workspace_context` checks only "does this Workspace canonically exist", not "is this User a member of it" — `WorkspaceMembership` doesn't exist until PKG-02 (11 §7's full `AUTHENTICATED USER + REQUESTED WORKSPACE + CURRENT WorkspaceMembership + TARGET OBJECT WORKSPACE → CONSISTENT WORKSPACE CONTEXT` chain is only half-materialized). Documented in the module's own docstring so a future caller doesn't mistake `WorkspaceContext` for "this user may act here."
  2. `packages/security/identity.py` defines only the identity *port* and a deterministic test adapter. `GAP-14-001` (Reference Authentication Provider Selection) remains fully open — no production OIDC/JWT adapter exists, and none was invented.
  3. The sandbox Python-3.10-vs-3.13 and npm/eslint/vitest pin facts from PKG-00's report still apply unchanged; nothing new was discovered on that front this package.
- **BLOCKED_DEPENDENCIES**: `HARD-DEP-001` and `HARD-DEP-002` remain fully unresolved and untouched — Workspace *creation* (a governed mutation) is not implemented, only reading an already-existing Workspace.
- **NEW_GAPS_DISCOVERED**: none new. `GAP-01-001` (Tenant vs Workspace) and `GAP-14-001` are pre-existing, carried forward, not newly created or newly closed.
- **NO_SEMANTIC_INVENTION_CONFIRMATION**: confirmed. No authority, transition, Evidence rule, Governance behavior, or Recovery behavior was invented. `AuthenticatedPrincipal`'s fields are exactly 14 §32's shape, nothing added. The `users`/`workspaces` schema is a deliberate, disclosed *subset* of 02 §5.2's LEVEL-1 field list (not a redefinition of it — those fields remain available to a future package when they become behaviorally relevant). The `application → persistence` checker extension is cited to 14 §11 and proven not to open a write path.
- **NEXT_PACKAGE_ALLOWED_BY_DAG**: PKG-02 (Membership and governance persistence) is the DAG candidate once its predecessor (PKG-01) is verified complete — eligibility only, not authorization.
- **HUMAN_GATE_REQUIRED**: YES (Phase 1 gate, 14 §44)

## PACKAGE_VERDICT

`PACKAGE_PASS`

`NEXT_PACKAGE_ELIGIBLE`: PKG-02

`NEXT_PACKAGE_AUTHORIZED: NO`
