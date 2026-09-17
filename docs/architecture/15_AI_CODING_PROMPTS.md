# 15_AI_CODING_PROMPTS.md

## Document status

`STATUS::READY_FOR_HUMAN_REVIEW`

`DOCUMENT_ROLE::EXECUTION_LAYER`

`APPLICATION_CODE_WRITTEN::NO`

`16_BUILT::NO`

`ARCHITECTURE_BASELINE_FROZEN::NO`

## 0. Authority and execution law

This document operationalizes `14_IMPLEMENTATION_SEQUENCE.md` into copyable coding-agent execution prompts. It does not rewrite 00 through 14 and does not authorize implementation by itself.

`ARCHITECTURE DEFINES WHAT MAY EXIST.`

`14 DEFINES HOW IT IS MATERIALIZED.`

`15 DEFINES HOW THE CODING AGENT MAY BUILD IT.`

`THE CODING AGENT DOES NOT DEFINE ARCHITECTURE.`

Preserve:

`CODE != AUTHORITY`

`TEST != AUTHORITY`

`TEST PASS != ARCHITECTURAL TRUTH`

`IMPLEMENTATION CONVENIENCE != SEMANTIC PERMISSION`

`FRAMEWORK DEFAULT != ARCHITECTURAL DECISION`

`DATABASE CAPABILITY != DOMAIN AUTHORITY`

`ADMIN ACCESS != DOMAIN AUTHORITY`

`AI OUTPUT != HUMAN DECISION`

`AI RECOMMENDATION != AUTHORITY`

`EVENT != COMMAND`

`PROJECTION != CANONICAL STATE`

`CACHE != CANONICAL STATE`

`RETRY != AUTHORIZATION`

`RECOVERY != AUTHORITY`

`LOG != AUDIT`

`MOCK != PRODUCTION ELIGIBILITY`

`TEST FIXTURE != LEGITIMATE BOOTSTRAP`

`GREEN CI != CLOSED UPSTREAM GAP`

Hard dependencies remain explicit:

`HARD-DEP-001`: legitimate first Workspace governance-root bootstrap.

`HARD-DEP-002`: provider/privacy eligibility for the exact prototype data class and selected provider path.

Carried implementation gaps remain explicit:

`GAP-14-001`: Reference Authentication Provider Selection.

`GAP-14-002`: Production Egress Enforcement Mechanism.

`GAP-14-003`: Audit Tamper-Evidence Strength.

`GAP-14-004`: Recovery Algorithm Approval Governance.

`GAP-14-005`: Production Retention/Deletion Materialization.

Reference stack is fixed by 14 for these prompts: Python 3.13, FastAPI, Python dataclasses, Pydantic v2, PostgreSQL 17, Alembic, SQLAlchemy 2.x Core with explicit repositories, pluggable OIDC adapter, Next.js 16, TypeScript, pytest, Hypothesis where useful, Vitest, Playwright, internal AI Gateway, MockProviderAdapter, OpenTelemetry API with local structured sink, Docker Compose and GitHub Actions.

Global repository topology is fixed: `apps/api`, `apps/web`, `apps/worker`, `packages/semantic_types`, `packages/domain`, `packages/governance`, `packages/authority`, `packages/boundaries`, `packages/evidence`, `packages/ai_contracts`, `packages/ai_gateway`, `packages/command`, `packages/commit`, `packages/audit`, `packages/events`, `packages/projection`, `packages/recovery`, `packages/security`, `packages/observability`, `packages/application`, `packages/persistence`, `packages/test_support`, `migrations`, `tests`, `scripts`, `config`, `infra`.

Global forbidden import law is inherited from 14. In particular: domain cannot depend on FastAPI, SQLAlchemy, PostgreSQL drivers or provider SDKs; authority cannot depend on UI role claims, projection truth or AI authority; AI Gateway cannot import canonical writer or HABB mutation; provider adapters cannot import CommandProcessor, CommitWriter or Decision write; projection cannot import canonical/governance mutation; event consumers cannot directly create consequential state; recovery cannot import unrestricted DB mutation or historical authority reuse; controllers cannot import ORM mutation, provider SDK or CommitUnit internals; frontend cannot import DB/governance/AuthorityResolver; test_support cannot enter production import graph.

## 1. Global coding-agent protocol

Every package uses this order:

`ORIENT -> TRACE -> PLAN -> PRE-IMPLEMENTATION FALSIFICATION -> IMPLEMENT -> STATIC VERIFY -> TARGETED TEST -> NEGATIVE TEST -> ADVERSARIAL TEST -> CROSS-LAYER TEST -> RECURSIVE REGRESSION -> DIFF AUDIT -> ARCHITECTURE RECONSTRUCTION CHECK -> PACKAGE VERDICT -> STOP OR RETURN`

Test oracle priority:

1. canonical authoritative state
2. governance authoritative state
3. CommitUnit
4. BoundaryProof
5. AuditEvent
6. durable Event/Outbox
7. Evidence/provenance
8. SecurityEvent
9. RecoveryRecord
10. projection only where projection is itself the target

Logs, UI and mock call counts are never primary proof.

No package self-authorizes a successor phase. Every phase 0 through 14 ends with `HUMAN_GATE_REQUIRED::YES`.

## 2. Repository precheck prompt

```text
PROMPT_REPOSITORY_PRECHECK
EXECUTION_MODE: VERIFY
MODIFICATION_AUTHORITY: NONE

Inspect repository reality without editing anything.

1. Locate architecture files 00 through 15.
2. Read 14 implementation package manifest, DAG, file map, DB map, API map, test map and stop conditions.
3. Inspect git status, git diff, untracked files and current branch.
4. Identify uncommitted human changes and do not alter them.
5. Identify existing Python, Node, PostgreSQL, FastAPI, Next.js, Alembic, SQLAlchemy, pytest, Vitest, Playwright, Docker Compose and CI configuration.
6. Determine whether implementation partially exists.
7. Compare repository reality with the fixed 14 reference stack. A material conflict is PRECHECK_CONFLICT, not an invitation to substitute technology.
8. Identify current migration head if migrations exist.
9. Inspect architecture dependency checks if present.
10. Verify no secrets are exposed in tracked files, logs or fixtures during inspection.
11. Do not reset, clean, install destructively, migrate, drop databases, edit or generate files.

Return:
ARCHITECTURE_FILES_FOUND
GIT_STATE
UNCOMMITTED_HUMAN_CHANGES
EXISTING_IMPLEMENTATION
EXISTING_STACK
REFERENCE_STACK_CONFLICTS
MIGRATION_STATE
DEPENDENCY_CHECK_STATE
POTENTIAL_ARCHITECTURE_CONFLICTS
SAFE_TO_START_PKG_00

Verdict exactly one:
PRECHECK_PASS
PRECHECK_BLOCKED
PRECHECK_CONFLICT

STOP.
```

## 3. Package execution prompts


### PKG-00: Repository and architecture skeleton


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-00
BUILD_PHASE: 0
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-00 ONLY

AUTHORIZATION
You are authorized to implement only PKG-00, "Repository and architecture skeleton". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Create toolchain, package boundaries, dependency enforcement, local DB and CI skeleton
Package materialization task:
Create the Python and Node toolchain, repository package topology, pyproject configuration, Next.js package setup, Docker Compose PostgreSQL 17 local environment, test directory topology T0 through T12, architecture dependency scripts, provider SDK import checker, test-only import checker, Alembic validation skeleton, GitHub Actions skeleton, semantic_types base package, Clock port, ID generator port. Do not implement domain, authority, repository behavior, or fake persistence.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 00-14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-00; Build Phase 0; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
none

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
CODE != AUTHORITY; repository structure must enforce dependency direction before behavior exists.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-00. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
Root toolchain files; apps/api skeleton; apps/web skeleton; apps/worker skeleton; packages/semantic_types; scripts/architecture_checks; tests/semantic and tests/regression skeleton; infra/docker-compose; CI workflow.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-00, predecessor extension points explicitly exposed for PKG-00, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: semantic_types and architecture checks.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
No domain tables. Local PostgreSQL container and empty Alembic pipeline only.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
None executable.

AUTHORITY
None executable.

EVIDENCE
None.

AI
Only import-boundary scaffolding. No provider execution.

FAILURE_RECOVERY
Toolchain and architecture-check failure only.

SECURITY
Test-support production-import prohibition and provider SDK import restriction.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Controlled forbidden import fixture; provider SDK import outside packages/ai_gateway approved adapter boundary; production import of packages/test_support. Architecture checks must reject each controlled violation.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T0/T12.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-18,P-23,P-24.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-01: Identity and Workspace types


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-01
BUILD_PHASE: 1
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-01 ONLY

AUTHORIZATION
You are authorized to implement only PKG-01, "Identity and Workspace types". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Materialize User identity mapping, Workspace identity and request Workspace context
Package materialization task:
Materialize UserId, WorkspaceId, authenticated principal mapping, request Workspace context, identity ports, WorkspaceRepository read contract, and migration 001 subset exactly as mapped by 14. Token claims may resolve identity only.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 01,02,04,11,12,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-01; Build Phase 1; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-00

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
IDENTITY != AUTHORITY; AUTH TOKEN != AUTHORITY; WORKSPACE CONTEXT != AUTHORITY.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-01. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/semantic_types identity/workspace IDs; packages/security identity port; packages/application Workspace context; packages/persistence Workspace read repository; migration 001 subset; T0/T1/T9 tests.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-01, predecessor extension points explicitly exposed for PKG-01, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: identity ports, WorkspaceRepository read contracts.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 001.
Users and Workspaces subset from 14 migration map, with Workspace identity constraints.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Prepare inputs for BND-001 and BND-002, do not implement later boundary behavior.

AUTHORITY
No authority resolution.

EVIDENCE
None.

AI
None.

FAILURE_RECOVERY
Unknown or conflicting Workspace fails closed for consequential preparation.

SECURITY
Authenticated principal mapping and Workspace scoping only.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Forged Workspace context; missing Workspace; cross-Workspace ID; token role claim treated as domain right.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T0,T1,T9.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-22,P-25.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-02: Membership and governance persistence


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-02
BUILD_PHASE: 1
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-02 ONLY

AUTHORIZATION
You are authorized to implement only PKG-02, "Membership and governance persistence". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Membership, HABB, governance history and governed mutation ports
Package materialization task:
Implement WorkspaceMembership, HumanAuthorityBinding, FacilitatorScopeBinding where 14 requires it, governance history/versioning, revocation representation, typed MembershipRepository and AuthorityBindingRepository, migration 002. No generic ACL, wildcard authority, role fallback, or Owner superuser.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 02,04,05,09,11,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-02; Build Phase 1; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-01

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
MEMBERSHIP != AUTHORITY; ROLE != AUTHORITY; OWNERSHIP != UNIVERSAL AUTHORITY; REVOCATION MUST BE REPRESENTABLE.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-02. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/governance; packages/persistence governance repositories; migration 002; tests/authority and tests/security fixtures.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-02, predecessor extension points explicitly exposed for PKG-02, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: MembershipRepository, AuthorityBindingRepository.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 002.
workspace_memberships, human_authority_bindings, facilitator_scope_bindings if mapped, history/version fields and constraints from 14.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
No boundary engine yet.

AUTHORITY
Persist authority facts only, do not resolve them.

EVIDENCE
None.

AI
AI actor must not receive human rights.

FAILURE_RECOVERY
Invalid governance references fail before persistence.

SECURITY
Workspace-composite integrity and actor-class constraints where expressible.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Revoked HABB; absent membership; wrong Workspace binding; AI actor binding; SYSTEM_SERVICE given human right; Owner assumed superuser.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T3.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-10,P-11,P-12.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-03: AuthorityResolver


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-03
BUILD_PHASE: 1
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-03 ONLY

AUTHORIZATION
You are authorized to implement only PKG-03, "AuthorityResolver". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Current operation-specific authority resolution with proof refs
Package materialization task:
Implement AuthorityResolver with actor, Workspace, operation, target, authority class, current membership, current HABB, scope and governance state as inputs. Return GRANTED, DENIED, or approved unresolved representation with proof refs. Consequential unresolved fails closed. Never trust request body, JWT role, UI, cache, AI, authorship, DB admin or service identity.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 04,05,06,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-03; Build Phase 1; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-02

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
AUTHENTICATION != AUTHORITY; MEMBERSHIP != AUTHORITY; ROLE != AUTHORITY; AI != AUTHORITY-BEARING HUMAN ACTOR; CURRENT AUTHORITY MUST BE OPERATION-SPECIFIC AND SCOPE-SPECIFIC.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-03. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/authority; governance read ports as needed; tests/authority; architecture dependency tests.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-03, predecessor extension points explicitly exposed for PKG-03, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: AuthorityResolver.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
No new schema.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Produces proof inputs later consumed by BND-005/BND-006.

AUTHORITY
Core package responsibility.

EVIDENCE
None.

AI
AI cannot resolve to human authority.

FAILURE_RECOVERY
Unknown current authority on consequential path is DENIED/fail closed according to upstream semantics.

SECURITY
Technical identity cannot become domain authority. HUMAN_GATE_REQUIRED after package.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Role-only; Owner-only; author-only; AI; service; revoked binding; wrong scope; wrong Workspace; stale binding; missing membership. Add at least three novel attacks.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T3,T4.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-10,P-11,P-24.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-04: NonProof bootstrap adapter


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-04
BUILD_PHASE: 1
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-04 ONLY

AUTHORIZATION
You are authorized to implement only PKG-04, "NonProof bootstrap adapter". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Test/dev-only fixture bootstrap without legitimacy claim
Package materialization task:
Create only NonProofWorkspaceBootstrap in test/dev support. Every produced root fixture must carry NON_PROOF_FIXTURE semantics. Production import graph must reject it. Do not claim legitimate first Workspace governance-root bootstrap.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-04; Build Phase 1; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-02

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
TEST FIXTURE != LEGITIMATE BOOTSTRAP; NON_PROOF_FIXTURE CANNOT SATISFY HARD-DEP-001.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-04. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/test_support only plus architecture checks and fixture tests.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-04, predecessor extension points explicitly exposed for PKG-04, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: NonProofWorkspaceBootstrap.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: test only.
Test/dev fixture operations only, no production migration.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
None.

AUTHORITY
Fixture may seed facts for tests but proves no bootstrap legitimacy.

EVIDENCE
None.

AI
None.

FAILURE_RECOVERY
Production availability is package failure.

SECURITY
Build/import guard required.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Production import; fixture used to claim bootstrap legitimacy; fixture authority escaping test environment.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: fixture validation.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: downstream only.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-05: Challenge and Session domain


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-05
BUILD_PHASE: 2
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-05 ONLY

AUTHORIZATION
You are authorized to implement only PKG-05, "Challenge and Session domain". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Canonical Challenge/Session types and transition registry base
Package materialization task:
Implement Challenge and Session canonical types plus approved Session state vocabulary and TransitionSpec registry base from 03/12/14. No generic setStatus. Keep transition rules independent from HTTP and ORM.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 02,03,12,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-05; Build Phase 2; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-01

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
STATE != STATUS STRING; ILLEGAL TRANSITION MUST NOT BE ENABLED BY GENERIC SETTER.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-05. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/domain challenge/session; transition registry; persistence mapping; migration 003; tests/domain and tests/transitions.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-05, predecessor extension points explicitly exposed for PKG-05, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: Challenge, Session, TransitionSpec.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 003.
Challenge and Session tables per 14 map.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Transition specs expose required boundary refs but boundary engine comes later.

AUTHORITY
Transition specs reference approved authority classes only.

EVIDENCE
Only approved references, no new sufficiency.

AI
None.

FAILURE_RECOVERY
Illegal/unknown transition fails closed precommit.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Illegal transition; unknown transition; controller-supplied target state; cross-Workspace target; direct enum coercion.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T1,T2.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-25.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-06: Question identity and lineage


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-06
BUILD_PHASE: 2
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-06 ONLY

AUTHORIZATION
You are authorized to implement only PKG-06, "Question identity and lineage". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Question stable identity, immutable original, lineage
Package materialization task:
Implement Question stable identity, immutable original_text, origin/derivation representation, QuestionLineage relation and typed QuestionRepository contract. Reframe never overwrites human original.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 02,03,07,12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-06; Build Phase 2; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-05

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
QUESTION IS FIRST-CLASS; ORIGINAL_TEXT IS IMMUTABLE; REFRAME CREATES NEW QUESTION IDENTITY PLUS LINEAGE.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-06. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/domain question; persistence mapping; migration 004 question subset; tests/domain/question.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-06, predecessor extension points explicitly exposed for PKG-06, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: QuestionRepository contract.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 004.
questions and question_lineage with immutability/composite Workspace constraints where feasible.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
No new boundary semantics.

AUTHORITY
No authorship-as-authority.

EVIDENCE
Preserve provenance hooks.

AI
AI reframe remains derived/new identity.

FAILURE_RECOVERY
Immutable-field mutation rejected.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Repository or SQL update original_text; cross-Workspace lineage; invalid self-lineage where forbidden; AI reframe replacing human original.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T1.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-01,P-02.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-07: Question Burst and frozen set


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-07
BUILD_PHASE: 2
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-07 ONLY

AUTHORIZATION
You are authorized to implement only PKG-07, "Question Burst and frozen set". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Human-only Burst states, capture, freeze and contamination guard
Package materialization task:
Implement QuestionBurst PREPARED, ACTIVE, PAUSED, COMPLETED, human-only capture, QuestionBurstQuestion membership and frozen raw-set fingerprint/reconstructable membership mechanism allowed by 14. Manual authorized completion only. No automatic timer.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 03,06,08,12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-07; Build Phase 2; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-06,PKG-03

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
HUMAN_ONLY ACTIVE BURST EXCLUDES AI; VERBATIM CAPTURE; FROZEN RAW SET CANNOT MUTATE; AUTOMATIC TIMER IS NOT AUTHORIZED.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-07. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/domain burst; packages/application burst operations; persistence mapping; migration 004 burst subset; tests/transitions, boundaries and ai guards.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-07, predecessor extension points explicitly exposed for PKG-07, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: Burst operations.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 004.
question_bursts and burst membership relation per 14.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Prepare BND-008 facts.

AUTHORITY
Session control authority referenced, not bypassed.

EVIDENCE
None.

AI
AI prohibited during HUMAN_ONLY ACTIVE.

FAILURE_RECOVERY
Freeze mutation denied.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
AI invocation ACTIVE; modify Question after freeze; add raw member after freeze; remove member after freeze; analyze before COMPLETED; timer auto-completes without authority.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T2,T4.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-03,P-04.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-08: Boundary engine core


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-08
BUILD_PHASE: 3
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-08 ONLY

AUTHORIZATION
You are authorized to implement only PKG-08, "Boundary engine core". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Boundary types, proof, registry, monotonic restriction
Package materialization task:
Implement BoundaryInput, BoundaryContext, BoundaryResult, BoundaryProof, evaluator protocol, registry, versioning and monotonic restriction. Results exactly ALLOW, DENY, REQUIRE, ESCALATE.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 06,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-08; Build Phase 3; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-03,PKG-05

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
ALLOW != AUTHORITY != COMMIT; DOWNSTREAM ALLOW NEVER OVERRIDES UPSTREAM DENY.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-08. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/boundaries core; tests/boundaries; architecture tests.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-08, predecessor extension points explicitly exposed for PKG-08, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: BoundaryEvaluator registry.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
No schema unless 14 maps operational proof persistence later; do not invent.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Core only, no semantic compression.

AUTHORITY
Boundary engine consumes authority proof but does not create it.

EVIDENCE
Typed slots only.

AI
None.

FAILURE_RECOVERY
Unknown/exception on consequential chain cannot silently ALLOW.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
DENY followed by ALLOW; missing result; unknown boundary; evaluator exception; cached ALLOW.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T4.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-13.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-09: Prototype boundaries 001-008


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-09
BUILD_PHASE: 3
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-09 ONLY

AUTHORIZATION
You are authorized to implement only PKG-09, "Prototype boundaries 001-008". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Identity through Burst boundary evaluators
Package materialization task:
Implement prototype BND-001 Identity, BND-002 Workspace, BND-003 Membership, BND-004 Governance/Role Context, BND-005 Human Authority, BND-006 Human Decision Authority, BND-007 State Transition, BND-008 Question Burst. Each produces reconstructable BoundaryProof. Do not compress to one authorization function.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 06,11,12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-09; Build Phase 3; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-07,PKG-08

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
BND-001..BND-008 REMAIN DISTINCT; HUMAN DECISION AUTHORITY IS NOT GENERIC AUTHORIZATION; BURST CONTAMINATION IS ITS OWN BOUNDARY.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-09. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/boundaries evaluators; tests/boundaries; tests/security cross-layer.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-09, predecessor extension points explicitly exposed for PKG-09, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: BND-001..008.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
No new domain schema.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
BND-001 through BND-008 executable.

AUTHORITY
Use AuthorityResolver current proof only.

EVIDENCE
Not yet BND-013.

AI
BND-008 blocks forbidden Burst AI.

FAILURE_RECOVERY
DENY terminal for consequence. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Attack each boundary individually plus chained combinations, including forged identity, Workspace mismatch, missing membership, role-only authority, missing human Decision, illegal state transition, ACTIVE Burst AI contamination, and downstream ALLOW after earlier DENY.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T4,T9.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-03,P-04,P-10,P-13,P-22.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-10: Command envelope and attempts


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-10
BUILD_PHASE: 4
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-10 ONLY

AUTHORIZATION
You are authorized to implement only PKG-10, "Command envelope and attempts". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Command contracts, registry, attempts and expected versions
Package materialization task:
Implement versioned CommandEnvelope, CommandRegistry, CommandId, AttemptId, CommandAttempt persistence and expected-version contracts from 09/14.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 09,12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-10; Build Phase 4; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-09

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
COMMAND != EVENT; ATTEMPT != COMMAND; AUTHORITY CONTEXT REF != REUSABLE AUTHORIZATION TOKEN.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-10. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/command; packages/persistence command repository; migration 008 subset; tests/command_commit_event.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-10, predecessor extension points explicitly exposed for PKG-10, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: CommandEnvelope, CommandRegistry.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 008.
commands and command_attempts per 14 map.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Command carries refs, never bypass tokens.

AUTHORITY
Current authority resolved later, never trusted from envelope.

EVIDENCE
Evidence refs typed when applicable.

AI
AI proposal cannot become command authority.

FAILURE_RECOVERY
Attempt outcome uses approved semantics only.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Event submitted as Command; stale authority context reused; changed payload under same command identity; wrong Workspace; missing required expected version.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T7.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-16,P-19.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-11: Idempotency


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-11
BUILD_PHASE: 4
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-11 ONLY

AUTHORIZATION
You are authorized to implement only PKG-11, "Idempotency". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Durable idempotency lifecycle and payload identity
Package materialization task:
Implement durable idempotency lifecycle with Workspace, command_type, payload_fingerprint, status, attempt, commit_id and result ref as mapped by 14.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 09,10,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-11; Build Phase 4; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-10

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
IDEMPOTENCY != AUTHORIZATION; COMMITTED DUPLICATE MUST NOT RE-EXECUTE; INDETERMINATE MUST NOT BLINDLY RETRY.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-11. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/command idempotency; persistence; migration 008 subset; tests/command_commit_event and recovery.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-11, predecessor extension points explicitly exposed for PKG-11, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: IdempotencyPort.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 008.
idempotency_records constraints/indexes per 14.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
No authority cached in idempotency.

AUTHORITY
Retry always requires fresh evaluation when execution is permitted.

EVIDENCE
Freshness not cached.

AI
None.

FAILURE_RECOVERY
Exact outcome-specific retry law.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
New; in-progress duplicate; committed duplicate; same key different payload; FAILED_PRECOMMIT retry; INDETERMINATE retry; cross-Workspace key collision.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T7.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-19,P-20.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-12: Audit and outbox contracts


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-12
BUILD_PHASE: 4
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-12 ONLY

AUTHORIZATION
You are authorized to implement only PKG-12, "Audit and outbox contracts". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Append AuditEvent and durable outbox semantics
Package materialization task:
Implement append-oriented AuditEvent contract/repository and durable Outbox contract/repository. Normal application cannot update/delete audit. Outbox delivery state is operational.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 09,11,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-12; Build Phase 4; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-10

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
LOG != AUDIT; AUDIT EVENT != DOMAIN EVENT; OUTBOX DELIVERY != NEW DOMAIN CONSEQUENCE.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-12. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/audit; packages/events outbox contracts; persistence; migration 009 subset; tests/command_commit_event.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-12, predecessor extension points explicitly exposed for PKG-12, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: AuditRepository, OutboxRepository.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 009.
audit_events and outbox_events with append-oriented constraints/privilege expectations.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Audit records boundary outcomes but does not grant authority.

AUTHORITY
None created.

EVIDENCE
Audit may reference Evidence proof, never replace it.

AI
None.

FAILURE_RECOVERY
Delivery failure after commit does not undo domain commit.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Audit update; audit delete; outbox duplicate; outbox failure after canonical commit fixture; outbox replay.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T7.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-16,P-25.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-13: Commit coordinator and BND-014


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-13
BUILD_PHASE: 4
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-13 ONLY

AUTHORIZATION
You are authorized to implement only PKG-13, "Commit coordinator and BND-014". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Atomic governed CommitUnit with fresh authority/version checks
Package materialization task:
Implement CommitCoordinator and BND-014 exactly: allocate CommitId; begin transaction; load authoritative current versions, governance, membership, HABB and Evidence where required; run BND-014; verify expected versions; prepare/apply canonical, relation and governance mutations; insert AuditEvent, Outbox and CommitUnit; update idempotency; commit; resolve consequence certainty. Use deterministic failure injection at all 14-specified points. Implement optimistic concurrency using expected versions and affected-row checks. Do not infer COMMITTED from client response.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 03,05,06,09,10,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-13; Build Phase 4; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-11,PKG-12

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
EARLIER ALLOW != COMMIT AUTHORITY; DATABASE TRANSACTION != LEGITIMATE TRANSITION; EXCEPTION != FAILURE SEMANTICS; BND-014 MUST REVALIDATE FRESH AUTHORITATIVE FACTS.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-13. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/commit coordinator/transaction ports; BND-014 evaluator; persistence commit repository; migration 009 commit subset; deterministic test-only failure injector; tests/command_commit_event, boundaries, mutation.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-13, predecessor extension points explicitly exposed for PKG-13, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: CommitCoordinator.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 009.
commit_units plus transactionally coupled canonical/governance mutation, audit, outbox and idempotency updates. PostgreSQL transaction semantics per 14.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
BND-014 mandatory final freshness gate.

AUTHORITY
Reload current membership/HABB/governance inside commit path. No cached authority.

EVIDENCE
Reload exact Evidence versions where command consumes Evidence.

AI
No AI authority path.

FAILURE_RECOVERY
Map DENIED, FAILED_PRECOMMIT, COMMITTED, INDETERMINATE only after certainty analysis. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Authority revoked after preparation; state version changed; Evidence changed; abort before commit; connection loss after commit; audit insertion failure; outbox insertion failure; duplicate idempotent request; concurrent Commands; failure after first mutation; failure before DB commit. Reconstruct exact authoritative result for every case.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T4,T7,T11.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-10,P-11,P-13,P-18,P-19,P-25.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-14: QuestionSelection


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-14
BUILD_PHASE: 5
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-14 ONLY

AUTHORIZATION
You are authorized to implement only PKG-14, "QuestionSelection". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Authority-bearing QuestionSelection relation
Package materialization task:
Implement QuestionSelection Command/path with QUESTION_SELECTION_RIGHT, current authority, Workspace, Session, eligible Question, boundary chain, BND-014, CommitUnit and Audit.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 02,03,04,06,12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-14; Build Phase 5; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-13,PKG-07

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
AI RECOMMENDATION != QUESTION SELECTION; QUESTION SELECTION IS AN AUTHORITY-BEARING RELATION.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-14. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/domain relation; packages/application selection handler; persistence; migration 005 subset if mapped; tests/authority/boundaries/e2e.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-14, predecessor extension points explicitly exposed for PKG-14, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: SelectQuestion command.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 005.
question_selections per 14.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
BND-001..008 and BND-014 as applicable.

AUTHORITY
QUESTION_SELECTION_RIGHT current binding required.

EVIDENCE
No invented Evidence requirement.

AI
AI may recommend only.

FAILURE_RECOVERY
Denied/stale selection creates no canonical relation.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
AI selection; human without right; stale selector authority; wrong Workspace; selection in invalid Session state; duplicate selection where relation semantics forbid it.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T3,T7.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-08.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-15: Human Decision


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-15
BUILD_PHASE: 5
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-15 ONLY

AUTHORIZATION
You are authorized to implement only PKG-15, "Human Decision". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
UNDER_CONSIDERATION to human DECIDED, separate downstream execution
Package materialization task:
Implement Decision UNDER_CONSIDERATION to DECIDED only through explicit authorized human Decision creation. Record human actor, DECISION_RIGHT, Workspace, scope, Decision content, source context, consumed AI recommendation refs, consumed Evidence refs, timestamp, version and provenance. Do not implement ApproveAIRecommendationAsDecision. Do not let AI, admin, author status or role-only actor write DECIDED. A committed Decision must not automatically execute downstream action.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 02,03,04,06,08,12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-15; Build Phase 5; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-13

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
AI RECOMMENDATION != HUMAN DECISION; AI PREPARATION != HUMAN DECISION; HUMAN APPROVAL OF AI OUTPUT != AUTOMATIC HUMAN DECISION SEMANTICS; DECIDED != EXECUTED; DECIDED != DOWNSTREAM AUTHORIZATION.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-15. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/domain decision; packages/application human Decision command; persistence migration 005 subset; tests/authority, transitions, e2e.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-15, predecessor extension points explicitly exposed for PKG-15, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: Decision commands.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 005.
decisions with exact states/version/provenance fields from 14.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
BND-005, BND-006, state boundary, BND-014.

AUTHORITY
DECISION_RIGHT current explicit human authority.

EVIDENCE
Consumed refs preserved, no new sufficiency.

AI
AI is context only and cannot write Decision state.

FAILURE_RECOVERY
Denied/stale human Decision creates no DECIDED state. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Persist AI proposal then only view it; unrelated approval click; technical admin update; role-only actor; revoked actor; cross-Workspace Decision; unattributed Decision; recommendation persistence setting DECIDED; committed Decision followed by downstream action without separate authority.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T3,T10.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-07,P-09,P-10.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-16: Evidence core


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-16
BUILD_PHASE: 6
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-16 ONLY

AUTHORIZATION
You are authorized to implement only PKG-16, "Evidence core". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Evidence, source, anchor, relation, set and provenance storage
Package materialization task:
Implement Evidence, SourceReference, ClaimAnchor, EvidenceRelation, EvidenceSet consumption linkage, validation state, relation assessment, versioning and provenance exactly from 07/14. No global Evidence score.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 07,09,12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-16; Build Phase 6; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-13

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
SOURCE != CLAIM; CLAIM != EVIDENCE; PROVENANCE != TRUTH; AI CONFIDENCE != EVIDENCE; AI CITATION != VALIDATED SUPPORT; STRUCTURALLY_VALID != TRUE; EVIDENCE EXISTENCE != SUFFICIENCY; EVIDENCE != AUTHORITY.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-16. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/evidence; persistence; migration 006; tests/evidence.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-16, predecessor extension points explicitly exposed for PKG-16, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: EvidenceRepository.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 006.
evidence, source_references, claim_anchors, evidence_relations, evidence_set consumption tables/refs per 14.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Prepare BND-013 facts.

AUTHORITY
Evidence does not grant authority.

EVIDENCE
Core responsibility.

AI
AI may propose/derive only as upstream allows.

FAILURE_RECOVERY
Invalid relation/version fails closed for consequential consumption.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
AI confidence cast as Evidence; citation auto-support; structural validity treated as truth; Evidence existence treated as sufficiency; Evidence treated as authority; cross-Workspace relation; stale ClaimAnchor.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T5.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-14,P-15.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-17: Evidence freshness boundary


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-17
BUILD_PHASE: 6
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-17 ONLY

AUTHORIZATION
You are authorized to implement only PKG-17, "Evidence freshness boundary". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
BND-013 and commit freshness linkage
Package materialization task:
Implement Evidence freshness evaluation and BND-013 for prototype. Bind exact Evidence, relation and set versions consumed by Command. Revalidate at commit through BND-014 integration. Do not invent global sufficiency.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 06,07,09,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-17; Build Phase 6; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-16,PKG-13

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
EVIDENCE EXISTENCE != SUFFICIENCY; EVIDENCE FRESHNESS IS COMMIT-SENSITIVE; STALE EVIDENCE CANNOT SUPPORT CONSEQUENCE.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-17. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/boundaries BND-013; packages/evidence freshness ports; commit integration; tests/evidence, boundaries, concurrency.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-17, predecessor extension points explicitly exposed for PKG-17, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: Evidence proof resolver.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
No new semantic tables beyond 16 unless 14 maps consumption refs.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
BND-013 plus BND-014 freshness coupling.

AUTHORITY
Evidence cannot replace human authority.

EVIDENCE
Exact version proof refs.

AI
AI confidence/citation rejected as Evidence.

FAILURE_RECOVERY
Freshness failure prevents commit. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Evidence invalidated after prepare; unavailable after prepare; EvidenceRelation changed; set membership changed; cross-Workspace Evidence; stale source/ClaimAnchor version where required.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T4,T5,T7.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-14,P-15,P-25.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-18: AI contracts and AIGeneration


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-18
BUILD_PHASE: 7
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-18 ONLY

AUTHORIZATION
You are authorized to implement only PKG-18, "AI contracts and AIGeneration". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
AIOP registry, generation lifecycle and derived artifact types
Package materialization task:
Implement prototype AIOP contracts, AIGeneration lifecycle REQUESTED, RUNNING, OUTPUT_RECEIVED, VALIDATED, REJECTED, FAILED, AI derived artifact type mapped by 14, and versioned validators. Preserve AI origin.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 08,09,12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-18; Build Phase 7; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-17

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
AI OUTPUT != CANONICAL AUTHORITY; VALIDATED != DOMAIN CONSEQUENCE; RETRY CREATES NEW GENERATION IDENTITY.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-18. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/ai_contracts; persistence migration 007 subset; tests/ai.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-18, predecessor extension points explicitly exposed for PKG-18, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: AI contracts.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 007.
ai_generations and ai_derived_artifacts per 14.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
No provider call yet; contract validation proof only.

AUTHORITY
AI records never authority.

EVIDENCE
AI_VALIDATION_PROOF remains distinct from DOMAIN_EVIDENCE.

AI
Core contracts and lifecycle.

FAILURE_RECOVERY
Rejected/failed generations create no canonical consequence.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Invalid contract; wrong version; forbidden effect; missing provenance; wrong Workspace; AI output marked human; retry reuses GenerationId.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T6.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-05,P-06,P-07.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-19: AI Gateway and MockProvider


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-19
BUILD_PHASE: 7
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-19 ONLY

AUTHORIZATION
You are authorized to implement only PKG-19, "AI Gateway and MockProvider". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Exclusive provider path, context manifest, prompt, validator
Package materialization task:
Implement exclusive AIGateway, AIOP registry, AIContextManifest allowlist builder, Prompt Builder with DATA delimitation, minimal Model Router, MockProviderAdapter, Response Validator, AI_VALIDATION_PROOF and derived artifact persistence. Provider credentials only Gateway. Real provider execution disabled and policy-gated beyond an environment variable. HUMAN_ONLY ACTIVE Burst must block invocation.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 08,11,12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-19; Build Phase 7; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-18,PKG-09

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
MODEL SDK != AI ARCHITECTURE; PROVIDER ACCESS != AUTHORITY; MOCK != PRODUCTION ELIGIBILITY; HARD-DEP-002 REMAINS BLOCKED.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-19. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/ai_gateway; approved provider adapter subpackage; packages/ai_contracts integration; tests/ai/security; import checker updates.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-19, predecessor extension points explicitly exposed for PKG-19, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: AIGateway.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 007.
Use migration 007 records only.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
BND-008 and AI invocation boundaries as mapped by 14.

AUTHORITY
No AI authority. Prompt text cannot grant it.

EVIDENCE
Context allowlist uses exact refs; AI_VALIDATION_PROOF not Evidence.

AI
Exclusive provider path. MockProvider default. Real provider execution BLOCKED by HARD-DEP-002.

FAILURE_RECOVERY
Provider failure creates AIGeneration FAILED/appropriate operational outcome, no domain consequence. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Mock valid; invalid schema; timeout; provider error; partial response; duplicate response; prompt injection; wrong Workspace artifact; forbidden canonical effect; missing provenance; direct provider import; prompt/retrieved text attempting to grant authority; active Burst invocation.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T6,T9.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-04,P-05,P-06,P-07,P-23.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-20: Event and outbox worker


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-20
BUILD_PHASE: 8
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-20 ONLY

AUTHORIZATION
You are authorized to implement only PKG-20, "Event and outbox worker". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
EventEnvelope delivery from committed outbox
Package materialization task:
Implement EventEnvelope serialization/versioning, outbox worker delivery and idempotent consumer contracts. Worker may deliver facts, not recreate domain consequence.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 09,10,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-20; Build Phase 8; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-13

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
EVENT != COMMAND; EVENT IS POST-COMMIT FACT; OUTBOX RETRY != DOMAIN RETRY.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-20. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/events; apps/worker outbox worker; tests/command_commit_event.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-20, predecessor extension points explicitly exposed for PKG-20, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: EventPublisher/consumer contracts.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
Outbox delivery operational fields only, no new domain authority.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
No new consequential boundary path.

AUTHORITY
Event carries attribution refs, not authority token.

EVIDENCE
Event may reference Evidence proof only.

AI
No rerun AI on replay.

FAILURE_RECOVERY
Delivery failure leaves domain COMMITTED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Duplicate delivery; worker restart; delivery failure; forged Event without CommitUnit; consumer attempts canonical write; outbox retry interpreted as command retry.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T7.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-16,P-17.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-21: Projection and replay


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-21
BUILD_PHASE: 8
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-21 ONLY

AUTHORIZATION
You are authorized to implement only PKG-21, "Projection and replay". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Rebuildable read models, replay without consequence
Package materialization task:
Implement projection repository/read model, projection consumer and rebuild/replay path. Projection can be dropped and rebuilt without canonical mutation. Commit/authority evaluation must not import projection.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 06,09,10,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-21; Build Phase 8; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-20

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
PROJECTION != CANONICAL STATE; EVENT REPLAY != NEW AUTHORIZATION.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-21. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/projection; apps/worker projection consumer; migration 010; tests/command_commit_event/mutation.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-21, predecessor extension points explicitly exposed for PKG-21, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: ProjectionRepository.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 010.
Projection tables/checkpoints only, write-owned by projection principal later.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
None created.

AUTHORITY
Projection never authority source.

EVIDENCE
Projection Evidence views non-authoritative.

AI
Replay cannot invoke AI.

FAILURE_RECOVERY
Projection failure does not alter canonical legitimacy.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Delete projection then rebuild; replay twice; corrupt projection; use projection in authority/commit; replay tries Command; replay reruns AI.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T7,T11.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-17.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-22: Failure classification and certainty


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-22
BUILD_PHASE: 9
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-22 ONLY

AUTHORIZATION
You are authorized to implement only PKG-22, "Failure classification and certainty". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Four outcomes and consequence certainty resolver
Package materialization task:
Implement four approved outcomes and consequence certainty resolver classes from 10. Classify only after authoritative consequence analysis.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 10,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-22; Build Phase 9; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-13,PKG-20

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
DENIED != FAILED_PRECOMMIT != COMMITTED != INDETERMINATE; TIMEOUT != FAILED; DB EXCEPTION != FAILED.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-22. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/recovery failure classifier/certainty types; tests/recovery.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-22, predecessor extension points explicitly exposed for PKG-22, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: FailureClassifier.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
No new schema.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Consumes commit/audit/outbox facts.

AUTHORITY
No authority creation.

EVIDENCE
Evidence state may be certainty input where relevant.

AI
No special AI shortcut.

FAILURE_RECOVERY
Core responsibility.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Timeout before/after commit; DB exception; client disconnect; missing projection; missing delivery; ambiguous connection loss.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T8.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-20,P-25.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-23: LPVS and RecoveryRecord


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-23
BUILD_PHASE: 9
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-23 ONLY

AUTHORIZATION
You are authorized to implement only PKG-23, "LPVS and RecoveryRecord". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Legitimacy-based LPVS and RecoveryRecord
Package materialization task:
Implement LPVSResolver and RecoveryRecord persistence. LPVS proof uses legal prior state, legal transition, actor, authority at commit, human Decision where required, Evidence where required, boundaries, commit, canonical resulting version, audit and provenance. Return UNRESOLVED if unique legitimate state cannot be proven.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 10,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-23; Build Phase 9; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-22,PKG-17

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
LPVS != LATEST; RECOVERY RECORD != AUTHORITY; LEGITIMACY MUST BE RECONSTRUCTED.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-23. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/recovery LPVS; persistence migration 011 subset; tests/recovery.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-23, predecessor extension points explicitly exposed for PKG-23, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: LPVSResolver, RecoveryRepository.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 011.
recovery_records plus approved refs.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Reads prior boundary proofs.

AUTHORITY
Historical authority proves prior legitimacy only, never current recovery authority.

EVIDENCE
Exact historical refs only.

AI
AI lineage may be reconstructed but not authority.

FAILURE_RECOVERY
UNRESOLVED preserved.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Later illegitimate row; later uncertain row; latest Event differs; projection newer; backup-like stale snapshot; missing authority proof; missing audit.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T8.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-20,P-21.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-24: BND-017/BND-018 and Recovery Command


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-24
BUILD_PHASE: 9
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-24 ONLY

AUTHORIZATION
You are authorized to implement only PKG-24, "BND-017/BND-018 and Recovery Command". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Indeterminate blocking, reconciliation and governed recovery
Package materialization task:
Implement BND-017 INDETERMINATE blocking, dependent-operation detection, BND-018 reconciliation routing, Recovery Command through normal identity, Workspace, current authority, Evidence if required, boundaries, BND-014 and CommitUnit. Deterministic recovery only restores already-established legitimate state. Discretionary domain choice requires existing human authority.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 06,10,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-24; Build Phase 9; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-23,PKG-13

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
RECOVERY != AUTHORITY; HISTORICAL AUTHORITY != CURRENT AUTHORITY; INDETERMINATE != FAILED; RETRY != REPLAY.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-24. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/recovery; packages/boundaries BND-017/BND-018; application Recovery Command; persistence migration 011 completion; tests/recovery/boundaries.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-24, predecessor extension points explicitly exposed for PKG-24, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: RecoveryService through Command.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 011.
RecoveryRecord and explicit dependency/block refs as mapped by 14.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
BND-017/BND-018 plus normal BND-014.

AUTHORITY
Current authority revalidated; technical admin not domain authority.

EVIDENCE
Fresh where recovery operation requires it.

AI
AI may not choose recovery domain state.

FAILURE_RECOVERY
Blind retry after INDETERMINATE blocked. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Admin recovery; service uses old authority; blind retry; direct SQL rollback; latest-row LPVS; recover to never-legitimate state; erase audit/history; revoked current authority; stale Evidence; event replay as recovery.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T4,T8.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-20,P-21.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-25: Service identity and DB principals


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-25
BUILD_PHASE: 10
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-25 ONLY

AUTHORIZATION
You are authorized to implement only PKG-25, "Service identity and DB principals". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Runtime technical identities and privilege separation
Package materialization task:
Implement service identities and local PostgreSQL principals derived by 14: migration_owner, api_reader, governed_commit_writer, ai_gateway_writer, projection_writer, recovery_reader, security_event_writer, audit_reader, test_principal. No runtime superuser. Execute real privilege tests.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 11,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-25; Build Phase 10; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-13,PKG-19,PKG-21,PKG-24

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
SERVICE IDENTITY != SYSTEM_DERIVED AUTHORITY; DB CREDENTIAL != DOMAIN AUTHORITY; MIGRATION OWNER != RUNTIME ACTOR.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-25. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/security service identity/capability map; migration 012 principal grants; infra local DB role setup; tests/security.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-25, predecessor extension points explicitly exposed for PKG-25, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: security capability map.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 012.
Principal/grant definitions only.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Technical privilege never replaces semantic boundaries.

AUTHORITY
No human rights in service identities.

EVIDENCE
No privilege-based Evidence trust.

AI
Gateway gets only required operational writes.

FAILURE_RECOVERY
Forbidden DB operation must fail technically.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
For each principal attempt permitted and forbidden read/write; attempt canonical write from projection; governance write from AI Gateway; Decision write from admin-like technical identity.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T9.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-18,P-22,P-23,P-24.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-26: RLS and SecurityEvents


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-26
BUILD_PHASE: 10
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-26 ONLY

AUTHORIZATION
You are authorized to implement only PKG-26, "RLS and SecurityEvents". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Workspace defense-in-depth and security operational records
Package materialization task:
Implement PostgreSQL RLS defense-in-depth and SecurityEvent operational records for prototype attacks. Test Workspace isolation at repository, Command, Evidence, AI context, projection and DB-policy layers. Technical admin identity still has no Decision right.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 11,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-26; Build Phase 10; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-25

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
RLS != DOMAIN AUTHORITY; SECURITY CONTROL MAY BLOCK BUT MAY NOT CREATE LEGITIMACY.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-26. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/security RLS context/SecurityEvent; migration 012 RLS policies/security_events; tests/security.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-26, predecessor extension points explicitly exposed for PKG-26, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: SecurityEventRepository.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: 012.
RLS policies and security_events per 14.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
BND-002 remains semantic enforcement in addition to RLS.

AUTHORITY
RLS success never grants domain authority.

EVIDENCE
Cross-Workspace Evidence denied.

AI
Cross-Workspace AI context denied.

FAILURE_RECOVERY
SecurityEvent records attack where appropriate without mutating domain. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Cross-Workspace at every layer; wrong DB principal; forged role; forged authority request; direct canonical write; privileged technical identity attempts Decision; RLS bypass assumption.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T9.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-22,P-24.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-27: Observability correlation


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-27
BUILD_PHASE: 10
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-27 ONLY

AUTHORIZATION
You are authorized to implement only PKG-27, "Observability correlation". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Structured diagnostic correlation without authority/truth
Package materialization task:
Implement structured ObservationContext and local OpenTelemetry API sink with correlation_id, command_id, attempt_id, commit_id, event_id, generation_id, recovery_id, operation, boundary result and failure class. Minimize content.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 11,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-27; Build Phase 10; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-13,PKG-19,PKG-24

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
OBSERVABILITY != AUDIT; TRACE != AUTHORITY; TELEMETRY != TRUTH.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-27. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/observability; app/worker instrumentation integration; tests/security/observability.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-27, predecessor extension points explicitly exposed for PKG-27, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: ObservationContext.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
No domain schema.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Observe result refs only.

AUTHORITY
Never consumed as authority proof.

EVIDENCE
No sensitive Evidence content by default.

AI
No raw prompt by default.

FAILURE_RECOVERY
Diagnostic only.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Secret in trace; full Evidence in log; prompt content leakage; trace value used as authority; missing audit replaced by log.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T9.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-25.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-28: Minimum frontend shell


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-28
BUILD_PHASE: 11
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-28 ONLY

AUTHORIZATION
You are authorized to implement only PKG-28, "Minimum frontend shell". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Workspace, Session, Burst, origin labels and blocked states
Package materialization task:
Implement minimum Next.js shell for Workspace context, Challenge/Session, HUMAN_ONLY Question Burst, verbatim Question capture, frozen raw set, AI analysis view/origin labels, blocked/denied and INDETERMINATE states. Typed API client only.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 12,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-28; Build Phase 11; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-21,PKG-26

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
FRONTEND CAPABILITY != AUTHORITY; HIDING BUTTON != SECURITY.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-28. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
apps/web routes/components/api client; Vitest/Playwright tests.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-28, predecessor extension points explicitly exposed for PKG-28, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: typed API client.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
None.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Server responses only, no client authority calculation.

AUTHORITY
Display server-provided capability for UX only.

EVIDENCE
Display only where mapped.

AI
No ACTIVE Burst AI controls.

FAILURE_RECOVERY
Render denied/blocked/indeterminate distinctly.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Manually send hidden/disabled action; forged Workspace in client; attempt AI control during ACTIVE Burst; manipulate client capability flag.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: UI tests.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-03,P-04,P-22.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-29: Human Decision UI


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-29
BUILD_PHASE: 11
EXECUTION_MODE: CREATE
HUMAN_AUTHORIZED_SCOPE: PKG-29 ONLY

AUTHORIZATION
You are authorized to implement only PKG-29, "Human Decision UI". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Separate AI recommendation from human Decision creation
Package materialization task:
Implement Human Decision UI separated visually and semantically from AI recommendation. Capture human Decision content and consumed AI/Evidence refs. Browser path: AI recommendation exists, Decision remains UNDER_CONSIDERATION, authorized human creates Decision, Decision becomes DECIDED, no downstream consequence occurs automatically.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-29; Build Phase 11; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-15,PKG-19,PKG-28

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
AI RECOMMENDATION != HUMAN DECISION; HUMAN DECISION UI CREATES A NEW HUMAN-OWNED DECISION; DECIDED DOES NOT AUTO-EXECUTE.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-29. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
apps/web Decision components/routes; typed API client extension; Playwright E2E.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-29, predecessor extension points explicitly exposed for PKG-29, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: Decision UI contract.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
None.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Server BND chain authoritative.

AUTHORITY
UI never calculates DECISION_RIGHT.

EVIDENCE
Consumed refs sent as context only.

AI
Recommendation displayed separately.

FAILURE_RECOVERY
Denied/stale server response leaves Decision unchanged. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Label/action implying Approve AI Decision; view-only action causing Decision; disabled button bypass; role-only actor; admin path; auto-action after DECIDED.
At least 5 total novel/adapted attacks are required for this package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: E2E.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-07,P-08,P-09.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
Respect the phase boundary. Package completion does not authorize the next phase.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-30: TestProofBundle and E2E proof paths


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-30
BUILD_PHASE: 12
EXECUTION_MODE: VERIFY
HUMAN_AUTHORIZED_SCOPE: PKG-30 ONLY

AUTHORIZATION
You are authorized to implement only PKG-30, "TestProofBundle and E2E proof paths". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Authoritative proof collection and six mandatory paths
Package materialization task:
Implement TestProofBundle as test-only representation and six E2E proof paths: happy, denial, stale-authority, cross-Workspace, AI-boundary, recovery. Collect canonical state, governance, authority, BoundaryProof, CommitUnit, AuditEvent, Event, Evidence, AI lineage, RecoveryRecord and SecurityEvent. Map all executable P-01..P-25. Keep hard dependencies BLOCKED.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 12,13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-30; Build Phase 12; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-24,PKG-26,PKG-29

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
TESTPROOFBUNDLE COLLECTS EXISTING PROOF ONLY; TEST != AUTHORITY; GREEN ASSERTION != ARCHITECTURAL PROOF.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-30. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
packages/test_support proof bundle; tests/e2e; P-claim matrix artifact.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-30, predecessor extension points explicitly exposed for PKG-30, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: TestProofBundle.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
No production schema.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Collect actual boundary proofs.

AUTHORITY
Collect actual resolver/binding refs.

EVIDENCE
Collect exact consumed versions.

AI
Collect generation/context/validation refs.

FAILURE_RECOVERY
Collect exact outcomes/certainty/recovery refs. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
For each E2E path add at least one counter-path attempting to manufacture missing proof; use NON_PROOF bootstrap only with explicit non-proof marker; ensure MockProvider cannot satisfy provider eligibility.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T10.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-01..P-25.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-31: Mutation and adversarial harness


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-31
BUILD_PHASE: 13
EXECUTION_MODE: ATTACK
HUMAN_AUTHORIZED_SCOPE: PKG-31 ONLY

AUTHORIZATION
You are authorized to implement only PKG-31, "Mutation and adversarial harness". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Mutate core invariants and require test detection
Package materialization task:
Implement mutation/adversarial harness that deliberately removes BND-014, trusts cached authority, removes Workspace check, treats AI recommendation as Decision, enables direct DB write, treats Event as Command, accepts stale Evidence, enables INDETERMINATE retry, enables admin fallback and bypasses AI Gateway. Baseline PASS, mutation must make relevant tests FAIL, restore, baseline PASS.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-31; Build Phase 13; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-30

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
MUTATION TESTING ASKS WHETHER THE PROOF SUITE NOTICES ARCHITECTURAL VIOLATION.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-31. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
tests/mutation; scripts/mutation runner; test-only controlled mutation seams allowed by 14.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-31, predecessor extension points explicitly exposed for PKG-31, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: mutation runner.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
No production schema.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Mutate boundary enforcement only under test harness.

AUTHORITY
Mutate authority shortcuts only under test harness.

EVIDENCE
Mutate stale acceptance under test harness.

AI
Mutate Gateway/Decision collapse under test harness.

FAILURE_RECOVERY
Surviving mutation means PACKAGE_FAIL_IMPLEMENTATION or TEST_DESIGN_DEFECT. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
The listed ten mutations are mandatory. Add novel mutations where safe. Never weaken mutation or production semantics for convenience.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T11.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-01..P-25.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

### PKG-32: Recursive regression and proof report


```text
NQUIRY_CODEX_EXECUTION_PROMPT
PROMPT_VERSION: 1.0
PACKAGE_ID: PKG-32
BUILD_PHASE: 14
EXECUTION_MODE: RECONSTRUCT
HUMAN_AUTHORIZED_SCOPE: PKG-32 ONLY

AUTHORIZATION
You are authorized to implement only PKG-32, "Recursive regression and proof report". Do not start a successor package. Inspect git status before work. Preserve unrelated human changes. Do not reset broadly, delete unrecognized files, rewrite architecture files, commit secrets, or modify lockfiles without package necessity.

OBJECTIVE
Dependency-driven regression and implementation proof report
Package materialization task:
Run T0 through T12, reconstruct P-01 through P-25, generate final implementation proof report with PASS, FAIL, BLOCKED, INCONCLUSIVE and cause attribution IMPLEMENTATION_DEFECT, ARCHITECTURE_CONTRADICTION, UPSTREAM_GAP, TEST_DESIGN_DEFECT, FIXTURE_INVALID, ENVIRONMENT_FAILURE, INCONCLUSIVE_PROOF. Preserve possible result ARCHITECTURAL_IMPLEMENTATION_PROOF::PASS with EXECUTABLE_PROTOTYPE_ACCEPTANCE::BLOCKED if hard dependencies remain.

SOURCE_AUTHORITY
Strict hierarchy: LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15.
Architecture defines what may exist. 14 defines how it is materialized. 15 defines your execution discipline. You do not define architecture.

MANDATORY_FILES_TO_READ
Read 14_IMPLEMENTATION_SEQUENCE.md first, including this package manifest entry, repository topology, file-level map, DB map, API map if applicable, test map, package DAG, phase gates, forbidden dependencies and stop conditions.
Then read upstream architecture files listed by 14 for this package: 13,14.
Read 15_AI_CODING_PROMPTS.md execution law and this package prompt.
Inspect predecessor implementation, relevant tests, relevant migrations, architecture dependency checks and current git diff.

MANDATORY_14_SECTIONS
Package manifest for PKG-32; Build Phase 14; Coding Package DAG; repository topology; dependency direction; semantic type system; applicable database/migration/repository/API maps; test implementation map; proof-claim map; stop conditions; forbidden shortcuts.

PREDECESSORS
PKG-31

PREDECESSOR_ACCEPTANCE_REQUIRED
Every predecessor above must exist in repository reality and have accepted completion evidence. Self-reported completion is insufficient. If a required predecessor contract is absent or not accepted, return PACKAGE_BLOCKED_PREDECESSOR and STOP.

ARCHITECTURAL_INVARIANTS
PASS != BLOCKED; GREEN CI != CLOSED UPSTREAM GAP; FINAL PROOF MUST PRESERVE CAUSE ATTRIBUTION.
CODE != AUTHORITY.
DATABASE SCHEMA != DOMAIN SEMANTICS.
FRAMEWORK CAPABILITY != SYSTEM PERMISSION.
HTTP ENDPOINT != COMMAND AUTHORITY.
DATABASE TRANSACTION != LEGITIMATE TRANSITION.
ADMIN API != GOVERNANCE AUTHORITY.
BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY.
CACHE != CANONICAL STATE.
LOGGING != AUDIT.
TEST PASS != ARCHITECTURAL TRUTH.

NON_COLLAPSE_RULES
Preserve every upstream distinction consumed by this package. Use separate types/contracts where 14 requires them. Unknown consequential semantic input fails closed. Do not turn origin into authority, confidence into Evidence, role into authority, Event into Command, projection into canonical truth, retry into authorization, recovery into authority, or mock/fixture into production eligibility.

PACKAGE_BOUNDARY
Implement only PKG-32. Do not implement successor behavior. Do not create temporary semantic interfaces for later packages. If a later contract is required but absent, STOP rather than stub semantic behavior.

FILES_ALLOWED_TO_CREATE
tests/regression; proof report output under docs/proof or exact 14 mapped path; no architecture edits.
Only exact files/directories justified by 14 file-level implementation map and this package may be added.

FILES_ALLOWED_TO_MODIFY
Existing files directly required by PKG-32, predecessor extension points explicitly exposed for PKG-32, package tests, relevant migration chain, architecture-check configuration where this package is its authorized owner.

FILES_FORBIDDEN_TO_MODIFY
Architecture files 00 through 15; unrelated packages; unrelated migrations; unrelated tests; production code solely to ease a test; successor package implementation; broad generic utils/helpers/services/common dumping grounds.

PUBLIC_INTERFACES
14 requires: proof report.
Create only the typed public interfaces needed by this package. Generic Repository<T>, generic status setters, generic authority booleans and unversioned consequential dict payloads are forbidden where they erase semantics.

DATABASE_CHANGES
14 mapping: none.
No schema changes.
When a migration is required: inspect migration head; create exactly required migration; review SQL; verify upgrade; inspect schema; verify downgrade only as schema migration behavior; re-upgrade; run constraints. Schema downgrade is not domain rollback.

COMMANDS
Implement only Commands assigned by 14 to this package. A Command is not an Event and carries no reusable authority token. If none are assigned, NOT_APPLICABLE.

QUERIES
Implement only Queries assigned by 14. Queries must not mutate canonical/governance state. If none, NOT_APPLICABLE.

EVENTS
Use only event contracts assigned by 14. If none are assigned, NOT_APPLICABLE.

BOUNDARIES
Reconstruct all exercised boundary chains.

AUTHORITY
Reconstruct all exercised authority paths.

EVIDENCE
Reconstruct exact versions.

AI
Reconstruct Gateway lineage and non-authority.

FAILURE_RECOVERY
Reconstruct certainty/LPVS/recovery. HUMAN_GATE_REQUIRED.

SECURITY
Apply global security and Workspace isolation requirements from 11/14. Do not create new security semantics.

IMPLEMENTATION_SEQUENCE
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
Do not edit before A through D are complete.

PRE_IMPLEMENTATION_TRACE
Produce:
PACKAGE_ID
BUILD_PHASE
PREDECESSORS_FOUND
UPSTREAM_FILES_READ
14_SECTIONS_READ
EXISTING_IMPLEMENTATION_FOUND
EXISTING_TESTS_FOUND
MIGRATIONS_FOUND
POTENTIAL_CONFLICTS
Then reconstruct:
SOURCE REQUIREMENT
-> DOMAIN SEMANTIC
-> STATE / RELATION
-> AUTHORITY
-> BOUNDARY
-> COMMAND / QUERY
-> PERSISTENCE
-> AUDIT / EVENT
-> FAILURE
-> TEST
-> PROOF CLAIM
Use NOT_APPLICABLE explicitly where legitimate.

PRE_IMPLEMENTATION_ATTACK_MODEL
Before coding, answer: How could an incorrect implementation appear to work?
Enumerate at least 3 semantic shortcut attacks; 3 authority/boundary bypass attacks where relevant; 2 persistence/concurrency attacks where relevant; 2 Workspace attacks where relevant; 2 AI-authority attacks where relevant; 2 failure/retry attacks where relevant; 1 projection/cache truth attack where relevant. Mark genuinely non-applicable categories.
Package-specific mandatory attacks:
Re-run critical red-team prompts and verify proof artifacts are authoritative, not logs/UI/mocks. Verify no hard dependency converted to PASS.
At least 10 total novel/adapted attacks are required for this critical package.

TESTS_TO_WRITE_FIRST
Write negative/falsification tests before or alongside architecture-critical behavior. Demonstrate expected pre-fix failure where technically practical. If not possible, report PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::NOT_AVAILABLE with reason. Tests must prefer authoritative canonical/governance state, BoundaryProof, CommitUnit, AuditEvent, durable Event/Outbox, Evidence/provenance, SecurityEvent and RecoveryRecord over private call counts or logs.

IMPLEMENTATION_TASKS
Implement the smallest complete coherent change described above and in 14. No unrelated refactor. No future-generic abstraction. No architecture-critical TODO/FIXME, allow-all boundary, mock authority resolver, fake audit/commit, in-memory idempotency where durability is required, catch-all retry, admin bypass, placeholder Workspace filter, or test-only path reachable from production.

STATIC_VERIFICATION
Run formatting for affected code, lint, typecheck, architecture dependency checks, provider SDK import checker, test-only import checker, schema/migration validation where applicable. Verify forbidden imports from 14 remain absent.

TARGETED_TESTS
14 test families: T12.
Run package unit, semantic and migration tests first. For DB principals, run real local PostgreSQL privilege tests. For concurrency, use deterministic barriers/hooks, never sleep-based proof. For failure injection, use test-only deterministic hooks.

NEGATIVE_TESTS
Run all negative tests designed before implementation. Assert canonical/governance result, not merely error text.

ADVERSARIAL_COUNTER_TESTS
After targeted tests pass, construct additional attacks not used by the happy path. For each report:
ATTACK
EXPECTED DEFENSE
EXPECTED BOUNDARY
EXPECTED CANONICAL RESULT
EXPECTED PROOF ARTIFACT
ACTUAL RESULT
Do not merely rerun existing tests.

CROSS_LAYER_TESTS
Exercise this package with all predecessor layers it consumes. Verify relational proof, not isolated mocks. If package participates in a consequential path, reconstruct current authoritative inputs and resulting proof records.

RECURSIVE_REGRESSION
Run all tests for this package; predecessor invariants consumed; every already-existing P claim this package could invalidate; architecture dependency checks. Determine regression scope from dependency graph, not convenience.

PROOF_CLAIMS
14 assigns: P-01..P-25.
Track each as introduced, exercised, potentially affected, or regression required. A blocked upstream dependency remains BLOCKED.

REQUIRED_PROOF_ARTIFACTS
Collect every applicable canonical state reference, governance reference, authority proof, BoundaryProof, CommitUnit, AuditEvent, Outbox/Event, Evidence/version reference, AI lineage, RecoveryRecord and SecurityEvent. Logs and UI are not primary proof.

DIFF_AUDIT
Inspect actual git diff. Confirm only authorized files changed. Ask explicitly whether you introduced a new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency. Any unauthorized semantic change means PACKAGE_FAIL_IMPLEMENTATION or STOP_ARCHITECTURE_CONFLICT.

ARCHITECTURE_RECONSTRUCTION_CHECK
Where relevant reconstruct:
REQUEST
-> ACTOR
-> WORKSPACE
-> CURRENT STATE
-> CURRENT GOVERNANCE
-> CURRENT AUTHORITY
-> HUMAN DECISION
-> EVIDENCE
-> BOUNDARIES
-> BND-014
-> COMMAND
-> COMMIT UNIT
-> CANONICAL MUTATION
-> AUDIT
-> OUTBOX
-> EVENT
-> RESULTING STATE
Identify every proof artifact. If the package does not yet reach a full consequence, reconstruct the longest legitimate chain it participates in and mark remaining nodes NOT_APPLICABLE or SUCCESSOR_NOT_BUILT.

FORBIDDEN_SHORTCUTS
14: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs.
DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
No direct canonical mutation outside governed path. No feature flag may grant authority, bypass boundaries, disable isolation/audit, permit blind retry, or convert AI output into Decision.

STOP_CONDITIONS
14: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable.
Also STOP if required authority is undefined; transition absent from 03; Evidence rule undefined; Workspace scope unresolved; HARD-DEP-001 legitimacy is required; HARD-DEP-002 real-provider eligibility is required; recovery needs a new domain choice; Export Authority is required; test expectation conflicts with architecture; upstream files materially contradict; invariant must be weakened; CommitUnit atomicity cannot be provided; security boundary cannot be enforced as claimed.
On STOP, stop editing and return:
STOP::TRUE
PACKAGE_ID
STOP_REASON
FIRST_CONFLICTING_SOURCE
SECOND_CONFLICTING_SOURCE if applicable
14_REQUIREMENT
IMPLEMENTATION_POINT
AFFECTED_FILES
AFFECTED_TESTS
AFFECTED_PROOF_CLAIMS
WHY_LOCAL_WORKAROUND_WOULD_BE_SEMANTIC_INVENTION
MINIMUM_HUMAN_DECISION_REQUIRED

COMPLETION_REPORT
Return exactly these fields, with evidence:
PACKAGE_ID
PACKAGE_TITLE
BUILD_PHASE
VERDICT
UPSTREAM_FILES_READ
14_REQUIREMENTS_MATERIALIZED
PREDECESSORS_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_DELETED
MIGRATIONS_CREATED
SCHEMA_CHANGES
DB_PRIVILEGE_CHANGES
PUBLIC_INTERFACES_CREATED
COMMANDS_CREATED
QUERIES_CREATED
EVENTS_CREATED
BOUNDARIES_CREATED_OR_CHANGED
AUTHORITY_PATH
EVIDENCE_PATH
AI_PATH
RECOVERY_PATH
TESTS_CREATED
TESTS_MODIFIED
TARGETED_TEST_RESULTS
NEGATIVE_TEST_RESULTS
ADVERSARIAL_TEST_RESULTS
CROSS_LAYER_TEST_RESULTS
RECURSIVE_REGRESSION_RESULTS
P_CLAIMS_TESTED
PROOF_ARTIFACTS
FORBIDDEN_DEPENDENCY_CHECK
PROVIDER_SDK_CHECK
TEST_ONLY_IMPORT_CHECK
DIFF_AUDIT
ARCHITECTURE_RECONSTRUCTION_RESULT
KNOWN_LIMITATIONS
BLOCKED_DEPENDENCIES
NEW_GAPS_DISCOVERED
NO_SEMANTIC_INVENTION_CONFIRMATION
NEXT_PACKAGE_ALLOWED_BY_DAG
HUMAN_GATE_REQUIRED

PACKAGE_VERDICT
Terminate with exactly one:
PACKAGE_PASS
PACKAGE_FAIL_IMPLEMENTATION
PACKAGE_BLOCKED_UPSTREAM
PACKAGE_BLOCKED_PREDECESSOR
PACKAGE_INCONCLUSIVE_ENVIRONMENT
ARCHITECTURE_CONTRADICTION

HUMAN_GATE
HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any successor.

Repository hygiene at return: show git status, changed files, concise diff summary, migrations and test artifacts.

DO NOT START SUCCESSOR PACKAGE.

RETURN PACKAGE COMPLETION REPORT.

STOP.
```

## 4. Phase completion prompts

### PHASE_GATE_00
```text
PHASE_GATE_00
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 0 VERIFICATION ONLY
PACKAGES: PKG-00
REQUIRED_PREVIOUS_PHASE_GATE: none

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 0, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 1.
STOP.
```

### PHASE_GATE_01
```text
PHASE_GATE_01
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 1 VERIFICATION ONLY
PACKAGES: PKG-01, PKG-02, PKG-03, PKG-04
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 0 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 1, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 2.
STOP.
```

### PHASE_GATE_02
```text
PHASE_GATE_02
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 2 VERIFICATION ONLY
PACKAGES: PKG-05, PKG-06, PKG-07
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 1 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 2, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 3.
STOP.
```

### PHASE_GATE_03
```text
PHASE_GATE_03
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 3 VERIFICATION ONLY
PACKAGES: PKG-08, PKG-09
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 2 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 3, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 4.
STOP.
```

### PHASE_GATE_04
```text
PHASE_GATE_04
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 4 VERIFICATION ONLY
PACKAGES: PKG-10, PKG-11, PKG-12, PKG-13
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 3 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 4, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 5.
STOP.
```

### PHASE_GATE_05
```text
PHASE_GATE_05
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 5 VERIFICATION ONLY
PACKAGES: PKG-14, PKG-15
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 4 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 5, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 6.
STOP.
```

### PHASE_GATE_06
```text
PHASE_GATE_06
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 6 VERIFICATION ONLY
PACKAGES: PKG-16, PKG-17
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 5 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 6, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 7.
STOP.
```

### PHASE_GATE_07
```text
PHASE_GATE_07
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 7 VERIFICATION ONLY
PACKAGES: PKG-18, PKG-19
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 6 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 7, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 8.
STOP.
```

### PHASE_GATE_08
```text
PHASE_GATE_08
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 8 VERIFICATION ONLY
PACKAGES: PKG-20, PKG-21
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 7 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 8, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 9.
STOP.
```

### PHASE_GATE_09
```text
PHASE_GATE_09
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 9 VERIFICATION ONLY
PACKAGES: PKG-22, PKG-23, PKG-24
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 8 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 9, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 10.
STOP.
```

### PHASE_GATE_10
```text
PHASE_GATE_10
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 10 VERIFICATION ONLY
PACKAGES: PKG-25, PKG-26, PKG-27
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 9 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 10, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 11.
STOP.
```

### PHASE_GATE_11
```text
PHASE_GATE_11
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 11 VERIFICATION ONLY
PACKAGES: PKG-28, PKG-29
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 10 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 11, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 12.
STOP.
```

### PHASE_GATE_12
```text
PHASE_GATE_12
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 12 VERIFICATION ONLY
PACKAGES: PKG-30
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 11 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 12, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 13.
STOP.
```

### PHASE_GATE_13
```text
PHASE_GATE_13
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 13 VERIFICATION ONLY
PACKAGES: PKG-31
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 12 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 13, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE 14.
STOP.
```

### PHASE_GATE_14
```text
PHASE_GATE_14
EXECUTION_MODE: VERIFY + RECONSTRUCT + REPORT
AUTHORIZED_SCOPE: PHASE 14 VERIFICATION ONLY
PACKAGES: PKG-32
REQUIRED_PREVIOUS_PHASE_GATE: PHASE 13 HUMAN_APPROVED

Repository reality wins over completion reports. Do not implement successor behavior.
Read 14 Phase 14, package manifest entries, DAG, file map, DB map, API map, test map, proof map and stop conditions. Read all package completion reports. Inspect git status/diff and migrations.

VERIFY
1. Every package in this phase has an accepted package verdict and all DAG predecessors are accepted.
2. Files, public contracts, migrations, DB privileges and API surfaces match 14.
3. No forbidden dependency, provider SDK leak, test_support production import, admin fallback, direct canonical write or generic semantic dumping ground exists.
4. Run phase format, lint, typecheck, architecture checks, migration validation and all phase tests.
5. Run affected P-claim regressions and critical-package adversarial tests.
6. Inspect tests for weakening, deleted negative cases, overmocking, fixture circularity or proof from logs/UI.
7. Inspect migration SQL, constraints, RLS and real DB privileges where applicable.
8. Reconstruct one cross-package consequence or longest available legitimate chain from authoritative records.
9. HARD-DEP-001 and HARD-DEP-002 remain explicit unless resolved upstream by human architecture work.
10. GAP-14-001 through GAP-14-005 remain explicit unless resolved upstream.

Return PHASE PROOF REPORT:
PHASE_ID
PACKAGES_VERIFIED
DAG_PREDECESSORS_VERIFIED
FILES_REVIEWED
MIGRATIONS_REVIEWED
FORBIDDEN_DEPENDENCY_RESULT
TARGETED_TEST_RESULT
PHASE_REGRESSION_RESULT
P_CLAIMS_EXERCISED
ADVERSARIAL_RESULT
CROSS_PACKAGE_RECONSTRUCTION
HARD_DEP_STATUS
CARRIED_GAP_STATUS
IMPLEMENTATION_DEFECTS
TEST_DESIGN_DEFECTS
ARCHITECTURE_CONTRADICTIONS
ENVIRONMENT_BLOCKERS
READY_FOR_HUMAN_REVIEW

Architecture contradiction means STOP, with first conflicting source, implementation point, affected packages/tests/proof claims and minimum human decision required.

Final status exactly one:
READY_FOR_HUMAN_REVIEW
BLOCKED

HUMAN_GATE_REQUIRED::YES
DO NOT START PHASE SUCCESSOR WORK.
STOP.
```


## 5. Reusable independent review and counter-test prompts

### PROMPT_CROSS_MODEL_ARCHITECTURE_REVIEW
```text
PROMPT_CROSS_MODEL_ARCHITECTURE_REVIEW
EXECUTION_MODE: VERIFY
Do not edit code. Input PACKAGE_ID, package completion report, diff, relevant architecture files, tests and proof artifacts. Ignore developer confidence. Inspect source directly. Search for semantic collapse, authority leak, boundary bypass, Workspace leak, Evidence collapse, AI authority leak, failure/retry ambiguity, projection truth, admin fallback, test circularity, missing negative case, missing proof artifact, forbidden dependency and hidden upstream-gap closure. Trace every finding to source -> implementation -> test -> proof.
Return findings with exact file/test references and one verdict: REVIEW_PASS, REVIEW_FINDING, ARCHITECTURE_CONFLICT, INCONCLUSIVE.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_PACKAGE_RED_TEAM
```text
PROMPT_PACKAGE_RED_TEAM
EXECUTION_MODE: ATTACK
Assume tests are green. Do not trust completion report, developer explanation, test names or comments. Read code and architectural source. Generate novel attacks. Critical packages 03,09,13,15,17,19,24,26,30,31,32 require at least 10 attacks; ordinary packages at least 5.
For each: ATTACK_ID, INVARIANT_TARGETED, ATTACK_PATH, EXPECTED_DEFENSE, ACTUAL_DEFENSE, CANONICAL_CONSEQUENCE, PROOF_ARTIFACTS, VERDICT.
Do not edit code. STOP after red-team report.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_TEST_FALSIFICATION_REVIEW
```text
PROMPT_TEST_FALSIFICATION_REVIEW
EXECUTION_MODE: VERIFY
Determine whether tests prove architecture or merely mirror implementation. Inspect implementation mirroring, overmocking, private-call assertions, missing canonical-state assertion, missing negative path, missing Workspace path, missing revocation, missing deterministic concurrency, missing failure injection, missing proof reconstruction, fixture circularity, NON_PROOF misuse, MockProvider overclaim and mutation survival.
Return exactly one: TEST_PROOF_STRONG, TEST_PROOF_WEAK, TEST_DESIGN_DEFECT, BLOCKED.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_MIGRATION_ARCHITECTURE_REVIEW
```text
PROMPT_MIGRATION_ARCHITECTURE_REVIEW
EXECUTION_MODE: VERIFY
Inspect migration ordering, tables, columns, constraints, Workspace keys, composite FKs, versions, append-oriented records, indexes, write principals, RLS and rollback scripts. Verify schema rollback != domain rollback. Verify no migration grants runtime domain authority and no cascade delete removes proof-critical history without approved policy. Do not edit.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_SECURITY_COUNTER_TEST
```text
PROMPT_SECURITY_COUNTER_TEST
EXECUTION_MODE: ATTACK
Controlled local/test only. Verify environment before any destructive action. Attack cross-Workspace references, wrong DB principal, direct canonical write, provider credential access, Gateway bypass, admin domain mutation, forged role, forged authority, revoked identity/session fixture, Event forgery, audit tamper fixture and test-support production import. Report exact SecurityEvents, canonical result, boundary proof and DB result. Security control may block but may not create legitimacy.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_RECOVERY_COUNTER_TEST
```text
PROMPT_RECOVERY_COUNTER_TEST
EXECUTION_MODE: ATTACK
Attack timeout before commit, timeout after commit, partial transaction fixture, unknown external consequence, stale/revoked authority, stale Evidence, duplicate retry, blind retry after INDETERMINATE, admin recovery, latest-row recovery, Event-replay recovery and backup-like stale state fixture. Prove RECOVERY != AUTHORITY, LPVS != LATEST, INDETERMINATE != FAILED, RETRY != REPLAY. Do not invent recovery authority.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_AI_AUTHORITY_COUNTER_TEST
```text
PROMPT_AI_AUTHORITY_COUNTER_TEST
EXECUTION_MODE: ATTACK
Attack AI output DECIDED, AI QuestionSelection, AI HABB mutation, AI Evidence truth promotion, AI citation auto-support, AI confidence as Evidence, prompt grants authority, retrieved text grants authority, tool access treated as authority, provider output directly persisted canonical, Gateway bypass and Human-only Burst invocation. Prove AI authority boundary from canonical/proof artifacts, not logs.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_HUMAN_DECISION_COUNTER_TEST
```text
PROMPT_HUMAN_DECISION_COUNTER_TEST
EXECUTION_MODE: ATTACK
Attack AI decides plus human approves, human click without Decision semantics, role-only Decision, Owner fallback, admin Decision, author Decision, stale DECISION_RIGHT, cross-Workspace Decision, unattributed Decision, Decision auto-executes action and recommendation persistence sets DECIDED.
Expected invariant: Human creates Decision under current explicit DECISION_RIGHT. Nothing else creates DECIDED. DECIDED alone creates no downstream consequence.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_COMMITUNIT_COUNTER_TEST
```text
PROMPT_COMMITUNIT_COUNTER_TEST
EXECUTION_MODE: ATTACK
Test fresh/revoked authority, fresh/stale state, fresh/stale Evidence, duplicate idempotency, concurrent Command, audit failure, outbox failure, before-commit disconnect, after-commit disconnect, DB error and unknown commit result.
For every run reconstruct Command, Attempt, BoundaryProof, BND-014, CommitUnit, canonical versions, AuditEvent, Outbox, idempotency, outcome and certainty. Exception alone never determines outcome.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_WORKSPACE_ISOLATION_COUNTER_TEST
```text
PROMPT_WORKSPACE_ISOLATION_COUNTER_TEST
EXECUTION_MODE: ATTACK
Create Workspace A and B with NON_PROOF fixture status explicit. Attempt cross-reference at membership, HABB, Challenge, Session, Question, Question lineage, Burst membership, QuestionSelection, Decision, Evidence, ClaimAnchor, EvidenceRelation, AI context, Command target and projection. Test application semantic enforcement and DB/RLS enforcement separately. Fixture does not prove bootstrap legitimacy.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_RECURSIVE_TRACE
```text
PROMPT_RECURSIVE_TRACE
EXECUTION_MODE: RECONSTRUCT
Input one canonical consequence ID. Reconstruct backwards:
resulting canonical state <- CommitUnit <- Command <- Attempt <- BND-014 <- boundary chain <- Evidence <- human Decision <- authority <- HABB <- membership <- actor <- prior state.
Then reconstruct forward again. Use authoritative records only. If backward and forward reconstruction do not converge on the same legitimate state: TRACE_FAIL. Otherwise TRACE_PASS. Missing required proof is not inferred.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_RESUME_AFTER_INTERRUPTION
```text
PROMPT_RESUME_AFTER_INTERRUPTION
EXECUTION_MODE: RECONSTRUCT
Do not trust chat memory. Read git status, git diff, package completion reports, test results, migration state, architecture 00-15 and package DAG. Determine LAST_ACCEPTED_PACKAGE, CURRENT_INCOMPLETE_PACKAGE, SAFE_RESUME_POINT, TESTS_TO_RERUN, HUMAN_GATE_STATE. Do not edit until safe resume point is proven. If ambiguous, STOP.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_ARCHITECTURAL_BUGFIX
```text
PROMPT_ARCHITECTURAL_BUGFIX
EXECUTION_MODE: EXTEND + VERIFY
Input failing test or defect. Trace failure -> proof claim -> package -> implementation -> architecture source. Fix only an implementation defect inside already-authorized scope. If source contradiction or undefined semantic appears, STOP. After fix run targeted test, novel counter-test, recursive regression, diff audit and proof reconstruction. Do not weaken test.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

### PROMPT_ARCHITECTURE_CHANGE_REQUEST_ANALYSIS
```text
PROMPT_ARCHITECTURE_CHANGE_REQUEST_ANALYSIS
EXECUTION_MODE: REPORT
Do not modify code. Given requested behavior, trace architecture 00-15, identify first authoritative layer requiring change, affected downstream architecture, packages, tests, migrations and P claims, and whether baseline reconstruction would be required. Return impact map for human decision. Do not propose a local implementation workaround.

DO NOT OPTIMIZE AWAY SEMANTIC SEPARATION.
DO NOT RENAME ARCHITECTURAL CONCEPTS FOR CONVENIENCE.
DO NOT SUBSTITUTE FRAMEWORK CONVENTION FOR SOURCE SEMANTICS.
DO NOT INFER AUTHORITY.
DO NOT INFER EVIDENCE SUFFICIENCY.
DO NOT INFER RECOVERY RIGHTS.
DO NOT INFER EXPORT RIGHTS.
DO NOT CLOSE HARD DEPENDENCIES.
DO NOT WEAKEN TESTS TO FIT CODE.
DO NOT CHANGE UPSTREAM ARCHITECTURE.
STOP ON CONTRADICTION.
STOP.
```

## 6. NQUIRY_CODEX_RUNBOOK
```text
NQUIRY_CODEX_RUNBOOK
PACKAGE STATUS: NOT_STARTED | AUTHORIZED | IN_PROGRESS | PACKAGE_PASS | PACKAGE_FAIL_IMPLEMENTATION | PACKAGE_BLOCKED_UPSTREAM | PACKAGE_BLOCKED_PREDECESSOR | PACKAGE_INCONCLUSIVE_ENVIRONMENT | ARCHITECTURE_CONTRADICTION
PHASE STATUS: NOT_STARTED | IN_PROGRESS | READY_FOR_HUMAN_REVIEW | HUMAN_APPROVED | BLOCKED

PRECHECK
PKG-00
PACKAGE REPORT
PHASE 0 GATE

PKG-01
PKG-02
PKG-03
PKG-04
PHASE 1 GATE

PKG-05
PKG-06
PKG-07
PHASE 2 GATE

PKG-08
PKG-09
PHASE 3 GATE

PKG-10
PKG-11
PKG-12
PKG-13
PHASE 4 GATE

PKG-14
PKG-15
PHASE 5 GATE

PKG-16
PKG-17
PHASE 6 GATE

PKG-18
PKG-19
PHASE 7 GATE

PKG-20
PKG-21
PHASE 8 GATE

PKG-22
PKG-23
PKG-24
PHASE 9 GATE

PKG-25
PKG-26
PKG-27
PHASE 10 GATE

PKG-28
PKG-29
PHASE 11 GATE

PKG-30
PHASE 12 GATE

PKG-31
PHASE 13 GATE

PKG-32
PHASE 14 GATE

FINAL PROOF REPORT
STOP.

No phase becomes HUMAN_APPROVED automatically.
HARD-DEP-001 and HARD-DEP-002 remain explicit.
Do not build 16.
```

## 7. P-01 through P-25 execution tracking matrix

`P-01` -> PKG-06, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-02` -> PKG-06, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-03` -> PKG-07, PKG-09, PKG-28, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-04` -> PKG-07, PKG-09, PKG-19, PKG-28, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-05` -> PKG-18, PKG-19, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-06` -> PKG-18, PKG-19, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-07` -> PKG-15, PKG-18, PKG-19, PKG-29, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-08` -> PKG-14, PKG-29, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-09` -> PKG-15, PKG-29, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-10` -> PKG-02, PKG-03, PKG-09, PKG-13, PKG-15, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-11` -> PKG-02, PKG-03, PKG-13, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-12` -> PKG-02, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-13` -> PKG-08, PKG-09, PKG-13, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-14` -> PKG-16, PKG-17, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-15` -> PKG-16, PKG-17, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-16` -> PKG-10, PKG-12, PKG-20, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-17` -> PKG-20, PKG-21, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-18` -> PKG-00, PKG-13, PKG-25, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-19` -> PKG-10, PKG-11, PKG-13, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-20` -> PKG-11, PKG-22, PKG-23, PKG-24, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-21` -> PKG-23, PKG-24, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-22` -> PKG-01, PKG-09, PKG-25, PKG-26, PKG-28, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-23` -> PKG-00, PKG-19, PKG-25, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-24` -> PKG-00, PKG-03, PKG-25, PKG-26, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

`P-25` -> PKG-01, PKG-05, PKG-12, PKG-13, PKG-17, PKG-22, PKG-27, PKG-30, PKG-31, PKG-32. PKG-32 must report implementation location, test location, attack, expected defense, actual proof and status.

## 8. Final falsification of 15 itself

TEST A, PKG-13 ISOLATION: CommitCoordinator/BND-014 prompt must provide current authority, transaction sequence, failure injection, certainty, tests and proof without invention.

TEST B, PKG-15 ISOLATION: AI-decision-plus-human-approval must not satisfy the prompt. Human creates the Decision under current DECISION_RIGHT.

TEST C, PKG-19: Real Workspace data cannot be sent to a real provider while HARD-DEP-002 remains unresolved.

TEST D, PKG-24: Recovery cannot establish a state that was never legitimate.

TEST E, PKG-26: DB admin or technical service identity cannot become domain authority.

TEST F, ORDINARY PACKAGE: Every prompt specifies what to read, build, where to build, what not to touch, semantics, tests, attacks, regressions, proof, stop and report.

TEST G: Tests cannot be weakened to make code green without diff audit/mutation review detecting it.

TEST H: No package self-authorizes successor phase.

TEST I: TestProofBundle collects proof and cannot manufacture legitimacy.

TEST J: NonProofWorkspaceBootstrap and MockProviderAdapter cannot establish production acceptance.

`FINAL_FALSIFICATION_15::PASS`

## 9. Recursive validation against 14

For every package:

`14 PACKAGE -> 15 PROMPT -> FILES -> IMPLEMENTATION TASKS -> TESTS -> ATTACKS -> PROOF -> STOP CONDITIONS -> REPORT`

Inverse validation:

`15 CODING TASK -> EXACT 14 IMPLEMENTATION REQUIREMENT`

No orphan implementation task. No orphan 14 package. No new semantic branch.

## 10. Completion report

`DOCUMENT_VERDICT::READY_FOR_HUMAN_REVIEW`
`PACKAGE_PROMPTS_CREATED::33`
`PHASE_GATE_PROMPTS_CREATED::15`
`REUSABLE_PROMPTS_CREATED::14`
`PRECHECK_PROMPT_CREATED::YES`
`RESUME_PROMPT_CREATED::YES`
`BUGFIX_PROMPT_CREATED::YES`
`CHANGE_ANALYSIS_PROMPT_CREATED::YES`
`RUNBOOK_CREATED::YES`
`PACKAGE_DAG_PRESERVED::YES`
`ALL_14_PACKAGES_MAPPED::YES`
`ALL_14_FILE_MAPS_REFERENCED::YES`
`ALL_DATABASE_MIGRATIONS_MAPPED::YES`
`ALL_API_SURFACES_MAPPED::BY_REFERENCE_TO_14_AND_PACKAGE_SCOPE`
`ALL_P01_P25_CLAIMS_MAPPED::YES`
`ALL_CRITICAL_PACKAGES_HAVE_RED_TEAM_REQUIREMENTS::YES`
`ALL_PACKAGES_HAVE_COUNTER_TESTS::YES`
`ALL_PACKAGES_HAVE_RECURSIVE_REGRESSION::YES`
`ALL_PACKAGES_HAVE_DIFF_AUDIT::YES`
`ALL_PACKAGES_HAVE_ARCHITECTURE_RECONSTRUCTION_CHECK::YES`
`ALL_PACKAGES_HAVE_STOP_CONDITIONS::YES`
`HARD_DEP_001_PRESERVED::YES`
`HARD_DEP_002_PRESERVED::YES`
`GAP_14_001_PRESERVED::YES`
`GAP_14_002_PRESERVED::YES`
`GAP_14_003_PRESERVED::YES`
`GAP_14_004_PRESERVED::YES`
`GAP_14_005_PRESERVED::YES`
`NEW_GAPS_FOUND::NONE_REQUIRED_TO_GENERATE_15`
`READY_FOR_CODEX_EXECUTION::CONDITIONALLY_YES_AFTER_HUMAN_APPROVAL_OF_15_AND_PER_PACKAGE_AUTHORIZATION`
`READY_FOR_16_DECISION_GAP_REGISTER::NOT_AUTHORIZED_BY_THIS DOCUMENT`

## 11. Final stop gate

`15_COMPLETE::YES`
`16_GENERATED::NO`
`PKG_00_IMPLEMENTED::NO`
`APPLICATION_CODE_WRITTEN::NO`
`UPSTREAM_GAPS_RESOLVED::NO`
`ARCHITECTURE_BASELINE_FROZEN::NO`
`HUMAN_REVIEW_REQUIRED::YES`

STOP.
