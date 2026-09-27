# WU-CY-01 — Human Visual Review Guide

**Runtime:** `http://127.0.0.1:13500` — compose project `nquiry-cy01-inspect`: the pinned RED producer
`checkpoint-PFC-B5` (`7d3f74e4685b821cc948f45e413c1e0c207259d4`, MockProvider in `NQUIRY_ENVIRONMENT=TEST`) behind this
tree's web app; its own database volume. The SF-06 review runtime `:13400` (published F03 producer) is untouched and
stays the visual reference for everything that must not have changed.

**What is under review:** the ANALYSIS boundary as a projected relation (WU-CY-01.md) — one new lawful transition,
one new chamber (the derived field), the proof mode of a Session. Everything else on the Session page is the
human-reviewed SF-06 organism and must look and behave as before. TECHNICAL PASS ≠ HUMAN VISUAL ACCEPTANCE: the
technical proof surface is closed (WU-CY-01.md §4); this review decides acceptance.

**Ceiling to keep in mind while looking:** everything derived is MOCK / NON_PROOF (the MockProvider is the only
provider), a Fixture Session is FIXTURE_NON_PROOF, and the producer is checkpointed, not reviewed. The frontend must
say exactly that, and never more.

## 1. Accounts

All four are local, dev-provisioned identities (identity rows only); every membership, role, authority and
participation below was created through the product API, never by direct database writes. The passwords were issued
once in the review session and are not repeated here.

| Account | Name | Role in the Workspace | Authority | Participation |
|---|---|---|---|---|
| `owner@cy01.local.test` | CY-01 Owner | Owner (founder, governance root) | WORKSPACE_GOVERNANCE_RIGHT; **no** Session control | none |
| `facilitator@cy01.local.test` | Maya Torres | Facilitator | SESSION_CONTROL_RIGHT at CHALLENGE scope and at SESSION scope for A, B and C | participant in A, B, C |
| `ravi@cy01.local.test` | Ravi Shah | Contributor | none | participant in A, B, C |
| `elena@cy01.local.test` | Elena Park | Contributor | none | participant in A, B, C |

**Maya** is the only account that can begin analysis. **Ravi** (or Elena) is the frozen-set audience without
authority. The **Owner** is neither participant nor controller of any Session.

## 2. Prepared scenario

Workspace **Onboarding inquiry** `2c8b7729-868c-46e2-af9a-8ef40ba4afee`
Challenge **Where does onboarding lose enterprise admins?** `49369d62-93a7-452f-bfab-1dacdb1fbc52`
Session URL pattern: `http://127.0.0.1:13500/workspaces/2c8b7729-868c-46e2-af9a-8ef40ba4afee/sessions/<sessionId>`

| Session | Id | Proof mode | Expected canonical state at the start of the review | Content |
|---|---|---|---|---|
| **A** | `58ed8f33-7074-5593-ad20-2e0382c45941` | GOVERNED | **QUESTION_CAPTURE**, Burst COMPLETED, version 6 | 3 frozen human questions (Ravi, Elena, Maya) |
| **B** | `77276c5e-d912-547c-a9b7-bb5f74c5cf07` | **FIXTURE_NON_PROOF** | **QUESTION_CAPTURE**, Burst COMPLETED | 2 frozen human questions (Ravi, Elena) |
| **C** | `b2c9af2a-ff08-5099-9c23-3b3f9ac3ace1` | GOVERNED | **ANALYSIS**, analysis ACCEPTED (MOCK / NON_PROOF), clustering ACCEPTED | 3 frozen human questions; taken across the boundary through the API by Maya so the end state can be seen without acting |

Session A is the one you cross yourself. Crossing is irreversible (a governed transition); C stays as the reference.

## 3. Order of review

### Step 1 — Session A as Ravi (participant, no authority)

Log in as `ravi@cy01.local.test`, open Session A.

Verify:
- Path: Workspace › Challenge › Session › **QUESTION_CAPTURE** as the current, breathing station.
- Core: "Frozen human question set", state QUESTION_CAPTURE, "You: Role: Contributor · Not the Session controller · Participant". **No** fixture tag.
- Ring 1 (lifecycle): 1–4 passed, **5 Question capture current**, **6 Analysis later**, 7 Reflection later; later phases as small spheres whose names open in the focus lens.
- Frozen chamber: the 3 questions verbatim with the `human` tag, "immutable", fingerprint verified. **No "Begin analysis" button.** Instead the producer's reason as a classed boundary mark **MISSING_AUTHORITY** ("Requires SESSION_CONTROL_RIGHT …") — a boundary, not an alert, not red.
- **Derived field** chamber (new, below participants/proof, above the Decision surface): title "Derived field" in the derived type role (italic), dashed glyph and inner contour, marker **not begun**, Status NOT_BEGUN, Generations 0. **No** Proof line, **no** provider, **no** derived text — nothing exists yet and nothing is invented.
- Proof chamber: spine ending in `COMPLETE_BURST`; **Proof mode GOVERNED** — "A governed Session: its commits are the proof."

Must remain impossible here: any affordance for Ravi; any word of an analysis result; the word "proof" for anything derived.

### Step 2 — Session A as Maya (Session controller): cross the boundary

Log in as `facilitator@cy01.local.test`, open Session A.

Verify before acting:
- Same page as Ravi's, except the frozen chamber now shows **Begin analysis** as the lawful next transition, with its explanation ("Closes the human question regime … a proposal, marked AI-derived and NON_PROOF; it never becomes a question").
- Core meta: "You: Role: Facilitator · Session controller · Participant".

Press **Begin analysis**. Verify the re-read gate, in this order:
1. Outcome "Committed" with the reconstruction note **reading** — the ring, the core state word and the derived chamber do **not** change yet.
2. After the canonical re-read: state **ANALYSIS**; ring **6 Analysis current**, 5 passed, 7 Reflection next (labelled), later phases as spheres; path station ANALYSIS.
3. The resonance event **ANALYSIS BEGUN** appears once ("… anything derived is AI-derived and NON_PROOF") and leaves on its own.
4. Derived field chamber: marker **accepted**; Status ACCEPTED; **Proof MOCK / NON_PROOF**; Provider mock; Accepted <time>; Clustering ACCEPTED; Generations 2; the note "Produced by the development MockProvider. It is not an analysis of these Questions and is not proof of anything."; origin read as "AI-derived from the frozen human question set".
5. The frozen human set is unchanged: 3 questions, verbatim, `human`, immutable. **No derived sentence, label or cluster appears anywhere on the page.**
6. No further button: Begin analysis is gone; no request / retry / clustering affordance (out of WU-CY-01).
7. Proof chamber: spine now ends in `CMD_BEGIN_ANALYSIS` by Maya Torres, authority SESSION_CONTROL_RIGHT at SESSION scope, commit id; Proof mode GOVERNED.

Also verify motion and calm: nothing else in the organism moved; the organ still scrolls internally at desktop width; on a phone viewport the chambers stack in the same order (frozen · control · participants · proof · derived · decision entry).

### Step 3 — Session C as Maya, then as Ravi (the end state as reference)

Open Session C as Maya (still logged in).

Verify:
- State ANALYSIS; ring 6 current; the derived field exactly as A became in Step 2 (accepted · MOCK / NON_PROOF · mock · Clustering ACCEPTED · Generations 2 · note).
- Proof spine `CMD_BEGIN_ANALYSIS`; Proof mode GOVERNED.
- Compare A and C side by side: they must read identically apart from questions and times.

Log in as `ravi@cy01.local.test`, open Session C:
- The same derived field is visible (frozen-set audience), still without any affordance; the boundary mark for BEGIN_ANALYSIS is gone because the transition is no longer relevant in ANALYSIS.

### Step 4 — Session B as Maya (Fixture Session)

Open Session B as `facilitator@cy01.local.test`.

Verify:
- Core meta carries the tag **FIXTURE_NON_PROOF** (hover: "a Fixture Session: nothing here is proof").
- Proof chamber: **Proof mode FIXTURE_NON_PROOF** — "A Fixture Session declared at creation: nothing in it is proof of anything." The spine still names the governed commit (fixture is a proof ceiling, not a missing commit).
- Everything else identical in shape to Session A before the crossing: 2 frozen questions, Begin analysis available to Maya, derived field "not begun".
- Optional: press Begin analysis here too. The fixture Session crosses the boundary exactly like A; the derived field is MOCK / NON_PROOF; the FIXTURE_NON_PROOF tag stays.

### Step 5 — Challenge page as Maya (the fixture choice)

Open the Challenge "Where does onboarding lose enterprise admins?" as Maya.

Verify in the "Open a Session" chamber: the checkbox **Open as a Fixture Session**, unchecked by default, with the note
"Declared at creation and immutable: a Fixture Session is FIXTURE_NON_PROOF everywhere it appears." Do not open a new
Session unless you want a fourth one; the choice is only to be seen. The Sessions ring of the Challenge shows A, B, C
with their states.

### Step 6 — the Owner (nothing new for a non-participant)

Optional. Log in as `owner@cy01.local.test`, open Session A or C: the Owner is the governance root but neither
participant nor controller — no Begin analysis; the derived field is shown only if the producer serves the frozen set
to the Owner (frozen-set audience is the producer's decision, HD-13/HD-22), otherwise not at all. Nothing is inferred
either way.

## 4. What must remain true (the SF-06 organism)

Compare with `:13400` where in doubt: round orbits and sphere core; family spheres and satellites; the focus lens on
encounter; the glass bento organ with membranes, motes and inner light; chevron path with the breathing current
station; the wordmark; no green token; no timer-driven change; text never below the material-text law; reduced motion
removes every animation and keeps every meaning; no horizontal scroll at any width.

## 5. Possible verdicts

- **PASS** — WU-CY-01 accepted visually (not FIELD_GREEN, not REVIEWED_FIELD, not PUBLISHED_FIELD until the
  corresponding conditions exist; nothing is committed without your explicit word).
- **REPAIR_REQUIRED** — name the chamber, relation or motion; the repair stays inside WU-CY-01's scope.
- **REJECT** — rollback is `field-SF-06` for CYAN and `checkpoint-PFC-B5` for RED, independently.

## 6. Runtime notes

- Rebuild the runner only (never re-seed): the runtime keeps its volume; re-running the seed would found a second
  Workspace.
- The lane behind the numbers in WU-CY-01.md is `scripts/run_cy01_real_stack.sh` (own project `nquiry-cy01`, no host
  ports); it never touches this review runtime.
- Host load from the desktop makes the real-stack specs slow (F03 protected ≈ 2–3.5 min); that is lane timing, not
  product behaviour.
