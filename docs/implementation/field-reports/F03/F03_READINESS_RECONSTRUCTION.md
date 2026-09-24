# F03 READINESS RECONSTRUCTION — PROTECTED HUMAN QUESTION FIELD

Date: 2026-09-24. Mode: reconstruction only. No implementation, no schema
change, no architecture edit. Nothing staged, committed or pushed.

Reconstructed from the published F02 state:
- `origin/master` = `bea864b`, with the F02 commit `2f33be1` carrying the
  signed annotated tag `field-F02`;
- worktree `.claude/worktrees/local-login-auth` at `bea864b`, with only the
  two withheld files untracked (`apps/web/AGENTS.md`, `apps/web/CLAUDE.md`).

Every claim cites its authoritative home. Code is cited as evidence of
materialization, never as authority (20 §0).

## 0. Readiness status

**NOT READY — BLOCKED ON CASE-3.**
- One Case-3 boundary blocks the Field's core relation, capture: **C3-1,
  the questions-only validator**.
- Two further Case-3 boundaries decide who may capture and what the
  frontend may show: **C3-2** and **C3-3**.
- Six First Broken Relations are derivable and can be repaired inside F03
  once it starts.
- Both entry conditions are **architecture-derived invariants** that hold.

## 1. Human authority for this Field (given with the F03 bootstrap instruction, 2026-09-24)

| Id (proposed) | Decision | Effect |
|---|---|---|
| HD-10 | PAUSE / RESUME is **out of scope for F03**. HD-9 does not authorize it. It stays OPEN as a Case-3 relation. | TRN-BURST-003 / 004 and AUTH-DEP-BURST-003 / 004 are not materialized. Burst states reachable in F03 are PREPARED → ACTIVE → COMPLETED. PAUSED stays in the schema (03 §19) but has no Command |
| HD-11 | **Automatic timer completion is NOT authorized.** The timer is presentation only. Completion is an explicit manual consequential action under HD-9. Time passing alone must not commit the completion effect. | The SYSTEM_SERVICE path of AUTH-DEP-BURST-005 / AUTH-DEP-SESS-005 is not materialized. This affirms NQ-DEC-017 and 12 §11. CONFLICT-007, NQ-GAP-022 and NQ-GAP-032 stay OPEN and are not needed |

**Ledger reconciliation pending.** No other existing record closes
PAUSE/RESUME. Only the timer path is already closed for the prototype, by
NQ-DEC-017. HD-10 and HD-11 are to be reconciled into 16 §41 (proposed
NQ-DEC-038 / 039) and 20 §15 in F03's first Work Unit, per 20 §14. This
report is not a Work Unit, and no ledger was edited.

## 2. Field map

| Item | Value |
|---|---|
| Field | F03 — PROTECTED HUMAN QUESTION FIELD (19 §23). Regime: protected human generation |
| Parent | SFE (20) → product architecture 00–18 + 16 → F02 (published `2f33be1`, `field-F02`) |
| Target path | QUESTION_GENERATION → ACTIVE HUMAN_ONLY Burst → admitted participants → human capture (TRN-Q-001) → immutable `original_text` → manual completion (TRN-SESS-005 + TRN-BURST-005, one bundle) → COMPLETED Burst, Session QUESTION_CAPTURE → frozen, fingerprinted human raw set |
| Ends at | Session **QUESTION_CAPTURE**. 03 §16 declares `QUESTION_GENERATION -> ANALYSIS` illegal. 12's happy-path row 13 (Session → ANALYSIS right after completion) is read through 12 §10's own hedge ("may include any additional intermediate 03 state"). TRN-SESS-006 BEGIN_ANALYSIS is F04 |
| Downstream | F04 (post-Burst AI / sensemaking) and F08 (event contracts may start in parallel after F03's contracts stabilize, 19 §47) |

## 3. Inherited relations (from F02 and the ledger)

- A Session reaches QUESTION_GENERATION with an ACTIVE HUMAN_ONLY Burst in
  one bundle (TRN-SESS-004 + TRN-BURST-002, F02).
- At least one current SessionParticipation (HD-8).
- Participants are admitted by the Session controller (HD-7).
- Session control resolves at `SESSION:<id>` (HD-1).
- Burst start and manual completion are closed by the same Session-scoped
  binding (HD-9, a prototype narrowing; NQ-GAP-080 is open for production).
- Effect gate: CommitCoordinator + BND-014 with typed authority sources
  BINDING / ROLE / FOUNDING (HD-6). An idempotency key is one logical
  Command (F02 WU-02.12).
- The outcome vocabulary is uniform on every route (WU-02.12).
- **Already materialized (PKG-06 / PKG-07), unused in production until
  F03:**
  - `questions`: `original_text` non-empty CHECK + an immutability trigger
    on `original_text`, `challenge_id`, `workspace_id`, `origin` and
    `author_user_id`; `origin` HUMAN ⇔ `author_user_id` present; no
    `status` column (NQ-GAP-019); no `text` column (NQ-GAP-008).
  - `question_bursts`: `mode = 'HUMAN_ONLY'` CHECK; a transition trigger;
    `frozen_membership_fingerprint` ⇔ COMPLETED.
  - `burst_question_memberships`: `capture_origin = 'HUMAN'` CHECK;
    rows immutable (UPDATE trigger); INSERT/DELETE refused once the Burst
    is COMPLETED.
  - Repository and domain code: `BurstRepository.add_member / complete /
    list_members`, `QuestionRepository.create_root`,
    `domain.burst_membership.compute_frozen_membership_fingerprint`.
- **Not yet materialized:**
  - no Command, route or UI for capture or completion;
  - no typed authority source for the participation right;
  - no AI path is reachable at runtime (the gateway is not wired to HTTP),
    so AI contamination is structurally absent today.

## 4. Entry-condition analysis

### EC-1 — `burst_repository.get_by_session` assumes one Burst per Session

**Classification: ARCHITECTURE-DERIVED INVARIANT** (derived, not stated). It
holds, and it is only partly enforced at the database.

Derivation chain (authoritative homes):
1. 02 §13.4 / §51.1 [ARCHITECTURAL CLOSURE]: "QuestionBurst → exactly one
   Session". 02 fixes the Burst side only. Session→Burst multiplicity is
   **not** stated in 02 ("Session HAS QuestionBurst").
2. 03 topology (§13–§16): the 13 Session edges TRN-SESS-001..013 are strictly
   forward, one outgoing edge per state. Backward edges are illegal (§16:
   "REVIEW -> DRAFT", "CLOSED -> any Session state"). AC-03-001 (§14):
   "A new inquiry cycle creates a new Session under the same Challenge."
   CHALLENGE_CAPTURE → QUESTION_GENERATION (TRN-SESS-004) is therefore
   taken **at most once per Session**.
3. TRN-SESS-004 couples that single Session edge with "the" Burst
   PREPARED → ACTIVE. TRN-BURST-001 requires "Session is in a
   pre-generation state compatible with later start". So no Burst can be
   prepared once generation has begun, and at most one Burst ever becomes
   ACTIVE / COMPLETED in a Session.
4. The only extra rule is F02's `BURST_ALREADY_EXISTS` precondition (at
   most one PREPARED Burst before start). It is derived from TRN-SESS-004
   needing an unambiguous Burst.

**Enforcement homes:**

| Rule | Where enforced |
|---|---|
| (3) no Burst prepared after generation begins | application precondition `SESSION_NOT_PRE_GENERATION` |
| (4) at most one PREPARED Burst before start | application `BURST_ALREADY_EXISTS` + DB partial unique `uq_question_bursts_one_open_per_session` (`state <> 'COMPLETED'`) |
| ≤ 1 Burst per Session in total | application preconditions only. The DB would accept a new PREPARED row after COMPLETED if application code ever skipped the precondition |

**First Broken Relation?** None today. Recommended F03 hardening (Case 2,
same invariant, no new semantics): a full `UNIQUE (session_id)` on
`question_bursts`, or a trigger refusing a Burst for a Session outside
DRAFT / SETUP / CHALLENGE_CAPTURE. That moves the derived invariant into
its persistence home, so `one_or_none` can never raise.

**Architecture change if ever relaxed:** multiple Bursts per Session would
need a new Session topology or method semantics (Case 3). The assumption
must not be widened silently.

### EC-2 — `inquiry_directory.session_state_established_by` assumes no re-entered state

**Classification: ARCHITECTURE-DERIVED INVARIANT.** It holds for Session
states.

Derivation: the same 03 §13–§16 topology. Each Session state is entered by
exactly one edge, exactly once. CLOSED is terminal, and iteration means a
new Session (AC-03-001). The query matches audit rows whose `target_refs`
contain `session:<id>` and whose `state_after_ref` is `session:<STATE>`
or `session:<STATE>|…`. At most one committed row can match per
(Session, state).

**F03 obligations to keep it true:**
1. Capture (TRN-Q-001: "Session remains QUESTION_GENERATION") must write
   **no** `session:*` `state_after_ref`. Otherwise it would duplicate
   QUESTION_GENERATION's establishing row and make `one_or_none` raise.
2. The TRN-SESS-005 bundle must write
   `session:QUESTION_CAPTURE|burst:COMPLETED` (the F02 bundle form).

**Not transferable to Bursts.** A Burst state *can* be re-entered in the
architecture (ACTIVE → PAUSED → ACTIVE, TRN-BURST-003/004). Any future
"Burst established by" projection must not copy this `one_or_none`
pattern. That is harmless in F03, because HD-10 keeps PAUSE/RESUME out,
but the relation is recorded for the Field that materializes PAUSE/RESUME.

## 5. Authority map

| Operation | Architecture home | Prototype authority | Effect-gate source | Scope | Re-resolved at commit |
|---|---|---|---|---|---|
| Capture a Question (TRN-Q-001) | 04 §40 AUTH-DEP-Q-001: "Session Participant … Direct source participation right … LEVEL_1_EXPLICIT"; "Workspace role label alone is not sufficient or necessary"; delegation: "personal to participant identity. No AI delegation" | Authenticated human with a **current SessionParticipation** in the Burst's Session (left_at NULL; admitted by the controller, HD-7), whose Workspace membership is still ACTIVE (BND-003) | **None exists today → FBR-F03-5** (proposed PARTICIPATION source, ref = participation id) | the specific ACTIVE Burst of that Session | yes: participation + membership + Burst ACTIVE |
| Complete the Burst (TRN-BURST-005, human path) | 04 §39 AUTH-DEP-BURST-005: Facilitator end right | **HD-9**: Session-scoped `SESSION_CONTROL_RIGHT` at `SESSION:<id>` | BINDING (binding id, `SESSION:<id>`) | the specific ACTIVE Burst | yes |
| Close question generation (TRN-SESS-005, coupled) | 04 §26 AUTH-DEP-SESS-005: Facilitator or timer | **HD-1** (Session transitions) + **HD-9** (the coupled Burst half). The timer path is excluded (HD-11) | BINDING, same binding, one bundle | `SESSION:<id>` | yes |
| Admit a participant (F02) | 09 §28 / HD-7 | the Session controller | BINDING | `SESSION:<id>` | yes. **Self-admission is ambiguous → C3-3** |
| Pause / resume | 04 §37–§38 | **NONE (HD-10, out of scope)** | — | — | — |
| Automatic completion | 04 §39 SYSTEM path | **NOT AUTHORIZED (HD-11)** | — | — | — |

What the capture authority relation requires, exactly:
- **Who**: an authenticated human (BND-001), with a current
  SessionParticipation in the Session that owns the Burst and an ACTIVE
  membership in that Workspace (BND-002 / 003).
- **Under what**:
  - the Session must be in QUESTION_GENERATION;
  - the Burst must be ACTIVE (not PREPARED, PAUSED or COMPLETED) and in
  HUMAN_ONLY mode;
  - the same Workspace throughout.
- **Nothing else**: no Workspace role, no binding, no controller status, no
  client claim. There is no path by which the author authorizes themselves:
  the participation relation is created only by the controller's Command
  (HD-7), subject to C3-3.

## 6. Boundary map (F03 Commands)

| Command | Precommit chain | Blockers (BLOCKED 422) | Commit |
|---|---|---|---|
| CMD_CAPTURE_BURST_QUESTION | BND-001 identity, BND-002 Workspace, BND-003 membership, **participation check** (AUTH-DEP-Q-001), BND-008 contamination (**requires BURST_INPUT_VALID → C3-1**) | Session not QUESTION_GENERATION; Burst not ACTIVE; empty input | BND-014 with the PARTICIPATION source (FBR-F03-5); Burst ACTIVE re-read under lock (FBR-F03-2) |
| CMD_COMPLETE_BURST (TRN-SESS-005 + TRN-BURST-005 bundle) | BND-001/002/003/005 (`SESSION:<id>`), BND-007 topology, BND-008 (freeze preconditions) | Burst not ACTIVE; unresolved capture (FBR-F03-3); zero captured Questions (**see O-6**) | BND-014 BINDING; Burst row locked before memberships are read; fingerprint over immutable facts (FBR-F03-4); Session + Burst in one SAVEPOINT |

**BND-009 AI invocation.** No AI operation is reachable. F03 must *prove*
the denial: any AI-ish input is refused at the API, the DB mode and origin
CHECKs, and in the tests (P-04, B-ATT-01/02).

## 7. Transition map (F03 scope)

| Transition | From → To | In F03 | Notes |
|---|---|---|---|
| TRN-Q-001 CAPTURE_BURST_QUESTION | Question absent → present; Session and Burst unchanged | **yes** | creates the Question (HUMAN, author, verbatim `original_text`, `normalized_text` NULL) and the membership (order, time, actor, HUMAN) in one commit |
| TRN-BURST-005 COMPLETE_BURST + TRN-SESS-005 CLOSE_QUESTION_GENERATION | Burst ACTIVE → COMPLETED; Session QUESTION_GENERATION → QUESTION_CAPTURE | **yes, one bundle** | membership frozen, fingerprint set |
| TRN-BURST-003 / 004 | ACTIVE ↔ PAUSED | **no** (HD-10) | — |
| TRN-SESS-006 BEGIN_ANALYSIS | QUESTION_CAPTURE → ANALYSIS | **no** (F04) | requires the provable frozen set F03 produces |

## 8. First Broken Relations (to be repaired inside F03; none requires new semantics)

| Id | Relation | Evidence | Authoritative home | Class |
|---|---|---|---|---|
| FBR-F03-1 | Capture ↔ questions-only validity | BND-008 VALIDATION "input must satisfy BURST_INPUT_VALID … validator remains GAP-03-003"; REQUIRE "If BURST_INPUT_VALID cannot be established by a source-compatible mechanism: REQUIRE compliant validation mechanism". With no mechanism, BND-008 cannot ALLOW any capture | 03 §24 GAP-03-003, 06 BND-008, 16 NQ-GAP-023 (OPEN), LEVEL 1 (01:292 "answers/explanations are prevented") | **CASE 3 → C3-1** |
| FBR-F03-2 | Freeze ↔ concurrent capture | `trg_burst_memberships_enforce_freeze` reads the Burst state with a plain SELECT (no row lock) and refuses only COMPLETED. A capture that passed the check while ACTIVE can commit after a concurrent completion that computed its fingerprint without that row. The result is a frozen set that disagrees with its fingerprint (the BND-008 bypass "retry of late Question after COMPLETED"). A PREPARED Burst also accepts membership rows at the DB level | migration `d8a1147fde30` trigger 3 + the completion handler | Case 1: completion takes `FOR UPDATE` on the Burst before reading memberships; capture takes `FOR SHARE` (or the trigger does) and requires `state = 'ACTIVE'` on INSERT (TRN-Q-001 "Burst ACTIVE") |
| FBR-F03-3 | Completion ↔ unresolved acknowledged capture | TRN-BURST-005 "No capture write acknowledged to the user remains unresolved"; BND-008 "Capture uncertainty blocks Burst completion". No persisted row links a capture attempt to its Burst: `commands` has no target refs, `idempotency_records` has none, and audit exists only for commits | 09 command / idempotency contract; 10 INDETERMINATE | Case 2: persist the Burst reference for capture attempts (e.g. target refs on `commands`, or a capture-attempt relation), then block completion while any capture for the Burst is IN_PROGRESS / INDETERMINATE |
| FBR-F03-4 | Frozen fingerprint ↔ reconstructability | The fingerprint hashes `question_id:record_version`. `questions.normalized_text` and `record_version` stay updatable: the trigger guards only birth facts. Normalization is legitimate derived work after the Burst (03 §25.5, F04). A later normalization bump would make the recomputed fingerprint of an untouched raw set disagree | `domain.burst_membership` (14 §19 [IMPLEMENTATION CHOICE]); 03 TRN-SESS-005 "frozen-set identity must be reconstructable" | Case 2: fingerprint over immutable birth facts only (membership ids, question ids, `original_text` digests, `captured_order`, actor, `captured_at`), with the deviation from 14's historical choice disclosed |
| FBR-F03-5 | Effect gate ↔ participation authority | AUTH-DEP-Q-001's source is the participation right. BND-014 admits only BINDING / ROLE / FOUNDING, and `audit_events.authority_source_type` has a closed CHECK. Encoding capture as ROLE would fabricate provenance (HD-6 forbids it) | 20 §7 (typed sources), 16 REC-004 (HD-6: "at minimum BINDING, ROLE and FOUNDING"), migration `a7f2c91d4e10` | Derivable (Case 1): a PARTICIPATION source (ref = SessionParticipation id, scope `SESSION:<id>`), re-read at commit. It **extends the effect-gate contract**, so it must be reconciled into 20 §7 (successor note) and 16 §41 in the same WU. **Flagged for confirmation**, see §10 |
| FBR-F03-6 | Membership order ↔ concurrency | `captured_order` has no per-Burst uniqueness. Concurrent captures can compute the same order | `burst_question_memberships` | Case 2: `UNIQUE (question_burst_id, captured_order)` plus assignment under the Burst row lock |

EC-1 hardening (§4) is optional defense-in-depth, not a broken relation.

## 9. Open relations (not blocking F03, carried forward)

- **O-1** PAUSE / RESUME authority (HD-10: open, Case 3 when a Field needs
  it).
- **O-2** Automatic timer completion and duration: CONFLICT-007,
  NQ-GAP-022, NQ-GAP-032 (HD-11: not authorized; NQ-DEC-017 manual).
- **O-3** Timer *presentation*. Case 2, recommended: elapsed time since
  `started_at` plus non-authoritative "about four minutes" guidance.
  LEVEL 1 says "approximately four minutes", and every reading of
  CONFLICT-007 agrees on four minutes as the guide. No countdown to a
  deadline, and no effect when it is reached.
- **O-4** Question.status (NQ-GAP-019): omitted, never used as a guard.
  text vs original_text (NQ-GAP-008): only `original_text` is written.
  `normalized_text` stays NULL during the Burst (no silent normalization).
- **O-5** Verbatim storage. `original_text` is stored exactly as submitted:
  no trim, no Unicode normalization, no case change (03 §25.5; "questions
  are stored verbatim"). Empty or whitespace-only input is **rejected**
  without being altered. A maximum length is a technical safeguard only
  (Case 2, disclosed).
- **O-6** Completing a Burst with **zero** captured Questions.
  `compute_frozen_membership_fingerprint` refuses an empty set (PKG-07
  choice), and TRN-BURST-005 speaks of "complete captured membership". The
  prototype reading is BLOCKED (`NO_CAPTURED_QUESTIONS`): derivable, since
  an empty raw set cannot seed F04's AIOP-001 input. Disclosed. It becomes
  Case 3 only if a stakeholder needs empty Bursts.
- **O-7** Leave / remove participation (NQ-GAP-079 remainder). Not needed
  for F03 capture.
- **O-8** NQ-GAP-003 active-Burst AI observer/recorder. Not materialized;
  BND-008 REQUIRE before any model call.
- **O-9** 12 vs 03: 12's happy-path row 13 goes to ANALYSIS right after
  completion; F03 follows 03 (→ QUESTION_CAPTURE). Recorded, not a
  blocker.

## 10. Case-3 boundaries (Human Authority required before F03 implementation)

**C3-1 — Questions-only validator (BLOCKING).**
- **Why it is Case 3.** LEVEL 1 requires that "answers/explanations are
  prevented in Question Burst mode". BND-008 cannot ALLOW a capture without
  a `BURST_INPUT_VALID` mechanism, and forbids AI semantic evaluation as
  that mechanism. Any mechanism defines what counts as a question, which is
  product meaning.
- **Options:**
  - **(a) Deterministic form rule.** Accept non-empty input whose last
    non-whitespace character is a question mark in any script (`?`, `？`,
    `؟`, Greek `;`, …); refuse other input as `rejected`. Store the text
    verbatim either way. This is a prototype narrowing: it enforces form,
    not meaning, and NQ-GAP-023 stays open for a semantic mechanism.
  - **(b) Human attestation.** The UI instructs "questions only". No system
    validation. The disclosed ceiling is that LEVEL 1 "prevented" is not
    met by the system.
  - **(c) Controller moderation.** Rejected per item. This adds a
    discussion-like step during the Burst, which LEVEL 1 forbids ("no
    discussion").
- **Recommendation: (a)**, recorded like HD-9 as a prototype narrowing.

**C3-2 — Visibility of Questions during the ACTIVE Burst (blocks the
frontend acceptance definition).**
- **Why it is Case 3.** The architecture defines only "participants cannot
  edit others' questions" (00 §11.1). Whether a participant sees other
  participants' Questions live, and whether author identity is shown to
  peers during or after the Burst, changes the ideation method and
  privacy. That is product meaning, not presentation.
- **Options:**
  - **(a)** each participant sees only their own Questions during the
    Burst; everyone in the Session sees the full frozen set after
    completion, with human origin marked and author names shown;
  - **(b)** the live shared list is visible to all participants during the
    Burst;
  - **(c)** as (a) or (b), but without author names shown to peers.
- **Recommendation: (a).** It is the least influence during generation;
  human origin is always explicit; the controller sees only a count during
  the Burst.

**C3-3 — Can a Session controller admit themselves as a participant?
(decides whether the controller can author Questions).**
- **Why it is Case 3.** Two readings conflict:
  - HD-7 says "No self-join". F02's admit handler accepts
    `actor == participant`.
  - 12's happy path has the controller Alpha capturing Q1 (row 9). Under a
    strict reading of "no self-join", that is reachable only if a *second*
    controller admits Alpha, and controller multiplicity is itself open
    (GAP-04-004 / NQ-GAP-029).
- **Options:**
  - **(a)** "self-join" means a member joining without the controller. A
    controller exercising their own admission right, including for
    themselves, is lawful (current F02 behaviour; audited, BINDING-sourced).
  - **(b)** self-admission is forbidden. F02 then has a defect to repair,
    and a sole controller can never author Questions.
- **Recommendation: (a)**, with the audit making self-admission visible.

**Confirmation requested (not Case 3 in my reading) — FBR-F03-5
PARTICIPATION source.**
- AUTH-DEP-Q-001 makes the participation right the authority. HD-6 sets
  typed sources "at minimum" BINDING / ROLE / FOUNDING and requires "actual,
  reconstructable authority provenance". The only truthful encoding is a
  new PARTICIPATION source.
- 20 §7 currently says the gate admits "exactly these" three, so adding a
  fourth amends a human-authorized document's contract. I will do it by
  successor note, not a rewrite, unless Human Authority objects.

## 11. TDD falsifier plan

Levels: L1 domain / repository, L2 handler ↔ BND-014 ↔ audit, L3 HTTP on
real PostgreSQL, L7 real-stack browser.

| Relation | MUST BECOME TRUE | MUST REMAIN IMPOSSIBLE | Falsifier (test) |
|---|---|---|---|
| Capture before ACTIVE | — | a Question or membership for a PREPARED Burst | capture while PREPARED → `blocked` `BURST_NOT_ACTIVE`, no rows; DB INSERT into a PREPARED Burst's membership raises (FBR-F03-2) |
| Capture after completion / late capture | — | a membership added to a COMPLETED Burst; a late retry changing the set | capture after the complete commit → `blocked`, no rows; **concurrency test**: capture transaction held open across a completion → exactly one of them wins, and the fingerprint matches the final membership |
| Non-participant capture | — | an active member without participation, the controller without participation, or the Workspace owner capturing | each → `denied` (participation check), no rows |
| Foreign Session / Burst | — | capture into a Burst of another Session the actor participates in via a mismatched path | `denied` / `rejected`, no rows |
| Cross-Workspace | — | an outsider reading or capturing | `denied` at HTTP and in the browser (real-stack); RLS / composite FKs |
| Duplicate / idempotent | an identical retry (same key, same payload) → `committed` + `replayed`, one Question | the same key with another text or Burst → an effect | 09 §108.2: key + fingerprint; `rejected` `IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_COMMAND`. Two *different* keys with identical text are two legitimate captures (no content dedup: not in the architecture) |
| Verbatim / Unicode | `original_text` byte-equal to the submitted text (emoji, RTL, combining marks, CJK, leading/trailing spaces, newlines) | trimming, NFC/NFKC, case change, `normalized_text` set during the Burst | round-trip HTTP → DB → HTTP equality; empty / whitespace-only → `rejected` |
| Question mutation | — | UPDATE of `original_text`, `origin` or `author`; rewrite via any route | DB trigger tests (existing, re-run); no update route exists (static route inventory) |
| Questions-only | per C3-1 decision | per C3-1 decision | per C3-1 (e.g. statement without `?` → `rejected`, stored nothing) |
| AI-origin contamination | origin HUMAN, author = actor, capture_origin HUMAN | client-supplied `origin` / `author` honoured; AI-origin row in the membership; any AI invocation while ACTIVE | a request carrying `origin: "AI"` / `authorUserId` → ignored or `rejected`; DB CHECKs; static: no gateway import on the capture path; P-04 / B-ATT-01..08 |
| Completion without authority | — | participant-only, Owner, Challenge- or Workspace-scoped binding completing | `denied`, Burst ACTIVE, Session QUESTION_GENERATION |
| Completion stale | — | completing on an old expected version | `stale` (with current state), nothing changed |
| Second completion | — | COMPLETED → COMPLETED; a new fingerprint | second request → `blocked` (Burst not ACTIVE) or `committed` + `replayed` for the same key |
| Unresolved capture | — | completion while a capture for the Burst is IN_PROGRESS / INDETERMINATE | seeded unresolved attempt → completion `blocked` (FBR-F03-3) |
| Zero questions | per O-6 | an empty frozen set | completion → `blocked` `NO_CAPTURED_QUESTIONS` |
| Freeze integrity | membership immutable after COMPLETED; Session QUESTION_CAPTURE and Burst COMPLETED in one commit | a partial bundle | failure injection mid-bundle → both unchanged (`failed_precommit`) |
| Reconstruction integrity | recomputing the fingerprint from immutable facts equals the stored value, **also after a simulated `normalized_text` update** | a fingerprint that depends on mutable columns | FBR-F03-4 test |
| Provenance | capture audit = PARTICIPATION source + participation id + `SESSION:<id>`; completion audit = BINDING; `establishedBy` resolves QUESTION_CAPTURE | a `session:*` `state_after_ref` on capture (EC-2) | audit row assertions; the `one_or_none` path is exercised |
| Frontend | controls only from server capabilities | client-side authority or origin | mocked component tests + real-stack |

## 12. Real-stack acceptance path (L7, no mocking; three dev identities, HD-3)

1. Controller B (Facilitator with the Session-scoped binding) brings the
   Session to QUESTION_GENERATION as in F02. Participant A (and C, per
   C3-2/C3-3) is admitted.
2. The Session page shows the Burst ACTIVE, marked HUMAN_ONLY, with
   "questions only" guidance and elapsed-time presentation (O-3). There is
   no AI surface.
3. A submits a question. It appears exactly as typed (verbatim, including
   Unicode), marked **human** and attributed per C3-2. A submits another.
   A statement is refused as `rejected` (per C3-1).
4. The Owner (not a participant) has no capture affordance, and the
   server's reason is shown. The outsider is denied (in-page `fetch`).
5. B presses **Complete Burst**. The server re-resolves authority. The
   Session becomes QUESTION_CAPTURE and the Burst COMPLETED. The capture
   form disappears, and a late capture attempt (a stale tab) is `blocked`.
6. The frozen human question set is visible, per C3-2. "Established by"
   shows the completion Command, B, BINDING at `SESSION:<id>`, and the
   commit. The UI shows the fingerprint / frozen marker.
7. axe 0 serious/critical, keyboard-operable capture and completion, and
   desktop + mobile, as in F02.

## 13. F04 downstream dependencies (what F03 must hand over)

- **TRN-SESS-006 BEGIN_ANALYSIS**: requires Burst COMPLETED, a *provably*
  frozen set (fingerprint recomputable from immutable facts, FBR-F03-4),
  and the `original_text` invariants.
- **AIOP-001 input**: exactly the frozen membership (08 §23 AIOP-001). AIContextManifest
  references the frozen-set fingerprint. Clusters must never mutate raw
  membership (DB-immutable).
- **Provenance**: human origin + author on every raw Question, so F04's
  AI-origin artifacts stay distinguishable (08 §39 effect matrix).
- **Normalization / derived representations** after freeze must not
  disturb frozen-set verification (FBR-F03-4).
- **External**: HARD-DEP-002 (real provider). F04 structural lane on
  MockProvider with a ceiling. **Open tensions:** GAP-03-006 (19 F04 "AI
  unavailable leaves workflow usable" vs 03's no-skip path) and NQ-GAP-003
  (AI observer).

## 14. Stop conditions — evaluation

| Condition | Result |
|---|---|
| An authority relation is not derivable | Capture and completion are derivable (AUTH-DEP-Q-001 + HD-7; HD-9 + HD-1). The **effect-gate encoding** of capture needs a contract extension (FBR-F03-5, confirmation) |
| An entry condition changes architecture semantics | No. Both are architecture-derived and hold |
| A required transition is undefined | No. TRN-Q-001, TRN-BURST-005 and TRN-SESS-005 are fully defined |
| Freeze semantics are ambiguous | The semantics are defined (03 / 09 §30.1). Implementation defects are FBR-F03-2 / 4 (derivable). The empty-set reading is O-6 (derivable, disclosed) |
| Human vs AI origin becomes ambiguous | No. The DB CHECKs + AUTH-DEP-Q-001 make origin explicit |
| Completion authority conflicts with existing architecture | No. HD-9 narrows 04 §39 explicitly for the prototype |
| **Capture input validity** | **STOP: C3-1** (BND-008 REQUIRE; no source-compatible mechanism exists) |

**READY FOR F03 IMPLEMENTATION: NO.** It becomes YES once C3-1, C3-2 and
C3-3 are decided and the FBR-F03-5 confirmation is given (or objected to).

---

## 15. Human decisions closing the Case-3 boundaries (2026-09-24, appended)

The human operator answered §10 with "3": option (a) for C3-1, C3-2 and
C3-3, and confirmation of the PARTICIPATION source. The analysis above is
preserved unchanged. Proposed ledger ids are given for each decision;
reconciliation into 16 §41 and 20 §15 happens in F03's first Work Unit
(20 §14).

| Id (proposed) | Closes | Decision |
|---|---|---|
| HD-12 (NQ-DEC-040) | C3-1, NQ-GAP-023 for the prototype | **Deterministic form rule.** Capture input is `BURST_INPUT_VALID` when it contains non-whitespace and its last non-whitespace character is a question mark in any script (`?`, `？`, `؟`, Greek `;` U+037E, and equivalents). Any other input is `rejected`, and nothing is stored. The text itself is stored verbatim; validation never alters it. **Prototype narrowing:** it enforces form, not meaning. NQ-GAP-023 stays OPEN for a semantic mechanism, and AI remains excluded as validator (BND-008) |
| HD-13 (NQ-DEC-041) | C3-2 | **Visibility.** While the Burst is ACTIVE, each participant sees only their own Questions, and the controller sees only a count. After completion, every Session member who can read the Session sees the full frozen set, with human origin marked and author names shown |
| HD-14 (NQ-DEC-042) | C3-3, HD-7 interpretation | **Controller self-admission is lawful.** "No self-join" means a member cannot join without the controller's admission. The holder of `SESSION_CONTROL_RIGHT` at `SESSION:<id>` may admit themselves, audited and BINDING-sourced. F02's behaviour stands |
| HD-15 (NQ-DEC-043) | FBR-F03-5 | **PARTICIPATION authority source confirmed.** The effect gate gains a fourth typed source, PARTICIPATION (ref = SessionParticipation id, scope `SESSION:<id>`), re-read at commit. It is recorded in 20 §7 by successor note and in 16 §41. The `audit_events.authority_source_type` CHECK is extended by migration |

With HD-10..HD-15 given, every stop condition in §14 is closed.

**READY FOR F03 IMPLEMENTATION: YES.** Scope is §7 (TRN-Q-001; the
TRN-BURST-005 + TRN-SESS-005 bundle). First Broken Relations to repair
first: FBR-F03-2..6. Falsifiers: §11 plus the HD-12 and HD-13 cases.
Acceptance: §12. Implementation starts only on explicit F03 execution
authority.

---

## 16. Materialization pointer (F03 implementation, appended)

Implemented in WU-03.0..03.11 (see `STATUS.md`, `FIELD_REVIEW.md`, `PROOF_MATRIX.md`).
FBR-F03-2..6 were repaired first. Two further First Broken Relations were found
and repaired at their homes: FBR-F03-7 (a BND-014 DENY left the attempt
IN_PROGRESS) and FBR-F03-8 (the PKG-28 GetSession read bypassed HD-13). Nothing
above was rewritten.
