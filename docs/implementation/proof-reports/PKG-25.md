# PKG-25 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-25
PACKAGE_TITLE: Service identity and DB principals
BUILD_PHASE: 10
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  11_SECURITY_PRIVACY_OBSERVABILITY.md section 8 ("Service Identity" --
    AC-11-003: "Service identity proves which technical principal
    called. It does not prove that the requested domain consequence is
    authorized"), section 9 (SYSTEM_SERVICE and SYSTEM_DERIVED remain
    separate), section 10 (AI_PROCESSOR separation -- "cannot... write
    authority-bearing canonical state"), section 14 ("Canonical Write
    Protection" -- AC-11-005: the exact list of components that do NOT
    receive canonical write capability -- frontend, AI processor,
    background worker, event consumer, external integration adapter,
    analytics service, projection service, observability service,
    model provider, AI tool), section 15 ("Canonical Database Privilege
    Architecture" -- the 4 conceptual principal categories
    CANONICAL_READER/CANONICAL_COMMIT_WRITER/MIGRATION_PRINCIPAL/
    BACKUP_PRINCIPAL; "No principal name itself creates semantic
    permission... Database-level permission is a necessary
    infrastructure capability for the approved path. It is never
    sufficient legitimacy"), section 35 ("Audit Mutation Control" --
    "Ordinary application principals cannot rewrite established audit
    history"), section 83 ("Canonical Write Enforcement Implementation
    Dependency" -- "Potential mechanisms may include database
    principals... 11 does not prescribe a specific stack")
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md's T9 row ("SECURITY /
    ISOLATION TEST -- Workspace isolation, identity, direct-write and
    gateway controls... Two Workspaces, service principals... Technical
    bypass blocked/detected"), the P-18/P-22/P-23/P-24 rows
  14_IMPLEMENTATION_SEQUENCE.md section 9's own migration-bucket table
    (`012_security_events_rls`: "security_events, RLS/policies/grants |
    prior protected tables | isolation/privilege tests"), section 10
    (repository ports -- confirms which repositories are read-only vs.
    governed-mutation-only as of PKG-24), the repository-topology table
    row for `packages/security/identity.py` ("human/service identity |
    11 | semantic_types | domain authority | ... | 10"), PKG-25's own
    package manifest (BUILD_PHASE 10, OBJECTIVE, REQUIRED PREDECESSORS
    PKG-13/PKG-19/PKG-21/PKG-24, DATABASE_CHANGES 012, PROOF_CLAIMS
    P-18/P-22/P-23/P-24)
  16_DECISION_GAP_REGISTER.md's own P-18/P-22/P-23/P-24 rows (exact
    claim text and required-package lists, each naming PKG-25)

14_REQUIREMENTS_MATERIALIZED:
  The literal 9-principal list from 14's own PKG-25 OBJECTIVE
  (`migration_owner`, `api_reader`, `governed_commit_writer`,
  `ai_gateway_writer`, `projection_writer`, `recovery_reader`,
  `security_event_writer`, `audit_reader`, `test_principal`), each as a
  real, LOGIN-capable, NON-superuser local PostgreSQL role
  (`infra/local/db_roles.sql`). Migration `012`'s own "principal/grant
  definitions only" half (`2feb99a01f9d_service_identity_db_principals.py`
  -- the `security_events` table itself and its RLS policies are
  PKG-26's own later revision in the same bucket). The "security
  capability map" PUBLIC INTERFACE
  (`packages.security.identity.SECURITY_CAPABILITY_MAP`). Real local
  PostgreSQL privilege tests (T9,
  `tests/security/test_db_principals.py`), not simulated ones.

PREDECESSORS_VERIFIED:
  PKG-13 (a579e80, PACKAGE_PASS, CRITICAL -- Commit coordinator and
    BND-014; `governed_commit_writer`'s own table set is exactly the
    tables `CommitCoordinator`'s own real callers write through).
  PKG-19 (93f2816, PACKAGE_PASS -- AI Gateway and MockProvider;
    `ai_gateway_writer`'s own table set is exactly
    `packages/persistence/ai_record_repository.py`'s own real write
    surface).
  PKG-21 (3b0697c, PACKAGE_PASS -- Projection and replay;
    `projection_writer`'s own table set is exactly
    `packages/persistence/projection_repository.py`'s own real write
    surface).
  PKG-24 (45ce69f, PACKAGE_PASS, CRITICAL -- BND-017/BND-018 and
    Recovery Command; `recovery_reader`'s own grant on
    `recovery_records` was explicitly disclosed as deferred to THIS
    package by PKG-24's own migration docstring).
  Full chain unbroken: PKG-00 dd4aad2 through PKG-24 45ce69f. No file
  outside this package's own new-file set was touched beyond the one
  disclosed predecessor extension point (see FILES_MODIFIED).

FILES_CREATED:
  infra/local/db_roles.sql
  migrations/versions/2feb99a01f9d_service_identity_db_principals.py
  tests/security/test_service_identity.py
  tests/security/test_db_principals.py

FILES_MODIFIED:
  packages/security/identity.py (PKG-01's own file -- extended, not
    replaced. PKG-01's own `AuthenticatedPrincipal`/`ExternalCredential`/
    `IdentityPort` are byte-for-byte unchanged; this package adds
    `ServicePrincipal`, `TableOperation`, `TableCapability`,
    `ALL_PROTECTED_TABLES`, `SECURITY_CAPABILITY_MAP`,
    `capability_tables`, `capability_operations`, plus a new module
    docstring section explaining each design decision. This is the
    exact "predecessor extension point explicitly exposed for PKG-25"
    PKG-01's own docstring itself already named: "Service identity...
    land in later phases (14 section 46: PKG-25/PKG-26, Phase 10)")

FILES_DELETED: none

MIGRATIONS_CREATED: 2feb99a01f9d (service_identity_db_principals),
  revises b7ec21429b53. Grants table-level SELECT/INSERT/UPDATE/DELETE
  (as applicable per principal) across the 31 tables that already exist
  as of head b7ec21429b53, to the 8 DML-capable principals, plus
  `CREATE ON SCHEMA public` for `migration_owner`. Also performs
  `REVOKE ALL ON SCHEMA public FROM PUBLIC` (defense-in-depth hardening
  -- proven load-bearing by MUT-PKG25-01, not merely asserted) followed
  by an explicit `GRANT USAGE ON SCHEMA public` to each of the 9
  principals. `security_event_writer`'s own role exists (created by
  `infra/local/db_roles.sql`) but receives no GRANT here -- its one
  target table, `security_events`, does not exist until PKG-26's own
  migration in this same `012` bucket. PRECONDITION, disclosed in the
  migration's own docstring: assumes `infra/local/db_roles.sql` has
  already created the 9 roles; a missing role raises a real
  `role "..." does not exist` Postgres error at apply time (fail
  technically, not silently). Applied live to a fresh compose
  PostgreSQL 17; downgrade(-1) then re-upgrade cycle verified (0 grants
  after downgrade, 231 grant rows restored identically after
  re-upgrade); `\d`/`information_schema.role_table_grants` inspected
  directly via `psql` and cross-checked row-for-row against
  `packages.security.identity.SECURITY_CAPABILITY_MAP` (see
  TARGETED_TEST_RESULTS).
SCHEMA_CHANGES: no table created, altered, or dropped -- GRANT/REVOKE
  only. No other migration touched.
DB_PRIVILEGE_CHANGES: the entire point of this package -- see
  MIGRATIONS_CREATED above and PROOF_ARTIFACTS below for the full,
  table-by-table live grant matrix.

PUBLIC_INTERFACES_CREATED:
  security.identity.{ServicePrincipal, TableOperation, TableCapability,
    ALL_PROTECTED_TABLES, SECURITY_CAPABILITY_MAP, capability_tables,
    capability_operations} -- 14's own literal PUBLIC INTERFACES:
    "security capability map".

COMMANDS_CREATED: NOT_APPLICABLE. 14 assigns no Command to this
  package -- its own scope is technical identity/privilege
  infrastructure, not a domain Command.
QUERIES_CREATED: NOT_APPLICABLE. `capability_tables`/
  `capability_operations` are plain Python lookups over a static map,
  never a canonical/governance-state Query.
EVENTS_CREATED: NOT_APPLICABLE. No Event contract assigned by 14 to
  this package.

BOUNDARIES_CREATED_OR_CHANGED: none (no `boundaries.BndNNN*` file
  created or modified). This package's own "boundary" is a DIFFERENT,
  technical kind -- the PostgreSQL GRANT/REVOKE system itself is the
  enforcement mechanism 11 section 83 explicitly allows ("Potential
  mechanisms may include database principals... 11 does not prescribe a
  specific stack"), verified for real rather than asserted (see
  TARGETED_TEST_RESULTS). "Technical privilege never replaces semantic
  boundaries" (this package's own BOUNDARIES line): every existing
  BND-001..018 evaluator remains fully in force, unmodified, and this
  package's own grants do not and cannot substitute for any of them --
  a `governed_commit_writer`-authenticated connection with a valid
  GRANT can still only write through code that itself still calls
  `evaluate_chain`/`CommitCoordinator`; DB permission is a NECESSARY,
  not SUFFICIENT, condition (11 section 15's own words).

AUTHORITY_PATH: No new Decision Right, `AuthorityClass` value,
  `AuthorityResolver` fallback, or Owner/Admin superpower was
  introduced -- this package's own NON_COLLAPSE_RULES line states it
  plainly: "SERVICE IDENTITY != SYSTEM_DERIVED AUTHORITY; DB CREDENTIAL
  != DOMAIN AUTHORITY; MIGRATION OWNER != RUNTIME ACTOR." Proven, not
  merely asserted: `migration_owner` -- the ONE principal among these 9
  with elevated schema (DDL) rights -- has ZERO row-level capability on
  any canonical table in `SECURITY_CAPABILITY_MAP`
  (`test_migration_owner_has_no_row_level_dml_capability_at_all`), and
  a live connection authenticated as it is denied a real `INSERT INTO
  decisions` even though it CAN create/drop an unrelated schema object
  (`test_migration_owner_can_create_schema_objects_but_never_write_domain_rows`)
  -- the mandatory package-specific attack "Decision write from
  admin-like technical identity", DENIED. P-24 ("Admin/root technical
  capability is not domain authority") is exercised directly by this
  proof, for the first time at the DB-principal layer (04/03's own
  authority/BND-005/014 path remains the ONLY separate proof for the
  application layer -- this package adds the infrastructure-layer
  half).
EVIDENCE_PATH: NOT_APPLICABLE. This package introduces no Evidence
  concept, no `EvidenceRepository` change, and no privilege-based
  Evidence trust -- 11 section 15's own text is exercised negatively
  here: DB-level permission (even `governed_commit_writer`'s own broad
  canonical-write grant) never substitutes for a real
  `resolve_evidence_set_freshness` check anywhere in this codebase; no
  such substitution was added.
AI_PATH: `ai_gateway_writer` is scoped to EXACTLY the 3 tables
  `packages/persistence/ai_record_repository.py` (PKG-18/19's own real
  writer) already writes -- `ai_generations`, `ai_derived_artifacts`,
  `ai_context_manifests` -- and to NOTHING else, proven live: a real
  connection authenticated as `ai_gateway_writer` is denied `INSERT
  INTO decisions`/`commands`/`commit_units`/`human_authority_bindings`
  (`test_ai_gateway_writer_cannot_write_canonical_domain_or_commit_tables`).
  This is the DB-permission-layer half of P-23 ("AI Gateway is
  exclusive provider path") -- the application-layer half (BND-009/010,
  Gateway-only invocation) remains PKG-19's own, unmodified, proof.
RECOVERY_PATH: `recovery_reader` is scoped to `recovery_records` only,
  with full CRUD (SELECT/INSERT/UPDATE -- the name is this package's
  own literal 14-assigned label, not a read-only constraint; see
  `security.identity`'s own "WHY recovery_reader GETS FULL CRUD"
  docstring section) -- matching `RecoveryService.resolve_recovery`'s
  own deliberately-separate-from-`CommitCoordinator` write path
  (PKG-24's own disclosed architectural decision). Proven live: a
  connection authenticated as `recovery_reader` can INSERT/UPDATE
  `recovery_records` but cannot even SELECT `decisions`/`commands`
  (`test_recovery_reader_is_scoped_to_recovery_records_only`).

TESTS_CREATED:
  tests/security/test_service_identity.py (12 tests -- pure Python,
    no database: exactly the 9 named principals exist; api_reader is
    SELECT-only on every one of the 31 protected tables;
    migration_owner/security_event_writer have zero row-level
    capability; ai_gateway_writer/projection_writer/recovery_reader are
    each structurally disjoint from governed_commit_writer's own table
    set; audit_reader is read-only; the 7 "no governed writer yet"
    tables receive no write grant from any principal except
    test_principal; test_principal has broad DML but `TableOperation`
    itself has no DDL member; fail-closed lookup defaults;
    `ALL_PROTECTED_TABLES` stays exhaustive against the map)
  tests/security/test_db_principals.py (11 tests -- real live
    PostgreSQL: no principal is a superuser/can create roles or
    databases; each of the 9 principals' own permitted case proven via
    `has_table_privilege` over a REAL connection authenticated as that
    principal, and its forbidden cross-scope case proven via a REAL
    denied DML/SELECT attempt; MUT-PKG25-01 guard-necessity proof for
    `REVOKE ALL FROM PUBLIC`)

TESTS_MODIFIED: none. First package since PKG-22/23 with zero modified
  test files -- PKG-01's own `tests/security/test_identity.py` was left
  completely untouched (its own `AuthenticatedPrincipal`/`IdentityPort`
  scope is unrelated to and unaffected by this package's additions to
  the SAME production file).

TARGETED_TEST_RESULTS:
  Pure-Python (no `DATABASE_URL`): 672 passed, 367 skipped (skips are
    the established `SKIPPED_NO_DATABASE` convention).
  Live PostgreSQL 17 (`DATABASE_URL=postgresql+psycopg://nquiry:
    nquiry_local_dev_only@localhost:15432/nquiry`), full suite
    (`tests/ apps/api/tests apps/worker`): 1039 passed, 1 skipped (the
    one pre-existing, unrelated, disclosed skip). Zero failures, zero
    new skips, zero regressions against PKG-24's own 1016-passed
    baseline (+23 new tests: 12 + 11).
  Direct `psql`/`information_schema.role_table_grants` inspection
    (independent of pytest): the live grant matrix was read back
    row-for-row after `upgrade head` and matches
    `SECURITY_CAPABILITY_MAP` exactly (231 grant rows total); after
    `downgrade -1`, 0 grant rows remain for these 9 principals; after
    re-`upgrade head`, 231 grant rows are restored identically.

NEGATIVE_TEST_RESULTS: every principal's own forbidden case (see
  ADVERSARIAL_TEST_RESULTS) is a designed-before-implementation negative
  test, asserting the REAL Postgres denial (`permission denied` /
  `does not exist`), never merely an application-layer mock or a
  private call count.

ADVERSARIAL_TEST_RESULTS:
  PRE_IMPLEMENTATION_ATTACK_MODEL category coverage: semantic-shortcut
  (3, below), authority/boundary-bypass (3, below), persistence/
  concurrency (NOT_APPLICABLE -- this package introduces no new
  concurrent-write path, only read/write GRANT boundaries on
  already-concurrency-proven tables), Workspace (NOT_APPLICABLE -- DB
  principals are not Workspace-scoped; Workspace isolation is BND-002's
  own semantic job, RLS-per-Workspace is PKG-26's own scope), AI-
  authority (2, below), failure/retry (NOT_APPLICABLE -- no retry/
  idempotency path in this package's own scope), projection/cache-truth
  (1, below).

  Mandatory (14/14, "for each principal attempt permitted and
  forbidden read/write" plus the 3 named package-specific attacks):
  1. ATTACK: api_reader attempts a canonical write
     EXPECTED DEFENSE: DB GRANT boundary -- no INSERT/UPDATE/DELETE
       privilege on any table
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY (technical, not a semantic
       BND -- see BOUNDARIES_CREATED_OR_CHANGED)
     EXPECTED CANONICAL RESULT: no canonical state change; real
       Postgres `permission denied` error
     EXPECTED PROOF ARTIFACT: `has_table_privilege` false + a real
       denied `INSERT` over a live connection
     ACTUAL RESULT: matches
       (test_api_reader_can_read_but_cannot_write_a_canonical_table)
  2. ATTACK: governed_commit_writer attempts to write an AI-Gateway,
       projection, or recovery table
     EXPECTED DEFENSE: DB GRANT boundary -- narrow to its own 17-table
       set, no broader
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY
     EXPECTED CANONICAL RESULT: real `permission denied`
     EXPECTED PROOF ARTIFACT: `has_table_privilege` false + denied
       `INSERT` on `ai_generations`/`recovery_records`
     ACTUAL RESULT: matches
       (test_governed_commit_writer_can_write_its_own_tables_but_not_ai_or_projection_or_recovery)
  3. ATTACK: "governance write from AI Gateway" -- ai_gateway_writer
       attempts `human_authority_bindings`/`decisions`
     EXPECTED DEFENSE: DB GRANT boundary -- scoped to exactly 3 AI
       tables
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY
     EXPECTED CANONICAL RESULT: real `permission denied`; P-23 further
       exercised at the DB layer
     EXPECTED PROOF ARTIFACT: `has_table_privilege` false + denied
       `INSERT` on `human_authority_bindings`
     ACTUAL RESULT: matches
       (test_ai_gateway_writer_cannot_write_canonical_domain_or_commit_tables)
  4. ATTACK: "attempt canonical write from projection" --
       projection_writer attempts `decisions`/`sessions`
     EXPECTED DEFENSE: DB GRANT boundary -- scoped to exactly 3
       read-model/checkpoint tables
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY
     EXPECTED CANONICAL RESULT: real `permission denied`; 11 section
       14's own explicit "projection service" exclusion proven, not
       merely asserted
     EXPECTED PROOF ARTIFACT: `has_table_privilege` false + denied
       `INSERT` on `decisions`
     ACTUAL RESULT: matches
       (test_projection_writer_cannot_write_a_canonical_write_table)
  5. ATTACK: recovery_reader attempts `decisions`/`commands`
     EXPECTED DEFENSE: DB GRANT boundary -- scoped to `recovery_records`
       only
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY
     EXPECTED CANONICAL RESULT: real `permission denied`
     EXPECTED PROOF ARTIFACT: `has_table_privilege` false + denied
       `SELECT` on `decisions`
     ACTUAL RESULT: matches
       (test_recovery_reader_is_scoped_to_recovery_records_only)
  6. ATTACK: audit_reader attempts to write `audit_events`, or to read
       an unrelated canonical table
     EXPECTED DEFENSE: DB GRANT boundary -- SELECT-only on exactly one
       table
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY
     EXPECTED CANONICAL RESULT: real `permission denied`; 11 section
       35's own "cannot rewrite established audit history" proven at
       the DB layer for the first time in this codebase
     EXPECTED PROOF ARTIFACT: `has_table_privilege` false for
       INSERT/UPDATE/DELETE + denied `INSERT`
     ACTUAL RESULT: matches
       (test_audit_reader_can_read_but_never_write_audit_events)
  7. ATTACK: security_event_writer attempts to read/write ANY existing
       table (its own target does not exist yet)
     EXPECTED DEFENSE: DB GRANT boundary -- zero table grants; schema
       `USAGE` alone is not sufficient to reach any table
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY
     EXPECTED CANONICAL RESULT: real `permission denied`
     EXPECTED PROOF ARTIFACT: `has_table_privilege` false + denied
       `SELECT` on `decisions` AND `audit_events`
     ACTUAL RESULT: matches
       (test_security_event_writer_has_no_table_access_at_all_yet)
  8. ATTACK: "Decision write from admin-like technical identity" --
       migration_owner attempts `INSERT INTO decisions`
     EXPECTED DEFENSE: DB GRANT boundary -- DDL rights never imply
       row-level DML rights
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY
     EXPECTED CANONICAL RESULT: real `permission denied`; P-24 further
       exercised at the DB-principal layer
     EXPECTED PROOF ARTIFACT: `has_table_privilege` false + denied
       `INSERT`, alongside a REAL, successful `CREATE TABLE`/`DROP
       TABLE` proving the DDL/DML asymmetry is real, not just an
       absence of any privilege at all
     ACTUAL RESULT: matches
       (test_migration_owner_can_create_schema_objects_but_never_write_domain_rows)
  9. ATTACK: any of the 9 principals is a Postgres superuser or can
       create roles/databases
     EXPECTED DEFENSE: 14's own literal "No runtime superuser"
       requirement
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY (role-attribute level)
     EXPECTED CANONICAL RESULT: `rolsuper`/`rolcreatedb`/
       `rolcreaterole`/`rolbypassrls` all false for all 9
     EXPECTED PROOF ARTIFACT: `pg_roles` row read directly
     ACTUAL RESULT: matches
       (test_all_nine_principals_exist_and_none_is_a_superuser_or_can_create_roles_or_databases)
  10-14. ATTACK: each remaining principal (api_reader,
       governed_commit_writer, ai_gateway_writer, projection_writer,
       audit_reader) attempts its OWN permitted operation
     EXPECTED DEFENSE: the grant exists and the operation succeeds
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY (positive control)
     EXPECTED CANONICAL RESULT: NOT_APPLICABLE (no canonical Command
       exists for this package; the positive proof is the grant itself,
       via `has_table_privilege`/a real successful DDL)
     EXPECTED PROOF ARTIFACT: `has_table_privilege` true for the
       principal's own table set
     ACTUAL RESULT: matches (positive assertions embedded in tests
       #1-8 above -- each test proves BOTH its own permitted and
       forbidden case together, per this package's own mandatory-attack
       phrasing "for each principal attempt permitted and forbidden
       read/write")

  Novel/adapted (>=5 required for this package; 9 delivered, 23 total):
  15. ATTACK: a capability-map row could be silently mutated (e.g.
        ai_gateway_writer's own table set widened to include a
        canonical table) without any structural test catching it
      ACTUAL RESULT: matches -- the isdisjoint/membership assertions in
        `tests/security/test_service_identity.py`
        (test_ai_gateway_writer_cannot_touch_any_governed_commit_writer_table,
        test_projection_writer_cannot_touch_any_canonical_write_table)
        would fail on any such widening; independently re-verified live
        against the actual database
  16. ATTACK: `SECURITY_CAPABILITY_MAP` and the migration's own literal
        SQL silently drift apart over time
      ACTUAL RESULT: matches -- `TARGETED_TEST_RESULTS`'s own direct
        `information_schema.role_table_grants` read-back, performed
        independently of pytest, confirms row-for-row identity; the two
        table lists (`security.identity`'s and the migration's own)
        were kept as two independently-typed literal tuples on purpose
        (see this module's own docstring: migrations never import
        application packages, an established, unbroken precedent since
        `001`) precisely so drift would be DETECTABLE, not silently
        masked by a single shared source
  17. ATTACK: a "no governed writer yet" table (e.g. `human_authority_bindings`)
        silently receives a write grant "just in case" a future package
        needs it
      ACTUAL RESULT: matches
        (test_no_governed_writer_yet_tables_receive_no_write_grant_from_any_principal)
        -- structurally enforced against all 9 principals except the
        disclosed `test_principal` NON_PROOF exception
  18. ATTACK: `TableOperation` is extended with a DDL-shaped member,
        letting a future edit accidentally grant CREATE/ALTER/DROP
        through the same table-keyed map `migration_owner` is
        deliberately excluded from
      ACTUAL RESULT: matches
        (test_test_principal_has_broad_dml_but_capability_map_names_no_ddl_verb
        asserts the exact 4-member `TableOperation` set)
  19. ATTACK: a lookup for a principal/table pair with no declared
        capability silently returns a default/inferred capability
        instead of failing closed
      ACTUAL RESULT: matches
        (test_capability_operations_returns_empty_for_an_unrelated_table)
  20. ATTACK: `ALL_PROTECTED_TABLES` silently omits a table that DOES
        appear somewhere in `SECURITY_CAPABILITY_MAP` (a drift in the
        OTHER direction from #16)
      ACTUAL RESULT: matches
        (test_all_protected_tables_is_exhaustive_against_the_capability_map)
  21. ATTACK: security_event_writer reads ANY table by virtue of
        Postgres's own historical `PUBLIC` schema defaults, never having
        needed an explicit grant of its own at all
      ACTUAL RESULT: matches
        (test_security_event_writer_has_no_table_access_at_all_yet --
        this role has literally nothing granted beyond schema `USAGE`,
        and still cannot reach a single table)
  22. ATTACK (MUT-PKG25-01, projection/cache-truth-adjacent guard-
        necessity category): is `REVOKE ALL ON SCHEMA public FROM
        PUBLIC` genuinely load-bearing, or would a brand-new role with
        ZERO explicit grants of its own (not even from this migration)
        already be blocked by something else?
      ACTUAL RESULT: matches
        (test_mut_pkg25_01_revoke_all_from_public_is_genuinely_load_bearing
        -- see MUTATION_TESTS)
  23. ATTACK: `test_principal`'s own broad NON_PROOF fixture power is
        mistaken for (or silently expanded into) a 10th named production
        principal with real application-layer callers
      ACTUAL RESULT: matches -- `test_principal` is exercised ONLY by
        this package's own new tests; no production `application`/
        `persistence` module references it anywhere (confirmed by
        `grep -r test_principal packages/` returning only
        `security/identity.py`'s own declaration)

MUTATION_TESTS:
  METHODOLOGY NOTE (same disclosed adaptation as PKG-24): this
  session's own auto-mode tool classifier denies temporarily weakening
  a real security control in place, even reverted immediately
  afterward. This package's own "mutation surface" is a live GRANT
  matrix, not application control flow, so the natural, permission-safe
  proof is a GUARD-NECESSITY test against real, unmodified production
  SQL/roles -- never a code or schema edit.

  MUT-PKG25-01: is the migration's own `REVOKE ALL ON SCHEMA public
    FROM PUBLIC` genuinely necessary, or would PostgreSQL's own default
    behavior already have blocked an ungranted role? A throwaway role
    created with NO grant statement of any kind (not even from this
    migration) is used to probe a real table -> expected: still denied,
    proving the explicit revoke (not mere absence of an accidental
    grant) is what closes this door. ACTUAL: confirmed
    (test_mut_pkg25_01_revoke_all_from_public_is_genuinely_load_bearing
    -- the probe role cannot even resolve the unqualified table name,
    reported as "does not exist" rather than merely "permission
    denied", since it also lacks schema `USAGE` -- an even stronger
    lockdown than the 9 named principals, each of which IS granted
    `USAGE`). INTERPRETATION: guard confirmed load-bearing, not a
    coincidence of this package's own specific grant list.
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TEST_RESULTS: `tests/security/test_db_principals.py`
  exercises the full real stack: PostgreSQL 17 role catalog (`pg_roles`)
  -> the real migration's own GRANT/REVOKE state
  (`information_schema.role_table_grants`) -> a genuine, separate
  network connection authenticated AS each of the 9 principals (never
  the superuser asking on another role's behalf) -> a real DML/DDL
  attempt against the real schema every prior package's own migrations
  built (PKG-01 through PKG-24's tables). No mock, no fake role, no
  simulated permission check anywhere in this file.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through
  PKG-24's tests) re-run alongside PKG-25's new tests, both without a
  live database (672 passed, 367 skipped) and against a real
  PostgreSQL 17 instance with all 18 migrations applied
  (`tests/ apps/api/tests apps/worker`: 1039 passed, 1 skipped). Zero
  regressions; every previously-green test remains green, including
  PKG-01's own `tests/security/test_identity.py` (untouched, still
  passing against the extended production file).

P_CLAIMS_TESTED:
  P-18 (Direct canonical persistence is not legitimate app write path):
    substantially exercised for the first time at the DB-PRINCIPAL
    layer -- `api_reader` (the closest analogue to an "application
    principal" among these 9) is proven, live, to have zero write
    capability on any canonical table; PKG-13's own application-layer
    proof (governed Command path is the only route to a canonical
    mutation) remains the primary, unmodified proof for this claim.
  P-22 (Workspace isolation blocks cross-Workspace protected-data use):
    NOT directly exercised by this package -- DB principals in this
    prototype are not themselves Workspace-scoped (RLS-per-Workspace,
    which WOULD make this direct, is explicitly PKG-26's own scope,
    "RLS and SecurityEvents"). 14 still assigns P-22 to this package
    because BND-002 + the now-real privilege separation are
    complementary layers of the SAME isolation law (11 section 13); the
    Workspace-specific half remains `SUCCESSOR_NOT_BUILT` here,
    disclosed, not fabricated.
  P-23 (AI Gateway is exclusive provider path): substantially exercised
    at the DB-principal layer for the first time -- `ai_gateway_writer`
    is proven, live, to be unable to reach any canonical/commit/
    governance table, closing the "what if the Gateway process itself
    is compromised or misconfigured" half of this claim that PKG-19's
    own application-layer Gateway-only-invocation proof does not cover.
  P-24 (Admin/root technical capability is not domain authority): fully
    exercised at the DB-principal layer for the first time --
    `migration_owner`'s own elevated DDL rights are proven, live,
    incapable of any row-level canonical write, the mandatory
    "Decision write from admin-like technical identity" attack, DENIED.

PROOF_ARTIFACTS:
  - 1039-test live-database pass (0 regressions against PKG-24's own
    1016-passed baseline), including 23 distinct adversarial proofs (14
    mandatory + 9 novel/adapted) and 1 guard-necessity mutation proof
  - 9 real, non-superuser PostgreSQL roles, each verified via `pg_roles`
    to have `rolsuper = rolcreatedb = rolcreaterole = rolbypassrls =
    false`
  - A complete, live `information_schema.role_table_grants` matrix (231
    rows) matching `SECURITY_CAPABILITY_MAP` exactly, re-verified
    identical after a downgrade(-1)/re-upgrade cycle
  - 9 real, separate network connections (one per principal), each
    proving its OWN permitted operation via `has_table_privilege` and
    its cross-scope forbidden operation via a genuine denied DML/SELECT
    attempt at the PostgreSQL protocol level
  - A real `CREATE TABLE`/`DROP TABLE` executed and rolled back cleanly
    as `migration_owner`, proving its DDL capability is real (not a
    universal deny) while its row-level DML remains fully denied
  - A real, cleanly-cleaned-up throwaway role with zero grants, proving
    `REVOKE ALL FROM PUBLIC` is load-bearing (MUT-PKG25-01)
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output, including a full upgrade to head 2feb99a01f9d,
    a downgrade(-1)/re-upgrade cycle, and direct `psql` grant inspection
  - Diff audit (inline answers below), cross-checked against `git
    status --short` before staging per this session's own standing
    instruction

FORBIDDEN_DEPENDENCY_CHECK: PASS. Zero new extension needed --
  `packages/security/identity.py`'s own allow-list (`{"semantic_types"}`)
  has been sufficient since PKG-00's own skeleton; nothing this package
  adds imports anything beyond the Python standard library
  (`dataclasses`, `enum`).
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT:
  New semantic type/enum value: `ServicePrincipal` (9 values) and
    `TableOperation` (4 values) are both this package's own disclosed
    `[IMPLEMENTATION CHOICE]` shapes for materializing 14's own literal
    9-principal list and the 4 DML verbs `information_schema` itself
    reports -- not domain vocabularies 00-10 claim to close, and not
    Decision Rights, authority classes, or Recovery/Boundary outcomes.
  New transition: none -- no state machine, no `result`/`status`
    column anywhere in this package's own scope.
  New authority path: none -- see AUTHORITY_PATH above; this is a
    package whose entire OBJECTIVE requires proving the ABSENCE of a
    new authority path at the DB-principal layer, symmetrical to how
    PKG-23 proved the absence of one for Recovery.
  New DB write path: none for any CANONICAL table -- every DML grant
    given here targets a table a real, already-merged repository
    ALREADY writes to (PKG-10 through PKG-24's own migrations); this
    package only narrows WHICH connection identity may exercise an
    ALREADY-EXISTING write path, it does not add a new one.
  Weakened boundary: none -- no BND-001..018 evaluator touched. The
    mutation-testing methodology adaptation (guard-necessity proof
    instead of an in-place source edit) is the same disclosed tooling
    change PKG-24 first encountered, not a weakening of anything
    shipped.
  Easier test / removed negative test / admin shortcut / projection or
    cache truth / AI canonical authority / broader Workspace scope:
    none. If anything, this package NARROWS existing implicit access
    (the pre-existing `nquiry` bootstrap credential's own scope is
    unchanged and out of this package's reach, but every one of the 9
    NEW principals is strictly narrower than that credential ever was).
  Changed migration semantics: none -- no prior migration edited, only
    a new, purely additive `GRANT`/`REVOKE` migration.
  Files touched outside this package's own new-file set:
    `packages/security/identity.py` only -- explicitly the one
    predecessor extension point PKG-01's own docstring already named
    for this exact package. No other predecessor file touched. No
    previously-green test required a fix. No production bug was found
    this package -- every new test passed on its first run, pure and
    live-DB alike.
  `git status --short` immediately before staging matched this section
    exactly: 1 modified file
    (`packages/security/identity.py`) plus 4 new files
    (`infra/local/db_roles.sql`,
    `migrations/versions/2feb99a01f9d_service_identity_db_principals.py`,
    `tests/security/test_service_identity.py`,
    `tests/security/test_db_principals.py`), nothing else, no tooling/
    lock files.

ARCHITECTURE_RECONSTRUCTION_RESULT:
  This package participates in NO single consequential request path of
  its own -- 14 assigns it no Command, Query, or Boundary. Its own
  longest legitimate "chain" is infrastructural, not domain-shaped:
  DB CONNECTION AUTHENTICATION (a real service process connects using
  ONE of the 9 named principals' own credentials) -> DB-GRANT BOUNDARY
  (PostgreSQL itself checks the connection's own privilege before any
  statement executes) -> [the ALREADY-EXISTING, unmodified governed
  path for whichever table was targeted -- BND-001..018 ->
  `CommitCoordinator`/`RecoveryService`/`ProjectionWorker`/`AiRecordRepository`,
  each exactly as PKG-09 through PKG-24 already built and proved] ->
  RESULTING STATE (unchanged by this package). REQUEST -> ACTOR ->
  WORKSPACE -> CURRENT STATE -> CURRENT GOVERNANCE -> CURRENT AUTHORITY
  -> HUMAN DECISION -> EVIDENCE -> BOUNDARIES -> BND-014 -> COMMAND ->
  COMMIT UNIT -> CANONICAL MUTATION -> AUDIT -> OUTBOX -> EVENT ->
  RESULTING STATE: every one of these nodes is `NOT_APPLICABLE` for
  THIS package's own direct scope (it is a cross-cutting infrastructure
  layer BENEATH all of them, not a node ON that chain) -- each remains
  exactly as thoroughly reconstructed and proven by the package that
  actually owns it (PKG-01 through PKG-24). What THIS package adds and
  proves is a NEW, orthogonal dimension: which technical identity is
  even PERMITTED to attempt the write that reaches that chain at all.

KNOWN_LIMITATIONS:
  - No production code in this repository has been wired to actually
    CONNECT as any of these 9 new principals yet -- every existing
    application/worker/test process still connects via the
    pre-existing bootstrap `nquiry` superuser credential
    (`docker-compose.yml`'s own `POSTGRES_USER`). This package proves
    the MECHANISM (the principals exist, are correctly scoped, are
    verifiably non-superuser) exactly as PKG-13/16/17 each proved a
    generic engine before any concrete production caller existed --
    wiring `apps/api`/`apps/worker`'s own runtime `DATABASE_URL` per
    process to its own scoped principal remains `SUCCESSOR_NOT_BUILT`,
    disclosed, not fabricated.
  - `migration_owner` does NOT own the 31 pre-existing tables (all
    still owned by the bootstrap `nquiry` role) -- reassigning
    ownership of every existing object was judged out of this
    package's own narrow scope (a large, disclosed, disruptive
    operation touching every prior package's own migration lineage,
    not required by "Runtime technical identities and privilege
    separation"). Alembic itself continues to run via the existing
    `nquiry` connection for now.
  - `BACKUP_PRINCIPAL` (11 section 15's own 4th conceptual category) is
    not among 14's own literal 9-name list for this package and was
    not built -- no backup/restore tooling exists in this prototype at
    all yet.
  - `security_event_writer`'s own one GRANT (on `security_events`)
    remains deferred to PKG-26's own migration, disclosed, matching the
    identical pattern `recovery_reader` itself already followed one
    package earlier.
  - The `record_version` staleness gap PKG-24 disclosed
    (`RecoveryService.resolve_recovery`'s own guard has no independent
    DB-layer enforcement) is UNCHANGED by this package -- `recovery_reader`'s
    own grant does not add or remove any row-level version check; that
    limitation remains open, owned by PKG-24's own report.
  - Sandbox Python remains 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still
  BLOCKED. Neither is touched by this package's own scope.

NEW_GAPS_DISCOVERED:
  1. No production process is wired to any of the 9 new principals yet
     (see KNOWN_LIMITATIONS) -- a genuine, disclosed integration gap
     for a future package (or an infra-only follow-up) to close.
  2. `migration_owner` does not yet own the pre-existing schema objects
     (see KNOWN_LIMITATIONS) -- disclosed, deliberately out of this
     package's own narrow blast radius.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. `ServicePrincipal`'s 9
  values are 14's own literal, verbatim OBJECTIVE-line list --
  transcribed, not invented. `TableOperation`'s 4 values are
  PostgreSQL's own `information_schema` privilege vocabulary, not a
  domain concept. Every table -> principal assignment in
  `SECURITY_CAPABILITY_MAP` was derived by tracing real, already-merged
  repository code (`grep`-verified INSERT/UPDATE/DELETE call sites),
  never guessed at a plausible-looking future architecture -- see
  `security.identity`'s own "WHY THIS CAPABILITY MAP IS CODE-GROUNDED"
  docstring section. No new Decision Right, authority class, Command,
  Query, Event, Boundary, or canonical write PATH was introduced --
  only a narrower technical GATE on paths every one of PKG-09 through
  PKG-24 already built and proved.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-26 becomes DAG-eligible once its own
  required predecessors are verified. Eligibility is not authorization.
HUMAN_GATE_REQUIRED: YES -- 14 PKG-25's own coding prompt: "Respect the
  phase boundary. Package completion does not authorize the next
  phase." Do not authorize PKG-26 without explicit human authorization
  naming the package and this package's own commit hash.
```
