# 14_IMPLEMENTATION_SEQUENCE.md

## DOCUMENT STATUS

`[SPECIFIED]` Implementation Architecture and Implementation Sequence derived from approved architecture 00 through 13.

`HUMAN_REVIEW_STATUS::DRAFT_FOR_REVIEW`

This file is authoritative only for implementation architecture, physical mapping, dependency direction, implementation sequencing, package decomposition, and implementation proof gates.

It does not authorize application implementation.

It does not close unresolved upstream authority, provider, privacy, Evidence, recovery, export, or bootstrap semantics.

---

## 0. SOURCE AUTHORITY AND IMPLEMENTATION LAW

Strict source hierarchy:

`LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14`

Implementation law:

`IMPLEMENTATION MUST MATERIALIZE ARCHITECTURE.`

`IMPLEMENTATION MUST NOT COMPLETE ARCHITECTURE BY GUESSING.`

Non-collapse invariants:

- `CODE != AUTHORITY`
- `DATABASE SCHEMA != DOMAIN SEMANTICS`
- `FRAMEWORK CAPABILITY != SYSTEM PERMISSION`
- `LIBRARY FEATURE != APPROVED BEHAVIOR`
- `ORM RELATION != DOMAIN RELATION`
- `HTTP ENDPOINT != COMMAND AUTHORITY`
- `SERVICE METHOD != AUTHORITY`
- `DATABASE TRANSACTION != LEGITIMATE TRANSITION`
- `ADMIN API != GOVERNANCE AUTHORITY`
- `MODEL SDK != AI ARCHITECTURE`
- `BACKGROUND JOB != SYSTEM_DERIVED AUTHORITY`
- `TEST SEED != LEGITIMATE BOOTSTRAP`
- `CONFIGURATION != GOVERNANCE`
- `CACHE != CANONICAL STATE`
- `EXCEPTION != FAILURE SEMANTICS`
- `RETRY LIBRARY != RETRY AUTHORITY`
- `LOGGING != AUDIT`

Hard dependencies preserved from 12 and 13:

1. `HARD-DEP-001`: legitimate first Workspace governance-root bootstrap.
2. `HARD-DEP-002`: provider/privacy eligibility for the exact prototype data class and selected provider path.

Neither dependency is closed in 14.

Implementation paths requiring either dependency return `BLOCKED_BY_UPSTREAM_GAP`.

Export Authority remains unresolved and operational export is not implemented.

Architecture Baseline is not frozen.

---

## 1. IMPLEMENTATION TARGET

`[SPECIFIED]` Target: the Minimum Closed Architectural Prototype defined by 12, with falsification architecture defined by 13.

The target is an architectural proof, not the complete product and not a production-readiness claim.

Included capabilities:

- authenticated human identity mapping
- two isolated Workspaces for architectural tests
- Workspace membership
- executable governance bindings
- explicit HumanAuthorityBinding lifecycle
- Challenge
- Session
- Human-only Question Burst
- verbatim Question capture
- frozen human raw Question membership
- post-Burst AI analysis through AI Gateway
- AI derived artifact persistence
- human QuestionSelection
- Decision `UNDER_CONSIDERATION -> DECIDED`
- minimum Evidence, SourceReference, ClaimAnchor, EvidenceRelation and Evidence consumption path
- governed Command processing
- current authority resolution
- explicit boundary evaluation
- BND-014 fresh commit revalidation
- transactional CommitUnit
- AuditEvent
- transactional outbox
- EventEnvelope
- rebuildable projection
- idempotency
- four approved transition outcomes
- consequence certainty resolution
- INDETERMINATE blocking
- RecoveryRecord
- BND-017 and BND-018
- AI Gateway
- service identity
- Workspace isolation
- canonical-write privilege separation
- SecurityEvent
- structured observability correlation
- architectural test harness and mutation harness

Explicitly not implemented in the prototype:

- legitimate production first-Workspace governance-root bootstrap, blocked by `HARD-DEP-001`
- real provider data execution until `HARD-DEP-002` is closed
- operational export consequence
- full Research Mode
- production multi-provider routing
- production collaboration breadth
- complete methodology catalogue
- automatic Burst timer completion
- unresolved global Evidence sufficiency semantics
- full retention/deletion automation
- production incident-response automation
- production deployment certification
- regulatory or privacy approval claims

`MINIMUM != WEAKENED`.

`PROTOTYPE EXECUTION != PROTOTYPE EXCEPTION`.

---

## 2. TECHNOLOGY DECISION POLICY AND REFERENCE STACK

Technical requirements are derived first:

1. one transactional authority for canonical mutation, governance mutation, AuditEvent, outbox, CommitUnit and idempotency state
2. explicit optimistic concurrency
3. strong schema constraints and Workspace-key integrity
4. typed contracts at HTTP, Command, Event, AI and configuration boundaries
5. static dependency enforcement
6. deterministic test hooks for commit, concurrency, AI and recovery
7. one-process deployment allowed while semantic boundaries remain enforceable
8. provider SDK isolation
9. testable DB principal separation
10. no infrastructure whose complexity is itself mistaken for architectural proof

### 2.1 Reference stack

| Concern | Reference choice | Status | Architectural reason |
|---|---|---|---|
| Backend language/runtime | Python 3.13 | `[IMPLEMENTATION CHOICE]` | Mature typing, testing and FastAPI ecosystem, compact prototype implementation |
| Web framework | FastAPI | `[IMPLEMENTATION CHOICE]` | Explicit request contracts and dependency injection without defining domain semantics |
| Domain/application typing | Python dataclasses plus Pydantic v2 boundary models | `[IMPLEMENTATION CHOICE]` | Separate internal semantic types from external validation contracts |
| Database | PostgreSQL 17 | `[IMPLEMENTATION CHOICE]` | ACID transaction for CommitUnit, row locking, constraints, RLS, advisory/test primitives |
| Migration system | Alembic | `[IMPLEMENTATION CHOICE]` | Ordered, reviewable schema evolution |
| Query/persistence layer | SQLAlchemy 2.x Core plus explicit repositories | `[IMPLEMENTATION CHOICE]` | Avoid generic ORM entity mutation and preserve transaction visibility |
| Authentication adapter | pluggable OIDC adapter plus deterministic test adapter | `[IMPLEMENTATION CHOICE]` | Establish identity without embedding domain authority in tokens |
| Frontend | Next.js 16 with TypeScript | `[IMPLEMENTATION CHOICE]` | Minimal server-backed prototype UI, typed contracts, no authority calculation |
| Backend tests | pytest | `[IMPLEMENTATION CHOICE]` | Deterministic fixtures and failure injection |
| Property testing | Hypothesis where invariant spaces benefit | `[IMPLEMENTATION CHOICE]` | Negative and mutation-oriented semantic testing |
| Frontend tests | Vitest plus Playwright for architectural E2E | `[IMPLEMENTATION CHOICE]` | UI contract plus browser proof paths |
| AI abstraction | internal AI Gateway ports, MockProviderAdapter default | `[IMPLEMENTATION CHOICE]` | 08 non-bypass and unresolved provider eligibility |
| Observability | OpenTelemetry API with local structured sink | `[IMPLEMENTATION CHOICE]` | Correlation without vendor dependence |
| Local development | Docker Compose for PostgreSQL, backend, worker, frontend | `[IMPLEMENTATION CHOICE]` | Reproducible proof environment |
| CI | GitHub Actions reference workflow | `[IMPLEMENTATION CHOICE]` | Ordered structural and falsification gates |

PostgreSQL materializes transaction atomicity, version checks, constraints, RLS defense-in-depth, append-oriented privileges and durable outbox storage. PostgreSQL does not decide authority, Evidence sufficiency, legal transitions, human decisions, recovery legitimacy, or epistemic truth.

Changing the stack is permitted if the replacement preserves every mapped semantic and proof property. Stack substitution is an implementation change, not semantic authority.

---

## 3. REPOSITORY TOPOLOGY

```text
/
  README.md
  pyproject.toml
  package.json
  docker-compose.yml
  architecture/
    00_NQUIRY_MASTER_ARCHITECTURE.md
    ...
    14_IMPLEMENTATION_SEQUENCE.md
  docs/
    implementation/
      package-status/
      proof-reports/
  apps/
    api/
      src/nquiry_api/
        main.py
        http/
        auth/
        dispatch/
      tests/
    web/
      app/
      components/
      lib/
      tests/
    worker/
      src/nquiry_worker/
        outbox_worker.py
        projection_worker.py
        recovery_worker.py
  packages/
    semantic_types/
    domain/
    governance/
    authority/
    boundaries/
    evidence/
    ai_contracts/
    ai_gateway/
    command/
    commit/
    audit/
    events/
    projection/
    recovery/
    security/
    observability/
    application/
    persistence/
    test_support/
  migrations/
    versions/
  tests/
    semantic/
    domain/
    transitions/
    authority/
    governance/
    boundaries/
    evidence/
    ai/
    command_commit_event/
    recovery/
    security/
    e2e/
    mutation/
    regression/
    proof/
  scripts/
    check_architecture_dependencies.py
    check_provider_sdk_imports.py
    check_test_only_imports.py
    verify_migrations.py
  config/
    schema/
    prompts/
    aiop/
    boundaries/
  infra/
    local/
    ci/
```

No generic `utils/`, `helpers/`, `services/`, or `common/` package is permitted as a semantic dumping ground.

### 3.1 Directory ownership contract

| Package | Responsibility | May depend on | Must not depend on | Canonical write |
|---|---|---|---|---|
| semantic_types | IDs, versions, closed semantic primitives | stdlib | HTTP, DB, AI SDK | no |
| domain | Things, Relations, state specs, invariants | semantic_types | infrastructure, HTTP, AI SDK | no |
| governance | governance state and mutation plans | domain, semantic_types | UI, provider SDK | only through CommitUnit |
| authority | current authority resolution | governance, domain | UI roles, AI, projection | no |
| boundaries | BND-001 through BND-018 evaluators | domain, authority, governance, evidence contracts | controllers, provider SDK | no |
| evidence | Evidence and provenance semantics | domain, semantic_types | AI provider, UI | only through CommitUnit |
| ai_contracts | AIOP and AI contract types | semantic_types, evidence read contracts | provider SDK | no |
| ai_gateway | context, prompt, provider adapter, validation | ai_contracts, security, operational persistence | canonical writer | derived operational writes only |
| command | CommandEnvelope, registry, handler contracts | domain contracts, semantic_types | HTTP, provider SDK | no direct write |
| commit | BND-014, transaction orchestration, mutation application | command, boundaries, persistence ports, audit, events | frontend, provider SDK | exclusive governed writer |
| audit | AuditEvent contracts and append port | semantic_types | domain mutation | append only |
| events | EventEnvelope and outbox contracts | semantic_types | command mutation internals | outbox only |
| projection | read models and rebuild | events, projection persistence | canonical writer, authority resolver as source | projection only |
| recovery | 10 recovery orchestration | command, boundaries, commit, recovery ports | unrestricted DB writer | only governed Recovery Command |
| security | identity/service identity, Workspace security, SecurityEvent | semantic_types | domain authority invention | no domain write |
| observability | correlation and diagnostic telemetry | semantic_types | canonical mutation | no |
| application | use-case orchestration and Query/Command dispatch | public ports above | ORM mutation, provider SDK | no direct write |
| persistence | PostgreSQL adapters implementing typed ports | semantic contracts | UI semantics | capability limited by DB principal |
| test_support | deterministic fixtures, clocks, hooks | public contracts | production importers | test only |

---

## 4. DEPENDENCY DIRECTION AND FORBIDDEN DEPENDENCIES

Allowed high-level graph:

```text
INTERFACE
  -> APPLICATION
      -> COMMAND
      -> QUERY PORTS
      -> AI GATEWAY PORT
      -> RECOVERY PORT

COMMAND
  -> DOMAIN
  -> GOVERNANCE
  -> AUTHORITY
  -> BOUNDARIES
  -> EVIDENCE CONTRACTS
  -> COMMIT

COMMIT
  -> PERSISTENCE PORTS
  -> AUDIT
  -> OUTBOX

AI GATEWAY
  -> AI CONTRACTS
  -> PROVIDER ADAPTER
  -> OPERATIONAL AI RECORD PORT

EVENT WORKER
  -> EVENT
  -> PROJECTION

RECOVERY
  -> COMMAND
  -> BND-017/BND-018
  -> COMMIT

INFRASTRUCTURE ADAPTERS
  -> IMPLEMENT PORTS
```

Forbidden dependency matrix:

| From | Forbidden dependency |
|---|---|
| domain | FastAPI, SQLAlchemy, PostgreSQL driver, Next.js, provider SDK, OpenTelemetry vendor |
| authority | UI role claims, projection as authoritative source, AI output |
| boundaries | controller state, cache ALLOW, frontend capabilities |
| ai_gateway | canonical repository writer, HumanAuthorityBinding mutation |
| provider adapter | CommandProcessor, CommitWriter, DecisionRepository write |
| projection | canonical mutation port, governance mutation port |
| event consumer | internal handler that bypasses CommandEnvelope |
| recovery | unrestricted repository mutation, original actor authority reuse |
| controller | ORM session mutation, provider SDK, direct CommitUnit internals |
| frontend | DB, governance repository, authority resolver |
| observability | canonical writer, governance writer |
| test-only bootstrap | any production package |
| migration code | runtime authority resolver |

Automated architecture tests fail CI on forbidden imports.

---

## 5. SEMANTIC TYPE SYSTEM

Strong code-level identities:

`WorkspaceId`, `UserId`, `ServiceIdentityId`, `ThingId`, `RelationId`, `ChallengeId`, `SessionId`, `BurstId`, `QuestionId`, `QuestionSelectionId`, `DecisionId`, `EvidenceId`, `SourceReferenceId`, `ClaimAnchorId`, `EvidenceRelationId`, `EvidenceSetId`, `CommandId`, `AttemptId`, `CommitId`, `EventId`, `GenerationId`, `RecoveryId`, `CorrelationId`, `CausationId`, `AuthorityBindingId`, `FacilitatorScopeBindingId`, `AuditEventId`, `SecurityEventId`, `RecordVersion`, `ContractVersion`, `PromptVersion`, `MethodVersion`.

`[IMPLEMENTATION CHOICE]`: use frozen wrapper value objects around UUIDv7-compatible values. Tests may use deterministic generators. IDs carry no authority and no semantic state.

Consequential payloads use versioned typed contracts. Raw dictionaries are rejected at public consequential boundaries.

---

## 6. CLOSED VOCABULARIES

Prototype code materializes only approved values.

### Session
`DRAFT`, `SETUP`, `CHALLENGE_CAPTURE`, `QUESTION_GENERATION`, `QUESTION_CAPTURE`, `ANALYSIS`, `REFLECTION`, `QUESTION_SELECTION`, `INVESTIGATION`, `EXPERIMENT`, `ACTION`, `REVIEW`, `CLOSED`

Only prototype-exercised transitions are enabled. Unused states remain declared where required to reject illegal skips.

### QuestionBurst
`PREPARED`, `ACTIVE`, `PAUSED`, `COMPLETED`

### Decision
`UNDER_CONSIDERATION`, `DECIDED`

### AIGeneration
`REQUESTED`, `RUNNING`, `OUTPUT_RECEIVED`, `VALIDATED`, `REJECTED`, `FAILED`

### Command outcome
`DENIED`, `FAILED_PRECOMMIT`, `COMMITTED`, `INDETERMINATE`

### Boundary result
`ALLOW`, `DENY`, `REQUIRE`, `ESCALATE`

### Evidence validation
`UNVALIDATED`, `STRUCTURALLY_VALID`, `INVALIDATED`, `UNAVAILABLE`

### EvidenceRelation assessment
`UNASSESSED`, `SUPPORTS`, `CONTRADICTS`, `CONTEXTUAL`, `DOES_NOT_SUPPORT`

### Recovery certainty
`PROVEN_COMMITTED`, `PROVEN_NOT_COMMITTED`, `EXTERNAL_CONSEQUENCE_PROVEN`, `EXTERNAL_CONSEQUENCE_PROVEN_ABSENT`, `EXTERNAL_CONSEQUENCE_UNKNOWN`, `CANONICAL_STATE_UNKNOWN`, `GOVERNANCE_STATE_UNKNOWN`

### RecoveryRecord outcome
`RECOVERED`, `RECONCILED`, `COMPENSATED`, `NO_ACTION_REQUIRED`, `UNRESOLVED`

Unknown consequential enum values fail closed.

---

## 7. DATABASE ARCHITECTURE

`[IMPLEMENTATION CHOICE]`: one PostgreSQL database for the prototype, with schemas and DB privileges preserving semantic separation. Physical co-location does not collapse semantic classes.

### 7.1 Core tables

| Table | Semantic class | Workspace key | Version | Write owner |
|---|---|---:|---:|---|
| users | canonical identity reference | no | record_version | governed_commit_writer for mapped user state |
| workspaces | canonical | yes, self | record_version | governed_commit_writer |
| workspace_memberships | relation/governance | yes | record_version | governed_commit_writer |
| human_authority_bindings | governance | yes | record_version | governed_commit_writer |
| facilitator_scope_bindings | governance relation | yes | record_version | governed_commit_writer |
| challenges | canonical | yes | record_version | governed_commit_writer |
| sessions | canonical | yes | record_version | governed_commit_writer |
| question_bursts | canonical | yes | record_version | governed_commit_writer |
| questions | canonical | yes | record_version | governed_commit_writer |
| question_lineage | relation | yes | immutable | governed_commit_writer |
| burst_question_memberships | relation | yes | immutable after freeze | governed_commit_writer |
| question_selections | authority-bearing relation | yes | record_version | governed_commit_writer |
| decisions | canonical | yes | record_version | governed_commit_writer |
| source_references | canonical support record | yes | record_version | governed_commit_writer |
| evidence | canonical | yes | record_version | governed_commit_writer |
| claim_anchors | semantic target reference | yes | version | governed_commit_writer |
| evidence_relations | relation | yes | record_version | governed_commit_writer |
| evidence_set_memberships | consumption relation | yes | immutable per set version | governed_commit_writer |
| ai_generations | operational record | yes | lifecycle version | ai_gateway_writer |
| ai_context_manifests | operational immutable context | yes | immutable | ai_gateway_writer |
| ai_derived_artifacts | derived | yes | record_version | ai_gateway_writer through bounded derived port |
| commands | operational | yes | contract version | command_processor |
| command_attempts | operational | yes | attempt identity | command_processor |
| idempotency_records | operational control | yes | state version | commit writer |
| commit_units | operational proof | yes | immutable after result | commit writer |
| audit_events | audit | yes | append only | commit writer |
| outbox_events | operational/event | yes | delivery version | commit writer, then outbox worker delivery fields only |
| projection_checkpoints | projection | yes | checkpoint version | projection_writer |
| session_read_model | projection | yes | projection version | projection_writer |
| inquiry_read_model | projection | yes | projection version | projection_writer |
| recovery_records | operational recovery | yes | record_version | recovery orchestration through governed path |
| security_events | security operational | yes where resolvable | append oriented | security_event_writer |

### 7.2 Required column pattern

Protected mutable canonical tables include:

`id`, `workspace_id`, `record_version`, `created_at`, and `updated_at` only where mutable history semantics permit it.

Immutable history tables use `created_at` and no semantic `updated_at`.

Consequential relations include endpoint IDs plus `workspace_id` and composite constraints ensuring same-Workspace endpoints.

### 7.3 Critical field constraints

- `questions.original_text` is non-null and has no repository update operation.
- `questions.origin` and lineage fields cannot be rewritten to convert AI to human origin.
- `human_authority_bindings` preserve grant and revocation history.
- `audit_events` have no normal update/delete privilege.
- `outbox_events.event_id` is unique.
- `commands.command_id` unique.
- idempotency uniqueness includes Workspace, command type and idempotency key.
- payload fingerprint mismatch under same idempotency identity is rejected.
- all protected foreign relations include Workspace-compatible constraints or application plus trigger/constraint enforcement where SQL cannot express a cross-table invariant directly.

Database constraints are defense-in-depth. They do not decide current authority.

---

## 8. DATABASE PRINCIPALS AND WORKSPACE ISOLATION

Reference principals:

| Principal | Reads | Writes | Forbidden |
|---|---|---|---|
| `migration_owner` | all schema | DDL/migration | runtime use |
| `api_reader` | approved canonical/projection views | none canonical | canonical mutation |
| `governed_commit_writer` | authoritative canonical/governance/Evidence | approved canonical, audit, outbox, commit, idempotency | arbitrary audit update/delete |
| `ai_gateway_writer` | approved context source views | AI operational and derived artifact tables only | Decision, HABB, QuestionSelection, canonical transition tables |
| `projection_writer` | outbox/Event source | projection only | canonical/governance/Evidence writes |
| `recovery_reader` | recovery reconstruction inputs | RecoveryRecord staging where non-consequential, otherwise via governed writer | direct canonical repair |
| `security_event_writer` | minimal security refs | security_events | domain state |
| `audit_reader` | audit | none | mutation |
| `test_principal` | test-scoped | only test database | production access |

`[IMPLEMENTATION CHOICE]`: PostgreSQL RLS is enabled for Workspace-keyed protected tables using transaction-local Workspace context set only by trusted server adapter. RLS is defense-in-depth and is never used as the authority oracle.

Unknown or conflicting Workspace scope fails before repository access and is also rejected by RLS.

---

## 9. MIGRATION PLAN

| Migration | Creates | Depends on | Gate |
|---|---|---|---|
| 001_semantic_identity_workspace | users, workspaces | none | type/schema tests |
| 002_membership_governance | memberships, HABB, facilitator scope | 001 | cross-Workspace and history tests |
| 003_challenge_session | challenges, sessions | 001,002 | transition constraints |
| 004_burst_question | bursts, questions, lineage, memberships | 003 | immutability/freeze tests |
| 005_selection_decision | selections, decisions | 004,002 | authority relation tests |
| 006_evidence_provenance | source refs, evidence, anchors, relations, sets | 001 | version/scope tests |
| 007_ai_operational | generations, manifests, derived artifacts | 004,006 | AI provenance tests |
| 008_command_attempt_idempotency | commands, attempts, idempotency | 001 | identity/retry tests |
| 009_commit_audit_outbox | commit_units, audit_events, outbox_events | 008 | atomicity/failure injection |
| 010_projection | read models, checkpoints | 009 | rebuild tests |
| 011_recovery | recovery_records | 009 | 10 semantics tests |
| 012_security_events_rls | security_events, RLS/policies/grants | prior protected tables | isolation/privilege tests |

Schema migration rollback is infrastructure rollback only. It is not domain rollback.

---

## 10. REPOSITORY PORTS

Repositories are semantic ports, not generic `Repository<T>`.

Each protected repository requires explicit Workspace scope.

- `WorkspaceRepository`: authoritative Workspace reads, governed mutation plan only.
- `MembershipRepository`: current and historical membership reads, governed mutation plan.
- `AuthorityBindingRepository`: current/historical HABB reads, no direct grant/revoke outside governance Command.
- `ChallengeRepository`: canonical read and mutation-plan application inside CommitUnit.
- `SessionRepository`: canonical current version, state mutation only through transition plan.
- `BurstRepository`: canonical Burst state and frozen membership.
- `QuestionRepository`: create/read, no original-text update.
- `QuestionSelectionRepository`: authority-bearing relation read/write only through governed selection Command.
- `DecisionRepository`: read and governed human Decision mutation.
- `EvidenceRepository`: authoritative versioned Evidence and relation reads, governed writes.
- `AIRecordRepository`: AIGeneration, manifest and derived artifact operational writes only.
- `CommandRepository`: immutable Command plus attempt records.
- `CommitRepository`: CommitUnit proof records.
- `AuditRepository`: append only.
- `OutboxRepository`: append in CommitUnit, delivery-state update by worker.
- `ProjectionRepository`: projection-only read/write.
- `RecoveryRepository`: RecoveryRecord reads and bounded operational updates.
- `SecurityEventRepository`: append only.

No repository returns an authority conclusion. AuthorityResolver consumes authoritative state and returns a proof-bearing resolution.

---

## 11. READ MODEL VS WRITE MODEL

Three explicit interfaces:

1. `CanonicalReadPort`
2. `GovernedMutationPort`, available only inside CommitUnit transaction orchestration
3. `ProjectionReadPort`

Commit evaluation, authority evaluation, governance evaluation, Evidence freshness and BND-014 use canonical reads.

UI may use projections for non-authoritative display. Any action request is re-resolved against canonical state.

Projection/cache values never satisfy a commit predicate.

---

## 12. COMMAND REGISTRY

Prototype Command catalogue:

| Command | Required authority | Human Decision | Evidence | Primary boundaries | Canonical effect |
|---|---|---|---|---|---|
| `CreateWorkspace` | BLOCKED for legitimate first root bootstrap | upstream unresolved | no | BND-001,002,014 | blocked in proof runtime |
| `AddWorkspaceMember` | WORKSPACE_GOVERNANCE_RIGHT | no separate domain Decision | no | 001,002,003,004,005,014,015 | membership relation |
| `GrantHumanAuthorityBinding` | WORKSPACE_GOVERNANCE_RIGHT | no | no | 001-005,014,015 | new HABB |
| `RevokeHumanAuthorityBinding` | WORKSPACE_GOVERNANCE_RIGHT | no | no | 001-005,014,015 | terminal revocation |
| `CreateChallenge` | approved Workspace-scoped operation authority from upstream mapping | as upstream requires | no | 001-005,014,015 | Challenge |
| `CreateSession` | SESSION_CONTROL_RIGHT where required | no | no | 001-007,014,015 | Session |
| `StartQuestionBurst` | SESSION_CONTROL_RIGHT | no | no | 001-008,014,015 | PREPARED -> ACTIVE |
| `PauseQuestionBurst` | SESSION_CONTROL_RIGHT | no | no | 001-008,014,015 | ACTIVE -> PAUSED |
| `ResumeQuestionBurst` | SESSION_CONTROL_RIGHT | no | no | 001-008,014,015 | PAUSED -> ACTIVE |
| `CompleteQuestionBurst` | SESSION_CONTROL_RIGHT | no | no | 001-008,014,015 | ACTIVE/allowed prior -> COMPLETED plus frozen set |
| `SubmitQuestion` | membership/participant eligibility, no invented human Decision right | no | no | 001-004,007,008,014,015 | Question plus Burst membership |
| `RequestAIAnalysis` | operation eligibility, not domain Decision Authority | no | context refs | 001-004,008,009,010,013 where used | AIGeneration/derived artifact only |
| `SelectQuestion` | QUESTION_SELECTION_RIGHT | human selection act | no unless path requires | 001-007,014,015 | QuestionSelection relation |
| `CreateEvidenceCandidate` | approved human/system operation path only | no | source/provenance | 001-005,013,014,015 | Evidence UNVALIDATED |
| `RecordHumanDecision` | DECISION_RIGHT | human creates Decision | exact consumed Evidence set if used | 001-007,013,014,015 | UNDER_CONSIDERATION -> DECIDED |
| `RequestConsequentialTransition` | target-specific approved authority | required where 03/04 say so | required where path says so | applicable chain plus 014/015 | legal target transition only |
| `RequestRecovery` | target-specific existing authority or deterministic 10 path | where discretionary | current Evidence where required | 001-007,013,014,015,017,018 | approved recovery effect only |

`CreateWorkspace` remains blocked for proof legitimacy. `NonProofWorkspaceBootstrap` is test/development-only and is not a Command in the legitimate runtime catalogue.

No generic `SetStatus`, `PatchDecision`, `PatchAuthority`, or `AdminRepair` Command exists.

---

## 13. QUERY REGISTRY

Queries are side-effect free.

| Query | Source | Scope rule |
|---|---|---|
| `GetWorkspaceContext` | canonical plus projection display | authenticated Workspace membership |
| `GetSession` | projection for display, canonical option for proof | Workspace scoped |
| `GetBurst` | projection/canonical proof | Workspace scoped |
| `ListBurstQuestions` | projection/canonical proof | Workspace scoped |
| `GetAIAnalysis` | derived/AI operational | Workspace scoped |
| `GetQuestionSelection` | canonical | Workspace scoped/read authorized |
| `GetDecision` | canonical | Workspace scoped/read authorized |
| `GetEvidenceContext` | canonical | Workspace and data access rules |
| `GetAuditTrail` | audit | Workspace/read authorization |
| `GetProvenance` | canonical/operational refs | Workspace/read authorization |
| `GetCommandProof` | command/commit/audit | proof-authorized Workspace query |
| `GetRecoveryStatus` | recovery | Workspace/read authorization |

Queries cannot mutate state, enqueue Commands, call providers, or create Events.

---

## 14. COMMAND PROCESSOR

Mandatory pipeline:

```text
RECEIVE COMMAND
-> VALIDATE VERSIONED CONTRACT
-> RESOLVE AUTHENTICATED ACTOR / SERVICE IDENTITY
-> RESOLVE WORKSPACE
-> LOAD AUTHORITATIVE CURRENT TARGET STATE
-> LOAD CURRENT MEMBERSHIP / GOVERNANCE
-> RESOLVE CURRENT AUTHORITY
-> RESOLVE HUMAN DECISION IF REQUIRED
-> RESOLVE CURRENT EVIDENCE SET IF REQUIRED
-> RUN PRECOMMIT BOUNDARIES
-> VALIDATE EXPECTED VERSIONS
-> BUILD MUTATION PLAN
-> ENTER COMMIT COORDINATOR
-> BND-014 FRESH RELOAD AND REVALIDATION
-> BEGIN DB TRANSACTION
-> APPLY CANONICAL / RELATION / GOVERNANCE MUTATIONS
-> INSERT AUDIT EVENT(S)
-> INSERT OUTBOX EVENT(S)
-> INSERT COMMIT UNIT
-> UPDATE IDEMPOTENCY STATE
-> COMMIT
-> RECONSTRUCT CONSEQUENCE CERTAINTY
-> RETURN ARCHITECTURAL OUTCOME
```

No handler may skip stages. Middleware may supply correlation, authentication and contract parsing, but may not pre-authorize the consequence.

---

## 15. BOUNDARY ENGINE

Interface:

```text
BoundaryInput
BoundaryContext
BoundaryResult
BoundaryProof
```

`BoundaryProof` contains:

`boundary_id`, `boundary_version`, `result`, `reason_code`, `workspace_id`, actor/service ref, input refs, authoritative version refs, authority proof refs where applicable, Evidence proof refs where applicable, timestamp, `correlation_id`.

Free text may accompany a reason code but cannot be the only proof.

Prototype status map:

- BND-001 Identity: IMPLEMENTED
- BND-002 Workspace: IMPLEMENTED
- BND-003 Membership: IMPLEMENTED
- BND-004 Role/Governance Context: IMPLEMENTED
- BND-005 Human Authority: IMPLEMENTED
- BND-006 Human Decision Authority: IMPLEMENTED
- BND-007 State Transition: IMPLEMENTED
- BND-008 Question Burst: IMPLEMENTED
- BND-009 AI Invocation: IMPLEMENTED
- BND-010 AI Output/Canonical State: IMPLEMENTED
- BND-011 SYSTEM_DERIVED: IMPLEMENTED only for exercised deterministic operations
- BND-012 Method: NOT_EXERCISED
- BND-013 Evidence: IMPLEMENTED for minimum Evidence path
- BND-014 Persistence/Commit: IMPLEMENTED, critical gate
- BND-015 Audit: IMPLEMENTED
- BND-016 Export: BLOCKED
- BND-017 Failure/Indeterminate: IMPLEMENTED
- BND-018 Recovery: IMPLEMENTED

A downstream ALLOW cannot override any upstream DENY.

---

## 16. AUTHORITY RESOLVER

Input:

actor, Workspace, operation, target, required authority class, current membership, current HABB, scope, governance state, current time/version where modeled.

Output `AuthorityResolution`:

`GRANTED`, `DENIED`, or `UNRESOLVED`.

`UNRESOLVED` is fail-closed for consequential operation.

Proof contains binding identity/version, membership identity/version, scope, operation, target, evaluated time/version and reason code.

Never authoritative inputs:

request `authorized=true`, JWT role alone, UI state, projection, cache, AI output, object authorship, database role, admin flag.

Commit-time resolver reloads current authoritative state.

---

## 17. GOVERNANCE MODULE

Executable governance includes:

- WorkspaceMembership
- HumanAuthorityBinding
- FacilitatorScopeBinding where exercised
- grant
- revocation
- replacement as revoke plus new grant
- current effective authority reconstruction
- immutable/history-preserving governance audit

Governance mutation itself is a governed Command and CommitUnit.

No direct governance CRUD.

`HARD-DEP-001` remains: first legitimate Workspace governance root creation is not solved here.

---

## 18. STATE TRANSITION ENGINE

Transition rules are centralized registry entries, not controller conditionals.

Each `TransitionSpec` includes:

object type, from state, requested transition, to state, required authority class, precondition evaluator refs, Evidence dependency, boundary refs, failure semantics.

No generic `set_status`.

Illegal topology is denied before mutation.

Prototype uses real 03 transitions. If a required legal path cannot be represented without an unapproved skip, that package stops.

---

## 19. QUESTION AND BURST IMPLEMENTATION

Question:

- create stable QuestionId
- persist immutable `original_text`
- persist origin separately from derivation
- reframe creates a new Question and QuestionLineage relation
- no update-original operation exists

Human-only Burst:

- PREPARED -> ACTIVE
- ACTIVE <-> PAUSED only if exercised
- authorized manual completion -> COMPLETED
- completion writes immutable frozen membership set and fingerprint
- no AI operation allowed while Human-only Burst is ACTIVE
- no append/remove/rewrite after frozen completion

`[IMPLEMENTATION CHOICE]`: frozen set fingerprint uses canonical sorted serialization of membership IDs plus Question content versions. Hash establishes identity/integrity relation only.

Automatic timer completion is not implemented.

---

## 20. QUESTION SELECTION

`SelectQuestion` creates QuestionSelection relation only after current `QUESTION_SELECTION_RIGHT` is proven.

AI recommendation may reference a Question but cannot create QuestionSelection.

Selection records actor, authority proof refs, Workspace, Session, Question, command/commit/audit correlation and version.

---

## 21. HUMAN DECISION

Decision lifecycle:

`UNDER_CONSIDERATION -> DECIDED`.

`RecordHumanDecision` is a human-authored Command path.

It records:

human actor, current `DECISION_RIGHT`, scope, Decision content, source context, AI recommendation refs if consumed, Evidence refs if consumed, provenance, version, timestamp, command/commit/audit refs.

No `ApproveAIRecommendationAsDecision` API exists.

The human creates the Decision the AI was never authorized to make.

A DECIDED Decision still does not equal executed downstream transition. Downstream transition is separately authorized and revalidated.

---

## 22. EVIDENCE AND PROVENANCE

Minimum physical semantics:

- Evidence is canonical and versioned.
- SourceReference identifies source material.
- ClaimAnchor identifies exact target/version/fingerprint semantics.
- EvidenceRelation links Evidence to ClaimAnchor with approved assessment vocabulary.
- EvidenceSetReference is an immutable consumed version set.
- ProvenanceEnvelope is represented as typed structured provenance attached to each provenance-bearing record, plus normalized lineage references where cross-artifact traversal is required.

`[IMPLEMENTATION CHOICE]`: hybrid typed JSONB provenance envelope plus normalized lineage link table. JSONB schema is versioned. This does not make ProvenanceEnvelope a universal domain Thing.

Commit freshness rechecks every Evidence version consumed by a consequential operation.

No global Evidence score or unresolved sufficiency algorithm is implemented.

---

## 23. AI GATEWAY AND AIOP IMPLEMENTATION

Only `packages/ai_gateway/adapters/providers/` may import a provider SDK.

Gateway pipeline:

```text
AIOP REQUEST
-> CONTRACT REGISTRY
-> WORKSPACE CHECK
-> CONTEXT ALLOWLIST BUILDER
-> AIContextManifest
-> PROMPT BUILDER
-> MODEL ROUTER
-> PROVIDER ADAPTER
-> RESPONSE VALIDATOR
-> AI_VALIDATION_PROOF
-> DERIVED ARTIFACT MATERIALIZATION
```

Only Gateway receives provider credentials.

Default prototype adapter: `MockProviderAdapter`.

Real provider execution remains blocked by `HARD-DEP-002`.

Prototype AIOPs:

- AIOP-001 Question analysis
- optional minimum perspective/derived operation only if 12 proof path requires it

No AIOP has authority-bearing canonical effect.

AIOP contract records operation ID, contract version, input schema, context allowlist, forbidden context, output schema, validator, maximum canonical effect, provenance, retry and failure policy.

---

## 24. AI CONTEXT, PROMPTS AND RESPONSE VALIDATION

AIContextManifest includes:

Workspace, AIOP, contract version, input refs/versions, Evidence refs if used, source refs if used, excluded context classes, prompt version, provider-policy decision reference, generation_id.

Whole-Workspace context is forbidden.

Prompt layers are stored/versioned separately:

1. system operation contract
2. task instruction
3. structured context
4. retrieved data
5. user content

Retrieved/user/imported material is delimited as DATA.

Response validation checks schema, contract, maximum canonical effect, origin/provenance, Workspace and resource bounds.

Successful validation yields `AI_VALIDATION_PROOF`, never Domain Evidence, Human Decision or Authority.

AI proposal for consequence becomes only an application proposal. A legitimate actor must create a new governed Command through the normal pipeline.

---

## 25. COMMIT UNIT IMPLEMENTATION

`[IMPLEMENTATION CHOICE]`: PostgreSQL transaction with `READ COMMITTED` plus explicit row/version locking and compare-and-swap version predicates. Where a multi-row predicate requires stronger serialization, the CommitCoordinator acquires deterministic row locks in canonical ID order. The semantic requirement is fresh predicate validation, not reliance on isolation level alone.

Commit algorithm:

1. allocate `commit_id` before transaction body as non-semantic unique identity
2. begin transaction
3. load authoritative target versions and dependency versions
4. load current membership/governance/HABB
5. load current Evidence versions where required
6. execute BND-014 inside the commit coordination window
7. verify expected versions
8. apply canonical mutations with version predicates
9. apply relation mutations
10. apply governance mutations where applicable
11. insert required AuditEvent rows
12. insert Outbox rows
13. insert CommitUnit proof row
14. update IdempotencyRecord
15. commit database transaction
16. resolve post-commit certainty using authoritative DB evidence

If transaction is proven rolled back before commit: `FAILED_PRECOMMIT`.

If commit is proven durable: `COMMITTED`.

If commit acknowledgement is lost and authoritative reconstruction cannot prove committed or not committed: `INDETERMINATE`.

Client timeout alone never selects an outcome.

Atomicity gate: no phase after Build Phase 4 may proceed unless failure injection proves canonical mutation, required relations/governance, AuditEvent, outbox, CommitUnit and idempotency outcome cannot expose a falsely legitimate partial state.

---

## 26. OPTIMISTIC CONCURRENCY

Mutable consequential records use `record_version`.

Command carries expected versions.

Canonical mutation pattern:

```text
UPDATE target
SET ..., record_version = record_version + 1
WHERE id = :id
  AND workspace_id = :workspace_id
  AND record_version = :expected_version
```

Unexpected affected-row count is a stale conflict. No overwrite occurs.

Governance and Evidence dependencies carry expected/current proof refs and are freshly checked at BND-014.

No last-write-wins domain winner selection.

---

## 27. IDEMPOTENCY

Idempotency identity includes Workspace, command type, idempotency key and payload fingerprint.

Stored:

idempotency_key, command_id, Workspace, command_type, payload_fingerprint, status, latest_attempt_id, commit_id, result_ref.

Rules:

- new request -> create command/attempt
- same identity IN_PROGRESS -> return in-progress state, no second execution
- same identity COMMITTED -> return prior committed result
- same key different payload -> reject collision
- FAILED_PRECOMMIT -> same command_id, new attempt_id, full fresh boundaries
- INDETERMINATE -> no blind retry, route BND-017/BND-018

---

## 28. AUDIT, OUTBOX, EVENT AND PROJECTION

AuditEvent is append-oriented. Normal runtime cannot update/delete audit.

Correction creates a new corrective AuditEvent.

Outbox is inserted in the same CommitUnit transaction. Delivery worker may update delivery metadata only.

Outbox retry is delivery retry, not domain retry.

EventEnvelope is created from committed fact and includes event_id, schema version, Workspace, aggregate/version, command_id, commit_id, correlation_id, causation_id, actor/service and authority source references.

Event consumers may rebuild/update projections and perform explicitly permitted non-consequential work.

Consequential follow-on requires a new Command.

Projection is rebuildable and may be dropped without canonical consequence. Commit/authority/Evidence freshness never reads projection as truth.

---

## 29. FAILURE, CONSEQUENCE CERTAINTY AND INDETERMINATE

Code uses an explicit outcome union, never boolean success.

Failure classifier first determines consequence certainty, then maps operational failure.

ConsequenceCertaintyResolver uses:

Command/Attempt history, CommitUnit, canonical versions, governance versions, AuditEvent, outbox, external consequence records where applicable, idempotency, AI/tool lineage and correlation.

Telemetry is diagnostic only.

INDETERMINATE creates dependency blocking metadata tied to the affected command/target/dependency graph. It is not a global failed flag.

Dependent consequential Commands encounter BND-017 and are blocked until reconciliation.

---

## 30. LAST_PROVEN_VALID_STATE AND RECOVERY

LPVS algorithm:

1. gather candidate historical states from committed canonical versions
2. require reconstructable legal transition
3. require actor/service identity
4. require authority current at commit
5. require Human Decision where required
6. require consumed Evidence versions where required
7. require boundary and BND-014 proof
8. require CommitUnit and required audit/outbox proof
9. exclude later uncertain attempts from legitimacy
10. return latest state in the legitimate causal chain, not latest timestamp

If no candidate satisfies proof: `UNRESOLVED`.

RecoveryRecord persists 10 fields and outcome vocabulary.

Recovery Command passes normal identity, Workspace, current authority, Evidence where required, boundaries, BND-018, BND-014 and CommitUnit.

Recovery worker cannot inherit original actor authority and has no unrestricted canonical writer.

---

## 31. SECURITY IMPLEMENTATION

Authentication adapter establishes actor identity only.

Service identities are explicit for API/application, Commit writer, projection worker, AI Gateway, recovery worker and security/observability actors.

Provider credentials exist only in AI Gateway runtime secret scope.

DB credentials are capability-specific.

Admin tooling has no domain-authority fallback.

SecurityEvent records cross-Workspace attempt, direct-write attempt where detectable, Gateway bypass, credential misuse, audit anomaly and privileged infrastructure mutation.

SecurityEvent cannot mutate domain state.

Environment identity is included in audit/observability proof where relevant.

---

## 32. AUTHENTICATION AND SERVICE IDENTITY

`[IMPLEMENTATION CHOICE]`: OIDC-compatible authentication port.

Production-compatible adapter validates issuer, audience, signature, expiry and revocation/session state as supported by the chosen identity provider. Test adapter is deterministic.

Mapped request context:

`AuthenticatedPrincipal(UserId, authentication_session_ref, authentication_time, issuer_ref)`.

No authority classes are accepted from token claims as authoritative facts.

Service identities use separately provisioned credentials and are mapped to fixed technical capability scopes. `AI_PROCESSOR != SYSTEM_SERVICE`. SYSTEM_DERIVED remains operation-specific and predicate-bound.

---

## 33. SECRETS AND CONFIGURATION

Typed configuration domains:

environment, provider, security, resource limits, observability.

Human authority never comes from configuration.

Secrets are injected at runtime through a secret-loading port.

Forbidden locations:

frontend bundles, source control, prompts, logs, traces, fixtures, architecture files.

`REAL_PROVIDER_ENABLED=false` is default, but changing it is not sufficient to prove provider eligibility. A provider-policy eligibility record/configuration proof must also exist after `HARD-DEP-002` is legitimately resolved upstream.

---

## 34. OBSERVABILITY

Structured diagnostic fields:

correlation_id, command_id, attempt_id, commit_id, event_id, generation_id, recovery_id, pseudonymous Workspace ref where appropriate, operation, boundary result, failure class, service identity.

No full sensitive Evidence or unrestricted prompts by default.

Trace context contains correlation only, never reusable authorization.

Audit is separate persistence and separate semantics.

---

## 35. API EDGE AND ERROR CONTRACT

HTTP pipeline:

```text
HTTP
-> AUTHENTICATION
-> CORRELATION
-> WORKSPACE CONTEXT
-> VERSIONED CONTRACT VALIDATION
-> QUERY OR COMMAND DISPATCH
```

Controllers contain no authority logic, no ORM mutation, no provider SDK.

External errors distinguish:

validation, authentication, authority/boundary denial, stale version/conflict, failed precommit, indeterminate, blocked unresolved state, Workspace-scoped not-found, provider unavailable.

Internal proof remains richer and sensitive authority/security detail is not leaked unnecessarily.

---

## 36. PROTOTYPE API MAP

| Method | Path | Dispatch | Key requirements |
|---|---|---|---|
| POST | `/v1/workspaces` | `CreateWorkspace` | BLOCKED in legitimate proof runtime by HARD-DEP-001 |
| POST | `/v1/workspaces/{workspace_id}/members` | `AddWorkspaceMember` | governance right, idempotency, expected governance version |
| POST | `/v1/workspaces/{workspace_id}/authority-bindings` | `GrantHumanAuthorityBinding` | WORKSPACE_GOVERNANCE_RIGHT |
| POST | `/v1/workspaces/{workspace_id}/authority-bindings/{binding_id}/revoke` | `RevokeHumanAuthorityBinding` | WORKSPACE_GOVERNANCE_RIGHT |
| POST | `/v1/workspaces/{workspace_id}/challenges` | `CreateChallenge` | semantic operation authority, idempotency |
| POST | `/v1/workspaces/{workspace_id}/sessions` | `CreateSession` | SESSION_CONTROL_RIGHT where required |
| POST | `/v1/workspaces/{workspace_id}/sessions/{session_id}/bursts` | `Create/Prepare Burst` | Session legality |
| POST | `/v1/workspaces/{workspace_id}/bursts/{burst_id}/start` | `StartQuestionBurst` | SESSION_CONTROL_RIGHT, expected version |
| POST | `/v1/workspaces/{workspace_id}/bursts/{burst_id}/pause` | `PauseQuestionBurst` | only if exercised |
| POST | `/v1/workspaces/{workspace_id}/bursts/{burst_id}/resume` | `ResumeQuestionBurst` | only if exercised |
| POST | `/v1/workspaces/{workspace_id}/bursts/{burst_id}/questions` | `SubmitQuestion` | Human-only Burst rules |
| POST | `/v1/workspaces/{workspace_id}/bursts/{burst_id}/complete` | `CompleteQuestionBurst` | SESSION_CONTROL_RIGHT, freeze |
| POST | `/v1/workspaces/{workspace_id}/bursts/{burst_id}/ai-analysis` | `RequestAIAnalysis` | post-freeze, Gateway only |
| POST | `/v1/workspaces/{workspace_id}/sessions/{session_id}/question-selection` | `SelectQuestion` | QUESTION_SELECTION_RIGHT |
| POST | `/v1/workspaces/{workspace_id}/evidence` | `CreateEvidenceCandidate` | Workspace/provenance |
| POST | `/v1/workspaces/{workspace_id}/decisions` | `CreateDecisionUnderConsideration` | approved path only |
| POST | `/v1/workspaces/{workspace_id}/decisions/{decision_id}/decide` | `RecordHumanDecision` | DECISION_RIGHT, expected version, Evidence refs if used |
| POST | `/v1/workspaces/{workspace_id}/transitions` | `RequestConsequentialTransition` | target-specific contract |
| POST | `/v1/workspaces/{workspace_id}/recoveries` | `RequestRecovery` | BND-017/BND-018 plus normal governance |
| GET | `/v1/workspaces/{workspace_id}/sessions/{session_id}` | Query | Workspace-scoped |
| GET | `/v1/workspaces/{workspace_id}/audit` | Query | read authorization |
| GET | `/v1/workspaces/{workspace_id}/proof/commands/{command_id}` | Query | proof-authorized |
| GET | `/v1/workspaces/{workspace_id}/recoveries/{recovery_id}` | Query | Workspace-scoped |

No operational export endpoint.

No generic PATCH status endpoint.

---

## 37. FRONTEND ARCHITECTURE

Minimum modules:

- Workspace context
- Challenge/Session
- Question Burst
- Question capture
- frozen raw set
- AI analysis panel with AI origin
- QuestionSelection
- Decision workspace
- Evidence context
- blocked/denied/indeterminate state
- audit/provenance proof viewer

Human Decision UI shows AI recommendation separately. The human Decision control creates a human-owned Decision and records consumed context.

During Human-only ACTIVE Burst there are no AI analysis, suggestion, scoring, reframing or generation controls.

UI capability hints are non-authoritative. Every request is server revalidated.

---

## 38. LOCAL DEVELOPMENT AND MOCKS

Docker Compose:

- PostgreSQL
- API/backend
- worker process
- frontend
- local mock provider endpoint or in-process adapter selected by explicit test config

Mock provider scenarios:

valid output, invalid schema, timeout, provider error, partial response, duplicate response, prompt injection payload, wrong Workspace artifact, retry scenario, forbidden-effect payload.

Mock provider proves Gateway/contract behavior only.

`NonProofWorkspaceBootstrap` is available only under `packages/test_support/nonproof_bootstrap.py`, guarded by test/development build condition and import architecture test.

Every record created through it carries test metadata `fixture_legitimacy = NON_PROOF_FIXTURE` in the test harness, not as production domain semantics.

---

## 39. TEST DIRECTORY AND PROOF HARNESS

13 levels map:

- T0 -> `tests/semantic/`
- T1 -> `tests/domain/`
- T2 -> `tests/transitions/`
- T3 -> `tests/authority/`, `tests/governance/`
- T4 -> `tests/boundaries/`
- T5 -> `tests/evidence/`
- T6 -> `tests/ai/`
- T7 -> `tests/command_commit_event/`
- T8 -> `tests/recovery/`
- T9 -> `tests/security/`
- T10 -> `tests/e2e/`
- T11 -> `tests/mutation/`
- T12 -> `tests/regression/`

`TestProofBundle` gathers authoritative references to canonical state, governance, authority, boundaries, CommitUnit, AuditEvent, EventEnvelope, Evidence versions, AI lineage, RecoveryRecord and SecurityEvent.

Logs are never the sole oracle.

---

## 40. FAILURE, CONCURRENCY AND SECURITY INJECTION

Test-only `FailureInjector` hooks:

before transaction, after authority evaluation, after BND-014, after first canonical mutation, after relation mutation, before audit, after audit, before outbox, after outbox, before DB commit, after DB commit before response.

Production import test forbids FailureInjector.

Deterministic concurrency harness uses barriers/hooks, never sleep timing, for:

two Commands same initial version, authority revocation between prepare/commit, Evidence change between prepare/commit, state change between prepare/commit.

Security attack harness covers cross-Workspace references, wrong DB principal, direct canonical write, direct provider path, admin domain mutation, forged role/authority request, revoked session, Event forgery, audit tamper and isolated backup restore.

---

## 41. DEPENDENCY ENFORCEMENT

Mandatory static checks:

- provider SDK import only under provider adapter
- AI packages cannot import canonical writer
- projection cannot import canonical mutation
- controllers cannot import SQLAlchemy mutation session
- domain cannot import infrastructure
- recovery cannot import unrestricted DB writer
- event consumer cannot import direct consequential handler
- frontend cannot import backend persistence
- production packages cannot import `test_support`
- observability cannot import domain mutation

A surviving forbidden import fails Phase 0 or the phase that introduced it.

---

## 42. CONTRACT VERSIONING, CLOCK, IDS AND FINGERPRINTS

Commands, Events, AIOPs, AI outputs and materially changed boundary contracts are versioned.

No silent semantic contract change.

Boundary validation occurs at HTTP, Command, Event, AI input/output, configuration and external payload edges.

`Clock` port centralizes time for deterministic expiry, binding validity where modeled, audit, event and recovery tests.

`IdGenerator` port supports deterministic tests. IDs are non-semantic.

Fingerprints use canonical serialization with explicit schema/version. Hash proves content identity/integrity relationship only.

---

## 43. DELETION, EXPORT, METHOD APPROVAL, PRODUCTION CLAIMS

Global deletion is not implemented. Retention/deletion tension remains explicit.

Export consequence is blocked because Export Authority is unresolved.

Method Approval is `NOT_EXERCISED` in the prototype. No default approved method is invented.

Completed implementation may claim only `ARCHITECTURAL PROTOTYPE`, subject to proof status. It may not automatically claim production readiness, regulatory compliance, privacy approval, provider approval, security certification or validated-system status.

---

## 44. BUILD PHASES AND GATES

### PHASE 0: ARCHITECTURE MATERIALIZATION SKELETON
Objective: repository, toolchain, semantic packages, dependency tests, PostgreSQL dev environment, CI skeleton.
Gate: build/lint/typecheck pass, DB starts, migration pipeline empty-pass, forbidden imports detected.
Human gate: required.

### PHASE 1: IDENTITY / WORKSPACE / GOVERNANCE FOUNDATION
Implement identity mapping, Workspace, membership, HABB, facilitator scope if exercised, governance ports, AuthorityResolver skeleton.
Use NonProof bootstrap only for tests.
Gate: role alone grants nothing, cross-Workspace governance refs fail, revocation represented, AI/service cannot receive human right.
Human gate: required.

### PHASE 2: DOMAIN CORE / SESSION / QUESTION
Implement Challenge, Session, Question, lineage, Burst, transition registry, frozen raw set.
Gate: P-01 through P-04 candidate tests, illegal transition tests, immutability.
Human gate: required.

### PHASE 3: BOUNDARY PIPELINE
Implement BND registry and prototype boundaries through Burst.
Gate: monotonic DENY, no cached ALLOW substitution, no handler bypass.
Human gate: required.

### PHASE 4: COMMAND / COMMIT FOUNDATION
Implement CommandEnvelope, attempts, idempotency, expected versions, CommitUnit, AuditEvent, outbox, BND-014.
Critical gate: transaction failure injection proves atomic legitimacy.
Human gate: required. Do not proceed if not proven.

### PHASE 5: QUESTION SELECTION / HUMAN DECISION AUTHORITY
Implement QuestionSelection, QUESTION_SELECTION_RIGHT, Decision, DECISION_RIGHT, BND-006.
Gate: AI/admin cannot decide/select, human creates Decision, stale authority cannot commit.
Human gate: required.

### PHASE 6: EVIDENCE / PROVENANCE
Implement minimum 07 stack and freshness.
Gate: stale Evidence fails, provenance reconstructable, AI confidence rejected as Evidence.
Human gate: required.

### PHASE 7: AI GATEWAY / DERIVED ARTIFACTS
Implement AIGeneration, Gateway, AIOP registry, prompt/context, MockProvider, validator, AI_VALIDATION_PROOF.
Gate: active Burst blocks AI, direct provider path blocked, cross-Workspace context blocked, AI output non-authoritative.
Human gate: required.

### PHASE 8: EVENT / PROJECTION
Implement outbox worker, EventEnvelope, projection, rebuild.
Gate: Event post-commit, replay no consequence, projection cannot drive commit authority.
Human gate: required.

### PHASE 9: FAILURE / INDETERMINATE / RECOVERY
Implement classifier, certainty resolver, blocking, LPVS, RecoveryRecord, BND-017/018.
Gate: blind retry blocked, recovery cannot create authority, LPVS legitimacy over recency.
Human gate: required.

### PHASE 10: SECURITY HARDENING
Implement DB principals, service identities, RLS defense, AI credential isolation, SecurityEvents, admin separation.
Gate: direct invalid write paths technically rejected where claimed.
Human gate: required.

### PHASE 11: MINIMUM UI
Implement only 12 proof UI.
Gate: human/AI distinction visible, Decision creation semantics correct, Burst protection visible, server authority remains decisive.
Human gate: required.

### PHASE 12: END-TO-END ARCHITECTURAL PROOF
Run happy, denial, stale-authority, cross-Workspace, AI-boundary and recovery paths with TestProofBundle.
Gate: P-01 through P-25 pass where legitimately executable. Hard dependencies remain blocked.
Human gate: required.

### PHASE 13: MUTATION / ADVERSARIAL PROOF
Remove core invariants intentionally.
Gate: relevant tests fail for each mutation. Surviving mutation fails suite.
Human gate: required.

### PHASE 14: RECURSIVE REGRESSION
Run dependency-based affected suite and produce proof report.
Possible status:
`ARCHITECTURAL_IMPLEMENTATION_PROOF::PASS`
`EXECUTABLE_PROTOTYPE_ACCEPTANCE::BLOCKED`
while hard dependencies remain.
Human gate: required.

Every phase report includes PHASE ID, objective, source architecture, files created/modified, migrations, public contracts, invariants, tests, proof claims, gaps, blockers, forbidden shortcuts, pass/fail criteria and next-phase authorization.

Codex never self-authorizes the next phase.

---

## 45. CODING AGENT DISCIPLINE

Every coding task:

1. read exact upstream files/sections
2. state intended change
3. state affected invariants
4. state modules and migrations
5. state tests before coding
6. implement smallest coherent change
7. run targeted tests
8. run recursive affected tests
9. report diff and proof artifacts
10. report failures and architecture questions
11. stop on semantic ambiguity

Forbidden:

invent authority, transition, role fallback, Evidence semantics, recovery behavior, provider policy, bootstrap legitimacy, weaken tests, delete failing tests without approval, silently edit architecture.

No architecture-critical TODO, FIXME, allow-all boundary, mock AuthorityResolver, fake audit/commit, in-memory production idempotency, catch-all retry, admin bypass or placeholder Workspace filter can satisfy a phase gate.

---

## 46. CODING PACKAGE MANIFEST

Packages are ordered semantic implementation units.

### PKG-00: Repository and architecture skeleton

- BUILD_PHASE: 0
- OBJECTIVE: Create toolchain, package boundaries, dependency enforcement, local DB and CI skeleton
- UPSTREAM FILES TO READ: 00-14
- REQUIRED PREDECESSORS: none
- PUBLIC INTERFACES: semantic_types and architecture checks
- DATABASE CHANGES: none
- TESTS REQUIRED: T0/T12
- PROOF CLAIMS: P-18,P-23,P-24
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-01: Identity and Workspace types

- BUILD_PHASE: 1
- OBJECTIVE: Materialize User identity mapping, Workspace identity and request Workspace context
- UPSTREAM FILES TO READ: 01,02,04,11,12,14
- REQUIRED PREDECESSORS: PKG-00
- PUBLIC INTERFACES: identity ports, WorkspaceRepository read contracts
- DATABASE CHANGES: 001
- TESTS REQUIRED: T0,T1,T9
- PROOF CLAIMS: P-22,P-25
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-02: Membership and governance persistence

- BUILD_PHASE: 1
- OBJECTIVE: Membership, HABB, governance history and governed mutation ports
- UPSTREAM FILES TO READ: 02,04,05,09,11,14
- REQUIRED PREDECESSORS: PKG-01
- PUBLIC INTERFACES: MembershipRepository, AuthorityBindingRepository
- DATABASE CHANGES: 002
- TESTS REQUIRED: T3
- PROOF CLAIMS: P-10,P-11,P-12
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-03: AuthorityResolver

- BUILD_PHASE: 1
- OBJECTIVE: Current operation-specific authority resolution with proof refs
- UPSTREAM FILES TO READ: 04,05,06,13,14
- REQUIRED PREDECESSORS: PKG-02
- PUBLIC INTERFACES: AuthorityResolver
- DATABASE CHANGES: none
- TESTS REQUIRED: T3,T4
- PROOF CLAIMS: P-10,P-11,P-24
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-04: NonProof bootstrap adapter

- BUILD_PHASE: 1
- OBJECTIVE: Test/dev-only fixture bootstrap without legitimacy claim
- UPSTREAM FILES TO READ: 12,13,14
- REQUIRED PREDECESSORS: PKG-02
- PUBLIC INTERFACES: NonProofWorkspaceBootstrap
- DATABASE CHANGES: test only
- TESTS REQUIRED: fixture validation
- PROOF CLAIMS: downstream only
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-05: Challenge and Session domain

- BUILD_PHASE: 2
- OBJECTIVE: Canonical Challenge/Session types and transition registry base
- UPSTREAM FILES TO READ: 02,03,12,14
- REQUIRED PREDECESSORS: PKG-01
- PUBLIC INTERFACES: Challenge, Session, TransitionSpec
- DATABASE CHANGES: 003
- TESTS REQUIRED: T1,T2
- PROOF CLAIMS: P-25
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-06: Question identity and lineage

- BUILD_PHASE: 2
- OBJECTIVE: Question stable identity, immutable original, lineage
- UPSTREAM FILES TO READ: 02,03,07,12,13,14
- REQUIRED PREDECESSORS: PKG-05
- PUBLIC INTERFACES: QuestionRepository contract
- DATABASE CHANGES: 004
- TESTS REQUIRED: T1
- PROOF CLAIMS: P-01,P-02
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-07: Question Burst and frozen set

- BUILD_PHASE: 2
- OBJECTIVE: Human-only Burst states, capture, freeze and contamination guard
- UPSTREAM FILES TO READ: 03,06,08,12,13,14
- REQUIRED PREDECESSORS: PKG-06,PKG-03
- PUBLIC INTERFACES: Burst operations
- DATABASE CHANGES: 004
- TESTS REQUIRED: T2,T4
- PROOF CLAIMS: P-03,P-04
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-08: Boundary engine core

- BUILD_PHASE: 3
- OBJECTIVE: Boundary types, proof, registry, monotonic restriction
- UPSTREAM FILES TO READ: 06,14
- REQUIRED PREDECESSORS: PKG-03,PKG-05
- PUBLIC INTERFACES: BoundaryEvaluator registry
- DATABASE CHANGES: none
- TESTS REQUIRED: T4
- PROOF CLAIMS: P-13
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-09: Prototype boundaries 001-008

- BUILD_PHASE: 3
- OBJECTIVE: Identity through Burst boundary evaluators
- UPSTREAM FILES TO READ: 06,11,12,13,14
- REQUIRED PREDECESSORS: PKG-07,PKG-08
- PUBLIC INTERFACES: BND-001..008
- DATABASE CHANGES: none
- TESTS REQUIRED: T4,T9
- PROOF CLAIMS: P-03,P-04,P-10,P-13,P-22
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-10: Command envelope and attempts

- BUILD_PHASE: 4
- OBJECTIVE: Command contracts, registry, attempts and expected versions
- UPSTREAM FILES TO READ: 09,12,13,14
- REQUIRED PREDECESSORS: PKG-09
- PUBLIC INTERFACES: CommandEnvelope, CommandRegistry
- DATABASE CHANGES: 008
- TESTS REQUIRED: T7
- PROOF CLAIMS: P-16,P-19
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-11: Idempotency

- BUILD_PHASE: 4
- OBJECTIVE: Durable idempotency lifecycle and payload identity
- UPSTREAM FILES TO READ: 09,10,13,14
- REQUIRED PREDECESSORS: PKG-10
- PUBLIC INTERFACES: IdempotencyPort
- DATABASE CHANGES: 008
- TESTS REQUIRED: T7
- PROOF CLAIMS: P-19,P-20
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-12: Audit and outbox contracts

- BUILD_PHASE: 4
- OBJECTIVE: Append AuditEvent and durable outbox semantics
- UPSTREAM FILES TO READ: 09,11,13,14
- REQUIRED PREDECESSORS: PKG-10
- PUBLIC INTERFACES: AuditRepository, OutboxRepository
- DATABASE CHANGES: 009
- TESTS REQUIRED: T7
- PROOF CLAIMS: P-16,P-25
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-13: Commit coordinator and BND-014

- BUILD_PHASE: 4
- OBJECTIVE: Atomic governed CommitUnit with fresh authority/version checks
- UPSTREAM FILES TO READ: 03,05,06,09,10,13,14
- REQUIRED PREDECESSORS: PKG-11,PKG-12
- PUBLIC INTERFACES: CommitCoordinator
- DATABASE CHANGES: 009
- TESTS REQUIRED: T4,T7,T11
- PROOF CLAIMS: P-10,P-11,P-13,P-18,P-19,P-25
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-14: QuestionSelection

- BUILD_PHASE: 5
- OBJECTIVE: Authority-bearing QuestionSelection relation
- UPSTREAM FILES TO READ: 02,03,04,06,12,13,14
- REQUIRED PREDECESSORS: PKG-13,PKG-07
- PUBLIC INTERFACES: SelectQuestion command
- DATABASE CHANGES: 005
- TESTS REQUIRED: T3,T7
- PROOF CLAIMS: P-08
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-15: Human Decision

- BUILD_PHASE: 5
- OBJECTIVE: UNDER_CONSIDERATION to human DECIDED, separate downstream execution
- UPSTREAM FILES TO READ: 02,03,04,06,08,12,13,14
- REQUIRED PREDECESSORS: PKG-13
- PUBLIC INTERFACES: Decision commands
- DATABASE CHANGES: 005
- TESTS REQUIRED: T3,T10
- PROOF CLAIMS: P-07,P-09,P-10
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-16: Evidence core

- BUILD_PHASE: 6
- OBJECTIVE: Evidence, source, anchor, relation, set and provenance storage
- UPSTREAM FILES TO READ: 07,09,12,13,14
- REQUIRED PREDECESSORS: PKG-13
- PUBLIC INTERFACES: EvidenceRepository
- DATABASE CHANGES: 006
- TESTS REQUIRED: T5
- PROOF CLAIMS: P-14,P-15
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-17: Evidence freshness boundary

- BUILD_PHASE: 6
- OBJECTIVE: BND-013 and commit freshness linkage
- UPSTREAM FILES TO READ: 06,07,09,13,14
- REQUIRED PREDECESSORS: PKG-16,PKG-13
- PUBLIC INTERFACES: Evidence proof resolver
- DATABASE CHANGES: none
- TESTS REQUIRED: T4,T5,T7
- PROOF CLAIMS: P-14,P-15,P-25
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-18: AI contracts and AIGeneration

- BUILD_PHASE: 7
- OBJECTIVE: AIOP registry, generation lifecycle and derived artifact types
- UPSTREAM FILES TO READ: 08,09,12,13,14
- REQUIRED PREDECESSORS: PKG-17
- PUBLIC INTERFACES: AI contracts
- DATABASE CHANGES: 007
- TESTS REQUIRED: T6
- PROOF CLAIMS: P-05,P-06,P-07
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-19: AI Gateway and MockProvider

- BUILD_PHASE: 7
- OBJECTIVE: Exclusive provider path, context manifest, prompt, validator
- UPSTREAM FILES TO READ: 08,11,12,13,14
- REQUIRED PREDECESSORS: PKG-18,PKG-09
- PUBLIC INTERFACES: AIGateway
- DATABASE CHANGES: 007
- TESTS REQUIRED: T6,T9
- PROOF CLAIMS: P-04,P-05,P-06,P-07,P-23
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-20: Event and outbox worker

- BUILD_PHASE: 8
- OBJECTIVE: EventEnvelope delivery from committed outbox
- UPSTREAM FILES TO READ: 09,10,13,14
- REQUIRED PREDECESSORS: PKG-13
- PUBLIC INTERFACES: EventPublisher/consumer contracts
- DATABASE CHANGES: none
- TESTS REQUIRED: T7
- PROOF CLAIMS: P-16,P-17
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-21: Projection and replay

- BUILD_PHASE: 8
- OBJECTIVE: Rebuildable read models, replay without consequence
- UPSTREAM FILES TO READ: 06,09,10,13,14
- REQUIRED PREDECESSORS: PKG-20
- PUBLIC INTERFACES: ProjectionRepository
- DATABASE CHANGES: 010
- TESTS REQUIRED: T7,T11
- PROOF CLAIMS: P-17
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-22: Failure classification and certainty

- BUILD_PHASE: 9
- OBJECTIVE: Four outcomes and consequence certainty resolver
- UPSTREAM FILES TO READ: 10,13,14
- REQUIRED PREDECESSORS: PKG-13,PKG-20
- PUBLIC INTERFACES: FailureClassifier
- DATABASE CHANGES: none
- TESTS REQUIRED: T8
- PROOF CLAIMS: P-20,P-25
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-23: LPVS and RecoveryRecord

- BUILD_PHASE: 9
- OBJECTIVE: Legitimacy-based LPVS and RecoveryRecord
- UPSTREAM FILES TO READ: 10,13,14
- REQUIRED PREDECESSORS: PKG-22,PKG-17
- PUBLIC INTERFACES: LPVSResolver, RecoveryRepository
- DATABASE CHANGES: 011
- TESTS REQUIRED: T8
- PROOF CLAIMS: P-20,P-21
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-24: BND-017/BND-018 and Recovery Command

- BUILD_PHASE: 9
- OBJECTIVE: Indeterminate blocking, reconciliation and governed recovery
- UPSTREAM FILES TO READ: 06,10,13,14
- REQUIRED PREDECESSORS: PKG-23,PKG-13
- PUBLIC INTERFACES: RecoveryService through Command
- DATABASE CHANGES: 011
- TESTS REQUIRED: T4,T8
- PROOF CLAIMS: P-20,P-21
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-25: Service identity and DB principals

- BUILD_PHASE: 10
- OBJECTIVE: Runtime technical identities and privilege separation
- UPSTREAM FILES TO READ: 11,13,14
- REQUIRED PREDECESSORS: PKG-13,PKG-19,PKG-21,PKG-24
- PUBLIC INTERFACES: security capability map
- DATABASE CHANGES: 012
- TESTS REQUIRED: T9
- PROOF CLAIMS: P-18,P-22,P-23,P-24
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-26: RLS and SecurityEvents

- BUILD_PHASE: 10
- OBJECTIVE: Workspace defense-in-depth and security operational records
- UPSTREAM FILES TO READ: 11,13,14
- REQUIRED PREDECESSORS: PKG-25
- PUBLIC INTERFACES: SecurityEventRepository
- DATABASE CHANGES: 012
- TESTS REQUIRED: T9
- PROOF CLAIMS: P-22,P-24
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-27: Observability correlation

- BUILD_PHASE: 10
- OBJECTIVE: Structured diagnostic correlation without authority/truth
- UPSTREAM FILES TO READ: 11,13,14
- REQUIRED PREDECESSORS: PKG-13,PKG-19,PKG-24
- PUBLIC INTERFACES: ObservationContext
- DATABASE CHANGES: none
- TESTS REQUIRED: T9
- PROOF CLAIMS: P-25
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-28: Minimum frontend shell

- BUILD_PHASE: 11
- OBJECTIVE: Workspace, Session, Burst, origin labels and blocked states
- UPSTREAM FILES TO READ: 12,14
- REQUIRED PREDECESSORS: PKG-21,PKG-26
- PUBLIC INTERFACES: typed API client
- DATABASE CHANGES: none
- TESTS REQUIRED: UI tests
- PROOF CLAIMS: P-03,P-04,P-22
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-29: Human Decision UI

- BUILD_PHASE: 11
- OBJECTIVE: Separate AI recommendation from human Decision creation
- UPSTREAM FILES TO READ: 12,13,14
- REQUIRED PREDECESSORS: PKG-15,PKG-19,PKG-28
- PUBLIC INTERFACES: Decision UI contract
- DATABASE CHANGES: none
- TESTS REQUIRED: E2E
- PROOF CLAIMS: P-07,P-08,P-09
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-30: TestProofBundle and E2E proof paths

- BUILD_PHASE: 12
- OBJECTIVE: Authoritative proof collection and six mandatory paths
- UPSTREAM FILES TO READ: 12,13,14
- REQUIRED PREDECESSORS: PKG-24,PKG-26,PKG-29
- PUBLIC INTERFACES: TestProofBundle
- DATABASE CHANGES: none
- TESTS REQUIRED: T10
- PROOF CLAIMS: P-01..P-25
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-31: Mutation and adversarial harness

- BUILD_PHASE: 13
- OBJECTIVE: Mutate core invariants and require test detection
- UPSTREAM FILES TO READ: 13,14
- REQUIRED PREDECESSORS: PKG-30
- PUBLIC INTERFACES: mutation runner
- DATABASE CHANGES: none
- TESTS REQUIRED: T11
- PROOF CLAIMS: P-01..P-25
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof
### PKG-32: Recursive regression and proof report

- BUILD_PHASE: 14
- OBJECTIVE: Dependency-driven regression and implementation proof report
- UPSTREAM FILES TO READ: 13,14
- REQUIRED PREDECESSORS: PKG-31
- PUBLIC INTERFACES: proof report
- DATABASE CHANGES: none
- TESTS REQUIRED: T12
- PROOF CLAIMS: P-01..P-25
- FORBIDDEN SHORTCUTS: direct persistence, inferred authority, projection truth, AI authority, admin fallback, semantic TODOs
- STOP CONDITIONS: unresolved required authority/transition/Evidence rule, Workspace ambiguity, hard dependency required, CommitUnit atomicity failure, security boundary unenforceable
- ACCEPTANCE: targeted tests and affected recursive tests PASS with reconstructable proof

---

## 47. CODING PACKAGE DAG

```text
PKG-00
  -> PKG-01
      -> PKG-02
          -> PKG-03
          -> PKG-04
      -> PKG-05
          -> PKG-06
              -> PKG-07
                  -> PKG-08
                      -> PKG-09
                          -> PKG-10
                              -> PKG-11
                              -> PKG-12
                                  -> PKG-13
                                      -> PKG-14
                                      -> PKG-15
                                      -> PKG-16
                                          -> PKG-17
                                              -> PKG-18
                                                  -> PKG-19
                                      -> PKG-20
                                          -> PKG-21
                                      -> PKG-22
                                          -> PKG-23
                                              -> PKG-24
                                      -> PKG-25
                                          -> PKG-26
                                      -> PKG-27
PKG-21 + PKG-26 -> PKG-28
PKG-15 + PKG-19 + PKG-28 -> PKG-29
PKG-24 + PKG-26 + PKG-29 -> PKG-30
PKG-30 -> PKG-31 -> PKG-32
```

Parallelization is permitted only after shared semantic predecessors are frozen for that phase. Authority, governance and CommitUnit packages are not developed against invented temporary contracts.

---

## 48. FILE-LEVEL IMPLEMENTATION MAP

Representative exact file tree follows. 15 may split a package into multiple prompts but may not relocate semantics without updating this map.

| File | Purpose | Source | Allowed imports | Forbidden imports | Test | Phase |
|---|---|---|---|---|---|---|
| `packages/semantic_types/ids.py` | strong IDs | 02,09,14 | stdlib | infrastructure | `tests/semantic/test_ids.py` | 0 |
| `packages/semantic_types/versions.py` | versions/contracts | 09,14 | stdlib | infrastructure | `tests/semantic/test_versions.py` | 0 |
| `packages/domain/session.py` | Session state | 02,03 | semantic_types | DB/HTTP | `tests/domain/test_session.py` | 2 |
| `packages/domain/question.py` | Question identity/original | 02,03 | semantic_types | DB/AI | `tests/domain/test_question.py` | 2 |
| `packages/domain/burst.py` | Burst state/freeze | 03,06 | domain types | provider SDK | `tests/domain/test_burst.py` | 2 |
| `packages/domain/transitions.py` | TransitionSpec registry | 03 | domain | controllers | `tests/transitions/test_registry.py` | 2 |
| `packages/governance/models.py` | membership/HABB | 04,05 | semantic_types | UI/AI | `tests/governance/test_models.py` | 1 |
| `packages/governance/commands.py` | governed mutations | 05,09 | command contracts | direct DB | `tests/governance/test_commands.py` | 1/4 |
| `packages/authority/resolver.py` | current authority | 04,05 | governance/domain ports | projection/UI claims | `tests/authority/test_resolver.py` | 1 |
| `packages/boundaries/types.py` | BoundaryProof | 06 | semantic_types | HTTP | `tests/boundaries/test_types.py` | 3 |
| `packages/boundaries/registry.py` | BND registry | 06 | boundary evaluators | provider SDK | `tests/boundaries/test_registry.py` | 3 |
| `packages/boundaries/bnd_014_commit.py` | fresh commit gate | 06,09 | authority/evidence canonical ports | projection | `tests/boundaries/test_bnd014.py` | 4 |
| `packages/evidence/models.py` | Evidence semantics | 07 | semantic_types | AI SDK | `tests/evidence/test_models.py` | 6 |
| `packages/evidence/provenance.py` | provenance envelope/lineage | 07 | semantic_types | authority invention | `tests/evidence/test_provenance.py` | 6 |
| `packages/evidence/freshness.py` | commit Evidence proof | 07,09 | canonical ports | projection | `tests/evidence/test_freshness.py` | 6 |
| `packages/command/envelope.py` | CommandEnvelope | 09 | semantic_types | HTTP | `tests/command_commit_event/test_command.py` | 4 |
| `packages/command/registry.py` | semantic Command catalogue | 09,14 | command/domain contracts | ORM | `tests/command_commit_event/test_registry.py` | 4 |
| `packages/commit/coordinator.py` | CommitUnit transaction | 05,06,09,10 | boundaries/persistence ports | provider SDK | `tests/command_commit_event/test_commit.py` | 4 |
| `packages/commit/idempotency.py` | idempotency lifecycle | 09,10 | command/persistence ports | retry guess | `tests/command_commit_event/test_idempotency.py` | 4 |
| `packages/audit/models.py` | AuditEvent | 09,11 | semantic_types | domain mutation | `tests/command_commit_event/test_audit.py` | 4 |
| `packages/events/envelope.py` | EventEnvelope | 09 | semantic_types | Command execution | `tests/command_commit_event/test_event.py` | 8 |
| `packages/events/outbox.py` | outbox contract | 09 | persistence port | domain retry | `tests/command_commit_event/test_outbox.py` | 4/8 |
| `packages/projection/consumer.py` | projection only | 06,09 | Event/projection port | canonical writer | `tests/command_commit_event/test_projection.py` | 8 |
| `packages/ai_contracts/aiop.py` | AIOP contracts | 08 | semantic_types | provider SDK | `tests/ai/test_aiop.py` | 7 |
| `packages/ai_gateway/context.py` | allowlisted manifest | 08,11 | evidence read ports | whole Workspace dump | `tests/ai/test_context.py` | 7 |
| `packages/ai_gateway/prompt.py` | prompt version/layers | 08 | ai contracts | authority | `tests/ai/test_prompt.py` | 7 |
| `packages/ai_gateway/validator.py` | AI_VALIDATION_PROOF | 08 | ai contracts | Evidence promotion | `tests/ai/test_validator.py` | 7 |
| `packages/ai_gateway/adapters/providers/mock.py` | deterministic mock | 12,13 | provider port | canonical writer | `tests/ai/test_mock_provider.py` | 7 |
| `packages/recovery/certainty.py` | consequence certainty | 10 | proof repositories | telemetry-only truth | `tests/recovery/test_certainty.py` | 9 |
| `packages/recovery/lpvs.py` | LPVS | 10 | authoritative histories | latest-row heuristic | `tests/recovery/test_lpvs.py` | 9 |
| `packages/recovery/service.py` | governed recovery | 10 | command/boundary/commit | unrestricted DB | `tests/recovery/test_service.py` | 9 |
| `packages/security/identity.py` | human/service identity | 11 | semantic_types | domain authority | `tests/security/test_identity.py` | 10 |
| `packages/security/workspace.py` | security Workspace enforcement | 11 | identity | projection truth | `tests/security/test_workspace.py` | 10 |
| `packages/security/events.py` | SecurityEvent | 11 | semantic_types | domain writer | `tests/security/test_events.py` | 10 |
| `packages/observability/context.py` | correlation | 11 | semantic_types | authority tokens | `tests/security/test_observability.py` | 10 |
| `packages/test_support/nonproof_bootstrap.py` | NON_PROOF fixture | 12,13 | test DB adapter | production imports | fixture tests | 1 |
| `packages/test_support/failure_injector.py` | deterministic failure hooks | 13,14 | test contracts | production imports | failure tests | 4+ |
| `packages/test_support/concurrency.py` | deterministic barriers | 13,14 | test contracts | production imports | concurrency tests | 4+ |
| `apps/api/src/nquiry_api/http/commands.py` | HTTP dispatch only | 09,14 | application contracts | ORM/provider SDK | API tests | 4+ |
| `apps/api/src/nquiry_api/http/queries.py` | Query dispatch | 09,14 | Query ports | mutation | API tests | 4+ |
| `apps/web/app/...` | minimum proof UI | 12,14 | typed HTTP client | backend internals | Playwright | 11 |

Every package-specific file created by 15 must inherit the ownership and forbidden dependency rules above.

---

## 49. DATABASE IMPLEMENTATION MAP

Semantic source-derived fields are marked `S`; physical choices `I`.

Key patterns:

- UUID-compatible primary IDs: `I`, identity semantics: `S`.
- `workspace_id` on protected records: `S`.
- `record_version bigint >= 1`: `I` materializing approved version semantics `S`.
- timestamps `timestamptz`: `I`.
- provenance JSONB envelope: `I`, provenance semantics `S`.
- append-only privilege strategy: `I`, audit/history preservation `S`.
- RLS: `I`, Workspace hard isolation requirement `S`.

Critical foreign keys use `(workspace_id, id)` composite uniqueness where needed to prevent cross-Workspace endpoint references.

No cascading delete is enabled for audit/provenance-critical records without an approved deletion policy. Default is restrictive foreign-key behavior.

---

## 50. TEST IMPLEMENTATION MAP FOR P-01 THROUGH P-25

| Claim | Primary test file | Fixture/attack | Expected proof |
|---|---|---|---|
| P-01 | `tests/domain/test_question.py` | create/read stable identity | canonical QuestionId |
| P-02 | same | overwrite original_text | rejected/no changed canonical version |
| P-03 | `tests/domain/test_burst.py` | mutate frozen set | immutable membership proof |
| P-04 | `tests/ai/test_burst_ai_block.py` | AI during ACTIVE Human-only | BND-008 DENY |
| P-05 | `tests/ai/test_post_burst_analysis.py` | pre/post freeze analysis | post-freeze AIGeneration only |
| P-06 | `tests/ai/test_canonical_effect.py` | AI output mutation attempt | derived artifact only |
| P-07 | `tests/authority/test_ai_non_authority.py` | AI sets DECIDED | BND-006 DENY |
| P-08 | `tests/authority/test_question_selection.py` | AI/no-right selection | exact QUESTION_SELECTION_RIGHT proof |
| P-09 | `tests/e2e/test_ai_decision_boundary.py` | recommendation persistence | Decision remains UNDER_CONSIDERATION |
| P-10 | `tests/authority/test_current_authority.py` | no current binding | DENY/no commit |
| P-11 | `tests/authority/test_stale_authority.py` | revoke after prepare | BND-014 DENY |
| P-12 | `tests/governance/test_executable_binding.py` | policy text/role only | no authority |
| P-13 | `tests/boundaries/test_monotonic_deny.py` | downstream ALLOW after DENY | no consequence |
| P-14 | `tests/evidence/test_consumption_proof.py` | consumed Evidence set | versioned reconstruction |
| P-15 | `tests/evidence/test_noncollapse.py` | confidence as Evidence | rejected |
| P-16 | `tests/command_commit_event/test_command_event_split.py` | Event submitted as Command | rejected |
| P-17 | `tests/command_commit_event/test_replay.py` | replay | projection only |
| P-18 | `tests/security/test_direct_write.py` | app/worker direct write | technical reject or illegitimate tamper detection |
| P-19 | `tests/command_commit_event/test_idempotency.py` | duplicate COMMITTED | one consequence |
| P-20 | `tests/recovery/test_indeterminate.py` | timeout/unknown commit | blind retry blocked |
| P-21 | `tests/recovery/test_non_authority.py` | RecoveryRecord/admin authority | denied |
| P-22 | `tests/security/test_workspace_isolation.py` | A references B | DENY, no provider leak |
| P-23 | `tests/security/test_ai_gateway.py` | direct provider import/path | unavailable/security signal |
| P-24 | `tests/security/test_admin_non_authority.py` | admin/root decides | no legitimate transition |
| P-25 | `tests/proof/test_reconstruct_consequence.py` | committed Decision path | full actor/authority/state/Evidence/boundary/commit/audit/event chain |

Bootstrap legitimacy test remains `TEST_BLOCKED_BY_UPSTREAM_GAP`.

Real-provider eligibility test remains `TEST_BLOCKED_BY_UPSTREAM_GAP`.

---

## 51. CI PIPELINE

Order:

1. format
2. lint
3. typecheck
4. architecture dependency tests
5. provider SDK import restriction
6. test-only import restriction
7. migration validation
8. T0 semantic tests
9. T1 domain tests
10. T2 transitions
11. T3 authority/governance
12. T4 boundaries
13. T5 Evidence/provenance
14. T6 AI contracts with MockProvider
15. T7 Command/Commit/Event
16. T8 recovery
17. T9 security/isolation
18. T10 E2E architectural proof
19. T11 mutation
20. T12 recursive regression
21. proof report generation

CI reports blocked mandatory dependencies separately. Green executable tests do not convert blocked bootstrap/provider eligibility into PASS.

---

## 52. DEFINITION OF DONE

A package is DONE only if code, semantic types, public contracts, migration where required, targeted tests and affected regressions are complete, proof artifacts reconstruct, forbidden dependency checks pass, and no semantic guess or architecture-critical placeholder remains.

---

## 53. CODEX STOP CONDITIONS

Immediate STOP when:

- required authority undefined
- required transition absent from 03
- required Evidence rule undefined
- Workspace unresolved/conflicting
- provider/privacy eligibility required
- legitimate first bootstrap required
- recovery requires new domain choice
- Export Authority required
- test expectation conflicts with architecture
- upstream files materially contradict
- implementation requires invariant weakening
- CommitUnit atomicity cannot be proven
- claimed security boundary cannot be enforced

Report:

`STOP_REASON`, `SOURCE_FILES`, `CONFLICT`, `AFFECTED_PACKAGE`, `AFFECTED_TESTS`, `MINIMUM_UPSTREAM_DECISION_REQUIRED`.

No workaround.

---

## 54. RECURSIVE CHANGE PROTOCOL

Implementation contradiction:

`STOP -> FIRST AUTHORITATIVE LAYER -> RECONSTRUCT THERE -> PROPAGATE DOWNSTREAM -> UPDATE 14 -> REGENERATE AFFECTED 15 PACKAGES -> RERUN AFFECTED 13 TESTS`.

Never patch only implementation.

---

## 55. FINAL ORDERED IMPLEMENTATION SEQUENCE

| Phase | Packages | Preconditions | Implement | Test/Proof | Human gate |
|---|---|---|---|---|---|
| 0 | PKG-00 | 00-14 available | skeleton/dependency enforcement | T0 structural | YES |
| 1 | PKG-01..04 | Phase 0 | identity/Workspace/governance/nonproof fixture | T3/T9 partial | YES |
| 2 | PKG-05..07 | Phase 1 | domain/Session/Question/Burst | P-01..04 | YES |
| 3 | PKG-08..09 | Phase 2 | boundary engine | T4 | YES |
| 4 | PKG-10..13 | Phase 3 | Command/idempotency/Commit/Audit/Outbox | critical atomic proof | YES |
| 5 | PKG-14..15 | Phase 4 | selection/human Decision | P-07..11 | YES |
| 6 | PKG-16..17 | Phase 5 | Evidence/provenance | P-14..15 | YES |
| 7 | PKG-18..19 | Phase 6 | AI Gateway/mock/derived | P-04..07,P-23 | YES |
| 8 | PKG-20..21 | Phase 7 | Event/projection | P-16..17 | YES |
| 9 | PKG-22..24 | Phase 8 | failure/LPVS/recovery | P-20..21 | YES |
| 10 | PKG-25..27 | Phase 9 | security/identity/RLS/observability | P-18,P-22..25 | YES |
| 11 | PKG-28..29 | Phase 10 | minimum UI | UI architectural proof | YES |
| 12 | PKG-30 | Phase 11 | six E2E paths/TestProofBundle | P-01..25 executable subset | YES |
| 13 | PKG-31 | Phase 12 | mutation/adversarial proof | T11 must detect mutations | YES |
| 14 | PKG-32 | Phase 13 | recursive regression/report | T12 | YES |

---

## 56. NEW IMPLEMENTATION GAPS

### GAP-14-001: Reference Authentication Provider Selection
Status: `[IMPLEMENTATION CHOICE NOT YET BOUND TO VENDOR]`.
The OIDC port is implementable. Concrete production identity provider selection is not required for architectural prototype semantics.

### GAP-14-002: Production Egress Enforcement Mechanism
Status: `[IMPLEMENTATION CHOICE]`.
Local/container prototype can enforce provider path by credential isolation, dependency rules and network topology tests. Production-grade egress mechanism remains deployment-specific.

### GAP-14-003: Audit Tamper-Evidence Strength
Status: `[IMPLEMENTATION CHOICE / 11 DEPENDENCY]`.
Prototype provides append-oriented privilege isolation and integrity checks. It does not claim mathematically immutable storage.

### GAP-14-004: Recovery Algorithm Approval Governance
Status: `[CARRIED FROM GAP-10-005]`.
Only recovery algorithms already unambiguously deterministic under 10 may be implemented. New approval semantics are not invented.

### GAP-14-005: Production Retention/Deletion Materialization
Status: `[CARRIED]`.
Prototype avoids convenience hard-delete and retains proof dependencies.

---

## 57. UPSTREAM GAPS AND PERSISTING HARD DEPENDENCIES

Persisting hard dependencies:

1. `HARD-DEP-001`: legitimate first Workspace governance-root bootstrap.
2. `HARD-DEP-002`: provider/privacy eligibility for exact prototype data class/provider path.

Other carried blockers relevant if exercised:

- Export Authority unresolved, operational export blocked.
- Method Approval Authority unresolved, prototype marks path NOT_EXERCISED.
- automatic Burst timer semantics unresolved, prototype uses authorized manual completion only where upstream permits.
- collaborative QuestionSelection unresolved, prototype uses one explicit selector.
- unresolved global Assumption Evidence sufficiency, not exercised.
- retention/deletion tension remains open.
- external consequential tool recovery contracts remain outside minimum prototype unless exercised.

No implementation default closes any of these.

---

## 58. COMPLETION REPORT

### IMPLEMENTATION ARCHITECTURE VERDICT

`IMPLEMENTATION_ARCHITECTURE::COHERENT`

14 translates 00 through 13 into a concrete reference implementation without creating a parallel semantic or authority architecture.

### REFERENCE STACK
Python 3.13, FastAPI, PostgreSQL 17, Alembic, SQLAlchemy Core, Pydantic v2, Next.js 16/TypeScript, pytest/Hypothesis, Playwright/Vitest, internal AI Gateway with MockProvider, OpenTelemetry API, Docker Compose, GitHub Actions. All are `[IMPLEMENTATION CHOICE]`.

### STACK DECISION RATIONALE
The stack minimizes deployment complexity while preserving explicit transaction semantics, type contracts, dependency tests, Workspace isolation, provider isolation and deterministic falsification.

### REPOSITORY TOPOLOGY
Defined in Sections 3 and 48.

### DEPENDENCY GRAPH
Defined in Sections 4 and 47.

### FORBIDDEN DEPENDENCIES
Explicit static restrictions defined in Sections 4 and 41.

### SEMANTIC TYPE MAP
Defined in Section 5.

### DOMAIN ENUM MAP
Defined in Section 6.

### DATABASE SCHEMA
Defined in Sections 7 and 49.

### DATABASE PRINCIPALS
Defined in Sections 8 and 31.

### MIGRATION PLAN
Defined in Section 9.

### REPOSITORY PORTS
Defined in Section 10.

### COMMAND REGISTRY
Defined in Section 12.

### QUERY REGISTRY
Defined in Section 13.

### BOUNDARY IMPLEMENTATION MAP
Defined in Section 15.

### AUTHORITY IMPLEMENTATION MAP
Defined in Section 16.

### GOVERNANCE IMPLEMENTATION MAP
Defined in Section 17.

### STATE TRANSITION IMPLEMENTATION MAP
Defined in Section 18.

### QUESTION/BURST IMPLEMENTATION
Defined in Section 19.

### QUESTION SELECTION IMPLEMENTATION
Defined in Section 20.

### HUMAN DECISION IMPLEMENTATION
Defined in Section 21.

### EVIDENCE/PROVENANCE IMPLEMENTATION
Defined in Section 22.

### AI GATEWAY IMPLEMENTATION
Defined in Sections 23 and 24.

### AIOP IMPLEMENTATION
Minimum AIOP set defined in Section 23, constrained by approved 08 contracts.

### COMMIT UNIT IMPLEMENTATION
Defined concretely in Section 25.

### CONCURRENCY IMPLEMENTATION
Defined in Sections 26 and 40.

### IDEMPOTENCY IMPLEMENTATION
Defined in Section 27.

### AUDIT/OUTBOX/EVENT IMPLEMENTATION
Defined in Section 28.

### PROJECTION IMPLEMENTATION
Defined in Section 28.

### FAILURE CLASSIFICATION
Defined in Section 29.

### INDETERMINATE IMPLEMENTATION
Defined in Section 29.

### LPVS IMPLEMENTATION
Defined in Section 30.

### RECOVERY IMPLEMENTATION
Defined in Section 30.

### SECURITY IMPLEMENTATION
Defined in Sections 31 through 33.

### WORKSPACE ISOLATION IMPLEMENTATION
Semantic BND-002 plus repository scope, composite constraints and RLS defense-in-depth.

### API IMPLEMENTATION MAP
Defined in Sections 35 and 36.

### FRONTEND IMPLEMENTATION MAP
Defined in Section 37.

### OBSERVABILITY IMPLEMENTATION
Defined in Section 34.

### LOCAL DEVELOPMENT TOPOLOGY
Defined in Section 38.

### TEST HARNESS
Defined in Sections 39 and 50.

### FAILURE INJECTION
Defined in Section 40.

### CONCURRENCY HARNESS
Defined in Section 40.

### SECURITY ATTACK HARNESS
Defined in Section 40.

### CI PIPELINE
Defined in Section 51.

### BUILD PHASES
Defined in Section 44.

### PHASE GATES
Every major phase has an explicit human gate.

### CODING PACKAGE MANIFEST
PKG-00 through PKG-32 defined in Section 46.

### CODING PACKAGE DAG
Defined in Section 47. No package requires a contract from a later package.

### FILE-LEVEL IMPLEMENTATION MAP
Defined in Section 48.

### DATABASE IMPLEMENTATION MAP
Defined in Sections 7, 8, 9 and 49.

### API IMPLEMENTATION MAP
Defined in Section 36.

### TEST IMPLEMENTATION MAP
All P-01 through P-25 mapped in Section 50.

### CODEX STOP CONDITIONS
Defined in Section 53.

### NEW IMPLEMENTATION GAPS
GAP-14-001 through GAP-14-005 defined in Section 56.

### UPSTREAM GAPS
Preserved in Section 57.

### PERSISTING HARD DEPENDENCIES
Both 12/13 hard dependencies remain unresolved.

### ARCHITECTURAL IMPLEMENTATION READINESS
`READY_FOR_15_PROMPT_ARCHITECTURE_AFTER_HUMAN_REVIEW`

This does not authorize coding.

### READINESS FOR 15
`CONDITIONALLY_READY_FOR_15_AFTER_HUMAN_APPROVAL_OF_14`

15 has not been built.

---

## 59. FINAL IMPLEMENTATION-CLOSURE TEST

### QUESTION 1

Could a competent coding agent implement the architectural prototype from 14 plus 00 through 13 without inventing domain, authority, governance, Evidence, AI, failure, security or test semantics?

`YES`, for the explicitly scoped architectural prototype and packages whose upstream dependencies are satisfied.

The two hard dependencies remain explicit blockers for claims requiring legitimate first bootstrap or real-provider eligibility.

### QUESTION 2

Does every consequential write path converge on governed Command, Boundary, BND-014 and CommitUnit architecture?

`YES`.

No normal consequential write port exists outside that path.

### QUESTION 3

Can AI, admin, worker, Event consumer, projection service, recovery service, frontend or direct application code create legitimate canonical consequence outside that path?

`NO`.

Infrastructure root may physically tamper with bytes, as 11 and 13 already distinguish. Such tampering does not become a legitimate governed transition and must be detected/reconstructed.

### QUESTION 4

Can every P-01 through P-25 claim be mapped to concrete implementation files, fixtures, tests and proof artifacts?

`YES`.

Section 50 provides the primary mapping, with package and file maps supplying implementation ownership.

### QUESTION 5

Can every coding package be implemented without requiring a contract from a later unbuilt package?

`YES`.

The DAG orders semantic prerequisites before consumers. Parallel work is allowed only after shared contracts are fixed.

### QUESTION 6

Are unresolved upstream gaps still explicit rather than hidden behind implementation defaults?

`YES`.

Workspace bootstrap and provider/privacy eligibility remain hard dependencies. Export remains blocked. Method Approval, timer automation, global Evidence sufficiency and retention/deletion are not silently closed.

---

## 60. STOP GATE

`14_IMPLEMENTATION_SEQUENCE.md` is complete for human review.

`15_AI_CODING_PROMPTS`: NOT BUILT.

APPLICATION CODE: NOT WRITTEN.

WORKSPACE BOOTSTRAP: NOT SILENTLY RESOLVED.

PROVIDER/PRIVACY ELIGIBILITY: NOT SILENTLY RESOLVED.

EXPORT AUTHORITY: NOT IMPLEMENTED.

ARCHITECTURE BASELINE: NOT FROZEN.

`STATUS::READY_FOR_HUMAN_REVIEW`
