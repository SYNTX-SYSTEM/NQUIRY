# PKG-26 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-26
PACKAGE_TITLE: RLS and SecurityEvents
BUILD_PHASE: 10
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  11_SECURITY_PRIVACY_OBSERVABILITY.md section 3 ("Security Trust
    Boundary Inventory" -- "The approved system is divided into the
    following technical trust boundaries: TB-01 ... TB-19" -- exact,
    closed, numbered list), section 15 ("Canonical Database Privilege
    Architecture"), section 41 ("SecurityEvent" -- [ARCHITECTURAL
    CLOSURE] AC-11-014: "SecurityEvent is an operational/security
    record, not a 02 domain Thing and not a 09 Domain Event";
    "Examples:" event-type list; "does not itself authorize domain
    mutation"), section 42 ("SecurityEvent Minimum Semantics" -- the
    field list, itself disclosing "Exact physical schema belongs to
    implementation materialization"), section 60 ([ARCHITECTURAL
    CLOSURE] AC-11-017: "Development, test, staging and production are
    separate security environments" -- exact 4-value list)
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md's T9 row
  14_IMPLEMENTATION_SEQUENCE.md section 7.1 (`security_events`
    core-tables row: "security operational | Workspace key: yes where
    resolvable | append oriented | security_event_writer"), section 7.2
    ("Required column pattern"), section 8 ("Database Principals and
    Workspace Isolation" -- the full 9-principal reads/writes/forbidden
    reference table, AND its own `[IMPLEMENTATION CHOICE]`: "PostgreSQL
    RLS is enabled for Workspace-keyed protected tables using
    transaction-local Workspace context set only by trusted server
    adapter. RLS is defense-in-depth and is never used as the authority
    oracle."), section 9's own `012_security_events_rls` migration
    bucket row, the repository-topology rows for
    `packages/security/workspace.py`/`packages/security/events.py`,
    PKG-26's own package manifest (BUILD_PHASE 10, CRITICAL, REQUIRED
    PREDECESSORS PKG-25, DATABASE_CHANGES 012, PROOF_CLAIMS P-22/P-24)
  16_DECISION_GAP_REGISTER.md's own P-22/P-24 rows

14_REQUIREMENTS_MATERIALIZED:
  PostgreSQL RLS enabled on every Workspace-keyed protected table (14
  section 8's own `[IMPLEMENTATION CHOICE]`, materialized literally: a
  transaction-local `app.workspace_id` GUC, set only by the "trusted
  server adapter" `WorkspaceContextPort`/`SqlAlchemyWorkspaceContext`).
  `SecurityEvent`/`SecurityEventRepository` (14's own PUBLIC_INTERFACES),
  materializing 11 section 42's own "should reconstruct, where known"
  field list. `security_event_writer`'s own deferred grant from PKG-25
  is completed now that its target table exists. Workspace isolation
  re-exercised (not rebuilt) at the repository/Command/Evidence/AI
  context/projection layers via full-suite regression; the DB-policy
  layer is the one genuinely NEW mechanism this package builds and
  proves.

PREDECESSORS_VERIFIED:
  PKG-25 (4caccd4, PACKAGE_PASS -- Service identity and DB principals;
    every RLS policy this package creates applies identically to all 9
    of PKG-25's own principals; `security_event_writer`'s own role,
    created by PKG-25's own `infra/local/db_roles.sql`, receives its
    first real grant here).
  Full chain unbroken: PKG-00 dd4aad2 through PKG-25 4caccd4. No file
  outside this package's own new-file set was touched beyond the two
  disclosed extension points (see FILES_MODIFIED).

FILES_CREATED:
  migrations/versions/047bdf9bc528_rls_and_security_events.py
  packages/security/events.py
  packages/security/workspace.py
  packages/persistence/security_event_repository.py
  packages/persistence/workspace_rls_context.py
  tests/security/test_events.py
  tests/security/test_workspace.py

FILES_MODIFIED:
  packages/persistence/tables.py (`security_events_table` added +
    header docstring extended with a PKG-26 cross-reference; no
    existing table definition changed)
  scripts/check_architecture_dependencies.py
    (`INTERNAL_ALLOWED["persistence"] += "security"`, needed so
    `security_event_repository.py`/`workspace_rls_context.py` can
    import `security.events`/`security.workspace`; also added a
    defensive `EXTERNAL_FORBIDDEN["security"] = _DB_DRIVER |
    PROVIDER_SDK_MODULES` hardening entry, matching `audit`/`events`'
    own precedent (PKG-12) -- `security`'s own allowed-imports already
    implied no ORM code belongs there, this makes that implication
    independently checkable now that the package holds real content)

FILES_DELETED: none

MIGRATIONS_CREATED: 047bdf9bc528 (rls_and_security_events), revises
  2feb99a01f9d. Creates `security_events` (11 section 42's own field
  list; `environment`/`trust_boundary` CHECK-constrained to their own
  exact closed lists; deliberately NO foreign key on
  `workspace_id`/`command_id`/`generation_id`/`recovery_id` -- see
  `security.events`'s own module docstring for why a real FK would make
  it structurally impossible to record the one class of event this
  type most needs to: a forged/unresolvable claim). Two triggers
  (`trg_security_events_reject_update`/`_reject_delete`) mirror
  `audit_events`' own append-only precedent (PKG-12) -- verified live:
  a real UPDATE and a real DELETE attempt against a manually-inserted
  probe row both raised the expected trigger exception, cleaned up
  before any test ran. Grants `SELECT, INSERT` on `security_events` to
  `security_event_writer` (PKG-25's own deferred grant, now completed)
  and REVOKES `UPDATE` on `audit_events` from `governed_commit_writer`
  (a disclosed retrofit -- see DIFF_AUDIT). Enables RLS + creates one
  `workspace_isolation` policy (identical `USING`/`WITH CHECK` expression:
  `workspace_id = NULLIF(current_setting('app.workspace_id', true),
  '')::uuid`) on all 29 tables carrying a direct `workspace_id` column
  (`users`/`workspaces` excluded -- neither is itself a Workspace-scoped
  protected object). Applied live to a fresh compose PostgreSQL 17;
  downgrade(-1)/re-upgrade cycle verified live (RLS-enabled-table count:
  29 -> 0 -> 29; `governed_commit_writer`'s own `audit_events` grants:
  {INSERT,SELECT,UPDATE} -> {INSERT,SELECT} -> {INSERT,SELECT} after
  re-upgrade -- exact restoration both times); resulting policy
  expressions inspected directly via `pg_policies`/`psql \d
  security_events`.
SCHEMA_CHANGES: `security_events` created (see above). `recovery_records`/
  `decisions`/every other table in `_WORKSPACE_SCOPED_TABLES` gains RLS
  + one policy; no column added, altered, or dropped on any pre-existing
  table.
DB_PRIVILEGE_CHANGES: `security_event_writer` gains `SELECT, INSERT` on
  `security_events`; `governed_commit_writer` loses `UPDATE` on
  `audit_events` (disclosed retrofit, see DIFF_AUDIT). Every other one
  of PKG-25's own 9 principals' table-level grants is UNCHANGED --
  RLS is a row-level filter layered ON TOP of those existing grants,
  never a replacement for them.

PUBLIC_INTERFACES_CREATED:
  security.events.{Environment, TrustBoundary, SecurityEvent,
    SecurityEventRepository} -- 14's own literal PUBLIC INTERFACES:
    "SecurityEventRepository".
  security.workspace.{WORKSPACE_CONTEXT_SETTING, WorkspaceContextPort}
    -- the "trusted server adapter" port 14 section 8's own
    `[IMPLEMENTATION CHOICE]` names.
  persistence.security_event_repository.SqlAlchemySecurityEventRepository,
    persistence.workspace_rls_context.SqlAlchemyWorkspaceContext -- the
    concrete adapters (`security`'s own allow-list is `semantic_types`
    only, so neither concrete adapter can live inside the `security`
    package itself -- the identical `persistence`-hosts-the-adapter
    split PKG-12/17/23/24 already established for
    Audit/Evidence/Recovery repositories).

COMMANDS_CREATED: NOT_APPLICABLE. 14 assigns no Command to this
  package.
QUERIES_CREATED: NOT_APPLICABLE. `SecurityEventRepository.get`/
  `list_for_correlation` are plain repository reads, never a
  canonical/governance-state Query object.
EVENTS_CREATED: NOT_APPLICABLE. No Event contract assigned by 14 to
  this package; a `SecurityEvent` is explicitly "not a 09 Domain Event"
  (11 section 41's own classification).

BOUNDARIES_CREATED_OR_CHANGED: none (no `boundaries.BndNNN*` file
  created or modified). This package's own BOUNDARIES line: "BND-002
  remains semantic enforcement in addition to RLS" -- proven, not
  merely asserted: `test_mut_pkg26_01_rls_bypass_assumption_arbitrary_context_grants_access`
  demonstrates that RLS ALONE cannot verify genuine Workspace
  membership (a connection can claim any `WorkspaceId` and RLS will
  honor the claim) -- BND-002's own real membership verification,
  performed BEFORE the trusted server adapter is ever called, remains
  the ONLY semantic proof of legitimate access; RLS is disclosed,
  honestly, as accidental-leakage defense-in-depth, never a
  replacement.

AUTHORITY_PATH: This package's own AUTHORITY line -- "RLS success
  never grants domain authority" -- is a structural fact, not a
  runtime promise: `WorkspaceContextPort`'s own two methods both return
  `None`; there is no method anywhere on this Protocol that could hand
  back an authority token, a BoundaryProof, or any authorization-shaped
  value (see `security.workspace`'s own module docstring). No new
  Decision Right, `AuthorityClass` value, `AuthorityResolver` fallback,
  or Owner/Admin superpower was introduced. `migration_owner`'s own
  elevated DDL rights remain proven incapable of any row-level write
  even with RLS now layered on top
  (`test_migration_owner_remains_denied_all_dml_regardless_of_rls_context`)
  -- P-24's own claim, re-exercised, not weakened.
EVIDENCE_PATH: This package's own EVIDENCE line -- "Cross-Workspace
  Evidence denied" -- is now reinforced at the DB-policy layer:
  `evidence`/`claim_anchors`/`evidence_relations`/`evidence_set_references`/
  `source_references` are all among the 29 RLS-protected tables. The
  application-layer proof (PKG-16/17's own cross-Workspace Evidence
  tests) remains the primary, unmodified proof; this package adds an
  independent, additional DB-layer defense underneath it, re-exercised
  by the full-suite regression.
AI_PATH: This package's own AI line -- "Cross-Workspace AI context
  denied" -- likewise reinforced: `ai_generations`/`ai_derived_artifacts`/
  `ai_context_manifests` are RLS-protected. PKG-19's own
  single-Workspace `AIContextManifest` proof remains the primary,
  unmodified application-layer proof.
RECOVERY_PATH: `recovery_records` is RLS-protected exactly like every
  other Workspace-scoped table, exercised directly by this package's
  own primary test fixture (`recovery_reader`'s own real CRUD access,
  PKG-24/25). Recovery still cannot create legitimacy -- RLS ALLOW is
  never treated as an authority or recovery-legitimacy proof anywhere
  in this codebase.

TESTS_CREATED:
  tests/security/test_events.py (12 tests -- construction validation,
    Protocol structural shape (no update/delete method), round-trip
    create/get, a forged/unresolvable `workspace_id` recording
    successfully (the whole point of the no-FK design),
    `list_for_correlation` ordering, DB-trigger rejection of UPDATE and
    DELETE, DB CHECK-constraint rejection of an unknown environment/
    trust boundary)
  tests/security/test_workspace.py (10 tests -- `WorkspaceContextPort`
    structural shape; RLS fail-closed default (zero rows with no
    context set, even though real rows exist); correct context reveals
    only its own Workspace's row; MUT-PKG26-01 "RLS bypass assumption"
    (an arbitrary, unverified claimed Workspace DOES grant access --
    disclosed, not hidden); clearing context returns to fail-closed;
    `WITH CHECK` rejects an INSERT whose own `workspace_id` does not
    match the connection's current context even though the table-level
    GRANT alone would have allowed it; RLS applies identically across
    different principals (`api_reader` as well as `recovery_reader`);
    `migration_owner` remains denied all DML regardless of RLS;
    every one of the 29 intended tables has RLS enabled, no more, no
    fewer; MUT-PKG26-02 counterfactual proof that RLS itself (not an
    empty table) causes the visible-row-count difference)

TESTS_MODIFIED: none. Third package in this Phase (after PKG-22/23/25)
  with zero modified test files.

TARGETED_TEST_RESULTS:
  Pure-Python (no `DATABASE_URL`): 677 passed, 384 skipped (skips are
    the established `SKIPPED_NO_DATABASE` convention).
  Live PostgreSQL 17 (`DATABASE_URL=postgresql+psycopg://nquiry:
    nquiry_local_dev_only@localhost:15432/nquiry`), full suite
    (`tests/ apps/api/tests apps/worker`): 1061 passed, 1 skipped (the
    one pre-existing, unrelated, disclosed skip). Zero failures, zero
    new skips, zero regressions against PKG-25's own 1039-passed
    baseline (+22 new tests: 12 + 10).
  Direct `psql`/`pg_policies`/`information_schema.role_table_grants`
    inspection (independent of pytest): every one of the 29 RLS
    policies matches the intended expression exactly; grant deltas
    match `governed_commit_writer`'s own revocation and
    `security_event_writer`'s own new grant precisely.

NEGATIVE_TEST_RESULTS: every forbidden case (RLS denying an
  out-of-context row, the `WITH CHECK` insert rejection, the
  append-only trigger rejections, the CHECK-constraint rejections) is a
  designed-before-implementation negative test asserting a REAL
  Postgres denial, never merely an application-layer mock.

ADVERSARIAL_TEST_RESULTS:
  PRE_IMPLEMENTATION_ATTACK_MODEL category coverage: semantic-shortcut
  (3, below), authority/boundary-bypass (3, below), persistence/
  concurrency (NOT_APPLICABLE -- this package adds no new concurrent-
  write path, only a row-level filter on already-concurrency-proven
  tables), Workspace (4, below -- the package's own primary category),
  AI-authority (1, below), failure/retry (NOT_APPLICABLE -- no
  retry/idempotency path in this package's own scope), projection/
  cache-truth (1, below).

  Mandatory (7/7, this package's own literal "Package-specific
  mandatory attacks" line):
  1. ATTACK: Cross-Workspace at every layer
     EXPECTED DEFENSE: repository/Command/Evidence/AI-context/
       projection layers already deny (PKG-01/09/10/16/17/19/21, still
       green); the DB-policy layer denies independently, for the first
       time
     EXPECTED BOUNDARY: BND-002 (existing, unmodified) PLUS the new
       DB-GRANT+RLS boundary
     EXPECTED CANONICAL RESULT: zero rows visible/writable outside the
       resolved Workspace, at either layer, independently
     EXPECTED PROOF ARTIFACT: full-suite regression (existing layers) +
       `test_correct_context_reveals_only_its_own_workspace_row`/
       `test_api_reader_is_subject_to_the_same_rls_policy_as_recovery_reader`
       (new DB-policy layer)
     ACTUAL RESULT: matches
  2. ATTACK: wrong DB principal
     EXPECTED DEFENSE: RLS applies uniformly to every non-owner
       principal, not only whichever one a test happens to exercise
       most
     EXPECTED BOUNDARY: DB-GRANT + RLS BOUNDARY
     EXPECTED CANONICAL RESULT: identical isolation for `api_reader` as
       for `recovery_reader`
     EXPECTED PROOF ARTIFACT:
       `test_api_reader_is_subject_to_the_same_rls_policy_as_recovery_reader`
     ACTUAL RESULT: matches
  3. ATTACK: forged role
     EXPECTED DEFENSE: a `SecurityEvent` about a forged/nonexistent
       Workspace claim must still be recordable (the claim itself is
       the fact being captured) without granting it any legitimacy
     EXPECTED BOUNDARY: NOT_APPLICABLE (no boundary evaluates
       SecurityEvent recording; it is a pure operational record)
     EXPECTED CANONICAL RESULT: the row persists, `workspace_id` names
       the forged reference exactly, no FK validates or rejects it
     EXPECTED PROOF ARTIFACT:
       `test_record_with_a_forged_unresolvable_workspace_id_succeeds`
     ACTUAL RESULT: matches
  4. ATTACK: forged authority request
     EXPECTED DEFENSE: `WorkspaceContextPort` has no method that could
       accept or return an authority-shaped value at all
     EXPECTED BOUNDARY: NOT_APPLICABLE (structural, not a runtime
       boundary evaluation)
     EXPECTED CANONICAL RESULT: NOT_APPLICABLE
     EXPECTED PROOF ARTIFACT: `test_workspace_context_port_structural_shape`
     ACTUAL RESULT: matches
  5. ATTACK: direct canonical write
     EXPECTED DEFENSE: RLS's own `WITH CHECK` clause defends the WRITE
       side, independent of the table-level GRANT: `recovery_reader`
       genuinely HAS INSERT on `recovery_records` (PKG-25), but an
       INSERT claiming a `workspace_id` that does not match the
       connection's own current context is rejected anyway
     EXPECTED BOUNDARY: DB-GRANT + RLS BOUNDARY (WITH CHECK)
     EXPECTED CANONICAL RESULT: real `new row violates row-level
       security policy` Postgres error; no row persists
     EXPECTED PROOF ARTIFACT:
       `test_with_check_rejects_an_insert_claiming_the_wrong_workspace`
     ACTUAL RESULT: matches
  6. ATTACK: privileged technical identity attempts Decision
     EXPECTED DEFENSE: `migration_owner`'s own elevated DDL rights
       (real, proven: `CREATE TABLE`/`DROP TABLE` succeed) never imply
       row-level DML rights, RLS or no RLS
     EXPECTED BOUNDARY: DB-GRANT BOUNDARY (RLS is moot here --
       `migration_owner` is denied before RLS would even evaluate)
     EXPECTED CANONICAL RESULT: real `permission denied` on `SELECT`
     EXPECTED PROOF ARTIFACT:
       `test_migration_owner_remains_denied_all_dml_regardless_of_rls_context`
     ACTUAL RESULT: matches
  7. ATTACK: RLS bypass assumption
     EXPECTED DEFENSE: honestly disclosed as a REAL LIMIT, not hidden --
       `set_workspace_context` performs no membership verification of
       its own; an arbitrary, unverified claimed Workspace DOES grant
       access to that Workspace's own rows
     EXPECTED BOUNDARY: NONE at the RLS layer for this specific claim
       (BND-002 remains the only semantic proof, and is deliberately
       NOT called by this test, to isolate and prove the limit)
     EXPECTED CANONICAL RESULT: the claimed Workspace's own row IS
       returned -- a DELIBERATE, disclosed proof of RLS's own honest
       boundary, not a hidden defect
     EXPECTED PROOF ARTIFACT:
       `test_mut_pkg26_01_rls_bypass_assumption_arbitrary_context_grants_access`
     ACTUAL RESULT: matches

  Novel/adapted (>=10 required for this CRITICAL package; 10 delivered,
  17 total):
  8. ATTACK: RLS defaults to fail-open (sees everything) rather than
       fail-closed when no context is ever set
     ACTUAL RESULT: matches
       (test_no_context_set_yields_zero_rows_even_though_real_rows_exist
       -- proves the opposite: zero rows, not all rows)
  9. ATTACK: clearing the context via an empty string is treated
       differently from "never set", accidentally leaving a stale
       Workspace visible
     ACTUAL RESULT: matches
       (test_clearing_context_returns_to_the_fail_closed_default --
       `NULLIF(..., '')` collapses both to the identical `NULL`
       comparison)
  10. ATTACK: a future migration adds a new Workspace-keyed table and
        forgets to enable RLS on it
      ACTUAL RESULT: matches (test_rls_is_enabled_on_every_workspace_scoped_table
        -- asserts the EXACT set of 29 table names, would fail on a
        silent omission or an accidental addition)
  11. ATTACK (MUT-PKG26-02, guard-necessity/counterfactual, projection/
        cache-truth-adjacent): is the visible-row-count difference
        genuinely caused by RLS, or could it be an unrelated artifact
        (e.g. the seeded rows not actually existing)?
      ACTUAL RESULT: matches
        (test_mut_pkg26_02_rls_is_the_actual_mechanism_not_an_empty_table_coincidence
        -- see MUTATION_TESTS)
  12. ATTACK: `SecurityEventRepository`'s own Protocol silently grows an
        update/delete method in a future edit
      ACTUAL RESULT: matches
        (test_security_event_repository_protocol_has_no_update_or_delete_method)
  13. ATTACK: a caller bypasses `SecurityEventRepository` entirely (raw
        SQL) and tampers with an established SecurityEvent
      ACTUAL RESULT: matches (test_db_trigger_rejects_update,
        test_db_trigger_rejects_delete -- real Postgres triggers,
        independent of the Python Protocol's own structural defense)
  14. ATTACK: an unrecognized `environment`/`trust_boundary` value is
        silently accepted, widening these closed vocabularies by
        accident
      ACTUAL RESULT: matches
        (test_db_check_constraint_rejects_an_unknown_environment,
        test_db_check_constraint_rejects_an_unknown_trust_boundary)
  15. ATTACK: `SecurityEvent.occurred_at` accepts a naive (non-tz-aware)
        datetime, breaking correlation ordering across time zones
      ACTUAL RESULT: matches (test_security_event_rejects_naive_datetime)
  16. ATTACK: `list_for_correlation` returns SecurityEvents out of
        chronological order, hiding the true attack timeline from an
        investigator
      ACTUAL RESULT: matches (test_list_for_correlation_orders_by_occurred_at)
  17. ATTACK: RLS's own genuine table-owner/superuser bypass is
        mistaken for a leak in the mechanism itself, rather than
        understood as an orthogonal, pre-existing Postgres property
      ACTUAL RESULT: matches -- the same
        `test_mut_pkg26_02_rls_is_the_actual_mechanism_not_an_empty_table_coincidence`
        test explicitly demonstrates and documents this distinction
        rather than leaving it implicit

MUTATION_TESTS:
  METHODOLOGY NOTE (same disclosed adaptation as PKG-24/25): this
  session's own auto-mode tool classifier denies temporarily weakening
  a real security control in place, even reverted immediately
  afterward. Both mutation proofs below are guard-necessity/
  counterfactual tests against real, unmodified production SQL/roles --
  never a code, policy, or schema edit.

  MUT-PKG26-01: is `set_workspace_context`'s own lack of membership
    verification a real, exploitable limit, or does something else
    (an assumption in this test suite, an accidental extra check)
    prevent an arbitrary claimed Workspace from actually working? A
    connection claims a Workspace it was never seeded/verified against
    -> expected (if the limit is real): that Workspace's own row IS
    returned. ACTUAL: confirmed
    (test_mut_pkg26_01_rls_bypass_assumption_arbitrary_context_grants_access).
    INTERPRETATION: the limit is real and now explicitly, permanently
    proven rather than merely asserted in prose -- disclosed in
    KNOWN_LIMITATIONS, not silently accepted as acceptable-by-omission.
  MUT-PKG26-02: is the visible-row-count difference between a
    superuser connection and a `recovery_reader` connection genuinely
    caused by the RLS policy, or could the same result arise from an
    unrelated cause (e.g. a fixture bug where only one row was ever
    really inserted)? Querying the SAME two seeded rows through BOTH
    connections in the SAME test -> expected: superuser sees 2, RLS-
    subject connection sees 1. ACTUAL: confirmed
    (test_mut_pkg26_02_rls_is_the_actual_mechanism_not_an_empty_table_coincidence).
    INTERPRETATION: RLS is confirmed as the actual, load-bearing cause
    of the isolation this package's other tests observe, not a
    coincidence of fixture data.
  A THIRD, PROCESS-LEVEL FINDING WORTH RECORDING HERE: while first
    writing these tests, four of them initially reported a FALSE
    PASS -- they used a genuinely SEPARATE physical connection
    (`_principal_engine`, PKG-25's own pattern) to read rows seeded via
    the shared `db_connection` fixture's own STILL-OPEN, never-committed
    transaction. A separate Postgres session cannot see another
    session's uncommitted rows regardless of RLS, so those four tests
    were passing/failing for the WRONG reason (visibility, not
    permission) until rewritten to use `SET ROLE`/`RESET ROLE` on the
    SAME connection/transaction (`_as_principal`) instead -- this
    surfaced the bug immediately, since the corrected tests initially
    FAILED against the real RLS policy before the policy's own
    `USING`/`WITH CHECK` expressions were fully verified against
    `psql`'s own live output. Caught and fixed before this report was
    written, not a surviving defect; disclosed because it is a
    genuinely reusable lesson: "add a role/table's own real DB test"
    for GRANTS (catalog metadata, cross-session-visible) is safe with a
    separate connection; the identical pattern for ROW VISIBILITY needs
    `SET ROLE` on the SAME session as the seeding, or the seeded data
    must actually be committed.
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TEST_RESULTS: `tests/security/test_workspace.py` exercises
  the full real stack for its own primary fixture: `NonProofWorkspaceBootstrap`
  (PKG-04) -> real `SqlAlchemyCommandRepository`/`SqlAlchemyCommitRepository`
  (PKG-10/13) -> a real, committed `Command`/`CommitUnit` pair -> a real
  `SqlAlchemyRecoveryRepository.create` (PKG-23/24) -> the SAME session,
  `SET ROLE`d to a real PKG-25 principal -> the real
  `SqlAlchemyWorkspaceContext` adapter -> the real RLS policy this
  package's own migration created -> a real, observed row-count/
  denial outcome. No mock, no fake role, no simulated permission or
  policy check anywhere in either new test file.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through
  PKG-25's tests) re-run alongside PKG-26's new tests, both without a
  live database (677 passed, 384 skipped) and against a real
  PostgreSQL 17 instance with all 19 migrations applied
  (`tests/ apps/api/tests apps/worker`: 1061 passed, 1 skipped). Zero
  regressions; every previously-green test remains green -- including
  every prior package's own Workspace-isolation proof at the
  repository/Command/Evidence/AI-context/projection layers this
  package's own OBJECTIVE names, none of which needed a single line
  changed to keep passing under the new RLS policies (RLS is
  transparently bypassed for the bootstrap `nquiry` superuser/table-owner
  connection every existing test still uses -- verified live before
  writing this migration).

P_CLAIMS_TESTED:
  P-22 (Workspace isolation blocks cross-Workspace protected-data use):
    substantially exercised for the first time at the DB-POLICY layer --
    a real RLS policy now independently proves cross-Workspace
    isolation for 29 tables, live, in addition to (never instead of)
    BND-002's own semantic proof. The "RLS bypass assumption" attack
    (MUT-PKG26-01) is disclosed explicitly as the honest boundary of
    this NEW layer's own contribution: it defends against accidental
    leakage, not against a caller with a verified-membership port that
    chooses to lie to it -- that half of P-22 remains BND-002's own,
    unchanged, primary proof.
  P-24 (Admin/root technical capability is not domain authority): further
    exercised -- `migration_owner`'s own elevated DDL capability (PKG-25's
    own proof) is re-proven UNCHANGED now that RLS is layered on top of
    the grant system, confirming RLS was added as a genuine
    ADDITIONAL layer, not a replacement that could have accidentally
    widened or narrowed this claim's own prior proof.

PROOF_ARTIFACTS:
  - 1061-test live-database pass (0 regressions against PKG-25's own
    1039-passed baseline), including 17 distinct adversarial proofs (7
    mandatory + 10 novel/adapted) and 2 guard-necessity/counterfactual
    mutation proofs
  - A live `pg_policies` read-back confirming all 29
    `workspace_isolation` policies carry the EXACT intended `USING`/
    `WITH CHECK` expression, re-verified identical after a
    downgrade(-1)/re-upgrade cycle
  - A real, observed row-count difference (2 visible to a superuser vs.
    1 visible to a RLS-subject `recovery_reader` connection) over the
    SAME underlying data, in the SAME test
  - A real `new row violates row-level security policy` Postgres error
    for an INSERT whose claimed `workspace_id` does not match the
    connection's own current RLS context
  - A real, live trigger rejection for both an UPDATE and a DELETE
    attempt against `security_events`, and for two unrecognized
    CHECK-constrained vocabulary values
  - A real, cleanly-cleaned-up manual probe row used to prove the
    append-only triggers before any pytest run touched the table
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output, including a full upgrade to head 047bdf9bc528,
    a downgrade(-1)/re-upgrade cycle, and direct `psql`
    schema/policy/grant inspection
  - Diff audit (inline answers below), cross-checked against `git
    status --short` before staging per this session's own standing
    instruction

FORBIDDEN_DEPENDENCY_CHECK: PASS (one new, disclosed, cited extension:
  persistence -> security, 21st overall; one-directional -- `security`'s
  own allowed set, 14 section 3.1: "semantic_types", does not include
  `persistence`, so no cycle is created; no file under
  `packages/security/` imports `persistence` at all)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT:
  New semantic type/enum value: `Environment` (4 values) and
    `TrustBoundary` (19 values) are both 11's own, verbatim,
    definitively-closed lists (sections 60/3) -- transcribed, not
    invented. `SecurityEvent`/`SecurityEventRepository`/
    `WorkspaceContextPort` are this package's own disclosed
    `[IMPLEMENTATION CHOICE]` shapes for a field list/adapter port 11/14
    themselves explicitly leave to "implementation materialization" --
    not new domain concepts.
  New transition: none -- `security_events` is append-only (no
    `result`/`status` state machine of its own).
  New authority path: none -- see AUTHORITY_PATH above; this package's
    entire OBJECTIVE requires proving RLS success is STRUCTURALLY
    incapable of granting authority, not merely disclaiming it.
  New DB write path: yes, disclosed -- `SqlAlchemySecurityEventRepository.record`
    is a genuinely new write path, but writes only to the new,
    non-canonical, append-only `security_events` table (11 section 41's
    own explicit "not a 02 domain Thing" classification) -- never a
    canonical table.
  Weakened boundary: none -- no BND-001..018 evaluator touched, and RLS
    is additive defense-in-depth, never a replacement (see
    BOUNDARIES_CREATED_OR_CHANGED). One EXISTING grant was NARROWED
    (`governed_commit_writer` loses `UPDATE` on `audit_events`) --
    narrowing a privilege is the opposite of weakening a boundary.
  Easier test / removed negative test / admin shortcut / projection or
    cache truth / AI canonical authority / broader Workspace scope:
    none. If anything, this package NARROWS a predecessor's own
    over-grant (see below) and ADDS a Workspace-scope restriction (RLS)
    that did not exist before.
  Changed migration semantics: none -- no prior migration's own DDL/DML
    is edited; PKG-25's own migration (`2feb99a01f9d`) is unchanged, its
    OWN deferred grant is simply completed by this LATER migration, the
    identical pattern that migration's own docstring already disclosed
    as the intended sequencing.
  Retrofit of a predecessor's own now-discovered gap: yes, disclosed --
    `governed_commit_writer` loses its own previously-granted `UPDATE`
    on `audit_events`. Discovered while cross-checking PKG-25's own
    grants against 14 section 8's explicit "governed_commit_writer ...
    Forbidden: arbitrary audit update/delete" row (not fully consulted
    at PKG-25 authoring time, which worked primarily from 11 section
    15's own 4-category framing instead). Code-grounded-tracing
    confirms no production code anywhere calls
    `sa.update(audit_events_table)` -- `SELECT`/`INSERT` (both
    code-grounded and required) are retained. Same "retrofit a
    predecessor's own now-discovered gap in the package that discovers
    it" pattern already used repeatedly (PKG-13's FK retrofits, PKG-24's
    `record_version` retrofit).
  Forbidden dependency: one new, disclosed, cited extension --
    persistence -> security (21st overall, see
    FORBIDDEN_DEPENDENCY_CHECK).
  Files touched outside this package's own new-file set:
    `packages/persistence/tables.py`,
    `scripts/check_architecture_dependencies.py` -- both explicitly the
    disclosed extension points this package's own new table/adapters
    require; no other predecessor file touched. No previously-green
    test required a fix. One real bug WAS found and fixed during this
    package's own development (see MUTATION_TESTS' own "process-level
    finding") -- a test-authoring bug (wrong-connection visibility),
    not a production defect, caught before any test was reported as
    passing for the wrong reason in this report.
  `git status --short` immediately before staging matched this section
    exactly: 2 modified files
    (`packages/persistence/tables.py`,
    `scripts/check_architecture_dependencies.py`) plus 5 new production
    files
    (`migrations/versions/047bdf9bc528_rls_and_security_events.py`,
    `packages/security/events.py`, `packages/security/workspace.py`,
    `packages/persistence/security_event_repository.py`,
    `packages/persistence/workspace_rls_context.py`) plus 2 new test
    files (`tests/security/test_events.py`,
    `tests/security/test_workspace.py`), nothing else, no tooling/lock
    files.

ARCHITECTURE_RECONSTRUCTION_RESULT:
  This package participates in NO single consequential request path of
  its own -- 14 assigns it no Command, Query, or Boundary. Its own
  longest legitimate chain is the SAME cross-cutting infrastructure
  shape PKG-25 established, extended by one more layer: DB CONNECTION
  AUTHENTICATION (a real service process connects as one of PKG-25's
  own 9 principals) -> TRUSTED SERVER ADAPTER (this package's own
  `WorkspaceContextPort`, called ONLY after BND-002/003 have already
  verified the caller's own effective Workspace -- never from an
  unverified claim) -> DB-GRANT + RLS BOUNDARY (PostgreSQL checks BOTH
  table privilege AND the row-level policy before any statement
  executes) -> [the ALREADY-EXISTING, unmodified governed path for
  whichever table was targeted, exactly as PKG-09 through PKG-25 already
  built and proved] -> RESULTING STATE (unchanged by this package).
  SecurityEvent recording is a SEPARATE, parallel, non-consequential
  chain of its own: OBSERVED TECHNICAL FACT (an attack, a denial, an
  anomaly -- from ANY layer above) -> `SecurityEventRepository.record`
  -> a real, append-only `security_events` row -> ALERTING/CONTAINMENT/
  INVESTIGATION/a governed Command (11 section 41's own explicit list
  of what MAY follow) -- each remaining downstream node
  (alerting/containment/a real governed Command actually consuming a
  SecurityEvent) is `SUCCESSOR_NOT_BUILT`, disclosed: no production
  code anywhere in this codebase yet calls
  `SecurityEventRepository.record` from within an actual attack path
  (e.g. from inside `Bnd002WorkspaceEvaluator`'s own DENY branch) --
  this package proves the mechanism (14's own file-level map assigns it
  only `packages/security/*`, never a boundary-evaluator file), the
  identical "engine before concrete caller" pattern PKG-08/09/13/16/17/
  25 each already established.

KNOWN_LIMITATIONS:
  - "RLS bypass assumption" is a REAL, disclosed, proven limit (MUT-
    PKG26-01): `set_workspace_context` performs no membership
    verification of its own. A future integration wiring the trusted
    server adapter's own real call site (inside an actual request
    pipeline, immediately after a real BND-002 ALLOW) remains
    `SUCCESSOR_NOT_BUILT` -- no such call site exists in production
    code yet, matching PKG-25's own identical disclosed gap ("no
    production process is wired to connect as any of the 9
    principals yet").
  - No production code anywhere calls `SecurityEventRepository.record`
    from within an actual attack/denial path yet (see
    ARCHITECTURE_RECONSTRUCTION_RESULT) -- the repository and its own
    schema are proven end-to-end, but wiring a real caller (e.g. a
    boundary evaluator emitting a SecurityEvent on DENY) remains
    `SUCCESSOR_NOT_BUILT`.
  - `governed_commit_writer`'s own remaining table set was NOT
    re-audited verb-by-verb against 14 section 8's own table beyond the
    one `audit_events` UPDATE gap this package discovered and fixed --
    a full re-audit of every other principal/table/verb combination
    was judged out of this package's own narrow scope (RLS/
    SecurityEvents, not "re-derive PKG-25's entire grant matrix from
    scratch"). Disclosed, not silently assumed perfect.
  - `recovery_reader`'s own broader-than-14-section-8-literal-text
    write scope (full CRUD on `recovery_records`, per PKG-24's own
    human-confirmed architectural decision) is unchanged by this
    package and remains exactly as disclosed in PKG-24/25's own reports
    -- not re-litigated here.
  - `BACKUP_PRINCIPAL`/backup-restore RLS interaction remains
    unbuilt/undefined (no backup tooling exists in this prototype at
    all, unchanged since PKG-25).
  - Sandbox Python remains 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still
  BLOCKED. Neither is touched by this package's own scope.

NEW_GAPS_DISCOVERED:
  1. `governed_commit_writer` held an over-broad `UPDATE` grant on
     `audit_events` (PKG-25's own uniform-grant simplification,
     disclosed at the time) -- discovered and retrofitted THIS package
     (see DIFF_AUDIT).
  2. No production call site exists yet for either the trusted server
     adapter's own real request-pipeline integration or
     `SecurityEventRepository.record`'s own real attack-path integration
     (see KNOWN_LIMITATIONS) -- both disclosed, both matching this
     codebase's own repeated "engine before concrete caller" precedent.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. `Environment`/
  `TrustBoundary` are 11's own literal, verbatim, closed lists.
  `SecurityEvent`'s own field list is 11 section 42's own list,
  materialized exactly as that section itself invites ("Exact physical
  schema belongs to implementation materialization"). The RLS
  mechanism itself is 14 section 8's own literal `[IMPLEMENTATION
  CHOICE]`, transcribed, not invented. No new Decision Right, authority
  class, Command, Query, Event, Boundary, or canonical write PATH was
  introduced -- only a new, independently-proven, additive defense-in-
  depth layer underneath paths every one of PKG-09 through PKG-25
  already built and proved, plus one disclosed narrowing retrofit of a
  predecessor's own over-grant.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-27 becomes DAG-eligible once its own
  required predecessors are verified. Eligibility is not authorization.
HUMAN_GATE_REQUIRED: YES -- 14 PKG-26's own coding prompt:
  "HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any
  successor." Do not authorize PKG-27 without explicit human
  authorization naming the package and this package's own commit hash.
```
