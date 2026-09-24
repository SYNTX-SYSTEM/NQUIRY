# SFE Agent Reconstruction — 2026-09-24

Bootstrap report of a new engineering agent with no conversational memory.
Mode: reconstruction only. **No implementation, no stage, no commit, no push.**
Every claim below was reconstructed from repository files, git state, or
commands executed in this run. Where a claim rests on a sub-sweep rather than
first-hand reading, it is marked *(sweep)*. Findings I verified personally
are marked **[verified]**.

---

## 1. REPOSITORY TRUTH

| Item | Value |
|---|---|
| Main checkout | `~/Entwicklung/nquiry`, branch `master` @ `c529d3d` (F00), **behind origin/master by 1** |
| origin/master | `0ea5bbb` "Field F01: Identity, Workspace, and Governance vertical (FIELD PASS)" |
| Worktree | `.claude/worktrees/local-login-auth`, branch `worktree-local-login-auth` @ `0ea5bbb` (= origin/master); upstream branch `origin/worktree-local-login-auth` **gone** |
| Worktree dirty state | 39 tracked files modified, 55 untracked paths (94 porcelain lines) = **all of F02, uncommitted** |
| Index | empty in both checkouts |
| Stash | `stash@{0}` "On master: pre-login-merge leftover work, unreviewed" (2026-09-21): 9 files (web clients/tests, RUNTIME_OPERATION.md). **Owner: no Field. Unreviewed. Not to be touched.** |
| Main checkout dirty state | 6 modified docs + untracked F02 reports + doc 20 + reconciliation record + `.claude/worktrees/`. **Byte-identical copies** of the worktree's doc files (verified with `cmp`/`diff -rq`). They are a docs-only mirror on top of an F00 base. The main checkout contains no F02 code. |
| Runtime | docker project `nquiry`: postgres (:15432, healthy), api (:8000, `/healthz` 200), web (:3000). Containers built 2026-09-24 02:08 CEST from the worktree. No code file has changed since the build **[verified]**. |
| Migration head | `b3d8e5f0a2c7` on both `nquiry` and `nquiry_test` **[verified]** |

**Material WIP ownership**

| WIP | Owner Field | Status |
|---|---|---|
| All worktree changes (code, 2 migrations, tests, web, docs, 16 §41, doc 20) | F02 | FIELD_GREEN_WITH_DISCLOSED_EXTERNAL_CEILINGS (self-declared), awaiting `FIELD_COMMIT_APPROVED F02` |
| Main-checkout doc copies | F02 (mirror) | Duplicate of the worktree. Must not diverge. |
| `stash@{0}` | none | Pre-F01, unreviewed |
| This report | bootstrap (no Field) | Untracked, new |

**Structural git fact.** The canonical line of development is the worktree
branch. `master` in the main checkout is one commit behind origin and carries
F02 docs on an F00 code base. Publishing F02 means committing in the
worktree. Human authority decides how `master` then catches up (fast-forward
or otherwise). I have not touched either checkout.

---

## 2. AUTHORITATIVE ARCHITECTURE MAP

### Authority stack (reconstructed; two naming schemes collide)

- **Doc 20 §0 (SFE, HUMAN AUTHORIZED 2026-09-24):**
  `LEVEL 1 SFE (how)` → `LEVEL 2 product architecture 00–18 + 16 ledger`
  → `LEVEL 3 HEAD (evidence, not authority)` → `LEVEL 4 Field (19)` → `LEVEL 5 Work Unit`.
  20 never overrides product semantics.
- **Doc 00 §3:** LEVEL 1 = N.Q.U.I.R.Y. Product & System Specification
  (external source, not in repo). LEVEL 2 = sweep document. LEVEL 3 =
  architectural closure. The 00–13 chain derives from those.
- **Collision.** "LEVEL 1/2" means different things in 00 and in 20. There
  is no semantic contradiction: 20 governs process, 00 governs product.
  Reports should say which scheme they mean.

### Document → semantic ownership

| Doc | Owns | Status header |
|---|---|---|
| 00 Master | system map, module authority map (§18), status vocabulary | DRAFT FOR HUMAN REVIEW |
| 01 Boundary/Principles | system principles, Burst modes, CONFLICT-007 origin | DRAFT |
| 02 Domain/Relation | objects, relations (SessionParticipation = relation §12; FrozenRawQuestionSet = projection §13.7) | DRAFT |
| 03 State/Transition | Session 13 states, TRN-SESS-001..013, TRN-BURST-001..005, TRN-Q-001, 4 generic outcomes (§8) | DRAFT |
| 04 Authority | AUTH-DEP-* per operation | DRAFT |
| 05 Governance | GOV-*, FacilitatorScopeBinding (§20, GOV-008), SessionControl assignment (GOV-009) | DRAFT |
| 06 Boundaries | BND-001..018 (BND-008 contamination, BND-009 AI invocation, BND-014 commit) | DRAFT |
| 07 Evidence/Provenance | origin classes, human-question minimum provenance (§54.1) | DRAFT |
| 08 AI | Gateway chain, AIContextManifest, AIGeneration lifecycle, AIOP registry, effect matrix §39 | DRAFT |
| 09 Data/Event/API | fields, commands, API envelope (§77/78), idempotency record | DRAFT |
| 10 Failure/Recovery | "no fifth outcome", failure classes F-NET, F-PROVDR | DRAFT |
| 11 Security/Privacy/Observability | — | DRAFT |
| 12 Minimum Prototype | prototype narrowing: HUMAN_ONLY, manual completion, AIOP-001 only | DRAFT (+ F02 post-baseline notes, uncommitted) |
| 13 Test/Falsification | P-01..25, TF-QUESTION, TF-BURST, attack catalogue | DRAFT |
| 14 / 15 | PKG-00..32 sequence and prompts | historical, closed (20 §0) |
| 16 Decision/Gap Register | canonical ledger; §41 post-baseline records = current | READY_FOR_HUMAN_REVIEW (+ §41 uncommitted) |
| 17 / 18 | live runtime materialization; local auth adapter | committed |
| 19 Field Execution Master | F00–F12 content, DAG, WU/Field report templates (§13/§14/§15) | applied form of 20 |
| 20 SFE | engineering law, HD-1/3/6/7/8 | **untracked (F02 WIP)** |
| 00_AGENT_WORKFLOW | PKG-era process | superseded for Field execution by 19/20 |
| `docs/RUNTIME_OPERATION.md` | runbook (§18 routes, §22 isolated test DB) | modified (F02) |

Documentation convention: `docs/implementation/field-reports/<Fxx>/`
holding `STATUS.md`, `WU-xx.y.md`, `FIELD_REVIEW.md`, `CHATGPT_REVIEW.txt`.
Proof reports: `docs/implementation/proof-reports/`. Corrections are made
through successor records (e.g. `F02-PROOF-LANGUAGE-RECONCILIATION.md`).
There was no convention for bootstrap reports; this file creates
`docs/implementation/agent-bootstrap/` as the prompt suggests.

**Important status fact.** 00–13 still say "DRAFT FOR HUMAN REVIEW", and
16's header says "BASELINE: NOT HUMAN APPROVED". Implementation has
nevertheless proceeded on them (F00–F02 approved per Field). The repository
treats them as operative LEVEL-2 architecture without a formal freeze. F02
disclosed this as a known limitation.

---

## 3. SFE COMPREHENSION (own words)

- **Field.** The whole set of objects, relations, authorities and boundaries
  that together decide which next change is legitimate. It is the unit of
  engineering because meaning only holds at that level. A ticket or file is
  just a place where a Field's relations happen to be written down.
- **Relation.** How one thing affects what is true or legitimate for
  another, for example "binding X at SESSION:s makes actor A's
  OpenQuestionGeneration admissible". Code is the storage of relations, not
  the relations themselves.
- **State.** The authoritative configuration right now: canonical rows and
  their versions. It is not the UI's belief or a cached projection.
- **Delta.** One admitted effect that changes State. In NQUIRY a Delta
  exists only once it passes the effect gate (CommitCoordinator + BND-014).
- **Boundary.** The place where the Field no longer contains enough to
  close the next relation on its own. It is not an error.
- **Authority.** Whatever may legitimately close what autonomy may not.
  Human authority is one kind. Typed binding, role or founding sources are
  its materialized runtime forms.
- **Reconstruction.** After a Delta, derive the Field again from actual
  state rather than carrying the old Field forward. At runtime this means
  per-request authority resolution, commit-time revalidation and
  post-commit reread. In engineering it is exactly what this report does.
- **Child law.** A child Field or Work Unit may narrow what it inherits. It
  may never quietly widen authority, drop a boundary or re-mean a parent
  concept. Narrowing is safe because every parent guarantee still holds.
- **Tree vs graph.** The tree tells me where I am and who may authorize
  here. The graph tells me what my change touched elsewhere. A change is
  local in the tree and global in the graph.
- **Candidate vs effect.** Anything (AI output, a UI click, a proposal) can
  exist as a candidate. Only the gated transition makes it effective.
  Governance sits in that gap, not in the candidate's source.
- **Human-authority recursion.** For every open relation: derivable → do
  it. Several interchangeable options → pick one, record it. Resolving it
  would create meaning, authority, protected effect or external consequence
  → stop and ask. "I don't know" alone is not grounds to ask; "answering
  would invent something" is.
- **First Broken Relation.** The failure surfaces somewhere; the cause
  lives at the first upstream relation that no longer holds. Repair that
  relation where it is owned, then propagate forward.
- **Recursive DeepSweep.** After a change, walk outward (producers,
  consumers, siblings, persistence, API, UI, tests, docs) to find what else
  it changed.
- **Inverse DeepSweep.** Before claiming a visible effect, walk it back to
  its origin. Every hop must be real; one mocked or fixture link voids the
  claim.
- **Field GREEN.** The relations the Field promised hold end to end, the
  forbidden effects are still impossible, and the documentation says so. A
  local test pass is only evidence toward this.
- **Documentation law.** Docs are part of the Delta. An undocumented WU is
  not done, and architectural resolutions must reach their ledger (16 §41,
  20 §15, the owning doc) in the same WU.
- **Git authority law.** Publishing into shared history is itself a
  consequential effect with its own authority (the human, via
  `FIELD_COMMIT_APPROVED Fxx`). Being green is not permission to commit.

---

## 4. FIELD MAP

| Field | Purpose | State | Proof status | Ceilings / notes |
|---|---|---|---|---|
| F00 Execution control | proof harness and loop | FIELD_PASS, committed `f27942e` (+`c529d3d`) | browser claims corrected to MOCKED by successor record | — |
| F01 Identity/Workspace/Governance | legitimacy, founding (HARD-DEP-001 Option A), membership, grants, revoke | FIELD_PASS, committed `0ea5bbb` (origin/master) | backend live-DB; browser only MOCKED plus manual real check | GAP-14-001 (prod IdP) |
| **F02 Challenge/Session/Participation** | governed inquiry context up to QUESTION_GENERATION | **FIELD_GREEN_WITH_DISCLOSED_EXTERNAL_CEILINGS (self-declared), UNCOMMITTED** | real-stack lane 4/4 (per report); live-DB 1342/2 skip and pure 745 **[re-verified this run]**; vitest 91 **[re-verified]**; static gates PASS **[re-verified]** | see §6. **Two confirmed defects contradict its review.** |
| F03 Protected Human Question Field | capture, completion, frozen set | NOT_STARTED | — | parent F02 uncommitted |
| F04 AI boundary / post-Burst sensemaking | Gateway, AIOP-001, derived field | NOT_STARTED | — | HARD-DEP-002 external; MockProvider only |
| F05–F07 | reflection → decision/action | NOT_STARTED | — | — |
| F08 Events/workers/projections | outbox consumption | NOT_STARTED | worker is a no-op; outbox written, never consumed | may start after F03 event contracts |
| F09–F12 | failure/security, runtime, semiotic frontend, acceptance | NOT_STARTED | — | F11 foundation partially laid in F02 (`globals.css`) |

**F02 Work Units** (all reported PASS): WU-02.0 GrantHumanAuthorityBinding;
02.1 Create/GetChallenge (ROLE: Facilitator); 02.2 ChallengeCapability;
02.3 CreateSession (SESSION_CONTROL_RIGHT at CHALLENGE); 02.4 doc 20 plus
ledger; 02.5 real-stack lane plus DEV identity (HD-3); 02.6 typed authority
sources (HD-6); 02.7 Session control, transitions, Burst prepare,
TRN-SESS-004 bundle (HD-1); 02.8 participation (HD-7/HD-8); 02.9 HTTP
envelope, idempotency and projections; 02.10 frontend and F11 foundation;
02.11 field-end proof.

---

## 5. HUMAN AUTHORITY DECISIONS

| ID | Decision | Scope | Persisted | Depends on it |
|---|---|---|---|---|
| NQ-DEC-001..021 | baseline decisions (question-first, original_text immutable, AI output derived, CommitUnit, BND-014, Gateway exclusive, **016 HUMAN_ONLY Burst**, **017 manual authorized Burst completion**, 018 one selector …) | whole system | 16 §6 | everything |
| REC-001 / NQ-DEC-022 | HARD-DEP-001 Option A: any verified human may found a Workspace and becomes its governance root (replaceable eligibility step) | founding | F01 WU-01.4 (2026-09-21); 16 §41 (uncommitted) | CreateWorkspace, FOUNDING source |
| HD-1 / NQ-DEC-032 | SESSION_CONTROL_RIGHT for Session transitions resolves at `SESSION:<id>`, with no inheritance | Session control | 20 §15; 16 §41 REC-002 | session_control_handler, burst prepare, queries |
| HD-3 / NQ-DEC-033 | DEV-ONLY local identity provisioning without any membership or authority | dev proof | 20 §15; REC-003 | real-stack lane identities |
| HD-6 / NQ-DEC-034 | effect gate typed sources BINDING / ROLE / FOUNDING; no fabricated provenance | effect gate | 20 §15; REC-004 | coordinator, BND-014 v1.1, audit migration |
| HD-7 / NQ-DEC-035 | Session controller admits active Workspace members as participants; no self-join | participation | 20 §15; REC-006 | CMD_ADMIT_SESSION_PARTICIPANT |
| HD-8 / NQ-DEC-036 | at least one participant before QUESTION_GENERATION | TRN-SESS-004 | 20 §15; REC-007 | open-question-generation blocker |
| REC-005 | mocked browser proof is not real-stack proof (wording correction) | proof language | 16 §41; reconciliation record | report language |
| REC-008 | Documentation Hard Law | process | 20 §14; 16 §41 | all WUs |
| WU-02.0 decision | grant Command built in F02; Owner ≠ Facilitator | grants | WU-02.0.md (2026-09-22) | grant handler |
| WU-02.2 decision | ChallengeCapability option A | projection | WU-02.2.md | capability projection |
| "Tobi" / commit gates | `FIELD_COMMIT_APPROVED F00`, `F01` given | publication | STATUS.md | commits `f27942e`, `0ea5bbb` |

Still **REQUIRED** in 16 (not decided): NQ-DEC-023 export authority home,
024 provider/privacy eligibility, 025 target market, 026 AI autonomy,
027 data sovereignty, 028 collaboration, 029 measurement, 030 methodology
governance, 031 AI provider.

---

## 6. OPEN RELATIONS

### Defects in the uncommitted F02 (contradict the F02 FIELD_REVIEW) **[verified]**

1. **Session-command idempotency collision is not rejected.**
   `packages/application/session_control_handler.py:146-162` `_replay_guard`
   treats any COMMITTED record with the same key as a replay. It checks
   `existing.command_id == ident.command_id`, which is always true because
   the key *is* the command_id, and it never compares the payload
   fingerprint. So reusing a key with a different `expectedVersion` or
   `participantUserId` (same workspace and command type) returns
   `committed` + `replayed`, not `rejected`. FIELD_REVIEW claims "same key
   with a different payload is `rejected`". That claim holds only for
   challenge, session and grant creation. There is no test for the Session
   commands.
2. **`rejected` breaks the `/decision` consumer.** F02 changed
   `GET /workspaces/{w}/sessions/{s}` to return
   `{"kind":"rejected"}` (`apps/api/src/nquiry_api/http/queries.py:46-48`).
   `apps/web/lib/api/client.ts:108-126` `parseSessionReadResult` throws on
   `rejected`, and the UI shows a network error. This is a producer/consumer
   relation the F02 DeepSweep missed.

### Further drift *(sweep, spot-checked)*

- **Doc 20 §15 vs 16 §41.** Doc 20 says "reconciled … as NQ-DEC-032..034";
  §41 has 032..036 **[verified in 20]**.
- **16 internal consistency.** The counts (§36/§40) still read BLOCKED 1 /
  ESTABLISHED 21. Several passages (§39, §40 Q17/Q22, P-10/12/22/23/25,
  PKG-02..04) still cite HARD-DEP-001 as blocking. NQ-DEC-032..036 are
  absent from the §6 table and the YAML. The status tokens are
  non-standard. GAP-09-007 has no canonical NQ-GAP row even though REC-006
  "closes" it. NQ-GAP-068's alias list is incoherent (it contains
  GAP-14-001..005).
- **F01 routes** still return HTTP 200 for denied, rejected and
  indeterminate bodies, and have no `stale` or `failed_precommit` kind. The
  "common envelope" covers only the 11 F02 routes.
- **FastAPI RequestValidationError** falls through to its default 422
  `{detail}`, which collides with the envelope's `blocked`=422 and is not
  `rejected`.
- **The static "no parallel writer" test** matches only the literal
  `with connection.begin_nested(`.
- **Stale docstrings:** `commit/coordinator.py:329-332`,
  `application/burst_operations.py:38,87` (WORKSPACE scope, a module no
  longer wired into production).
- **Nullability.** `audit_events.authority_source_type` is nullable. "Every
  new row typed" is enforced in code only.
- **Burst lookup.** `burst_repository.get_by_session` uses `one_or_none`,
  but the DB only enforces one *open* Burst. A second Burst after
  COMPLETED would make it raise. This is F03-relevant.
- **`establishedBy`** (`inquiry_directory.py`) uses `one_or_none` on
  `state_after_ref`. It is only correct while no state is ever re-entered.
- **Frontend:** `inquiryClient` casts `ok`/`committed` bodies without shape
  validation. Add-member is gated on the F01 `governanceCapable` boolean
  rather than the server's `overview.capabilities.addMember`. The F02 pages
  have no mocked/component tests. `/decision` and `/login` lack labels and
  the AppShell.

### OPEN / BLOCKED / HUMAN_DECISION_REQUIRED / EXTERNAL

- **HUMAN_DECISION_REQUIRED (Case 3, F03-blocking):** Burst control
  authority source. See §10 and §13.
- **CONFLICT-007 (OPEN SOURCE TENSION):** Burst duration. NQ-GAP-022 pause
  and timer semantics; NQ-GAP-032 timer identity and trust. *Contained* by
  NQ-DEC-017 and 12 §11: the timer is presentation only, completion is
  manual. **Does not block F03** unless the human wants automatic
  completion.
- **OPEN, relevant to F03:** NQ-GAP-019 Question.status (omit the field);
  NQ-GAP-008 text vs original_text (persist original_text only); NQ-GAP-009
  origin/source axis (AC-02-002 orthogonality applies); NQ-GAP-023
  questions-only enforcement mechanism (no AI evaluation may be introduced;
  the predicate is defined); NQ-GAP-050 idempotency identity; GAP-09-007
  remainder (leave/remove); NQ-GAP-029 Session control multiplicity;
  GAP-06-001 commit freshness; GAP-03-001 Session cancellation.
- **EXTERNAL_DEPENDENCY:** HARD-DEP-002 / NQ-GAP-060 (real AI provider;
  requires D3 + D9 + data classification); GAP-14-001 (production IdP).
- **Architecture tensions** (12 vs 03/04), not marked in the docs:
  - Burst start/complete authority (12: SESSION_CONTROL_RIGHT; 04/05:
    Facilitator + FacilitatorScopeBinding).
  - 12 §10 lists QUESTION_GENERATION→ANALYSIS, which 03 declares illegal
    (QUESTION_CAPTURE in between).
  - 12's happy path orders Session QUESTION_GENERATION before Burst
    PREPARED, which is incompatible with TRN-SESS-004. F02 followed 03.
  - 19 F04 "AI unavailable leaves human workflow usable" vs 03 GAP-03-006
    (no skip path from ANALYSIS without AI_VALIDATION_PROOF).
- **Test gaps:** Session-command idempotency collision; `rejected` on
  `/decision`; F02 component tests; FastAPI validation envelope.
- **Runtime gaps:** worker is a no-op and the outbox is never consumed
  (F08). The AI gateway is not reachable from HTTP (F04).
- **Frontend gaps:** no question capture, no Burst completion, nothing past
  QUESTION_GENERATION, no revoke UI, member added by raw user id, no
  AI-origin rendering in F02 pages.
- **Documentation drift:** 00–13 "DRAFT" headers; 16 header "NOT HUMAN
  APPROVED / IMPLEMENTATION: NOT STARTED".

---

## 7. TEST PROOF MAP

| Lane | Command | Count (this run) | Proves |
|---|---|---|---|
| Pure Python | `pytest tests/ apps/api/tests` (no DATABASE_URL) | **745 passed, 599 skipped** | domain, semantic, static checks; skips are the visible SKIPPED_NO_DATABASE convention |
| Live DB (isolated `nquiry_test`) | `DATABASE_URL=…/nquiry_test pytest` | **1342 passed, 2 skipped** | persistence, triggers, RLS, commit gate, handlers, HTTP via TestClient (`test_http_f02` monkeypatches `connect` onto the real DB) |
| Static / architecture gates | 4 scripts | **PASS** (migration live check skipped without URL) | import DAG, provider-SDK containment, test-only imports, single linear migration head (22) |
| Vitest | `npx vitest run` | **91 passed** | client parsers, display components (renderToStaticMarkup) |
| Playwright MOCKED | `npm run e2e` | 37 (per report, not re-run) | component contract only (`page.route`), **never runtime proof** |
| Playwright REAL-STACK | `npm run e2e:real` | 4 (per report, **not re-run**: it writes durable history into `nquiry`) | real browser → web → FastAPI → local auth → PostgreSQL → governed Commands. The global setup refuses route mocking. |
| Adversarial | security/*, mutation harness, real-stack page-level fetches | included above | cross-workspace, stale, forged scope, key reuse (challenge only) |

Fixture ceilings: `scripts/seed_local_demo.py` (NON_PROOF, labelled in the
UI from provenance); `nonproof_bootstrap`; grant-suite direct Challenge
inserts; dev identities (HD-3). The only Decision data comes from the
NON_PROOF seed.

Mock ceilings: the mocked Playwright lane; MockProviderAdapter (AI, not yet
wired).

---

## 8. FRONTEND CURRENT STATE

- **Routes:** `/` (→ `/workspaces` or `/login`), `/login`, `/workspaces`,
  `/workspaces/[w]`, `/workspaces/[w]/challenges/[c]`,
  `/workspaces/[w]/sessions/[s]` (inquiry position),
  `/workspaces/[w]/sessions/[s]/decision` (PKG-28/29 prototype view,
  real backend, fixture-only data).
- **Real backend connections:** every route above talks to the real API
  (cookie on :8000).
- **Capability projections:** server `{available, reasonCode, reason,
  relevant}` drives every F02 control. Unavailable shows the server's
  reason and no control. There is no client-side role inference (display
  of server values only).
- **Authority visibility:** bindings with holder, class, grantor and scope.
  Session controllers are listed.
- **State visibility:** phase list (display only, `aria-current=step`),
  Burst state and mode. "AI is absent while the burst is open."
- **Failure visibility:** distinct `Outcome` for committed, denied,
  rejected, stale (with current state), blocked, failed_precommit,
  indeterminate, not_found and network_failure.
- **Provenance:** "established by" (command, actor, typed authority source,
  scope, commit). NON_PROOF label derived from `governedFounding`.
- **Responsive and a11y:** tokens with light/dark, breakpoints at 640 and
  860, 44px targets, focus-visible, reduced motion. axe shows 0
  serious/critical on F02 pages (per report).
- **Clickable today:** login → found Workspace → add member (raw id) →
  create Challenge (Facilitator) → grant Challenge-scoped control → open
  Session → grant Session-scoped control → begin setup → begin challenge
  capture → prepare Burst → admit participant → open question generation.
- **Not implemented:** question capture ("arrives with F03"), Burst
  completion, anything after QUESTION_GENERATION, revoke UI, AI surfaces,
  Decision creation.

---

## 9. END-TO-END INVERSE TRACE (deepest real visible effect)

Visible `session-state = QUESTION_GENERATION`, Burst `ACTIVE HUMAN_ONLY`:

| Hop | Evidence | Status |
|---|---|---|
| visible effect | session page `data-testid=session-state` | REAL (real-stack spec) |
| frontend | renders server `position` from the post-commit reread | REAL |
| API | `POST …/transitions/open-question-generation` (`http/inquiry.py`), `Idempotency-Key`, `expectedVersion` | REAL |
| application | `session_control_handler` `CMD_OPEN_QUESTION_GENERATION` | REAL |
| command | CommandEnvelope and attempt rows | REAL |
| boundary | BND-001/002/003/005/007 precommit, BND-014 v1.1 at commit | REAL |
| authority | BINDING `SESSION_CONTROL_RIGHT` at `SESSION:<id>`, granted by the WORKSPACE_GOVERNANCE_RIGHT holder | REAL. **But its sufficiency for the coupled TRN-BURST-002 (Burst START) is an interpretation. See §10 FBR-A.** |
| domain | TRN-SESS-004 + TRN-BURST-002 in one mutation | REAL |
| persistence | sessions/question_bursts rows, commit_units, audit_events (typed), outbox | REAL (outbox unconsumed) |
| provenance | `establishedBy` command, actor, source, scope, commit | REAL |
| origin | membership (CMD_ADD_MEMBER) ← FOUNDING (CMD_CREATE_WORKSPACE) ← verified local login (dev-provisioned identity, HD-3) | REAL, with the disclosed identity ceiling (GAP-14-001) |

No mocked or fixture hop. One hop rests on a disputed authority mapping.

---

## 10. FIRST BROKEN RELATIONS

**FBR-A: Burst control authority source (architecture ↔ implementation;
Case 3).**
- 04 §36 AUTH-DEP-BURST-002 (START), §37 (PAUSE), §38 (RESUME) and §39
  (COMPLETE) name the **Facilitator** as the source right. 05 §20 closes
  GAP-04-005: "Workspace Facilitator role + ACTIVE Session
  FacilitatorScopeBinding → source-explicit Burst control rights in that
  Session. This does not grant generic Session Control."
- 12 (prototype tables §9/§23) says "SESSION_CONTROL_RIGHT plus
  facilitator scope where applicable".
- FacilitatorScopeBinding does not exist in code (`bnd_004_role_context.py`
  says so and requires callers to REQUIRE rather than treat a role as
  sufficient).
- F02 WU-02.7 classified "Session-scoped SESSION_CONTROL_RIGHT **is** the
  explicit source-equivalent binding" as **Case 1**. I cannot reconstruct
  that as derivable. It maps an authority the architecture keeps separate
  ("does not grant generic Session Control", and conversely) onto another.
  HD-1 decided the *scope* of SESSION_CONTROL_RIGHT for Session
  transitions, not which right governs Burst control.
- It already underlies F02's Burst START (inside the TRN-SESS-004 bundle).
  F03's Burst COMPLETE and TRN-SESS-005 (and pause/resume, if in scope)
  cannot be built without closing it.

**FBR-B: F02 idempotency relation (Session commands).** The replay guard
without a payload check (§6.1). Home: `session_control_handler._replay_guard`
and the `commit/idempotency` disposition. F03 capture reuses this pattern
(09 §108.2 requires key + fingerprint for capture), so it must be repaired
before F03 copies it.

**FBR-C: F02 producer/consumer outcome vocabulary.** `rejected` is not
handled by the PKG-28 `client.ts` consumer; F01 routes are outside the
envelope; FastAPI 422 collides with `blocked`. Home:
`client.ts` / `http_dispatch` / an API exception handler.

**FBR-D: The ledger does not reflect its own records.** 16 counts, stale
HARD-DEP-001 references, missing DEC rows, and 20 §15 "032..034". Home: 16
(successor/annotation per §41 convention) and 20 §15.

**FBR-E: Publication.** The F02 parent is uncommitted. F03 as a child
would inherit relations that are not yet in shared history. Home: human
commit authority.

(Future, not blocking F03: `burst_repository.get_by_session` single-row
assumption; the `establishedBy` single-row assumption.)

---

## 11. NEXT FIELD RECOMMENDATION

Dependency truth: F03 depends on F02. F02 is complete *except* for FBR-B,
FBR-C and FBR-D, which are defects inside F02's own claimed scope, and it
is uncommitted.

1. **First: F02 closure** (not a new Field). Repair FBR-B, FBR-C and FBR-D
   at their homes, test-first, with a WU-02.12 report and a FIELD_REVIEW
   successor note correcting the idempotency claim. Then human review →
   `FIELD_COMMIT_APPROVED F02`. All three are Case 1 (derivable from
   existing F02 claims and architecture). They still need the human's go
   because this bootstrap is NO_IMPLEMENTATION, and reopening a Field that
   is under review is the reviewer's call.
2. **Then: F03 Protected Human Question Field**, once FBR-A is closed by
   human authority. Derivable scope:
   - CMD_CAPTURE_BURST_QUESTION: participant right AUTH-DEP-Q-001 (ROLE-like
     relation source via SessionParticipation), verbatim `original_text`,
     key + fingerprint, BND-008.
   - Burst COMPLETE coupled with TRN-SESS-005 → QUESTION_CAPTURE, frozen
     membership fingerprint.
   - Timer as non-authoritative presentation only (NQ-DEC-017, 12 §11).
   - Question.status omitted (NQ-GAP-019).
   - Active-Burst and frozen-set frontend, contamination proof, real-stack
     proof.
3. F08 event-contract work may run in parallel after F03's event contracts
   stabilize (19 §47). F04 follows F03 with an explicit MockProvider
   ceiling (HARD-DEP-002).

---

## 12. SEMIOTIC FRONTEND READINESS (no design)

| Semantic state to represent | Backend truth | Projection exists | Needs architecture decision | Presentation only |
|---|---|---|---|---|
| current Session state / phase | yes | yes (`position.session.state`) | — | form of the phase line |
| possible action | yes | yes (capabilities) | — | — |
| unavailable action + reason | yes | yes (`reasonCode`/`reason`) | — | — |
| boundary (blocked / denied / stale …) | yes | yes (envelope kinds) | F01 routes are outside the envelope | outcome styling |
| authority (holder, class, scope, grantor) | yes | yes | Burst control source (FBR-A) | — |
| human origin | yes (actor, HUMAN_ONLY) | partially (tag on participants/mode) | Question origin/source axis (NQ-GAP-009) for F03 | — |
| AI-derived origin | schema only (ai_generations etc.) | no | F04 | `.tag.ai` token exists, unused |
| canonical vs candidate | canonical yes; candidate/proposal not materialized | no | F04 (AI derived vs adopted, 08 §40) | — |
| committed effect | yes (commitId, establishedBy) | yes | — | — |
| controlled denial | yes | yes | — | — |
| uncertainty (indeterminate) | yes | yes | — | — |
| provenance | yes (typed audit) | yes (last transition only) | history projection (F08) | — |
| history | audit/outbox yes | no | F08 projections | — |
| system position (where in the inquiry) | yes | yes (breadcrumb + phase) | — | layout |
| time / Burst timer | no (by decision) | no | CONFLICT-007 only if timer authority is wanted | a timer display is presentation if non-authoritative |
| NON_PROOF fixture | yes (governedFounding) | yes | — | — |

---

## 13. STOP CONDITIONS

**May implementation begin without new Human Authority?**

- **F02 closure repairs (FBR-B/C/D): semantically YES** (Case 1, derivable
  from F02's own claims, 09 and 16 §41 convention). **Procedurally NO**
  under this run's mandate (NO_IMPLEMENTATION). The operator must say
  whether F02 is reopened for WU-02.12 before commit review.
- **F03: NO.** Exact Case-3 boundary:

  > **Which authority closes Burst control (at minimum COMPLETE_BURST,
  > coupled with TRN-SESS-005 CLOSE_QUESTION_GENERATION; and,
  > retroactively, the START already coupled into TRN-SESS-004)?**
  > (a) Facilitator role + a materialized ACTIVE Session
  > FacilitatorScopeBinding (04 §36–39, 05 §20/GOV-008), which requires
  > building that governance object; or (b) Session-scoped
  > SESSION_CONTROL_RIGHT as the prototype narrowing (12 §9/§23, F02 WU-02.7
  > reading), recorded as a human decision in 16 §41 with a note that it
  > narrows 04/05 for the prototype; or (c) both required.
  > This creates authority semantics. It is not derivable, because the two
  > homes disagree and 05 explicitly separates the rights.

- **Not Case 3 for F03** (already closed or derivable): manual completion
  (NQ-DEC-017), timer as presentation only, HUMAN_ONLY mode (NQ-DEC-016),
  participant capture right (AUTH-DEP-Q-001 + HD-7), immutability
  (NQ-DEC-002), Question.status omission.
- **Conditional Case 3:** automatic timer completion (CONFLICT-007 +
  NQ-GAP-022/032) and pause/resume inclusion only if the operator wants
  them in F03. Leave/remove participation (GAP-09-007 remainder) only if
  F03 needs it (it does not for capture).
- **Publication:** `FIELD_COMMIT_APPROVED F02` is required before F03
  should be built on F02 as a parent in shared history.

---

## ADVERSARIAL SELF-CHECK (corrections made)

- *Role vs authority:* I initially read HD-1 as covering Burst start. It
  does not; HD-1 is about scope for Session transitions. **Corrected →
  FBR-A.**
- *Docs vs implementation:* I did not accept the FIELD_REVIEW idempotency
  claim. I checked the code and **found it false for Session commands.**
- *Mocked vs real:* I did not re-run the real-stack lane (it writes
  durable history into `nquiry`). Its 4/4 is marked "per report". The
  lanes I re-ran are listed with counts.
- *Fixture as runtime:* The `/decision` view has real backend code but
  fixture-only data. It is not counted as a real visible effect.
- *Closed decision inferred from code:* The Burst START authority exists in
  code. I do not treat it as decided (FBR-A).
- *Dirty worktree:* Both checkouts and the stash are inventoried. The main
  checkout's F02 docs are a mirror, not independent WIP.
- *Missed authoritative file:* The LEVEL-1 product specification named by
  00 §3 is not in the repository. I reconstruct it only through 00–13.
  **Disclosed.**
- *OPEN called solved:* CONFLICT-007 is reported as contained, not
  resolved. GAP-09-007 is reported as partially closed.
- *Frontend capability vs backend legitimacy:* Capabilities are
  projections. Commands re-resolve (verified in the handler chain).
- *Local vs Field GREEN:* My re-runs confirm LOCAL/lane green. F02 is
  **not** Field GREEN as claimed until FBR-B/C are repaired.
- *Assumed previous-agent state:* The F02 timestamps (WU-02.4..02.11
  written in about 75 min) and the report's own "disclosed deviations"
  mean TDD order was partly retrofitted. I take the reports at their own
  disclosure and do not upgrade them.

## GIT STATE OF THIS REPORT

New untracked file
`docs/implementation/agent-bootstrap/SFE_AGENT_RECONSTRUCTION_2026-09-24.md`
in the worktree. It is not mirrored to the main checkout. Nothing staged,
committed or pushed.

---

## CLOSURE STATUS (appended 2026-09-24 after F02 WU-02.12)

The reconstruction above is preserved unchanged as the evidence that opened
WU-02.12. Human authority answered its §13 stop conditions: (1) reopen F02
for WU-02.12; (2) HD-9, Option B, prototype narrowing.

| Finding | Status | Where |
|---|---|---|
| FBR-A Burst control authority (Case 3) | CLOSED by HD-9 for the prototype; production model open as NQ-GAP-080 | 16 §41 REC-009 / NQ-DEC-037; 20 §15; 04 §36/§39, 05 §20, 12 §9 pointers |
| FBR-B idempotency | REPAIRED. The root was deeper than reported here: `command_repository.record_attempt` did not enforce Command-type identity (09 §4.3), so a key reused across Command types committed an effect under another Command's row. Cross-Workspace reuse gave a 500 | F02 WU-02.12 |
| FBR-C outcome vocabulary | REPAIRED: two consumers now parse `rejected`; framework validation → `rejected`; `failed_precommit` un-folded on F01/PKG routes | F02 WU-02.12 |
| FBR-D ledger | REPAIRED: 16 §41 REC-010 (counts, rows, YAML, index, LD-1..5); 20 §15 range | F02 WU-02.12 |
| FBR-E publication | OPEN: awaiting `FIELD_COMMIT_APPROVED F02` | human |
| Weak static writer gate, stale docstrings | REPAIRED | F02 WU-02.12 |
| `get_by_session` / `establishedBy` single-row assumptions | Carried forward as F03 entry conditions | F02 FIELD_REVIEW |

Corrections to this report, found during WU-02.12:
- §6/§10 FBR-B understated the defect. It was not only "replay without
  payload check" but also Command-type identity at the command repository.
- §7 listed the mocked lane's 37 as "per report". The lanes additionally
  reuse whatever serves `:3000`/`:8000`, so any lane result must name the
  build it ran against (runbook §22).
