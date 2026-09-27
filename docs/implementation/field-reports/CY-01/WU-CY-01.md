# WORK UNIT REPORT
FIELD: CYAN symbiotic frontend — Session position projection across the ANALYSIS boundary
WORK_UNIT: WU-CY-01
AUTHORITY: HD-27 (HA-03 Option B; `HUMAN_DECISIONS.md` in this directory, verbatim). Human Visual Authority: the operator.
DATE: 2026-09-27

## 1. Work Unit header (Architecture 25 §23.4)

| Field | Value |
|---|---|
| COLOR / ROLE / MODEL | CYAN · bounded frontend materialization · Fable |
| RELATION | `GET /workspaces/{w}/sessions/{s}/position` (pinned RED producer) → CYAN Session field: `actions.BEGIN_ANALYSIS`, `session.proofMode`, `session.fixture`, `analysis` |
| CURRENT STATE (before) | CYAN typed the closed F03 position contract; unknown keys ignored; ANALYSIS always "later"; no Fixture Session could be opened; no derived field |
| RECOVERABLE PREDECESSOR STATE | CYAN `field-SF-06` (tag object `1eb3c14b498a27d6ba277cbc3d4ccd4845074728`) → `d3d9bd6722bbddabeca56f18d468a8e78bfa294b` = `origin/frontend-symbiotic`, verified with `git ls-remote`. RED `checkpoint-PFC-B5` (tag object `fd3d5600132e4dcb9203702d500daccf4c6d0439`, annotated, signed, good signature) → `7d3f74e4685b821cc948f45e413c1e0c207259d4`, tree `bc77cc8bb6414e6104aabdd5bd2fb1874f63f750`, verified remotely with `^{}` |
| RED PRODUCER | branch of origin `pfc-integration` (NOT consumed as a branch); tag `checkpoint-PFC-B5`; commit `7d3f74e4685b821cc948f45e413c1e0c207259d4`; migration head `e8c2a5f1b7d4`; status **TECHNICALLY_CLOSED, CHECKPOINTED; NOT REVIEWED_FIELD; NOT PUBLISHED_FIELD**; proof mode of everything derived: **MOCK / NON_PROOF** (MockProvider is the only provider; HD-19); Fixture Sessions **FIXTURE_NON_PROOF** (HD-24) |
| ROUTES CONSUMED (new) | `POST …/sessions/{s}/transitions/begin-analysis` `{expectedVersion}` (TRN-SESS-006; `packages/application/http_f04.py` `dispatch_begin_analysis`); `POST …/challenges/{c}/sessions` with body `{fixture: true}` only when the human chose it (`CreateSessionBody`, HD-24) |
| PROJECTION KEYS CONSUMED (new) | `position.actions.BEGIN_ANALYSIS {available, reasonCode, reason, relevant}`; `position.session.fixture`, `position.session.proofMode`; `position.analysis` (`visible`; `marker {origin, derived, kind, provider, proof, isMock, note}`; `analysis {status, reasonCode, artifact {acceptedAt, marker, …}}`; `clustering.status`; `generations.length`). NOT consumed: `artifact.content`, `clustering.clusters`, `generations[].authorization`, `REQUEST_QUESTION_ANALYSIS`, `REQUEST_QUESTION_CLUSTERING`, `BEGIN_REFLECTION` and every later action, `reflection`, `reflectionCompletion`, `investigation`, `selection`, `impactChain` |
| STATE ISOLATION | Real-stack proof in compose project `nquiry-cy01` (own volume, no host ports; `infra/cy01/`); mocked proof on the SF-01 lane (:3301, dead proxy); human review runtime `nquiry-cy01-inspect` (:13500, own volume); the SF-06 review runtime :13400 (F03 producer) untouched |
| AUTHORIZED DELTA | Tolerant superset typing of `position`; `BEGIN_ANALYSIS` as one more lawful next transition through the existing effect lifecycle; `session.proofMode` in the producer's words at the core (Fixture only) and in the proof chamber; `position.analysis` as ONE derived chamber (status, reason, proof marker, provider, note; AI-derived origin with lineage; no artifact content); the Fixture choice when opening a Session; the gate law updated from "F04 vocabulary absent" to "consumed only where the projection is consumed; no provider named; no derived text rendered" |
| NOT IN SCOPE (untouched) | artifact content, clusters, RETRY / RECOVERY requests, Reflection, Question Selection, Impact Chain, Investigation, Challenge frame fields, any RED change, any backend change, geometry, organ laws, any new page |
| BROWSER / RUNTIME PRODUCER IDENTITY USED FOR PROOF | `apps/web/test-results/cy01-real-stack/producer.json` (copied to `browser-evidence/run-1/producer.json`): the `git archive` of `7d3f74e4685b821cc948f45e413c1e0c207259d4` (tree `bc77cc8bb6414e6104aabdd5bd2fb1874f63f750`) built into image `nquiry-cy01-runner` by `scripts/run_cy01_real_stack.sh`, which refuses to start when the tag's object, commit or tree differs from the pin; runtime env `NQUIRY_AI_PROVIDER=mock`, `NQUIRY_ENVIRONMENT=TEST` |
| HUMAN REVIEW REQUIRED | yes (material CYAN change): the derived chamber, the Fixture marker, the fixture choice |
| EXPECTED END STATUS | READY_FOR_HUMAN_FRONTEND_REVIEW |

## 2. FIRST BROKEN RELATION → AUTHORITATIVE HOME

`VISIBLE EFFECT` (ANALYSIS shown as "later" with no affordance while the producer projects `BEGIN_ANALYSIS.available = true`) → `CONSUMER` (Session page STEPS / `relevantSteps`) → `RELATION` (position → lifecycle affordances) → `PRODUCER` (`inquiry_queries.py` `session_position` at the pinned commit: 18 action keys, `proofMode`, `analysis`) → `AUTHORITY` (SESSION_CONTROL_RIGHT at SESSION; server-decided) → `STATE` (TRN-SESS-006 QUESTION_CAPTURE → ANALYSIS) → **FIRST BROKEN RELATION: CANONICAL STATE → VALID RELATIONS → VISIBLE AFFORDANCES for the Session position contract** (CYAN typed a closed F03 contract and dropped the superset).

**Authoritative home:** `apps/web/lib/api/inquiryClient.ts` (`SessionPosition`, `SessionActionName`, `SESSION_COMMAND_PATHS`, `openSession`) with the Session page's STEPS and the new `apps/web/lib/field/analysis.ts`. RED side of the contract: `packages/application/inquiry_queries.py`, `analysis_projection.py`, `http_f04.py` at `7d3f74e`.

**Minimum legitimate root repair:** widen the contract tolerantly at its home (optional keys; absence = "not projected"), add the one transition path, project the two new facts in the producer's words, and lift the law that forbade the vocabulary.

## 3. Delta (files)

| File | Change |
|---|---|
| `apps/web/lib/api/inquiryClient.ts` | `AnalysisActionName`, `AnalysisMarker`, `AnalysisProjection`; `session.fixture?`/`proofMode?`; `actions` = F03 record ∧ `Partial<Record<"BEGIN_ANALYSIS", …>>`; `analysis?`; `SESSION_COMMAND_PATHS.BEGIN_ANALYSIS`; `openSession(…, {fixture?})` sends `{fixture:true}` only when chosen |
| `apps/web/lib/field/analysis.ts` (new) | `proofModeOf(session)` (not projected / mode / NON_PROOF in words), `analysisFacts(analysis)` (null when absent or invisible; status words for the producer's vocabulary, unknown verbatim; tone; reason; proof marker; provider; note; accepted at; clustering status; generation count; **no content**) |
| `apps/web/app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx` | STEP "Begin analysis" + its event "ANALYSIS BEGUN"; `relevantSteps` skips actions the producer does not project; `session-proof-mode` tag at the core (Fixture only); "Proof mode" line in the proof chamber (when projected); the derived chamber (`Plane semantic="derived"`, `testId="analysis-chamber"`, tone from the status) before the decision entry |
| `apps/web/app/workspaces/[workspaceId]/challenges/[challengeId]/page.tsx` | checkbox "Open as a Fixture Session" (+ note) inside the existing Open-a-Session chamber; the Open Session effect sends the choice |
| `apps/web/components/field/chambers.tsx` | `SemanticChamber` + `"derived"`; its glyph (dashed circle, diamond) |
| `apps/web/components/field/topology/FieldStage.tsx` | `Plane` optional `tone` → `data-tone` |
| `apps/web/app/globals.css` | appended: derived chamber tone (violet, dashed inner contour; boundary tone when unavailable), Session placement row 3 (decision entry → row 4), `.derived-note`, tag size inside the derived chamber. No other rule changed |
| `apps/web/tests/field/gates.test.ts` | law change: `consumers` (files that consume the producer's projection) vs `allow` (presentation-only); gates: BEGIN_ANALYSIS only in the Session page and `lib/field/analysis.ts`; no provider / AIOP / analysis contact named anywhere; no `artifact.content` / `clusters` in field sources |
| `apps/web/tests/field/analysis.test.ts` (new), `apps/web/tests/e2e/cy01-field.spec.ts` (new), `apps/web/tests/real-stack/cy01-analysis.real.spec.ts` (new), `apps/web/playwright.sf01.config.ts` (phone project matches `cy01-*`) | proofs |
| `infra/cy01/compose.yaml`, `infra/cy01/runner.Dockerfile`, `scripts/run_cy01_real_stack.sh` (new) | the pinned-producer lane (guarded pin, `git archive` export, `PRODUCER_IDENTITY.json`, no host ports) |
| `docs/implementation/field-reports/CY-01/*` | this record |

Untouched: RED (no file under `packages/`, `apps/api`, `apps/worker`, `migrations` in this tree; the producer is consumed only as an export of the pinned commit), geometry, orbit, core, rail, the SF-06 organ laws, every other page.

## 4. Proof surface

| Step (§23.3) | Result | Evidence |
|---|---|---|
| FALSIFIER RED | mocked lane before the delta: 7 of 9 contracts failed for the right reason (no affordance, no derived chamber, no proof mode); the 2 preservation contracts passed on the predecessor; unit file failed (module absent) | `browser-evidence/run-1/falsifier-red-mocked.log` |
| LOCAL PROOF (L1) | vitest **302 / 302** (26 files) incl. `tests/field/analysis.test.ts` (proof mode words, status words/tones, no content in the projection, route and body contract) and the updated `gates.test.ts` laws | run 2026-09-27 |
| STATIC GATES (L5) | `tsc --noEmit` clean; `eslint .` 0 errors / 0 warnings; `next build` clean, **8 routes (no new page)** | `next-build` log in scratch |
| MOCKED BROWSER PROOF (L3) | `tests/e2e/cy01-field.spec.ts` **18 / 18** (9 contracts × desktop 1280 + Pixel 7): affordance exactly when available; re-read gate (ring and state word wait for the canonical re-read, `data-reconstruction=reading` → `done`, event only after); classed boundary MISSING_AUTHORITY for NO_SESSION_CONTROL, no alert in the field; FIXTURE_NON_PROOF at core/proof chamber; MOCK / NON_PROOF marker; UNAVAILABLE with reason code, boundary tone; hidden outside the audience; F03-shaped position renders unchanged; fixture choice sends `{fixture:true}` only when chosen; no horizontal overflow, material text ≥ 11.5 px | `browser-evidence/run-1/mocked-lane.log` |
| REAL-STACK BROWSER PROOF (L7, pinned producer) | `tests/real-stack/cy01-analysis.real.spec.ts` **2 / 2** (desktop, Pixel 7) against `7d3f74e…` via `scripts/run_cy01_real_stack.sh`: UI chain to the frozen set → participant has no affordance and is DENIED by the producer on a real request → controller BEGIN_ANALYSIS committed → ANALYSIS current after the re-read → derived chamber accepted · MOCK / NON_PROOF · MockProvider note → canonical position equals the visible state → no derived word on the page → stale re-request refused → axe wcag2a/aa serious+critical **0** → participant sees the same derived field, no affordance → Fixture Session opened by the explicit choice: FIXTURE_NON_PROOF at core and proof chamber, `position.session.fixture=true`, axe 0 | `browser-evidence/run-1/lane-summary.txt`, `screenshots/desktop-*.png`, `mobile-*.png`, `producer.json` |
| INTEGRATION PROOF (whole real-stack lane on the pinned producer) | run 1: 13 / 16 (3 test-timeouts at 90 s under host load 9–11, no assertion failed); re-run of the two files alone with `--timeout=300000`: **4 / 4** (F03 protected 2.1 / 3.3 min). Every F02 / F03 / SF-01 / WU-02.12 spec is green against `checkpoint-PFC-B5` | `lane-summary.txt`, `lane-rerun-1-summary.txt`, `lane-rerun-2-summary.txt` |
| RESPONSIVE PROOF | 1280 × 860 and Pixel 7 in the mocked lane (18 / 18); Pixel 7 in the real-stack lane; reviewer views at 1600 × 1000 and Pixel 7 on the review runtime: no overflow, the organ scrolls internally, the derived chamber spans the organ width before the decision entry | `screenshots/review-*.png` |
| ACCESSIBILITY PROOF | axe wcag2a/aa (serious + critical) 0 on the Session page in ANALYSIS and on the Fixture Session (real stack, both projects); the derived field's origin is in words (`AI-derived from the frozen human question set`), structure (`data-origin="ai-derived"`) and type role; every affordance a real button; the boundary reason a classed, non-alert mark | real-stack spec |
| PRESERVATION PROOF | full mocked lane (auth, decision, session-view, workspaces, sf01–sf05, cy01; desktop + Pixel 7): **184 / 184** — SF-01..SF-06 laws unchanged (geometry, orbit, chambers, commit resonance, breadcrumb, login, decision surface, reduced motion) | `full-mocked-lane-summary.txt` |
| REGRESSION PROOF (F03 producer) | SF-01 lane (this tree's web against the published F03 backend in this tree, `scripts/run_sf01_real_stack.sh --timeout=300000`): **14 / 14** (F02 a11y + context, F03 a11y + protected field, SF-01 field + reduced motion, WU-02.12), desktop + Pixel 7 — the deployed producer still renders every surface; plus the mocked "F03-shaped position" contract | `lane-f03-producer-regression-summary.txt` |
| INVERSE PROOF / DEEP SWEEPS | §6, §7 | — |
| HUMAN REVIEW | **required and prepared**: review runtime `nquiry-cy01-inspect` at `http://127.0.0.1:13500` (pinned producer B5 + this tree; own volume; MockProvider TEST). Identities (dev provisioning, identity rows only) `owner@cy01.local.test` (Owner), `facilitator@cy01.local.test` (Maya Torres, Session controller), `ravi@cy01.local.test` and `elena@cy01.local.test` (participants); passwords issued once in the review session, not recorded. Workspace `2c8b7729-…`, Challenge `49369d62-…`: **Session A** `58ed8f33-…` governed, QUESTION_CAPTURE, 3 frozen questions — "Begin analysis" waits for the reviewer (Maya); **Session B** `77276c5e-…` FIXTURE_NON_PROOF, QUESTION_CAPTURE, 2 questions; **Session C** `b2c9af2a-…` governed, already in ANALYSIS with the accepted MOCK / NON_PROOF derived field (taken across the boundary through the API by the controller). The SF-06 runtime :13400 (F03 producer) is untouched | `screenshots/review-*.png` |
| CHECKPOINTING | none: nothing committed, tagged, pushed, merged or deployed (HD-27 grants no publication authority; commit gate) | `git status` |


## 5. PROPAGATION (affected / not affected)

| Consumer / sibling | Affected? | Why |
|---|---|---|
| Session page | affected | the delta |
| Challenge page | affected | the fixture choice only; layout and Sessions ring unchanged |
| Workspace page, Workspaces overview, login, decision surface | not affected | no position contract; sf01–sf05 lanes green |
| `Orbit`, `FieldCore`, geometry, `RelationTrace` | not affected | ANALYSIS current/passed comes from `phases` exactly as before |
| `BurstCapturePanel`, `FrozenQuestionSet` | not affected | the step list sits above them in the same chamber; the frozen set stays verbatim |
| `chambers.tsx`, `FieldStage.Plane` | affected additively | one semantic class, one optional attribute |
| Real-stack F02/F03/SF-01 specs | not affected | green against the pinned producer (see §4) |
| F03 producer (deployed nquiry.condyn.eu, review runtime :13400) | not affected | regression proof §4: the F03 shape renders unchanged |
| RED line | not affected | nothing written to `pfc-integration`; the HD-27 persistence on RED is open (below) |

## 6. INVERSE PROOF

visible "accepted · MOCK / NON_PROOF" (`analysis-chamber`) ← `analysisFacts(position.analysis)` (no inference) ← `GET …/position` re-read after commit (`useEffectField.reconstruct`) ← `position.analysis` served to the frozen-set audience (`analysis_projection.py`, HD-22) ← accepted `AIDerivedArtifact` (MOCK_NON_PROOF) of the OA-1 run ← `CMD_BEGIN_ANALYSIS` committed under SESSION_CONTROL_RIGHT @ SESSION (TRN-SESS-006) ← frozen human set (F03) ← governed chain ← verified login. No link ends in an assumption; the FIXTURE marker ← `position.session.proofMode` ← `Session.fixture` declared at creation (HD-24).

## 7. Deep sweeps

- **Semantic drift:** none — words are the producer's (`NOT_BEGUN` → "not begun" … unknown verbatim); "proof" is never said of a mock or a Fixture; the derived field is called a proposal, never a question.
- **Authority leakage:** none — every affordance is `actions.*.available`; the gate test still forbids role/viewer inference; the participant's own request is DENIED by the producer (real-stack).
- **Hidden cross-field mutation:** none — no RED file in this tree; the lane exports the producer read-only.
- **Projection inconsistency:** the F03 shape renders as before (mocked regression test; F03-producer lane).
- **Preservation regression:** sf01–sf05 mocked lanes and the F02/F03/SF-01 real-stack specs (both producers) — see §4.
- **Documentation / evidence drift:** SF-05 docs still describe the superseded Workspace geometry (known, unchanged); `tests/field/gates.test.ts` header updated; this record is the successor truth.

## 8. Open

- **HD-27 persistence on the RED line:** appending HD-27 to `docs/implementation/field-reports/PFC/HUMAN_DECISIONS.md` and resolving the HA-03 row in `HUMAN_AUTHORITY_QUEUE.md` on `pfc-integration` was refused by the execution environment (shared-resource protection of another line's worktree). The text to persist is `HUMAN_DECISIONS.md` here, verbatim; the ledger allocation is REC-031 / NQ-DEC-055 (RED writes it; its register counts are pinned by `tests/regression/test_pfc_ledger.py`).
- The derived chamber's `data-tone` uses the producer's status only; a RETRY / RECOVERY affordance (`REQUEST_QUESTION_ANALYSIS`, `case`) is projected by the producer but not consumed (out of scope).
- Reflection and everything after it: not consumed (out of scope by HD-27).

## 9. Resulting Field status

**WU-CY-01: TECHNICALLY_CLOSED · HUMAN_VISUAL_REVIEW_PASS (2026-09-28, `HUMAN_REVIEW_RESULT.md`) · CHECKPOINTED.**
Resulting CYAN Field status: **FIELD_GREEN_WITH_DISCLOSED_CEILINGS for the WU-CY-01 scope** (technical proof surface
closed and human visual acceptance given; the ceilings below stay disclosed). Not REVIEWED_FIELD (no independent
Field review), not PUBLISHED_FIELD (no publication authority; not merged to master; not deployed). Checkpoint identity:
`STATUS.md`.

Successor note (kept for reconstruction): the status before the review was READY_FOR_HUMAN_FRONTEND_REVIEW with
this text —

- (before the review) Not FIELD_GREEN. Not REVIEWED_FIELD. Not PUBLISHED_FIELD. TECHNICAL PASS ≠ HUMAN VISUAL ACCEPTANCE.
- The RED producer's status is unchanged by this consumption: `checkpoint-PFC-B5` stays TECHNICALLY_CLOSED,
  CHECKPOINTED, not REVIEWED_FIELD, not PUBLISHED_FIELD; everything derived is MOCK / NON_PROOF; Fixture Sessions are
  FIXTURE_NON_PROOF. Real Sessions reach ANALYSIS and stop there (HD-20 / HA-02), exactly as the producer says.
- (before the review) Uncommitted on `frontend-symbiotic` above `field-SF-06` (`d3d9bd6`). Recoverable predecessor:
  CYAN `field-SF-06`; RED `checkpoint-PFC-B5`; independent. After the review: committed and checkpointed (`STATUS.md`).
- Evidence: this directory; `browser-evidence/run-1/` (11 MB: screenshots, producer identity, lane summaries).
- Field reconstruction after the delta (DELTA → RE-READ → COMPARE → RECONSTRUCT): the Session field now projects the
  pinned producer's ANALYSIS boundary and nothing beyond it; the F03 producer projects as before; the organism,
  geometry and organ laws of SF-06 are preserved (184 / 184, 14 / 14); the next relation on the Session chain
  (REQUEST_QUESTION_ANALYSIS / RECOVERY, then REFLECTION) is NOT started — STOP per HD-27.
- Next legitimate step: the Human Visual Authority's review on :13500 (Sessions A, B, C above). No further CYAN
  Work Unit is started.

