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
