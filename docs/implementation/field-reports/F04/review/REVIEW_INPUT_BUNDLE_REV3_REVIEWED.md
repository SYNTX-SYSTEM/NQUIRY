# F04 ARCHITECTURE REVIEW — INPUT BUNDLE

Persistent review provenance for the F04 architecture review. This bundle
is a verbatim copy; it creates no semantics. Where it and a source file ever
differ, the source file wins.

| Property | Value |
|---|---|
| Created | 2026-09-24T20:37:13Z |
| Worktree | `.claude/worktrees/local-login-auth` |
| HEAD | `c9d86bab64505845f406ba43a8c78ac185383680` (= `origin/master`, published F03 identity commit) |
| Published F03 | `0d59ae3`, tag `field-F03` |
| Review status | READY_FOR_F04_ARCHITECTURE_REVIEW |
| Open, non-blocking, not altered here | H-7 (stale F03 publication records); H-8 (SF-01 committed locally, unpublished) |
| Git state | nothing staged, committed, tagged or pushed |

## Source files and checksums (sha256 at bundle time)

| Part | Source | Lines | sha256 |
|---|---|---|---|
| full content | `docs/implementation/field-reports/F04/F04_ARCHITECTURE_RECONSTRUCTION.md` | 755 | `9ef3c07643bb00cc…` |
| full content | `docs/implementation/field-reports/F04/HUMAN_DECISIONS.md` | 232 | `531356b913c59485…` |
| full content | `docs/implementation/field-reports/F04/STATUS.md` | 39 | `5e4ad3106c71f931…` |
| proposed F04 changes (diff vs HEAD) | `docs/architecture/16_DECISION_GAP_REGISTER.md` | +143 / -0 | working copy `d2c226705076a878…` |
| proposed F04 changes (diff vs HEAD) | `docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md` | +40 / -0 | working copy `1a1b3de0e3f4814e…` |


================================================================================
BEGIN FILE: docs/implementation/field-reports/F04/F04_ARCHITECTURE_RECONSTRUCTION.md  (complete current content)
================================================================================

# F04 ARCHITECTURE RECONSTRUCTION — AI BOUNDARY · POST-BURST SENSEMAKING

**Revision 3 (2026-09-24).** This revision incorporates the human operator's
answers to C3-F04-1..6 (HD-16..HD-22, revision 2) and to C3-F04-7 (HD-23,
revision 3). Revision 1 held the same analysis with the decisions open. The
options as posed are preserved verbatim in `HUMAN_DECISIONS.md`.

Mode: architecture only. No implementation, no schema change, no code.
F03 and SF-01 are not modified. Nothing staged, committed, tagged or pushed.

**Baseline** (verified):
- `origin/master` = `c9d86ba`.
- `field-F03` is a signed annotated tag (good signature) resolving to
  `0d59ae3`.
- Worktree `.claude/worktrees/local-login-auth` is at `c9d86ba`.

**Sources.** The authoritative architecture is 03, 04, 06, 07, 08, 09, 10,
11, 12, 13, 16, 19 and 20, with the published F03 reports. Code is
evidence, never authority (20 §0).

**FINAL STATUS: READY_FOR_F04_ARCHITECTURE_REVIEW.**
- All seven F04 Case-3 decisions are closed: C3-F04-1..6 by HD-16..HD-22,
  and C3-F04-7 (the AIOP-002 trigger, surfaced by HD-21) by HD-23.
- No F04 Case-3 relation remains open.
- H-7 (stale F03 publication records) stays open and non-blocking.

---

## 0. Human decisions incorporated

| HD | Ledger | Question | Decision |
|---|---|---|---|
| HD-16 | NQ-DEC-044 / REC-018 | C3-F04-1: who may start AIOP-001 | **(b)** A committed CMD_BEGIN_ANALYSIS authorizes **exactly one** AIOP-001 run, executed by the system right after that commit. Re-runs after a failure need an explicit controller request |
| HD-17 | NQ-DEC-045 / REC-019 | C3-F04-2: authority source for system acceptance / invocation | **(a)** A fifth typed effect-gate source, **SYSTEM_OPERATION**. It references the authorizing human command, is scoped `SESSION:<id>`, and is re-checked at commit |
| HD-18 | NQ-DEC-046 / REC-020 | C3-F04-3: analysis content | **(b)** Classification proposals, Question families, unusual-question flags, pattern descriptions and contradiction proposals. **No** additional Question suggestions. **`normalized_text` is not written in F04** |
| HD-19 | NQ-DEC-047 / REC-021 | C3-F04-4: the runtime model | **(b)** MockProvider enabled in the dev runtime. Every AI run and result is marked mock and projected as NON_PROOF / MOCK, never as analysis of the real Questions |
| HD-20 | NQ-DEC-048 / REC-022 | C3-F04-4, supplement | A mock-validated proof **must never** count toward F05 BEGIN_REFLECTION for a non-fixture Session |
| HD-21 | NQ-DEC-049 / REC-023 | C3-F04-5: AIOP scope | **(b)** AIOP-001 + AIOP-002 (question clustering). Assumptions (AIOP-004), perspectives and AI-origin Questions are out |
| HD-22 | NQ-DEC-050 / REC-024 | C3-F04-6: who sees derived analysis | **(a)** Every member who can read the frozen set (the HD-13 audience) |
| HD-23 | NQ-DEC-051 / REC-026 | C3-F04-7: what triggers AIOP-002 | **(c)** One AIOP-002 run becomes authorized only after an accepted AIOP-001 artifact exists. Execution is SYSTEM_OPERATION, referencing the same BEGIN_ANALYSIS authority chain. If AIOP-001 fails or is not accepted, clustering must not run. If AIOP-002 itself fails, any retry requires an explicit controller request |

**Reconciliation.**
- Recorded in `16_DECISION_GAP_REGISTER.md`: §6 table, YAML, §41
  REC-018..REC-027 (REC-025 and REC-027 are the count records).
- Recorded in `20_SYSTEM_FIELD_ENGINEERING.md`: §7 successor note
  (SYSTEM_OPERATION, *decided, not yet materialized*), §15B.
- The published ledgers permitted this without conflict. The identifiers
  continue the published sequence (NQ-DEC-043 → 044, REC-017 → 018,
  HD-15 → 16), and every edit is additive.
- Architecture home-file pointers (04 AUTH-DEP-SESS-006, 06 BND-010,
  08 §23/§24, 09 §68) are due when each decision is materialized
  (WU-04.0 / the owning WU), as F03 did for 04 §40.

**Readings this revision records** (derived from the decisions; flagged for
the architecture review):
- **R1 (HD-16).** The system-executed run carries **no SYSTEM_DERIVED
  authority**.
  - Its authority is the committed human BEGIN_ANALYSIS command, recorded as
    SYSTEM_OPERATION (HD-17).
  - BND-011/012 (method-derived authority, D8) are therefore not consulted
    and stay REQUIRE/DENY for any genuinely automatic path.
  - The run is not an automatic *Session* authority (HD-1): it changes no
    Session state.
- **R2 (HD-16).** Nothing authorizes a **re-run after a successful
  (VALIDATED and accepted) run**. Absent authority means denial, so each
  Session has **at most one accepted AIOP-001 artifact**. This also removes
  the open "current cluster run" question (NQ-GAP-010) for the prototype.
- **R3 (HD-16).** The BEGIN_ANALYSIS authorization is **consumed** by the
  first generation that references it. If none was ever created (the
  process stopped between commit and invocation), the authorization is
  unconsumed and the controller's explicit request may execute it. This is
  within the more conservative human-act envelope.
- **R4 (HD-19).** A MockProvider run never discloses Workspace data to any
  external party: the mock adapter has no egress. 11 AC-11-011 (provider
  disclosure DENY without eligibility) is therefore not engaged.
  - **Production must not enable the mock** (19 §40, line 2786: "Do not silently
    substitute MockProvider"). Enablement is a dev-runtime configuration
    only.
- **R5 (HD-20).** HD-20 states a prohibition only. It does **not** state
  that a mock proof *may* count for a fixture Session; F05 decides that.
  - Consequence: in a mock-only runtime, **no governed Session can ever
    satisfy BEGIN_REFLECTION**.
  - REFLECTION for governed Sessions needs a real eligible provider
    (HARD-DEP-002) or a future decision on NQ-GAP-024.
- **R6 (HD-22).** The analysis audience equals the HD-13 frozen-set
  audience, evaluated server-side by the same read chain. The mock marker
  is part of what every viewer sees.
- **R7 (HD-23).** The automatic clustering run records SYSTEM_OPERATION with
  **reference = the BEGIN_ANALYSIS command** (the "same BEGIN_ANALYSIS
  authority chain"). The accepted AIOP-001 artifact is a **commit-time
  precondition** and is recorded as the authorizing link in the generation
  / manifest provenance.
  - This holds whether that artifact came from the original authorized run
    or from a controller re-run (HD-16). The chain is BEGIN_ANALYSIS →
    [controller re-run request] → accepted artifact → clustering
    authorization.
  - A controller re-run of clustering (after an AIOP-002 failure) records
    SYSTEM_OPERATION referencing that controller request command.
- **R8 (HD-23).** Nothing authorizes a clustering re-run after an
  **accepted** cluster run. So each Session has **at most one accepted
  cluster run** (one `cluster_run_id`). NQ-GAP-010 ("which run is current")
  therefore does not arise in the prototype.
- **R9 (HD-23).** The clustering authorization is **consumed** by the first
  AIOP-002 generation that references it. If the process stops between the
  AIOP-001 acceptance commit and the AIOP-002 generation, the authorization
  is unconsumed and the controller's explicit request may execute it (the
  same conservative envelope as R3).
- **R10 (HD-23).** The AIOP-001 artifact **authorizes** clustering. It is
  **not model input**: AIOP-002's input stays the verified frozen human set
  (08 §24: "Question IDs/versions, frozen set"). AI-derived content never
  feeds a second AI operation in F04, so cluster lineage stays human-sourced.

## 1. F04 current-state reconstruction (published F03 terminal state)

| Relation | Published truth | Home |
|---|---|---|
| Session | `QUESTION_CAPTURE` ("input is closed … raw set frozen … eligible to consider post-burst analysis") | 03 §13.3 |
| Burst | `COMPLETED`, HUMAN_ONLY; `UNIQUE(session_id)` | migration `e5a1b3c8f204` |
| Frozen human source | membership immutable, frozen after COMPLETED. Fingerprint `NQ-FROZEN-SET-V2` over immutable birth facts only. `verify_frozen_set` recomputes it | `domain/burst_membership.py`, `application/frozen_set.py` |
| Questions | HUMAN origin, author, trigger-immutable `original_text`. `normalized_text` NULL and writable, **but not written in F04 (HD-18)** | migration `33e1d1feed5b` |
| Provenance | completion: BINDING `SESSION:<id>`, `session:QUESTION_CAPTURE\|burst:COMPLETED`; capture: PARTICIPATION, `question:<id>\|burst:ACTIVE` | F03 code |
| Effect-gate sources | BINDING, ROLE, FOUNDING, PARTICIPATION (published). **SYSTEM_OPERATION decided (HD-17), not materialized** | 20 §7 |
| Projection | `questionSet FULL_FROZEN_SET` with `frozen.verified`; no BEGIN_ANALYSIS action | `inquiry_queries.session_position` |
| TRN-SESS-006 | in the registry; no handler, route, UI or test | `domain/session_transitions.py` |
| AI machinery | Gateway (sync, MockProvider only, **writes artifacts itself**), 16 AIOP ids without schemas, `ai_generations` / `ai_derived_artifacts` / `ai_context_manifests`, BND-009 / BND-010. Tests only. No QuestionCluster table | code |
| Ledger | after this revision: 50 decisions (41 ESTABLISHED, 9 REQUIRED), 80 gaps | 16 §41 REC-025 |

**Inherited open relations:**
- NQ-GAP-024 (no way out of ANALYSIS when AI fails; F05).
- NQ-GAP-003.
- HARD-DEP-002 (real provider).
- D2 / D3 / D8 / D9.
- H-7 (stale F03 records).

## 2. Parent Field and child Field definition

- **Parent chain:** SFE (20) → product architecture (00–18 + 16) → F03
  (published). F04 inherits the frozen human source as an **immutable input
  relation**. It may read and verify it; it never writes it. HD-18 also
  keeps `normalized_text` untouched.
- **F04 (19 §24):** "FROZEN HUMAN QUESTION FIELD → DERIVED RELATIONAL FIELD."
- **Material Delta F04 owns:**
  1. the Session phase change QUESTION_CAPTURE → ANALYSIS;
  2. governed AIOP-001 and AIOP-002 invocation over exactly the frozen set;
  3. operational AI records (manifest, generation, **persisted** validation
     proof);
  4. SYSTEM_OPERATION-sourced acceptance of validated derived output
     (analysis artifact; QuestionCluster + memberships);
  5. projections with explicit AI origin and the MOCK / NON_PROOF marker.
- **F04 must not:**
  - write human source;
  - create a domain Thing without a 09 contract;
  - produce AI-origin Questions, Assumptions or Perspectives;
  - create authority from AI output;
  - advance the Session beyond ANALYSIS.

## 3. Relational map

```text
Session(QUESTION_CAPTURE) ──HAS──► Burst(COMPLETED, fingerprint F) ──CAPTURED──► Question[HUMAN] ×n (immutable)
   │
   └─CMD_BEGIN_ANALYSIS  (controller; BINDING SESSION:<id>)  ─commit─►  Session(ANALYSIS)
          │  authorizes exactly one AIOP-001 run (HD-16) → consumed by the first generation referencing it (R3)
          ▼  system executes, immediately after commit
      CMD_AI_QUESTION_ANALYSIS   actor SYSTEM_SERVICE   source SYSTEM_OPERATION(ref = BEGIN_ANALYSIS command)
          │  BND-007(ANALYSIS) → BND-008(COMPLETED, verified F) → BND-009(contract, manifest, Gateway only)
          ▼
      AIContextManifest (immutable; inputs = burst:<id> + F + question ids + original_text digests)
          ▼ AI Gateway → MockProvider (dev runtime, HD-19) → validator (closed HD-18 schema)
      AIGeneration → VALIDATED | REJECTED | FAILED   +  AI_VALIDATION_PROOF (persisted, immutable)
          ▼ candidate (not an effect)
      CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT  actor SYSTEM_SERVICE  source SYSTEM_OPERATION  BND-010 → BND-014
          ▼
      Derived analysis artifact (AI origin, provider=mock, NON_PROOF) — at most one accepted per Session (R2)

   [after a FAILED/REJECTED AIOP-001 run]  controller: CMD_REQUEST_QUESTION_ANALYSIS (BINDING) → new generation, retry_of lineage
   [AIOP-002, HD-23]  only after an ACCEPTED AIOP-001 artifact exists (no clustering if AIOP-001 fails or is not accepted):
               system runs exactly one CMD_AI_QUESTION_CLUSTERING  actor SYSTEM_SERVICE
                  source SYSTEM_OPERATION(ref = BEGIN_ANALYSIS command; precondition link = accepted AIOP-001 artifact)
                  input = verified frozen set only (R10)
               → generation + proof → CMD_ACCEPT_CLUSTERING_OUTPUT (SYSTEM_OPERATION; BND-010 → BND-014)
               → QuestionCluster + memberships (one cluster_run_id) — at most one accepted cluster run per Session (R8)
   [after a FAILED/REJECTED AIOP-002 run]  controller: CMD_REQUEST_QUESTION_CLUSTERING (BINDING) → new generation, retry_of lineage
   Projection (HD-22 audience): human Questions primary; derived field marked AI · DERIVED/PROPOSAL · MOCK/NON_PROOF
```

These relations must **not** exist:
- AI output → Question / membership / fingerprint mutation;
- AI output → Session advance;
- AI output → selection, Decision, Evidence or Assumption;
- a mock proof → REFLECTION eligibility for a non-fixture Session (HD-20);
- provider → canonical table;
- worker → provider.

## 4. State / transition map

| Object | Transition | In F04 | Rule |
|---|---|---|---|
| Session | TRN-SESS-006 QUESTION_CAPTURE → ANALYSIS | **yes** | 03 TRN-SESS-006: Burst COMPLETED, frozen set proven, `original_text` invariants, no unresolved capture. A failed transition leaves QUESTION_CAPTURE |
| Session | ANALYSIS → ANALYSIS (AI work, acceptance) | **yes** | 03 §26 / §47.8 state-preserving; no commit writes a `session:*` after-state except BEGIN_ANALYSIS (EC-2) |
| Session | TRN-SESS-007 → REFLECTION | **no (F05)** | needs AI_VALIDATION_PROOF; **mock proofs excluded for non-fixture Sessions (HD-20)**; NQ-GAP-024 |
| AIGeneration | REQUESTED → RUNNING → OUTPUT_RECEIVED → VALIDATED \| REJECTED \| FAILED | **yes** | 08 §14-15; DB trigger. A retry is a new id with `retry_of` |
| AI_VALIDATION_PROOF | VALIDATED / REJECTED / INDETERMINATE | **yes, persisted** | 07 §4, 09 §56. INDETERMINATE → generation FAILED (validation infrastructure failure, 08:731-740) |
| BEGIN_ANALYSIS authorization | unconsumed → consumed | **yes** | R3: consumed by the first generation referencing the command |
| Clustering authorization | absent → authorized (at the AIOP-001 acceptance commit) → consumed (first AIOP-002 generation) | **yes** | HD-23; R9. Never authorized while no accepted AIOP-001 artifact exists |
| QuestionCluster run | absent → accepted (one `cluster_run_id`) | **yes (WU-04.9)** | 09 §34/§35; at most one accepted run per Session (R8) |
| Burst / Question / membership / fingerprint | none | **forbidden** | STATE-INV-04/05 |

Resolved conflict C1: 12 §10 lists `QUESTION_GENERATION -> ANALYSIS`; 03
governs, and that transition is illegal.

## 5. Authority map (final)

| Operation | Actor | Authority | Effect-gate source | Re-checked at commit |
|---|---|---|---|---|
| CMD_BEGIN_ANALYSIS | human | `SESSION_CONTROL_RIGHT` at `SESSION:<id>` (04 AUTH-DEP-SESS-006 human path + HD-1). The System path is REQUIRE/DENY (D8) | BINDING | binding, Session QUESTION_CAPTURE, frozen set verified |
| CMD_AI_QUESTION_ANALYSIS (the authorized run) | SYSTEM_SERVICE | the committed BEGIN_ANALYSIS (HD-16), unconsumed (R3) | **SYSTEM_OPERATION** (ref = BEGIN_ANALYSIS command id) | that command committed; Session still ANALYSIS; authorization unconsumed; no accepted AIOP-001 artifact (R2) |
| CMD_REQUEST_QUESTION_ANALYSIS (re-run) | human controller | `SESSION_CONTROL_RIGHT` at SESSION. Allowed only when the latest AIOP-001 generation is terminal FAILED / REJECTED, or the authorization is unconsumed (R3), and no accepted artifact exists (R2) | BINDING | binding; state predicates |
| system execution of that re-run | SYSTEM_SERVICE | the committed re-run request | SYSTEM_OPERATION (ref = request command id) | as above |
| CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT | SYSTEM_SERVICE | HD-17 | SYSTEM_OPERATION (ref = the authorizing human command of that generation) | authorizing command committed; Session ANALYSIS; generation VALIDATED; persisted proof VALIDATED; the generation belongs to this authorization; no prior acceptance |
| CMD_AI_QUESTION_CLUSTERING (the authorized run) | SYSTEM_SERVICE | **HD-23**: one run, authorized only once an accepted AIOP-001 artifact exists | **SYSTEM_OPERATION** (ref = BEGIN_ANALYSIS command; the accepted artifact is the precondition link, R7) | BEGIN_ANALYSIS committed; Session ANALYSIS; an accepted AIOP-001 artifact exists for this Session; clustering authorization unconsumed; no accepted cluster run (R8) |
| CMD_REQUEST_QUESTION_CLUSTERING (re-run) | human controller | `SESSION_CONTROL_RIGHT` at SESSION. Allowed only when an accepted AIOP-001 artifact exists, the latest AIOP-002 generation is terminal FAILED / REJECTED or the authorization is unconsumed (R9), and there is no accepted cluster run (R8) | BINDING | binding; state predicates |
| system execution of that re-run | SYSTEM_SERVICE | the committed clustering re-run request | SYSTEM_OPERATION (ref = request command id) | as above |
| CMD_ACCEPT_CLUSTERING_OUTPUT | SYSTEM_SERVICE | HD-17 | SYSTEM_OPERATION | as for analysis acceptance |
| AI_PROCESSOR | — | never an authority; no self-invocation (04, BND-009) | — | — |

**SYSTEM_OPERATION contract** (HD-17, to be materialized in WU-04.3 / 04.5):
- **Reference:** a committed human command id (BEGIN_ANALYSIS or a
  controller request).
- **Scope:** `SESSION:<id>`.
- **Actor:** must be SYSTEM_SERVICE. A human or AI_PROCESSOR actor → DENY.
- **Commit-time checks:** re-read the referenced command's COMMITTED
  outcome, its Workspace and Session, and the operation-specific predicates
  above.
- **Not reusable:** no ALLOW is carried between operations.
- **Never** a SYSTEM_DERIVED method authority (R1).
- **Audit CHECK:** extended by migration.
- **20 §7:** successor note written now (decided / not materialized).

## 6. Boundary map (final)

- **BEGIN_ANALYSIS:** BND-001 → 002 → 003 → 005 (BINDING `SESSION:<id>`) →
  007 (TRN-SESS-006) → 008 (COMPLETED; `verify_frozen_set` matches) →
  blockers (`UNRESOLVED_CAPTURE`, `FROZEN_SET_UNVERIFIED`) → 014 BINDING.
- **Authorized AIOP-001 run (system):** SYSTEM_SERVICE identity → 002 →
  **SYSTEM_OPERATION check** → 007 (Session ANALYSIS) → 008 (COMPLETED,
  verified F; **the AI category is denied while ACTIVE/PAUSED for any
  requester**, FBR-F04-3) → 009 (contract AIOP-001 approved and registered;
  manifest Workspace; Gateway only; requester ≠ AI_PROCESSOR) → Gateway →
  validator → persisted proof.
- **Acceptance:** 010 (generation VALIDATED; proof VALIDATED; same
  Workspace; output type ∈ HD-18; no human attribution; no implicit state
  advance) → 014 SYSTEM_OPERATION → 015 (coordinator audit).
- **Re-run request:** 001-003 → 005 BINDING → 007 → predicates (R2/R3) →
  014 BINDING. Its execution follows the system run path with
  SYSTEM_OPERATION.
- **AIOP-002 (HD-23):** SYSTEM_SERVICE identity → 002 → **SYSTEM_OPERATION
  check** (BEGIN_ANALYSIS committed; **an accepted AIOP-001 artifact exists
  for this Session**; authorization unconsumed; no accepted cluster run) →
  007 (Session ANALYSIS) → 008 (COMPLETED, verified F) → 009 (AIOP-002
  contract; manifest = frozen set only) → Gateway → validator → persisted
  proof → acceptance 010 → 014 SYSTEM_OPERATION → 015 (08 §24 boundary path
  BND-007/008/009/010/014/015).
- **Clustering re-run request:** 001-003 → 005 BINDING → 007 → predicates
  (accepted AIOP-001 artifact exists; R8/R9) → 014 BINDING.
- **Failure:** provider timeout or error → FAILED, no consequence, Session
  stays ANALYSIS. An INDETERMINATE commit → BND-017; no blind retry. A stuck
  non-terminal generation blocks re-runs (a disclosed ceiling; F09
  recovery).
- **Automatic (method-derived) path:** BND-011/012 DENY (D8). Not
  materialized.

## 7. Analysis input / output model (final)

| Question | Answer |
|---|---|
| What establishes ANALYSIS? | A committed CMD_BEGIN_ANALYSIS: the single `session:ANALYSIS` audit row (EC-2) |
| Canonical analysis state | only `Session.state = ANALYSIS`. There is no "analysis complete" canonical flag |
| Input | exactly the verified frozen membership + the Challenge title/description. The manifest pins `burst:<id>`, fingerprint F, question ids and `original_text` digests (not `record_version`) |
| Immutable input | membership, `original_text`, origin, author, F, the manifest; `normalized_text` untouched in F04 (HD-18) |
| Derived state | AIGeneration (operational); AI_VALIDATION_PROOF (operational, persisted); **one** accepted analysis artifact per Session (R2); QuestionCluster + memberships per accepted `cluster_run_id` |
| Analysis artifact schema (HD-18, closed) | `classification_proposals[]` (question refs → proposed class label); `question_families[]` (label + member question refs); `unusual_question_flags[]` (question ref + reason); `pattern_descriptions[]` (text + supporting question refs); `contradiction_proposals[]` (pair or set of question refs + description). Every question ref must be ∈ the manifest. **No** new-question text field. Exact field names and limits are Case 2, fixed in WU-04.4 |
| Reconstructable | manifest ← F; proof ← generation; artifact lineage (09 §118). Provider output is not replayable (GAP-08-011) |
| Retryable | after FAILED / REJECTED, by an explicit controller request (HD-16). Never after an accepted success (R2) |
| Idempotent | BEGIN_ANALYSIS; the re-run request; the authorized run (one generation per authorization); acceptance (one per generation) |
| Human source | the frozen HUMAN Questions |
| AI derived | generation output, the artifact, clusters: always AI origin, provider `mock` |
| Evidence | nothing |
| Result | the accepted artifact and clusters, as DERIVED / PROPOSAL, MOCK / NON_PROOF |
| Candidate only | a validated generation before acceptance; every proposal inside the artifact |
| What may produce an effect | BEGIN_ANALYSIS (the phase); acceptance of derived output (via BND-010 / 014). Nothing authority-bearing |

## 8. Provenance model (final)

- **The chain:** artifact / cluster → generation → manifest → {burst, F,
  question ids + text digests} → F03 completion (BINDING) → captures
  (PARTICIPATION) → admission (BINDING) → FOUNDING → login.
- **Authority provenance:** the artifact's acceptance audit carries
  SYSTEM_OPERATION → the authorizing command → that command's BINDING
  audit (the controller).
- **The generation records:** provider `mock`, model, prompt version, the
  invoking command id, correlation, retry lineage, failure code.
- **The proof records:** generation, contract and validator version, result,
  output fingerprint, time. Provider identity resolves through the
  generation.
  - That is what F05 needs to enforce HD-20.
  - Non-fixture is determined by the existing provenance: a Workspace with a
    FOUNDING audit event is governed; a fixture has none.
- **The projection** exposes `origin = AI`, `derived = true`,
  `provider = mock`, `proof = NON_PROOF / MOCK` and the generation
  reference.
- **Logging:** no full prompt or output logging by default (11 §51).

## 9. Effect model (final)

| Candidate | Gate | Effect | Never |
|---|---|---|---|
| begin analysis | 005/007/008 → 014 BINDING | Session ANALYSIS; one AIOP-001 authorization | an automatic or System begin |
| authorized run | SYSTEM_OPERATION → 007/008/009 | generation + proof (operational) | a call before COMPLETED; a call outside the Gateway; a second run per authorization |
| validated output | 010 → 014 SYSTEM_OPERATION | one accepted artifact (AI, MOCK) | Question/membership/F change; Session advance; selection / Decision / Evidence / Assumption; human attribution; a second accepted artifact |
| controller re-run request | 005 → 014 BINDING | a new authorization | a re-run after an accepted success |
| AIOP-001 acceptance (as a side relation) | — | authorizes exactly one AIOP-002 run (HD-23) | clustering authorization when AIOP-001 failed, was rejected or was not accepted |
| authorized clustering run | SYSTEM_OPERATION → 007/008/009 | generation + proof (operational) | a run before AIOP-001 acceptance; a second run per authorization; AIOP-001 output as model input |
| clustering output | 010 → 014 SYSTEM_OPERATION | QuestionCluster + memberships (one accepted run per Session) | a Question identity change; a priority grant; a second accepted cluster run |
| controller clustering re-run request | 005 → 014 BINDING | a new clustering authorization | a re-run after an accepted cluster run; a re-run while no accepted AIOP-001 artifact exists |
| mock proof | — | — | counting toward non-fixture REFLECTION (HD-20) |

## 10. Recursive DeepSweep (final, after decisions)

- **Producer (F03).**
  - Read-only. `verify_frozen_set` errors map to BLOCKED.
  - HD-18 leaves `normalized_text` untouched, so fingerprint V2 is
    unaffected either way.
- **Parent / governance.**
  - HD-17 adds the fifth source. 20 §7 gets a successor note now; the audit
    CHECK and BND-014 branch change at materialization.
  - HD-1 is intact: no automatic Session authority (R1).
  - D8 is intact (BND-011/012 not used).
- **Authority.**
  - Every AI effect is traceable to one human BINDING act (R1, R3).
  - SYSTEM_SERVICE becomes a real actor class at the effect gate for the
    first time. It needs an identity in the command envelope
    (`requesting_actor_type = SYSTEM_SERVICE`, a service id), and a static
    rule that only F04 handlers may construct it.
- **Siblings.**
  - Session control handler reuse (`_run`) for BEGIN_ANALYSIS and the re-run
    request.
  - `establishedBy`: only BEGIN_ANALYSIS writes `session:ANALYSIS`.
  - BND-008 is shared with capture: the FBR-F04-3 repair must keep every F03
    capture test green.
- **Persistence (at materialization).**
  - proof table;
  - manifest immutability trigger;
  - artifact append-only trigger;
  - `question_clusters` + `question_cluster_memberships` (09 §34/§35);
  - audit CHECK + SYSTEM_OPERATION;
  - uniqueness: one generation per authorizing command, one acceptance per
    generation, one accepted AIOP-001 artifact per Session.
- **Runtime.**
  - MockProvider enabled by dev configuration only (HD-19 / R4).
  - Production-profile config must refuse the mock (19 §40, line 2786).
  - The worker stays out: synchronous execution after the BEGIN_ANALYSIS
    commit, in separate transactions (T1 transition → T2 invocation records
    + provider call + proof → T3 acceptance). Case 2.
- **API** (F02 envelope):
  - `…/transitions/begin-analysis`;
  - `…/analysis/request` (controller re-run);
  - read on `position.analysis`.
  - The begin-analysis response returns the committed transition plus the
    run outcome **as separate facts**. A failed run never makes the
    transition look failed.
- **Frontend.**
  - ANALYSIS phase; a Begin-analysis control from server capability.
  - A derived field showing families, patterns, contradictions, unusual
    flags and clusters, marked **AI · DERIVED / PROPOSAL · MOCK /
    NON_PROOF**.
  - Human Questions stay primary and verbatim.
  - An "analysis unavailable" state with a re-run control from server
    capability.
  - No chat. No SF-01 changes (SF-01 integration is a later relation).
- **Tests:** a TF-ANALYSIS family (§15).
- **F05.**
  - HD-20 must be enforced at F05's BEGIN_REFLECTION through provenance
    (provider `mock` → not eligible for a non-fixture Session).
  - In the mock dev runtime, governed Sessions stay in ANALYSIS (R5).
  - F05 must disclose that, or wait for HARD-DEP-002 / NQ-GAP-024.
- **F08:** new outbox events (`SESSION_ANALYSIS_BEGUN`, `AI_GENERATION_*`,
  `AI_OUTPUT_ACCEPTED`, `QUESTION_CLUSTERS_ACCEPTED`). The naming is
  Case 2.
- **Clustering (HD-23), outward sweep:**
  - **Producer:** the AIOP-001 acceptance commit. It becomes the only source
    of the clustering authorization.
    - Is creating the authorization in the same commit as acceptance a new
      authority-bearing write? No. It is operational state implied by HD-23,
      and it is represented by the accepted artifact itself.
    - The clustering run's SYSTEM_OPERATION check reads "an accepted AIOP-001
      artifact exists and no AIOP-002 generation references BEGIN_ANALYSIS
      yet". So no separate authorization row is required (Case 2).
  - **Consumers:** the projection shows clusters only after acceptance, and
    "clustering not run" when AIOP-001 failed or was not accepted. That is
    an honest state, not an error.
  - **Execution chain (Case 2):** synchronous in the same request after the
    AIOP-001 acceptance commit (T3 → T4 invocation → T5 acceptance). The
    same applies after a controller AIOP-001 re-run is accepted.
  - **Siblings:** HD-16 is unchanged (AIOP-001-only authorization).
  - **SYSTEM_OPERATION (HD-17)** now covers three reference shapes:
    BEGIN_ANALYSIS, a controller AIOP-001 re-run request, and a controller
    clustering re-run request. Each must re-check its own predicates.
  - **Persistence:** `question_clusters` + `question_cluster_memberships`
    (09 §34/§35). Uniqueness: one AIOP-002 generation per authorization;
    one accepted cluster run per Session.
  - **Tests:** the K group, extended.
- **Ledger:** HD-16..23 reconciled (REC-018..027). No F04 Case-3 relation is
  open. H-7 is open.

## 11. Inverse DeepSweep (final)

1. **"Session is in ANALYSIS"**
   - Chain: projection ← Session row ← CMD_BEGIN_ANALYSIS commit
     (`establishedBy`) ← BND-014 BINDING `SESSION:<id>` ← grant ← FOUNDING ←
     login.
   - Preconditions proven by the COMPLETED Burst, `verify_frozen_set`, and
     no unresolved capture.
   - **Complete.**
2. **Visible derived analysis**
   - Chain: projection (HD-22 audience) ← accepted artifact ← acceptance
     commit, SYSTEM_OPERATION → BEGIN_ANALYSIS command → BINDING (controller)
     ← BND-010 ← persisted proof VALIDATED ← generation VALIDATED ← Gateway
     ← manifest = verified F ← Session ANALYSIS ← frozen set ← human
     captures.
   - **The provider link is MockProvider.** It is disclosed in every
     record and projection as MOCK / NON_PROOF (HD-19). Per 20 §11 this
     chain is a **mock-ceiling proof**, never a real-analysis proof. It is
     complete *as a mock-ceiling chain* once FBR-F04-1/4/5/6/7/8 are
     repaired.
3. **"Analysis unavailable"**
   - Chain: projection ← generation FAILED / REJECTED ← Gateway ← authorized
     run.
   - The re-run control comes from the server capability (controller,
     R2/R3).
   - **Complete.**
4. **Visible clusters (HD-23)**
   - Chain: projection (HD-22 audience) ← QuestionCluster + memberships
     (one `cluster_run_id`) ← CMD_ACCEPT_CLUSTERING_OUTPUT
     (SYSTEM_OPERATION → BEGIN_ANALYSIS → controller BINDING) ← BND-010 ←
     persisted proof VALIDATED ← AIOP-002 generation VALIDATED ← Gateway ←
     manifest = verified F (frozen human Questions only, R10) ← clustering
     authorization ← **accepted AIOP-001 artifact** (its own chain, item 2)
     ← BEGIN_ANALYSIS ← frozen set ← human captures.
   - The provider link is MockProvider, marked MOCK / NON_PROOF (HD-19).
   - **Complete as a mock-ceiling chain** once FBR-F04-1/4/5/6/7/8/9 are
     repaired.
   - Negative inverse: if the AIOP-001 artifact link is absent (failed or
     not accepted), **no** cluster, generation or authorization can exist
     for this Session. That is the falsifier K7.
5. **A persisted generation, one per authorizing command (R3):** generation
   → invoking command → SYSTEM_OPERATION → human command. The PKG-era
   Gateway's unlinked write path is FBR-F04-7.

## 12. First Broken Relations (all derivable; repaired at their homes during implementation)

| Id | Broken relation | Evidence | Home | Repair |
|---|---|---|---|---|
| FBR-F04-1 | The Gateway is a parallel canonical writer: it persists the artifact itself | `ai_gateway/gateway.py:296-316`; 08 §20/§22; 09 §68; 20 §7 | 08 §20, 09 §68 | The Gateway ends at a validated candidate (generation + proof). Acceptance is a separate SYSTEM_OPERATION command via BND-010 → BND-014 |
| FBR-F04-2 | BND-010 ordering: the artifact is written before the generation is VALIDATED | `gateway.py:308-316`; `bnd_010_ai_output.py:111-124` | 06 BND-010 | Follows from FBR-F04-1 |
| FBR-F04-3 | Protected-Burst AI denial is keyed on the requester; BND-009 doesn't check Burst state | `bnd_008_question_burst.py:148-156`; `bnd_009_ai_invocation.py:97-112`; 06 BND-009 | 06 BND-008/009 | Deny the AI categories during ACTIVE/PAUSED for any requester; BND-009 requires COMPLETED + a verified F |
| FBR-F04-4 | AI_VALIDATION_PROOF is not persisted (HD-20 enforcement depends on it) | `ai_contracts/generation.py`; 09 §56; 07 §4 | 09 §56 | An immutable proof record, one per generation |
| FBR-F04-5 | Manifests are mutable; artifacts are append-only by convention only | migrations `7c2e8a4f1d6b`, `4a7c1e9f2b3d`; 09 §54.1 | 09 §54/§118 | DB triggers |
| FBR-F04-6 | The manifest is not bound to the frozen set; it pins the mutable `record_version` | `ai_gateway/context.py:158-195`; 08 §23 | 08 §6/§23 | The manifest is built only from `verify_frozen_set` output (burst, F, ids, text digests) |
| FBR-F04-7 | Gateway authorization is a caller boolean; generations are not tied to a command | `gateway.py:178-201`; 09 §128 | 09 §67/§128 | Only F04 command handlers call the Gateway; the generation stores the invoking command id; a static import gate |
| FBR-F04-8 | AIOP-001 / 002 contracts are unregistered and schemaless; the validator hard-codes one mock shape | `ai_contracts/aiop.py`; `validator.py:403-463`; BLOCK-08-008 | 08 §7/§23/§24 | Register both contracts with the closed schemas (HD-18; 09 §34/§35 for clusters) and deterministic validators |
| FBR-F04-9 | The mock output is independent of the input and carries no MOCK marker anywhere | `adapters/providers/mock.py:508-516` | HD-19 | Every mock generation, artifact and projection is marked; the mock output conforms to the HD-18 schema with question refs drawn from the manifest (deterministic, still input-independent in meaning) |
| FBR-F04-10 | Published F03 publication records are stale | F03 `STATUS.md:10-12`, `FIELD_REVIEW.md:137` | F03 reports | H-7 (human) |

**Obligations (not broken):**
- Only BEGIN_ANALYSIS writes `session:ANALYSIS`.
- `verify_frozen_set` errors map to BLOCKED.
- The mock is refused in production-profile config.
- SYSTEM_SERVICE is constructible only by F04 handlers.

## 13. Case-3 status

| Id | Status |
|---|---|
| C3-F04-1..6 | **CLOSED** by HD-16..HD-22 (see §0 and `HUMAN_DECISIONS.md`) |
| **C3-F04-7** | **CLOSED by HD-23** (option (c) plus the three stated rules). Surfaced by incorporating HD-21 |
| H-7 | OPEN, non-blocking: correct the stale F03 publication records? |
| H-8 | OPEN, non-blocking, observed during the revision-3 sweep: SF-01 is committed **locally** as `447b24e` on branch `frontend-symbiotic` (worktree `~/Entwicklung/nquiry-frontend`). It is **not published**, and its parent is F02 `bea864b`, not the F03 line `c9d86ba`. WU-04.8 (F04 frontend) is designed against the published tree with SF-01 untouched. Which frontend foundation F04 builds on, and in what order SF-01 and F03/F04 are integrated, is a publication / integration decision for human authority. It is needed before WU-04.8 starts, not for this review. Not caused or modified by the F04 architecture work |

**C3-F04-7 — What triggers the AIOP-002 clustering run?** *(RESOLVED: (c),
HD-23. The option text is kept as the record of what was decided.)*
- *Question.* HD-21 puts clustering in scope. Who or what authorizes its
  invocation, and who may re-run it?
- *Why human authority is required.*
  - HD-16 authorizes **exactly one AIOP-001 run** per BEGIN_ANALYSIS.
    Extending that authorization to a second operation would widen a human
    decision by analogy.
  - 08 §24 names no invocation authority for AIOP-002 (its boundary path
    begins at BND-007).
  - 04 has no AUTH-DEP for AIOP invocation.
- *Blocked relation:* the WU-04.9 invocation link; the visible-clusters
  chain (§11.4).
- *Options:*
  - **(a)** BEGIN_ANALYSIS also authorizes exactly one AIOP-002 run,
    executed by the system after the AIOP-001 run, with SYSTEM_OPERATION
    referencing BEGIN_ANALYSIS. Re-runs after failure need an explicit
    controller request, symmetric to HD-16.
    *Consequence:* one human act yields both derived views; the
    authorization scope of BEGIN_ANALYSIS doubles.
  - **(b)** Clustering runs only on an explicit controller request (BINDING),
    and its execution is SYSTEM_OPERATION.
    *Consequence:* clustering is a deliberate second act; one extra control.
  - **(c)** The system runs one AIOP-002 automatically only after an
    accepted AIOP-001 artifact exists, referencing the same BEGIN_ANALYSIS.
    *Consequence:* clusters depend on analysis success; no clusters when
    analysis fails.
- *Smallest decision:* pick (a), (b) or (c).

Carried forward (not F04 decisions): NQ-GAP-024; D8; NQ-GAP-003; the
AUTH-DEP-SESS-007 human path; HARD-DEP-002.

## 14. Final F04 Work Unit graph

```text
WU-04.0 ledger/home-file pointers ─┬─► WU-04.1 BEGIN_ANALYSIS ─────────────────────────────┐
                                   ├─► WU-04.2 protected-set boundary repair (FBR-3) ─┐    │
                                   └─► WU-04.3 effect-gate SYSTEM_OPERATION + AI record │    │
                                        integrity (HD-17; FBR-4,5) ──────────────────┤    │
                         WU-04.4 AIOP-001 contract + manifest binding (HD-18; FBR-6,8,9)│    │
                                                  ▼                                   ▼    │
                         WU-04.5 authorized run + acceptance + controller re-run (HD-16/17; FBR-1,2,7)
                                                  ▼
                         WU-04.6 mock lane: dev-only enablement, MOCK/NON_PROOF marking, unavailable state (HD-19/20)
                                                  ▼
                         WU-04.9 AIOP-002 clustering (HD-21 + HD-23: authorized only by an accepted AIOP-001 artifact; 09 §34/35 tables)
                                                  ▼
                         WU-04.7 projection (HD-22) ◄── 04.1, 04.5, 04.6, 04.9
                                                  ▼
                         WU-04.8 frontend (projection only; SF-01 untouched)
                                                  ▼
                         WU-04.10 field-end proof (L0–L8, real stack, mock ceiling)
```

| WU | Relation owned | Input → target | Authority / boundary | Command / query | Persistence | Projection | MUST BECOME TRUE | MUST REMAIN IMPOSSIBLE | Falsifiers | Depends on |
|---|---|---|---|---|---|---|---|---|---|---|
| 04.0 | decisions → home files | REC-018..025 → pointers in 04 AUTH-DEP-SESS-006, 06 BND-010, 08 §23/§24, 09 §68 | human (given) | — | docs | — | every HD referenced at its home | an unrecorded semantic choice | L-1 | — |
| 04.1 | Session phase + authorization | QUESTION_CAPTURE → ANALYSIS | BINDING `SESSION:<id>`; 005/007/008/014 | CMD_BEGIN_ANALYSIS; `…/transitions/begin-analysis`; `BEGIN_ANALYSIS` capability | Session; audit `session:ANALYSIS`; outbox | action + reason; `establishedBy` | a controller begins; exactly one authorization exists | non-controller begin; bad state; unverified F; unresolved capture; stale; double begin; any AI call in this commit | A1-A10 | 04.0 |
| 04.2 | protected set ↔ AI | — | 008/009 | — | — | — | AI categories denied while ACTIVE/PAUSED for any requester; BND-009 requires COMPLETED + verified F | a human- or system-requested AI op during the Burst | B1-B4 | — |
| 04.3 | effect gate + AI records | — | BND-014 SYSTEM_OPERATION | — | audit CHECK +SYSTEM_OPERATION; proof table; manifest immutable; artifact append-only; uniqueness constraints | — | SYSTEM_OPERATION resolves only for SYSTEM_SERVICE with a committed referenced command | a fabricated / human / AI SYSTEM_OPERATION; mutation of proof / manifest / artifact | C1-C8 | 04.0 |
| 04.4 | AIOP-001 contract + input | verified F → manifest | BND-009 | — | registered contract; manifest | — | manifest = F exactly; closed HD-18 schema validated deterministically; mock output conforms, marked | foreign / extra / missing Question; unverified F; a new-question field; schema-invalid VALIDATED | D1-D8 | 04.3 |
| 04.5 | run → candidate → accepted artifact; re-run | ANALYSIS → gen terminal → ≤1 accepted artifact | HD-16/17; 009/010/014 | CMD_AI_QUESTION_ANALYSIS; CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT; CMD_REQUEST_QUESTION_ANALYSIS; `…/analysis/request` | generation, proof, artifact | — | one authorized run per BEGIN_ANALYSIS; one acceptance per VALIDATED generation | a second run per authorization; a re-run after accepted success; acceptance of REJECTED / FAILED; Session / Question change; AI self-invocation | E1-E14 | 04.2, 04.4 |
| 04.6 | mock lane | — | 11 fail-closed | — | `provider = mock` | MOCK / NON_PROOF; unavailable | dev-only mock; every artifact marked; proof carries resolvable provider identity (HD-20 enforceable) | mock in the production profile; an unmarked mock; a real provider call | F1-F6 | 04.5 |
| 04.9 | clustering | accepted AIOP-001 artifact + frozen set → ≤1 accepted cluster run | HD-21, HD-23; SYSTEM_OPERATION (ref BEGIN_ANALYSIS) / BINDING (re-run request); 009/010/014 | CMD_AI_QUESTION_CLUSTERING; CMD_ACCEPT_CLUSTERING_OUTPUT; CMD_REQUEST_QUESTION_CLUSTERING; `…/analysis/clustering/request` | `question_clusters`, `question_cluster_memberships` (09 §34/35); uniqueness per authorization and per Session | "clustering not run" / clusters | exactly one automatic clustering run after AIOP-001 acceptance; clusters reference only frozen Questions | clustering without an accepted AIOP-001 artifact; AIOP-001 output as input; a second run per authorization; a re-run after an accepted cluster run; membership / Question mutation; a priority grant | K1-K14 | 04.5 |
| 04.7 | read side | — | read chain (HD-22 = HD-13 audience) | `position.analysis` | — | status, generations, accepted artifact, clusters, provenance, MOCK marker | server-side audience; AI origin explicit | merged human / AI provenance; client-side visibility | G1-G5 | 04.1, 04.5, 04.6, 04.9 |
| 04.8 | frontend | — | projection only | — | — | ANALYSIS phase; derived field; markers; human primary; no chat | the real-stack flow §15 H | client authority; chat; AI text shown as human; mock shown as real | H1-H7 | 04.7 |
| 04.10 | proof | — | — | — | — | — | L0-L8; the mock ceiling documented | a mock claimed as real | full ladder | all |

## 15. Final TDD / falsifier matrix

**L — ledger**
- **L-1:** 16 §41 REC-018..025, the §6 rows, the YAML and 20 §15B agree
  (a count check).

**A — BEGIN_ANALYSIS (04.1)**
- **A1 happy path:** the controller begins. Session ANALYSIS, version +1,
  audit BINDING `SESSION:<id>`, `establishedBy` resolves, and one unconsumed
  authorization exists.
- **A2 wrong authority:** participant, Owner, Challenge- or Workspace-scoped
  binding → denied; an outsider → denied.
- **A3 wrong state:** from QUESTION_GENERATION or ANALYSIS → blocked /
  illegal.
- **A4 unverified F:** a tampered fingerprint (test superuser) → blocked,
  Session unchanged.
- **A5 unresolved capture** → blocked.
- **A6 stale:** an old expected version → stale.
- **A7 idempotency:** an identical retry → replayed; the same key with a
  different payload → rejected.
- **A8 no AI in the transition commit:** a static import gate on the
  transition handler; the T1 commit contains no generation.
- **A9 EC-2:** exactly one `session:ANALYSIS` row.
- **A10 failure injection:** failed_precommit; Session QUESTION_CAPTURE and
  no authorization.

**B — protected set (04.2)**
- **B1:** an AI category while ACTIVE → DENY for HUMAN_USER and
  SYSTEM_SERVICE. RED today for HUMAN_USER.
- **B2:** BND-009 with the Burst not COMPLETED → DENY.
- **B3:** BND-009 with an unverified F → DENY.
- **B4:** all F03 capture tests stay green.

**C — effect gate and records (04.3)**
- **C1:** SYSTEM_OPERATION with a human actor → DENY.
- **C2:** SYSTEM_OPERATION with an AI_PROCESSOR actor → DENY.
- **C3:** SYSTEM_OPERATION referencing a non-committed, foreign-Session or
  non-existent command → DENY.
- **C4:** audit rows carry type SYSTEM_OPERATION, ref = command id, scope
  `SESSION:<id>`; the CHECK refuses an unknown type.
- **C5:** a proof UPDATE → DB error; a second proof per generation → DB
  error.
- **C6:** a manifest UPDATE → DB error.
- **C7:** an artifact UPDATE / DELETE → DB error.
- **C8:** a second generation for the same authorizing command → refused.

**D — contract and input (04.4)**
- **D1:** manifest = exactly the frozen members (ids + text digests), F and
  the burst.
- **D2:** an extra, missing or foreign Question → refused before the
  provider is called.
- **D3:** an F mismatch → refused.
- **D4:** schema-invalid, partial or wrong-operation output → REJECTED, with
  no artifact.
- **D5:** output containing a new-question field, or question refs outside
  the manifest → REJECTED (HD-18).
- **D6:** prompt injection in Question text → the structure is unchanged
  and the output is unaffected.
- **D7:** no cross-Workspace refs in the manifest.
- **D8:** `normalized_text` is unchanged for every Question after the full
  F04 flow (HD-18).

**E — run, acceptance, re-run (04.5)**
- **E1:** after BEGIN_ANALYSIS, the system executes exactly one AIOP-001
  run, whose generation references the BEGIN_ANALYSIS command (R3).
- **E2:** validated → exactly one accepted artifact, with 09 §118 lineage
  and a SYSTEM_OPERATION audit whose ref is the BEGIN_ANALYSIS command.
- **E3:** REJECTED or FAILED → acceptance blocked, with no artifact.
- **E4:** the artifact exists only via the acceptance commit; a static gate
  shows the Gateway has no artifact write.
- **E5:** acceptance changes no Session, Question, membership or F
  (snapshot diff).
- **E6:** a second system run for the same authorization → refused.
- **E7:** the controller requests a re-run after FAILED → a new generation
  with `retry_of`; the old one is not revived.
- **E8:** a re-run request after an accepted success → blocked (R2).
- **E9:** a re-run request by a participant, the Owner or an outsider →
  denied.
- **E10:** a re-run while a generation is non-terminal → blocked (a
  disclosed ceiling).
- **E11:** an unconsumed authorization (no generation) → the controller
  request executes it (R3).
- **E12:** invocation while the Session is not ANALYSIS → blocked.
- **E13:** an AI_PROCESSOR requester → denied.
- **E14:** output claiming a Decision, selection, Evidence or Assumption
  status → BND-010 DENY.

**F — mock lane (04.6)**
- **F1:** the production-profile config with mock enabled → refused at
  startup.
- **F2:** every generation has `provider = mock`; every artifact and
  projection is marked MOCK / NON_PROOF.
- **F3:** a provider timeout or error → FAILED, an unavailable state, and
  the frozen set still readable.
- **F4:** only the mock adapter exists; no provider SDK import.
- **F5:** the proof resolves its provider identity through the generation
  (the HD-20 hook).
- **F6:** the mock never performs network egress (static + runtime check).

**K — clustering (04.9)**
- **K1:** clusters reference only frozen Questions of this Session.
- **K2:** membership, Question and F are unchanged.
- **K3:** the per-run `cluster_run_id`; at most one accepted cluster run per
  Session (R8).
- **K4:** a REJECTED output → no clusters.
- **K5:** there is no priority or selection field.
- **K6:** a cross-Session or cross-Workspace ref → REJECTED.
- **K7 (HD-23):** AIOP-001 FAILED, REJECTED or validated-but-not-accepted →
  **no** AIOP-002 generation, no cluster, and the clustering capability
  unavailable with its reason. Also: a direct clustering invocation attempt
  → blocked `NO_ACCEPTED_ANALYSIS`.
- **K8:** after AIOP-001 acceptance, the system runs exactly one AIOP-002
  generation. Its audit is SYSTEM_OPERATION with ref = the BEGIN_ANALYSIS
  command id, and it links the accepted AIOP-001 artifact (R7).
- **K9:** the same after an accepted **controller re-run** of AIOP-001: one
  clustering run, and the chain resolves through the re-run request to
  BEGIN_ANALYSIS.
- **K10:** the AIOP-002 manifest contains only frozen human Questions. The
  AIOP-001 artifact is not in the model input (R10).
- **K11:** AIOP-002 FAILED → **no automatic retry**. The controller request
  → a new generation with `retry_of`; the failed one is not revived.
- **K12:** a clustering re-run request by a participant, the Owner or an
  outsider → denied; before any accepted AIOP-001 artifact → blocked.
- **K13:** a clustering re-run request after an accepted cluster run →
  blocked (R8). A second system run for the same authorization → refused.
- **K14:** an unconsumed clustering authorization (no AIOP-002 generation) →
  the controller request executes it (R9).

**G — projection (04.7)**
- **G1:** the audience equals the HD-13 frozen-set audience, server-side.
- **G2:** an outsider → denied.
- **G3:** AI origin, generation ref and MOCK marker are present.
- **G4:** human Questions are unchanged and listed separately.
- **G5:** a failed run shows unavailable, with the re-run capability for the
  controller only.

**H — real stack (04.8 / 04.10; no mocked backend; the MockProvider is the
declared ceiling)**
- **H1:** the controller begins analysis; the phase shows ANALYSIS, and
  `establishedBy` shows BEGIN_ANALYSIS.
- **H2:** the derived field appears, marked AI · DERIVED / PROPOSAL · MOCK /
  NON_PROOF; the human Questions are verbatim.
- **H3:** a participant sees the same derived field (HD-22) without controls.
- **H4:** an injected provider failure → unavailable, then the controller
  re-run.
- **H5:** the Owner or a participant has no begin or re-run control, and the
  server's reason is shown.
- **H6:** clusters become visible only after the analysis artifact is
  accepted. When the AIOP-001 run is made to fail (injected), "clustering not
  run" is shown and no clusters appear (HD-23).
- **H7:** axe 0 serious/critical; keyboard; mobile.

## 16. F04 end boundary

F04 ends when a governed Session is in **ANALYSIS**, with a provable chain
to its human origin, and:
- one BEGIN_ANALYSIS authorization, consumed by exactly one system run;
- controller re-runs only after failure;
- every VALIDATED generation has a persisted proof and at most one accepted
  AI-origin artifact;
- at most one accepted AIOP-001 artifact per Session;
- a clustering run is authorized only by an accepted AIOP-001 artifact, with
  at most one accepted cluster run per Session, and no clustering when
  analysis failed or was not accepted (HD-23);
- everything is visible to the HD-13 audience, marked MOCK / NON_PROOF in
  the dev runtime;
- "analysis unavailable" is an honest state.

F04 does **not** execute BEGIN_REFLECTION.

## 17. F05+ deferred relations

| Relation | Deferred to | Note |
|---|---|---|
| TRN-SESS-007 BEGIN_REFLECTION | F05 | must enforce HD-20 via proof → generation → provider provenance |
| Whether a mock proof may count for *fixture* Sessions | F05 | HD-20 is only a prohibition (R5) |
| NQ-GAP-024 way out of ANALYSIS | F05 (Case 3) | in the mock-only runtime, governed Sessions cannot reach REFLECTION (R5) |
| AUTH-DEP-SESS-007 human path D8-bound? | F05 | 04:1560 |
| Human adoption of AI proposals, QuestionSelection | F05 | 07 §30, 08 §40 |
| Assumptions (AIOP-004), Perspectives, AI-origin Questions | out (HD-21) | new architecture / Mode C needed |
| Automatic Begin Analysis / Reflection | D8 | BND-012 DENY |
| Real provider lane | HARD-DEP-002 (D3, D9) | external |
| Outbox delivery, workers, per-principal DB roles, recovery of stuck generations | F08 / F09 | infrastructure |

## 18. Architecture readiness status

**READY_FOR_F04_ARCHITECTURE_REVIEW**

- **Closed:** C3-F04-1..7 (HD-16..HD-23, reconciled in 16 §41 REC-018..027
  and 20 §7 / §15B). **No F04 Case-3 relation remains open.**
- **Derivable, ready for implementation after review:**
  - all Work Units WU-04.0..04.10, including WU-04.9 clustering;
  - FBR-F04-1..9 repaired at their homes.
- **Open for review:**
  - H-7 (non-blocking);
  - the readings R1–R10 (§0), which the review should confirm or correct.
- **External:** HARD-DEP-002. F04 passes structurally under the declared
  MockProvider ceiling (19 §24 STOP; HD-19 / HD-20).

================================================================================
END FILE: docs/implementation/field-reports/F04/F04_ARCHITECTURE_RECONSTRUCTION.md
================================================================================

================================================================================
BEGIN FILE: docs/implementation/field-reports/F04/HUMAN_DECISIONS.md  (complete current content)
================================================================================

# F04 — HUMAN DECISIONS

The six Case-3 decisions C3-F04-1 through C3-F04-6 below are copied verbatim
from `F04_ARCHITECTURE_RECONSTRUCTION.md` §13 (revision 1), as reconstructed
on 2026-09-24 from published F03 (`0d59ae3`, tag `field-F03`;
`origin/master` `c9d86ba`).

**All six are now RESOLVED by the human operator (2026-09-24).** The
resolutions are recorded at the end of this file ("Resolutions"). The option
text above them is kept unchanged as the record of what was decided. A
seventh decision, **C3-F04-7**, surfaced while incorporating them. It is
**RESOLVED** as well (HD-23). **No F04 Case-3 decision remains open.**

Legend used in the source (unchanged):
- *Question*: the decision needed.
- *Not derivable because*: why human authority is required.
- *Blocks*: the blocked relation.
- *Options* and *Consequences*: the options and what each one means.

---

**C3-F04-1 — Who may invoke AIOP-001, and when?**
- *Question.* After BEGIN_ANALYSIS, what authorizes a model call over the
  frozen set, and who may re-request it after failure?
- *Not derivable because* 04 defines no AUTH-DEP for AIOP invocation.
  AUTH-DEP-SESS-006 says only "AI may execute analysis once operation is
  authorized". 12 says "approved application/system caller". The system
  path needs D8, which is open. Who may start machine participation is
  authority.
- *Blocks:* invocation, retry and the whole derived path.
- *Options:*
  - **(a)** The controller runs CMD_AI_QUESTION_ANALYSIS explicitly
    (BINDING `SESSION:<id>`). Beginning analysis and running AI are two
    human acts. Every retry is also explicit.
  - **(b)** CMD_BEGIN_ANALYSIS authorizes exactly one AIOP-001 run, executed
    by the system immediately after commit. Re-runs after failure need an
    explicit controller request.
  - **(c)** Any Session participant may request analysis.
- *Consequences:*
  - (a) is the most explicit, with one extra step in the UI.
  - (b) matches AUTH-DEP-SESS-006's wording, but "system runs AI after a
    human act" must be recorded, so as not to create an undocumented
    automatic path (HD-1).
  - (c) widens authority beyond the controller.
- *Smallest decision:* pick (a), (b) or (c).

**C3-F04-2 — What authority source records SYSTEM_SERVICE acceptance of AI
output (and invocation, if system-executed)?**
- *Not derivable because* 20 §7 admits exactly BINDING, ROLE, FOUNDING and
  PARTICIPATION. 09 §68 names SYSTEM_SERVICE as the accepting actor. BND-010
  defers acceptance authority to "08/09", which never define it. Recording
  it as BINDING would fabricate provenance, because the service holds no
  binding (HD-6).
- *Blocks:* every accepted artifact.
- *Options:*
  - **(a)** A new typed source **SYSTEM_OPERATION** (ref = the authorizing
    human command id, scope `SESSION:<id>`, re-read at commit: that command
    committed, the Session is still ANALYSIS, the proof is VALIDATED). This
    is a 5th effect-gate source, recorded like HD-15.
  - **(b)** Derived AI artifacts and AI records are **operational records
    outside the effect gate**, like commands and attempts: no BND-014,
    audit only. That contradicts 08 §22 / 09 §68 ("BND-014") and so needs an
    explicit architecture narrowing.
  - **(c)** Acceptance is a human act by the controller (BINDING). That
    adds a human review step 09 does not require.
- *Consequences:*
  - (a) keeps a single effect gate and truthful provenance.
  - (b) is simpler, but weakens "single governed commit boundary".
  - (c) turns derived analysis into human adoption, which changes its
    meaning (07 §30).
- *Smallest decision:* pick (a), (b) or (c).

**C3-F04-3 — What does AIOP-001 analysis contain (the output schema)?**
- *Not derivable because* 08 §23 lists outputs "such as" (classification,
  patterns, unusual-question flags, contradiction proposals, Question
  families, additional Question suggestions). The schema is open
  (BLOCK-08-008). Deciding which dimensions exist, and whether AI
  *suggests new Questions* to humans, is product meaning. D2 (AI autonomy)
  is also open.
- *Blocks:* FBR-F04-8 validator, projection and frontend.
- *Options:*
  - **(a)** Minimal: classification proposals + Question families +
    unusual-question flags.
  - **(b)** (a) + pattern descriptions + contradiction proposals.
  - **(c)** (b) + additional Question suggestions, shown as AI-origin
    proposals and never as Questions.
- *Consequences:* each step adds AI influence on the inquiry. (c) is the
  first place AI proposes questions to humans.
- *Smallest decision:* pick the dimension set. Separately, choose whether
  `normalized_text` is written in F04: **recommended no**, because
  normalization is AIOP-independent and not required.

**C3-F04-4 — What runs as "the model" in the runtime, and how is
mock-derived content marked?**
- *Not derivable because* HARD-DEP-002 is EXTERNAL_DEPENDENCY. 19:2784
  says "Do not silently substitute MockProvider". MockProvider output does
  not depend on the input, so showing it as analysis presents fabricated
  content. 13 AC-13-008 says "Mock proves gateway behavior only".
- *Blocks:* runtime behaviour, stakeholder acceptance, and what F05 may
  later consume.
- *Options:*
  - **(a)** No provider in the runtime. Analysis shows "AI analysis
    unavailable: no eligible provider". MockProvider is used in tests only.
  - **(b)** MockProvider enabled in the dev runtime. Every generation and
    artifact is marked `provider = mock` and projected as
    **NON_PROOF / MOCK**, never as analysis of the actual Questions.
  - **(c)** Resolve HARD-DEP-002 now (D3, D9, data classification, provider
    choice). This is an external decision.
- *Consequences:*
  - (a) is the truest, but the stakeholder sees no derived field.
  - (b) makes the pipeline visible, with a disclosed ceiling.
  - (c) unlocks the real lane.
- *Also decide:* whether a mock-validated proof may *ever* count toward
  F05's BEGIN_REFLECTION on a non-fixture Session. **Recommend recording
  "no" now**, so F04 marks provenance accordingly.

**C3-F04-5 — F04 AIOP scope beyond AIOP-001.**
- *Not derivable because:*
  - 12 §12 says "AIOP-001 required; AIOP-002 optional only if needed to make
    the derived artifact visually useful". "Visually useful" is a product
    judgement.
  - 19 §24 also lists perspectives (no 09 contract, so a new
    representation), assumptions (AIOP-004, creates a domain object in
    UNKNOWN) and AI-origin Questions (Mode C, excluded by 12 §5).
- *Blocks:* the Work Unit set and the frontend "derived relational field".
- *Options:*
  - **(a)** AIOP-001 only.
  - **(b)** + AIOP-002 clustering (09 §34 QuestionCluster exists;
    per-run clusters, with no "current" run).
  - **(c)** + AIOP-004 assumptions in UNKNOWN.
- Perspectives and AI Questions would need new architecture or Mode C, so
  they are out unless the human authorizes that architecture.
- *Smallest decision:* pick (a), (b) or (c).

**C3-F04-6 — Who sees derived analysis?**
- *Not derivable because* HD-13 governs human Question visibility only.
  Analysis visibility (controller only / all Session members / all Workspace
  members) is product meaning and privacy.
- *Options:*
  - **(a)** every member who can read the frozen set (the HD-13 audience);
  - **(b)** the controller only, until F05;
  - **(c)** participants + controller.
- *Smallest decision:* pick one.


---

## Resolutions (human operator, 2026-09-24)

The instruction, verbatim: "C3-F04-1 = (b); C3-F04-2 = (a); C3-F04-3 = (b);
normalized_text = NO in F04; C3-F04-4 = (b); Mock-validated proof MUST NEVER
count toward F05 BEGIN_REFLECTION for a non-fixture Session; C3-F04-5 = (b);
C3-F04-6 = (a). Treat these as human authority decisions."

| Decision | Chosen | Recorded as | Meaning (option text above, applied) |
|---|---|---|---|
| C3-F04-1 | **(b)** | HD-16 · NQ-DEC-044 · 16 §41 REC-018 | Beginning analysis authorizes exactly one AIOP-001 run, executed by the system right after the BEGIN_ANALYSIS commit. Re-runs after a failure need an explicit controller request |
| C3-F04-2 | **(a)** | HD-17 · NQ-DEC-045 · REC-019 | A fifth typed effect-gate source, SYSTEM_OPERATION (ref = the authorizing human command, scope `SESSION:<id>`, re-checked at commit). 20 §7 successor note: decided, not yet materialized |
| C3-F04-3 | **(b)** | HD-18 · NQ-DEC-046 · REC-020 | Classification proposals, Question families, unusual-question flags, pattern descriptions, contradiction proposals. No additional Question suggestions |
| C3-F04-3 supplement | **`normalized_text` = NO in F04** | HD-18 (same record) | F04 writes no `normalized_text` |
| C3-F04-4 | **(b)** | HD-19 · NQ-DEC-047 · REC-021 | MockProvider enabled in the dev runtime. Every AI run and result is marked mock and projected as NON_PROOF / MOCK, never as analysis of the real questions |
| C3-F04-4 supplement | **Mock-validated proof MUST NEVER count toward F05 BEGIN_REFLECTION for a non-fixture Session** | HD-20 · NQ-DEC-048 · REC-022 | A prohibition only. Whether a mock proof may count for a fixture Session is left to F05 |
| C3-F04-5 | **(b)** | HD-21 · NQ-DEC-049 · REC-023 | AIOP-001 + AIOP-002 (question clustering) |
| C3-F04-6 | **(a)** | HD-22 · NQ-DEC-050 · REC-024 | Every member who can read the frozen set (the HD-13 audience) |

The ledger reconciliation is recorded in `16_DECISION_GAP_REGISTER.md`
§6 / YAML / §41 (REC-018..REC-025) and in `20_SYSTEM_FIELD_ENGINEERING.md`
§7 successor note / §15B.

Readings derived from these decisions, for architecture review (full text
in the reconstruction §0, R1–R6):
- **R1:** the system run is not SYSTEM_DERIVED authority.
- **R2:** no re-run after an accepted success.
- **R3:** the authorization is consumed by its first generation.
- **R4:** the mock is dev-only and has no egress.
- **R5:** in a mock-only runtime, governed Sessions cannot reach REFLECTION.
- **R6:** the analysis audience is the HD-13 audience.

---

## C3-F04-7 — surfaced while incorporating the resolutions (now RESOLVED, see below)

**C3-F04-7 — What triggers the AIOP-002 clustering run?**
- *Question.* HD-21 puts clustering in scope. Who or what authorizes its
  invocation, and who may re-run it?
- *Why human authority is required.*
  - HD-16 authorizes **exactly one AIOP-001 run** per BEGIN_ANALYSIS.
    Extending that authorization to a second operation would widen a human
    decision by analogy.
  - 08 §24 names no invocation authority for AIOP-002 (its boundary path
    begins at BND-007).
  - 04 has no AUTH-DEP for AIOP invocation.
- *Blocked relation:* the WU-04.9 invocation link; the visible-clusters
  chain.
- *Options:*
  - **(a)** BEGIN_ANALYSIS also authorizes exactly one AIOP-002 run,
    executed by the system after the AIOP-001 run, with SYSTEM_OPERATION
    referencing BEGIN_ANALYSIS. Re-runs after failure need an explicit
    controller request, symmetric to HD-16.
    *Consequence:* one human act yields both derived views; the
    authorization scope of BEGIN_ANALYSIS doubles.
  - **(b)** Clustering runs only on an explicit controller request (BINDING),
    and its execution is SYSTEM_OPERATION.
    *Consequence:* clustering is a deliberate second act; one extra control.
  - **(c)** The system runs one AIOP-002 automatically only after an
    accepted AIOP-001 artifact exists, referencing the same BEGIN_ANALYSIS.
    *Consequence:* clusters depend on analysis success; no clusters when
    analysis fails.
- *Smallest decision:* pick (a), (b) or (c).

### Resolution of C3-F04-7 (human operator, 2026-09-24)

The instruction, verbatim: "C3-F04-7 = (c). One AIOP-002 run becomes
authorized only after an accepted AIOP-001 artifact exists. The AIOP-002
execution is SYSTEM_OPERATION and references the same BEGIN_ANALYSIS
authority chain. If AIOP-001 fails or is not accepted, clustering must not
run. If AIOP-002 itself fails, any retry requires an explicit controller
request. Record this as the human authority decision."

| Decision | Chosen | Recorded as |
|---|---|---|
| C3-F04-7 | **(c)** plus the three stated rules | HD-23 · NQ-DEC-051 · 16 §41 REC-026 (counts in REC-027) · 20 §15B |

Readings derived from it, for architecture review (full text in the
reconstruction §0, R7–R10):
- **R7:** the clustering run's reference is the BEGIN_ANALYSIS command; the
  accepted AIOP-001 artifact is a commit-time precondition.
- **R8:** at most one accepted cluster run per Session.
- **R9:** the clustering authorization is consumed by its first AIOP-002
  generation; if it is unconsumed, the controller's request may execute it.
- **R10:** the AIOP-001 artifact authorizes clustering but is not model
  input; the input stays the verified frozen human set.

================================================================================
END FILE: docs/implementation/field-reports/F04/HUMAN_DECISIONS.md
================================================================================

================================================================================
BEGIN FILE: docs/implementation/field-reports/F04/STATUS.md  (complete current content)
================================================================================

# FIELD STATUS

## Field
F04 — AI BOUNDARY · POST-BURST SENSEMAKING

## Semantic regime
Derived machine participation after protected human generation (§24).

## Status
NOT_STARTED — ARCHITECTURE REVISION 3: READY_FOR_F04_ARCHITECTURE_REVIEW

The architecture was reconstructed on 2026-09-24 from published F03
(`0d59ae3`, tag `field-F03`, `origin/master` `c9d86ba`). See
F04_ARCHITECTURE_RECONSTRUCTION.md (revision 3) and HUMAN_DECISIONS.md.
- **Closed:** all seven F04 Case-3 decisions, C3-F04-1..7, by human
  decisions HD-16..HD-23. They are reconciled in 16 §41 REC-018..REC-027
  (NQ-DEC-044..051) and in 20 §7 (SYSTEM_OPERATION successor note, decided
  and not yet materialized) and §15B.
- **Open (non-blocking):**
  - H-7, the stale F03 publication records.
  - H-8, SF-01 committed locally (`447b24e`, unpublished, based on F02),
    which F04's frontend WU must integrate with. This is a human
    integration-order decision before WU-04.8.
- The readings R1–R10 are for architecture review.
- Ten First Broken Relations; nine are derivable and repaired at their
  homes during implementation. The tenth is H-7.
- **Clustering (HD-23):** runs only after an accepted AIOP-001 artifact
  exists, as SYSTEM_OPERATION on the BEGIN_ANALYSIS chain. It never runs
  when AIOP-001 fails or is not accepted. A retry after an AIOP-002 failure
  needs an explicit controller request.
- Real provider lane: blocked by HARD-DEP-002. F04 passes under a declared
  MockProvider ceiling (HD-19); mock proofs never count toward
  BEGIN_REFLECTION for non-fixture Sessions (HD-20).

## Upstream dependencies
F03

## Downstream dependencies
F05

================================================================================
END FILE: docs/implementation/field-reports/F04/STATUS.md
================================================================================

================================================================================
BEGIN PROPOSED CHANGES: docs/architecture/16_DECISION_GAP_REGISTER.md
Unified diff of the uncommitted working copy against HEAD c9d86ba.
All lines are additions (F04 architecture revisions 2 and 3); nothing is removed.
================================================================================

```diff
diff --git a/docs/architecture/16_DECISION_GAP_REGISTER.md b/docs/architecture/16_DECISION_GAP_REGISTER.md
index 17b186d..e7306c4 100644
--- a/docs/architecture/16_DECISION_GAP_REGISTER.md
+++ b/docs/architecture/16_DECISION_GAP_REGISTER.md
@@ -199,6 +199,14 @@ For unresolved items, absent source detail remains explicit. No placeholder valu
 | NQ-DEC-041 | Burst visibility: own Questions only while ACTIVE, full frozen set with authors afterwards | ESTABLISHED (post-baseline, §41 REC-014) | F03 HD-13; 00 §11.1 | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
 | NQ-DEC-042 | Controller self-admission is lawful (HD-7 clarified) | ESTABLISHED (post-baseline, §41 REC-015) | F03 HD-14; NQ-DEC-035; NQ-GAP-079 (leave/removal stays open) | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
 | NQ-DEC-043 | PARTICIPATION is the fourth typed effect-gate authority source | ESTABLISHED (post-baseline, §41 REC-016) | F03 HD-15; NQ-DEC-034; 04 AUTH-DEP-Q-001 | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
+| NQ-DEC-044 | A committed BEGIN_ANALYSIS authorizes exactly one system-executed AIOP-001 run | ESTABLISHED (post-baseline, §41 REC-018) | F04 HD-16; 04 AUTH-DEP-SESS-006; 08 §23 | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
+| NQ-DEC-045 | SYSTEM_OPERATION is the fifth typed effect-gate authority source | ESTABLISHED (post-baseline, §41 REC-019) | F04 HD-17; NQ-DEC-034, NQ-DEC-043; 09 §68; 06 BND-010 | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
+| NQ-DEC-046 | AIOP-001 prototype output content; no normalized_text in F04 | ESTABLISHED (post-baseline, §41 REC-020) | F04 HD-18; 08 §23; BLOCK-08-008 | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
+| NQ-DEC-047 | MockProvider enabled in the dev runtime, marked MOCK / NON_PROOF | ESTABLISHED (post-baseline, §41 REC-021) | F04 HD-19; HARD-DEP-002; 19 §24 | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
+| NQ-DEC-048 | A mock-validated proof never counts toward BEGIN_REFLECTION for a non-fixture Session | ESTABLISHED (post-baseline, §41 REC-022) | F04 HD-20; 03 TRN-SESS-007; 13 AC-13-008 | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
+| NQ-DEC-049 | F04 AIOP scope is AIOP-001 + AIOP-002 | ESTABLISHED (post-baseline, §41 REC-023) | F04 HD-21; 12 §12; 08 §24 | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
+| NQ-DEC-050 | Derived analysis is visible to the HD-13 frozen-set audience | ESTABLISHED (post-baseline, §41 REC-024) | F04 HD-22; NQ-DEC-041 | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
+| NQ-DEC-051 | One AIOP-002 clustering run is authorized only after an accepted AIOP-001 artifact exists | ESTABLISHED (post-baseline, §41 REC-026) | F04 HD-23; 08 §24; NQ-DEC-044, NQ-DEC-045 | ARCHITECTURAL_HUMAN_DECISION | explicit human decision, 2026-09-24 |
 
 No recommendation, mock, default or implementation convenience is ESTABLISHED outside its authorized scope.
 
@@ -1848,6 +1856,62 @@ BASELINE_READINESS: BASELINE_READY_FOR_PROTOTYPE_IMPLEMENTATION pending HUMAN_RE
       "status": "ESTABLISHED",
       "post_baseline_record": "REC-016",
       "source": "F03 HD-15"
+    },
+    {
+      "id": "NQ-DEC-044",
+      "title": "A committed BEGIN_ANALYSIS authorizes exactly one system-executed AIOP-001 run",
+      "status": "ESTABLISHED",
+      "post_baseline_record": "REC-018",
+      "source": "F04 HD-16"
+    },
+    {
+      "id": "NQ-DEC-045",
+      "title": "SYSTEM_OPERATION is the fifth typed effect-gate authority source",
+      "status": "ESTABLISHED",
+      "post_baseline_record": "REC-019",
+      "source": "F04 HD-17"
+    },
+    {
+      "id": "NQ-DEC-046",
+      "title": "AIOP-001 prototype output content; no normalized_text in F04",
+      "status": "ESTABLISHED",
+      "post_baseline_record": "REC-020",
+      "source": "F04 HD-18"
+    },
+    {
+      "id": "NQ-DEC-047",
+      "title": "MockProvider enabled in the dev runtime, marked MOCK / NON_PROOF",
+      "status": "ESTABLISHED",
+      "post_baseline_record": "REC-021",
+      "source": "F04 HD-19"
+    },
+    {
+      "id": "NQ-DEC-048",
+      "title": "A mock-validated proof never counts toward BEGIN_REFLECTION for a non-fixture Session",
+      "status": "ESTABLISHED",
+      "post_baseline_record": "REC-022",
+      "source": "F04 HD-20"
+    },
+    {
+      "id": "NQ-DEC-049",
+      "title": "F04 AIOP scope is AIOP-001 + AIOP-002",
+      "status": "ESTABLISHED",
+      "post_baseline_record": "REC-023",
+      "source": "F04 HD-21"
+    },
+    {
+      "id": "NQ-DEC-050",
+      "title": "Derived analysis is visible to the HD-13 frozen-set audience",
+      "status": "ESTABLISHED",
+      "post_baseline_record": "REC-024",
+      "source": "F04 HD-22"
+    },
+    {
+      "id": "NQ-DEC-051",
+      "title": "One AIOP-002 clustering run is authorized only after an accepted AIOP-001 artifact exists",
+      "status": "ESTABLISHED",
+      "post_baseline_record": "REC-026",
+      "source": "F04 HD-23"
     }
   ],
   "packages": [
@@ -2523,3 +2587,82 @@ Successor record. Nothing in §1–§40 or REC-001..REC-010 is deleted.
 **Current counts** (superseding REC-010 for current use): Decisions 43 (ESTABLISHED 34: NQ-DEC-022, 032..043; REQUIRED 9). Canonical gaps stay 80. NQ-GAP-023, NQ-GAP-022, NQ-GAP-032 and NQ-GAP-079 stay OPEN; NQ-GAP-023 now records the prototype form rule.
 
 **Provenance.** F03 WU-03.0, authorized by the human operator's F03 instruction (2026-09-24), per `20_SYSTEM_FIELD_ENGINEERING.md` §14.
+
+### REC-018 / NQ-DEC-044: A committed BEGIN_ANALYSIS authorizes exactly one system-executed AIOP-001 run (F04 HD-16; closes C3-F04-1)
+
+- DECISION (human operator, 2026-09-24, option (b)): "Beginning analysis authorizes exactly one AI run, which the system executes right after that commit. Re-runs after a failure need an explicit controller request."
+- READING (F04 reconstruction revision 2, R1–R3, for architecture review):
+  - The run's authority is the committed human BEGIN_ANALYSIS command, recorded as SYSTEM_OPERATION (REC-019). It is not SYSTEM_DERIVED method authority, so BND-011/012 (D8) stay REQUIRE/DENY for any automatic path.
+  - No re-run is authorized after an accepted success.
+  - The authorization is consumed by the first generation referencing it.
+- NOT DECIDED at the time: the AIOP-002 invocation trigger (C3-F04-7). Decided afterwards by REC-026 / NQ-DEC-051.
+- MATERIALIZATION: F04 WU-04.1 / WU-04.5. Home-file pointer (04 AUTH-DEP-SESS-006) due in WU-04.0.
+
+### REC-019 / NQ-DEC-045: SYSTEM_OPERATION is the fifth typed effect-gate authority source (F04 HD-17; closes C3-F04-2)
+
+- DECISION (option (a)): a new typed source **SYSTEM_OPERATION**. Reference = the authorizing human command id; scope `SESSION:<id>`; re-checked at commit (that command committed, the Session is still ANALYSIS, and for acceptance the proof is VALIDATED). The actor must be SYSTEM_SERVICE.
+- WHY: 09 §68 names SYSTEM_SERVICE as the accepting actor. 06 BND-010 defers acceptance authority to 08/09, which never define it. BINDING, ROLE, FOUNDING and PARTICIPATION would fabricate provenance (HD-6 / NQ-DEC-034).
+- AFFECTS: NQ-DEC-034 / NQ-DEC-043 (typed-source set extended again), the 09 audit contract (`authority_source_type` vocabulary; CHECK change at materialization).
+- STATUS: decided, **not yet materialized**. `20_SYSTEM_FIELD_ENGINEERING.md` §7 carries a successor note.
+
+### REC-020 / NQ-DEC-046: AIOP-001 prototype output content; no normalized_text in F04 (F04 HD-18; closes C3-F04-3)
+
+- DECISION (option (b)): AIOP-001 analysis contains classification proposals, Question families, unusual-question flags, pattern descriptions and contradiction proposals. **No** additional Question suggestions. `Question.normalized_text` is not written in F04.
+- AFFECTS: BLOCK-08-008 (the AIOP-001 output schema is closed for the prototype; exact field names are implementation choices in WU-04.4). The 08 §23 "such as" list stays the broader model.
+
+### REC-021 / NQ-DEC-047: MockProvider enabled in the dev runtime, marked MOCK / NON_PROOF (F04 HD-19; closes C3-F04-4)
+
+- DECISION (option (b)): MockProvider is enabled in the dev runtime. Every generation, artifact and projection is marked mock and projected as NON_PROOF / MOCK, never as analysis of the real Questions.
+- NOT CLOSED: HARD-DEP-002 / NQ-GAP-060 (real provider eligibility; D3, D9) remain EXTERNAL_DEPENDENCY / DECISION_REQUIRED. Production must not enable the mock (19 §40 Production Readiness Gates: "Do not silently substitute MockProvider").
+
+### REC-022 / NQ-DEC-048: A mock-validated proof never counts toward BEGIN_REFLECTION for a non-fixture Session (F04 HD-20)
+
+- DECISION: "Mock-validated proof MUST NEVER count toward F05 BEGIN_REFLECTION for a non-fixture Session."
+- SCOPE: a prohibition only. Whether a mock proof may count for a fixture (NON_PROOF) Session is not decided (F05).
+- CONSEQUENCE: in a mock-only runtime, governed Sessions cannot satisfy TRN-SESS-007 until a real eligible provider exists (HARD-DEP-002) or NQ-GAP-024 is decided.
+- ENFORCEMENT HOME: F05 BEGIN_REFLECTION, via proof → generation → provider provenance.
+
+### REC-023 / NQ-DEC-049: F04 AIOP scope is AIOP-001 + AIOP-002 (F04 HD-21; closes C3-F04-5)
+
+- DECISION (option (b)): AIOP-001 plus AIOP-002 question clustering (09 §34/§35 QuestionCluster, per-run `cluster_run_id`). AIOP-004 assumptions, perspectives and AI-origin Questions are out of F04.
+- The AIOP-002 invocation trigger (C3-F04-7) was open at the time. It is decided by REC-026 / NQ-DEC-051.
+
+### REC-024 / NQ-DEC-050: Derived analysis is visible to the HD-13 frozen-set audience (F04 HD-22; closes C3-F04-6)
+
+- DECISION (option (a)): every member who can read the frozen set sees the derived analysis and clusters, with AI origin and the MOCK / NON_PROOF marker, evaluated server-side.
+
+### REC-025: Ledger reconciliation (F04 architecture revision 2)
+
+Successor record. Nothing earlier is deleted.
+
+**Current counts** (superseding REC-017 for current use):
+- Decisions: 50 (ESTABLISHED 41: NQ-DEC-022, 032..050; REQUIRED 9).
+- Canonical gaps: stay 80. No gap status changes.
+  - NQ-GAP-024, NQ-GAP-060 / HARD-DEP-002, NQ-GAP-070 (D2) and NQ-GAP-076 (D8) remain as they were.
+  - NQ-GAP-010 (cluster recomputation identity) stays OPEN. The prototype has at most one accepted run per Session under REC-018's reading.
+
+**Open Case-3 relation recorded, not closed:** C3-F04-7 (AIOP-002 invocation trigger).
+
+**Provenance.** The human operator's F04 decisions of 2026-09-24. `docs/implementation/field-reports/F04/HUMAN_DECISIONS.md`, `F04_ARCHITECTURE_RECONSTRUCTION.md` revision 2. Per `20_SYSTEM_FIELD_ENGINEERING.md` §14.
+
+### REC-026 / NQ-DEC-051: One AIOP-002 clustering run is authorized only after an accepted AIOP-001 artifact exists (F04 HD-23; closes C3-F04-7)
+
+- DECISION (human operator, 2026-09-24, option (c)), verbatim: "One AIOP-002 run becomes authorized only after an accepted AIOP-001 artifact exists. The AIOP-002 execution is SYSTEM_OPERATION and references the same BEGIN_ANALYSIS authority chain. If AIOP-001 fails or is not accepted, clustering must not run. If AIOP-002 itself fails, any retry requires an explicit controller request."
+- READING (F04 reconstruction revision 3, R7–R10, for architecture review):
+  - **R7.** The SYSTEM_OPERATION reference of the automatic clustering run is the BEGIN_ANALYSIS command. The accepted AIOP-001 artifact is a commit-time precondition, recorded as the authorizing link.
+  - **R8.** Nothing authorizes a clustering re-run after an accepted cluster run. At most one accepted cluster run per Session.
+  - **R9.** The clustering authorization is consumed by the first AIOP-002 generation referencing it. If none was created, the controller's explicit request may execute it.
+  - **R10.** The AIOP-002 input remains the verified frozen human set (08 §24). The AIOP-001 artifact authorizes the run but is not model input.
+- AFFECTS: NQ-DEC-044 (HD-16 stays AIOP-001-only), NQ-DEC-045 (SYSTEM_OPERATION reference semantics), NQ-DEC-049 (scope). NQ-GAP-010 stays OPEN, but the prototype has at most one accepted cluster run per Session.
+- MATERIALIZATION: F04 WU-04.9. Home-file pointer (08 §24) due in WU-04.0.
+
+### REC-027: Ledger reconciliation (F04 architecture revision 3)
+
+Successor record. Nothing earlier is deleted.
+
+**Current counts** (superseding REC-025 for current use):
+- Decisions: 51 (ESTABLISHED 42: NQ-DEC-022, 032..051; REQUIRED 9).
+- Canonical gaps: stay 80. No gap status changes.
+- C3-F04-7 is closed by REC-026. No F04 Case-3 relation remains open.
+
+**Provenance.** The human operator's F04 decision of 2026-09-24 ("C3-F04-7 = (c)"). `docs/implementation/field-reports/F04/HUMAN_DECISIONS.md`, `F04_ARCHITECTURE_RECONSTRUCTION.md` revision 3. Per `20_SYSTEM_FIELD_ENGINEERING.md` §14.
```

================================================================================
END PROPOSED CHANGES: docs/architecture/16_DECISION_GAP_REGISTER.md
================================================================================

================================================================================
BEGIN PROPOSED CHANGES: docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md
Unified diff of the uncommitted working copy against HEAD c9d86ba.
All lines are additions (F04 architecture revisions 2 and 3); nothing is removed.
================================================================================

```diff
diff --git a/docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md b/docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md
index 4bb194f..1e5bcad 100644
--- a/docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md
+++ b/docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md
@@ -171,6 +171,15 @@ the F02 state. F03 adds a fourth typed source, extending, not rewriting, it:
 |---|---|---|
 | PARTICIPATION | The source-explicit question-submission right of a current SessionParticipation (04 AUTH-DEP-Q-001), re-read at commit. It is not a role and not a binding | the SessionParticipation id (scope `SESSION:<id>`) |
 
+**Successor note (F04 HD-17, 16 §41 REC-019 / NQ-DEC-045). DECIDED, NOT YET
+MATERIALIZED.** F04 adds a fifth typed source, extending, not rewriting, the
+tables above. Until F04 materializes it, the effect gate still admits only
+the four sources above.
+
+| Source | Meaning | Reference recorded |
+|---|---|---|
+| SYSTEM_OPERATION | A SYSTEM_SERVICE operation executed under a committed human command that authorized it (F04: the BEGIN_ANALYSIS authorization of one AIOP-001 run, HD-16; the clustering run authorized once an AIOP-001 artifact is accepted, HD-23; and acceptance of validated AI output). Re-checked at commit: the referenced command committed, same Workspace and Session, and the operation-specific predicates (Session ANALYSIS; proof VALIDATED for acceptance). The actor must be SYSTEM_SERVICE. It is **not** SYSTEM_DERIVED method authority (D8 / BND-011 / BND-012 are untouched) and grants nothing reusable | the authorizing human command id (scope `SESSION:<id>`) |
+
 ## 8. THE RECURSION CONDITION (THREE CASES)
 
 For every unresolved next relation: *can it be legitimately derived from the
@@ -422,6 +431,37 @@ Supplied by the human operator on 2026-09-24 for Field F03. Reconciled into
 - **HD-15 (NQ-DEC-043)**: PARTICIPATION is the fourth typed effect-gate
   authority source (§7 successor note).
 
+## 15B. HUMAN DECISIONS RECORDED UNDER THIS ARCHITECTURE (F04)
+
+Supplied by the human operator on 2026-09-24 for Field F04, in answer to
+C3-F04-1..6 (`docs/implementation/field-reports/F04/HUMAN_DECISIONS.md`).
+Reconciled into 16 §41 as NQ-DEC-044..051 (REC-018..REC-027) at F04
+architecture revisions 2 and 3, before implementation.
+
+- **HD-16 (NQ-DEC-044)**: a committed BEGIN_ANALYSIS authorizes exactly one
+  AIOP-001 run, executed by the system right after that commit. Re-runs
+  after a failure need an explicit controller request.
+- **HD-17 (NQ-DEC-045)**: SYSTEM_OPERATION is the fifth typed effect-gate
+  authority source (§7 successor note; decided, not yet materialized).
+- **HD-18 (NQ-DEC-046)**: AIOP-001 content is classification proposals,
+  Question families, unusual-question flags, pattern descriptions and
+  contradiction proposals, with no additional Question suggestions.
+  `normalized_text` is not written in F04.
+- **HD-19 (NQ-DEC-047)**: MockProvider is enabled in the dev runtime. Every AI
+  run and result is marked mock and projected as NON_PROOF / MOCK.
+- **HD-20 (NQ-DEC-048)**: a mock-validated proof must never count toward F05
+  BEGIN_REFLECTION for a non-fixture Session.
+- **HD-21 (NQ-DEC-049)**: F04 AIOP scope is AIOP-001 + AIOP-002 (question
+  clustering). The AIOP-002 trigger, open at first (C3-F04-7), is decided by
+  HD-23.
+- **HD-22 (NQ-DEC-050)**: derived analysis is visible to the HD-13
+  frozen-set audience.
+- **HD-23 (NQ-DEC-051)**: one AIOP-002 clustering run is authorized only
+  after an accepted AIOP-001 artifact exists. It is executed as
+  SYSTEM_OPERATION referencing the same BEGIN_ANALYSIS authority chain. No
+  clustering runs if AIOP-001 fails or is not accepted. A retry after an
+  AIOP-002 failure needs an explicit controller request.
+
 ## 16. FINAL LAW
 
 Do not sacrifice architecture to make the product look finished. Do not
```

================================================================================
END PROPOSED CHANGES: docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md
================================================================================
