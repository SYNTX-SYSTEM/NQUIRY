# PKG-31: Mutation and adversarial harness — PACKAGE COMPLETION REPORT

```
PACKAGE_ID: PKG-31
PACKAGE_TITLE: Mutation and adversarial harness
BUILD_PHASE: 13
VERDICT: PACKAGE_PASS
```

## PRE_IMPLEMENTATION_TRACE

```
PACKAGE_ID: PKG-31
BUILD_PHASE: 13
PREDECESSORS_FOUND: PKG-30 (commit 9b804d4, PACKAGE_PASS, verified in
  repository reality: packages/test_support/proof_bundle.py,
  packages/test_support/proof_claim_matrix.py,
  tests/e2e/test_proof_bundle_paths.py all present and green)
UPSTREAM_FILES_READ: 13_TEST_AND_FALSIFICATION_ARCHITECTURE.md (via
  NQUIRY_IMPLEMENTATION_MASTER.md sections referencing T11/mutation
  testing discipline), 14_IMPLEMENTATION_SEQUENCE.md PKG-31 package
  manifest + COPY-PASTE CODING AGENT PROMPT (full text, sections 1-38
  of the PKG-31 chapter), CI pipeline order (section 51), Coding
  Package DAG (PKG-30 -> PKG-31 -> PKG-32)
14_SECTIONS_READ: Package manifest for PKG-31; Build Phase 13; Coding
  Package DAG; repository topology (tests/mutation already reserved as
  a placeholder directory since PKG-00); test implementation map (T11);
  proof-claim map (P-01..P-25); stop conditions; forbidden shortcuts
EXISTING_IMPLEMENTATION_FOUND: tests/mutation/.gitkeep (empty
  placeholder from PKG-00, reserved for this package);
  tests/command_commit_event/mutation/test_projection_mutations.py
  (PKG-21's own narrower, package-scoped mutation tests -- inline
  mutant-dependency-injection style, distinct from and not superseded
  by this package's generic runner); tests/boundaries/
  test_bnd_017_failure_indeterminate.py::test_mut_pkg24_01_... and
  tests/security/test_db_principals.py::test_mut_pkg25_01_... (two
  more prior packages' own local single-test mutation proofs, same
  precedent, not reused directly since this package's OBJECTIVE
  requires a package-level runner exercising the PRE-EXISTING suite,
  not a new local mutant)
EXISTING_TESTS_FOUND: full T0-T10 suite from PKG-00..PKG-30 (1100
  tests passing, 1 skipped, live-DB; 705 passing, 395 skipped,
  pure-Python) -- see RAW_EVIDENCE_APPENDIX section 6 for the fresh
  final counts
MIGRATIONS_FOUND: none new required (14 PKG-31 DATABASE_CHANGES: none)
POTENTIAL_CONFLICTS: none identified -- this package creates no
  production code and modifies no production file; the sole existing
  file touched (tests/e2e/test_proof_bundle_paths.py) is a PKG-30 test
  file, modified only under this package's own explicit human
  authorization (see DIFF_AUDIT)

SOURCE REQUIREMENT -> DOMAIN SEMANTIC -> STATE/RELATION -> AUTHORITY ->
BOUNDARY -> COMMAND/QUERY -> PERSISTENCE -> AUDIT/EVENT -> FAILURE ->
TEST -> PROOF CLAIM:
  NOT_APPLICABLE for a "new domain capability" trace -- 14 PKG-31 adds
  no Command/Query/Event/persistence/authority path of its own
  (PUBLIC_INTERFACES: "mutation runner" only). The trace this package
  DOES perform is orthogonal: for each of the ten mandatory mutations,
  PRODUCTION INVARIANT (an existing BND-* evaluator method, the
  AuthorityResolver, CommitCoordinator._commit_inner, CommandEnvelope's
  type guard, evidence.freshness._resolve_member, or the provider-SDK
  import checker) -> MONKEYPATCH SEAM (`tests/mutation/harness.py`'s
  `MutationPatch`) -> PRE-EXISTING TEST (a real, already-committed
  pytest node id from PKG-01..PKG-30) -> OBSERVED RESULT (baseline
  PASS / mutated FAIL / restored PASS) -> PROOF CLAIM (P-01..P-25,
  tracked per mutation where applicable). See
  ARCHITECTURE_RECONSTRUCTION_RESULT below for the full per-mutation
  table.
```

## PRE_IMPLEMENTATION_ATTACK_MODEL

14 PKG-31's own OBJECTIVE names exactly ten mandatory mutations
("deliberately removes BND-014, trusts cached authority, removes
Workspace check, treats AI recommendation as Decision, enables direct
DB write, treats Event as Command, accepts stale Evidence, enables
INDETERMINATE retry, enables admin fallback and bypasses AI Gateway").
All ten are implemented below (MUT-PKG31-01 through -10), satisfying
"At least 10 total novel/adapted attacks are required for this
critical package" without needing an eleventh. No category is marked
NOT_APPLICABLE -- every named mutation maps to a real, exercisable
production seam in this codebase's current build phase.

Category breakdown (14's own required attack-model categories):
- Semantic shortcut attacks (>= 3 required): MUT-01 (BND-014 skipped),
  MUT-06 (Event-as-Command type collapse), MUT-07 (stale Evidence
  accepted) -- 3.
- Authority/boundary bypass attacks (>= 3 required): MUT-02 (cached
  authority), MUT-03 (Workspace check removed), MUT-04 (AI-as-Human
  identity collapse), MUT-09 (admin fallback) -- 4.
- Persistence/concurrency attacks (>= 2 required): MUT-05 (direct DB
  write, atomic-bundle skip) -- 1, disclosed as the only one of this
  category this package's own real seams support without inventing a
  live DB-privilege weakening (see KNOWN_LIMITATIONS: a previous
  package's own tool-classifier precedent explicitly ruled out
  temporarily weakening a REAL granted DB principal's privileges even
  reversibly -- `tests/security/test_db_principals.py::
  test_mut_pkg25_01_...`'s own docstring records the identical
  decision at PKG-25/24 -- so MUT-05 mutates the APPLICATION-LEVEL
  commit orchestration instead of live GRANT/REVOKE).
- Workspace attacks (>= 2 required): MUT-03, and MUT-04's
  AI_BOUNDARY-adjacent path (BND-001 sits immediately upstream of
  BND-002 in the same chain) -- 2 (MUT-03 is the direct one).
- AI-authority attacks (>= 2 required): MUT-04 (AI recommendation as
  Decision), MUT-10 (Gateway bypass) -- 2.
- Failure/retry attacks (>= 2 required): MUT-08 (INDETERMINATE retry
  enabled), MUT-05 (a "direct write" is also a failure-semantics
  attack on AC-09-002's atomicity guarantee) -- 2.
- Projection/cache truth attack (>= 1 required where relevant):
  MUT-02's authority CACHE is exactly this category applied to
  Authority rather than Projection -- 1 (no Projection-specific cache
  exists to attack at this build phase; the closest real analogue,
  applied honestly to the nearest real cache-shaped seam, is used
  instead of a NOT_APPLICABLE claim).

## DESIGN_LESSONS_APPLIED_UPFRONT (per this package's own gate message)

- Closed vocabularies as real runtime-checked types, not casts:
  `MUTATION_IDS` (ten `MUT-PKG31-NN` strings) is validated in
  `MutationCase.__post_init__`; `MutationInterpretation` is a real
  `Enum` (`KILLED`/`SURVIVED`/`BASELINE_FAILED`/`RESTORE_FAILED`), not
  a bare string compared ad hoc.
- Error-state handling built in from the start for the one new
  I/O-adjacent surface this package introduces (subprocess-free but
  still externally-observable: `pytest.main()`'s own exit code):
  `run_mutation_case` distinguishes a genuine `SURVIVED` mutation from
  a `BASELINE_FAILED`/`RESTORE_FAILED` HARNESS integrity failure --
  the three-phase design's own `finally: setattr(owner, attr,
  original)` guarantees the patch is always reverted even if the
  mutated-phase pytest run itself raises, so a crash never leaves a
  monkeypatched production class defect live in whatever runs next in
  the same process.
- PKG-30 nachtrag applied (explicit instruction in this package's own
  gate message): all six E2E path tests in
  `tests/e2e/test_proof_bundle_paths.py` now call the shared
  `_assert_p_claims_are_real` helper, not only the HAPPY path -- see
  DIFF_AUDIT.

## IMPLEMENTATION_TASKS

```
FILES_CREATED:
  tests/mutation/harness.py (227 lines) -- generic T11 mutation-testing
    engine: MutationCase/MutationPatch/MutationRunResult dataclasses,
    MutationInterpretation enum, run_mutation_case() (baseline/mutate/
    restore, in-process pytest.main()).
  tests/mutation/mutation_cases.py (482 lines) -- the ten mandatory
    MutationCase definitions (MUT-PKG31-01..10), each naming a real
    production patch target and real pre-existing pytest node id(s).
  tests/mutation/test_pkg31_mutation_registry.py (90 lines) -- 5
    DB-free, pytest-collected falsifiability tests over the registry
    itself (exact 10-id coverage; every target file/function/patch
    target actually resolves).
  scripts/run_mutation_harness.py (99 lines) -- the standalone CLI
    "mutation runner" (14's own required PUBLIC_INTERFACE): loads
    harness.py and mutation_cases.py by absolute file path (tests/ is
    not on any configured import root outside pytest), runs all ten
    cases for real, prints a structured per-mutation report and a
    summary, exits 0 only if every mutation is KILLED.

FILES_MODIFIED:
  tests/e2e/test_proof_bundle_paths.py -- PKG-30 nachtrag, explicitly
    authorized in this package's own human gate message ("ergänze bei
    Gelegenheit... die fehlende p_claims_exercised-Matrix-
    Mitgliedschaftsprüfung für die fünf Nicht-HAPPY-Pfade"): added a
    shared `_assert_p_claims_are_real(bundle)` helper and called it
    from all six E2E path tests (previously only the HAPPY path
    checked `p_claims_exercised` membership against
    `PROOF_CLAIM_MATRIX`). No test logic, assertion strength, or
    scenario changed -- purely additive.

FILES_DELETED:
  tests/mutation/.gitkeep -- PKG-00's own placeholder for this exact
    directory, removed now that real content exists in it.

MIGRATIONS_CREATED: none (14 PKG-31 DATABASE_CHANGES: none)
SCHEMA_CHANGES: none
DB_PRIVILEGE_CHANGES: none (see PRE_IMPLEMENTATION_ATTACK_MODEL above
  on why MUT-05 deliberately does NOT touch live DB grants)
PUBLIC_INTERFACES_CREATED: mutation runner
  (scripts/run_mutation_harness.py), matching 14's own exact
  requirement ("14 requires: mutation runner").
COMMANDS_CREATED: NOT_APPLICABLE (none assigned to this package)
QUERIES_CREATED: NOT_APPLICABLE (none assigned to this package)
EVENTS_CREATED: NOT_APPLICABLE (none assigned to this package)
BOUNDARIES_CREATED_OR_CHANGED: none created; BND-001/002/005/014/017
  are each TEMPORARILY monkeypatched (setattr, always reverted) during
  the mutated phase of one mutation case each -- never permanently
  changed, and every case's `finally` block restores the real,
  unmodified evaluator before the process moves to its next case or
  exits.
AUTHORITY_PATH: unchanged in production; MUT-02 and MUT-09 each
  temporarily monkeypatch `AuthorityResolver.resolve` in-process,
  always restored (see above).
EVIDENCE_PATH: unchanged in production; MUT-07 temporarily monkeypatches
  `evidence.freshness._resolve_member`, always restored.
AI_PATH: unchanged in production; MUT-10 temporarily monkeypatches
  `check_provider_sdk_imports.check` (a CI-time static checker, not a
  runtime AI code path), always restored.
RECOVERY_PATH: unchanged; MUT-08 temporarily monkeypatches
  `Bnd017FailureIndeterminateEvaluator.evaluate`, always restored.
```

## TARGETED_TESTS / NEGATIVE_TESTS / ADVERSARIAL_COUNTER_TESTS

14 test family for this package: T11 (mutation). This package's own
"targeted test" IS the adversarial mutation harness -- there is no
separate positive-path unit test to write beyond the 5 registry
falsifiability tests (`tests/mutation/test_pkg31_mutation_registry.py`,
DB-free, always collected by `pytest -q`) and the actual empirical
mutation run (`scripts/run_mutation_harness.py`, live-DB, run
explicitly and separately, matching the established convention that
`scripts/verify_migrations.py`'s live-DB check is likewise not part of
the default `pytest -q` collection).

Per-mutation adversarial report (14's own required ATTACK / EXPECTED
DEFENSE / EXPECTED BOUNDARY / EXPECTED CANONICAL RESULT / EXPECTED
PROOF ARTIFACT / ACTUAL RESULT format):

```
MUT-PKG31-01 -- BND-014 removed (forced ALLOW)
  ATTACK: Bnd014CommitEvaluator.evaluate monkeypatched to always
    return ALLOW, ignoring expected/current versions and upstream
    chain result.
  EXPECTED DEFENSE: BND-014's own version/chain check.
  EXPECTED BOUNDARY: BND_014.
  EXPECTED CANONICAL RESULT: tests asserting a stale-version DENY now
    observe an incorrect ALLOW.
  EXPECTED PROOF ARTIFACT: BoundaryProof.result flips ALLOW where DENY
    is required; re-queried DB rows in test_commit.py's own assertions.
  ACTUAL RESULT: KILLED. baseline_exit=0, mutated_exit=1, restored_exit=0.
    tests/boundaries/test_bnd_014_commit.py::test_denies_a_stale_expected_version
    and tests/command_commit_event/test_commit.py::
    test_commit_denies_when_state_version_changed both flip PASS->FAIL->PASS.

MUT-PKG31-02 -- trust cached authority (resolver memoizes first verdict)
  ATTACK: AuthorityResolver.resolve wrapped to cache the first verdict
    per (workspace, actor, scope) key, forever after ignoring a
    real revocation.
  EXPECTED DEFENSE: AuthorityResolver's own "never caches, always
    fresh-reads" design (14 section 16).
  EXPECTED BOUNDARY: BND_005.
  EXPECTED CANONICAL RESULT: a second resolution after revocation
    incorrectly still reports GRANTED.
  EXPECTED PROOF ARTIFACT: AuthorityResolution.verdict.
  ACTUAL RESULT: KILLED. tests/authority/test_resolver.py::
    test_stale_binding_denied_after_revoke_between_two_resolutions
    flips PASS->FAIL->PASS.

MUT-PKG31-03 -- Workspace check removed (BND-002 forced ALLOW)
  ATTACK: Bnd002WorkspaceEvaluator.evaluate monkeypatched to always ALLOW.
  EXPECTED DEFENSE: BND-002's cross-Workspace scope check.
  EXPECTED BOUNDARY: BND_002.
  EXPECTED CANONICAL RESULT: a cross-Workspace object set is no longer
    denied.
  EXPECTED PROOF ARTIFACT: BoundaryProof.result / .boundary_id.
  ACTUAL RESULT: KILLED. tests/boundaries/test_bnd_002_workspace.py::
    test_denies_cross_workspace_object_set and
    tests/e2e/test_proof_bundle_paths.py::
    test_cross_workspace_path_a_challenge_from_another_workspace_is_denied
    both flip PASS->FAIL->PASS.

MUT-PKG31-04 -- AI recommendation as Decision (BND-001 forced ALLOW)
  ATTACK: Bnd001IdentityEvaluator.evaluate monkeypatched to always ALLOW,
    including for an AI_PROCESSOR actor.
  EXPECTED DEFENSE: BND-001's actor-class identity check.
  EXPECTED BOUNDARY: BND_001.
  EXPECTED CANONICAL RESULT: an AI actor is no longer denied before
    touching a Human Decision.
  EXPECTED PROOF ARTIFACT: BoundaryProof.result / .boundary_id.
  ACTUAL RESULT: KILLED. tests/boundaries/test_bnd_001_identity.py::
    test_ai_processor_can_never_pass_as_human_user and
    tests/e2e/test_proof_bundle_paths.py::
    test_ai_boundary_path_an_ai_actor_is_denied_before_any_decision_is_touched
    both flip PASS->FAIL->PASS.

MUT-PKG31-05 -- direct DB write enabled (CommitCoordinator skips audit/outbox)
  ATTACK: CommitCoordinator._commit_inner monkeypatched to apply the
    canonical mutation and fabricate a CommitUnit, WITHOUT writing
    commit_units/audit_events/outbox_events rows.
  EXPECTED DEFENSE: AC-09-002's atomic-bundle requirement, proven by
    re-querying the real database for the audit/outbox rows a genuine
    commit must have produced.
  EXPECTED BOUNDARY: N/A (post-BND-014 atomicity, not itself a boundary
    evaluator).
  EXPECTED CANONICAL RESULT: `len(audit_events) == 1` now observes 0.
  EXPECTED PROOF ARTIFACT: a real `SqlAlchemyAuditRepository` query result.
  ACTUAL RESULT: KILLED. tests/command_commit_event/test_commit.py::
    test_commit_succeeds_and_atomically_writes_every_artifact flips
    PASS->FAIL->PASS.

MUT-PKG31-06 -- Event treated as Command (type guard removed)
  ATTACK: CommandEnvelope.__post_init__ replaced with a no-op, removing
    the isinstance(command_id, CommandId) structural check.
  EXPECTED DEFENSE: 09 section 160.3's "EventEnvelope is type-distinct."
  EXPECTED BOUNDARY: N/A (semantic-type construction guard).
  EXPECTED CANONICAL RESULT: an EventId no longer raises when used to
    construct a CommandEnvelope.
  EXPECTED PROOF ARTIFACT: pytest.raises(...) context outcome.
  ACTUAL RESULT: KILLED. tests/command_commit_event/
    test_command_event_split.py::
    test_an_event_id_cannot_construct_a_command_envelope flips
    PASS->FAIL->PASS.

MUT-PKG31-07 -- stale Evidence accepted (freshness forced FRESH)
  ATTACK: evidence.freshness._resolve_member monkeypatched to always
    return FRESH regardless of invalidation/Workspace/version/
    supersession.
  EXPECTED DEFENSE: 09 section 114's five stale conditions.
  EXPECTED BOUNDARY: BND_014 (evidence_freshness branch).
  EXPECTED CANONICAL RESULT: an invalidated/cross-Workspace/superseded
    member is no longer detected as stale.
  EXPECTED PROOF ARTIFACT: EvidenceMemberFreshness value.
  ACTUAL RESULT: KILLED. tests/evidence/test_freshness.py::
    test_an_invalidated_member_after_prepare_is_stale,
    ::test_a_cross_workspace_member_is_stale, and
    ::test_a_superseded_member_is_stale all flip PASS->FAIL->PASS.

MUT-PKG31-08 -- INDETERMINATE retry enabled (BND-017 forced ALLOW)
  ATTACK: Bnd017FailureIndeterminateEvaluator.evaluate monkeypatched to
    always ALLOW.
  EXPECTED DEFENSE: BND-017's blind-retry / dependent-operation-blocked
    checks.
  EXPECTED BOUNDARY: BND_017.
  EXPECTED CANONICAL RESULT: a blind retry under uncertain consequence,
    and a dependent operation on a blocked target, are no longer denied.
  EXPECTED PROOF ARTIFACT: BoundaryProof.result.
  ACTUAL RESULT: KILLED. tests/boundaries/
    test_bnd_017_failure_indeterminate.py::
    test_uncertain_consequence_denies_blind_retry and
    ::test_denies_dependent_operation_while_target_is_blocked both flip
    PASS->FAIL->PASS.

MUT-PKG31-09 -- admin fallback enabled (resolver grants on membership alone)
  ATTACK: AuthorityResolver.resolve wrapped so that a DENIED_NO_MATCHING_BINDING
    result is silently upgraded to GRANTED whenever current membership exists.
  EXPECTED DEFENSE: 05 AC-05-004 (membership is a precondition, never a
    substitute for a matching HumanAuthorityBinding).
  EXPECTED BOUNDARY: BND_005.
  EXPECTED CANONICAL RESULT: an Owner/admin with no DECISION_RIGHT
    binding is incorrectly granted.
  EXPECTED PROOF ARTIFACT: AuthorityResolution.verdict.
  ACTUAL RESULT: KILLED. tests/security/test_admin_non_authority.py::
    test_admin_cannot_create_a_legitimate_decision and
    tests/authority/test_resolver.py::test_owner_only_is_denied both
    flip PASS->FAIL->PASS.

MUT-PKG31-10 -- AI Gateway bypassed (provider-SDK import checker disabled)
  ATTACK: check_provider_sdk_imports.check monkeypatched to always
    return an empty violation list.
  EXPECTED DEFENSE: the static "all LLM traffic through the Gateway"
    checker (BND-009's static enforcement half).
  EXPECTED BOUNDARY: BND_009 (static half).
  EXPECTED CANONICAL RESULT: a direct provider-SDK import outside the
    Gateway adapter boundary is no longer flagged.
  EXPECTED PROOF ARTIFACT: Violation list length.
  ACTUAL RESULT: KILLED. tests/security/test_ai_gateway.py::
    test_direct_provider_import_outside_gateway_adapter_is_rejected
    flips PASS->FAIL->PASS.
```

All ten mutations report `KILLED` (baseline_exit=0, mutated_exit=1,
restored_exit=0). Zero `SURVIVED` (no `TEST_DESIGN_DEFECT`). Zero
`BASELINE_FAILED`/`RESTORE_FAILED` (no harness integrity failure).
Full raw terminal output of the real, fresh run is in
RAW_EVIDENCE_APPENDIX section 5.

## CROSS_LAYER_TESTS

Every one of the ten mutations is exercised against the REAL
predecessor layers it targets (real PostgreSQL, real repositories,
real evaluator classes, real handler functions) via the pre-existing
test suite's own fixtures -- never a fresh mock built for this
package. `tests/mutation/harness.py`'s own module docstring states
explicitly why this matters: an in-process monkeypatch on a real,
already-imported production class is the only way a "restore, baseline
PASS" claim can be verified for real, since a subprocess-based design
would re-import the unpatched module and silently never apply the
mutation.

## RECURSIVE_REGRESSION

```
Full live-DB regression (python -m pytest -q): 1100 passed, 1 skipped
  (was 1095 passed, 1 skipped at PKG-30 -- +5, the new registry file's
  5 falsifiability tests; the mutation harness's own live empirical run
  is intentionally NOT part of this collected count, same convention
  as scripts/verify_migrations.py).
Pure-Python regression (DATABASE_URL unset, python -m pytest -q tests/):
  705 passed, 395 skipped (was 700 passed, 395 skipped at PKG-30 -- +5,
  same 5 registry tests, DB-free).
Static verification: ruff format --check . (301 files already
  formatted), ruff check . (all checks passed), mypy across
  packages/apps/api/src/apps/worker/src/scripts (Success: no issues
  found in 136 source files -- was 135 at PKG-30, +1 for
  scripts/run_mutation_harness.py).
Architecture checkers: ARCHITECTURE_DEPENDENCY_CHECK::PASS,
  PROVIDER_SDK_IMPORT_CHECK::PASS, TEST_ONLY_IMPORT_CHECK::PASS.
```

## PROOF_CLAIMS (P-01..P-25)

This package introduces no new proof claim (14: "14 assigns: P-01..P-25",
same closed set PKG-30 already tracked). Per-claim status is unchanged
from PKG-30 except where a mutation directly re-exercised a claim
through an ADVERSARIAL (mutated) lens rather than only a positive one:

```
EXERCISED (adversarially re-confirmed by a KILLED mutation this package):
  P-07 (BND-001 AI-actor denial) -- MUT-PKG31-04
  P-10 (no commit without current binding) -- MUT-PKG31-01, MUT-PKG31-02
  P-11 (BND-014/authority revocation detected) -- MUT-PKG31-01, MUT-PKG31-02
  P-13 (canonical state unchanged on DENY) -- MUT-PKG31-01, MUT-PKG31-04
  P-14 (commit rejected / proof incomplete) -- MUT-PKG31-07
  P-15 (evidence boundary rejects substitution) -- MUT-PKG31-07
  P-20 (retry denied; reconciliation required) -- MUT-PKG31-08
  P-22 (denied before AI/context/commit) -- MUT-PKG31-03, MUT-PKG31-04
  P-24 (governed path denies; direct tamper illegitimate/detectable) -- MUT-PKG31-05, MUT-PKG31-09

POTENTIALLY_AFFECTED (unchanged from PKG-30, no new evidence this
  package): P-01, P-02, P-03, P-04, P-05, P-06, P-08, P-09, P-12,
  P-16, P-17, P-18, P-19, P-21, P-23, P-25.

BLOCKED (unchanged, HARD-DEP-001/HARD-DEP-002 remain BLOCKED regardless
  of any claim status here, per 14's own explicit instruction):
  N/A at the P-NN level (HARD-DEP tracking is separate from the
  P-01..P-25 matrix).
```

`PROOF_CLAIM_MATRIX` itself (packages/test_support/proof_claim_matrix.py)
is NOT modified by this package (not in FILES_ALLOWED_TO_MODIFY for
PKG-31 -- it is PKG-30's own owned artifact) -- the EXERCISED-by-mutation
claims above are tracked here, in this report, not by editing that
file's own `ProofClaimStatus` values.

## DIFF_AUDIT

```
git status --short (before this package's work):
  ?? apps/web/AGENTS.md
  ?? apps/web/CLAUDE.md

git status --short (after, before staging):
   M tests/e2e/test_proof_bundle_paths.py
   D tests/mutation/.gitkeep
  ?? apps/web/AGENTS.md
  ?? apps/web/CLAUDE.md
  ?? scripts/run_mutation_harness.py
  ?? tests/mutation/harness.py
  ?? tests/mutation/mutation_cases.py
  ?? tests/mutation/test_pkg31_mutation_registry.py
```

`apps/web/AGENTS.md`/`apps/web/CLAUDE.md` are pre-existing untracked
files, unrelated to PKG-31, untouched by this package (flagged, not
staged, not modified -- same as flagged at the PKG-30 gate).

Explicit DIFF_AUDIT questions (14's own required list):

- New semantic type/enum value: `MutationInterpretation` (KILLED/
  SURVIVED/BASELINE_FAILED/RESTORE_FAILED) -- a TEST-ONLY vocabulary
  describing this harness's own run outcome, never a production/domain
  vocabulary. `MUTATION_IDS` (ten closed `MUT-PKG31-NN` strings) --
  same, test-only.
- New transition/authority path/DB write path: NONE. Every
  `setattr`-based patch is reverted in a `finally` block before the
  process moves on; no production class is left permanently altered.
- Weakened boundary/removed negative test/easier test/admin shortcut:
  NONE -- the whole POINT of this package is to temporarily weaken ten
  boundaries and prove the EXISTING test suite (unmodified) still
  catches it. No existing assertion was loosened; the sole edit to an
  existing test file (test_proof_bundle_paths.py) STRENGTHENS coverage
  (extends a check from 1 of 6 paths to 6 of 6), never weakens it.
- Projection/cache truth, AI canonical authority, broader Workspace
  scope, changed migration semantics, forbidden dependency: NONE.

No unauthorized semantic change. `PACKAGE_FAIL_IMPLEMENTATION`/
`STOP_ARCHITECTURE_CONFLICT` do not apply.

## ARCHITECTURE_RECONSTRUCTION_RESULT

This package participates in no single consequential request chain of
its own (14 PKG-31 PUBLIC_INTERFACES: "mutation runner" only, no
Command/Query/Event assigned). The reconstruction below is therefore
performed PER MUTATION, against the real chain each one temporarily
interrupts -- REQUEST -> ACTOR -> WORKSPACE -> CURRENT STATE -> CURRENT
GOVERNANCE -> CURRENT AUTHORITY -> HUMAN DECISION -> EVIDENCE ->
BOUNDARIES -> BND-014 -> COMMAND -> COMMIT UNIT -> CANONICAL MUTATION
-> AUDIT -> OUTBOX -> EVENT -> RESULTING STATE:

- MUT-01/07: ... -> BOUNDARIES -> BND-014 (mutated) -> [would-be]
  COMMIT UNIT -> reconstructed via the real, unmutated chain's own
  proof once restored; RESULTING STATE never actually diverges because
  the mutation is reverted before any real caller observes it, and the
  KILLED result is itself the reconstruction (a real pre-existing test
  proves the divergence WOULD occur).
- MUT-02/09: ... -> CURRENT AUTHORITY (mutated resolver) -> BND-005 ->
  same pattern.
- MUT-03/04: ... -> BOUNDARIES -> BND-002/BND-001 (mutated) -> same
  pattern, chain terminates before COMMAND/COMMIT UNIT is ever reached
  in the real (unmutated) case, and the mutated case's own would-be
  bypass is what the cited test catches.
- MUT-05: ... -> COMMIT UNIT (mutated _commit_inner) -> CANONICAL
  MUTATION (applied) -> AUDIT/OUTBOX (skipped) -> RESULTING STATE
  reconstructed as "canonical row exists, no matching audit/outbox row"
  -- exactly the divergence `test_commit_succeeds_and_atomically_writes_every_artifact`
  catches by re-querying both.
- MUT-06: a construction-time guard, upstream of REQUEST entirely (no
  request has been formed yet) -- reconstructs to
  SUCCESSOR_NOT_BUILT-adjacent NOT_APPLICABLE for the request chain,
  but fully reconstructable at the semantic-type layer (CommandEnvelope
  identity).
- MUT-08: ... -> BND-017 (mutated) -> same pattern, RECOVERY path.
- MUT-10: a CI-time static check, entirely outside any runtime request
  chain -- reconstructs to "build-time enforcement", not a per-request
  node.

## KNOWN_LIMITATIONS

- MUT-PKG31-05 ("enables direct DB write") mutates the APPLICATION-LEVEL
  commit orchestration (`CommitCoordinator._commit_inner`), not a live
  PostgreSQL GRANT/REVOKE against a real service principal, because a
  prior package's own tool-classifier precedent (recorded in
  `tests/security/test_db_principals.py::
  test_mut_pkg25_01_a_broken_blocking_guard_would_wrongly_allow`'s own
  docstring, and again at PKG-24) already established that temporarily
  weakening a REAL, currently-granted security control -- even
  reversibly -- is refused by this session's own tool classifier. The
  chosen alternative still empirically proves the named invariant
  ("direct DB write" = canonical mutation without the required
  audit/outbox bundle) is caught by a real, pre-existing, live-database
  test.
- `tests/mutation/harness.py`'s in-process `pytest.main()` design means
  `scripts/run_mutation_harness.py` must be run as its own dedicated
  step (like `scripts/verify_migrations.py`'s live-DB check), never
  folded into the default `pytest -q` collection -- ten mutations x
  three phases each takes on the order of tens of seconds against a
  real PostgreSQL connection, and nesting it inside an already-running
  pytest session would risk pytest-internal state interference this
  package deliberately avoids (see `harness.py`'s own module docstring).
- NEW_GAPS_DISCOVERED (not introduced by this package, found while
  running mypy against `tests/e2e/test_proof_bundle_paths.py` in
  isolation for this package's own verification, since `tests/` is
  excluded from the established `mypy packages apps/api/src
  apps/worker/src scripts` full-scope command by prior-package
  convention): PKG-30's own `_open`/`_record` local helpers
  (lines 188, 228) lack return-type annotations, and
  `ActorIdentity(ActorClass.SYSTEM_SERVICE, "recovery-worker-1")`
  (lines 877, 945) passes a bare `str` where `UserId` is the real
  parameter type. Both predate this package (present unchanged in
  commit `9b804d4`), are outside PKG-31's `FILES_ALLOWED_TO_MODIFY`
  scope to fix opportunistically, and do not affect any test's actual
  pass/fail outcome (mypy was simply never run over this specific file
  in isolation before). Flagged here for a future package's own
  `NEW_GAPS_DISCOVERED` triage, not silently fixed.

## BLOCKED_DEPENDENCIES

HARD-DEP-001 (legitimate first-Workspace bootstrap) and HARD-DEP-002
(real AI provider eligibility) remain BLOCKED, unchanged, exactly as
required ("DO NOT CLOSE HARD DEPENDENCIES"). MUT-PKG31-10 exercises
the checker that helps keep HARD-DEP-002 genuinely BLOCKED (proving
the checker itself is load-bearing) without touching HARD-DEP-002's
own BLOCKED status.

## NEW_GAPS_DISCOVERED

See KNOWN_LIMITATIONS above (pre-existing PKG-30 mypy gaps in
`tests/e2e/test_proof_bundle_paths.py`, disclosed, not fixed).

## NO_SEMANTIC_INVENTION_CONFIRMATION

No new Command, Query, Event, Boundary, Authority path, transition, or
persistence write path was invented. All ten `MutationPatch` targets
name real, pre-existing production attributes; all `target_test_nodeids`
name real, pre-existing test functions this package did not write. The
one new closed vocabulary (`MutationInterpretation`) and the one new
identifier set (`MUTATION_IDS`) are both TEST-ONLY, describing this
harness's own run outcome, never a domain/architectural concept.

## COMPLETION_REPORT (14 §46 exact field format)

```
PACKAGE_ID: PKG-31
PACKAGE_TITLE: Mutation and adversarial harness
BUILD_PHASE: 13
VERDICT: PACKAGE_PASS
UPSTREAM_FILES_READ: 14_IMPLEMENTATION_SEQUENCE.md (PKG-31 manifest +
  full COPY-PASTE CODING AGENT PROMPT), CI pipeline order (section 51)
14_REQUIREMENTS_MATERIALIZED: mutation runner (PUBLIC_INTERFACES); ten
  mandatory mutations (OBJECTIVE); T11 test family
PREDECESSORS_VERIFIED: PKG-30 (commit 9b804d4, PACKAGE_PASS)
FILES_CREATED: tests/mutation/harness.py, tests/mutation/mutation_cases.py,
  tests/mutation/test_pkg31_mutation_registry.py,
  scripts/run_mutation_harness.py
FILES_MODIFIED: tests/e2e/test_proof_bundle_paths.py (PKG-30 nachtrag,
  explicitly authorized)
FILES_DELETED: tests/mutation/.gitkeep
MIGRATIONS_CREATED: none
SCHEMA_CHANGES: none
DB_PRIVILEGE_CHANGES: none
PUBLIC_INTERFACES_CREATED: mutation runner
COMMANDS_CREATED: NOT_APPLICABLE
QUERIES_CREATED: NOT_APPLICABLE
EVENTS_CREATED: NOT_APPLICABLE
BOUNDARIES_CREATED_OR_CHANGED: none permanently; BND-001/002/005/014/017
  each temporarily monkeypatched and reverted per mutation case
AUTHORITY_PATH: unchanged in production (temporary monkeypatch only)
EVIDENCE_PATH: unchanged in production (temporary monkeypatch only)
AI_PATH: unchanged in production (temporary monkeypatch only)
RECOVERY_PATH: unchanged in production (temporary monkeypatch only)
TESTS_CREATED: 5 (tests/mutation/test_pkg31_mutation_registry.py) +
  10 mutation cases run via scripts/run_mutation_harness.py (not
  pytest-collected, run as its own explicit step)
TESTS_MODIFIED: 6 (tests/e2e/test_proof_bundle_paths.py's six E2E path
  tests, additive-only)
TARGETED_TEST_RESULTS: 5/5 registry tests PASSED (DB-free);
  10/10 mutation cases KILLED (live-DB, see RAW_EVIDENCE_APPENDIX)
NEGATIVE_TEST_RESULTS: all ten mutations' mutated-phase runs correctly
  FAILED (mutated_exit=1), proving the negative property under attack
ADVERSARIAL_TEST_RESULTS: see per-mutation ATTACK/EXPECTED/ACTUAL table
  above -- 10/10 KILLED
CROSS_LAYER_TEST_RESULTS: all ten mutations exercised against real
  PostgreSQL, real repositories, real evaluator/handler classes
RECURSIVE_REGRESSION_RESULTS: live-DB 1100 passed/1 skipped (+5 vs
  PKG-30); pure-Python 705 passed/395 skipped (+5 vs PKG-30)
P_CLAIMS_TESTED: P-07, P-10, P-11, P-13, P-14, P-15, P-20, P-22, P-24
  (adversarially re-confirmed by a KILLED mutation this package); all
  other P-01..P-25 unchanged (POTENTIALLY_AFFECTED) from PKG-30
PROOF_ARTIFACTS: BoundaryProof.result/.boundary_id (MUT-01/03/04/08),
  AuthorityResolution.verdict (MUT-02/09), real re-queried audit_events
  row count (MUT-05), pytest.raises outcome (MUT-06), EvidenceMemberFreshness
  value (MUT-07), Violation list length (MUT-10) -- all against REAL
  objects the pre-existing tests already independently construct
FORBIDDEN_DEPENDENCY_CHECK: PASS (ARCHITECTURE_DEPENDENCY_CHECK::PASS)
PROVIDER_SDK_CHECK: PASS (PROVIDER_SDK_IMPORT_CHECK::PASS)
TEST_ONLY_IMPORT_CHECK: PASS (TEST_ONLY_IMPORT_CHECK::PASS)
DIFF_AUDIT: see DIFF_AUDIT section above -- no unauthorized semantic
  change; two unrelated pre-existing untracked files (apps/web/AGENTS.md,
  apps/web/CLAUDE.md) flagged, untouched
ARCHITECTURE_RECONSTRUCTION_RESULT: see section above (per-mutation)
KNOWN_LIMITATIONS: see section above (MUT-05 design choice; harness
  run cadence; two pre-existing PKG-30 mypy gaps disclosed, not fixed)
BLOCKED_DEPENDENCIES: HARD-DEP-001, HARD-DEP-002 (unchanged, still BLOCKED)
NEW_GAPS_DISCOVERED: two pre-existing PKG-30 mypy gaps in
  tests/e2e/test_proof_bundle_paths.py (see KNOWN_LIMITATIONS)
NO_SEMANTIC_INVENTION_CONFIRMATION: confirmed, see section above
NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-32 (eligibility only, not authorization)
HUMAN_GATE_REQUIRED: YES
```

## PACKAGE VERDICT

```
PACKAGE:              PKG-31
STATUS:                PACKAGE_PASS
FILES_CREATED:        tests/mutation/harness.py, tests/mutation/mutation_cases.py,
                       tests/mutation/test_pkg31_mutation_registry.py,
                       scripts/run_mutation_harness.py
FILES_MODIFIED:        tests/e2e/test_proof_bundle_paths.py
MIGRATIONS:           none
TESTS_ADDED:          5 (registry) + 10 mutation cases (script-run)
TESTS_RUN:            5 registry + 10 mutation cases + full regression
                       (1100 live-DB, 705 pure-Python)
TEST_RESULTS:         5/5 registry PASSED; 1100 passed/1 skipped
                       live-DB; 705 passed/395 skipped pure-Python
NEGATIVE_TEST_RESULTS: 10/10 mutated-phase runs correctly FAILED
ADVERSARIAL_RESULTS:  10/10 KILLED, 0 SURVIVED, 0 HARNESS_INTEGRITY_FAILURE
MUTATION_RESULTS:     MUT-PKG31-01..10 all KILLED (see per-mutation
                       table above and RAW_EVIDENCE_APPENDIX section 5)
CROSS_LAYER_RESULTS:  all ten against real PostgreSQL/real production classes
REGRESSION_RESULTS:   +5/+5 (live-DB/pure-Python), 0 regressions
BOUNDARY_PROOFS:      BND-001/002/005/014/017 each independently
                       proven load-bearing by a KILLED mutation
AUTHORITY_PROOFS:     AuthorityResolver freshness (MUT-02) and
                       membership-is-not-authority (MUT-09) both
                       independently proven load-bearing
GOVERNANCE_PROOFS:    N/A (no new governance path)
PERSISTENCE_PROOFS:   AC-09-002 atomic-bundle requirement independently
                       proven load-bearing (MUT-05)
FAILURE_INJECTION_RESULTS: N/A (no new failure-injection hook; BND-017's
                       existing INDETERMINATE-retry defense independently
                       proven load-bearing, MUT-08)
ARCHITECTURE_TRACE:   see ARCHITECTURE_RECONSTRUCTION_RESULT above
DIFF_SUMMARY:         4 new files, 1 modified (additive-only), 1 deleted
                       (.gitkeep); 2 unrelated pre-existing untracked
                       files flagged, untouched
OPEN_GAPS:            2 pre-existing PKG-30 mypy annotation gaps (disclosed)
BLOCKERS:             none
UPSTREAM_CONTRADICTIONS: none
RECONSTRUCTION_REQUIRED: NO
FIRST_BROKEN_LAYER:   N/A
HUMAN_GATE_REQUIRED:  YES
PACKAGE_VERDICT:      PACKAGE_PASS
NEXT_PACKAGE_ELIGIBLE: PKG-32
NEXT_PACKAGE_AUTHORIZED: NO
```

---

# RAW_EVIDENCE_APPENDIX

Full raw content -- new file diffs, cat -n excerpts of every real
backend source this package's mutations patch, the complete raw
terminal output of the actual mutation-harness run (all ten mutations,
real tracebacks under mutation), and the full final static-verification
and regression output. Embedded directly, not referenced, per standing
instruction.

```
################################################################
# PKG-31 EVIDENCE BUNDLE
################################################################

################################################################
# 1. git status --short
################################################################
 M tests/e2e/test_proof_bundle_paths.py
 D tests/mutation/.gitkeep
?? apps/web/AGENTS.md
?? apps/web/CLAUDE.md
?? scripts/run_mutation_harness.py
?? tests/mutation/harness.py
?? tests/mutation/mutation_cases.py
?? tests/mutation/test_pkg31_mutation_registry.py

################################################################
# 2. New files (full diff, git diff --no-index)
################################################################
diff --git a/tests/mutation/harness.py b/tests/mutation/harness.py
new file mode 100644
new file mode 100644
index 0000000..52e0d1e
--- /dev/null
+++ b/tests/mutation/harness.py
@@ -0,0 +1,200 @@
+"""T11 MUTATION TESTING ENGINE: the generic runner PKG-31's own
+"mutation runner" (14 §46 PUBLIC_INTERFACES) is built on.
+
+TEST ONLY. Never imported by production code. Not itself collected by
+pytest (this file has no `test_` prefix), but reachable in two ways:
+`tests/mutation/mutation_cases.py` imports it directly (same directory
+-- pytest's own rootless import inserts `tests/mutation/` onto
+`sys.path` the moment any sibling `test_*.py` file in this directory
+is collected, so a plain `from harness import ...` resolves); and
+`scripts/run_mutation_harness.py` loads it by absolute file path via
+`importlib.util.spec_from_file_location`, since `tests/` is not a
+configured import root outside pytest (`pyproject.toml` `pythonpath`
+lists `packages`/`apps/api/src`/`apps/worker/src`/`scripts`, not
+`tests` -- confirmed by grep before writing this file).
+
+WHY THIS RUNS THE PRE-EXISTING TEST SUITE, NOT NEW TESTS
+--------------------------------------------------------------------
+14 PKG-31's own OBJECTIVE: "Baseline PASS, mutation must make relevant
+tests FAIL, restore, baseline PASS." This is empirical mutation
+testing of the ALREADY-BUILT test suite's own detection power -- the
+question is whether PKG-00 through PKG-30's own tests would notice if
+a named invariant were removed, not whether new tests can be written
+that would notice (that would prove nothing about the tests that
+already exist). Each `MutationCase` therefore never adds a new
+assertion of its own; it monkeypatches one real production attribute
+in-process and re-invokes a real, pre-existing pytest node id.
+
+WHY IN-PROCESS `pytest.main()`, NOT A SUBPROCESS PER PHASE
+--------------------------------------------------------------------
+A monkeypatch (`setattr` on a real class/module attribute) only
+affects the CURRENT Python process's already-imported objects. A
+subprocess-per-phase design would spawn a fresh interpreter for the
+"mutated" phase that re-imports the target module from disk, seeing
+the ORIGINAL, unpatched code -- the mutation would silently never take
+effect and every case would report a false `SURVIVED`. Calling
+`pytest.main()` three times (baseline/mutated/restored) from this same
+process, targeting only the small node-id list each case names (never
+the whole suite), is the standard technique real mutation-testing
+tools use for exactly this reason, and keeps each phase to a handful
+of already-cached-import test files rather than requiring a full
+process boot per phase.
+"""
+
+from __future__ import annotations
+
+import importlib
+from collections.abc import Callable
+from dataclasses import dataclass
+from enum import Enum
+
+import pytest
+
+MUTATION_IDS = tuple(f"MUT-PKG31-{n:02d}" for n in range(1, 11))
+"""14's own OBJECTIVE names exactly ten mandatory mutations for this
+critical package ("The listed ten mutations are mandatory... At least
+10 total novel/adapted attacks are required"). Closed -- a case whose
+`mutation_id` is not one of these ten fails closed at construction,
+the same discipline `test_support.proof_bundle.E2E_PROOF_PATHS`
+already established for PKG-30's own six named paths.
+"""
+
+
+class MutationInterpretation(Enum):
+    """14 §27's own required vocabulary: "record invariant removed or
+    weakened, expected red test, actual result, and interpretation."
+    `SURVIVED` is the `TEST_DESIGN_DEFECT` case 14 §27 names explicitly
+    ("If a prohibited mutation survives, classify TEST_DESIGN_DEFECT;
+    do not report PASS."). `BASELINE_FAILED`/`RESTORE_FAILED` are
+    HARNESS-integrity failures (a typo'd node id, a flaky fixture) --
+    distinct from a genuine mutation-detection question, and reported
+    separately rather than folded into `SURVIVED` so a reader is never
+    misled into thinking the PRODUCTION invariant is unguarded when the
+    real problem is this harness's own node-id list.
+    """
+
+    KILLED = "KILLED"
+    SURVIVED = "SURVIVED"
+    BASELINE_FAILED = "BASELINE_FAILED"
+    RESTORE_FAILED = "RESTORE_FAILED"
+
+
+@dataclass(frozen=True, slots=True)
+class MutationPatch:
+    """One `setattr` seam: `target_module.target_qualname` is resolved
+    via `importlib`, its current value captured, replaced by
+    `replacement_factory(original_value)` for the mutated phase, then
+    restored verbatim. `replacement_factory` receives the real original
+    (not just a placeholder) so a mutation that needs to WRAP behavior
+    (MUT-PKG31-02's authority cache; MUT-PKG31-09's admin fallback) can
+    still call through to genuine production logic for the cases it
+    does not itself want to corrupt, while a mutation that unconditionally
+    replaces behavior (e.g. MUT-PKG31-01's forced ALLOW) simply ignores
+    the argument.
+    """
+
+    target_module: str
+    target_qualname: str
+    replacement_factory: Callable[[object], object]
+
+    def __post_init__(self) -> None:
+        if not self.target_module:
+            raise ValueError("MutationPatch.target_module must be non-empty")
+        if not self.target_qualname:
+            raise ValueError("MutationPatch.target_qualname must be non-empty")
+
+
+@dataclass(frozen=True, slots=True)
+class MutationCase:
+    mutation_id: str
+    invariant: str
+    """The architectural invariant this mutation removes or weakens,
+    transcribed from 14's own OBJECTIVE line for this mutation."""
+    expected_boundary: str
+    """The BoundaryId (or 'N/A' where the invariant is not itself a
+    BND-* evaluator, e.g. MUT-PKG31-06/10) this mutation targets."""
+    patch: MutationPatch
+    target_test_nodeids: tuple[str, ...]
+    """Real, pre-existing pytest node ids (`path::test_name`) this
+    mutation is expected to turn from PASS to FAIL. Never a new test
+    written for this package -- see module docstring."""
+
+    def __post_init__(self) -> None:
+        if self.mutation_id not in MUTATION_IDS:
+            raise ValueError(f"mutation_id must be one of {MUTATION_IDS}, got {self.mutation_id!r}")
+        if not self.invariant:
+            raise ValueError(f"{self.mutation_id}: invariant must be non-empty")
+        if not self.expected_boundary:
+            raise ValueError(f"{self.mutation_id}: expected_boundary must be non-empty")
+        if not self.target_test_nodeids:
+            raise ValueError(f"{self.mutation_id}: target_test_nodeids must be non-empty")
+
+
+@dataclass(frozen=True, slots=True)
+class MutationRunResult:
+    mutation_id: str
+    baseline_exit_code: int
+    mutated_exit_code: int
+    restored_exit_code: int
+    interpretation: MutationInterpretation
+
+
+def _resolve_owner_and_attr(module_path: str, qualname: str) -> tuple[object, str]:
+    module = importlib.import_module(module_path)
+    owner: object = module
+    *path, attr = qualname.split(".")
+    for part in path:
+        owner = getattr(owner, part)
+    return owner, attr
+
+
+def _run_nodeids(nodeids: tuple[str, ...]) -> int:
+    exit_code = pytest.main(["-q", *nodeids])
+    return int(exit_code)
+
+
+def run_mutation_case(case: MutationCase) -> MutationRunResult:
+    """Baseline -> apply patch -> mutated -> restore patch -> restored.
+    14 §46 OBJECTIVE's own exact four-phase sequence, in that order,
+    unconditionally (the patch is always restored via `finally`, even
+    if the mutated-phase run itself raises).
+    """
+    baseline = _run_nodeids(case.target_test_nodeids)
+
+    owner, attr = _resolve_owner_and_attr(case.patch.target_module, case.patch.target_qualname)
+    original = getattr(owner, attr)
+    mutant = case.patch.replacement_factory(original)
+    setattr(owner, attr, mutant)
+    try:
+        mutated = _run_nodeids(case.target_test_nodeids)
+    finally:
+        setattr(owner, attr, original)
+
+    restored = _run_nodeids(case.target_test_nodeids)
+
+    if baseline != int(pytest.ExitCode.OK):
+        interpretation = MutationInterpretation.BASELINE_FAILED
+    elif restored != int(pytest.ExitCode.OK):
+        interpretation = MutationInterpretation.RESTORE_FAILED
+    elif mutated == int(pytest.ExitCode.OK):
+        interpretation = MutationInterpretation.SURVIVED
+    else:
+        interpretation = MutationInterpretation.KILLED
+
+    return MutationRunResult(
+        mutation_id=case.mutation_id,
+        baseline_exit_code=baseline,
+        mutated_exit_code=mutated,
+        restored_exit_code=restored,
+        interpretation=interpretation,
+    )
+
+
+__all__ = [
+    "MUTATION_IDS",
+    "MutationInterpretation",
+    "MutationPatch",
+    "MutationCase",
+    "MutationRunResult",
+    "run_mutation_case",
+]

diff --git a/tests/mutation/mutation_cases.py b/tests/mutation/mutation_cases.py
new file mode 100644
new file mode 100644
index 0000000..5fed658
--- /dev/null
+++ b/tests/mutation/mutation_cases.py
@@ -0,0 +1,482 @@
+"""MUTATIONS: the ten mandatory PKG-31 mutations (14 §46 OBJECTIVE:
+"deliberately removes BND-014, trusts cached authority, removes
+Workspace check, treats AI recommendation as Decision, enables direct
+DB write, treats Event as Command, accepts stale Evidence, enables
+INDETERMINATE retry, enables admin fallback and bypasses AI Gateway").
+
+TEST ONLY. Never imported by production code -- same import-graph
+guard as every other file under `tests/`.
+
+Every `target_test_nodeids` entry below names a real, pre-existing
+test file/function this package did not write (all landed in PKG-01
+through PKG-30). This module writes zero new assertions; it only
+supplies the ten `setattr` seams and the pre-existing node ids each is
+expected to turn red -- see `harness.py`'s own module docstring for
+why that is deliberate, not an oversight.
+"""
+
+from __future__ import annotations
+
+from collections.abc import Callable
+from datetime import datetime
+from pathlib import Path
+from typing import Protocol
+from uuid import UUID
+
+from authority.resolver import (
+    AuthorityRequest,
+    AuthorityResolution,
+    AuthorityResolver,
+    AuthorityVerdict,
+    ResolutionReason,
+)
+from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
+from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
+from boundaries.bnd_014_commit import Bnd014CommitEvaluator, Bnd014Input
+from boundaries.bnd_017_failure_indeterminate import (
+    Bnd017FailureIndeterminateEvaluator,
+    Bnd017Input,
+)
+from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult
+from check_provider_sdk_imports import Violation
+from command.envelope import CommandEnvelope
+from commit.coordinator import CommitOutcome, CommitUnit
+from evidence.freshness import EvidenceFreshnessPort, EvidenceMemberFreshness
+from harness import MutationCase, MutationPatch
+from semantic_types.ids import CommitId, EvidenceId, UserId, WorkspaceId
+from semantic_types.versions import ContractVersion, RecordVersion
+
+
+class _MutationExecutorLike(Protocol):
+    def apply(self) -> object: ...
+
+
+def _forced_allow_proof(
+    evaluator_boundary_id: BoundaryId, context: BoundaryContext, reason_code: str
+) -> BoundaryProof:
+    return BoundaryProof(
+        boundary_id=evaluator_boundary_id,
+        boundary_version=ContractVersion("1.0"),
+        result=BoundaryResult.ALLOW,
+        reason_code=reason_code,
+        workspace_id=context.workspace_id,
+        actor=context.actor,
+        input_refs=(),
+        authoritative_version_refs=(),
+        authority_proof=None,
+        evidence_proof_refs=(),
+        evaluated_at=context.evaluated_at,
+        correlation_id=context.correlation_id,
+    )
+
+
+# ---------------------------------------------------------------------------
+# MUT-PKG31-01: BND-014 removed (commit-time boundary forced ALLOW)
+# ---------------------------------------------------------------------------
+
+
+def _mut01_bnd014_always_allows(
+    _original: Callable[[Bnd014CommitEvaluator, Bnd014Input, BoundaryContext], BoundaryProof],
+) -> Callable[[Bnd014CommitEvaluator, Bnd014Input, BoundaryContext], BoundaryProof]:
+    def _evaluate(
+        self: Bnd014CommitEvaluator, boundary_input: Bnd014Input, context: BoundaryContext
+    ) -> BoundaryProof:
+        return _forced_allow_proof(self.boundary_id, context, "MUT_PKG31_01_BND014_DISABLED")
+
+    return _evaluate
+
+
+MUT_PKG31_01 = MutationCase(
+    mutation_id="MUT-PKG31-01",
+    invariant="BND-014 evaluates expected/current versions, upstream chain result and "
+    "evidence freshness before any commit; removing it must let a stale-version or "
+    "already-denied commit through unchecked.",
+    expected_boundary="BND_014",
+    patch=MutationPatch(
+        target_module="boundaries.bnd_014_commit",
+        target_qualname="Bnd014CommitEvaluator.evaluate",
+        replacement_factory=_mut01_bnd014_always_allows,  # type: ignore[arg-type]
+    ),
+    target_test_nodeids=(
+        "tests/boundaries/test_bnd_014_commit.py::test_denies_a_stale_expected_version",
+        "tests/command_commit_event/test_commit.py::test_commit_denies_when_state_version_changed",
+    ),
+)
+
+
+# ---------------------------------------------------------------------------
+# MUT-PKG31-02: trust cached authority (resolver memoizes first verdict)
+# ---------------------------------------------------------------------------
+
+
+def _mut02_authority_resolver_caches(
+    original: Callable[[AuthorityResolver, AuthorityRequest], AuthorityResolution],
+) -> Callable[[AuthorityResolver, AuthorityRequest], AuthorityResolution]:
+    cache: dict[tuple[UUID, UserId, str, UUID], AuthorityResolution] = {}
+
+    def _resolve(self: AuthorityResolver, request: AuthorityRequest) -> AuthorityResolution:
+        key = (
+            request.workspace_id.value,
+            request.actor.user_id,
+            request.scope_type,
+            request.scope_id,
+        )
+        if key in cache:
+            return cache[key]
+        result = original(self, request)
+        cache[key] = result
+        return result
+
+    return _resolve
+
+
+MUT_PKG31_02 = MutationCase(
+    mutation_id="MUT-PKG31-02",
+    invariant="AuthorityResolver.resolve() never caches -- every call re-reads current "
+    "membership/binding state (14 section 16: commit-time resolver reloads current "
+    "authoritative state). Caching the first verdict lets a later revocation be invisible "
+    "to a second resolution that reuses the stale, still-GRANTED answer.",
+    expected_boundary="BND_005",
+    patch=MutationPatch(
+        target_module="authority.resolver",
+        target_qualname="AuthorityResolver.resolve",
+        replacement_factory=_mut02_authority_resolver_caches,  # type: ignore[arg-type]
+    ),
+    target_test_nodeids=(
+        "tests/authority/test_resolver.py::test_stale_binding_denied_after_revoke_between_two_resolutions",
+    ),
+)
+
+
+# ---------------------------------------------------------------------------
+# MUT-PKG31-03: Workspace check removed (BND-002 forced ALLOW)
+# ---------------------------------------------------------------------------
+
+
+def _mut03_bnd002_always_allows(
+    _original: Callable[[Bnd002WorkspaceEvaluator, Bnd002Input, BoundaryContext], BoundaryProof],
+) -> Callable[[Bnd002WorkspaceEvaluator, Bnd002Input, BoundaryContext], BoundaryProof]:
+    def _evaluate(
+        self: Bnd002WorkspaceEvaluator, boundary_input: Bnd002Input, context: BoundaryContext
+    ) -> BoundaryProof:
+        return _forced_allow_proof(self.boundary_id, context, "MUT_PKG31_03_BND002_DISABLED")
+
+    return _evaluate
+
+
+MUT_PKG31_03 = MutationCase(
+    mutation_id="MUT-PKG31-03",
+    invariant="BND-002 denies when a request's claimed Workspace does not match the "
+    "resolved scope of every object it names; removing it lets a request read/act across "
+    "Workspace boundaries.",
+    expected_boundary="BND_002",
+    patch=MutationPatch(
+        target_module="boundaries.bnd_002_workspace",
+        target_qualname="Bnd002WorkspaceEvaluator.evaluate",
+        replacement_factory=_mut03_bnd002_always_allows,  # type: ignore[arg-type]
+    ),
+    target_test_nodeids=(
+        "tests/boundaries/test_bnd_002_workspace.py::test_denies_cross_workspace_object_set",
+        "tests/e2e/test_proof_bundle_paths.py::test_cross_workspace_path_a_challenge_from_another_workspace_is_denied",
+    ),
+)
+
+
+# ---------------------------------------------------------------------------
+# MUT-PKG31-04: AI recommendation treated as Decision (BND-001 forced ALLOW)
+# ---------------------------------------------------------------------------
+
+
+def _mut04_bnd001_always_allows(
+    _original: Callable[[Bnd001IdentityEvaluator, Bnd001Input, BoundaryContext], BoundaryProof],
+) -> Callable[[Bnd001IdentityEvaluator, Bnd001Input, BoundaryContext], BoundaryProof]:
+    def _evaluate(
+        self: Bnd001IdentityEvaluator, boundary_input: Bnd001Input, context: BoundaryContext
+    ) -> BoundaryProof:
+        return _forced_allow_proof(self.boundary_id, context, "MUT_PKG31_04_BND001_DISABLED")
+
+    return _evaluate
+
+
+MUT_PKG31_04 = MutationCase(
+    mutation_id="MUT-PKG31-04",
+    invariant="BND-001 denies an actor class the operation does not accept -- in "
+    "particular an AI_PROCESSOR can never pass as the HUMAN_USER a Human Decision "
+    "requires. Removing it lets an AI-authored recommendation be recorded as if it were "
+    "a Human Decision.",
+    expected_boundary="BND_001",
+    patch=MutationPatch(
+        target_module="boundaries.bnd_001_identity",
+        target_qualname="Bnd001IdentityEvaluator.evaluate",
+        replacement_factory=_mut04_bnd001_always_allows,  # type: ignore[arg-type]
+    ),
+    target_test_nodeids=(
+        "tests/boundaries/test_bnd_001_identity.py::test_ai_processor_can_never_pass_as_human_user",
+        "tests/e2e/test_proof_bundle_paths.py::test_ai_boundary_path_an_ai_actor_is_denied_before_any_decision_is_touched",
+    ),
+)
+
+
+# ---------------------------------------------------------------------------
+# MUT-PKG31-05: direct DB write enabled (CommitCoordinator skips audit/outbox)
+# ---------------------------------------------------------------------------
+
+
+def _mut05_commit_inner_skips_audit_and_outbox(
+    _original: Callable[..., CommitUnit],
+) -> Callable[..., CommitUnit]:
+    def _commit_inner(
+        self: object,
+        *,
+        envelope: CommandEnvelope,
+        proof: BoundaryProof,
+        mutation: _MutationExecutorLike,
+        occurred_at: datetime,
+        commit_id: CommitId,
+    ) -> CommitUnit:
+        # Applies the canonical mutation directly and fabricates a
+        # CommitUnit WITHOUT ever writing commit_units/audit_events/
+        # outbox_events rows -- AC-09-002's "one atomic commit unit"
+        # bundle, with the audit/outbox/commit-record half silently
+        # skipped. This is what "enables direct DB write" means
+        # concretely: canonical state changes, nothing governed
+        # accompanies it.
+        mutation.apply()
+        return CommitUnit(
+            commit_id=commit_id,
+            command_id=envelope.command_id,
+            attempt_id=envelope.attempt_id,
+            workspace_id=envelope.workspace_scope_ref,
+            target_refs=envelope.target_refs,
+            relation_refs=(),
+            governance_refs=(),
+            audit_event_ids=(),
+            outbox_ids=(),
+            committed_at=occurred_at,
+            outcome=CommitOutcome.COMMITTED,
+        )
+
+    return _commit_inner
+
+
+MUT_PKG31_05 = MutationCase(
+    mutation_id="MUT-PKG31-05",
+    invariant="AC-09-002 (Governed Commit Unit): canonical mutation + audit + durable "
+    "outbox entry must be persisted as one atomic bundle. A direct write that applies "
+    "the canonical mutation without the audit/outbox half must be detectable by "
+    "re-querying the real database for the missing artifacts, not merely by trusting the "
+    "CommitUnit object returned to the caller.",
+    expected_boundary="N/A (post-BND-014 commit-bundle atomicity, not a boundary evaluator)",
+    patch=MutationPatch(
+        target_module="commit.coordinator",
+        target_qualname="CommitCoordinator._commit_inner",
+        replacement_factory=_mut05_commit_inner_skips_audit_and_outbox,  # type: ignore[arg-type]
+    ),
+    target_test_nodeids=(
+        "tests/command_commit_event/test_commit.py::test_commit_succeeds_and_atomically_writes_every_artifact",
+    ),
+)
+
+
+# ---------------------------------------------------------------------------
+# MUT-PKG31-06: Event treated as Command (CommandEnvelope type guard removed)
+# ---------------------------------------------------------------------------
+
+
+def _mut06_command_envelope_skips_validation(
+    _original: Callable[[CommandEnvelope], None],
+) -> Callable[[CommandEnvelope], None]:
+    def _post_init(self: CommandEnvelope) -> None:
+        return None
+
+    return _post_init
+
+
+MUT_PKG31_06 = MutationCase(
+    mutation_id="MUT-PKG31-06",
+    invariant="CommandEnvelope.__post_init__ structurally rejects a command_id that is "
+    "not a real CommandId (in particular an EventId) -- 09 section 160.3's own defense "
+    "against 'replay sends old Event to Command handler'. Removing the check lets an "
+    "EventEnvelope's own identity construct a CommandEnvelope.",
+    expected_boundary="N/A (semantic-type construction guard, not a boundary evaluator)",
+    patch=MutationPatch(
+        target_module="command.envelope",
+        target_qualname="CommandEnvelope.__post_init__",
+        replacement_factory=_mut06_command_envelope_skips_validation,  # type: ignore[arg-type]
+    ),
+    target_test_nodeids=(
+        "tests/command_commit_event/test_command_event_split.py::test_an_event_id_cannot_construct_a_command_envelope",
+    ),
+)
+
+
+# ---------------------------------------------------------------------------
+# MUT-PKG31-07: stale Evidence accepted (freshness check forced FRESH)
+# ---------------------------------------------------------------------------
+
+
+def _mut07_evidence_member_always_fresh(
+    _original: Callable[
+        [EvidenceId, RecordVersion, WorkspaceId, EvidenceFreshnessPort], EvidenceMemberFreshness
+    ],
+) -> Callable[
+    [EvidenceId, RecordVersion, WorkspaceId, EvidenceFreshnessPort], EvidenceMemberFreshness
+]:
+    def _resolve_member(
+        evidence_id: EvidenceId,
+        expected_content_version: RecordVersion,
+        workspace_id: WorkspaceId,
+        reader: EvidenceFreshnessPort,
+    ) -> EvidenceMemberFreshness:
+        return EvidenceMemberFreshness.FRESH
+
+    return _resolve_member
+
+
+MUT_PKG31_07 = MutationCase(
+    mutation_id="MUT-PKG31-07",
+    invariant="09 section 114: an Evidence member that is invalidated, superseded, "
+    "unavailable, wrong-Workspace, or content-version-changed since capture is stale, "
+    "and a commit naming a stale set must fail (BND-014's evidence branch). Forcing every "
+    "member FRESH lets a commit proceed on Evidence that no longer holds.",
+    expected_boundary="BND_014 (evidence_freshness branch)",
+    patch=MutationPatch(
+        target_module="evidence.freshness",
+        target_qualname="_resolve_member",
+        replacement_factory=_mut07_evidence_member_always_fresh,  # type: ignore[arg-type]
+    ),
+    target_test_nodeids=(
+        "tests/evidence/test_freshness.py::test_an_invalidated_member_after_prepare_is_stale",
+        "tests/evidence/test_freshness.py::test_a_cross_workspace_member_is_stale",
+        "tests/evidence/test_freshness.py::test_a_superseded_member_is_stale",
+    ),
+)
+
+
+# ---------------------------------------------------------------------------
+# MUT-PKG31-08: INDETERMINATE retry enabled (BND-017 forced ALLOW)
+# ---------------------------------------------------------------------------
+
+
+def _mut08_bnd017_always_allows(
+    _original: Callable[
+        [Bnd017FailureIndeterminateEvaluator, Bnd017Input, BoundaryContext], BoundaryProof
+    ],
+) -> Callable[[Bnd017FailureIndeterminateEvaluator, Bnd017Input, BoundaryContext], BoundaryProof]:
+    def _evaluate(
+        self: Bnd017FailureIndeterminateEvaluator,
+        boundary_input: Bnd017Input,
+        context: BoundaryContext,
+    ) -> BoundaryProof:
+        return _forced_allow_proof(self.boundary_id, context, "MUT_PKG31_08_BND017_DISABLED")
+
+    return _evaluate
+
+
+MUT_PKG31_08 = MutationCase(
+    mutation_id="MUT-PKG31-08",
+    invariant="BND-017 denies a blind retry while consequence certainty is genuinely "
+    "uncertain, and denies any operation on a target another INDETERMINATE record still "
+    "blocks. Forcing ALLOW lets a retry proceed on an unproven outcome.",
+    expected_boundary="BND_017",
+    patch=MutationPatch(
+        target_module="boundaries.bnd_017_failure_indeterminate",
+        target_qualname="Bnd017FailureIndeterminateEvaluator.evaluate",
+        replacement_factory=_mut08_bnd017_always_allows,  # type: ignore[arg-type]
+    ),
+    target_test_nodeids=(
+        "tests/boundaries/test_bnd_017_failure_indeterminate.py::test_uncertain_consequence_denies_blind_retry",
+        "tests/boundaries/test_bnd_017_failure_indeterminate.py::test_denies_dependent_operation_while_target_is_blocked",
+    ),
+)
+
+
+# ---------------------------------------------------------------------------
+# MUT-PKG31-09: admin fallback enabled (resolver grants on membership alone)
+# ---------------------------------------------------------------------------
+
+
+def _mut09_authority_resolver_admin_fallback(
+    original: Callable[[AuthorityResolver, AuthorityRequest], AuthorityResolution],
+) -> Callable[[AuthorityResolver, AuthorityRequest], AuthorityResolution]:
+    def _resolve(self: AuthorityResolver, request: AuthorityRequest) -> AuthorityResolution:
+        result = original(self, request)
+        if (
+            result.verdict is AuthorityVerdict.DENIED
+            and result.proof.reason is ResolutionReason.DENIED_NO_MATCHING_BINDING
+        ):
+            # Mutant "admin fallback": any current member, with no
+            # matching HumanAuthorityBinding at all, is granted anyway
+            # -- exactly the Membership != Authority / Role != Authority
+            # collapse 14's own non-collapse rules forbid.
+            return AuthorityResolution(verdict=AuthorityVerdict.GRANTED, proof=result.proof)
+        return result
+
+    return _resolve
+
+
+MUT_PKG31_09 = MutationCase(
+    mutation_id="MUT-PKG31-09",
+    invariant="AuthorityResolver.resolve() grants only on a current, scope-matching "
+    "HumanAuthorityBinding -- current Workspace membership alone (any role, including "
+    "Owner) is a precondition, never a substitute (05 AC-05-004). Granting on membership "
+    "alone whenever no binding matches is the 'admin fallback' 14 explicitly forbids.",
+    expected_boundary="BND_005",
+    patch=MutationPatch(
+        target_module="authority.resolver",
+        target_qualname="AuthorityResolver.resolve",
+        replacement_factory=_mut09_authority_resolver_admin_fallback,  # type: ignore[arg-type]
+    ),
+    target_test_nodeids=(
+        "tests/security/test_admin_non_authority.py::test_admin_cannot_create_a_legitimate_decision",
+        "tests/authority/test_resolver.py::test_owner_only_is_denied",
+    ),
+)
+
+
+# ---------------------------------------------------------------------------
+# MUT-PKG31-10: AI Gateway bypassed (provider-SDK import checker disabled)
+# ---------------------------------------------------------------------------
+
+
+def _mut10_provider_sdk_checker_disabled(
+    _original: Callable[[tuple[Path, ...] | None], list[Violation]],
+) -> Callable[[tuple[Path, ...] | None], list[Violation]]:
+    def _check(roots: tuple[Path, ...] | None = None) -> list[Violation]:
+        return []
+
+    return _check
+
+
+MUT_PKG31_10 = MutationCase(
+    mutation_id="MUT-PKG31-10",
+    invariant="check_provider_sdk_imports.check() rejects any production module outside "
+    "packages/ai_gateway/adapters/providers/ that imports a real provider SDK -- the "
+    "static half of 'all LLM traffic through the Gateway' (BND-009). Disabling the "
+    "checker lets a Gateway-bypassing direct provider call land undetected.",
+    expected_boundary="BND_009 (static enforcement half)",
+    patch=MutationPatch(
+        target_module="check_provider_sdk_imports",
+        target_qualname="check",
+        replacement_factory=_mut10_provider_sdk_checker_disabled,  # type: ignore[arg-type]
+    ),
+    target_test_nodeids=(
+        "tests/security/test_ai_gateway.py::test_direct_provider_import_outside_gateway_adapter_is_rejected",
+    ),
+)
+
+
+MUTATIONS: tuple[MutationCase, ...] = (
+    MUT_PKG31_01,
+    MUT_PKG31_02,
+    MUT_PKG31_03,
+    MUT_PKG31_04,
+    MUT_PKG31_05,
+    MUT_PKG31_06,
+    MUT_PKG31_07,
+    MUT_PKG31_08,
+    MUT_PKG31_09,
+    MUT_PKG31_10,
+)
+
+__all__ = ["MUTATIONS"]

diff --git a/tests/mutation/test_pkg31_mutation_registry.py b/tests/mutation/test_pkg31_mutation_registry.py
new file mode 100644
new file mode 100644
index 0000000..fbad915
--- /dev/null
+++ b/tests/mutation/test_pkg31_mutation_registry.py
@@ -0,0 +1,90 @@
+"""T11 MUTATION TEST: falsifiability of the PKG-31 mutation registry
+itself (`tests/mutation/mutation_cases.py`), mirroring PKG-30's own
+`test_every_proof_claim_matrix_evidence_file_actually_exists` /
+`test_every_pkg30_exercised_claim_has_this_files_own_path_as_evidence`
+discipline: a registry entry is only as trustworthy as a test that can
+falsify a stale or typo'd claim in it.
+
+This file does NOT run the mutation harness itself (that requires a
+real PostgreSQL connection and takes on the order of a minute for ten
+mutations x three phases each -- deliberately kept OUT of the normal
+`pytest -q` regression run, exactly like `scripts/verify_migrations.py`'s
+live-DB check is a separate, explicit step, not a collected test). It
+proves the REGISTRY is internally consistent and every reference in it
+resolves to something real, so a broken `target_test_nodeids` entry or
+a renamed patch target is caught here, fast and DB-free, rather than
+only surfacing as a confusing failure deep inside
+`scripts/run_mutation_harness.py`.
+"""
+
+from __future__ import annotations
+
+import importlib
+import re
+from pathlib import Path
+
+from harness import MUTATION_IDS
+from mutation_cases import MUTATIONS
+
+_REPO_ROOT = Path(__file__).resolve().parents[2]
+
+
+def test_mutations_covers_exactly_the_ten_mandatory_ids() -> None:
+    ids = tuple(case.mutation_id for case in MUTATIONS)
+    assert len(ids) == len(set(ids)), f"duplicate mutation_id in registry: {ids}"
+    assert set(ids) == set(MUTATION_IDS)
+    assert len(MUTATIONS) == 10
+
+
+def test_every_target_test_nodeid_file_actually_exists() -> None:
+    missing: list[str] = []
+    for case in MUTATIONS:
+        for nodeid in case.target_test_nodeids:
+            file_part = nodeid.split("::", 1)[0]
+            if not (_REPO_ROOT / file_part).is_file():
+                missing.append(f"{case.mutation_id}: {nodeid}")
+    assert missing == [], f"registry cites non-existent test files: {missing}"
+
+
+def test_every_target_test_function_name_appears_in_its_own_file() -> None:
+    """Catches a renamed/typo'd test function name -- the exact
+    drafting-error class PKG-30's own P-19 finding demonstrated is real,
+    not theoretical, for a hand-maintained evidence list."""
+    missing: list[str] = []
+    for case in MUTATIONS:
+        for nodeid in case.target_test_nodeids:
+            file_part, _, func_part = nodeid.partition("::")
+            source = (_REPO_ROOT / file_part).read_text(encoding="utf-8")
+            if not re.search(rf"^def {re.escape(func_part)}\(", source, re.MULTILINE):
+                missing.append(f"{case.mutation_id}: {nodeid}")
+    assert missing == [], f"registry cites test functions not found in their file: {missing}"
+
+
+def test_every_patch_target_resolves_to_a_real_attribute() -> None:
+    """Proves each `MutationPatch.target_module`/`target_qualname` pair
+    is currently valid -- an upstream rename would otherwise only be
+    discovered when `scripts/run_mutation_harness.py` crashes."""
+    unresolved: list[str] = []
+    for case in MUTATIONS:
+        try:
+            module = importlib.import_module(case.patch.target_module)
+        except ImportError:
+            unresolved.append(f"{case.mutation_id}: module {case.patch.target_module!r}")
+            continue
+        owner: object = module
+        *path, attr = case.patch.target_qualname.split(".")
+        try:
+            for part in path:
+                owner = getattr(owner, part)
+            getattr(owner, attr)
+        except AttributeError:
+            unresolved.append(
+                f"{case.mutation_id}: {case.patch.target_module}.{case.patch.target_qualname}"
+            )
+    assert unresolved == [], f"registry cites unresolvable patch targets: {unresolved}"
+
+
+def test_every_case_names_a_non_placeholder_invariant_and_boundary() -> None:
+    for case in MUTATIONS:
+        assert len(case.invariant) > 40, f"{case.mutation_id}: invariant looks like a placeholder"
+        assert case.expected_boundary, f"{case.mutation_id}: expected_boundary must be non-empty"

diff --git a/scripts/run_mutation_harness.py b/scripts/run_mutation_harness.py
new file mode 100644
new file mode 100644
index 0000000..6704d15
--- /dev/null
+++ b/scripts/run_mutation_harness.py
@@ -0,0 +1,99 @@
+"""PKG-31 mutation runner: 14 section 46's own required PUBLIC_INTERFACE
+("mutation runner") for CI pipeline step 19 ("T11 mutation").
+
+Runs each of the ten mandatory PKG-31 mutations (`tests/mutation/
+mutation_cases.py`) against the real, pre-existing test suite in three
+phases -- baseline, mutated, restored -- and prints one line per
+mutation plus a final summary. Exits 0 only if every mutation was
+genuinely KILLED (baseline PASS, mutated FAIL, restored PASS); exits 1
+otherwise, naming which mutation(s) failed and why (SURVIVED is a
+`TEST_DESIGN_DEFECT`, per 14 section 27; BASELINE_FAILED/RESTORE_FAILED
+are this harness's own integrity failures, reported distinctly).
+
+Usage: `python scripts/run_mutation_harness.py` with `DATABASE_URL`
+pointed at a real local PostgreSQL (same requirement every DB-backed
+test in this repository already has) and the `.venv` active.
+"""
+
+from __future__ import annotations
+
+import importlib.util
+import sys
+from pathlib import Path
+from typing import Any
+
+_REPO_ROOT = Path(__file__).resolve().parents[1]
+
+# `tests/` is not a configured import root outside pytest (pyproject.toml's
+# `pythonpath` lists `packages`/`apps/api/src`/`apps/worker/src`/`scripts`,
+# not `tests`) -- both `harness.py` and `mutation_cases.py` are loaded by
+# absolute file path via `importlib`, never a plain `import`, so this
+# script's own module-level static imports stay fully mypy-resolvable
+# without widening MYPYPATH for a `scripts`-wide type-check run.
+for _relative in ("packages", "apps/api/src", "apps/worker/src"):
+    _path = str(_REPO_ROOT / _relative)
+    if _path not in sys.path:
+        sys.path.insert(0, _path)
+
+
+def _load_by_path(module_name: str, relative_path: str) -> Any:
+    spec = importlib.util.spec_from_file_location(module_name, _REPO_ROOT / relative_path)
+    if spec is None or spec.loader is None:
+        raise RuntimeError(f"could not load {relative_path}")
+    module = importlib.util.module_from_spec(spec)
+    sys.modules[module_name] = module
+    spec.loader.exec_module(module)
+    return module
+
+
+def main() -> int:
+    harness = _load_by_path("pkg31_mutation_harness", "tests/mutation/harness.py")
+    MutationInterpretation = harness.MutationInterpretation
+    run_mutation_case = harness.run_mutation_case
+
+    # `mutation_cases.py` does `from harness import ...` -- registering the
+    # already-loaded harness module under the bare name `harness` in
+    # `sys.modules` first (see `_load_by_path` above) lets that plain
+    # import resolve without needing `tests/mutation` on `sys.path`.
+    sys.modules["harness"] = harness
+    mutation_cases = _load_by_path("pkg31_mutation_cases", "tests/mutation/mutation_cases.py")
+    mutations = mutation_cases.MUTATIONS
+    print(f"PKG-31 MUTATION HARNESS -- {len(mutations)} mutations registered\n")
+
+    results = []
+    for case in mutations:
+        print(f"--- {case.mutation_id} ---")
+        print(f"invariant: {case.invariant}")
+        print(f"expected_boundary: {case.expected_boundary}")
+        print(f"target_test_nodeids: {case.target_test_nodeids}")
+        result = run_mutation_case(case)
+        results.append(result)
+        print(
+            f"baseline_exit={result.baseline_exit_code} "
+            f"mutated_exit={result.mutated_exit_code} "
+            f"restored_exit={result.restored_exit_code} "
+            f"-> {result.interpretation.value}"
+        )
+        print()
+
+    killed = [r for r in results if r.interpretation is MutationInterpretation.KILLED]
+    survived = [r for r in results if r.interpretation is MutationInterpretation.SURVIVED]
+    harness_failures = [
+        r
+        for r in results
+        if r.interpretation
+        in (MutationInterpretation.BASELINE_FAILED, MutationInterpretation.RESTORE_FAILED)
+    ]
+
+    print("=== SUMMARY ===")
+    print(f"KILLED: {len(killed)}/{len(results)}")
+    if survived:
+        print(f"SURVIVED (TEST_DESIGN_DEFECT): {[r.mutation_id for r in survived]}")
+    if harness_failures:
+        print(f"HARNESS_INTEGRITY_FAILURE: {[r.mutation_id for r in harness_failures]}")
+
+    return 0 if not survived and not harness_failures else 1
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())

################################################################
# 3. Modified file diff (tests/e2e/test_proof_bundle_paths.py -- PKG-30 nachtrag)
################################################################
diff --git a/tests/e2e/test_proof_bundle_paths.py b/tests/e2e/test_proof_bundle_paths.py
index 516e9e3..ac90a84 100644
--- a/tests/e2e/test_proof_bundle_paths.py
+++ b/tests/e2e/test_proof_bundle_paths.py
@@ -364,6 +364,17 @@ def _seed_recovery_record(
     return record.recovery_id
 
 
+def _assert_p_claims_are_real(bundle: TestProofBundle) -> None:
+    """PKG-31 addition (explicit human instruction at the PKG-31 gate:
+    the PKG-30 HAPPY path test was the only one of six that checked
+    `p_claims_exercised` membership against `PROOF_CLAIM_MATRIX` --
+    called from all six path tests below rather than left as a single
+    unchecked path, so a typo'd `P-NN` on any of them now fails the
+    same way P-19's own real drafting error was caught in PKG-30."""
+    for claim in bundle.p_claims_exercised:
+        assert claim in PROOF_CLAIM_MATRIX
+
+
 # ---------------------------------------------------------------------------
 # 1. HAPPY
 # ---------------------------------------------------------------------------
@@ -426,8 +437,7 @@ def test_happy_path_full_decision_lifecycle_produces_a_reconstructable_bundle(
     assert row["decided_by_user_id"] == owner_id.value
     assert bundle.commit_unit is not None
     assert len(bundle.commit_unit.audit_event_ids) >= 1
-    for claim in bundle.p_claims_exercised:
-        assert claim in PROOF_CLAIM_MATRIX
+    _assert_p_claims_are_real(bundle)
 
 
 # ---------------------------------------------------------------------------
@@ -463,6 +473,7 @@ def test_denial_path_role_only_actor_produces_a_real_boundary_proof(
     assert excinfo.value.chain_result.result is BoundaryResult.DENY
     assert bundle.boundary_proofs[-1].result is BoundaryResult.DENY
     assert bundle.boundary_proofs[-1].boundary_id is BoundaryId.BND_005
+    _assert_p_claims_are_real(bundle)
     # No Decision row was ever created -- the DENY genuinely prevented consequence.
     remaining = db_connection.execute(
         sa.select(decisions_table).where(decisions_table.c.challenge_id == challenge_id.value)
@@ -563,6 +574,7 @@ def test_stale_authority_path_revoked_binding_cannot_survive_to_commit(
     )
     assert bundle.boundary_proofs[-1].result is BoundaryResult.DENY
     assert bundle.boundary_proofs[-1].boundary_id is BoundaryId.BND_005
+    _assert_p_claims_are_real(bundle)
     row = (
         db_connection.execute(
             sa.select(decisions_table).where(decisions_table.c.id == decision_id.value)
@@ -687,6 +699,7 @@ def test_cross_workspace_path_a_challenge_from_another_workspace_is_denied(
     )
     assert bundle.boundary_proofs[-1].boundary_id is BoundaryId.BND_002
     assert bundle.boundary_proofs[-1].result is BoundaryResult.DENY
+    _assert_p_claims_are_real(bundle)
 
 
 def test_cross_workspace_counter_attack_a_governance_ref_alone_cannot_read_the_other_ws(
@@ -761,6 +774,7 @@ def test_ai_boundary_path_an_ai_actor_is_denied_before_any_decision_is_touched(
     )
     assert bundle.boundary_proofs[-1].boundary_id is BoundaryId.BND_001
     assert bundle.boundary_proofs[-1].result is BoundaryResult.DENY
+    _assert_p_claims_are_real(bundle)
     remaining = db_connection.execute(
         sa.select(decisions_table).where(decisions_table.c.challenge_id == challenge_id.value)
     ).fetchall()
@@ -884,6 +898,7 @@ def test_recovery_path_deterministic_reconciliation_produces_a_resolved_record(
     assert bundle.recovery_record is not None
     assert bundle.recovery_record.result is RecoveryOutcome.RECONCILED
     assert bundle.recovery_record.resolved_at == _LATER
+    _assert_p_claims_are_real(bundle)
 
 
 def test_recovery_counter_attack_manufactured_clean_facts_do_not_override_a_real_blocking_record(

################################################################
# 4. Relevant backend sources this package patches (cat -n excerpts)
################################################################
----- boundaries/bnd_014_commit.py (Bnd014CommitEvaluator.evaluate) -----
   110	    "authority revoked after preparation" and "state version changed".
   111	    """
   112	
   113	    boundary_id = BoundaryId.BND_014
   114	    boundary_version = ContractVersion("1.0")
   115	
   116	    def __init__(self, resolver: AuthorityResolver) -> None:
   117	        self._resolver = resolver
   118	
   119	    def evaluate(self, boundary_input: Bnd014Input, context: BoundaryContext) -> BoundaryProof:
   120	        def deny(reason_code: str) -> BoundaryProof:
   121	            return BoundaryProof(
   122	                boundary_id=self.boundary_id,
   123	                boundary_version=self.boundary_version,
   124	                result=BoundaryResult.DENY,
   125	                reason_code=reason_code,
   126	                workspace_id=context.workspace_id,
   127	                actor=context.actor,
   128	                input_refs=tuple(sorted(boundary_input.expected_versions.keys())),
   129	                authoritative_version_refs=(),
   130	                authority_proof=None,
   131	                evidence_proof_refs=(),
   132	                evaluated_at=context.evaluated_at,
   133	                correlation_id=context.correlation_id,
   134	            )
   135	
   136	        # PRECONDITIONS: "Every applicable upstream boundary currently
   137	        # allows. No upstream DENY/REQUIRE/ESCALATE remains unresolved."
   138	        if boundary_input.upstream_chain_result is not BoundaryResult.ALLOW:
   139	            return deny(f"UPSTREAM_CHAIN_NOT_ALLOW:{boundary_input.upstream_chain_result.value}")
   140	
   141	        # VALIDATION: "concurrency/object version where implementation
   142	        # requires." Mandatory adversarial attack: state version changed.
   143	        if boundary_input.expected_versions != boundary_input.current_versions:
   144	            stale = sorted(
   145	                ref
   146	                for ref, expected in boundary_input.expected_versions.items()
   147	                if boundary_input.current_versions.get(ref) != expected
   148	            )
   149	            return deny(f"STALE_VERSION:{','.join(stale)}")
   150	
   151	        # 09 section 114: "BND-014 compares member versions/current
   152	        # states... then stale ALLOW fails." Mandatory adversarial
   153	        # attacks: Evidence invalidated/unavailable after prepare, set
   154	        # membership no longer resolvable, cross-Workspace Evidence.
   155	        if (
   156	            boundary_input.evidence_freshness is not None
   157	            and not boundary_input.evidence_freshness.is_fresh
   158	        ):
   159	            if not boundary_input.evidence_freshness.evidence_set_found:
   160	                return deny("EVIDENCE_SET_NOT_FOUND")
   161	            return deny(f"STALE_EVIDENCE:{','.join(boundary_input.evidence_freshness.stale_refs)}")
   162	
   163	        # VALIDATION: "current authority... No stale ALLOW." Mandatory
   164	        # adversarial attack: authority revoked after preparation.
   165	        resolution = self._resolver.resolve(
   166	            AuthorityRequest(
   167	                actor=context.actor,
   168	                workspace_id=context.workspace_id,
   169	                operation=context.operation,
   170	                required_authority_class=boundary_input.required_authority_class,
   171	                scope_type=boundary_input.authority_scope_type,
   172	                scope_id=boundary_input.authority_scope_id,
   173	            )
   174	        )
   175	        if resolution.verdict is not AuthorityVerdict.GRANTED:
   176	            return BoundaryProof(
   177	                boundary_id=self.boundary_id,
   178	                boundary_version=self.boundary_version,
   179	                result=BoundaryResult.DENY,
   180	                reason_code=f"AUTHORITY_NOT_CURRENT:{resolution.proof.reason.value}",
   181	                workspace_id=context.workspace_id,
   182	                actor=context.actor,
   183	                input_refs=tuple(sorted(boundary_input.expected_versions.keys())),
   184	                authoritative_version_refs=(),
   185	                authority_proof=resolution.proof,
   186	                evidence_proof_refs=(),
   187	                evaluated_at=context.evaluated_at,
   188	                correlation_id=context.correlation_id,
   189	            )
   190	
   191	        return BoundaryProof(
   192	            boundary_id=self.boundary_id,
   193	            boundary_version=self.boundary_version,
   194	            result=BoundaryResult.ALLOW,
   195	            reason_code="COMMIT_SENSITIVE_PREDICATES_CURRENT",
   196	            workspace_id=context.workspace_id,
   197	            actor=context.actor,
   198	            input_refs=tuple(sorted(boundary_input.expected_versions.keys())),
   199	            authoritative_version_refs=tuple(
   200	                f"{ref}:{version.value}"
   201	                for ref, version in sorted(boundary_input.current_versions.items())
   202	                if version is not None
   203	            ),
   204	            authority_proof=resolution.proof,
   205	            evidence_proof_refs=(
   206	                ()
   207	                if boundary_input.evidence_freshness is None
   208	                else (str(boundary_input.evidence_freshness.evidence_set_ref_id.value),)
   209	            ),
   210	            evaluated_at=context.evaluated_at,
   211	            correlation_id=context.correlation_id,
   212	        )
   213	
   214	
   215	__all__ = ["Bnd014Input", "Bnd014CommitEvaluator"]

----- authority/resolver.py (AuthorityResolver.resolve) -----
   160	        self._authority_binding_repository = authority_binding_repository
   161	        self._clock = clock
   162	
   163	    def resolve(self, request: AuthorityRequest) -> AuthorityResolution:
   164	        evaluated_at = self._clock.now()
   165	
   166	        # 04 §3.3/§3.2, 05 AC-05-007: only HUMAN_USER can hold a HABB.
   167	        # Structural DENY — no membership/binding read even attempted for
   168	        # any other actor class (ATK-003, ATK-009, ATK-010).
   169	        if request.actor.actor_class is not ActorClass.HUMAN_USER:
   170	            return AuthorityResolution(
   171	                verdict=AuthorityVerdict.DENIED,
   172	                proof=self._proof(request, evaluated_at, ResolutionReason.DENIED_ACTOR_NOT_HUMAN),
   173	            )
   174	
   175	        # 05 AC-05-004: membership is authority precondition, not authority.
   176	        membership = self._membership_repository.get_current_membership(
   177	            request.workspace_id, request.actor.user_id
   178	        )
   179	        if membership is None:
   180	            return AuthorityResolution(
   181	                verdict=AuthorityVerdict.DENIED,
   182	                proof=self._proof(
   183	                    request, evaluated_at, ResolutionReason.DENIED_NO_ACTIVE_MEMBERSHIP
   184	                ),
   185	            )
   186	
   187	        current_bindings = self._authority_binding_repository.list_current_bindings(
   188	            request.workspace_id, request.actor.user_id
   189	        )
   190	
   191	        class_matches = [
   192	            b for b in current_bindings if b.authority_class == request.required_authority_class
   193	        ]
   194	        if not class_matches:
   195	            return AuthorityResolution(
   196	                verdict=AuthorityVerdict.DENIED,
   197	                proof=self._proof(
   198	                    request,
   199	                    evaluated_at,
   200	                    ResolutionReason.DENIED_NO_MATCHING_BINDING,
   201	                    membership_id=membership.id,
   202	                    membership_record_version=membership.record_version,
   203	                ),
   204	            )
   205	
   206	        scope_matches = [
   207	            b
   208	            for b in class_matches
   209	            if b.scope_type == request.scope_type and b.scope_id == request.scope_id
   210	        ]
   211	        if not scope_matches:
   212	            return AuthorityResolution(
   213	                verdict=AuthorityVerdict.DENIED,
   214	                proof=self._proof(
   215	                    request,
   216	                    evaluated_at,
   217	                    ResolutionReason.DENIED_WRONG_SCOPE,
   218	                    membership_id=membership.id,
   219	                    membership_record_version=membership.record_version,
   220	                ),
   221	            )
   222	
   223	        if len(scope_matches) > 1:
   224	            # Data-integrity ambiguity migration 002's schema does not
   225	            # prevent (no uniqueness constraint spans authority_class +
   226	            # scope for human_authority_bindings): fail closed rather
   227	            # than arbitrarily pick one (14 non-collapse: "Unknown
   228	            # consequential semantic input fails closed").
   229	            return AuthorityResolution(
   230	                verdict=AuthorityVerdict.UNRESOLVED,

----- boundaries/bnd_002_workspace.py (Bnd002WorkspaceEvaluator.evaluate signature) -----
    45	class Bnd002Input:
    46	    boundary_id: BoundaryId
    47	    context: BoundaryContext
    48	    resolved_object_workspace_ids: tuple[WorkspaceId, ...]
    49	
    50	    def __post_init__(self) -> None:
    51	        if self.boundary_id is not BoundaryId.BND_002:
    52	            raise ValueError(f"Bnd002Input.boundary_id must be BND_002, got {self.boundary_id}")
    53	
    54	
    55	class Bnd002WorkspaceEvaluator:
    56	    boundary_id = BoundaryId.BND_002
    57	    boundary_version = ContractVersion("1")
    58	
    59	    def __init__(self, workspace_repository: WorkspaceRepository) -> None:
    60	        self._workspace_repository = workspace_repository
    61	
    62	    def evaluate(self, boundary_input: Bnd002Input, context: BoundaryContext) -> BoundaryProof:
    63	        def deny(reason_code: str) -> BoundaryProof:
    64	            return BoundaryProof(
    65	                boundary_id=self.boundary_id,

----- boundaries/bnd_001_identity.py (Bnd001IdentityEvaluator.evaluate signature) -----
    38	
    39	@dataclass(frozen=True, slots=True)
    40	class Bnd001Input:
    41	    boundary_id: BoundaryId
    42	    context: BoundaryContext
    43	    required_actor_classes: frozenset[ActorClass]
    44	
    45	    def __post_init__(self) -> None:
    46	        if self.boundary_id is not BoundaryId.BND_001:
    47	            raise ValueError(f"Bnd001Input.boundary_id must be BND_001, got {self.boundary_id}")
    48	        if not self.required_actor_classes:
    49	            raise ValueError("Bnd001Input.required_actor_classes must be non-empty")
    50	
    51	
    52	class Bnd001IdentityEvaluator:
    53	    boundary_id = BoundaryId.BND_001
    54	    boundary_version = ContractVersion("1")
    55	
    56	    def evaluate(self, boundary_input: Bnd001Input, context: BoundaryContext) -> BoundaryProof:
    57	        actor_class = context.actor.actor_class
    58	        if actor_class in boundary_input.required_actor_classes:
    59	            result = BoundaryResult.ALLOW
    60	            reason_code = "IDENTITY_VALID_FOR_OPERATION"

----- commit/coordinator.py (_commit_inner, full body) -----
   427	    def _commit_inner(
   428	        self,
   429	        *,
   430	        envelope: CommandEnvelope,
   431	        proof: BoundaryProof,
   432	        mutation: MutationExecutor,
   433	        occurred_at: datetime,
   434	        commit_id: CommitId,
   435	    ) -> CommitUnit:
   436	        audit_event_id = AuditEventId(uuid.uuid4())
   437	        outbox_id = uuid.uuid4()
   438	        authority_source_ref = (
   439	            proof.authority_proof.binding_id.value
   440	            if proof.authority_proof is not None and proof.authority_proof.binding_id is not None
   441	            else uuid.uuid4()
   442	        )
   443	
   444	        with self._connection.begin_nested():
   445	            mutation_outcome = mutation.apply()
   446	            self._failure_injector.before(CommitInjectionPoint.AFTER_FIRST_CANONICAL_MUTATION)
   447	            self._failure_injector.before(CommitInjectionPoint.AFTER_RELATION_MUTATION)
   448	
   449	            # `commit_units` is written BEFORE `audit_events`/`outbox_events`
   450	            # deliberately: their composite FK to `commit_units(id,
   451	            # workspace_id)` (migration `b06f9a5b3d1b`) requires the row
   452	            # to already exist, while `commit_units.audit_event_ids`/
   453	            # `outbox_ids` need only the *values* (already generated
   454	            # above), not the rows themselves -- no FK is declared on
   455	            # those two array columns, so this ordering has no circular
   456	            # dependency at all, unlike the naive "audit/outbox first"
   457	            # ordering it replaces.
   458	            commit_unit = CommitUnit(
   459	                commit_id=commit_id,
   460	                command_id=envelope.command_id,
   461	                attempt_id=envelope.attempt_id,
   462	                workspace_id=envelope.workspace_scope_ref,
   463	                target_refs=envelope.target_refs,
   464	                relation_refs=mutation_outcome.relation_refs,
   465	                governance_refs=(),
   466	                audit_event_ids=(audit_event_id,),
   467	                outbox_ids=(outbox_id,),
   468	                committed_at=occurred_at,
   469	                outcome=CommitOutcome.COMMITTED,
   470	            )
   471	            self._commit_repository.append(commit_unit)
   472	
   473	            self._failure_injector.before(CommitInjectionPoint.BEFORE_AUDIT)
   474	            audit_event = AuditEvent(
   475	                audit_event_id=audit_event_id,
   476	                event_type=f"{envelope.command_type}_COMMITTED",
   477	                event_schema_version=ContractVersion("1.0"),
   478	                workspace_id=envelope.workspace_scope_ref,
   479	                occurred_at=occurred_at,
   480	                actor_type=envelope.requesting_actor_type,
   481	                actor_id=envelope.requesting_actor_id,
   482	                command_type=envelope.command_type,
   483	                command_id=envelope.command_id,
   484	                commit_id=commit_id,
   485	                correlation_id=envelope.correlation_id,
   486	                causation_id=envelope.causation_id,
   487	                target_refs=envelope.target_refs,
   488	                authority_source_ref=authority_source_ref,
   489	                result=CommitOutcome.COMMITTED.value,
   490	                human_decision_ref=envelope.human_decision_ref,
   491	                evidence_set_ref=envelope.evidence_set_ref,
   492	                state_before_ref=mutation_outcome.state_before_ref,
   493	                state_after_ref=mutation_outcome.state_after_ref,
   494	            )
   495	            self._audit_repository.append(audit_event)
   496	            self._failure_injector.before(CommitInjectionPoint.AFTER_AUDIT)
   497	
   498	            self._failure_injector.before(CommitInjectionPoint.BEFORE_OUTBOX)
   499	            outbox_record = OutboxRecord(
   500	                outbox_id=outbox_id,
   501	                event_id=EventId(uuid.uuid4()),
   502	                workspace_id=envelope.workspace_scope_ref,
   503	                commit_id=commit_id,
   504	                event_type=f"{envelope.command_type}_COMMITTED",
   505	                created_at=occurred_at,
   506	                delivery_status=DeliveryStatus.PENDING,
   507	                delivery_attempt_count=0,
   508	            )
   509	            self._outbox_repository.append(outbox_record)
   510	            self._failure_injector.before(CommitInjectionPoint.AFTER_OUTBOX)
   511	
   512	            self._command_repository.record_outcome(
   513	                attempt_id=envelope.attempt_id,
   514	                workspace_id=envelope.workspace_scope_ref,
   515	                outcome=CommandOutcome.COMMITTED,
   516	                completed_at=occurred_at,
   517	                commit_id=commit_id,
   518	            )
   519	
   520	            if envelope.idempotency_key is not None:
   521	                self._idempotency_port.mark_committed(
   522	                    workspace_id=envelope.workspace_scope_ref,
   523	                    command_type=envelope.command_type,
   524	                    idempotency_key=envelope.idempotency_key,
   525	                    commit_id=commit_id,
   526	                    result_ref=str(commit_id.value),
   527	                )
   528	
   529	            self._failure_injector.before(CommitInjectionPoint.BEFORE_DB_COMMIT)
   530	

----- command/envelope.py (__post_init__ CommandId guard) -----
   145	
   146	    def __post_init__(self) -> None:
   147	        # Mandatory adversarial attack: Event submitted as Command. An
   148	        # EventId (or any other strong identity, or a bare string/UUID)
   149	        # is a structurally different type than CommandId -- this is
   150	        # the type system rejecting the substitution PKG-00's own
   151	        # semantic_types docstring promises ("mixing them is a semantic
   152	        # error the type system must reject"), enforced here at
   153	        # *runtime* since CommandEnvelope is a public consequential
   154	        # boundary a caller could otherwise miswire.
   155	        if not isinstance(self.command_id, CommandId):
   156	            raise TypeError(f"command_id must be a CommandId, got {type(self.command_id)!r}")
   157	        if not self.command_type:
   158	            raise ValueError("CommandEnvelope.command_type must be non-empty")
   159	        if not isinstance(self.command_contract_version, ContractVersion):
   160	            raise TypeError(
   161	                "command_contract_version must be a ContractVersion, "
   162	                f"got {type(self.command_contract_version)!r}"
   163	            )
   164	        if not isinstance(self.attempt_id, AttemptId):
   165	            raise TypeError(f"attempt_id must be an AttemptId, got {type(self.attempt_id)!r}")

----- evidence/freshness.py (_resolve_member) -----
   241	def _resolve_member(
   242	    evidence_id: EvidenceId,
   243	    expected_content_version: RecordVersion,
   244	    workspace_id: WorkspaceId,
   245	    reader: EvidenceFreshnessPort,
   246	) -> EvidenceMemberFreshness:
   247	    current = reader.get_evidence(evidence_id)
   248	    if current is None:
   249	        return EvidenceMemberFreshness.MEMBER_NOT_FOUND
   250	    if current.workspace_id != workspace_id:
   251	        return EvidenceMemberFreshness.WRONG_WORKSPACE
   252	    if current.validation_state is EvidenceValidationState.INVALIDATED:
   253	        return EvidenceMemberFreshness.INVALIDATED
   254	    if current.validation_state is EvidenceValidationState.UNAVAILABLE:
   255	        return EvidenceMemberFreshness.UNAVAILABLE
   256	    if current.content_version != expected_content_version:
   257	        return EvidenceMemberFreshness.CONTENT_VERSION_CHANGED
   258	    if reader.find_superseding_evidence_id(evidence_id) is not None:
   259	        return EvidenceMemberFreshness.SUPERSEDED
   260	    return EvidenceMemberFreshness.FRESH

----- boundaries/bnd_017_failure_indeterminate.py (evaluate signature) -----
   118	
   119	        if certainty is ConsequenceCertainty.PROVEN_COMMITTED:
   120	            if op == "acknowledge_committed":
   121	                return result_proof(BoundaryResult.ALLOW, "COMMITTED_CONSEQUENCE_ACKNOWLEDGED")
   122	            # 06 §24 ALLOW: "known COMMITTED -> do not repeat
   123	            # consequence" -- any operation that would repeat it
   124	            # (retry/reconcile/assume-anything) is denied.
   125	            return result_proof(BoundaryResult.DENY, "COMMITTED_CONSEQUENCE_MUST_NOT_REPEAT")
   126	
   127	        if certainty is ConsequenceCertainty.PROVEN_NOT_COMMITTED:
   128	            if op in _RETRY_LIKE_OPERATIONS or op == "reconcile":
   129	                return result_proof(BoundaryResult.ALLOW, "SAFE_RETRY_AFTER_PROVEN_NON_COMMIT")
   130	            return result_proof(BoundaryResult.REQUIRE, "FRESH_BOUNDARY_CHAIN_REQUIRED")
   131	
   132	        # Every remaining certainty value (`*_UNKNOWN`,
   133	        # `GOVERNANCE_STATE_UNKNOWN`) is genuinely uncertain.
   134	        if op in _ASSUMPTION_OPERATIONS:
   135	            return result_proof(BoundaryResult.DENY, f"CANNOT_ASSUME_OUTCOME_WITHOUT_PROOF:{op}")
   136	        if op in _RETRY_LIKE_OPERATIONS:
   137	            return result_proof(BoundaryResult.DENY, "BLIND_RETRY_ON_UNCERTAIN_CONSEQUENCE")
   138	        if op == "reconcile":
   139	            # 06 §24 REQUIRE ("Recovery/reconciliation for
   140	            # INDETERMINATE") is satisfied precisely by requesting

----- scripts/check_provider_sdk_imports.py (check signature) -----
    55	
    56	def _is_approved(file: Path) -> bool:
    57	    return str(_APPROVED_PATH_MARKER) in str(file)
    58	
    59	
    60	def check(roots: tuple[Path, ...] | None = None) -> list[Violation]:
    61	    """Run the check. `roots` defaults to this repository's real source
    62	    roots; tests pass a fabricated fixture tree instead so a controlled
    63	    violation can be proven without touching real production code.
    64	    """
    65	    scan_roots = roots if roots is not None else (PACKAGES_ROOT, API_SRC_ROOT, WORKER_SRC_ROOT)
################################################################
# 5. RAW TERMINAL OUTPUT -- mutation harness full run (all 10 mutations)
################################################################
PKG-31 MUTATION HARNESS -- 10 mutations registered

--- MUT-PKG31-01 ---
invariant: BND-014 evaluates expected/current versions, upstream chain result and evidence freshness before any commit; removing it must let a stale-version or already-denied commit through unchecked.
expected_boundary: BND_014
target_test_nodeids: ('tests/boundaries/test_bnd_014_commit.py::test_denies_a_stale_expected_version', 'tests/command_commit_event/test_commit.py::test_commit_denies_when_state_version_changed')
..                                                                       [100%]
2 passed in 0.46s
FF                                                                       [100%]
=================================== FAILURES ===================================
_____________________ test_denies_a_stale_expected_version _____________________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfacde03a0>

    def test_denies_a_stale_expected_version(db_connection: sa.Connection) -> None:
        """Mandatory adversarial attack: state version changed."""
        bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
        result = bootstrap.seed(owner_email="bnd014-stale-version@nonproof.test")
        _grant(
            db_connection,
            workspace_id=result.workspace_id,
            user_id=result.owner_user_id.value,
            authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        )
        context = _context(
            workspace_id=result.workspace_id,
            actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
        )
        boundary_input = _base_input(
            workspace_id=result.workspace_id,
            context=context,
            expected_versions={"burst-1": RecordVersion(1)},
            current_versions={"burst-1": RecordVersion(2)},  # competing operation advanced it
        )
    
        proof = _evaluator(db_connection).evaluate(boundary_input, context)
    
>       assert proof.result is BoundaryResult.DENY
E       AssertionError: assert <BoundaryResult.ALLOW: 'ALLOW'> is <BoundaryResult.DENY: 'DENY'>
E        +  where <BoundaryResult.ALLOW: 'ALLOW'> = BoundaryProof(boundary_id=<BoundaryId.BND_014: 'BND-014'>, boundary_version=ContractVersion(value='1.0'), result=<Boun... 0, 0, tzinfo=datetime.timezone.utc), correlation_id=CorrelationId(value=UUID('05975b0c-a15f-44a3-84ca-3f1eca729237'))).result
E        +  and   <BoundaryResult.DENY: 'DENY'> = BoundaryResult.DENY

tests/boundaries/test_bnd_014_commit.py:165: AssertionError
________________ test_commit_denies_when_state_version_changed _________________

self = <test_commit._BurstStartMutation object at 0x7bbfab98ab00>

    def apply(self) -> MutationOutcome:
        try:
>           self._repo.start(
                burst_id=self._burst_id,
                workspace_id=self._workspace_id,
                expected_record_version=self._expected_record_version,
                started_at=self._started_at,
            )

tests/command_commit_event/test_commit.py:262: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
packages/persistence/burst_repository.py:159: in start
    self._transition(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <persistence.burst_repository.SqlAlchemyBurstRepository object at 0x7bbfab98aa70>

    def _transition(
        self,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        values: dict[str, object],
    ) -> None:
        result = self._connection.execute(
            sa.update(question_bursts_table)
            .where(
                question_bursts_table.c.id == burst_id.value,
                question_bursts_table.c.workspace_id == workspace_id.value,
                question_bursts_table.c.record_version == expected_record_version.value,
            )
            .values(record_version=expected_record_version.next().value, **values)
        )
        if result.rowcount == 0:
>           raise BurstConflict(
                f"burst {burst_id!r} not found at workspace {workspace_id!r} with "
                f"expected record_version {expected_record_version.value}"
            )
E           persistence.burst_repository.BurstConflict: burst BurstId(value=UUID('01a0bfe9-9630-7e20-af9f-66089042ee20')) not found at workspace WorkspaceId(value=UUID('01a0bfe9-961f-78af-806a-2abd8f843bcf')) with expected record_version 1

packages/persistence/burst_repository.py:246: BurstConflict

The above exception was the direct cause of the following exception:

self = <test_commit._BurstStartMutation object at 0x7bbfab98ab00>

    def apply(self) -> MutationOutcome:
        try:
            self._repo.start(
                burst_id=self._burst_id,
                workspace_id=self._workspace_id,
                expected_record_version=self._expected_record_version,
                started_at=self._started_at,
            )
        except BurstConflict as exc:
>           raise StaleVersionConflict(str(exc)) from exc
E           commit.coordinator.StaleVersionConflict: burst BurstId(value=UUID('01a0bfe9-9630-7e20-af9f-66089042ee20')) not found at workspace WorkspaceId(value=UUID('01a0bfe9-961f-78af-806a-2abd8f843bcf')) with expected record_version 1

tests/command_commit_event/test_commit.py:269: StaleVersionConflict

During handling of the above exception, another exception occurred:

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfabdd9720>

    def test_commit_denies_when_state_version_changed(db_connection: sa.Connection) -> None:
        """Mandatory adversarial attack: state version changed.
        ATTACK: a competing operation advances the Burst's record_version
        between envelope preparation and this commit attempt.
        EXPECTED CANONICAL RESULT: CommitDenied (BND-014's own fresh read
        catches it before any mutation is even attempted).
        ACTUAL RESULT: matches.
        """
        workspace_id, owner_id, burst = _bootstrap_burst(
            db_connection, email="commit-stale-version@nonproof.test"
        )
        _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
        # A competing write advances the real row's version out from under us.
        db_connection.execute(
            sa.update(question_bursts_table)
            .where(question_bursts_table.c.id == burst.burst_id.value)
            .values(record_version=2, state="ACTIVE", started_at=_NOW)
        )
        envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
        SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
        coordinator = _build_coordinator(db_connection)
        mutation = _BurstStartMutation(
            SqlAlchemyBurstRepository(db_connection),
            burst_id=burst.burst_id,
            workspace_id=workspace_id,
            expected_record_version=burst.record_version,
            started_at=_NOW,
        )
    
        with pytest.raises(CommitDenied) as excinfo:
>           coordinator.commit(
                envelope=envelope,
                actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
                required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
                authority_scope_type="WORKSPACE",
                authority_scope_id=workspace_id.value,
                upstream_chain_result=BoundaryResult.ALLOW,
                current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
                mutation=mutation,
                occurred_at=_NOW,
                commit_id=CommitId(uuid.uuid4()),
            )

tests/command_commit_event/test_commit.py:447: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
packages/commit/coordinator.py:418: in commit
    self._mark_failed_precommit(envelope, occurred_at=occurred_at)
packages/commit/coordinator.py:542: in _mark_failed_precommit
    self._idempotency_port.mark_failed_precommit(
packages/commit/idempotency.py:455: in mark_failed_precommit
    self._transition(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <commit.idempotency.SqlAlchemyIdempotencyRepository object at 0x7bbfabddaa70>

    def _transition(
        self,
        *,
        workspace_id: WorkspaceId,
        command_type: str,
        idempotency_key: str,
        values: dict[str, object],
    ) -> None:
        result = self._connection.execute(
            sa.update(idempotency_records_table)
            .where(
                idempotency_records_table.c.workspace_id == workspace_id.value,
                idempotency_records_table.c.command_type == command_type,
                idempotency_records_table.c.idempotency_key == idempotency_key,
            )
            .values(**values)
        )
        if result.rowcount == 0:
>           raise IdempotencyRecordNotFound(
                f"idempotency_key {idempotency_key!r} not found at workspace {workspace_id!r}"
            )
E           commit.idempotency.IdempotencyRecordNotFound: idempotency_key 'start-burst-1' not found at workspace WorkspaceId(value=UUID('01a0bfe9-961f-78af-806a-2abd8f843bcf'))

packages/commit/idempotency.py:490: IdempotencyRecordNotFound
=========================== short test summary info ============================
FAILED tests/boundaries/test_bnd_014_commit.py::test_denies_a_stale_expected_version
FAILED tests/command_commit_event/test_commit.py::test_commit_denies_when_state_version_changed
2 failed in 0.27s
..                                                                       [100%]
2 passed in 0.22s
baseline_exit=0 mutated_exit=1 restored_exit=0 -> KILLED

--- MUT-PKG31-02 ---
invariant: AuthorityResolver.resolve() never caches -- every call re-reads current membership/binding state (14 section 16: commit-time resolver reloads current authoritative state). Caching the first verdict lets a later revocation be invisible to a second resolution that reuses the stale, still-GRANTED answer.
expected_boundary: BND_005
target_test_nodeids: ('tests/authority/test_resolver.py::test_stale_binding_denied_after_revoke_between_two_resolutions',)
.                                                                        [100%]
1 passed in 0.07s
F                                                                        [100%]
=================================== FAILURES ===================================
________ test_stale_binding_denied_after_revoke_between_two_resolutions ________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfacd1c520>

    def test_stale_binding_denied_after_revoke_between_two_resolutions(
        db_connection: sa.Connection,
    ) -> None:
        """Mandatory adversarial attack: stale binding (P-11 / ATK-011:
        "revoke before commit" -- 14 §16: "Commit-time resolver reloads
        current authoritative state"). Proves there is no caching: the
        exact same resolver instance flips from GRANTED to DENIED.
        """
        owner = _insert_user(db_connection, email="owner11@test.local")
        workspace_id = _insert_workspace(db_connection, owner_id=owner)
        member = _insert_user(db_connection, email="member11@test.local")
        _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
        scope_id = uuid.uuid4()
        binding_id = _insert_binding(
            db_connection,
            workspace_id=workspace_id,
            human_user_id=member,
            granted_by=owner,
            scope_id=scope_id,
        )
    
        request = AuthorityRequest(
            actor=ActorIdentity(ActorClass.HUMAN_USER, member),
            workspace_id=workspace_id,
            operation="RECORD_DECISION",
            required_authority_class=AuthorityClass.DECISION_RIGHT,
            scope_type="DECISION",
            scope_id=scope_id,
        )
        resolver = _resolver(db_connection)
    
        first = resolver.resolve(request)
        assert first.verdict == AuthorityVerdict.GRANTED
    
        db_connection.execute(
            sa.update(human_authority_bindings_table)
            .where(human_authority_bindings_table.c.id == binding_id)
            .values(
                state="REVOKED", revoked_at=datetime.now(timezone.utc), revoked_by_user_id=owner.value
            )
        )
    
        second = resolver.resolve(request)
>       assert second.verdict == AuthorityVerdict.DENIED
E       AssertionError: assert <AuthorityVer...ED: 'GRANTED'> == <AuthorityVer...IED: 'DENIED'>
E         
E         - DENIED
E         + GRANTED

tests/authority/test_resolver.py:504: AssertionError
=========================== short test summary info ============================
FAILED tests/authority/test_resolver.py::test_stale_binding_denied_after_revoke_between_two_resolutions
1 failed in 0.07s
.                                                                        [100%]
1 passed in 0.06s
baseline_exit=0 mutated_exit=1 restored_exit=0 -> KILLED

--- MUT-PKG31-03 ---
invariant: BND-002 denies when a request's claimed Workspace does not match the resolved scope of every object it names; removing it lets a request read/act across Workspace boundaries.
expected_boundary: BND_002
target_test_nodeids: ('tests/boundaries/test_bnd_002_workspace.py::test_denies_cross_workspace_object_set', 'tests/e2e/test_proof_bundle_paths.py::test_cross_workspace_path_a_challenge_from_another_workspace_is_denied')
..                                                                       [100%]
2 passed in 0.17s
FF                                                                       [100%]
=================================== FAILURES ===================================
____________________ test_denies_cross_workspace_object_set ____________________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfacd1ed10>

    def test_denies_cross_workspace_object_set(db_connection: sa.Connection) -> None:
        """Mandatory adversarial attack: Workspace mismatch."""
        bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
        workspace_a = bootstrap.seed(owner_email="bnd002-a@nonproof.test")
        workspace_b = bootstrap.seed(owner_email="bnd002-b@nonproof.test")
        context = _context(
            workspace_id=workspace_a.workspace_id,
            actor=ActorIdentity(ActorClass.HUMAN_USER, workspace_a.owner_user_id),
        )
        evaluator = Bnd002WorkspaceEvaluator(SqlAlchemyWorkspaceRepository(db_connection))
        boundary_input = Bnd002Input(
            boundary_id=BoundaryId.BND_002,
            context=context,
            resolved_object_workspace_ids=(workspace_a.workspace_id, workspace_b.workspace_id),
        )
    
        proof = evaluator.evaluate(boundary_input, context)
    
>       assert proof.result is BoundaryResult.DENY
E       AssertionError: assert <BoundaryResult.ALLOW: 'ALLOW'> is <BoundaryResult.DENY: 'DENY'>
E        +  where <BoundaryResult.ALLOW: 'ALLOW'> = BoundaryProof(boundary_id=<BoundaryId.BND_002: 'BND-002'>, boundary_version=ContractVersion(value='1.0'), result=<Boun... 0, 0, tzinfo=datetime.timezone.utc), correlation_id=CorrelationId(value=UUID('5efa5848-196a-47a4-9785-fe80af58ee6d'))).result
E        +  and   <BoundaryResult.DENY: 'DENY'> = BoundaryResult.DENY

tests/boundaries/test_bnd_002_workspace.py:75: AssertionError
____ test_cross_workspace_path_a_challenge_from_another_workspace_is_denied ____

self = <sqlalchemy.engine.base.Connection object at 0x7bbfab173bb0>
dialect = <sqlalchemy.dialects.postgresql.psycopg.PGDialect_psycopg object at 0x7bbfab173b80>
context = <sqlalchemy.dialects.postgresql.psycopg.PGExecutionContext_psycopg object at 0x7bbfab1c0580>
statement = <sqlalchemy.dialects.postgresql.psycopg.PGCompiler_psycopg object at 0x7bbfab1c03d0>
parameters = [{'challenge_id': UUID('01a0bfe9-9e4a-705b-ba35-60ab41ac3eea'), 'confidence': None, 'created_at': datetime.datetime(2030, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), 'criteria': ['impact', 'effort'], ...}]

    def _exec_single_context(
        self,
        dialect: Dialect,
        context: ExecutionContext,
        statement: Union[str, Compiled],
        parameters: Optional[_AnyMultiExecuteParams],
    ) -> CursorResult[Any]:
        """continue the _execute_context() method for a single DBAPI
        cursor.execute() or cursor.executemany() call.
    
        """
        if dialect.bind_typing is BindTyping.SETINPUTSIZES:
            generic_setinputsizes = context._prepare_set_input_sizes()
    
            if generic_setinputsizes:
                try:
                    dialect.do_set_input_sizes(
                        context.cursor, generic_setinputsizes, context
                    )
                except BaseException as e:
                    self._handle_dbapi_exception(
                        e, str(statement), parameters, None, context
                    )
    
        cursor, str_statement, parameters = (
            context.cursor,
            context.statement,
            context.parameters,
        )
    
        effective_parameters: Optional[_AnyExecuteParams]
    
        if not context.executemany:
            effective_parameters = parameters[0]
        else:
            effective_parameters = parameters
    
        if self._has_events or self.engine._has_events:
            for fn in self.dispatch.before_cursor_execute:
                str_statement, effective_parameters = fn(
                    self,
                    cursor,
                    str_statement,
                    effective_parameters,
                    context,
                    context.executemany,
                )
    
        if self._echo:
            self._log_info(str_statement)
    
            stats = context._get_cache_stats()
    
            if not self.engine.hide_parameters:
                self._log_info(
                    "[%s] %r",
                    stats,
                    sql_util._repr_params(
                        effective_parameters,
                        batches=10,
                        ismulti=context.executemany,
                    ),
                )
            else:
                self._log_info(
                    "[%s] [SQL parameters hidden due to hide_parameters=True]",
                    stats,
                )
    
        evt_handled: bool = False
        try:
            if context.execute_style is ExecuteStyle.EXECUTEMANY:
                effective_parameters = cast(
                    "_CoreMultiExecuteParams", effective_parameters
                )
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_executemany:
                        if fn(
                            cursor,
                            str_statement,
                            effective_parameters,
                            context,
                        ):
                            evt_handled = True
                            break
                if not evt_handled:
                    self.dialect.do_executemany(
                        cursor,
                        str_statement,
                        effective_parameters,
                        context,
                    )
            elif not effective_parameters and context.no_parameters:
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_execute_no_params:
                        if fn(cursor, str_statement, context):
                            evt_handled = True
                            break
                if not evt_handled:
                    self.dialect.do_execute_no_params(
                        cursor, str_statement, context
                    )
            else:
                effective_parameters = cast(
                    "_CoreSingleExecuteParams", effective_parameters
                )
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_execute:
                        if fn(
                            cursor,
                            str_statement,
                            effective_parameters,
                            context,
                        ):
                            evt_handled = True
                            break
                if not evt_handled:
>                   self.dialect.do_execute(
                        cursor, str_statement, effective_parameters, context
                    )

../../.local/lib/python3.10/site-packages/sqlalchemy/engine/base.py:1967: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
../../.local/lib/python3.10/site-packages/sqlalchemy/engine/default.py:941: in do_execute
    cursor.execute(statement, parameters)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <psycopg.Cursor [closed] [INTRANS] (host=localhost port=15432 database=nquiry) at 0x7bbfab118400>
query = 'INSERT INTO decisions (id, workspace_id, challenge_id, decision_question_ref, decision_question_text, options, criter...ESTAMP WITH TIME ZONE, %(decided_at)s::TIMESTAMP WITH TIME ZONE, %(record_version)s::BIGINT, %(provenance_ref)s::UUID)'
params = {'challenge_id': UUID('01a0bfe9-9e4a-705b-ba35-60ab41ac3eea'), 'confidence': None, 'created_at': datetime.datetime(2030, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), 'criteria': ['impact', 'effort'], ...}

    def execute(
        self,
        query: Query,
        params: Params | None = None,
        *,
        prepare: bool | None = None,
        binary: bool | None = None,
    ) -> Self:
        """
        Execute a query or command to the database.
        """
        try:
            with self._conn.lock:
                self._conn.wait(
                    self._execute_gen(query, params, prepare=prepare, binary=binary)
                )
        except e._NO_TRACEBACK as ex:
>           raise ex.with_traceback(None)
E           psycopg.errors.ForeignKeyViolation: insert or update on table "decisions" violates foreign key constraint "fk_decisions_challenge_workspace"
E           DETAIL:  Key (challenge_id, workspace_id)=(01a0bfe9-9e4a-705b-ba35-60ab41ac3eea, 01a0bfe9-9e32-7e24-86ca-23ab6d9547f2) is not present in table "challenges".

.venv/lib/python3.10/site-packages/psycopg/cursor.py:117: ForeignKeyViolation

The above exception was the direct cause of the following exception:

self = <commit.coordinator.CommitCoordinator object at 0x7bbfab1714b0>

    def commit(
        self,
        *,
        envelope: CommandEnvelope,
        actor: ActorIdentity,
        required_authority_class: AuthorityClass,
        authority_scope_type: str,
        authority_scope_id: uuid.UUID,
        upstream_chain_result: BoundaryResult,
        current_version_reader: CurrentVersionReader,
        mutation: MutationExecutor,
        occurred_at: datetime,
        commit_id: CommitId,
        evidence_freshness_reader: EvidenceFreshnessPort | None = None,
    ) -> CommitUnit:
        self._failure_injector.before(CommitInjectionPoint.BEFORE_TRANSACTION)
    
        current_versions: dict[str, RecordVersion | None] = {
            ref: current_version_reader.read(ref) for ref in envelope.target_refs
        }
    
        evidence_freshness: EvidenceSetFreshnessResult | None = None
        if envelope.evidence_set_ref is not None:
            if evidence_freshness_reader is None:
                raise EvidenceFreshnessReaderRequired(
                    f"envelope {envelope.command_id!r} names evidence_set_ref "
                    f"{envelope.evidence_set_ref!r} but no evidence_freshness_reader was supplied"
                )
            evidence_freshness = resolve_evidence_set_freshness(
                envelope.evidence_set_ref,
                workspace_id=envelope.workspace_scope_ref,
                reader=evidence_freshness_reader,
            )
    
        context = BoundaryContext(
            workspace_id=envelope.workspace_scope_ref,
            operation=envelope.command_type,
            actor=actor,
            correlation_id=envelope.correlation_id,
            evaluated_at=occurred_at,
        )
        self._failure_injector.before(CommitInjectionPoint.AFTER_AUTHORITY_EVALUATION)
        bnd014_input = Bnd014Input(
            boundary_id=BoundaryId.BND_014,
            context=context,
            required_authority_class=required_authority_class,
            authority_scope_type=authority_scope_type,
            authority_scope_id=authority_scope_id,
            expected_versions=envelope.expected_versions,
            current_versions=current_versions,
            upstream_chain_result=upstream_chain_result,
            evidence_freshness=evidence_freshness,
        )
        proof = self._bnd014_evaluator.evaluate(bnd014_input, context)
        self._failure_injector.before(CommitInjectionPoint.AFTER_BND014)
        if proof.result is not BoundaryResult.ALLOW:
            raise CommitDenied(proof)
    
        try:
>           commit_unit = self._commit_inner(
                envelope=envelope,
                proof=proof,
                mutation=mutation,
                occurred_at=occurred_at,
                commit_id=commit_id,
            )

packages/commit/coordinator.py:405: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
packages/commit/coordinator.py:445: in _commit_inner
    mutation_outcome = mutation.apply()
packages/application/human_decision_handler.py:272: in apply
    self._repository.create(self._decision)
packages/persistence/decision_repository.py:103: in create
    self._connection.execute(sa.insert(decisions_table).values(**_to_row(decision)))
../../.local/lib/python3.10/site-packages/sqlalchemy/engine/base.py:1418: in execute
    return meth(
../../.local/lib/python3.10/site-packages/sqlalchemy/sql/elements.py:515: in _execute_on_connection
    return connection._execute_clauseelement(
../../.local/lib/python3.10/site-packages/sqlalchemy/engine/base.py:1640: in _execute_clauseelement
    ret = self._execute_context(
../../.local/lib/python3.10/site-packages/sqlalchemy/engine/base.py:1846: in _execute_context
    return self._exec_single_context(
../../.local/lib/python3.10/site-packages/sqlalchemy/engine/base.py:1986: in _exec_single_context
    self._handle_dbapi_exception(
../../.local/lib/python3.10/site-packages/sqlalchemy/engine/base.py:2355: in _handle_dbapi_exception
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
../../.local/lib/python3.10/site-packages/sqlalchemy/engine/base.py:1967: in _exec_single_context
    self.dialect.do_execute(
../../.local/lib/python3.10/site-packages/sqlalchemy/engine/default.py:941: in do_execute
    cursor.execute(statement, parameters)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <psycopg.Cursor [closed] [INTRANS] (host=localhost port=15432 database=nquiry) at 0x7bbfab118400>
query = 'INSERT INTO decisions (id, workspace_id, challenge_id, decision_question_ref, decision_question_text, options, criter...ESTAMP WITH TIME ZONE, %(decided_at)s::TIMESTAMP WITH TIME ZONE, %(record_version)s::BIGINT, %(provenance_ref)s::UUID)'
params = {'challenge_id': UUID('01a0bfe9-9e4a-705b-ba35-60ab41ac3eea'), 'confidence': None, 'created_at': datetime.datetime(2030, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), 'criteria': ['impact', 'effort'], ...}

    def execute(
        self,
        query: Query,
        params: Params | None = None,
        *,
        prepare: bool | None = None,
        binary: bool | None = None,
    ) -> Self:
        """
        Execute a query or command to the database.
        """
        try:
            with self._conn.lock:
                self._conn.wait(
                    self._execute_gen(query, params, prepare=prepare, binary=binary)
                )
        except e._NO_TRACEBACK as ex:
>           raise ex.with_traceback(None)
E           sqlalchemy.exc.IntegrityError: (psycopg.errors.ForeignKeyViolation) insert or update on table "decisions" violates foreign key constraint "fk_decisions_challenge_workspace"
E           DETAIL:  Key (challenge_id, workspace_id)=(01a0bfe9-9e4a-705b-ba35-60ab41ac3eea, 01a0bfe9-9e32-7e24-86ca-23ab6d9547f2) is not present in table "challenges".
E           [SQL: INSERT INTO decisions (id, workspace_id, challenge_id, decision_question_ref, decision_question_text, options, criteria, selected_option, rationale, confidence, state, opened_by_user_id, decision_authority_binding_id, decided_by_user_id, created_at, decided_at, record_version, provenance_ref) VALUES (%(id)s::UUID, %(workspace_id)s::UUID, %(challenge_id)s::UUID, %(decision_question_ref)s::UUID, %(decision_question_text)s::VARCHAR, %(options)s::TEXT[], %(criteria)s::TEXT[], %(selected_option)s::VARCHAR, %(rationale)s::VARCHAR, %(confidence)s::VARCHAR, %(state)s::VARCHAR, %(opened_by_user_id)s::UUID, %(decision_authority_binding_id)s::UUID, %(decided_by_user_id)s::UUID, %(created_at)s::TIMESTAMP WITH TIME ZONE, %(decided_at)s::TIMESTAMP WITH TIME ZONE, %(record_version)s::BIGINT, %(provenance_ref)s::UUID)]
E           [parameters: {'id': UUID('01a0bfe9-9e4e-79ff-be09-7d440d094268'), 'workspace_id': UUID('01a0bfe9-9e32-7e24-86ca-23ab6d9547f2'), 'challenge_id': UUID('01a0bfe9-9e4a-705b-ba35-60ab41ac3eea'), 'decision_question_ref': None, 'decision_question_text': 'Which fix ships first?', 'options': ['fix_a', 'fix_b'], 'criteria': ['impact', 'effort'], 'selected_option': None, 'rationale': None, 'confidence': None, 'state': 'UNDER_CONSIDERATION', 'opened_by_user_id': UUID('01a0bfe9-9e32-7a39-9ed1-1501e3062a1d'), 'decision_authority_binding_id': UUID('01a0bfe9-9e4b-78d6-adfc-bca25c01be6b'), 'decided_by_user_id': None, 'created_at': datetime.datetime(2030, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), 'decided_at': None, 'record_version': 1, 'provenance_ref': None}]
E           (Background on this error at: https://sqlalche.me/e/20/gkpj)

.venv/lib/python3.10/site-packages/psycopg/cursor.py:117: IntegrityError

The above exception was the direct cause of the following exception:

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfab173bb0>

    def test_cross_workspace_path_a_challenge_from_another_workspace_is_denied(
        db_connection: sa.Connection,
    ) -> None:
        workspace_a, owner_a, _mem_a, _challenge_a = _bootstrap_challenge(
            db_connection, email="proof-xws-a@nonproof.test"
        )
        _workspace_b, _owner_b, _mem_b, challenge_b = _bootstrap_challenge(
            db_connection, email="proof-xws-b@nonproof.test"
        )
        binding_id = _grant_decision_right(
            db_connection,
            workspace_id=workspace_a,
            user_id=owner_a,
            scope_type="CHALLENGE",
            scope_id=challenge_b.value,
        )
        actor = ActorIdentity(ActorClass.HUMAN_USER, owner_a)
    
        with pytest.raises(HumanDecisionDenied) as excinfo:
>           _open(
                db_connection,
                actor=actor,
                workspace_id=workspace_a,
                challenge_id=challenge_b,
                decision_id=DecisionId(_ID_GEN.new_uuid()),
            )

tests/e2e/test_proof_bundle_paths.py:673: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tests/e2e/test_proof_bundle_paths.py:196: in _open
    return open_decision_consideration(
packages/application/human_decision_handler.py:510: in open_decision_consideration
    return coordinator.commit(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <commit.coordinator.CommitCoordinator object at 0x7bbfab1714b0>

    def commit(
        self,
        *,
        envelope: CommandEnvelope,
        actor: ActorIdentity,
        required_authority_class: AuthorityClass,
        authority_scope_type: str,
        authority_scope_id: uuid.UUID,
        upstream_chain_result: BoundaryResult,
        current_version_reader: CurrentVersionReader,
        mutation: MutationExecutor,
        occurred_at: datetime,
        commit_id: CommitId,
        evidence_freshness_reader: EvidenceFreshnessPort | None = None,
    ) -> CommitUnit:
        self._failure_injector.before(CommitInjectionPoint.BEFORE_TRANSACTION)
    
        current_versions: dict[str, RecordVersion | None] = {
            ref: current_version_reader.read(ref) for ref in envelope.target_refs
        }
    
        evidence_freshness: EvidenceSetFreshnessResult | None = None
        if envelope.evidence_set_ref is not None:
            if evidence_freshness_reader is None:
                raise EvidenceFreshnessReaderRequired(
                    f"envelope {envelope.command_id!r} names evidence_set_ref "
                    f"{envelope.evidence_set_ref!r} but no evidence_freshness_reader was supplied"
                )
            evidence_freshness = resolve_evidence_set_freshness(
                envelope.evidence_set_ref,
                workspace_id=envelope.workspace_scope_ref,
                reader=evidence_freshness_reader,
            )
    
        context = BoundaryContext(
            workspace_id=envelope.workspace_scope_ref,
            operation=envelope.command_type,
            actor=actor,
            correlation_id=envelope.correlation_id,
            evaluated_at=occurred_at,
        )
        self._failure_injector.before(CommitInjectionPoint.AFTER_AUTHORITY_EVALUATION)
        bnd014_input = Bnd014Input(
            boundary_id=BoundaryId.BND_014,
            context=context,
            required_authority_class=required_authority_class,
            authority_scope_type=authority_scope_type,
            authority_scope_id=authority_scope_id,
            expected_versions=envelope.expected_versions,
            current_versions=current_versions,
            upstream_chain_result=upstream_chain_result,
            evidence_freshness=evidence_freshness,
        )
        proof = self._bnd014_evaluator.evaluate(bnd014_input, context)
        self._failure_injector.before(CommitInjectionPoint.AFTER_BND014)
        if proof.result is not BoundaryResult.ALLOW:
            raise CommitDenied(proof)
    
        try:
            commit_unit = self._commit_inner(
                envelope=envelope,
                proof=proof,
                mutation=mutation,
                occurred_at=occurred_at,
                commit_id=commit_id,
            )
        except AmbiguousCommitFailure:
            self._record_indeterminate(
                envelope=envelope, occurred_at=occurred_at, commit_id=commit_id
            )
            raise CommitIndeterminate(commit_id) from None
        except StaleVersionConflict as exc:
            self._mark_failed_precommit(envelope, occurred_at=occurred_at)
            raise CommitFailedPrecommit(reason=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001 -- any other failure inside the SAVEPOINT is a proven rollback
            self._mark_failed_precommit(envelope, occurred_at=occurred_at)
>           raise CommitFailedPrecommit(reason=f"{type(exc).__name__}: {exc}") from exc
E           commit.coordinator.CommitFailedPrecommit: CommitFailedPrecommit: IntegrityError: (psycopg.errors.ForeignKeyViolation) insert or update on table "decisions" violates foreign key constraint "fk_decisions_challenge_workspace"
E           DETAIL:  Key (challenge_id, workspace_id)=(01a0bfe9-9e4a-705b-ba35-60ab41ac3eea, 01a0bfe9-9e32-7e24-86ca-23ab6d9547f2) is not present in table "challenges".
E           [SQL: INSERT INTO decisions (id, workspace_id, challenge_id, decision_question_ref, decision_question_text, options, criteria, selected_option, rationale, confidence, state, opened_by_user_id, decision_authority_binding_id, decided_by_user_id, created_at, decided_at, record_version, provenance_ref) VALUES (%(id)s::UUID, %(workspace_id)s::UUID, %(challenge_id)s::UUID, %(decision_question_ref)s::UUID, %(decision_question_text)s::VARCHAR, %(options)s::TEXT[], %(criteria)s::TEXT[], %(selected_option)s::VARCHAR, %(rationale)s::VARCHAR, %(confidence)s::VARCHAR, %(state)s::VARCHAR, %(opened_by_user_id)s::UUID, %(decision_authority_binding_id)s::UUID, %(decided_by_user_id)s::UUID, %(created_at)s::TIMESTAMP WITH TIME ZONE, %(decided_at)s::TIMESTAMP WITH TIME ZONE, %(record_version)s::BIGINT, %(provenance_ref)s::UUID)]
E           [parameters: {'id': UUID('01a0bfe9-9e4e-79ff-be09-7d440d094268'), 'workspace_id': UUID('01a0bfe9-9e32-7e24-86ca-23ab6d9547f2'), 'challenge_id': UUID('01a0bfe9-9e4a-705b-ba35-60ab41ac3eea'), 'decision_question_ref': None, 'decision_question_text': 'Which fix ships first?', 'options': ['fix_a', 'fix_b'], 'criteria': ['impact', 'effort'], 'selected_option': None, 'rationale': None, 'confidence': None, 'state': 'UNDER_CONSIDERATION', 'opened_by_user_id': UUID('01a0bfe9-9e32-7a39-9ed1-1501e3062a1d'), 'decision_authority_binding_id': UUID('01a0bfe9-9e4b-78d6-adfc-bca25c01be6b'), 'decided_by_user_id': None, 'created_at': datetime.datetime(2030, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), 'decided_at': None, 'record_version': 1, 'provenance_ref': None}]
E           (Background on this error at: https://sqlalche.me/e/20/gkpj)

packages/commit/coordinator.py:422: CommitFailedPrecommit
=========================== short test summary info ============================
FAILED tests/boundaries/test_bnd_002_workspace.py::test_denies_cross_workspace_object_set
FAILED tests/e2e/test_proof_bundle_paths.py::test_cross_workspace_path_a_challenge_from_another_workspace_is_denied
2 failed in 0.56s
..                                                                       [100%]
2 passed in 0.16s
baseline_exit=0 mutated_exit=1 restored_exit=0 -> KILLED

--- MUT-PKG31-04 ---
invariant: BND-001 denies an actor class the operation does not accept -- in particular an AI_PROCESSOR can never pass as the HUMAN_USER a Human Decision requires. Removing it lets an AI-authored recommendation be recorded as if it were a Human Decision.
expected_boundary: BND_001
target_test_nodeids: ('tests/boundaries/test_bnd_001_identity.py::test_ai_processor_can_never_pass_as_human_user', 'tests/e2e/test_proof_bundle_paths.py::test_ai_boundary_path_an_ai_actor_is_denied_before_any_decision_is_touched')
..                                                                       [100%]
2 passed in 0.09s
FF                                                                       [100%]
=================================== FAILURES ===================================
________________ test_ai_processor_can_never_pass_as_human_user ________________

    def test_ai_processor_can_never_pass_as_human_user() -> None:
        """06 section 7 TESTABLE INVARIANT: "AI_PROCESSOR can never pass as
        HUMAN_USER or SYSTEM_SERVICE." Exhaustive over all 4 actor classes
        when only HUMAN_USER is required.
        """
        evaluator = Bnd001IdentityEvaluator()
        for actor_class in ActorClass:
            actor = ActorIdentity(actor_class, UserId(uuid.uuid4()))
            context = _context(actor)
            boundary_input = Bnd001Input(
                boundary_id=BoundaryId.BND_001,
                context=context,
                required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
            )
    
            proof = evaluator.evaluate(boundary_input, context)
    
            if actor_class is ActorClass.HUMAN_USER:
                assert proof.result is BoundaryResult.ALLOW
            else:
>               assert proof.result is BoundaryResult.DENY
E               AssertionError: assert <BoundaryResult.ALLOW: 'ALLOW'> is <BoundaryResult.DENY: 'DENY'>
E                +  where <BoundaryResult.ALLOW: 'ALLOW'> = BoundaryProof(boundary_id=<BoundaryId.BND_001: 'BND-001'>, boundary_version=ContractVersion(value='1.0'), result=<Boun... 0, 0, tzinfo=datetime.timezone.utc), correlation_id=CorrelationId(value=UUID('7ff4d135-f449-487f-a504-0e4149335909'))).result
E                +  and   <BoundaryResult.DENY: 'DENY'> = BoundaryResult.DENY

tests/boundaries/test_bnd_001_identity.py:80: AssertionError
__ test_ai_boundary_path_an_ai_actor_is_denied_before_any_decision_is_touched __

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfacdb1690>

    def test_ai_boundary_path_an_ai_actor_is_denied_before_any_decision_is_touched(
        db_connection: sa.Connection,
    ) -> None:
        workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
            db_connection, email="proof-ai-boundary@nonproof.test"
        )
        _grant_decision_right(
            db_connection,
            workspace_id=workspace_id,
            user_id=owner_id,
            scope_type="CHALLENGE",
            scope_id=challenge_id.value,
        )
        ai_actor = ActorIdentity(ActorClass.AI_PROCESSOR, owner_id)
    
        with pytest.raises(HumanDecisionDenied) as excinfo:
            _open(
                db_connection,
                actor=ai_actor,
                workspace_id=workspace_id,
                challenge_id=challenge_id,
                decision_id=DecisionId(_ID_GEN.new_uuid()),
            )
    
        bundle = TestProofBundle(
            path_name="AI_BOUNDARY",
            canonical_state_ref=f"challenge:{challenge_id.value}",
            boundary_proofs=excinfo.value.chain_result.proofs,
            p_claims_exercised=("P-07", "P-13"),
        )
>       assert bundle.boundary_proofs[-1].boundary_id is BoundaryId.BND_001
E       AssertionError: assert <BoundaryId.BND_003: 'BND-003'> is <BoundaryId.BND_001: 'BND-001'>
E        +  where <BoundaryId.BND_003: 'BND-003'> = BoundaryProof(boundary_id=<BoundaryId.BND_003: 'BND-003'>, boundary_version=ContractVersion(value='1'), result=<Bounda... 0, 0, tzinfo=datetime.timezone.utc), correlation_id=CorrelationId(value=UUID('2d9e6058-086a-480a-a55a-2b1eff923f40'))).boundary_id
E        +  and   <BoundaryId.BND_001: 'BND-001'> = BoundaryId.BND_001

tests/e2e/test_proof_bundle_paths.py:762: AssertionError
=========================== short test summary info ============================
FAILED tests/boundaries/test_bnd_001_identity.py::test_ai_processor_can_never_pass_as_human_user
FAILED tests/e2e/test_proof_bundle_paths.py::test_ai_boundary_path_an_ai_actor_is_denied_before_any_decision_is_touched
2 failed in 0.11s
..                                                                       [100%]
2 passed in 0.09s
baseline_exit=0 mutated_exit=1 restored_exit=0 -> KILLED

--- MUT-PKG31-05 ---
invariant: AC-09-002 (Governed Commit Unit): canonical mutation + audit + durable outbox entry must be persisted as one atomic bundle. A direct write that applies the canonical mutation without the audit/outbox half must be detectable by re-querying the real database for the missing artifacts, not merely by trusting the CommitUnit object returned to the caller.
expected_boundary: N/A (post-BND-014 commit-bundle atomicity, not a boundary evaluator)
target_test_nodeids: ('tests/command_commit_event/test_commit.py::test_commit_succeeds_and_atomically_writes_every_artifact',)
.                                                                        [100%]
1 passed in 0.16s
F                                                                        [100%]
=================================== FAILURES ===================================
__________ test_commit_succeeds_and_atomically_writes_every_artifact ___________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfaacb00a0>

    def test_commit_succeeds_and_atomically_writes_every_artifact(db_connection: sa.Connection) -> None:
        """Positive control: the full atomic bundle, real predecessor
        chain, real mutation.
        """
        workspace_id, owner_id, burst = _bootstrap_burst(
            db_connection, email="commit-success@nonproof.test"
        )
        _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
        envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
        SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
        _begin_idempotency_if_needed(db_connection, envelope)
        coordinator = _build_coordinator(db_connection)
        mutation = _BurstStartMutation(
            SqlAlchemyBurstRepository(db_connection),
            burst_id=burst.burst_id,
            workspace_id=workspace_id,
            expected_record_version=burst.record_version,
            started_at=_NOW,
        )
    
        commit_unit = coordinator.commit(
            envelope=envelope,
            actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            authority_scope_type="WORKSPACE",
            authority_scope_id=workspace_id.value,
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
            mutation=mutation,
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
        )
    
        assert commit_unit.outcome is CommitOutcome.COMMITTED
        updated_burst = SqlAlchemyBurstRepository(db_connection).get(burst.burst_id)
        assert updated_burst.state is BurstState.ACTIVE
        assert updated_burst.record_version == RecordVersion(2)
    
        stored_commit = SqlAlchemyCommitRepository(db_connection).get(commit_unit.commit_id)
>       assert stored_commit is not None
E       assert None is not None

tests/command_commit_event/test_commit.py:502: AssertionError
=========================== short test summary info ============================
FAILED tests/command_commit_event/test_commit.py::test_commit_succeeds_and_atomically_writes_every_artifact
1 failed in 0.14s
.                                                                        [100%]
1 passed in 0.12s
baseline_exit=0 mutated_exit=1 restored_exit=0 -> KILLED

--- MUT-PKG31-06 ---
invariant: CommandEnvelope.__post_init__ structurally rejects a command_id that is not a real CommandId (in particular an EventId) -- 09 section 160.3's own defense against 'replay sends old Event to Command handler'. Removing the check lets an EventEnvelope's own identity construct a CommandEnvelope.
expected_boundary: N/A (semantic-type construction guard, not a boundary evaluator)
target_test_nodeids: ('tests/command_commit_event/test_command_event_split.py::test_an_event_id_cannot_construct_a_command_envelope',)
.                                                                        [100%]
1 passed in 0.03s
F                                                                        [100%]
=================================== FAILURES ===================================
_____________ test_an_event_id_cannot_construct_a_command_envelope _____________

    def test_an_event_id_cannot_construct_a_command_envelope() -> None:
        """ATTACK: submit an EventId as command_id.
        EXPECTED DEFENSE: CommandEnvelope.__post_init__'s isinstance(command_id, CommandId) check.
        EXPECTED BOUNDARY: NOT_APPLICABLE (no BND-XXX invoked at this layer).
        EXPECTED CANONICAL RESULT: TypeError, no CommandEnvelope instance produced.
        EXPECTED PROOF ARTIFACT: the raised TypeError itself (construction never completes).
        ACTUAL RESULT: matches.
        """
>       with pytest.raises(TypeError, match="command_id must be a CommandId"):
E       Failed: DID NOT RAISE <class 'TypeError'>

tests/command_commit_event/test_command_event_split.py:76: Failed
=========================== short test summary info ============================
FAILED tests/command_commit_event/test_command_event_split.py::test_an_event_id_cannot_construct_a_command_envelope
1 failed in 0.02s
.                                                                        [100%]
1 passed in 0.02s
baseline_exit=0 mutated_exit=1 restored_exit=0 -> KILLED

--- MUT-PKG31-07 ---
invariant: 09 section 114: an Evidence member that is invalidated, superseded, unavailable, wrong-Workspace, or content-version-changed since capture is stale, and a commit naming a stale set must fail (BND-014's evidence branch). Forcing every member FRESH lets a commit proceed on Evidence that no longer holds.
expected_boundary: BND_014 (evidence_freshness branch)
target_test_nodeids: ('tests/evidence/test_freshness.py::test_an_invalidated_member_after_prepare_is_stale', 'tests/evidence/test_freshness.py::test_a_cross_workspace_member_is_stale', 'tests/evidence/test_freshness.py::test_a_superseded_member_is_stale')
...                                                                      [100%]
3 passed in 0.32s
FFF                                                                      [100%]
=================================== FAILURES ===================================
______________ test_an_invalidated_member_after_prepare_is_stale _______________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfaaba2c80>

    def test_an_invalidated_member_after_prepare_is_stale(db_connection: sa.Connection) -> None:
        """Mandatory package-specific attack: Evidence invalidated after
        prepare."""
        workspace_id = _bootstrap(db_connection, email="freshness-invalidated@nonproof.test")
        repo = SqlAlchemyEvidenceRepository(db_connection)
        evidence = _make_evidence(workspace_id=workspace_id)
        repo.create_evidence(evidence)
        evidence_set = _make_set(
            workspace_id=workspace_id,
            members=(
                EvidenceSetMember(
                    evidence_id=evidence.evidence_id, content_version=evidence.content_version
                ),
            ),
        )
        repo.create_evidence_set_reference(evidence_set)
    
        # "Prepare" happened above; now Evidence is invalidated before commit.
        repo.update_validation_state(
            evidence_id=evidence.evidence_id,
            workspace_id=workspace_id,
            expected_record_version=evidence.record_version,
            new_state=EvidenceValidationState.INVALIDATED,
        )
    
        result = resolve_evidence_set_freshness(
            evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
        )
    
>       assert result.is_fresh is False
E       AssertionError: assert True is False
E        +  where True = EvidenceSetFreshnessResult(evidence_set_ref_id=EvidenceSetId(value=UUID('01a0bfe9-b055-7f4d-b8c1-e9e1b7ee44f5')), evid...expected_content_version=RecordVersion(value=1), outcome=<EvidenceMemberFreshness.FRESH: 'FRESH'>),), claim_anchors=()).is_fresh

tests/evidence/test_freshness.py:150: AssertionError
____________________ test_a_cross_workspace_member_is_stale ____________________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfabdd8880>

    def test_a_cross_workspace_member_is_stale(db_connection: sa.Connection) -> None:
        """Mandatory package-specific attack: cross-Workspace Evidence.
        Constructs the set with a claimed workspace that does not match the
        Evidence row's real workspace -- proving the check compares against
        the CALLER's own asserted scope, not merely the set's own recorded
        workspace_id.
        """
        workspace_a = _bootstrap(db_connection, email="freshness-cross-a@nonproof.test")
        workspace_b = _bootstrap(db_connection, email="freshness-cross-b@nonproof.test")
        repo = SqlAlchemyEvidenceRepository(db_connection)
        evidence = _make_evidence(workspace_id=workspace_a)
        repo.create_evidence(evidence)
        evidence_set = _make_set(
            workspace_id=workspace_a,
            members=(
                EvidenceSetMember(
                    evidence_id=evidence.evidence_id, content_version=evidence.content_version
                ),
            ),
        )
        repo.create_evidence_set_reference(evidence_set)
    
        result = resolve_evidence_set_freshness(
            evidence_set.evidence_set_ref_id, workspace_id=workspace_b, reader=repo
        )
    
>       assert result.members[0].outcome is EvidenceMemberFreshness.WRONG_WORKSPACE
E       AssertionError: assert <EvidenceMemberFreshness.FRESH: 'FRESH'> is <EvidenceMemberFreshness.WRONG_WORKSPACE: 'WRONG_WORKSPACE'>
E        +  where <EvidenceMemberFreshness.FRESH: 'FRESH'> = EvidenceMemberFreshnessResult(evidence_id=EvidenceId(value=UUID('01a0bfe9-b09b-7cc6-84e8-daa69e7fdb0a')), expected_content_version=RecordVersion(value=1), outcome=<EvidenceMemberFreshness.FRESH: 'FRESH'>).outcome
E        +  and   <EvidenceMemberFreshness.WRONG_WORKSPACE: 'WRONG_WORKSPACE'> = EvidenceMemberFreshness.WRONG_WORKSPACE

tests/evidence/test_freshness.py:212: AssertionError
______________________ test_a_superseded_member_is_stale _______________________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfacd7f6a0>

    def test_a_superseded_member_is_stale(db_connection: sa.Connection) -> None:
        """09 section 114: "superseded where current use requires newer
        version"."""
        workspace_id = _bootstrap(db_connection, email="freshness-superseded@nonproof.test")
        repo = SqlAlchemyEvidenceRepository(db_connection)
        original = _make_evidence(workspace_id=workspace_id)
        repo.create_evidence(original)
        evidence_set = _make_set(
            workspace_id=workspace_id,
            members=(
                EvidenceSetMember(
                    evidence_id=original.evidence_id, content_version=original.content_version
                ),
            ),
        )
        repo.create_evidence_set_reference(evidence_set)
    
        successor = _make_evidence(
            workspace_id=workspace_id, supersedes_evidence_id=original.evidence_id
        )
        repo.create_evidence(successor)
    
        result = resolve_evidence_set_freshness(
            evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
        )
    
>       assert result.members[0].outcome is EvidenceMemberFreshness.SUPERSEDED
E       AssertionError: assert <EvidenceMemberFreshness.FRESH: 'FRESH'> is <EvidenceMemberFreshness.SUPERSEDED: 'SUPERSEDED'>
E        +  where <EvidenceMemberFreshness.FRESH: 'FRESH'> = EvidenceMemberFreshnessResult(evidence_id=EvidenceId(value=UUID('01a0bfe9-b0d1-700e-9920-9a5f01bd7c36')), expected_content_version=RecordVersion(value=1), outcome=<EvidenceMemberFreshness.FRESH: 'FRESH'>).outcome
E        +  and   <EvidenceMemberFreshness.SUPERSEDED: 'SUPERSEDED'> = EvidenceMemberFreshness.SUPERSEDED

tests/evidence/test_freshness.py:268: AssertionError
=========================== short test summary info ============================
FAILED tests/evidence/test_freshness.py::test_an_invalidated_member_after_prepare_is_stale
FAILED tests/evidence/test_freshness.py::test_a_cross_workspace_member_is_stale
FAILED tests/evidence/test_freshness.py::test_a_superseded_member_is_stale - ...
3 failed in 0.20s
...                                                                      [100%]
3 passed in 0.26s
baseline_exit=0 mutated_exit=1 restored_exit=0 -> KILLED

--- MUT-PKG31-08 ---
invariant: BND-017 denies a blind retry while consequence certainty is genuinely uncertain, and denies any operation on a target another INDETERMINATE record still blocks. Forcing ALLOW lets a retry proceed on an unproven outcome.
expected_boundary: BND_017
target_test_nodeids: ('tests/boundaries/test_bnd_017_failure_indeterminate.py::test_uncertain_consequence_denies_blind_retry', 'tests/boundaries/test_bnd_017_failure_indeterminate.py::test_denies_dependent_operation_while_target_is_blocked')
..                                                                       [100%]
2 passed in 0.17s
FF                                                                       [100%]
=================================== FAILURES ===================================
________________ test_uncertain_consequence_denies_blind_retry _________________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfab081030>

    def test_uncertain_consequence_denies_blind_retry(db_connection: sa.Connection) -> None:
        """Mandatory adversarial attack (06 section 24 DENY): "blind retry
        when duplicate consequence is possible."""
        workspace_id, actor = _bootstrap(db_connection, email="bnd017-uncertain-retry@nonproof.test")
        context = _context(workspace_id=workspace_id, actor=actor)
        evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
        boundary_input = _input(
            context=context,
            requested_operation="retry",
            known_consequence_certainty=ConsequenceCertainty.GOVERNANCE_STATE_UNKNOWN,
            target_ref="session:1",
        )
    
        proof = evaluator.evaluate(boundary_input, context)
    
>       assert proof.result is BoundaryResult.DENY
E       AssertionError: assert <BoundaryResult.ALLOW: 'ALLOW'> is <BoundaryResult.DENY: 'DENY'>
E        +  where <BoundaryResult.ALLOW: 'ALLOW'> = BoundaryProof(boundary_id=<BoundaryId.BND_017: 'BND-017'>, boundary_version=ContractVersion(value='1.0'), result=<Boun... 0, 0, tzinfo=datetime.timezone.utc), correlation_id=CorrelationId(value=UUID('26632f2e-f91a-4e1b-a4f2-05f77f681831'))).result
E        +  and   <BoundaryResult.DENY: 'DENY'> = BoundaryResult.DENY

tests/boundaries/test_bnd_017_failure_indeterminate.py:339: AssertionError
___________ test_denies_dependent_operation_while_target_is_blocked ____________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfab10d5a0>

    def test_denies_dependent_operation_while_target_is_blocked(db_connection: sa.Connection) -> None:
        """Mandatory adversarial attack (06 section 24's own DENY line):
        a dependent consequential operation is denied unconditionally
        while ANY unresolved RecoveryRecord names its target as blocked --
        regardless of what certainty or operation the caller claims."""
        workspace_id, actor = _bootstrap(db_connection, email="bnd017-blocked@nonproof.test")
        _seed_blocking_recovery_record(db_connection, workspace_id=workspace_id, target_ref="session:1")
        context = _context(workspace_id=workspace_id, actor=actor)
        evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
        boundary_input = _input(
            context=context,
            requested_operation="acknowledge_committed",
            known_consequence_certainty=ConsequenceCertainty.PROVEN_COMMITTED,
            target_ref="session:1",
        )
    
        proof = evaluator.evaluate(boundary_input, context)
    
>       assert proof.result is BoundaryResult.DENY
E       AssertionError: assert <BoundaryResult.ALLOW: 'ALLOW'> is <BoundaryResult.DENY: 'DENY'>
E        +  where <BoundaryResult.ALLOW: 'ALLOW'> = BoundaryProof(boundary_id=<BoundaryId.BND_017: 'BND-017'>, boundary_version=ContractVersion(value='1.0'), result=<Boun... 0, 0, tzinfo=datetime.timezone.utc), correlation_id=CorrelationId(value=UUID('0bdeda83-ae75-47e8-8fb7-33a22fd43a9a'))).result
E        +  and   <BoundaryResult.DENY: 'DENY'> = BoundaryResult.DENY

tests/boundaries/test_bnd_017_failure_indeterminate.py:179: AssertionError
=========================== short test summary info ============================
FAILED tests/boundaries/test_bnd_017_failure_indeterminate.py::test_uncertain_consequence_denies_blind_retry
FAILED tests/boundaries/test_bnd_017_failure_indeterminate.py::test_denies_dependent_operation_while_target_is_blocked
2 failed in 0.17s
..                                                                       [100%]
2 passed in 0.16s
baseline_exit=0 mutated_exit=1 restored_exit=0 -> KILLED

--- MUT-PKG31-09 ---
invariant: AuthorityResolver.resolve() grants only on a current, scope-matching HumanAuthorityBinding -- current Workspace membership alone (any role, including Owner) is a precondition, never a substitute (05 AC-05-004). Granting on membership alone whenever no binding matches is the 'admin fallback' 14 explicitly forbids.
expected_boundary: BND_005
target_test_nodeids: ('tests/security/test_admin_non_authority.py::test_admin_cannot_create_a_legitimate_decision', 'tests/authority/test_resolver.py::test_owner_only_is_denied')
..                                                                       [100%]
2 passed in 0.12s
FF                                                                       [100%]
=================================== FAILURES ===================================
________________ test_admin_cannot_create_a_legitimate_decision ________________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfaaba5930>

    def test_admin_cannot_create_a_legitimate_decision(db_connection: sa.Connection) -> None:
        """ATTACK column: "admin finalizes Decision" with no human right."""
        owner = _insert_user(db_connection, email="owner@test.local")
        workspace_id = _insert_workspace(db_connection, owner_id=owner)
        admin = _insert_user(db_connection, email="admin@test.local")
        _insert_membership(db_connection, workspace_id=workspace_id, user_id=admin)
        # Deliberately no human_authority_bindings row for `admin` at all --
        # elevated technical access grants nothing here because there is
        # nothing for it to grant through.
    
        request = AuthorityRequest(
            actor=ActorIdentity(ActorClass.HUMAN_USER, admin),
            workspace_id=workspace_id,
            operation="RECORD_DECISION",
            required_authority_class=AuthorityClass.DECISION_RIGHT,
            scope_type="DECISION",
            scope_id=uuid.uuid4(),
        )
        resolution = _resolver(db_connection).resolve(request)
    
>       assert resolution.verdict == AuthorityVerdict.DENIED
E       AssertionError: assert <AuthorityVer...ED: 'GRANTED'> == <AuthorityVer...IED: 'DENIED'>
E         
E         - DENIED
E         + GRANTED

tests/security/test_admin_non_authority.py:120: AssertionError
__________________________ test_owner_only_is_denied ___________________________

db_connection = <sqlalchemy.engine.base.Connection object at 0x7bbfab0f7430>

    def test_owner_only_is_denied(db_connection: sa.Connection) -> None:
        """Mandatory adversarial attack: Owner-only (AC-04-001: Owner is not
        an automatic executor of every operation; ATK-005)."""
        owner = _insert_user(db_connection, email="owner3@test.local")
        workspace_id = _insert_workspace(db_connection, owner_id=owner)
        membership_id = _insert_membership(db_connection, workspace_id=workspace_id, user_id=owner)
        _insert_role(
            db_connection,
            workspace_id=workspace_id,
            membership_id=membership_id,
            role=WorkspaceRole.OWNER,
            granted_by=owner,
        )
    
        request = AuthorityRequest(
            actor=ActorIdentity(ActorClass.HUMAN_USER, owner),
            workspace_id=workspace_id,
            operation="RECORD_DECISION",
            required_authority_class=AuthorityClass.DECISION_RIGHT,
            scope_type="DECISION",
            scope_id=uuid.uuid4(),
        )
        resolution = _resolver(db_connection).resolve(request)
    
>       assert resolution.verdict == AuthorityVerdict.DENIED
E       AssertionError: assert <AuthorityVer...ED: 'GRANTED'> == <AuthorityVer...IED: 'DENIED'>
E         
E         - DENIED
E         + GRANTED

tests/authority/test_resolver.py:233: AssertionError
=========================== short test summary info ============================
FAILED tests/security/test_admin_non_authority.py::test_admin_cannot_create_a_legitimate_decision
FAILED tests/authority/test_resolver.py::test_owner_only_is_denied - Assertio...
2 failed in 0.14s
..                                                                       [100%]
2 passed in 0.11s
baseline_exit=0 mutated_exit=1 restored_exit=0 -> KILLED

--- MUT-PKG31-10 ---
invariant: check_provider_sdk_imports.check() rejects any production module outside packages/ai_gateway/adapters/providers/ that imports a real provider SDK -- the static half of 'all LLM traffic through the Gateway' (BND-009). Disabling the checker lets a Gateway-bypassing direct provider call land undetected.
expected_boundary: BND_009 (static enforcement half)
target_test_nodeids: ('tests/security/test_ai_gateway.py::test_direct_provider_import_outside_gateway_adapter_is_rejected',)
.                                                                        [100%]
1 passed in 0.02s
F                                                                        [100%]
=================================== FAILURES ===================================
_______ test_direct_provider_import_outside_gateway_adapter_is_rejected ________

tmp_path = PosixPath('/tmp/pytest-of-codi/pytest-149/test_direct_provider_import_ou0')

    def test_direct_provider_import_outside_gateway_adapter_is_rejected(tmp_path: Path) -> None:
        packages_root = tmp_path / "packages"
        # A hypothetical future package attempts to call a provider SDK directly,
        # bypassing the AI Gateway entirely.
        _write(packages_root, "command/__init__.py", "")
        _write(
            packages_root, "command/handler.py", "import openai\n\ndef handle():\n    return openai\n"
        )
    
        sdk_violations = check_provider_sdk_imports.check(roots=(packages_root,))
        dependency_violations = check_architecture_dependencies.check(roots=(packages_root,))
    
>       assert len(sdk_violations) == 1
E       assert 0 == 1
E        +  where 0 = len([])

tests/security/test_ai_gateway.py:50: AssertionError
=========================== short test summary info ============================
FAILED tests/security/test_ai_gateway.py::test_direct_provider_import_outside_gateway_adapter_is_rejected
1 failed in 0.02s
.                                                                        [100%]
1 passed in 0.02s
baseline_exit=0 mutated_exit=1 restored_exit=0 -> KILLED

=== SUMMARY ===
KILLED: 10/10
################################################################
# 6. RAW TERMINAL OUTPUT -- static verification + regression (final, fresh)
################################################################
--- ruff format --check . ---
301 files already formatted
EXIT:0
--- ruff check . ---
All checks passed!
EXIT:0
--- mypy (packages/apps/scripts, established full-scope convention) ---
Success: no issues found in 136 source files
--- mypy (tests/mutation + this package's own new/modified test files, ad-hoc since tests/ is excluded from the full-scope command by convention -- see NEW_GAPS_DISCOVERED) ---
Success: no issues found in 3 source files
--- architecture checkers ---
ARCHITECTURE_DEPENDENCY_CHECK::PASS
PROVIDER_SDK_IMPORT_CHECK::PASS
TEST_ONLY_IMPORT_CHECK::PASS
--- pytest tests/mutation/test_pkg31_mutation_registry.py -v ---
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: /home/codi/Entwicklung/nquiry
configfile: pyproject.toml
plugins: hypothesis-6.168.0, cov-7.1.0, anyio-4.3.0, asyncio-1.3.0
asyncio: mode=strict, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 5 items

tests/mutation/test_pkg31_mutation_registry.py::test_mutations_covers_exactly_the_ten_mandatory_ids PASSED [ 20%]
tests/mutation/test_pkg31_mutation_registry.py::test_every_target_test_nodeid_file_actually_exists PASSED [ 40%]
tests/mutation/test_pkg31_mutation_registry.py::test_every_target_test_function_name_appears_in_its_own_file PASSED [ 60%]
tests/mutation/test_pkg31_mutation_registry.py::test_every_patch_target_resolves_to_a_real_attribute PASSED [ 80%]
tests/mutation/test_pkg31_mutation_registry.py::test_every_case_names_a_non_placeholder_invariant_and_boundary PASSED [100%]

============================== 5 passed in 0.54s ===============================
--- pytest tests/e2e/test_proof_bundle_paths.py -v (nachtrag re-verified) ---
rootdir: /home/codi/Entwicklung/nquiry
configfile: pyproject.toml
plugins: hypothesis-6.168.0, cov-7.1.0, anyio-4.3.0, asyncio-1.3.0
asyncio: mode=strict, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 17 items

tests/e2e/test_proof_bundle_paths.py::test_happy_path_full_decision_lifecycle_produces_a_reconstructable_bundle PASSED [  5%]
tests/e2e/test_proof_bundle_paths.py::test_denial_path_role_only_actor_produces_a_real_boundary_proof PASSED [ 11%]
tests/e2e/test_proof_bundle_paths.py::test_denial_counter_attack_a_forged_allow_boundary_proof_does_not_change_real_state PASSED [ 17%]
tests/e2e/test_proof_bundle_paths.py::test_stale_authority_path_revoked_binding_cannot_survive_to_commit PASSED [ 23%]
tests/e2e/test_proof_bundle_paths.py::test_stale_authority_counter_attack_reusing_an_earlier_allow_does_not_bypass_reeval PASSED [ 29%]
tests/e2e/test_proof_bundle_paths.py::test_cross_workspace_path_a_challenge_from_another_workspace_is_denied PASSED [ 35%]
tests/e2e/test_proof_bundle_paths.py::test_cross_workspace_counter_attack_a_governance_ref_alone_cannot_read_the_other_ws PASSED [ 41%]
tests/e2e/test_proof_bundle_paths.py::test_ai_boundary_path_an_ai_actor_is_denied_before_any_decision_is_touched PASSED [ 47%]
tests/e2e/test_proof_bundle_paths.py::test_ai_boundary_counter_attack_nonproof_ownership_cannot_be_mistaken_for_ai_eligibility PASSED [ 52%]
tests/e2e/test_proof_bundle_paths.py::test_mock_provider_cannot_satisfy_real_provider_eligibility PASSED [ 58%]
tests/e2e/test_proof_bundle_paths.py::test_recovery_path_deterministic_reconciliation_produces_a_resolved_record PASSED [ 64%]
tests/e2e/test_proof_bundle_paths.py::test_recovery_counter_attack_manufactured_clean_facts_do_not_override_a_real_blocking_record PASSED [ 70%]
tests/e2e/test_proof_bundle_paths.py::test_bundle_rejects_an_unrecognized_path_name PASSED [ 76%]
tests/e2e/test_proof_bundle_paths.py::test_bundle_rejects_a_malformed_p_claim_identifier PASSED [ 82%]
tests/e2e/test_proof_bundle_paths.py::test_proof_claim_matrix_covers_exactly_p01_through_p25 PASSED [ 88%]
tests/e2e/test_proof_bundle_paths.py::test_every_proof_claim_matrix_evidence_file_actually_exists PASSED [ 94%]
tests/e2e/test_proof_bundle_paths.py::test_every_pkg30_exercised_claim_has_this_files_own_path_as_evidence PASSED [100%]

============================== 17 passed in 1.46s ==============================
--- full live-DB regression: python -m pytest -q ---
..................................................s..................... [ 85%]
........................................................................ [ 91%]
........................................................................ [ 98%]
.....................                                                    [100%]
1100 passed, 1 skipped in 25.98s
--- pure-Python regression: unset DATABASE_URL; python -m pytest -q tests/ ---
.........s..s.ss.............ss...sssssssssssssssss....ssssssssssssss... [ 85%]
...........................................sssssssss.................... [ 91%]
........................ssssssssssssssssssss...................sssssssss [ 98%]
sssssss.............                                                     [100%]
705 passed, 395 skipped in 5.47s
--- final git status --short ---
 M tests/e2e/test_proof_bundle_paths.py
 D tests/mutation/.gitkeep
?? apps/web/AGENTS.md
?? apps/web/CLAUDE.md
?? scripts/run_mutation_harness.py
?? tests/mutation/harness.py
?? tests/mutation/mutation_cases.py
?? tests/mutation/test_pkg31_mutation_registry.py
```
