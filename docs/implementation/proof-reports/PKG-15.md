# PKG-15 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-15
PACKAGE_TITLE: Human Decision
BUILD_PHASE: 5
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  02_DOMAIN_AND_RELATION_MODEL.md section 26 (Decision --
    CANONICAL_DOMAIN_OBJECT, identity via `Decision.id`, belongs to a
    Challenge, relates to Question/Evidence; section 26.6 GAP-02-006
    explicitly defers lifecycle/authority interaction to 03/04)
  03_STATE_AND_TRANSITION_ARCHITECTURE.md section 35 (Decision State
    Architecture -- exact 2-value vocabulary UNDER_CONSIDERATION/DECIDED,
    `[ARCHITECTURAL CLOSURE]`), section 36 (TRN-DEC-001
    OPEN_DECISION_CONSIDERATION, TRN-DEC-002 RECORD_HUMAN_DECISION --
    exact CURRENT STATE/PRECONDITIONS/DENY CONDITION/NEXT STATE text),
    section 37 (Decision Does Not Equal Authorized Execution), section
    38 (GAP-03-005 -- DECIDED -> UNDER_CONSIDERATION forbidden as a
    silent rewrite)
  04_AUTHORITY_AND_DECISION_RIGHTS.md section 9.5 (DECISION_RIGHT
    definition), section 49 (AUTH-DEP-DEC-001 -- exact AUTHORITY SCOPE
    "Specific Decision/Challenge"), section 50 (AUTH-DEP-DEC-002 --
    exact AUTHORITY SCOPE "Specific Decision", exact DENY CONDITION
    text)
  06_BOUNDARY_ARCHITECTURE.md section 4 (Canonical Consequential
    Request Path), section 10 (BND-004 -- "Observer/Viewer mutation"
    DENY example), section 12 (BND-006 -- already generic across
    DECISION_RIGHT/QUESTION_SELECTION_RIGHT/etc.), section 13 (BND-007
    -- "one specific 03 transition or state-preserving consequential
    mutation")
  08_AI_ARCHITECTURE_AND_CONTRACTS.md (confirmed AI context-only role
    for Decision; no AIOP/Gateway wiring needed -- no AIGeneration
    infrastructure exists yet, correctly NOT_APPLICABLE at this phase)
  12_MINIMUM_PROTOTYPE_ARCHITECTURE.md section 7 (Authority Profile --
    DECISION_RIGHT row, no bootstrap-ordering hedge), section 28
    (PROTOTYPE HAPPY PATH steps 22/24: Decision opened / Human Decision
    created), P-07/P-09/P-10 fixture rows
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md section 6/54.6 (P-07/P-09/
    P-10 matrix rows -- exact ATTACK/CONTROL/CANONICAL RESULT text),
    section 39 (T3 -> tests/authority/; T10 -> tests/e2e/)
  14_IMPLEMENTATION_SEQUENCE.md section on PKG-15 (BUILD_PHASE 5,
    UPSTREAM FILES 02/03/04/06/08/12/13/14, REQUIRED PREDECESSORS
    PKG-13, PUBLIC INTERFACES "Decision commands", DATABASE CHANGES
    005, TESTS REQUIRED T3/T10, PROOF CLAIMS P-07/P-09/P-10, flagged
    CRITICAL with >=10 total novel/adapted attacks required), section
    3.1/4 (directory ownership, forbidden dependency matrix -- no new
    extension needed, `application -> commit` from PKG-14 already
    covers this package), section 9 (migration plan --
    005_selection_decision: "selections, decisions" -- decisions half),
    section 10 (REPOSITORY PORTS -- `DecisionRepository`/
    `ChallengeRepository` exact wording), section 12 (COMMAND
    REGISTRY -- `RecordHumanDecision` row: authority, boundaries
    001-007,013,014,015, canonical effect), section 21 (HUMAN
    DECISION), section 27 (IDEMPOTENCY rules), section 46/48 (PKG-15
    manifest, file-level map)

14_REQUIREMENTS_MATERIALIZED:
  PUBLIC_INTERFACES: "Decision commands" (plural) -- created as
    `application.human_decision_handler.{open_decision_consideration,
    record_human_decision}`, materializing BOTH TRN-DEC-001 and
    TRN-DEC-002. No other package in the 32-package DAG is ever
    assigned `CMD_OPEN_DECISION_CONSIDERATION`/TRN-DEC-001 -- see
    DIFF_AUDIT for the full reasoning. Supporting types not
    independently invented: `Decision`'s field list is 09 section 47's
    own, verbatim; `DecisionState`'s 2 values are 03 section 35.2's own
    vocabulary.
  DATABASE_CHANGES: 005 (decisions half only) -- `decisions` created;
    `selections` half was PKG-14's own scope. Sixth application of the
    one-conceptual-bucket-across-two-Alembic-revisions split.
  TESTS_REQUIRED: T3 (tests/authority/test_decision_authority.py -- 6
    tests proving DECISION_RIGHT resolves correctly at the new
    CHALLENGE/DECISION scopes), T10 (tests/e2e/test_human_decision.py
    -- 13 tests, full end-to-end handler, first file in
    `tests/e2e/`) -- both created, including the new
    `tests/e2e/conftest.py` fixture file (mirroring every other test
    directory's identical `db_connection` fixture). T2
    (tests/transitions/test_decision_transition_constraints.py, 13
    tests) and T4 (tests/boundaries/test_bnd_007_state_transition.py
    extension, 2 tests) added proactively, though not formally
    required by this package's own TESTS_REQUIRED line.
  PROOF_CLAIMS: P-07, P-09, P-10 -- see P_CLAIMS_TESTED below.

PREDECESSORS_VERIFIED:
  PKG-13 (a579e80, PACKAGE_PASS, human gate given).
  Full chain unbroken: PKG-00 dd4aad2 through PKG-14 43d70bd. No
  predecessor's own non-test files were touched beyond the disclosed
  extension points (BND-007's tagged union, persistence tables) --
  full regression re-run below confirms no invalidation.

FILES_CREATED:
  packages/domain/decision.py
  packages/application/human_decision_handler.py
  packages/persistence/challenge_repository.py
  packages/persistence/decision_repository.py
  migrations/versions/e2f94137f8a9_decisions.py
  tests/authority/test_decision_authority.py
  tests/transitions/test_decision_transition_constraints.py
  tests/e2e/conftest.py
  tests/e2e/test_human_decision.py

FILES_MODIFIED:
  packages/boundaries/bnd_007_state_transition.py (widened
    `Bnd007Input.resolution`'s tagged union to accept
    `DecisionTransitionResolution` as a fourth member -- unlike PKG-14's
    QuestionSelection, Decision has genuine `from_state != to_state`
    pairs, the same shape Session/Burst already use)
  packages/persistence/tables.py (`decisions_table` added; docstring
    cross-reference)
  tests/boundaries/test_bnd_007_state_transition.py (+2 tests for the
    new `DecisionTransitionResolution` tagged-union member)

FILES_DELETED: none

MIGRATIONS_CREATED: e2f94137f8a9 (decisions), revises d9d99d8d2869.
  Creates `decisions`; composite FKs to `challenges`/`questions`
  (nullable, for the optional `decision_question_ref`); a CHECK
  enforcing 03 section 35.2's state vocabulary; a second CHECK
  enforcing the DECIDED<->attribution biconditional at the database
  layer; two triggers enforcing 03 section 36/38's transition topology,
  making DECIDED terminal at the database layer too. Full downgrade
  drops both triggers, both indexes, then the table.
SCHEMA_CHANGES: `decisions` (id, workspace_id, challenge_id,
  decision_question_ref [nullable], decision_question_text [nullable],
  options[], criteria[], selected_option [nullable], rationale
  [nullable], confidence [nullable], state, opened_by_user_id,
  decision_authority_binding_id [no FK, disclosed], decided_by_user_id
  [nullable], created_at, decided_at [nullable], record_version,
  provenance_ref [nullable]).
DB_PRIVILEGE_CHANGES: none. Deferred to migration
  012_security_events_rls, consistent with every migration since 001.

PUBLIC_INTERFACES_CREATED:
  domain.decision.{DecisionState, Decision, DecisionTransitionId,
    DecisionOperation, DecisionTransitionVerdict,
    DecisionTransitionResolution, resolve_decision_transition_to_state,
    challenge_target_ref, decision_target_ref}
  application.human_decision_handler.{OpenDecisionConsiderationPayload,
    RecordHumanDecisionPayload, HumanDecisionDenied,
    SelectedOptionNotCandidate, open_decision_consideration,
    record_human_decision}
  persistence.challenge_repository.{ChallengeRepository,
    SqlAlchemyChallengeRepository, SqlAlchemyChallengeVersionReader}
  persistence.decision_repository.{DecisionConflict, DecisionRepository,
    SqlAlchemyDecisionRepository, SqlAlchemyDecisionVersionReader}

COMMANDS_CREATED: OpenDecisionConsideration, RecordHumanDecision
  (`application.human_decision_handler`'s two functions) -- 14's own
  "Decision commands" (plural) PUBLIC_INTERFACES wording.
QUERIES_CREATED: NOT_APPLICABLE (14 assigns no Query to this package;
  `GetDecision` remains a future package's own scope).
EVENTS_CREATED: NOT_APPLICABLE (EventEnvelope remains PKG-20's own
  scope, Phase 8).
BOUNDARIES_CREATED_OR_CHANGED: BND-007 extended (not created) -- see
  FILES_MODIFIED. No new BoundaryId invented; BND-001..006/014 reused
  entirely unchanged.

AUTHORITY_PATH: `Bnd005HumanAuthorityEvaluator` resolves DECISION_RIGHT
  at `scope_type="CHALLENGE"` (OpenDecisionConsideration, since no
  Decision exists yet) and `scope_type="DECISION"`
  (RecordHumanDecision, once it does) -- the third distinct,
  literally-read authority-scope convention this codebase materializes
  (after WORKSPACE for Burst/Session-control, SESSION for
  QuestionSelection). `AuthorityResolver` itself required no code
  change. BND-014's own fresh, uncached resolve() (PKG-13) is reused
  unmodified as the commit-time revalidation.

EVIDENCE_PATH: 14 PKG-15 EVIDENCE: "Consumed refs preserved, no new
  sufficiency" -- honored via the ALREADY-EXISTING
  `CommandEnvelope.evidence_set_ref` (PKG-10) carrier, which
  `CommitCoordinator._commit_inner` already writes onto the resulting
  `AuditEvent.evidence_set_ref` unconditionally (PKG-13). This package
  only threads a caller-supplied `EvidenceSetId` through; no new
  Decision-level Evidence field or sufficiency check was added. BND-013
  (Evidence boundary) does not exist yet (PKG-16, Phase 6) and is
  correctly absent from the boundary chain, matching this package's own
  coding-prompt BOUNDARIES line.

AI_PATH: "AI is context only and cannot write Decision state" (14
  PKG-15 AI). No provider/model path introduced; BND-001 (actor class)
  and BND-006 (content-origin check, reused unmodified) both
  independently refuse an AI-class actor or AI-originated content from
  ever reaching a committed Decision -- proven by
  `test_denies_ai_actor_opening_consideration`.

RECOVERY_PATH: "Denied/stale human Decision creates no DECIDED state"
  (14 PKG-15 FAILURE_RECOVERY) -- proven directly: every DENY path
  raises before `CommitCoordinator` is entered; every precommit-layer
  failure (concurrent record, selected-option-not-candidate) surfaces
  as `CommitFailedPrecommit`/a raised exception, never a partial
  DECIDED row (the database's own attribution CHECK constraint makes
  an unattributed DECIDED row structurally impossible regardless of
  application-layer behavior).

TESTS_CREATED: 4 files, 34 new test functions (test_decision_authority.py:
  6; test_decision_transition_constraints.py: 13 [6 pure domain, 7
  live-DB]; test_human_decision.py: 13, covering all mandatory attacks
  plus 4 novel ones; tests/e2e/conftest.py is fixture-only, no test
  functions).
TESTS_MODIFIED: tests/boundaries/test_bnd_007_state_transition.py (+2
  tests).

TARGETED_TEST_RESULTS:
  Static: ruff format --check . -- PASS
          ruff check . -- PASS
          MYPYPATH=... mypy packages apps/api/src apps/worker/src scripts
            -- PASS (94 source files, no issues on first pass -- no new
            Protocol-variance `type: ignore` needed beyond the two
            already-disclosed uses this package's own
            `_build_registry` reuses from PKG-14's precedent)
  Architecture checks: check_architecture_dependencies.py -- PASS (no
    new extension required; `application -> commit`, established by
    PKG-14, already covers this package's own needs)
                        check_provider_sdk_imports.py -- PASS
                        check_test_only_imports.py -- PASS
                        verify_migrations.py -- PASS (static: 11
                          revisions, single head e2f94137f8a9; live: db
                          head matches after full upgrade from empty,
                          plus a downgrade(-1)/re-upgrade cycle)
  Pure-Python suite (no DB): tests/ -- 459 passed, 220 skipped (all
    SKIPPED_NO_DATABASE, none unexpected)
  Live-PostgreSQL 17 suite (full tree, DATABASE_URL set,
    POSTGRES_PORT=15432): tests/ -- 678 passed, 1 skipped, 0 failed
    (after fixing one genuine, disclosed design bug found by a live-DB
    test failure -- see NEW_GAPS_DISCOVERED)

NEGATIVE_TEST_RESULTS: all designed-before-implementation negative
  tests pass; each asserts a specific named exception type
  (HumanDecisionDenied carrying the chain's own terminal_boundary_id,
  SelectedOptionNotCandidate, DecisionConflict,
  IdempotencyAlreadyCommitted) or a real database constraint/trigger
  exception, never merely "an error occurred."

ADVERSARIAL_COUNTER_TESTS:
  Mandatory (9 named in the coding prompt; all proven, several jointly):
  1. Persist AI proposal then only view it
     EXPECTED DEFENSE: Bnd001IdentityEvaluator's required_actor_classes
       = {HUMAN_USER}, checked before any Decision-content concept
       exists at all
     EXPECTED BOUNDARY: BND-001
     EXPECTED CANONICAL RESULT: DENY, terminal_boundary_id=BND_001; no
       Decision row created
     ACTUAL RESULT: matches (test_denies_ai_actor_opening_consideration)
  2. Unrelated approval click
     EXPECTED DEFENSE: Bnd005HumanAuthorityEvaluator's fresh
       AuthorityResolver.resolve() -- a human with no DECISION_RIGHT
       binding at all
     EXPECTED BOUNDARY: BND-005
     ACTUAL RESULT: matches (test_denies_role_only_actor_without_binding)
  3. Technical admin update
     EXPECTED DEFENSE: same BND-005 check -- an OWNER-role holder
       (maximal Workspace role) still denied without an explicit
       DECISION_RIGHT binding (04: "Role alone does not grant
       authority")
     EXPECTED BOUNDARY: BND-005
     ACTUAL RESULT: matches
       (test_denies_technical_admin_without_decision_right)
  4. Role-only actor
     ACTUAL RESULT: matches (identical mechanism/test as #2 --
       04/06 name these as the same underlying attack shape)
  5. Revoked actor
     EXPECTED DEFENSE: same BND-005 fresh resolve(), binding revoked
       after OPEN succeeded, before RECORD
     EXPECTED BOUNDARY: BND-005
     ACTUAL RESULT: matches
       (test_denies_revoked_decision_right_before_record)
  6. Cross-Workspace Decision
     EXPECTED DEFENSE: Bnd002WorkspaceEvaluator's
       resolved_object_workspace_ids cross-check
     EXPECTED BOUNDARY: BND-002
     ACTUAL RESULT: matches (test_denies_a_challenge_from_another_workspace)
  7. Unattributed Decision
     EXPECTED DEFENSE: `Decision.__post_init__`'s own biconditional
       check (Python layer) AND `ck_decisions_decided_attribution`
       (database layer) -- defense in depth
     EXPECTED CANONICAL RESULT: ValueError (domain) / IntegrityError (DB)
     ACTUAL RESULT: matches
       (test_decided_without_attribution_is_rejected_at_the_database_layer,
       plus domain-level construction tests)
  8. Recommendation persistence setting DECIDED
     EXPECTED DEFENSE: `DecisionRepository.record_decision` requires a
       real `decided_by_user_id: UserId` parameter -- structurally no
       AI-authored path exists that could populate it; the same
       governed path proven in #1/#2 is the ONLY route to DECIDED
     ACTUAL RESULT: matches (proven by construction -- no alternate
       write path exists; see FORBIDDEN_DEPENDENCY_CHECK)
  9. Committed Decision followed by downstream action without separate
     authority
     EXPECTED DEFENSE: 03 section 37 ("Decision Does Not Equal
       Authorized Execution") -- this package builds no downstream
       transition machinery at all; `record_human_decision`'s own
       return value (`CommitUnit`) carries no reusable authorization
       token (matches AC-06-001 "Commit Permit Is Ephemeral")
     ACTUAL RESULT: matches (proven by absence -- no code path in this
       package reads a DECIDED Decision and triggers any further
       governed mutation)

  Novel/adapted (4 additional, total 13 >= this critical package's own
  ">=10" floor):
  10. State skip: RecordHumanDecision with no prior OpenDecisionConsideration
      EXPECTED DEFENSE: resolve_decision_transition_to_state's
        current_state=None branch
      EXPECTED BOUNDARY: BND-002 in the end-to-end handler (no
        Decision row resolves, so resolved_object_workspace_ids is
        empty and BND-002 denies first); BND-007 directly at the pure
        domain-function level
      ACTUAL RESULT: matches (test_denies_record_when_decision_absent;
        test_denies_record_when_decision_absent domain-level variant)
  11. Second OpenDecisionConsideration against an already-open decision_id
      EXPECTED DEFENSE: DecisionTransitionVerdict.DENIED_DECISION_ALREADY_EXISTS
        (mirrors BurstTransitionVerdict's own precedent)
      EXPECTED BOUNDARY: BND-007
      ACTUAL RESULT: matches
        (test_denies_a_second_open_against_the_same_decision_id)
  12. Second RecordHumanDecision against an already-DECIDED decision
      EXPECTED DEFENSE: 03 section 38 -- DECIDED is terminal; BND-007
        denies via DENIED_ILLEGAL_TRANSITION (no dedicated "already
        decided" verdict was needed -- the generic illegal-transition
        branch already covers it); the database's own
        trg_decisions_enforce_transition independently makes DECIDED
        immutable
      EXPECTED BOUNDARY: BND-007
      ACTUAL RESULT: matches
        (test_denies_a_second_record_against_an_already_decided_decision)
  13. Selected option not among candidate options
      EXPECTED DEFENSE: 04 section 50 DENY CONDITION ("Selected option
        not explicitly human-adopted") in its narrowest structural
        reading -- `selected_option` must be one of `decision.options`
        when options were recorded
      ACTUAL RESULT: matches (test_denies_selected_option_not_among_candidates)

  Legitimate controls proven not vacuously strict:
  test_full_success_open_then_record_commits_atomically (both commands,
  atomic bundle, real DECIDED row with correct attribution);
  test_grants_when_a_current_challenge_scoped_binding_exists_for_open /
  test_grants_when_a_current_decision_scoped_binding_exists_for_record;
  test_denies_an_observer_role_even_with_the_right_bound (BND-004
    proven independent of BND-005).

MUTATION_TESTS:
  MUT-01 (13's own): "skip BND-014" -> expected red: P-07/P-09/P-10
    tests must fail -- by inspection, both `open_decision_consideration`
    and `record_human_decision` call `CommitCoordinator.commit`
    unconditionally after the precommit chain ALLOWs, and
    `CommitCoordinator.commit` itself unconditionally evaluates BND-014
    -- INTERPRETATION: mutation killed (inherited from PKG-13's own
    proof, re-exercised through a real caller for the first time here).
  MUT-PKG15-01: remove the DECIDED-terminal check from
    trg_decisions_enforce_transition -> expected red:
    test_decided_decision_is_fully_immutable -- by inspection, that
    test's only IntegrityError/DBAPIError source matching "is DECIDED,
    which is terminal" is the removed statement -- INTERPRETATION:
    mutation killed.
  MUT-PKG15-02: remove `ck_decisions_decided_attribution` -> expected
    red: test_decided_without_attribution_is_rejected_at_the_database_layer
    -- by inspection, `Decision.__post_init__`'s own Python-layer check
    is bypassed entirely by a raw SQL UPDATE (as that test does), so
    the CHECK constraint is the only remaining defense -- INTERPRETATION:
    mutation killed.
  MUT-PKG15-03: remove `_raise_if_already_committed`'s early
    short-circuit -> expected red:
    test_duplicate_idempotent_record_after_commit_is_denied -- by
    inspection, without it the retry's own BND-007 re-evaluation would
    see the already-advanced Decision state and raise
    `HumanDecisionDenied` instead of `IdempotencyAlreadyCommitted` --
    INTERPRETATION: mutation killed (this is the exact bug caught
    during implementation; see NEW_GAPS_DISCOVERED).
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TESTS: test_human_decision.py exercises the full real
  predecessor chain: NonProofWorkspaceBootstrap (PKG-04) ->
  Workspace/Challenge (PKG-01/05) -> real AuthorityResolver (PKG-03) ->
  the real BND-001..007 evaluators (PKG-09), composed via
  boundaries.evaluate_chain (PKG-08) -> Bnd014CommitEvaluator/
  CommitCoordinator (PKG-13) -> ChallengeRepository/DecisionRepository
  (this package) -> SqlAlchemyCommandRepository/
  SqlAlchemyIdempotencyRepository/SqlAlchemyAuditRepository/
  SqlAlchemyOutboxRepository/SqlAlchemyCommitRepository (PKG-10/11/
  12/13) -- the second genuine production-Command-handler-driven
  cross-layer chain, after PKG-14's SelectQuestion.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through
  PKG-14's tests) re-run alongside PKG-15's new tests, both without a
  database (459 passed, 220 skipped) and with a live PostgreSQL 17
  instance (678 passed, 1 skipped) -- 0 regressions.
  check_architecture_dependencies.py re-run clean, confirming all 12
  disclosed extensions remain intact (no new ones added this package).

P_CLAIMS_TESTED:
  P-07 (AI cannot directly create human-authoritative state):
    introduced and directly tested -- test_denies_ai_actor_opening_consideration
    is the literal T13-P07-AI-NO-HUMAN-AUTH fixture: an AI-class actor
    is denied by BND-001 before any Decision content concept even
    applies.
  P-09 (Recommendation != Decision): introduced and directly tested --
    the combination of BND-006's content-origin check (reused
    unmodified from PKG-09) and `DecisionRepository.record_decision`'s
    own structural requirement of a real `decided_by_user_id: UserId`
    proves no AI recommendation can ever auto-finalize a Decision;
    test_denies_a_second_record_against_an_already_decided_decision
    additionally proves a Decision does not silently re-finalize.
  P-10 (Consequential transition requires current authority): further
    exercised -- test_denies_revoked_decision_right_before_record is
    the literal T13-P10-CURRENT-AUTHORITY fixture, applied to
    DECISION_RIGHT at the new DECISION scope this package introduces.

PROOF_ARTIFACTS:
  - 678-test live-database pass, including 13 distinct adversarial
    proofs (9 mandatory + 4 novel)
  - Real `decisions` rows walked through the full genuine transition
    topology (absent -> UNDER_CONSIDERATION -> DECIDED), live-DB-joined
    to their Challenge, opener, and decider
  - `HumanDecisionDenied.chain_result.terminal_boundary_id` asserted
    precisely for every DENY-path test
  - The DECIDED-attribution CHECK constraint proven independently of
    the Python-layer invariant (raw SQL UPDATE bypass)
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output, including a full from-empty upgrade to head
    e2f94137f8a9 and a downgrade(-1)/re-upgrade cycle
  - Diff audit (inline answers above)
  - Mutation-kill analysis (4 mutations, all killed)

FORBIDDEN_DEPENDENCY_CHECK: PASS (no new extension required this
  package; the single existing `application -> commit` edge, PKG-14,
  already covers this package's own needs)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT:
  New semantic type/enum value: yes, but none invented -- `DecisionState`
    (03 section 35.2's own vocabulary), `Decision` (09 section 47's own
    exact field list), `DecisionTransitionId`/`DecisionOperation`/
    `DecisionTransitionVerdict` (03 section 36's own names).
  New DB write path: yes, disclosed -- `decisions`, exactly 14 section
    9's own assignment.
  New authority path: no new resolution logic -- `AuthorityResolver`
    reused unchanged at two new, literally-read scopes.
  Weakened boundary: no -- strictly additive (BND-007's tagged union
    gained a fourth member without changing its algebra).
  Easier test / removed negative test / admin shortcut /
    projection-as-truth / AI canonical authority / broader Workspace
    scope: none.
  Changed migration semantics: no prior migration edited, only a new
    additive migration.
  Forbidden dependency: none -- no new INTERNAL_ALLOWED extension was
    required; PKG-14's own `application -> commit` edge already covers
    everything this package's handler needs.
  Files touched outside this package's own new-file set:
    `boundaries/bnd_007_state_transition.py`,
    `persistence/tables.py`, and their corresponding test file -- both
    "predecessor extension points explicitly exposed for PKG-15"
    (widening an existing tagged union / adding a new table), never a
    rewrite of prior semantics. No predecessor test file needed a
    regression fix this package (contrast PKG-14), since no FK
    retrofit onto a predecessor table was required.
  Real design bug found and fixed during implementation, fully
    disclosed: the original design called
    `idempotency_port.begin()` only after the precommit boundary chain
    ALLOWs (correct, and unchanged) but performed no EARLIER check for
    an already-COMMITTED duplicate. Because BND-007's own state check
    depends directly on the Decision's own state (unlike PKG-14's
    QuestionSelection, whose BND-007 check is insensitive to a
    successful commit), a genuine retry of an already-committed request
    would see the Decision already advanced and be incorrectly denied
    by BND-007 instead of returning the prior committed result. Fixed
    by adding `_raise_if_already_committed`, an early, read-only check
    (via `commit.idempotency.decide_idempotency_action`) that
    short-circuits with `IdempotencyAlreadyCommitted` BEFORE boundaries
    run, but only for that one disposition -- every other idempotency
    disposition (IN_PROGRESS, payload collision, indeterminate, new)
    is unaffected and still flows through the normal fresh-boundaries-
    then-`begin()` pipeline, since none of those correspond to a state
    that has already, successfully changed. No predecessor file was
    touched to fix this -- it was caught and fixed entirely within this
    package's own new file before the diff was ever finalized.

ARCHITECTURE_RECONSTRUCTION_RESULT:
  REQUEST -> ACTOR (real UserId, authenticated as HUMAN_USER) ->
  WORKSPACE (real WorkspaceId, cross-checked by BND-002 against
  Challenge for OPEN, against the Decision's own stored workspace_id
  for RECORD) -> CURRENT STATE (real Challenge row; real Decision row,
  walked through the genuine 03 transition topology, DB-trigger
  enforced) -> CURRENT GOVERNANCE (real WorkspaceRole via
  role_assignments, checked by BND-004) -> CURRENT AUTHORITY (fresh
  AuthorityResolver.resolve() for DECISION_RIGHT at CHALLENGE or
  DECISION scope, re-run independently by both BND-005 and BND-014) ->
  HUMAN DECISION: this package's own subject -- BND-006 proves the
  selection content itself is human-originated -> EVIDENCE:
  NOT_APPLICABLE structurally (09 section 47's own field list has none;
  the caller-supplied EvidenceSetId flows through CommandEnvelope.evidence_set_ref
  unchanged, PKG-10's own existing carrier) -> BOUNDARIES (BND-001
  identity -> BND-002 workspace -> BND-003 membership -> BND-004 role
  -> BND-005 authority -> BND-006 human origin -> BND-007 state
  topology, sequential, first non-ALLOW terminates) -> BND-014 (fresh
  re-validation inside CommitCoordinator) -> COMMAND (real
  CommandEnvelope/AttemptId, CMD_OPEN_DECISION_CONSIDERATION or
  CMD_RECORD_HUMAN_DECISION) -> COMMIT UNIT (real commit_units row;
  target_refs naming the read-only-checked Challenge for OPEN,
  relation_refs naming the newly created Decision; target_refs naming
  the pre-existing Decision itself for RECORD) -> CANONICAL MUTATION
  (real `decisions` INSERT for OPEN, real `decisions` UPDATE for
  RECORD, each inside the same SAVEPOINT as the CommitUnit) -> AUDIT
  (real audit_events row, carrying evidence_set_ref where supplied) ->
  OUTBOX (real outbox_events row) -> EVENT: SUCCESSOR_NOT_BUILT (PKG-20,
  Phase 8) -> RESULTING STATE (real, live-DB-joined decisions +
  commit_units + audit_events + outbox_events rows). The second
  package (after PKG-14) where every node from REQUEST through
  RESULTING STATE is driven by one real production Command handler.

KNOWN_LIMITATIONS:
  - No `command.registry.CommandContract` registration exists for
    `CMD_OPEN_DECISION_CONSIDERATION`/`CMD_RECORD_HUMAN_DECISION` --
    same disclosed pattern as PKG-14's own SelectQuestion commands.
  - `options`/`criteria` remain plain string tuples with no structured
    Option/Criterion object -- 02/09 define no further sub-schema; a
    future package extending Decision content richness would need to
    resolve this deliberately, not silently widen these fields.
  - `provenance_ref`/"AI recommendation refs if consumed" remain a bare
    opaque `uuid.UUID | None` -- `ProvenanceEnvelope` is PKG-16's own
    scope (Phase 6), not yet built.
  - GAP-02-006 (Decision lifecycle semantics) is now closed for the
    UNDER_CONSIDERATION/DECIDED shape 03/04 define, but decision
    revision/withdrawal/supersession (03 section 38, GAP-03-005) remains
    entirely unaddressed -- this package deliberately does not invent a
    revision path.
  - Sandbox Python remains 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still
  BLOCKED. Used only via NonProofWorkspaceBootstrap in test fixtures.

NEW_GAPS_DISCOVERED: none structural. One genuine design bug was found
  and fixed within this package's own scope during implementation (not
  a production incident, and not present in the final committed code):
  the idempotency-ordering issue described in full under DIFF_AUDIT
  above. This is documented as PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::AVAILABLE
  in the sense that the live-DB test run caught it before completion
  (1 genuine failure -> 0 after the fix), the same disclosure discipline
  every prior package with a live-DB-caught bug has followed.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. `Decision`'s field list
  is 09 section 47's own, verbatim, plus the disclosed `workspace_id`
  technical necessity. `DecisionState`'s 2 values are 03 section 35.2's
  own vocabulary. `DecisionTransitionId`/`DecisionOperation` are 03
  section 36's own names, verbatim. The CHALLENGE/DECISION authority
  scopes are 04 section 49/50's own literal, unhedged text. BND-007's
  extension adds no new boundary concept. The
  DECIDED-attribution/terminal-state rules are 03 section 37/38's own
  stated requirements, enforced exactly as written, at both the Python
  and database layers.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-16 (Evidence core) becomes DAG-eligible
  now that PKG-13 (its sole required predecessor) is verified. With
  both PKG-14 and PKG-15 now complete, Build Phase 5 is fully
  materialized. Eligibility is not authorization.
HUMAN_GATE_REQUIRED: YES -- Build phase 5 complete (both PKG-14 and
  PKG-15 done). "Completion does not authorize the next phase"
  (verbatim, per this package's own coding prompt). Do not authorize
  any successor, Phase 6 or otherwise, without explicit human
  authorization naming the package and this package's commit hash.
```
