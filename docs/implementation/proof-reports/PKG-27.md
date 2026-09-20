# PKG-27 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-27
PACKAGE_TITLE: Observability correlation
BUILD_PHASE: 10
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  11_SECURITY_PRIVACY_OBSERVABILITY.md section 36 ("Observability
    Constitutional Rule" -- [ARCHITECTURAL CLOSURE] AC-11-013:
    "OBSERVABILITY RECONSTRUCTS TECHNICAL BEHAVIOR. OBSERVABILITY DOES
    NOT DEFINE DOMAIN TRUTH OR AUTHORITY... Telemetry absence does not
    prove event absence. Telemetry presence does not prove domain
    legitimacy"), section 37 ("Observability Correlation Model" -- the
    exact identity list: "correlation_id, command_id, attempt_id,
    commit_id, event_id, generation_id, recovery_id... A single
    governed operation should be traceable across API edge, Command
    processing, governance evaluation, boundaries, CommitUnit, outbox,
    AI Gateway, tool invocation and recovery without embedding reusable
    authority into trace context"), section 38 ("Trace Context Safety"
    -- the exact "must not carry" list: "HumanAuthorityBinding as
    reusable authorization; raw secrets; authentication tokens;
    unrestricted Evidence content; full prompts by default; full
    provider payloads by default; domain authority decisions as
    client-editable attributes"), section 39 (Metric Classes), section
    40 (Alerting -- "ALERT != PROOF. ALERT != AUTHORITY. ALERT != HUMAN
    DECISION")
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md's T9 row
  14_IMPLEMENTATION_SEQUENCE.md's PKG-27 package manifest (BUILD_PHASE
    10, OBJECTIVE "Structured diagnostic correlation without
    authority/truth... Implement structured ObservationContext and
    local OpenTelemetry API sink with correlation_id, command_id,
    attempt_id, commit_id, event_id, generation_id, recovery_id,
    operation, boundary result and failure class. Minimize content",
    REQUIRED PREDECESSORS PKG-13/PKG-19/PKG-24, DATABASE_CHANGES none,
    PROOF_CLAIMS P-25), the repository-topology row for
    `packages/observability/context.py` ("correlation | 11 |
    semantic_types | authority tokens | tests/security/test_observability.py
    | 10"), section 3.1's own `observability` allow-list
    (`semantic_types` only)
  16_DECISION_GAP_REGISTER.md's own P-25 row

14_REQUIREMENTS_MATERIALIZED:
  `ObservationContext` (14's own PUBLIC_INTERFACES) with exactly the
  10 fields the PKG-27 OBJECTIVE line names: `correlation_id`,
  `command_id`, `attempt_id`, `commit_id`, `event_id`, `generation_id`,
  `recovery_id`, `operation`, `boundary_result`, `failure_class`.
  `ObservationSink` port + `LocalOtelObservationSink` -- the "local
  OpenTelemetry API sink" the OBJECTIVE names, built against
  `opentelemetry-api` only (never the SDK, at runtime). "Minimize
  content" materialized structurally (no field exists for anything
  11 section 38 forbids) plus a length-cap/closed-vocabulary-mirror
  defense-in-depth layer on the three string fields. Real "app/worker
  instrumentation integration": the one real endpoint (`/healthz`) and
  the one real entrypoint (`nquiry_worker.__main__.main`) each now emit
  one genuine `ObservationContext` per invocation.

PREDECESSORS_VERIFIED:
  PKG-13 (a579e80, PACKAGE_PASS, CRITICAL -- Commit coordinator and
    BND-014; `commit_id`/`CommitUnit` is one of this package's own
    correlation identities).
  PKG-19 (93f2816, PACKAGE_PASS -- AI Gateway and MockProvider;
    `generation_id` is one of this package's own correlation
    identities).
  PKG-24 (45ce69f, PACKAGE_PASS, CRITICAL -- BND-017/BND-018 and
    Recovery Command; `recovery_id` is one of this package's own
    correlation identities).
  Full chain unbroken: PKG-00 dd4aad2 through PKG-26 1c010a8. No file
  outside this package's own new-file set was touched beyond the
  disclosed extension points (see FILES_MODIFIED).

FILES_CREATED:
  packages/observability/context.py
  tests/security/test_observability.py

FILES_MODIFIED:
  packages/observability/__init__.py (PKG-00's own Phase-0 skeleton
    docstring updated to reflect real PKG-27 materialization; no
    architectural claim changed)
  apps/api/src/nquiry_api/main.py (the real `/healthz` endpoint now
    emits one `ObservationContext` via `LocalOtelObservationSink` per
    request -- the "app... instrumentation integration" 14's own
    OBJECTIVE names; no Command/Query route added, none exists yet)
  apps/worker/src/nquiry_worker/__main__.py (the real, still-otherwise-
    no-op entrypoint now emits one `ObservationContext` per invocation
    -- the "...worker instrumentation integration" half; still performs
    no consequential work and claims none, unchanged)
  pyproject.toml (`opentelemetry-sdk` added to `[project.optional-
    dependencies].dev` -- DEV-ONLY, never a runtime dependency; see
    DIFF_AUDIT for why this specific, narrow addition is disclosed as
    directly required by this package)
  scripts/check_architecture_dependencies.py
    (`INTERNAL_ALLOWED["nquiry_api"]`/`["nquiry_worker"]` each gain
    `observability`, so the real call sites above can import
    `ObservationContext`/`LocalOtelObservationSink`;
    `EXTERNAL_FORBIDDEN["observability"]` added --
    `_WEB_FRAMEWORK | _DB_DRIVER | PROVIDER_SDK_MODULES`, deliberately
    NOT including `opentelemetry` itself, the one package this codebase
    designates to hold it directly)

FILES_DELETED: none

MIGRATIONS_CREATED: none. 14's own DATABASE_CHANGES mapping for this
  package is "none" -- no domain schema, confirmed by
  `verify_migrations.py` staying at head `047bdf9bc528` (PKG-26's own,
  unchanged).
SCHEMA_CHANGES: none.
DB_PRIVILEGE_CHANGES: none.

PUBLIC_INTERFACES_CREATED:
  observability.context.{ObservationContext, ObservationSink,
    LocalOtelObservationSink} -- 14's own literal PUBLIC INTERFACES:
    "ObservationContext".

COMMANDS_CREATED: NOT_APPLICABLE. 14 assigns no Command to this
  package.
QUERIES_CREATED: NOT_APPLICABLE. No Query assigned.
EVENTS_CREATED: NOT_APPLICABLE. No Event contract assigned; emitting an
  `ObservationContext` is diagnostic only, never a Domain Event (this
  package's own FAILURE_RECOVERY line: "Diagnostic only").

BOUNDARIES_CREATED_OR_CHANGED: none (no `boundaries.BndNNN*` file
  created or modified). This package's own BOUNDARIES line: "Observe
  result refs only" -- `ObservationContext.boundary_result` is a plain,
  closed-vocabulary-MIRRORED string (never `boundaries.types.BoundaryResult`
  itself, since `observability`'s own allow-list excludes `boundaries`
  entirely), holding only the terminal RESULT label a boundary already
  produced elsewhere -- never a boundary input, never something this
  package evaluates or influences.

AUTHORITY_PATH: This package's own AUTHORITY line -- "Never consumed as
  authority proof" -- is a structural fact, not a runtime promise:
  `ObservationSink.emit`/`LocalOtelObservationSink.emit` both return
  `None` (`test_mut_pkg27_01_emitting_never_returns_anything_authority_shaped`),
  and `scripts/check_architecture_dependencies.py`'s own dependency
  graph proves NONE of `boundaries`/`authority`/`governance` may import
  `observability` at all
  (`test_mandatory_attack_trace_value_used_as_authority_no_such_dependency_exists`)
  -- no boundary evaluator or `AuthorityResolver` could ever consume an
  `ObservationContext` as a decision input even if it wanted to. No new
  Decision Right, `AuthorityClass` value, or Owner/Admin superpower was
  introduced.
EVIDENCE_PATH: This package's own EVIDENCE line -- "No sensitive
  Evidence content by default" -- proven structurally, not merely by
  default-off configuration: `ObservationContext` has NO field that
  could ever carry Evidence content at all (a `TypeError` for an
  unexpected keyword, proven by
  `test_mandatory_attack_full_evidence_in_log_no_content_field_exists`,
  not a value-level redaction that could be forgotten).
AI_PATH: This package's own AI line -- "No raw prompt by default" --
  likewise structural: no field exists for prompt/provider-payload
  content; `operation`'s own length cap
  (`test_mandatory_attack_prompt_content_leakage_operation_length_capped`)
  additionally rejects an attempt to smuggle prompt-scale content
  through the one permitted free-text field. `generation_id` (an AI
  correlation identity) is a bare `GenerationId`, never the generation's
  own content.
RECOVERY_PATH: This package's own FAILURE_RECOVERY line -- "Diagnostic
  only" -- `recovery_id`/`failure_class` are bare correlation
  references; emitting an `ObservationContext` never restores,
  reconciles, or otherwise mutates any Recovery state, and cannot (no
  persistence access at all, structurally).

TESTS_CREATED:
  tests/security/test_observability.py (17 tests -- pure Python plus
    one real, module-scoped `opentelemetry.sdk` `TracerProvider`/
    `InMemorySpanExporter` capture, no PostgreSQL required: exact
    minimal field-set proof; frozen/immutable; wrong-type rejection for
    `correlation_id` and every optional strong-ID field; empty
    `operation` rejection; the 5 mandatory package-specific attacks
    (secret in trace x2, full Evidence in log, prompt content leakage,
    trace value used as authority, missing audit replaced by log);
    `ObservationSink` Protocol shape; a real emitted span's own exact
    attribute set, present and absent cases; MUT-PKG27-01
    authority-shape guard; a genuinely separate, fresh subprocess
    proving the sink never requires an SDK to be configured to avoid
    crashing)

TESTS_MODIFIED: none. Fourth package in this Phase (after
  PKG-22/23/25/26) with zero modified test files.

TARGETED_TEST_RESULTS:
  Pure-Python (no `DATABASE_URL`, `tests/`): 694 passed, 384 skipped
    (skips are the established `SKIPPED_NO_DATABASE` convention; this
    package's own 17 new tests need no database at all and are never
    among the skips).
  Live PostgreSQL 17 (`DATABASE_URL=postgresql+psycopg://nquiry:
    nquiry_local_dev_only@localhost:15432/nquiry`), full suite
    (`tests/ apps/api/tests apps/worker`): 1078 passed, 1 skipped (the
    one pre-existing, unrelated, disclosed skip). Zero failures, zero
    new skips, zero regressions against PKG-26's own 1061-passed
    baseline (+17 new tests).
  Real-process verification (independent of pytest): `python -m
    nquiry_worker` run directly -- exits 0, prints its own unchanged
    Phase-0 message, emits one real span; a real `fastapi.testclient.TestClient`
    call to `/healthz` -- returns `200 {"status": "ok", "phase": "0"}`
    unchanged, emits one real span. Both proven BEFORE any test file
    was written.

NEGATIVE_TEST_RESULTS: every rejection (wrong type, empty operation,
  over-length operation, unrecognized `boundary_result`/`failure_class`,
  an unexpected keyword for Evidence-shaped content) is a
  designed-before-implementation negative test asserting the real
  exception, never merely an error-text substring standing in for
  canonical/governance state (this package has no such state to
  assert against -- the exception ITSELF is the correct, exhaustive
  proof for a pure-validation type).

ADVERSARIAL_TEST_RESULTS:
  PRE_IMPLEMENTATION_ATTACK_MODEL category coverage: semantic-shortcut
  (3, below), authority/boundary-bypass (2, below -- "trace value used
  as authority" plus the MUT-PKG27-01 return-shape guard),
  persistence/concurrency (NOT_APPLICABLE -- this package has no
  persistence access at all, structurally, and no concurrent-write
  path of its own), Workspace (NOT_APPLICABLE -- `ObservationContext`
  carries no Workspace field at all; correlation is Workspace-agnostic
  by 11 section 37's own field list), AI-authority (1, below --
  "prompt content leakage"), failure/retry (NOT_APPLICABLE -- no
  retry/idempotency path in this package's own scope), projection/
  cache-truth (NOT_APPLICABLE -- no projection/cache concept here;
  11 section 36's own "telemetry presence does not prove domain
  legitimacy" is the closest analogue, covered under
  AUTHORITY_PATH instead).

  Mandatory (5/5, this package's own literal "Package-specific
  mandatory attacks" line):
  1. ATTACK: Secret in trace (via `boundary_result`)
     EXPECTED DEFENSE: fail-closed rejection of any value outside 06's
       own exact 4-value `BoundaryResult` vocabulary, mirrored locally
     EXPECTED BOUNDARY: NOT_APPLICABLE (structural type validation, not
       a runtime BND evaluation)
     EXPECTED CANONICAL RESULT: `ValueError` at construction; no
       `ObservationContext` instance is ever created to carry the
       secret
     EXPECTED PROOF ARTIFACT:
       `test_mandatory_attack_secret_in_trace_unknown_boundary_result_rejected`
     ACTUAL RESULT: matches
  2. ATTACK: Secret in trace (via `failure_class`)
     EXPECTED DEFENSE: fail-closed rejection of any value outside 10's
       own exact 19-value `FailureClass` vocabulary, mirrored locally
     EXPECTED BOUNDARY: NOT_APPLICABLE
     EXPECTED CANONICAL RESULT: `ValueError` at construction
     EXPECTED PROOF ARTIFACT:
       `test_mandatory_attack_secret_in_trace_unknown_failure_class_rejected`
     ACTUAL RESULT: matches
  3. ATTACK: full Evidence in log
     EXPECTED DEFENSE: no field exists to carry Evidence content at all
     EXPECTED BOUNDARY: NOT_APPLICABLE
     EXPECTED CANONICAL RESULT: `TypeError` for an unrecognized keyword
       -- the field never existed to reject a VALUE for
     EXPECTED PROOF ARTIFACT:
       `test_mandatory_attack_full_evidence_in_log_no_content_field_exists`
     ACTUAL RESULT: matches
  4. ATTACK: prompt content leakage
     EXPECTED DEFENSE: `operation`'s own length cap rejects
       prompt-scale content even though `operation` is otherwise a free
       string
     EXPECTED BOUNDARY: NOT_APPLICABLE
     EXPECTED CANONICAL RESULT: `ValueError` at construction
     EXPECTED PROOF ARTIFACT:
       `test_mandatory_attack_prompt_content_leakage_operation_length_capped`
     ACTUAL RESULT: matches
  5. ATTACK: trace value used as authority
     EXPECTED DEFENSE: no boundary evaluator or `AuthorityResolver` can
       even IMPORT `observability` -- proven against the real
       dependency-enforcement graph, not merely asserted in prose
     EXPECTED BOUNDARY: NOT_APPLICABLE (the proof IS the absence of any
       possible boundary consuming this package's own output)
     EXPECTED CANONICAL RESULT: `"observability" not in
       INTERNAL_ALLOWED["boundaries"|"authority"|"governance"]`
     EXPECTED PROOF ARTIFACT:
       `test_mandatory_attack_trace_value_used_as_authority_no_such_dependency_exists`
     ACTUAL RESULT: matches
  6. ATTACK: missing audit replaced by log
     EXPECTED DEFENSE: `observability` cannot reach `persistence`/any
       DB driver at all -- structurally, via the same dependency graph
       -- so nothing here could ever substitute for a real
       `AuditEvent`/`SecurityEvent` write
     EXPECTED BOUNDARY: NOT_APPLICABLE
     EXPECTED CANONICAL RESULT:
       `INTERNAL_ALLOWED["observability"] == {"semantic_types"}`
       exactly
     EXPECTED PROOF ARTIFACT:
       `test_mandatory_attack_missing_audit_replaced_by_log_no_persistence_access`
     ACTUAL RESULT: matches
     (6 mandatory attacks delivered against this package's own literal
     5-item list -- "Secret in trace" was tested against BOTH
     closed-vocabulary fields independently, since either is a
     genuinely distinct smuggling vector)

  Novel/adapted (>=5 required for this package; 10 delivered, 16
  total):
  7. ATTACK: `ObservationContext` gains an undisclosed field in a
       future edit, silently reintroducing "minimize content" risk
     ACTUAL RESULT: matches
       (test_observation_context_field_set_is_exactly_the_intended_minimum)
  8. ATTACK: `ObservationContext` is mutated after construction,
       letting a later step in the same request rewrite an earlier
       correlation fact
     ACTUAL RESULT: matches (test_observation_context_is_frozen)
  9. ATTACK: a bare `uuid.UUID` is accepted in place of a real strong ID
       type (`CorrelationId`/`CommandId`/etc.), collapsing this
       package's own type discipline
     ACTUAL RESULT: matches (test_rejects_wrong_correlation_id_type,
       test_rejects_wrong_optional_id_types)
  10. ATTACK: an empty `operation` string is accepted, producing an
        unidentifiable span
      ACTUAL RESULT: matches (test_rejects_empty_operation)
  11. ATTACK: `ObservationSink`'s own Protocol silently grows a second
        method that could return something authority-shaped
      ACTUAL RESULT: matches (test_observation_sink_protocol_returns_none)
  12. ATTACK: the real sink emits a span with the WRONG attributes, or
        omits ones it should have set
      ACTUAL RESULT: matches
        (test_local_otel_sink_emits_a_real_span_with_the_expected_attributes)
  13. ATTACK: an absent optional field is emitted as an empty-but-present
        attribute rather than genuinely omitted, misleading an
        investigator into believing it was resolved to nothing rather
        than never applying
      ACTUAL RESULT: matches
        (test_local_otel_sink_omits_absent_optional_attributes_entirely)
  14. ATTACK (MUT-PKG27-01): `emit` is changed to return something
        authority-shaped (a `bool`, a verdict object) in a future edit
      ACTUAL RESULT: matches
        (test_mut_pkg27_01_emitting_never_returns_anything_authority_shaped
        -- see MUTATION_TESTS)
  15. ATTACK: the sink crashes (or silently no-ops in a way that raises)
        when NO `opentelemetry.sdk` is installed/configured at all --
        proven in a genuinely fresh, separate process, not merely
        "this test file's own already-configured provider happens to
        work"
      ACTUAL RESULT: matches
        (test_local_otel_sink_is_safe_with_no_sdk_configured_in_a_fresh_process)
  16. ATTACK: every correlation-identity field is accepted with its own
        real strong type simultaneously, proving the "happy path" is
        genuinely reachable and not merely the rejection paths being
        exercised
      ACTUAL RESULT: matches
        (test_accepts_every_correlation_identity_field_with_the_real_strong_type)

MUTATION_TESTS:
  METHODOLOGY NOTE (same disclosed adaptation as PKG-24/25/26): this
  session's own auto-mode tool classifier denies temporarily weakening
  a real security-relevant control in place, even reverted immediately
  afterward.

  MUT-PKG27-01: does `LocalOtelObservationSink.emit` (and the
    `ObservationSink` Protocol it implements) genuinely return nothing
    a caller could mistake for an authority verdict, or could a future
    edit quietly start returning e.g. a boundary-shaped value? Called
    directly and its return value inspected -> expected: `None`.
    ACTUAL: confirmed
    (test_mut_pkg27_01_emitting_never_returns_anything_authority_shaped).
    INTERPRETATION: the AUTHORITY line ("Never consumed as authority
    proof") is enforced by the real return type today, not merely by
    convention -- a future edit widening the return type would need to
    consciously change this Protocol's own signature, which
    `test_observation_sink_protocol_returns_none`'s own structural
    method-set assertion would also have to be updated to permit,
    making an accidental widening visibly deliberate rather than
    silent.
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TEST_RESULTS: this package's own two real "instrumentation
  integration" call sites were exercised directly, end to end, against
  the REAL running processes, before any dedicated test file existed:
  `python -m nquiry_worker` (the real worker entrypoint) -- exits 0,
  unchanged Phase-0 message, one real span emitted; a real
  `fastapi.testclient.TestClient` request to the real `/healthz` route
  on the real `nquiry_api.main.app` FastAPI instance -- returns the
  unchanged `200 {"status": "ok", "phase": "0"}` body, one real span
  emitted. No mock FastAPI app, no mock worker process, no simulated
  span anywhere in either integration point.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through
  PKG-26's tests) re-run alongside PKG-27's new tests, both without a
  live database (694 passed, 384 skipped, `tests/` only) and against a
  real PostgreSQL 17 instance with all 19 migrations applied (unchanged
  -- this package creates none) (`tests/ apps/api/tests apps/worker`:
  1078 passed, 1 skipped). Zero regressions; every previously-green
  test remains green, including `apps/api/tests/test_health.py`'s own
  pre-existing `/healthz` assertion (still exactly `200 {"status": "ok",
  "phase": "0"}` despite the new instrumentation inside that same
  route handler).

P_CLAIMS_TESTED:
  P-25 (complete occurrence reconstructable): substantially exercised
    for the first time via a real, structured correlation type
    spanning every identity 11 section 37 itself names as required for
    reconstructing "a single governed operation... across API edge,
    Command processing, governance evaluation, boundaries, CommitUnit,
    outbox, AI Gateway, tool invocation and recovery" -- PKG-21's own
    `BoundaryProof.evidence_proof_refs` was this codebase's own first,
    narrower P-25 exercise (PKG-17); this package is the first to
    materialize the FULL, named correlation-identity SET as one
    reusable type. Full closure (every real Command/Boundary/CommitUnit
    call site actually constructing and emitting a fully-populated
    `ObservationContext`) remains `SUCCESSOR_NOT_BUILT` -- neither
    `apps/api` nor `apps/worker` has a real Command/Query/Boundary
    dispatch pipeline yet (both remain literal Phase-0 skeletons; see
    KNOWN_LIMITATIONS), so no call site in this codebase currently HAS
    a `command_id`/`commit_id`/`boundary_result` to populate beyond the
    two minimal, real, disclosed integration points this package adds.

PROOF_ARTIFACTS:
  - 1078-test live-database pass (0 regressions against PKG-26's own
    1061-passed baseline), including 16 distinct adversarial proofs (6
    mandatory + 10 novel/adapted) and 1 guard-necessity mutation proof
  - A real `opentelemetry.sdk` `InMemorySpanExporter` capture proving
    an actual emitted span's own exact attribute set, both the
    fully-populated and minimal-population cases
  - A real, separate, freshly-spawned Python process (no
    `opentelemetry.sdk` imported at all) proving the sink is safe with
    zero SDK configuration
  - A real `python -m nquiry_worker` process run and a real
    `TestClient` HTTP call to `/healthz`, both proving the two new
    "app/worker instrumentation integration" call sites work end to
    end, unchanged in their own pre-existing observable behavior
  - A live, structural proof against the real
    `check_architecture_dependencies.py` dependency graph that no
    boundary/authority/governance/persistence path can ever reach
    `observability`
  - Architecture dependency/provider-SDK/test-only-import checker PASS
    output; `verify_migrations.py` confirmed unchanged at head
    `047bdf9bc528` (no migration created)
  - Diff audit (inline answers below), cross-checked against `git
    status --short` before staging per this session's own standing
    instruction

FORBIDDEN_DEPENDENCY_CHECK: PASS (two new, disclosed, cited extensions:
  `nquiry_api -> observability` and `nquiry_worker -> observability`,
  22nd/23rd overall; both one-directional -- `observability`'s own
  allowed set, 14 section 3.1: "semantic_types", does not include
  `nquiry_api`/`nquiry_worker`, so no cycle is created)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT:
  New semantic type/enum value: none new that isn't a direct,
    disclosed MIRROR of an already-closed vocabulary (`_KNOWN_BOUNDARY_RESULTS`/
    `_KNOWN_FAILURE_CLASSES` reproduce 06/10's own exact closed lists
    literally, as plain strings, since `observability` cannot import
    `boundaries`/`recovery` -- transcribed, not invented, the same
    "closed vocabulary enforced elsewhere, mirrored as inert string
    here" pattern `audit.models.AuditEvent.result` already established).
  New transition: none -- no state machine anywhere in this package's
    own scope.
  New authority path: none -- see AUTHORITY_PATH above; this package's
    entire OBJECTIVE requires proving the STRUCTURAL absence of any
    authority path through observability, the identical shape PKG-25/26
    each proved for the DB-principal/RLS layers.
  New DB write path: none. `observability` cannot reach `persistence`
    or any DB driver at all (unchanged, code-grounded via the
    dependency graph, see FILES_MODIFIED's own
    `EXTERNAL_FORBIDDEN`/`INTERNAL_ALLOWED` entries).
  Weakened boundary: none -- no BND-001..018 evaluator touched, and no
    existing grant/policy from PKG-25/26 was altered.
  Easier test / removed negative test / admin shortcut / projection or
    cache truth / AI canonical authority / broader Workspace scope:
    none.
  Changed migration semantics: NOT_APPLICABLE -- no migration exists
    for this package.
  New external dependency, disclosed: `opentelemetry-sdk` added to
    `[project.optional-dependencies].dev` in `pyproject.toml` --
    DEV-ONLY (test-time), never a runtime dependency (production code
    in `packages/observability/context.py` calls only
    `opentelemetry.trace`'s own API surface, the ALREADY-declared
    `opentelemetry-api` runtime dependency from PKG-00's own skeleton).
    Judged directly required by this package: without it,
    `tests/security/test_observability.py` could only prove "the sink
    does not raise", never that a real span/attribute was genuinely
    recorded -- the identical justification `pytest-cov`/`hypothesis`
    already received as dev-only additions to the same
    `[project.optional-dependencies].dev` list at earlier, unrecorded
    points in this repository's own history.
  Forbidden dependency: two new, disclosed, cited extensions --
    `nquiry_api -> observability`, `nquiry_worker -> observability`
    (22nd/23rd overall, see FORBIDDEN_DEPENDENCY_CHECK). Also disclosed:
    `EXTERNAL_FORBIDDEN["observability"]` is a NEW entry that
    deliberately PERMITS `opentelemetry` (every other entry in that
    table forbids at least the provider-SDK group; this is the first,
    and only intended, package-specific carve-out for a DIFFERENT
    external SDK group, mirroring `ai_gateway/adapters/providers/`'s
    own existing provider-SDK carve-out).
  Files touched outside this package's own new-file set:
    `packages/observability/__init__.py`, `apps/api/src/nquiry_api/main.py`,
    `apps/worker/src/nquiry_worker/__main__.py`, `pyproject.toml`,
    `scripts/check_architecture_dependencies.py` -- all five explicitly
    the disclosed extension points this package's own "app/worker
    instrumentation integration" target requires; no other predecessor
    file touched. `apps/api/tests/test_health.py`'s own pre-existing
    assertion required no change (the route's own observable response
    body is byte-for-byte unchanged). No production bug was found this
    package -- every new test passed on its first run.
  `git status --short` immediately before staging matched this section
    exactly: 5 modified files
    (`apps/api/src/nquiry_api/main.py`,
    `apps/worker/src/nquiry_worker/__main__.py`,
    `packages/observability/__init__.py`, `pyproject.toml`,
    `scripts/check_architecture_dependencies.py`) plus 2 new files
    (`packages/observability/context.py`,
    `tests/security/test_observability.py`), nothing else, no tooling/
    lock files.

ARCHITECTURE_RECONSTRUCTION_RESULT:
  This package participates in NO single consequential request path of
  its own -- 14 assigns it no Command, Query, or Boundary; its own
  ARCHITECTURAL_INVARIANTS line states it directly: "OBSERVABILITY !=
  AUDIT; TRACE != AUTHORITY; TELEMETRY != TRUTH." Its own longest
  legitimate chain is diagnostic and PARALLEL to every real
  consequential chain, never part of one: REQUEST -> ACTOR -> WORKSPACE
  -> CURRENT STATE -> CURRENT GOVERNANCE -> CURRENT AUTHORITY -> HUMAN
  DECISION -> EVIDENCE -> BOUNDARIES -> BND-014 -> COMMAND -> COMMIT
  UNIT -> CANONICAL MUTATION -> AUDIT -> OUTBOX -> EVENT -> RESULTING
  STATE: every one of these nodes is `NOT_APPLICABLE` for THIS
  package's own direct scope (it reconstructs technical behavior AFTER
  the fact, from whichever of these nodes a caller chooses to name via
  `ObservationContext`'s own optional fields -- it never sits ON this
  chain, never gates it, never follows it in real time). The one real
  chain this package DOES complete, twice: REAL PROCESS EVENT (an
  incoming `/healthz` request; a worker process starting up) ->
  `ObservationContext` construction (correlation_id freshly generated,
  `operation` naming the event, every other field `None` -- there IS no
  richer upstream node to name yet) -> `LocalOtelObservationSink.emit`
  -> a real, locally-captured OpenTelemetry span. Populating the richer
  optional fields (`command_id`/`commit_id`/`boundary_result`/
  `failure_class`) for a REAL governed operation remains
  `SUCCESSOR_NOT_BUILT`, disclosed: no Command/Query/Boundary dispatch
  pipeline exists anywhere in `apps/api`/`apps/worker` yet for such an
  operation to occur through in the first place (see
  KNOWN_LIMITATIONS).

KNOWN_LIMITATIONS:
  - Neither `apps/api` nor `apps/worker` has a real Command/Query/
    Boundary dispatch pipeline yet -- both remain, even after PKG-26,
    literal Phase-0 skeletons (`apps/api/src/nquiry_api/main.py`'s own
    docstring: "toolchain boot proof only... must not gain a Command or
    Query route until `http/commands.py`/`queries.py` exist";
    `apps/worker/src/nquiry_worker/__main__.py`'s own docstring:
    "Phase 0 skeleton -- no workers implemented yet"). This package's
    own two real instrumentation call sites are therefore necessarily
    minimal (`operation` name + fresh `correlation_id` only) -- a
    richly-populated `ObservationContext` describing an actual governed
    operation remains `SUCCESSOR_NOT_BUILT`, disclosed, not fabricated
    by inventing a fake pipeline to instrument.
  - `outbox_worker.py`/`projection_worker.py` (PKG-20/21's own real
    worker logic) are NOT instrumented -- they are proven only through
    their own dedicated tests and are never actually invoked by
    `apps/worker/src/nquiry_worker/__main__.py` at all (that entrypoint
    still calls neither, unchanged since PKG-20). Instrumenting them
    would require wiring them into a real entrypoint first, which is
    outside this package's own narrow scope.
  - `opentelemetry-sdk`/any real exporter (OTLP, Jaeger, etc.) is a
    dev-only test dependency here, never configured for a real
    deployment -- an actual local development span exporter (e.g. a
    console exporter wired into `apps/api`/`apps/worker` at process
    startup) remains a disclosed, deliberate `SUCCESSOR_NOT_BUILT`; this
    package proves the API-level mechanism is safe and correct with or
    without one configured, matching 14's own "local OpenTelemetry API
    sink" (API, not SDK) framing literally.
  - Sandbox Python remains 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still
  BLOCKED. Neither is touched by this package's own scope.

NEW_GAPS_DISCOVERED:
  1. Neither `apps/api` nor `apps/worker` has a real Command/Query/
     Boundary dispatch pipeline as of PKG-27 (see KNOWN_LIMITATIONS) --
     not a new discovery this package caused, but the first package
     whose own OBJECTIVE ("app/worker instrumentation integration")
     made this pre-existing gap directly, concretely visible rather
     than an abstract, disclosed Phase-0 note.
  2. `apps/worker/__main__.py` still never invokes
     `outbox_worker.py`/`projection_worker.py` (disclosed, unchanged
     since PKG-20/21) -- newly relevant here since this package's own
     worker-side instrumentation could otherwise have been mistaken for
     covering those real workers too; it does not.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. `ObservationContext`'s
  own field list is 11 section 37's own exact correlation-identity list
  plus 14's own PKG-27 OBJECTIVE-line additions, transcribed verbatim.
  `_KNOWN_BOUNDARY_RESULTS`/`_KNOWN_FAILURE_CLASSES` mirror 06/10's own
  already-closed vocabularies exactly, never inventing a new one. No
  new Decision Right, authority class, Command, Query, Event, Boundary,
  or canonical write PATH was introduced. The two real instrumentation
  call sites emit ONLY a fresh `correlation_id` and a literal operation
  name -- no fabricated Command/Boundary/CommitUnit content was
  invented to make the integration look more complete than the
  underlying `apps/api`/`apps/worker` pipelines actually are.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-28 becomes DAG-eligible once its own
  required predecessors are verified. Eligibility is not authorization.
HUMAN_GATE_REQUIRED: YES -- 14 PKG-27's own coding prompt: "Respect the
  phase boundary. Package completion does not authorize the next
  phase." This package also completes Build Phase 10 (PKG-25/26/27, the
  last package in Phase 10) -- do not authorize PKG-28 (first package
  of Phase 11) without explicit human authorization naming the package
  and this package's own commit hash.
```
