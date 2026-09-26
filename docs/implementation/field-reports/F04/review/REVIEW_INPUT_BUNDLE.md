# F04 ARCHITECTURE REVIEW — INPUT BUNDLE (revision 6)

Persistent review provenance for the F04 architecture review. This bundle
is a verbatim copy; it creates no semantics. Where it and a source file ever
differ, the source file wins.

| Property | Value |
|---|---|
| Created | 2026-09-24T21:09:37Z |
| Worktree | `.claude/worktrees/local-login-auth` |
| HEAD | `c9d86bab64505845f406ba43a8c78ac185383680` (= `origin/master`, published F03 identity commit) |
| Published F03 | `0d59ae3`, tag `field-F03` |
| Architecture revision | 6 |
| Implementation | NOT_STARTED (no First Broken Relation repair is materialized) |
| Review status | READY_FOR_F04_ARCHITECTURE_REVIEW |
| Git state | nothing staged, committed, tagged or pushed |

## Review history

| Round | Input (preserved verbatim) | Result |
|---|---|---|
| 1 | revision 3: `review/REVIEW_INPUT_BUNDLE_REV3_REVIEWED.md` (sha256 `39bc4a11173c4555…`, 1328 lines) | **ARCHITECTURE_REVIEW_HOLD**: FBR-F04-11; ledger-range drift; H-7 / H-8 reconciliation |
| 2 | revision 4: `review/REVIEW_INPUT_BUNDLE_REV4_REVIEWED.md` (sha256 `378cdf236d4d94bc…`, 1552 lines) | **ARCHITECTURE_REVIEW_HOLD**: FBR-F04-11 **PASS**; FBR-F04-12 (retry provenance branches); current-state drift |
| 3 | revision 5: `review/REVIEW_INPUT_BUNDLE_REV5_REVIEWED.md` (sha256 `a6a2edbf015f128c…`, 1715 lines) | **ARCHITECTURE_REVIEW_HOLD**: FBR-F04-11 **PASS**, FBR-F04-12 **PASS**; FBR-F04-13 (the end boundary did not admit the legal unconsumed-authorization recovery path; "consumed by exactly one", "re-runs only after failure") |
| 4 | this bundle (revision 6) | pending |

What revision 6 resolved (architecture level; not materialized):
- **FBR-F04-13**, reconstruction §0.1:
  - rule 3 corrected: an OA is consumed by **at most one** generation and
    may remain unconsumed;
  - rule 5: only the latest OA executes; a superseded OA can never execute;
  - new rule 9, **RETRY vs RECOVERY** (derived, fail-closed):
    - RETRY: a prior generation exists and is FAILED / REJECTED (carries
      `retry_of`);
    - RECOVERY: the latest OA is unconsumed and a controller-created newer
      OA supersedes it (no `retry_of`; the case and the superseded OA are
      persisted write-once);
    - neither while a generation is non-terminal or after an accepted
      result.
- **Propagated through:** the relational map, authority rows (requests
  labelled RETRY / RECOVERY), effect rows, inverse branches 2b / 4b, Work
  Units 04.5 / 04.9, the end boundary (§16, rewritten), and "re-run"
  wording that wrongly excluded RECOVERY. HD-16 and the C3-F04-7 option text
  stay verbatim.
- **Falsifiers:** E1, E7-E11, E15, K8, K12-K14 and K16 revised; E17, E18,
  K19 and K20 added.
- **Final closure sweep** from BEGIN_ANALYSIS through OA-1 to OA-4 to the end
  boundary: paths P1-P9 (§11 item 6), all admitted or refused as specified.
- **No new human decision; no new Case 3.** The ledger files 16 and 20 and
  `HUMAN_DECISIONS.md` are unchanged since revision 4.

## Source files and checksums (sha256 at bundle time)

| Part | Source | Lines | sha256 |
|---|---|---|---|
| full content | `docs/implementation/field-reports/F04/F04_ARCHITECTURE_RECONSTRUCTION.md` | 1182 | `7f872017768eec90…` |
| full content | `docs/implementation/field-reports/F04/HUMAN_DECISIONS.md` | 264 | `eef4115f5844420e…` |
| full content | `docs/implementation/field-reports/F04/STATUS.md` | 77 | `4338283065a9898b…` |
| proposed F04 changes (diff vs HEAD) | `docs/architecture/16_DECISION_GAP_REGISTER.md` | +148 / -0 | working copy `7ffb6c0680f7372f…` |
| proposed F04 changes (diff vs HEAD) | `docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md` | +40 / -0 | working copy `cda5238b26bdab25…` |


================================================================================
BEGIN FILE: docs/implementation/field-reports/F04/F04_ARCHITECTURE_RECONSTRUCTION.md  (complete current content)
================================================================================

# F04 ARCHITECTURE RECONSTRUCTION — AI BOUNDARY · POST-BURST SENSEMAKING

**Revision 6 (2026-09-24).** This revision answers the ChatGPT architecture
review of revision 5: **ARCHITECTURE_REVIEW_HOLD**, with FBR-F04-11 and
FBR-F04-12 PASS. It repairs **FBR-F04-13**: the Field end boundary did not
admit the legal unconsumed-authorization recovery path.
- It adds the fail-closed distinction **RETRY** vs **RECOVERY** (§0.1
  rule 9).
- Consumption is corrected to "at most one generation per OA".
- The distinction is propagated through the map, authority, effect, inverse
  branches, Work Units, falsifiers and end boundary.

**Revision 5 (2026-09-24).** It answered the ChatGPT architecture review of
revision 4: **ARCHITECTURE_REVIEW_HOLD**, with FBR-F04-11 PASS and
the operation-scoped authorization model accepted. It adds:
- **FBR-F04-12:** retry provenance branches in the Inverse DeepSweep, and
  persisted, immutable binding of the accepted AIOP-001 artifact for every
  AIOP-002 authorization (§0.1 rule 8);
- corrections to current-state documentation drift (ledger counts, H-7 no
  longer listed as open, NOT_STARTED / not-materialized wording).

**Implementation status: NOT_STARTED.** Every First Broken Relation below has
a defined root repair at architecture level. None is materialized in code,
schema or tests yet.

**Revision 4:** repaired the review HOLD on revision 3.
- FBR-F04-11, an authorization identity collision between AIOP-001 and
  AIOP-002, resolved at the authorization model (§0.1);
- the ledger-range drift in WU-04.0 and L-1;
- H-7 and H-8 reconciled.

Revisions 2 and 3 incorporated the human operator's answers to C3-F04-1..6
(HD-16..HD-22) and to C3-F04-7 (HD-23). Revision 1 held the analysis with the
decisions open. The options as posed are preserved verbatim in
`HUMAN_DECISIONS.md`. The reviewed input bundles are preserved in
`review/REVIEW_INPUT_BUNDLE_REV3_REVIEWED.md`,
`review/REVIEW_INPUT_BUNDLE_REV4_REVIEWED.md` and
`review/REVIEW_INPUT_BUNDLE_REV5_REVIEWED.md`.

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
- FBR-F04-11, FBR-F04-12 and FBR-F04-13 are resolved at architecture level
  by derivation from HD-16, HD-17 and HD-23. Neither is materialized
  (implementation NOT_STARTED). No new human decision was needed, and **no
  F04 Case-3 relation is open**.
- H-7 is closed by the operator's instruction: the stale F03 text is
  historical documentation drift, published history is not rewritten, and
  F04 uses the verified published identities.
- H-8 (SF-01 integration order) is open and non-blocking for this review. It
  is not a Case 3 for the architecture (§13).

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
- **R3 (HD-16; revised in revision 4, FBR-F04-11).** The BEGIN_ANALYSIS
  commit creates the operation authorization **(BEGIN_ANALYSIS,
  AIOP-001)**. It is consumed by the first AIOP-001 generation carrying that
  identity (§0.1).
  - If none was ever created (the process stopped between commit and
    invocation), that authorization stays unconsumed and is never executed
    later by the system.
  - The controller's explicit request then creates a **new** operation
    authorization **(CMD_REQUEST_QUESTION_ANALYSIS, AIOP-001)**, which
    supersedes it (§0.1 rule 5). This is within the more conservative
    human-act envelope.
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
- **R7 (HD-23; revised in revision 4, FBR-F04-11).** Acceptance of an
  AIOP-001 artifact creates the operation authorization **(C, AIOP-002)**,
  where **C is the human command that authorized the accepted AIOP-001
  artifact**: BEGIN_ANALYSIS if the artifact came from the original run,
  CMD_REQUEST_QUESTION_ANALYSIS if it came from a controller request (RETRY or
  RECOVERY, §0.1 rule 9).
  - The automatic clustering run records SYSTEM_OPERATION with **reference
    = C**. The accepted AIOP-001 artifact is the mandatory **commit-time
    precondition** and the recorded authorizing link.
  - The provenance chain still resolves to BEGIN_ANALYSIS (the "same
    BEGIN_ANALYSIS authority chain", HD-23): C is BEGIN_ANALYSIS itself, or
    a RETRY / RECOVERY request whose recorded chain reference is the Session's
    BEGIN_ANALYSIS (§0.1 rule 6).
  - A controller clustering request creates
    **(CMD_REQUEST_QUESTION_CLUSTERING, AIOP-002)**. It is either RETRY (after
    an AIOP-002 failure) or RECOVERY (an unconsumed OA-3 or older OA-4,
    revision 6). It records
    SYSTEM_OPERATION with reference = that request.
- **R8 (HD-23).** Nothing authorizes a clustering re-run after an
  **accepted** cluster run. So each Session has **at most one accepted
  cluster run** (one `cluster_run_id`). NQ-GAP-010 ("which run is current")
  therefore does not arise in the prototype. Revision 4 leaves this
  unchanged: it is a per-Session invariant, independent of authorization
  identity.
- **R9 (HD-23; revised in revision 4, FBR-F04-11).** The clustering
  authorization **(C, AIOP-002)** is consumed by the first AIOP-002
  generation carrying that identity.
  - It is **never** consumed or blocked by an AIOP-001 generation, even when
    C is BEGIN_ANALYSIS, because the operation differs (§0.1).
  - If the process stops between the AIOP-001 acceptance commit and the
    AIOP-002 generation, (C, AIOP-002) stays unconsumed and is never
    executed later by the system.
  - The controller's explicit request creates **(CMD_REQUEST_QUESTION_CLUSTERING,
    AIOP-002)**, which supersedes it (the same conservative envelope as R3).
- **R10 (HD-23).** The AIOP-001 artifact **authorizes** clustering. It is
  **not model input**: AIOP-002's input stays the verified frozen human set
  (08 §24: "Question IDs/versions, frozen set"). AI-derived content never
  feeds a second AI operation in F04, so cluster lineage stays human-sourced.

## 0.1 Operation authorization identity (revision 4 root repair of FBR-F04-11)

**Law: ROOT AUTHORITY CHAIN ≠ OPERATION AUTHORIZATION IDENTITY.**

This is derived from HD-16 ("exactly one AIOP-001 run" per BEGIN_ANALYSIS;
re-runs need a controller request), HD-17 (SYSTEM_OPERATION references "the
authorizing human command") and HD-23 (one AIOP-002 run after an accepted
AIOP-001 artifact, "the same BEGIN_ANALYSIS authority chain"; retries need a
controller request). No human decision is added. Each rule below restates
what those decisions already fix per operation.

1. **Identity.** An operation authorization is identified by
   **OA = (authorizing_command_id, ai_operation_id)** within one Session.
   Generation uniqueness and authorization consumption are keyed on OA, never
   on the command alone.
2. **The four legal OA shapes:**

   | OA | Created by (commit) | Authorizing human command | Operation | Extra commit-time precondition |
   |---|---|---|---|---|
   | OA-1 | CMD_BEGIN_ANALYSIS | BEGIN_ANALYSIS | AIOP-001 | Session ANALYSIS; no accepted AIOP-001 artifact |
   | OA-2 | CMD_REQUEST_QUESTION_ANALYSIS | that request | AIOP-001 | **RETRY** (the latest AIOP-001 generation is terminal FAILED / REJECTED) or **RECOVERY** (the latest AIOP-001 OA is unconsumed: no generation carries it); no non-terminal AIOP-001 generation; no accepted AIOP-001 artifact |
   | OA-3 | CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT (acceptance of an AIOP-001 artifact) | **C** = the authorizing command of the accepted artifact's generation (BEGIN_ANALYSIS or CMD_REQUEST_QUESTION_ANALYSIS) | AIOP-002 | **the accepted AIOP-001 artifact exists**; no accepted cluster run |
   | OA-4 | CMD_REQUEST_QUESTION_CLUSTERING | that request | AIOP-002 | an accepted AIOP-001 artifact exists; **RETRY** (the latest AIOP-002 generation is terminal FAILED / REJECTED) or **RECOVERY** (the latest AIOP-002 OA is unconsumed); no non-terminal AIOP-002 generation; no accepted cluster run |

   OA-1 and an OA-3 whose C is BEGIN_ANALYSIS share `authorizing_command_id`
   and differ in `ai_operation_id`. They are distinct authorizations, and
   neither consumes or blocks the other.
3. **Consumption (corrected in revision 6, FBR-F04-13).** An OA is consumed
   by **at most one** generation carrying it. Persistence enforces **UNIQUE
   (authorizing_command_id, ai_operation_id)** on generations, and a second
   generation for the same OA is refused.
   - An OA **may remain unconsumed**: its system execution never created a
     generation (the process stopped after the authorizing commit).
   - No rule requires every OA to be consumed.
   - An unconsumed OA is resolved only by supersession (rule 5), through
     RECOVERY (rule 9).
4. **SYSTEM_OPERATION reference.** `authority_source_ref` = the OA's
   authorizing human command. The operation identity is carried by the
   generation's `ai_operation_id` and in the authority-source proof detail,
   so the audit resolves the full OA.
5. **Supersession (fail-closed).** Per (Session, operation), only the most
   recent OA is executable, and only immediately after its own authorizing
   commit.
   - An unconsumed OA is never executed later by the system.
   - A controller request creates a newer OA that supersedes it (R3, R9).
   - A superseded OA can never execute. Any attempt is refused at the
     SYSTEM_OPERATION check.
6. **Root chain.** Every OA resolves to the Session's BEGIN_ANALYSIS (the
   persisted form is rule 8):
   - OA-1 directly.
   - OA-2 and OA-4: each request records the BEGIN_ANALYSIS command id of
     its Session as its chain reference. It is read from `establishedBy`
     of ANALYSIS, which is the unique `session:ANALYSIS` row (EC-2).
   - OA-3 through C, which is OA-1's or OA-2's command.

   The chain is provenance, **not** the authorization identity.
7. **Per-Session invariants, unchanged:** at most one accepted AIOP-001
   artifact (R2); at most one accepted cluster run (R8); one acceptance per
   generation.
9. **RETRY vs RECOVERY (revision 6, FBR-F04-13; derived, fail-closed).**
   A controller request (CMD_REQUEST_QUESTION_ANALYSIS → OA-2, or
   CMD_REQUEST_QUESTION_CLUSTERING → OA-4) is legal in exactly two
   situations. Both require the Session controller (BINDING), no accepted
   result for that operation (R2 / R8), and no non-terminal generation for
   that operation.
   - **RETRY:** a prior generation for the operation exists and is terminal
     FAILED or REJECTED. The new generation carries `retry_of` → that
     generation (08 §45: "new generation", the failed one is not revived).
   - **RECOVERY:** the latest OA for the operation was created (OA-1 by
     BEGIN_ANALYSIS, OA-3 by acceptance, or an earlier OA-2 / OA-4 by a
     request) but **no generation carries it**. The new OA supersedes it.
     The new generation carries **no** `retry_of`, because nothing failed.
     Its persisted provenance records the superseded OA (the superseded
     authorizing command id + operation), so the recovery is reconstructable
     (rule 8).
   - A stuck **non-terminal** generation (REQUESTED / RUNNING /
     OUTPUT_RECEIVED) permits neither retry nor recovery. It is a disclosed
     ceiling (F09 recovery; E10).
   - Both are consequences of HD-16 / HD-23 ("exactly one run" per
     authorization is an upper bound, never an obligation) and R3 / R9. No
     human decision is added.
   - The request command records which case applies (`RETRY` or
     `RECOVERY`) write-once, as part of its persisted provenance.
8. **Persisted authorization provenance (revision 5, FBR-F04-12).** Every
   link an inverse resolution needs is **written once, at the moment the
   authorization is created, into an immutable record**. None is re-derived
   later from mutable or "current" state.
   - **OA-1:** created by the BEGIN_ANALYSIS commit (an immutable audit row).
     The generation persists `authorizing_command_id = BEGIN_ANALYSIS` and
     `ai_operation_id = AIOP-001`.
   - **OA-2:** the CMD_REQUEST_QUESTION_ANALYSIS commit persists its
     **chain reference = the Session's BEGIN_ANALYSIS command id**. The
     generation persists `authorizing_command_id = the request` and
     `AIOP-001`.
   - **OA-3:** created by the acceptance commit of AIOP-001 artifact **X**.
     The AIOP-002 generation persists
     `authorizing_command_id = C`, `ai_operation_id = AIOP-002` and
     **`precondition_artifact_ref = X`**, where C is read from X's
     generation (an immutable identity field).
   - **OA-4:** the CMD_REQUEST_QUESTION_CLUSTERING commit persists **both**
     `accepted_analysis_artifact_ref = X` and the chain reference
     `BEGIN_ANALYSIS`. The AIOP-002 generation persists
     `authorizing_command_id = the request`, `AIOP-002` and
     `precondition_artifact_ref = X`.
   - **Immutability homes:**
     - The generation's OA fields and `precondition_artifact_ref` join the
       generation's immutable identity fields (the existing
       `4a7c1e9f2b3d` trigger's identity set, extended at materialization).
     - The request commands' references live in their committed, immutable
       record: the command row / its audit row, covered by the payload
       fingerprint.
     - The exact column is a Case 2 materialization choice. **Written once
       and never updatable** is the architectural requirement.
     - Accepted artifacts and proofs are append-only / immutable
       (FBR-F04-4/5).
   - **Commit-time check vs provenance:** at commit, the SYSTEM_OPERATION
     check **verifies** the persisted X: it exists, is an accepted AIOP-001
     artifact of this Session, and was authorized by C (OA-3). It never
     **substitutes** a fresh "current accepted artifact" read for the
     persisted reference.
   - **Inverse resolution** uses only these records: artifact / cluster →
     generation (OA + X) → authorizing command record (chain reference) →
     audit (BINDING) → BEGIN_ANALYSIS. No step reads "the currently accepted
     artifact" or "the current state".

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
| Ledger | current (revisions 3-5): 51 decisions (42 ESTABLISHED, 9 REQUIRED), 80 gaps | 16 §41 REC-027 |

**Inherited open relations:**
- NQ-GAP-024 (no way out of ANALYSIS when AI fails; F05).
- NQ-GAP-003.
- HARD-DEP-002 (real provider).
- D2 / D3 / D8 / D9.

H-7 (the stale F03 publication records) is **not** an open relation. It is
closed as historical documentation drift (§13).

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
          │  creates OA-1 = (BEGIN_ANALYSIS, AIOP-001) (HD-16) → consumed by at most one generation; may remain unconsumed → RECOVERY (§0.1 rules 3, 5, 9)
          ▼  system executes, immediately after commit
      CMD_AI_QUESTION_ANALYSIS   actor SYSTEM_SERVICE   source SYSTEM_OPERATION(ref = BEGIN_ANALYSIS; OA-1)
          │  BND-007(ANALYSIS) → BND-008(COMPLETED, verified F) → BND-009(contract, manifest, Gateway only)
          ▼
      AIContextManifest (immutable; inputs = burst:<id> + F + question ids + original_text digests)
          ▼ AI Gateway → MockProvider (dev runtime, HD-19) → validator (closed HD-18 schema)
      AIGeneration → VALIDATED | REJECTED | FAILED   +  AI_VALIDATION_PROOF (persisted, immutable)
          ▼ candidate (not an effect)
      CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT  actor SYSTEM_SERVICE  source SYSTEM_OPERATION  BND-010 → BND-014
          ▼
      Derived analysis artifact (AI origin, provider=mock, NON_PROOF) — at most one accepted per Session (R2)

   [RETRY: after a FAILED/REJECTED AIOP-001 generation]   controller: CMD_REQUEST_QUESTION_ANALYSIS (BINDING) → OA-2 → new generation, retry_of lineage
   [RECOVERY: OA-1 (or the latest OA-2) unconsumed, no generation]  controller: CMD_REQUEST_QUESTION_ANALYSIS (BINDING) → OA-2 supersedes it → new generation, no retry_of
   [AIOP-002, HD-23]  only after an ACCEPTED AIOP-001 artifact exists (no clustering if AIOP-001 fails or is not accepted):
               system runs at most one CMD_AI_QUESTION_CLUSTERING per OA  actor SYSTEM_SERVICE (OA-3 may remain unconsumed → RECOVERY)
                  OA-3 = (C, AIOP-002), created at AIOP-001 acceptance; C = the human command that authorized the accepted artifact
                  source SYSTEM_OPERATION(ref = C; precondition link = accepted AIOP-001 artifact; chain → BEGIN_ANALYSIS)
                  input = verified frozen set only (R10)
               → generation + proof → CMD_ACCEPT_CLUSTERING_OUTPUT (SYSTEM_OPERATION; BND-010 → BND-014)
               → QuestionCluster + memberships (one cluster_run_id) — at most one accepted cluster run per Session (R8)
   [RETRY: after a FAILED/REJECTED AIOP-002 generation]   controller: CMD_REQUEST_QUESTION_CLUSTERING (BINDING) → OA-4 → new generation, retry_of lineage
   [RECOVERY: OA-3 (or the latest OA-4) unconsumed, no generation]  controller: CMD_REQUEST_QUESTION_CLUSTERING (BINDING) → OA-4 supersedes it → new generation, no retry_of
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
| Operation authorization OA (§0.1) | created → consumed (by **at most one** generation carrying OA) \| unconsumed (no generation; legal) → superseded (a newer controller-created OA for the same Session and operation, RECOVERY) | **yes** | keyed on (authorizing_command_id, ai_operation_id). OA-1 at BEGIN_ANALYSIS; OA-2 at an AIOP-001 re-run request; OA-3 at AIOP-001 acceptance (never while no accepted artifact exists); OA-4 at a clustering re-run request |
| QuestionCluster run | absent → accepted (one `cluster_run_id`) | **yes (WU-04.9)** | 09 §34/§35; at most one accepted run per Session (R8) |
| Burst / Question / membership / fingerprint | none | **forbidden** | STATE-INV-04/05 |

Resolved conflict C1: 12 §10 lists `QUESTION_GENERATION -> ANALYSIS`; 03
governs, and that transition is illegal.

## 5. Authority map (final)

| Operation | Actor | Authority | Effect-gate source | Re-checked at commit |
|---|---|---|---|---|
| CMD_BEGIN_ANALYSIS | human | `SESSION_CONTROL_RIGHT` at `SESSION:<id>` (04 AUTH-DEP-SESS-006 human path + HD-1). The System path is REQUIRE/DENY (D8) | BINDING | binding, Session QUESTION_CAPTURE, frozen set verified |
| CMD_AI_QUESTION_ANALYSIS (the authorized run) | SYSTEM_SERVICE | OA-1 = (BEGIN_ANALYSIS, AIOP-001) (HD-16), unconsumed and latest (§0.1) | **SYSTEM_OPERATION** (ref = BEGIN_ANALYSIS command id; OA-1) | that command committed; Session still ANALYSIS; OA-1 unconsumed and not superseded; no accepted AIOP-001 artifact (R2) |
| CMD_REQUEST_QUESTION_ANALYSIS (**RETRY or RECOVERY**, §0.1 rule 9) | human controller | `SESSION_CONTROL_RIGHT` at SESSION. Allowed only for RETRY (the latest AIOP-001 generation is terminal FAILED / REJECTED) or RECOVERY (the latest AIOP-001 OA is unconsumed, R3), with no non-terminal AIOP-001 generation and no accepted artifact (R2). It creates OA-2 (superseding any unconsumed OA) and records the chain reference BEGIN_ANALYSIS and the case, write-once | BINDING | binding; state predicates |
| system execution of that request | SYSTEM_SERVICE | OA-2 = (request, AIOP-001) | SYSTEM_OPERATION (ref = request command id; OA-2) | request committed; OA-2 unconsumed and latest; Session ANALYSIS; no accepted AIOP-001 artifact |
| CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT | SYSTEM_SERVICE | HD-17 | SYSTEM_OPERATION (ref = the OA's authorizing human command of that generation) | authorizing command committed; Session ANALYSIS; generation VALIDATED; persisted proof VALIDATED; the generation carries that OA; no prior acceptance. **Creates OA-3** = (that command, AIOP-002) |
| CMD_AI_QUESTION_CLUSTERING (the authorized run) | SYSTEM_SERVICE | **HD-23**: OA-3 = (C, AIOP-002), existing only once an accepted AIOP-001 artifact exists | **SYSTEM_OPERATION** (ref = C, the human command that authorized the accepted AIOP-001 artifact; the accepted artifact is the precondition link, R7) | C committed; Session ANALYSIS; an accepted AIOP-001 artifact exists for this Session, authorized by C; OA-3 unconsumed and latest; no accepted cluster run (R8) |
| CMD_REQUEST_QUESTION_CLUSTERING (**RETRY or RECOVERY**, §0.1 rule 9) | human controller | `SESSION_CONTROL_RIGHT` at SESSION. Allowed only when an accepted AIOP-001 artifact exists, for RETRY (the latest AIOP-002 generation is terminal FAILED / REJECTED) or RECOVERY (the latest AIOP-002 OA is unconsumed, R9), with no non-terminal AIOP-002 generation and no accepted cluster run (R8). It creates OA-4 (superseding any unconsumed OA) and records BEGIN_ANALYSIS, X and the case, write-once | BINDING | binding; state predicates |
| system execution of that request | SYSTEM_SERVICE | OA-4 = (request, AIOP-002) | SYSTEM_OPERATION (ref = request command id; OA-4) | request committed; OA-4 unconsumed and latest; accepted AIOP-001 artifact exists; no accepted cluster run |
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
- **RETRY / RECOVERY request:** 001-003 → 005 BINDING → 007 → predicates (R2/R3, §0.1 rule 9) →
  014 BINDING, creating OA-2. Its execution follows the system run path with
  SYSTEM_OPERATION on OA-2.
- **AIOP-002 (HD-23):** SYSTEM_SERVICE identity → 002 → **SYSTEM_OPERATION
  check** on OA-3 (C committed; **an accepted AIOP-001 artifact authorized
  by C exists for this Session**; OA-3 unconsumed and latest; no accepted
  cluster run) →
  007 (Session ANALYSIS) → 008 (COMPLETED, verified F) → 009 (AIOP-002
  contract; manifest = frozen set only) → Gateway → validator → persisted
  proof → acceptance 010 → 014 SYSTEM_OPERATION → 015 (08 §24 boundary path
  BND-007/008/009/010/014/015).
- **Clustering RETRY / RECOVERY request:** 001-003 → 005 BINDING → 007 → predicates
  (accepted AIOP-001 artifact exists; R8/R9) → 014 BINDING, creating OA-4.
- **Failure:** provider timeout or error → FAILED, no consequence, Session
  stays ANALYSIS. An INDETERMINATE commit → BND-017; no blind retry. A stuck
  non-terminal generation blocks both RETRY and RECOVERY (a disclosed ceiling; F09
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
| Idempotent | BEGIN_ANALYSIS; the RETRY / RECOVERY requests; the authorized runs (one generation per operation authorization OA = (authorizing command, operation), §0.1); acceptance (one per generation) |
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
- **The generation records:**
  - provider `mock`, model, prompt version, the invoking command id,
    correlation, retry lineage, failure code;
  - **immutably, the operation authorization (`authorizing_command_id`,
    `ai_operation_id`) and, for AIOP-002, `precondition_artifact_ref`**
    (§0.1 rule 8).
- **The request commands** (CMD_REQUEST_QUESTION_ANALYSIS,
  CMD_REQUEST_QUESTION_CLUSTERING) record immutably their chain reference
  (BEGIN_ANALYSIS). The clustering request also records the accepted
  AIOP-001 artifact it depends on.
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
| authorized run | SYSTEM_OPERATION → 007/008/009 | generation + proof (operational) | a call before COMPLETED; a call outside the Gateway; a second run per OA; execution of a superseded OA |
| validated output | 010 → 014 SYSTEM_OPERATION | one accepted artifact (AI, MOCK) | Question/membership/F change; Session advance; selection / Decision / Evidence / Assumption; human attribution; a second accepted artifact |
| controller request (RETRY or RECOVERY) | 005 → 014 BINDING | a new OA-2 (RECOVERY: supersedes the unconsumed OA) | a request after an accepted success; a request while a generation is non-terminal; execution of the superseded OA |
| AIOP-001 acceptance (as a side relation) | — | creates OA-3 = (C, AIOP-002): exactly one clustering run (HD-23) | OA-3 when AIOP-001 failed, was rejected or was not accepted |
| authorized clustering run | SYSTEM_OPERATION → 007/008/009 | generation + proof (operational) | a run before AIOP-001 acceptance; a second run per OA; blocking by the AIOP-001 generation of the same root command; AIOP-001 output as model input |
| clustering output | 010 → 014 SYSTEM_OPERATION | QuestionCluster + memberships (one accepted run per Session) | a Question identity change; a priority grant; a second accepted cluster run |
| controller clustering request (RETRY or RECOVERY) | 005 → 014 BINDING | a new OA-4 (RECOVERY: supersedes the unconsumed OA) | a request after an accepted cluster run; a request while no accepted AIOP-001 artifact exists; a request while a generation is non-terminal; execution of the superseded OA |
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
  - Session control handler reuse (`_run`) for BEGIN_ANALYSIS and the
    RETRY / RECOVERY requests.
  - `establishedBy`: only BEGIN_ANALYSIS writes `session:ANALYSIS`.
  - BND-008 is shared with capture: the FBR-F04-3 repair must keep every F03
    capture test green.
- **Persistence (at materialization).**
  - proof table;
  - manifest immutability trigger;
  - artifact append-only trigger;
  - `question_clusters` + `question_cluster_memberships` (09 §34/§35);
  - audit CHECK + SYSTEM_OPERATION;
  - uniqueness: **one generation per operation authorization, UNIQUE
    (authorizing_command_id, ai_operation_id)** (§0.1, revision 4); one
    acceptance per generation; one accepted AIOP-001 artifact per Session;
    one accepted cluster run per Session;
  - the RETRY / RECOVERY request commands record the Session's BEGIN_ANALYSIS command
    id as chain reference (§0.1 rule 6).
- **Runtime.**
  - MockProvider enabled by dev configuration only (HD-19 / R4).
  - Production-profile config must refuse the mock (19 §40, line 2786).
  - The worker stays out: synchronous execution after the BEGIN_ANALYSIS
    commit, in separate transactions (T1 transition → T2 invocation records
    + provider call + proof → T3 acceptance). Case 2.
- **API** (F02 envelope):
  - `…/transitions/begin-analysis`;
  - `…/analysis/request` (controller RETRY / RECOVERY);
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
  - An "analysis unavailable" state with a RETRY / RECOVERY control from
    server capability.
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
    of the automatic clustering authorization OA-3 (§0.1).
    - Is creating the authorization in the same commit as acceptance a new
      authority-bearing write? No. It is operational state implied by HD-23,
      and it is represented by the accepted artifact itself.
    - Revision 4: OA-3 = (C, AIOP-002) is derivable from the accepted
      artifact (its generation carries C). The clustering run's
      SYSTEM_OPERATION check reads "an accepted AIOP-001 artifact authorized
      by C exists, and no AIOP-002 generation carries (C, AIOP-002)". So no
      separate authorization row is required. Materialization as an
      explicit row or as a derived check is Case 2, as long as §0.1 holds.
  - **Consumers:** the projection shows clusters only after acceptance, and
    "clustering not run" when AIOP-001 failed or was not accepted. That is
    an honest state, not an error.
  - **Execution chain (Case 2):** synchronous in the same request after the
    AIOP-001 acceptance commit (T3 → T4 invocation → T5 acceptance). The
    same applies after an OA-2 artifact (RETRY or RECOVERY) is accepted.
  - **Siblings:** HD-16 is unchanged (AIOP-001-only authorization).
  - **SYSTEM_OPERATION (HD-17)** covers four operation authorizations, OA-1
    to OA-4 (§0.1). Each is identified by (command, operation) and re-checks
    its own predicates. Revision 4 removed the collision in which OA-1 and
    OA-3 shared the key "BEGIN_ANALYSIS".
  - **Persistence:** `question_clusters` + `question_cluster_memberships`
    (09 §34/§35). Uniqueness: one AIOP-002 generation per OA; one accepted
    cluster run per Session.
  - **Tests:** the K group, extended.
- **Ledger:** HD-16..23 reconciled (NQ-DEC-044..051, REC-018..027).
  Revision 4 amends the readings in REC-018 and REC-026 (unpublished
  records, amended in place) to the §0.1 identity. No F04 Case-3 relation is
  open. H-7 is closed (historical drift). H-8 is open and non-blocking.
- **Revision-6 re-sweep (FBR-F04-13), the affected edges:**
  - **Authorization model:** consumption is at most once per OA (rule 3); an
    unconsumed OA is legal and is resolved only by supersession (rule 5).
    RETRY and RECOVERY are distinguished by persisted state (rule 9).
  - **Producers:** the two request commands now persist the case (RETRY /
    RECOVERY) and, for RECOVERY, the superseded OA.
  - **Consumers:** generation `retry_of` exists only for RETRY.
  - **Effect gate:** the SYSTEM_OPERATION check refuses a superseded OA; the
    request check refuses a non-terminal generation and a mismatched case.
  - **Projection:** the controller capability is offered for both cases,
    with the server's reason.
  - **End boundary:** rewritten (§16).
  - **Falsifiers:** E1, E7, E8-E11, E15, K8, K12-K14 and K16 revised; E17,
    E18, K19 and K20 added.
  - Nothing else moves: authority classes, Session state, the frozen set,
    persisted provenance (rule 8), and the per-Session invariants.
- **Revision-5 re-sweep (FBR-F04-12), the affected edges:**
  - **Producer:** the two request commands now persist their chain reference,
    and the clustering request persists X.
  - **Consumer:** the AIOP-002 generation persists X immutably. The
    generation identity-field trigger gains the OA fields and X (at
    materialization).
  - **Effect gate:** the SYSTEM_OPERATION check verifies the persisted X; it
    never substitutes a fresh read.
  - **Audit / provenance:** the inverse resolver walks immutable records
    only.
  - **Projection:** it may show the lineage (generation → OA → command) but
    derives none of it.
  - **Tests:** E7, E11, E15, K11, K14 and K16 re-evaluated; E16, K17 and K18
    added.
  - Nothing else moves: authority, Session state, frozen set, and the
    per-Session invariants.
- **Revision-4 re-sweep (FBR-F04-11), outward from the authorization model:**
  - **Producer:** BEGIN_ANALYSIS (OA-1), the analysis acceptance (OA-3) and
    the two request commands (OA-2, OA-4).
  - **Consumers:** the generations, uniquely keyed on OA.
  - **Effect gate:** the SYSTEM_OPERATION check resolves OA, not the command
    alone.
  - **Audit:** reference = the OA's command. The operation comes from the
    generation or the proof detail.
  - **Projection:** unaffected (it reads generations and acceptances).
  - **Tests:** C8, E1, E2, E6, E11, K8, K9, K13 and K14 re-evaluated, and
    C9, E15, K15 and K16 added (§15).
  - Nothing else changes: frozen set, Session state, HD-18/19/20/22 and the
    per-Session invariants.

## 11. Inverse DeepSweep (final)

1. **"Session is in ANALYSIS"**
   - Chain: projection ← Session row ← CMD_BEGIN_ANALYSIS commit
     (`establishedBy`) ← BND-014 BINDING `SESSION:<id>` ← grant ← FOUNDING ←
     login.
   - Preconditions proven by the COMPLETED Burst, `verify_frozen_set`, and
     no unresolved capture.
   - **Complete.**
2. **Visible derived analysis.** Two legal branches (revision 5,
   FBR-F04-12). Every step is resolved from persisted immutable records
   (§0.1 rule 8).
   - **2a, original success:** projection (HD-22 audience) ← accepted
     AIOP-001 artifact ← acceptance commit (SYSTEM_OPERATION, ref =
     BEGIN_ANALYSIS) ← BND-010 ← persisted proof VALIDATED ← generation
     VALIDATED carrying **OA-1 = (BEGIN_ANALYSIS, AIOP-001)** ←
     **BEGIN_ANALYSIS** ← BND-014 **BINDING** `SESSION:<id>` ← **controller**
     (grant ← FOUNDING ← login).
   - **2b, controller request success (RETRY or RECOVERY):** projection ←
     accepted AIOP-001 artifact ← acceptance commit (SYSTEM_OPERATION, ref =
     the request) ← BND-010 ← persisted proof VALIDATED ← generation
     VALIDATED carrying **OA-2 = (CMD_REQUEST_QUESTION_ANALYSIS, AIOP-001)**.
     - *RETRY:* with `retry_of` → the prior FAILED / REJECTED generation.
     - *RECOVERY:* no `retry_of`; the request's persisted provenance names
       the superseded unconsumed OA (e.g. OA-1).

     ← **CMD_REQUEST_QUESTION_ANALYSIS**
     (committed, BND-014 **BINDING** `SESSION:<id>`, **controller**) →
     persisted **chain reference BEGIN_ANALYSIS** ← BEGIN_ANALYSIS ← BINDING
     ← controller.
   - Both branches continue: generation ← Gateway ← manifest = verified F ←
     Session ANALYSIS ← frozen set ← human captures.
   - **The provider link is MockProvider.** It is disclosed in every record
     and projection as MOCK / NON_PROOF (HD-19). Per 20 §11 this chain is a
     **mock-ceiling proof**, never a real-analysis proof. It will be complete
     *as a mock-ceiling chain* only once FBR-F04-1/4/5/6/7/8 are
     **materialized**. Today it is architecturally defined, not
     implemented.
3. **"Analysis unavailable"**
   - Chain: projection ← generation FAILED / REJECTED ← Gateway ← authorized
     run.
   - The request control comes from the server capability (controller,
     R2/R3). The request (RETRY here; RECOVERY when no generation exists)
     creates OA-2, and its success resolves as branch 2b.
   - **Complete.**
4. **Visible clusters (HD-23).** Two legal branches (revision 5,
   FBR-F04-12). The accepted AIOP-001 artifact X is resolved from the
   **persisted** `precondition_artifact_ref` (and, for OA-4, the request's
   persisted reference), never from current state (§0.1 rule 8).
   - **4a, automatic clustering success:** projection (HD-22 audience) ←
     QuestionCluster + memberships (one `cluster_run_id`) ←
     CMD_ACCEPT_CLUSTERING_OUTPUT (SYSTEM_OPERATION, ref = C) ← BND-010 ←
     persisted proof VALIDATED ← AIOP-002 generation VALIDATED carrying
     **OA-3 = (C, AIOP-002)** and `precondition_artifact_ref = X` ← **C** ←
     **accepted AIOP-001 artifact X** ← **X's OA** (OA-1 → branch 2a, or
     OA-2 → branch 2b) ← **BEGIN_ANALYSIS**.
   - **4b, controller clustering request success (RETRY or RECOVERY):**
     projection ← QuestionCluster + memberships ← CMD_ACCEPT_CLUSTERING_OUTPUT
     (SYSTEM_OPERATION, ref = the clustering request) ← BND-010 ← persisted
     proof VALIDATED ← AIOP-002 generation VALIDATED carrying **OA-4 =
     (CMD_REQUEST_QUESTION_CLUSTERING, AIOP-002)** and
     `precondition_artifact_ref = X`.
     - *RETRY:* with `retry_of` → the prior failed AIOP-002 generation
       (OA-3 or an earlier OA-4).
     - *RECOVERY:* no `retry_of`; the request names the superseded
       unconsumed OA-3 (or an earlier OA-4).

     ←
     **CMD_REQUEST_QUESTION_CLUSTERING** (committed, BINDING, controller;
     its persisted `accepted_analysis_artifact_ref = X` and chain reference)
     → **accepted AIOP-001 artifact X as required historical precondition**
     ← **X's OA** (OA-1 / 2a or OA-2 / 2b) ← **BEGIN_ANALYSIS**.
   - Both branches continue: generation ← Gateway ← manifest = verified F
     (frozen human Questions only, R10) ← frozen set ← human captures.
   - The provider link is MockProvider, marked MOCK / NON_PROOF (HD-19).
   - It will be **complete as a mock-ceiling chain** only once
     FBR-F04-1/4/5/6/7/8/9 and the §0.1 rule-8 fields are **materialized**.
     Today it is architecturally defined, not implemented.
   - Negative inverse: if the AIOP-001 artifact link is absent (failed or
     not accepted), **no** cluster, generation or authorization can exist
     for this Session. That is the falsifier K7.
5. **A persisted generation, one per operation authorization (§0.1):**
   - Chain: generation (carries OA = authorizing command + operation and,
     for AIOP-002, X) → invoking system command → SYSTEM_OPERATION → the
     human command → its persisted chain reference → root BEGIN_ANALYSIS.
     All four shapes, OA-1 to OA-4, resolve this way.
   - An AIOP-001 generation and an AIOP-002 generation may legally share the
     root command BEGIN_ANALYSIS, because their OAs differ.
   - The PKG-era Gateway's unlinked write path is FBR-F04-7.

6. **Final closure sweep (revision 6): from BEGIN_ANALYSIS through all four
   OA shapes to the end boundary.** Every reachable path ends in a state §16
   admits.

   | Path | OA sequence | Terminal state | Admitted by §16 |
   |---|---|---|---|
   | P1 original success | OA-1 consumed → accepted → OA-3 consumed → cluster accepted | 1 artifact, 1 cluster run | yes |
   | P2 analysis retry | OA-1 consumed (FAILED) → OA-2 RETRY consumed → accepted → OA-3 (C = request) … | 1 artifact | yes |
   | P3 analysis recovery | OA-1 **unconsumed** → OA-2 RECOVERY (supersedes OA-1) consumed → accepted → OA-3 … | 1 artifact; OA-1 superseded, never executed | **yes (FBR-F04-13)** |
   | P4 repeated recovery | OA-2 unconsumed → OA-2′ RECOVERY supersedes it | as P3 | yes |
   | P5 clustering retry | OA-3 consumed (FAILED) → OA-4 RETRY consumed → accepted | 1 cluster run | yes |
   | P6 clustering recovery | OA-3 **unconsumed** → OA-4 RECOVERY (supersedes OA-3) consumed → accepted | 1 cluster run; OA-3 superseded | **yes (FBR-F04-13)** |
   | P7 analysis never accepted | OA-1 / OA-2 all FAILED / REJECTED, no further request | Session ANALYSIS, "analysis unavailable"; no OA-3 exists | yes (HD-23: no clustering) |
   | P8 stuck generation | a generation non-terminal | no RETRY / RECOVERY possible; disclosed ceiling (F09) | yes, disclosed |
   | P9 forbidden | execute a superseded OA; a second generation per OA; any request after an accepted result; clustering without an accepted artifact | — | refused (C8, E6, E8, E11, K7, K13, K14) |

   All accepted results resolve through persisted provenance (rule 8) to
   BEGIN_ANALYSIS in every row. No path requires a new human decision.
   **No new Case 3.**

## 12. First Broken Relations

All are derivable, and each has a defined root repair. **None is
materialized:** implementation is NOT_STARTED. The "Repair" column states
what implementation must build at each home.

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
| FBR-F04-10 | Published F03 publication records are stale | F03 `STATUS.md:10-12`, `FIELD_REVIEW.md:137` | F03 reports | **Closed by H-7 resolution:** historical documentation drift; published history is not rewritten; F04 uses the verified published identities (`0d59ae3`, `field-F03` → `0d59ae3`, `origin/master` `c9d86ba`) |
| FBR-F04-13 | **The Field end boundary did not admit the legal unconsumed-authorization recovery path (found by the architecture review, revision 5).** It said "OA-1 … consumed by exactly one system run" and "controller re-runs only after failure". Both are false under R3 / R9 / E11 / K14, where an unconsumed OA-1 / OA-3 is superseded by a controller-created OA-2 / OA-4 | revision-5 §16; §0.1 rule 3 ("consumed by exactly one generation") | the F04 authorization model and end boundary (derived from HD-16, HD-23, R3, R9) | **Resolved at architecture level (revision 6):** §0.1 rule 3 (at most once), rule 5 (supersession), rule 9 (RETRY vs RECOVERY, persisted case); end boundary rewritten; E1, E11, K8 and K14 revised; E17, E18, K19 and K20 added. Not materialized |
| FBR-F04-12 | **Retry provenance branches missing (found by the architecture review, revision 4).** The final Inverse DeepSweep resolved every accepted AIOP-001 artifact directly through BEGIN_ANALYSIS and described clusters through OA-3 only. The accepted-artifact identity behind an OA-4 was not bound to persisted provenance | revision-4 §11 items 2 and 4; §0.1 rules 1-7 | the F04 provenance model (derived from HD-16, HD-17, HD-23; 09 §118) | **Resolved at architecture level (revision 5):** §0.1 rule 8 (write-once OA fields, `precondition_artifact_ref`, request-command chain / artifact references); inverse branches 2a/2b and 4a/4b; falsifiers E16, K17, K18. Not materialized |
| FBR-F04-11 | **Authorization identity collision (found by the architecture review, revision 3).** R3 consumed "the BEGIN_ANALYSIS authorization" with the first AIOP-001 generation. The automatic AIOP-002 run also referenced BEGIN_ANALYSIS. Uniqueness was "one generation per authorizing command" (C8), so a legal AIOP-002 generation became impossible | revision-3 §0 R3/R7/R9, §10, §15 C8 | the F04 authorization model (derived from HD-16/17/23) | **Resolved at the authorization model (revision 4, §0.1); not materialized:** OA = (authorizing command, operation); uniqueness and consumption keyed on OA; the clustering reference = the command that authorized the accepted AIOP-001 artifact; the root chain is provenance, not identity |

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
| H-7 | **CLOSED (operator instruction, revision 4):** do not rewrite published F03 history. The stale F03 report text is historical documentation drift; F04 uses the verified published identities |
| H-8 | **OPEN, non-blocking; not a Case 3 for the F04 architecture.** Current SF-01 state (verified read-only, revision 4): Field commit `447b24e`, documentation identity commit `c944b95`; worktree `/home/codi/Entwicklung/nquiry/worktrees/frontend-symbiotic`, branch `frontend-symbiotic`; clean, locally committed, **not tagged, not pushed**; parent line is F02 `bea864b`, so F03 `c9d86ba` is not in its history; **F03 integration not started**. The F04 architecture is independent of SF-01: WU-04.8 renders server projections only. The integration order of SF-01 relative to F03/F04 is a publication / integration decision, made by human authority when WU-04.8 starts; it is not resolved here. Not caused or modified by the F04 work |

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
                         WU-04.5 authorized run + acceptance + controller RETRY/RECOVERY (HD-16/17; FBR-1,2,7,13)
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
| 04.0 | decisions → home files | NQ-DEC-044..051 / REC-018..027 (HD-16..HD-23) → pointers in 04 AUTH-DEP-SESS-006, 06 BND-010, 08 §23/§24, 09 §68 | human (given) | — | docs | — | every HD referenced at its home | an unrecorded semantic choice | L-1 | — |
| 04.1 | Session phase + authorization | QUESTION_CAPTURE → ANALYSIS | BINDING `SESSION:<id>`; 005/007/008/014 | CMD_BEGIN_ANALYSIS; `…/transitions/begin-analysis`; `BEGIN_ANALYSIS` capability | Session; audit `session:ANALYSIS`; outbox | action + reason; `establishedBy` | a controller begins; exactly OA-1 = (BEGIN_ANALYSIS, AIOP-001) exists | non-controller begin; bad state; unverified F; unresolved capture; stale; double begin; any AI call in this commit | A1-A10 | 04.0 |
| 04.2 | protected set ↔ AI | — | 008/009 | — | — | — | AI categories denied while ACTIVE/PAUSED for any requester; BND-009 requires COMPLETED + verified F | a human- or system-requested AI op during the Burst | B1-B4 | — |
| 04.3 | effect gate + AI records + operation authorization identity | — | BND-014 SYSTEM_OPERATION (resolves OA, §0.1) | — | audit CHECK +SYSTEM_OPERATION; proof table; manifest immutable; artifact append-only; UNIQUE (authorizing_command_id, ai_operation_id) on generations; chain reference on request commands | — | SYSTEM_OPERATION resolves only for SYSTEM_SERVICE with a committed referenced command and a matching OA | a fabricated / human / AI SYSTEM_OPERATION; mutation of proof / manifest / artifact; two generations per OA | C1-C9 | 04.0 |
| 04.4 | AIOP-001 contract + input | verified F → manifest | BND-009 | — | registered contract; manifest | — | manifest = F exactly; closed HD-18 schema validated deterministically; mock output conforms, marked | foreign / extra / missing Question; unverified F; a new-question field; schema-invalid VALIDATED | D1-D8 | 04.3 |
| 04.5 | run → candidate → accepted artifact; controller RETRY / RECOVERY | ANALYSIS → gen terminal → ≤1 accepted artifact | HD-16/17; 009/010/014 | CMD_AI_QUESTION_ANALYSIS; CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT; CMD_REQUEST_QUESTION_ANALYSIS; `…/analysis/request` | generation, proof, artifact | — | at most one generation per OA-1 / OA-2; OA-1 either consumed or superseded by OA-2 (RECOVERY); one acceptance per VALIDATED generation; acceptance creates OA-3 | a second run per OA; execution of a superseded OA; a request while a generation is non-terminal; a re-run after accepted success; acceptance of REJECTED / FAILED; Session / Question change; AI self-invocation | E1-E18 | 04.2, 04.4 |
| 04.6 | mock lane | — | 11 fail-closed | — | `provider = mock` | MOCK / NON_PROOF; unavailable | dev-only mock; every artifact marked; proof carries resolvable provider identity (HD-20 enforceable) | mock in the production profile; an unmarked mock; a real provider call | F1-F6 | 04.5 |
| 04.9 | clustering | accepted AIOP-001 artifact + frozen set → ≤1 accepted cluster run | HD-21, HD-23; SYSTEM_OPERATION on OA-3 (ref = C) / OA-4, BINDING (RETRY / RECOVERY request); 009/010/014 | CMD_AI_QUESTION_CLUSTERING; CMD_ACCEPT_CLUSTERING_OUTPUT; CMD_REQUEST_QUESTION_CLUSTERING; `…/analysis/clustering/request` | `question_clusters`, `question_cluster_memberships` (09 §34/35); uniqueness per OA and per Session; write-once `precondition_artifact_ref` and request references (§0.1 rule 8) | "clustering not run" / clusters | at most one automatic clustering run per OA-3 after AIOP-001 acceptance (OA-3 consumed, or superseded by OA-4 via RECOVERY), never blocked by the AIOP-001 generation of the same root command; clusters reference only frozen Questions | clustering without an accepted AIOP-001 artifact; AIOP-001 output as input; a second run per OA; a re-run after an accepted cluster run; membership / Question mutation; a priority grant | K1-K20 | 04.5 |
| 04.7 | read side | — | read chain (HD-22 = HD-13 audience) | `position.analysis` | — | status, generations, accepted artifact, clusters, provenance, MOCK marker | server-side audience; AI origin explicit | merged human / AI provenance; client-side visibility | G1-G5 | 04.1, 04.5, 04.6, 04.9 |
| 04.8 | frontend | — | projection only | — | — | ANALYSIS phase; derived field; markers; human primary; no chat | the real-stack flow §15 H | client authority; chat; AI text shown as human; mock shown as real | H1-H7 | 04.7 |
| 04.10 | proof | — | — | — | — | — | L0-L8; the mock ceiling documented | a mock claimed as real | full ladder | all |

## 15. Final TDD / falsifier matrix

**L — ledger**
- **L-1:** 16 §41 REC-018..REC-027, the §6 rows NQ-DEC-044..051, the YAML
  (51 decisions, 80 gaps) and 20 §15B HD-16..HD-23 agree (a count check).

**A — BEGIN_ANALYSIS (04.1)**
- **A1 happy path:** the controller begins. Session ANALYSIS, version +1,
  audit BINDING `SESSION:<id>`, `establishedBy` resolves, and exactly one
  unconsumed OA-1 = (BEGIN_ANALYSIS, AIOP-001) exists.
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
- **C8 (revised in revision 4):** a second generation for the same
  **operation authorization** (authorizing_command_id, ai_operation_id) →
  refused.
- **C9 (revision 4, FBR-F04-11):** an AIOP-001 generation carrying
  (BEGIN_ANALYSIS, AIOP-001) and an AIOP-002 generation carrying
  (BEGIN_ANALYSIS, AIOP-002) **both persist**. The same root command with a
  different operation is not a collision.

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

**E — run, acceptance, RETRY / RECOVERY (04.5)**
- **E1 (revised in revision 6):** after BEGIN_ANALYSIS, the system executes
  **at most one** AIOP-001 run for OA-1. In the normal path exactly one
  generation carries OA-1 = (BEGIN_ANALYSIS, AIOP-001) (R3). If none is
  created, OA-1 stays unconsumed, and that is a legal state (E11 RECOVERY).
- **E2:** validated → exactly one accepted artifact, with 09 §118 lineage
  and a SYSTEM_OPERATION audit whose ref is the OA's command (BEGIN_ANALYSIS
  for OA-1, the request for OA-2).
- **E3:** REJECTED or FAILED → acceptance blocked, with no artifact.
- **E4:** the artifact exists only via the acceptance commit; a static gate
  shows the Gateway has no artifact write.
- **E5:** acceptance changes no Session, Question, membership or F
  (snapshot diff).
- **E6:** a second system run for the same OA → refused.
- **E7 RETRY (re-evaluated in revisions 5 and 6):** the controller requests a RETRY
  after FAILED → OA-2 and a new generation with `retry_of` and
  `authorizing_command_id = the request`. The old one is not revived.
- **E8:** a RETRY or RECOVERY request after an accepted success → blocked (R2).
- **E9:** a RETRY or RECOVERY request by a participant, the Owner or an outsider →
  denied.
- **E10:** a RETRY or RECOVERY request while a generation is non-terminal → blocked (a
  disclosed ceiling).
- **E11 RECOVERY (revised in revision 4; labelled in revision 6):** OA-1
  unconsumed (no generation) → the system never executes it later. The
  controller request creates OA-2 (case `RECOVERY`, persisted), and the
  system executes OA-2. The new generation has **no** `retry_of`. OA-1 is
  superseded, and any attempt to execute it → refused (R3, §0.1 rules 5
  and 9).
- **E17 (revision 6, FBR-F04-13):** a controller request while the latest
  AIOP-001 OA is unconsumed **and** a previous generation for an older OA
  failed → the case recorded is RECOVERY (the latest OA governs). The chain
  and supersession resolve through persisted records.
- **E18 (revision 6):** a RETRY request when the latest AIOP-001 OA is
  unconsumed, or a RECOVERY request when a terminal failed generation
  carries the latest OA → the recorded case must match the persisted state;
  a mismatched case → rejected. A request while a generation is non-terminal
  → blocked (E10).
- **E12:** invocation while the Session is not ANALYSIS → blocked.
- **E13:** an AI_PROCESSOR requester → denied.
- **E15 (revision 4; re-evaluated in revisions 5 and 6):** a RETRY or RECOVERY request
  records the Session's BEGIN_ANALYSIS command id as a **persisted,
  write-once** chain reference. The audit chain OA-2 → request →
  BEGIN_ANALYSIS resolves.
- **E16 (revision 5, FBR-F04-12):** for an artifact accepted from an OA-2
  run, the inverse resolver reaches BEGIN_ANALYSIS and the controller
  BINDING **using persisted records only**. It is run with a resolver that
  has no access to current Session / artifact / generation-status state,
  and the result equals branch 2b. An attempt to UPDATE the persisted OA
  fields or the chain reference → DB error.
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
- **K8 (revised in revisions 4 and 6):** after acceptance of an AIOP-001
  artifact from the **original** run, the system runs at most one AIOP-002
  generation for OA-3; in the normal path exactly one, carrying
  OA-3 = (BEGIN_ANALYSIS, AIOP-002). Its audit is
  SYSTEM_OPERATION with ref = BEGIN_ANALYSIS, it links the accepted artifact
  (R7), and it is **not** refused because the AIOP-001 generation also
  carries BEGIN_ANALYSIS (C9).
- **K9 (revised in revision 4):** after acceptance of an AIOP-001 artifact
  from an **OA-2 run (RETRY or RECOVERY)**, the AIOP-002 generation carries
  OA-3 = (CMD_REQUEST_QUESTION_ANALYSIS, AIOP-002). Its SYSTEM_OPERATION ref
  = that request, and the chain resolves request → BEGIN_ANALYSIS.
- **K10:** the AIOP-002 manifest contains only frozen human Questions. The
  AIOP-001 artifact is not in the model input (R10).
- **K11 (re-evaluated in revision 5):** AIOP-002 FAILED → **no automatic
  retry**. The controller request → OA-4, and a new generation with
  `retry_of`, the same persisted X and `authorizing_command_id = the
  request`. The failed one is not revived.
- **K12:** a clustering RETRY or RECOVERY request by a participant, the Owner or an
  outsider → denied; before any accepted AIOP-001 artifact → blocked.
- **K13:** a clustering RETRY or RECOVERY request after an accepted cluster run →
  blocked (R8). A second system run for the same OA → refused.
- **K14 RECOVERY (revised in revision 4; labelled in revision 6):** OA-3
  unconsumed (no AIOP-002 generation) → the system never executes it later.
  The controller request creates OA-4 = (CMD_REQUEST_QUESTION_CLUSTERING,
  AIOP-002) (case `RECOVERY`, persisted, with X), and the system executes
  OA-4 with **no** `retry_of`. OA-3 is superseded and can never execute
  (R9, §0.1 rules 5 and 9).
- **K19 (revision 6, FBR-F04-13):** the branch-4b inverse resolution holds
  for both RETRY (via `retry_of`) and RECOVERY (via the persisted superseded
  OA-3). Both reach X → X's OA → BEGIN_ANALYSIS from persisted records only.
- **K20 (revision 6):** a clustering request while an AIOP-002 generation is
  non-terminal → blocked. A request whose recorded case mismatches the
  persisted state → rejected.
- **K15 (revision 4):** an AIOP-002 generation whose SYSTEM_OPERATION ref is
  not the command that authorized the accepted AIOP-001 artifact (for
  example BEGIN_ANALYSIS when the accepted artifact came from OA-2) → DENY.
- **K16 RETRY (revision 4; re-evaluated in revisions 5 and 6):** a
  clustering RETRY after a failed AIOP-002 run carries OA-4. Its chain resolves OA-4 →
  request → BEGIN_ANALYSIS through persisted references, and there is at
  most one accepted cluster run per Session (R8).
- **K17 (revision 5, FBR-F04-12):** the CMD_REQUEST_QUESTION_CLUSTERING
  commit persists `accepted_analysis_artifact_ref = X` write-once, and the
  OA-4 generation persists `precondition_artifact_ref = X`. The
  persisted-only resolver reconstructs branch 4b (OA-4 → request → X → X's
  OA → BEGIN_ANALYSIS) for both X-from-OA-1 and X-from-OA-2. UPDATE of
  either reference → DB error.
- **K18 (revision 5):** an AIOP-002 generation whose persisted
  `precondition_artifact_ref` is not an accepted AIOP-001 artifact of the
  same Session, or (for OA-3) whose X was not authorized by C → commit DENY.
  The check verifies the persisted X and never substitutes a current read.

**G — projection (04.7)**
- **G1:** the audience equals the HD-13 frozen-set audience, server-side.
- **G2:** an outsider → denied.
- **G3:** AI origin, generation ref and MOCK marker are present.
- **G4:** human Questions are unchanged and listed separately.
- **G5:** a failed run shows unavailable, with the RETRY / RECOVERY capability for the
  controller only.

**H — real stack (04.8 / 04.10; no mocked backend; the MockProvider is the
declared ceiling)**
- **H1:** the controller begins analysis; the phase shows ANALYSIS, and
  `establishedBy` shows BEGIN_ANALYSIS.
- **H2:** the derived field appears, marked AI · DERIVED / PROPOSAL · MOCK /
  NON_PROOF; the human Questions are verbatim.
- **H3:** a participant sees the same derived field (HD-22) without controls.
- **H4:** an injected provider failure → unavailable, then the controller
  RETRY.
- **H5:** the Owner or a participant has no begin or RETRY / RECOVERY control, and the
  server's reason is shown.
- **H6:** clusters become visible only after the analysis artifact is
  accepted. When the AIOP-001 run is made to fail (injected), "clustering not
  run" is shown and no clusters appear (HD-23).
- **H7:** axe 0 serious/critical; keyboard; mobile.

## 16. F04 end boundary

F04 ends when a governed Session is in **ANALYSIS**, with a provable chain
to its human origin, and:
- **exactly one OA-1** = (BEGIN_ANALYSIS, AIOP-001) is created by
  BEGIN_ANALYSIS;
- **every OA is consumed by at most one generation**. Every AI generation
  carries a distinct operation authorization (authorizing command,
  operation) resolving to BEGIN_ANALYSIS (§0.1);
- an **unconsumed OA-1** may be superseded by a controller-created **OA-2**,
  and an **unconsumed OA-3** by a controller-created **OA-4** (RECOVERY,
  §0.1 rule 9). Likewise any unconsumed OA-2 / OA-4 by a newer request. A
  **superseded OA can never execute later**;
- controller **RETRY** requests after a FAILED / REJECTED generation are
  legal. Controller **RECOVERY** requests after an unconsumed automatic (or
  request) authorization are legal. Neither is legal while a generation is
  non-terminal, or after an accepted result for that operation;
- every accepted artifact and cluster run is reconstructable to
  BEGIN_ANALYSIS through **persisted, write-once** provenance only. That
  covers the original, RETRY and RECOVERY branches of both operations (§0.1
  rules 8-9; §11 items 2a/2b and 4a/4b);
- every VALIDATED generation has a persisted proof and at most one accepted
  AI-origin artifact;
- at most one accepted AIOP-001 artifact per Session;
- a clustering authorization exists only once an accepted AIOP-001 artifact
  exists, with at most one accepted cluster run per Session, and no
  clustering when
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
  as NQ-DEC-044..051, and in 20 §7 / §15B). **No F04 Case-3 relation remains
  open.**
- **Review HOLD item resolved at architecture level (revision 6; not
  materialized):** FBR-F04-13. The end boundary now admits the legal
  RECOVERY path; RETRY vs RECOVERY is §0.1 rule 9; consumption is at most
  once per OA.
- **Review HOLD items resolved at architecture level (revision 5; not
  materialized):**
  - FBR-F04-12: persisted authorization provenance (§0.1 rule 8) and the
    inverse retry branches 2a/2b and 4a/4b;
  - current-state documentation drift (ledger 51 / 42 / REC-027; H-7 not
    listed as open; NOT_STARTED wording).
- **Review HOLD items resolved at architecture level (revision 4):**
  - FBR-F04-11 (operation authorization identity, §0.1) at the authorization
    model;
  - ledger-range drift in WU-04.0 and L-1;
  - H-7 closed as historical drift;
  - H-8 reconciled to the current SF-01 state.
- **Derivable, ready for implementation after review (implementation
  NOT_STARTED):**
  - all Work Units WU-04.0..04.10;
  - FBR-F04-1..9 and 11..13 each have a defined root repair at their homes.
    **None is materialized yet.**
- **Open for review:**
  - H-8 (non-blocking; integration order decided before WU-04.8);
  - the readings R1–R10 (§0) and the §0.1 identity law.
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

---

## Revision-4 amendment to the derived readings (no decision changed)

The ChatGPT architecture review of revision 3 returned
**ARCHITECTURE_REVIEW_HOLD**. It found **FBR-F04-11**, an authorization
identity collision: the R3, R7 and R9 summaries above let AIOP-001 and
AIOP-002 share one authorization keyed on the BEGIN_ANALYSIS command alone.

The human decisions HD-16..HD-23 are **unchanged**. The repair is derived
from HD-16, HD-17 and HD-23 at the authorization model (reconstruction
§0.1: ROOT AUTHORITY CHAIN ≠ OPERATION AUTHORIZATION IDENTITY). The summaries
above are kept as the historical record. Their current readings are:

- **R3 (current):** BEGIN_ANALYSIS creates OA-1 = (BEGIN_ANALYSIS, AIOP-001),
  consumed by the one AIOP-001 generation carrying it. An unconsumed OA-1 is
  never executed later. A controller request creates OA-2 =
  (CMD_REQUEST_QUESTION_ANALYSIS, AIOP-001), which supersedes it.
- **R7 (current):** acceptance of an AIOP-001 artifact creates OA-3 =
  (C, AIOP-002), where C is the human command that authorized the accepted
  artifact (BEGIN_ANALYSIS, or CMD_REQUEST_QUESTION_ANALYSIS after a re-run).
  The clustering run's SYSTEM_OPERATION reference is C. The accepted artifact
  is the commit-time precondition, and the chain still resolves to
  BEGIN_ANALYSIS.
- **R9 (current):** OA-3 is consumed by the one AIOP-002 generation carrying
  it, and never by an AIOP-001 generation. An unconsumed OA-3 is never
  executed later. A controller request creates OA-4 =
  (CMD_REQUEST_QUESTION_CLUSTERING, AIOP-002), which supersedes it.
- R1, R2, R4, R5, R6, R8 and R10 are unchanged.

No new Case-3 relation was created.

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
NOT_STARTED — ARCHITECTURE REVISION 6: READY_FOR_F04_ARCHITECTURE_REVIEW

**Implementation has not started.** Every First Broken Relation has a
defined root repair at architecture level; none is materialized in code,
schema or tests.

The architecture was reconstructed on 2026-09-24 from published F03
(`0d59ae3`, tag `field-F03`, `origin/master` `c9d86ba`). See
F04_ARCHITECTURE_RECONSTRUCTION.md (revision 6) and HUMAN_DECISIONS.md.

**Review history** (reviewed inputs preserved in `review/`):
- Revision 3 → ARCHITECTURE_REVIEW_HOLD: FBR-F04-11 and ledger drift.
- Revision 4 → ARCHITECTURE_REVIEW_HOLD: FBR-F04-11 PASS, with the
  operation-scoped authorization model accepted; FBR-F04-12 and
  current-state drift remained.
- Revision 5 → ARCHITECTURE_REVIEW_HOLD: FBR-F04-11 and FBR-F04-12 PASS;
  FBR-F04-13 (the end boundary did not admit the legal
  unconsumed-authorization recovery path) remained.

**Revision 6 resolves at architecture level:**
- FBR-F04-13. An OA is consumed by at most one generation and may remain
  unconsumed. Controller requests are either RETRY (after a FAILED / REJECTED
  generation) or RECOVERY (superseding an unconsumed OA, with the case
  persisted). A superseded OA never executes. The end boundary, Work Units
  and falsifiers are updated, and a final closure sweep covers all paths
  P1-P9.

**Revision 5 resolved at architecture level:**
- FBR-F04-12. The accepted AIOP-001 artifact behind every AIOP-002
  authorization (OA-3 and OA-4) and every retry chain reference is persisted
  write-once and resolved from immutable records only (§0.1 rule 8). The
  Inverse DeepSweep covers the original and re-run branches of both
  operations.
- Current-state drift: ledger 51 decisions / 42 ESTABLISHED / REC-027;
  H-7 no longer listed as open; NOT_STARTED wording.

Derived from HD-16, HD-17 and HD-23; no new human decision.

**Decisions and open items:**
- **Closed:** all seven F04 Case-3 decisions, C3-F04-1..7, by HD-16..HD-23
  (NQ-DEC-044..051; 16 §41 REC-018..REC-027; 20 §7 SYSTEM_OPERATION
  successor note, decided and not yet materialized; §15B). No F04 Case-3
  relation is open.
- **H-7 closed:** historical documentation drift. Published F03 is not
  rewritten; F04 uses the verified published identities.
- **H-8 open, non-blocking.** SF-01:
  - Field commit `447b24e`, documentation identity commit `c944b95`;
  - worktree `/home/codi/Entwicklung/nquiry/worktrees/frontend-symbiotic`,
    branch `frontend-symbiotic`;
  - clean, locally committed, not tagged, not pushed;
  - F03 integration not started.

  The integration order is decided before WU-04.8. It is not a Case 3.

**First Broken Relations:** thirteen.
- FBR-F04-1..9 and 11..13 have defined root repairs. None is materialized
  (FBR-F04-11..13 are resolved at architecture level).
- FBR-F04-10 is closed by the H-7 resolution.

**Real provider lane:** blocked by HARD-DEP-002. F04 passes under a
declared MockProvider ceiling (HD-19). Mock proofs never count toward
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
All lines are additions (F04 architecture revisions 2-4; unchanged in revisions 5 and 6); nothing is removed.
================================================================================

```diff
diff --git a/docs/architecture/16_DECISION_GAP_REGISTER.md b/docs/architecture/16_DECISION_GAP_REGISTER.md
index 17b186d..fbac12b 100644
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
@@ -2523,3 +2587,87 @@ Successor record. Nothing in §1–§40 or REC-001..REC-010 is deleted.
 **Current counts** (superseding REC-010 for current use): Decisions 43 (ESTABLISHED 34: NQ-DEC-022, 032..043; REQUIRED 9). Canonical gaps stay 80. NQ-GAP-023, NQ-GAP-022, NQ-GAP-032 and NQ-GAP-079 stay OPEN; NQ-GAP-023 now records the prototype form rule.
 
 **Provenance.** F03 WU-03.0, authorized by the human operator's F03 instruction (2026-09-24), per `20_SYSTEM_FIELD_ENGINEERING.md` §14.
+
+### REC-018 / NQ-DEC-044: A committed BEGIN_ANALYSIS authorizes exactly one system-executed AIOP-001 run (F04 HD-16; closes C3-F04-1)
+
+- DECISION (human operator, 2026-09-24, option (b)): "Beginning analysis authorizes exactly one AI run, which the system executes right after that commit. Re-runs after a failure need an explicit controller request."
+- READING (F04 reconstruction revision 2, R1–R3, for architecture review):
+  - The run's authority is the committed human BEGIN_ANALYSIS command, recorded as SYSTEM_OPERATION (REC-019). It is not SYSTEM_DERIVED method authority, so BND-011/012 (D8) stay REQUIRE/DENY for any automatic path.
+  - No re-run is authorized after an accepted success.
+  - Revision 4 (FBR-F04-11): authorizations are operation-scoped. OA =
+    (authorizing command, AI operation). BEGIN_ANALYSIS creates OA-1 =
+    (BEGIN_ANALYSIS, AIOP-001), consumed by the one AIOP-001 generation
+    carrying it. A controller re-run request creates OA-2 =
+    (CMD_REQUEST_QUESTION_ANALYSIS, AIOP-001), superseding an unconsumed
+    OA-1. Generation uniqueness is keyed on OA, never on the command alone.
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
+  - **R7** (revision 4, FBR-F04-11). Acceptance of an AIOP-001 artifact creates OA-3 = (C, AIOP-002), where C is the human command that authorized the accepted artifact: BEGIN_ANALYSIS for the original run, CMD_REQUEST_QUESTION_ANALYSIS for a controller re-run. The SYSTEM_OPERATION reference of the automatic clustering run is C. The accepted AIOP-001 artifact is the mandatory commit-time precondition and the authorizing link. The chain resolves to BEGIN_ANALYSIS, as provenance, not identity.
+  - **R8.** Nothing authorizes a clustering re-run after an accepted cluster run. At most one accepted cluster run per Session.
+  - **R9** (revision 4). OA-3 is consumed by the one AIOP-002 generation carrying it, never by an AIOP-001 generation. An unconsumed OA-3 is never executed later. A controller request creates OA-4 = (CMD_REQUEST_QUESTION_CLUSTERING, AIOP-002), superseding it.
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
All lines are additions (F04 architecture revisions 2-4; unchanged in revisions 5 and 6); nothing is removed.
================================================================================

```diff
diff --git a/docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md b/docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md
index 4bb194f..f336f4d 100644
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
+| SYSTEM_OPERATION | A SYSTEM_SERVICE operation executed under a committed human command that authorized it (F04: the BEGIN_ANALYSIS authorization of one AIOP-001 run, HD-16; the clustering run authorized once an AIOP-001 artifact is accepted, HD-23; and acceptance of validated AI output). Re-checked at commit: the referenced command committed, same Workspace and Session, and the operation-specific predicates (Session ANALYSIS; proof VALIDATED for acceptance). The actor must be SYSTEM_SERVICE. It is **not** SYSTEM_DERIVED method authority (D8 / BND-011 / BND-012 are untouched) and grants nothing reusable | the authorizing human command id (scope `SESSION:<id>`). Operation authorizations are operation-scoped: OA = (authorizing command, AI operation), and consumption and uniqueness are keyed on OA. The root chain to BEGIN_ANALYSIS is provenance, not identity (F04 reconstruction §0.1, revision 4) |
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
