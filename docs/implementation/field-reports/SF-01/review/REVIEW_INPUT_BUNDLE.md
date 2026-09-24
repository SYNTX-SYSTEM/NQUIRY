# SF-01 REVIEW INPUT BUNDLE

Generated from the canonical SF-01 field-report artifacts for human/ChatGPT Field Review.



===== docs/implementation/field-reports/SF-01/CHATGPT_REVIEW.txt =====

NQUIRY FIELD REVIEW
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION (pulled forward; does not replace F11)
HEAD: bea864b (F02 published; field-F02 = 2f33be1) + uncommitted SF-01 on branch frontend-symbiotic (worktree ~/Entwicklung/nquiry-frontend)
STATUS: FIELD_GREEN_WITH_DISCLOSED_CEILINGS (awaiting human Field Review; NOT committed)
ARCHITECTURAL AUTHORITY: docs/implementation/frontend/21_SYMBIOTIC_FRONTEND_ARCHITECTURE.md (governing, persisted with SF-01), 20 SFE §8/§12/§13/§14, published F02 projections (inquiry_queries, http_f02) and F01 routes
HUMAN DECISIONS USED: SF01-HD-1 authorize SF-01 under doc 21 (not F11); SF01-HD-2 isolated real stack (own project/DB/no shared ports), no PASS before it; SF01-HD-3 F03 contact zone excluded, no F03 contract touched or inferred, integration law on F03 publication; SF01-HD-4 doc 21 persisted with SF-01; SF01-HD-5 (Case-3) ledger reconciliation deferred to post-F03 sync (shared REC/NQ-DEC sequence), exact entries recorded in STATUS.md

MISSION: The frontend must not overtake the system. Materialize only relations whose meaning is already closed: on the pre-Session surfaces (Workspaces, Workspace, Challenge), make canonical context shape position, affordance, effect, boundary and proof, from published F02 truth only.

FIRST BROKEN RELATION (bootstrap): CANONICAL CONTEXT/STATE -> HUMAN POSITION. Pages composed position from literal breadcrumbs (and showed "Workspaces > Session" before anything was confirmed); canonical state did not shape space. Downstream: page-local outcome residue, busy-flag lifecycle, "re-read" claimed before re-read, mutation network loss read "Nothing is assumed to have changed" (falsifier 17), keyless founding said "Please try again", Session identity invented as "Session {i+1}", proof flattened into permanent width.
  Root repair: Field Frame + Relation Trace derived only from confirmed projections (Session appears only as a possible/unavailable relation before CreateSession); one effect relation per action (intent -> outcome -> consequence -> canonical re-read); section-39 boundary language, each kind distinct; proof as a D2 depth; DOM order = relational order.

WHAT CHANGED:
  New: components/field (FieldFrame/Zone/Layout, RelationTrace, EffectIntent/EffectOutcome/ReconstructionNote, ReadBoundary, ProofDepth, OriginMark/StateName); lib/field (outcomeSemantics, effectLifecycle, position, useEffectField).
  Rewritten: the Workspaces, Workspace and Challenge pages (all F01/F02 test contracts preserved). globals.css: append-only SF-01 section.
  Not changed: Session page, inquiryClient, F02 AppShell/Outcome, legacy /decision, packages/**, apps/api/**, apps/worker/**, migrations/**, dependencies, every pre-existing test, docs/architecture 00-20.
  Lanes: playwright.sf01.config.ts (isolated mocked: own server :3301, reuseExistingServer false, unmocked traffic to a dead proxy); infra/sf01 + scripts/run_sf01_real_stack.sh (isolated real stack: project nquiry-sf01, own DB volume, no host ports, network-namespace isolation because the API CORS origin is fixed to localhost:3000 outside SF-01's scope).
  Semantics decided autonomously and recorded: PENDING not rendered (F02 has no producer; displayed certainty <= reconstructable certainty); server INDETERMINATE retains the Idempotency-Key (a new key could duplicate the effect).

MIGRATIONS: none. NEW DEPENDENCIES: none (npm ci from the unchanged lockfile; runner image installs pyproject + lockfile only).

TEST COMMANDS:
  (cd apps/web && npx eslint . && npx tsc --noEmit && npx vitest run && npx next build)
  (cd apps/web && npx playwright test --config playwright.sf01.config.ts)      # isolated mocked lane; afterwards remove apps/web/AGENTS.md, CLAUDE.md and restore next-env.d.ts (next dev regenerates them)
  bash scripts/run_sf01_real_stack.sh                                          # isolated real stack (L6/L7)

RESULTS (final tree):
  ARCHITECTURE PROOF: every rendered relation traces to a doc-21 law and a published F02/F01 projection (PROOF_MATRIX T1-T23); no authority or next-state computation; no invented DTO/route/capability; F03 absent by construction (gates + diff).
  IMPLEMENTATION PROOF: eslint/tsc clean; vitest 170 (98 baseline + 72 SF-01); next build 8 routes; static gates 13; diff gate: only 3 pages + globals.css tracked-changed (0 removed CSS lines), contact zone/backend/migrations/deps/existing tests untouched; git diff --check clean.
  MOCKED (isolated, component contract only): 81 passed (39 existing F01/F02 unchanged + 21 SF-01 x desktop + Pixel 7).
  REAL STACK PROOF (isolated nquiry-sf01, no interception): L6 guard PASS, DB principals, migrations static+live PASS on an empty DB (head b3d8e5f0a2c7); L7 10/10 twice (second run on the final tree): F02 flow + F02 a11y + WU-02.12 closure + SF-01 path + SF-01 reduced motion, desktop + Pixel 7. axe serious/critical = 0 on all SF-01 surfaces; no overflow; keyboard proof depth; real browser offline -> unknown consequence -> last-confirmed view -> re-read -> repeat with the retained key -> exactly ONE Challenge. The F03 environment was untouched (containers and times verified).

RED: all new modules RED by absence; F17 predicate proven against the real F02 wording; SF-01 mocked spec against the pre-SF-01 pages (bea864b): 19 failed / 2 passed (the passes are the isolation harness and the CF-07 rule F02 already held); gate predicates proven against planted violations; proof-depth marker assertion RED (2 failed) before repair.
  Disclosed deviations: ReconstructionNote/FieldFrame tests written in the same step as the component; L7 not run against pre-SF-01 pages (non-vacuity rests on L3 RED); the marker defect was found by visual proof, and the test was strengthened afterwards and shown RED before the repair.

DEFECTS FOUND BY THE REAL-STACK RUN (WU-SF01.7):
  Application: PROOF DEPTH -> PERCEIVABLE ACTIVATION TARGET. The flex summary dropped the native disclosure marker; the proof looked like a static heading (21 section 35). Root repair: explicit, visible open/closed marker (decorative for assistive tech), summary in the action color. RED 2 -> GREEN.
  Environment: root-owned runner output in the bind mount blocked other lanes (EACCES). Repair inside infra/sf01 only: output handed back to the mount owner on exit.

RECURSIVE DEEPSWEEP: PASS (the chain is in each WU report). F01 orientation/add-member and the F02 real-stack flow are green; Session page deliberately unchanged.
INVERSE DEEPSWEEP: PASS. The possible Session relation traces to the openSession capability, to an ACTIVE CHALLENGE-scoped SESSION_CONTROL_RIGHT binding, to a real grant by the governance root, to FOUNDING (proven by unavailable -> possible after a real grant). The unknown consequence traces to a real transport rejection, reconciled by a canonical re-read, and the repeat produced a single effect.

CEILINGS / KNOWN LIMITATIONS: Session page still page-centric with the F17 wording (F03 contact zone; Stage 2 after F03); PENDING not produced by F02 (OR-I); previous-state provenance not projected (OR-C); Challenge authorship origin not projected (OR-D); phases is enum-index (OR-E); no projection freshness/push (OR-F); F01 founding/add-member keyless; L7 web server is next dev (build proven separately); next dev regenerates AGENTS.md/CLAUDE.md/next-env.d.ts (cleaned after each lane); doc 21 not yet reconciled with the 19 DAG (OR-A); ledger entries pending (SF01-HD-5); GAP-14-001 production identity open.
DOWNSTREAM: on F03 PUBLISHED_FIELD: STOP -> reconstruct F03 -> sync branch -> contract/dependency DeepSweep -> ledger reconciliation -> Stage 2 (Session page on SF-01 primitives) and the WAIT_FOR_F03 relations. F11 later consumes the grammar.

GIT: 4 tracked files modified (+721/-380), no deletes, renames or staged files; new: components/field, lib/field, tests/field, sf01 specs (mocked + real), playwright.sf01.config.ts, infra/sf01, scripts/run_sf01_real_stack.sh, doc 21, docs/implementation/field-reports/SF-01 (reports + 10 curated PNGs). apps/web/AGENTS.md and CLAUDE.md absent (must stay out). git diff --check clean. Index empty.
COMMIT: none. Awaiting human Field Review; no commit, tag or push without explicit approval.


===== docs/implementation/field-reports/SF-01/FIELD_REVIEW.md =====

# NQUIRY FIELD REVIEW REPORT

## Field
SF-01: Symbiotic Frontend Foundation (pulled forward). Semantic regime: the pre-Session Relational
Interaction Field (doc 21 §48, Stage 1 plus the Stage 3 primitives).

## Worktree State
- Worktree `~/Entwicklung/nquiry-frontend`, branch `frontend-symbiotic`, at `bea864b` (F02 published, identity recorded). SF-01 is uncommitted.
- Index empty. `git diff --check` clean. **NOT COMMITTED.**
- F03 is in progress in a separate worktree and environment (compose project `nquiry`). It was neither inspected nor touched.

## Field Purpose
Make canonical context shape the frontend before a Session exists:
- where the human is (the Relation Trace);
- what is possible, unavailable, requested, committed or unknown;
- why an action is not available;
- where the proof is.

All of it projected from published F02 truth, never invented. The frontend must not overtake the system.

## Authoritative Parent
- **Governing:** `docs/implementation/frontend/21_SYMBIOTIC_FRONTEND_ARCHITECTURE.md` (doc 21, 3880 lines; persisted with SF-01 per SF01-HD-4).
- **Execution law:** 20 (SFE), §8 (three cases), §12 (TDD), §13 (frontend-first ≠ frontend-defined), §14 (documentation, no-commit).
- **Published system truth:** F02 (`inquiry_queries`, `http_f02`, and the F01 routes).

## Human decisions
| ID | Decision |
|---|---|
| SF01-HD-1 | SF-01 authorized as the pulled-forward foundation under doc 21. It does not replace F11 and invents no F11 semantics |
| SF01-HD-2 | Real-stack proof only in an isolated environment (own project, DB, no shared ports). No Field PASS before it |
| SF01-HD-3 | F03 contact zone excluded. No F03 contract modified, inferred, duplicated or stabilized. Integration law on F03 publication |
| SF01-HD-4 | Doc 21 governs SF-01 and is persisted with SF-01, not published separately |
| SF01-HD-5 | (Case-3 raised in WU-SF01.0) Ledger reconciliation (16 §41, 20 §15) deferred to the post-F03 sync, because the REC/NQ-DEC sequence is shared with F03. The exact entries are in STATUS.md |

## Initial State (bea864b)
- Pages composed position themselves: literal breadcrumb arrays, and "Workspaces › Session" was shown while nothing was confirmed.
- One `outcome` slot and a `busy` flag per page.
- The "re-read" claim appeared before the re-read (Workspace/Challenge pages).
- Mutation network loss read "Nothing is assumed to have changed".
- Keyless founding said "Please try again".
- Session identity was the client ordinal `Session {i+1}`.
- Authority lists were permanently on the surface.
- The mocked lane reused whatever served :3000, which is currently the F03 environment.

## Final State
On Workspaces, Workspace and Challenge:
- **Frame and position:** a Field Frame with a Relation Trace derived from confirmed projections. Before a Session exists, a Session appears only as a *possible* or *unavailable* relation.
- **Effect relations:** each has its own intent, outcome, consequence and canonical re-read.
  - Commit markers claim a re-read only after it happened.
  - Transport loss is an unknown consequence, reconciled before any repeat, with the same Idempotency-Key.
  - A failed re-read marks the view last-confirmed and blocks dependent effects.
- **Boundaries:** in the §39 language, each kind distinct.
- **Proof:** a visibly openable D2 depth.
- **Layout:** DOM order equals relational order at every width.
- **Verified end to end** in an isolated real stack.

## Internal Work Units
| WU | Title | Report |
|---|---|---|
| SF01.0 | Bootstrap reconstruction, decisions, baseline | WU-SF01.0.md |
| SF01.1 | Effect & Boundary grammar | WU-SF01.1.md |
| SF01.2 | Relation Trace | WU-SF01.2.md |
| SF01.3 | Semantic primitives | WU-SF01.3.md |
| SF01.4 | Adoption + isolated mocked lane | WU-SF01.4.md |
| SF01.5 | Static gates | WU-SF01.5.md |
| SF01.6 | Isolated real-stack environment (prepared) | WU-SF01.6.md |
| SF01.7 | Isolated real-stack execution + 2 repairs | WU-SF01.7.md |

## Architecture Materialization
- Doc 21 is persisted with the branch (unchanged, sha256 prefix `42e9202127756bd9`).
- No architecture file (00–20) changed. 16/20 reconciliation is deferred (SF01-HD-5); the pending entries are in STATUS.md.
- Case decisions made autonomously and recorded:
  - PENDING is not rendered as its own phase (Case 1, from 21 §3: F02 has no producer for it).
  - Server INDETERMINATE retains the intent key (Case 1, 21 §14).
  - Namespace isolation instead of port remapping (Case 2: the API CORS origin is fixed outside SF-01's scope).

## Domain / Authority / Boundary / Effect Gate / Provenance / Persistence / API Changes
**None.**
- `packages/**`, `apps/api/**`, `apps/worker/**` and `migrations/**` are untouched (diff gate).
- No DTO, route, capability or authority is invented. Every projection consumed is published F02/F01.

## Frontend Changes
- **New, `components/field/`:** `FieldFrame` (+ `FieldZone`, `FieldLayout`), `RelationTrace`, `EffectSurface` (`EffectIntent`, `EffectOutcome`, `ReconstructionNote`), `ReadBoundary`, `ProofDepth`, `Origin` (`OriginMark`, `StateName`).
- **New, `lib/field/`:** `outcomeSemantics`, `effectLifecycle`, `position`, `useEffectField`.
- **Rewritten:** the Workspaces, Workspace and Challenge pages. Every existing F01/F02 contract is preserved (the unchanged tests prove it).
- **`globals.css`:** append-only SF-01 section (typographic roles, edge grammar, trace, zones, effect and boundary surfaces, proof-depth marker, motion).
- **Untouched:** Session page, `inquiryClient`, F02 `AppShell` / `Outcome` / `Unavailable` (reused read-only), legacy `/decision`.

## Test-First Evidence
- L0/L1: RED by absence for every new module.
- The F17 predicate is proven against the real F02 wording.
- L3: the SF-01 spec ran against the pre-SF-01 pages (`bea864b` export, own lockfile install, own port): **19 failed / 2 passed**. The two passes are the isolation harness and the CF-07 rule F02 already held.
- L5: every gate predicate is proven against a planted violation.
- WU-SF01.7: the proof-depth marker assertion was RED (2 failed) before the repair.
- **Disclosed deviations:**
  - The `ReconstructionNote` and FieldFrame tests were added in the same step as the component (no RED).
  - L7 was not run against the pre-SF-01 pages. Non-vacuity rests on L3 RED.
  - The proof-depth marker defect was found by visual proof, not by a test. The test was strengthened after the fact and shown RED before the repair.

## Tests Added
- vitest (72):
  - `outcomeSemantics` 12, `effectLifecycle` 14, `position` 12, `primitives` 21, `gates` 13.
- Mocked (isolated): `sf01-field.spec.ts`, 21 tests × desktop + mobile.
- Real stack: `sf01-field.real.spec.ts`, 2 tests × desktop + mobile.

## Negative / Adversarial Tests
- Unmocked traffic to a live backend fails closed.
- NOT_FOUND invents nothing.
- An unavailable relation renders no control.
- Double submit is blocked (synchronous guard, reducer).
- A request is refused while the re-read is running.
- Settle without a request is ignored.
- Aborted POST, a 503 INDETERMINATE and a 500 non-JSON response all lead to unknown consequence.
- An aborted re-read after commit leads to C3-06.
- Key reuse only for unknown outcomes.
- **Real browser offline mode** (no interception): unknown → last-confirmed → re-read → the repeat creates exactly one Challenge.
- Static gates against timers, role inference, F03 vocabulary, AI, client persistence and contact-zone imports.

## ARCHITECTURE PROOF
- Every rendered relation traces to a doc-21 law and a published F02/F01 projection (PROOF_MATRIX T1–T23).
- Nothing in SF-01 computes authority or next state, or invents a projection.
- F03 relations are absent by construction (gate T20, diff T21).

## IMPLEMENTATION PROOF (final tree)
| Lane | Result |
|---|---|
| eslint / tsc | clean / clean |
| vitest | **170 passed** (98 baseline + 72) |
| `next build` | compiled, 8 routes (= F02) |
| Static gates | 13 passed |
| Diff gate vs `bea864b` | only 3 pages + `globals.css` tracked-changed; `globals.css` 0 removed lines; contact zone, backend, migrations, deps, existing tests untouched |
| Isolated mocked lane | **81 passed** (39 existing F01/F02 + 21 SF-01 × 2) |

## REAL STACK PROOF
- **L6:**
  - Isolated compose project `nquiry-sf01`: own Postgres volume, **no host ports**. This tree's API, `next dev` and Chromium run in one private network namespace.
  - Guard passed. DB principals applied; migrations static + live PASS on an empty DB (22 revisions, head `b3d8e5f0a2c7`).
- **L7:** `scripts/run_sf01_real_stack.sh` → **10/10 passed**, run twice. The second run is on the final tree.
  - F02 flow, F02 a11y and WU-02.12 closure: desktop + Pixel 7.
  - SF-01 path + SF-01 reduced motion: desktop + Pixel 7.
- **Accessibility:** axe WCAG 2 A/AA serious/critical = 0 on every SF-01 surface, desktop and mobile. Keyboard-only proof depth.
- **Responsive:** no horizontal overflow at 1280×860 or on Pixel 7. Relational order.
- **Visual:** `visual/`, 10 curated real-stack screenshots from the final run.
- **Isolation evidence:** F03 containers untouched. The F03 worker had already exited at 17:50:17Z (no-op skeleton), long before run 1 began at 19:09:25Z.

## Recursive Upward Test Ladder
L0 pure → L1 markup → L2 producer/consumer (F02 fixture shapes, envelope → boundary) → L3 isolated component contract → L4 F01/F02 regression (39 mocked, 6 real) → L5 static/build/diff → L6 isolated environment → L7 real browser → L8 full regression (all of the above on the final tree).

## Recursive DeepSweep Result
PASS.
- Chain: changed relation (position, effect, boundary, proof on pre-Session surfaces) → PF-01 → CF-01/02/07/08/09 → governance and authority unchanged (server capabilities only) → persistence and API unchanged → frontend → tests → reconstructed Field.
- Siblings: F01 orientation and add-member contracts, and the F02 real-stack flow, are all green.
- The Session page is deliberately unchanged (contact zone).

## Inverse DeepSweep Result
PASS.
- **Possible Session relation:** visible `session / possible` ← `capabilities.openSession.available` ← `_holds(SESSION_CONTROL_RIGHT, CHALLENGE:<id>)` ← ACTIVE binding ← committed grant by the governance root ← FOUNDING. Proven in L7 by the unavailable → possible transition after a real grant.
- **Unknown consequence:** visible `data-consequence="unknown"` ← `describeOutcome(network_failure, mutation)` ← a real transport rejection (offline) ← no response. Reconciled by a canonical re-read. Proven single-effect by a repeat under the retained key.

## First Broken Relation Result
- Root, from the WU-SF01.0 bootstrap: `CANONICAL CONTEXT/STATE → HUMAN POSITION`. The page composed position, and canonical state did not shape space. **Repaired on all pre-Session surfaces.**
- Found in WU-SF01.7:
  - `PROOF DEPTH → PERCEIVABLE ACTIVATION TARGET` (application; repaired);
  - `runner output → host ownership` (environment; repaired in `infra/sf01` only).
- **Known and unrepaired by law:** the same root break on the Session page (F03 contact zone), which is Stage 2 after F03.

## Fixture Ceilings
- Real-stack identities are dev-provisioned (HD-3) and carry no authority. Every relation is established through the product UI.
- The mocked lane is component contract only.

## Mock Ceilings
- The isolated mocked lane is not runtime proof.
- There are no backend mocks. The real-stack lane forbids interception (global setup).

## External Dependency Ceilings
- GAP-14-001 (production identity provider): open, unchanged.
- The L7 web server is `next dev` (same as F02's lane). The production build is proven separately.

## Known Limitations
1. The Session page keeps F02's page-centric model, including the F17 wording and index-based mobile phase hiding. It is re-homed only after F03.
2. PENDING has no F02 producer, so it is not shown (OR-I).
3. Previous-state provenance is not projected (OR-C).
4. Challenge authorship origin is not projected (OR-D); the Challenge framing is not marked HUMAN.
5. `phases` is an enum-index projection, not transition history (OR-E).
6. There is no projection freshness or push channel, so stale controls are caught only by the server (OR-F).
7. F01 `POST /workspaces` and add-member are keyless (F01 limitation), so a repeat after an unknown outcome is a new intent. The UI reconciles first and never invites a blind retry.
8. Every host `next dev` run regenerates `apps/web/AGENTS.md` / `CLAUDE.md` / `next-env.d.ts`; they are cleaned after each lane.
9. Doc 21 is not yet reconciled with the 19 F00–F12 DAG (OR-A), and ledger entries are pending (SF01-HD-5).

## Architecture Drift
None. Doc 21 is unchanged, and no 00–20 file is touched.

## Downstream
- **After F03 is PUBLISHED (integration law):** STOP → reconstruct F03 → sync this branch with the published commit → contract and dependency DeepSweep → reconcile ledgers (SF01-HD-5) → then Stage 2 (Session page on SF-01 primitives) and the WAIT_FOR_F03 relations.
- **F11:** consumes the grammar later (21 F11-R06).

## Git Diff Summary
- **Tracked, modified (4):**
  - `apps/web/app/globals.css`
  - `apps/web/app/workspaces/page.tsx`
  - `apps/web/app/workspaces/[workspaceId]/page.tsx`
  - `apps/web/app/workspaces/[workspaceId]/challenges/[challengeId]/page.tsx`

  (+721 / −380). No deletes, renames or staged files.
- **Untracked (new):**
  - `apps/web/components/field/` (6)
  - `apps/web/lib/field/` (4)
  - `apps/web/tests/field/` (5)
  - `apps/web/tests/e2e/sf01-field.spec.ts`
  - `apps/web/tests/real-stack/sf01-field.real.spec.ts`
  - `apps/web/playwright.sf01.config.ts`
  - `infra/sf01/` (4)
  - `scripts/run_sf01_real_stack.sh`
  - `docs/implementation/frontend/21_SYMBIOTIC_FRONTEND_ARCHITECTURE.md`
  - `docs/implementation/field-reports/SF-01/`: STATUS, WU-SF01.0–.7, FIELD_REVIEW, CHATGPT_REVIEW, PROOF_MATRIX, and `visual/` (10 PNGs)
- **Not part of SF-01 (must stay out):** `apps/web/AGENTS.md`, `apps/web/CLAUDE.md` (absent), `test-results/` (gitignored).
- **Secrets:** only the synthetic local-dev DB password already in committed history (`docker-compose.yml`, runbook) appears, in `infra/sf01`.

## Git Diff Check
Clean.

## Commit Status
**NOT COMMITTED.** Awaiting human Field Review. No commit, tag or push without explicit approval.

## Recommended Status
**FIELD_GREEN_WITH_DISCLOSED_CEILINGS.** The ceilings are Known Limitations 1–9 plus GAP-14-001. All are disclosed, and none hides an SF-01 relation.


===== docs/implementation/field-reports/SF-01/PROOF_MATRIX.md =====

# SF-01 PROOF MATRIX

Every SF-01 claim → governing law (doc 21, falsifier F-n from §42) → the lanes that prove it → RED evidence.

Lanes:
- **L0**: pure vitest.
- **L1**: static markup, no CSS.
- **L3**: isolated MOCKED browser, component contract only (`playwright.sf01.config.ts`, :3301, dead-proxy fail-closed; desktop + Pixel 7).
- **L5**: static gates / build / diff.
- **L7**: isolated REAL stack (`scripts/run_sf01_real_stack.sh`, project `nquiry-sf01`; desktop + Pixel 7).

RED key:
- **A**: module absent before implementation.
- **B**: failed against the pre-SF-01 pages (`bea864b`, L3, 19/21 failed).
- **P**: predicate proven against a planted violation.
- **R**: failed before the WU-SF01.7 repair.
- **—**: none demonstrated (disclosed).

| # | Claim | Law | L0/L1 | L3 | L5 | L7 | RED |
|---|---|---|---|---|---|---|---|
| T1 | Position is a Relation Trace built only from confirmed server projections; loading and NOT_FOUND keep only the confirmed access context | 21 §12, §14, CF-01 | `position.test` (12), `primitives` RelationTrace | trace from projection; unconfirmed → access only; NOT_FOUND invents nothing | — | exact trace data; **reload rebuilds an identical trace** | A, B |
| T2 | No Session coordinate exists before `CreateSession` commits | 21 §12, CF-02 | `position.test` | Challenge / Workspace traces | — | `session-state` absent on the Challenge page | A, B |
| T3 | The Session / Challenge relation is `possible` only when the server projects it, else `unavailable` with the server reason | 21 §12, §13, CF-07 | `position.test` | Workspace possible; Challenge unavailable | — | Owner: Challenge unavailable; Facilitator: possible; Session **unavailable → possible only after a real grant** | A, B |
| T4 | A future relation is never a navigable destination | F32 | `position.test`, `primitives` (2 hrefs only) | future segments have no link | — | (covered by the T1 data) | A, B |
| T5 | Session identity is server-projected (state + opening time), not a client ordinal | CF-02 | — | "Session opened …" + SYSTEM STATE; no "Session 1" | — | same, on a real Session | B |
| T6 | REQUESTED ≠ COMMITTED: no outcome and unchanged canonical state until the server answers | 21 §17, F7, F8 | reducer; `EffectIntent` | held request: intent shown, list unchanged, control disabled | — | — | A, B |
| T7 | "Re-read" is claimed only after the canonical re-read happened | 21 §22, F27 | `primitives` | held re-read: `reading` without the claim → `done` with it | — | commit markers after add-member and grant | A, B |
| T8 | C3-06: a committed but unreadable effect stays committed, the view is marked last-confirmed, dependent effects are blocked, and a manual re-read restores it | 21 §22, C3-06 | reducer; `primitives` | re-read aborted after commit | — | same machinery on the real offline path (network outcome, see T9) | A, B |
| T9 | C3-01: transport loss on a mutation → UNKNOWN consequence (never "nothing changed"), reconciled by re-read; repeating the intent reuses its Idempotency-Key | 21 §14, §39, C3-01, F17 | `outcomeSemantics` (F17 predicate catches the F02 text) | aborted POST → unknown, re-read, same key on repeat | — | **real browser offline** → unknown + last-confirmed → re-read → repeat → **exactly ONE Challenge** | A, B, P |
| T10 | Server INDETERMINATE retains the intent; a definitive outcome releases it | 21 §14, F18 | reducer | indeterminate → same key; denied → new key | — | — | A, B |
| T11 | A response outside the known vocabulary is INDETERMINATE, never a failure | 21 §14 | `useEffectField` (thrown `send`) | 500 text body → indeterminate / unknown | — | — | B |
| T12 | Keyless F01 founding: lost response → unknown, list re-read, never "try again" | C3-01 | — | aborted `POST /workspaces` | — | — | B |
| T13 | Boundary taxonomy: every kind has its own title, consequence and role | 21 §14, §39, F21, F22 | `outcomeSemantics`, `primitives` (9 distinct texts) | denied / rejected / failed_precommit / indeterminate each distinct | — | real `rejected` (malformed id) | A, B |
| T14 | Affordance only from server capability; unavailable → server reason and no control; no role inference | 21 §13, CF-07, F14 | — | unavailable Open Session | gate: no role / viewer-flag comparisons | F02 specs + SF-01 unavailable reason | P (gate); L3 passed on baseline (held since F02) |
| T15 | Proof is depth: D2 closed by default, keyboard-openable in place, focus kept, **visibly openable** | 21 §15, §35, §40, F23, F26 | `primitives` ProofDepth | keyboard open, focus kept, URL / position kept, marker ▸/▾ | — | keyboard open on the real Challenge page; visual check | A, B, **R** |
| T16 | Origin grammar: each class named in words; AI-derived impossible without lineage; Human ≠ AI markup | 21 §16, F11, F24 | `primitives` | SYSTEM STATE on Session items | — | SYSTEM STATE on a real Session | A (grammar only; applied only to SYSTEM STATE) |
| T17 | Relational order: position → active relation → affordance → proof; no horizontal overflow | 21 §30, §34, F28 | `primitives` FieldFrame DOM order | bounding-box order on Pixel 7; overflow ≤ 1 | — | overflow ≤ 1 on every SF-01 surface, desktop + mobile | A, B |
| T18 | Reduced motion removes animation, not meaning | 21 §33, F25 | — | `animation-name: none`, text and role kept | — | same on real outcomes | B |
| T19 | Accessibility: axe WCAG 2 A/AA serious/critical = 0 | 21 §35 | — | — | — | 0 on access, Workspace (owner + member), Challenge, proof open; desktop + mobile | — (F02's negative control proves the axe injection detects violations) |
| T20 | Impossible in SF-01 code: timers, role inference, F03 vocabulary, AI invocation, client persistence, contact-zone imports | SF01-HD-3, 21 §43 | — | — | `gates.test` (13), each predicate P-proven | — | P |
| T21 | F03 contact zone, backend, migrations, deps and existing tests untouched; CSS append-only | SF01-HD-3 | — | — | diff gate vs `bea864b`; `globals.css` 0 removed lines | — | — |
| T22 | No F01/F02 regression | 20 §12 | vitest 98 baseline | 39 existing mocked specs | build 8 routes | F02 flow, a11y, WU-02.12 closure (6/6) | — |
| T23 | Isolation from the running F03 environment | SF01-HD-2 | — | unmocked call to live `:8000` fails closed | — | guard: project `nquiry-sf01`, no host ports; F03 containers untouched | — |

## Not claimed (out of SF-01 scope)
- Session page semantics (F03 contact zone). It still shows the F02 wording "Nothing is assumed to have changed" (F17 residual) until Stage 2 after F03.
- Human Source, freeze, capture, completion: WAIT_FOR_F03.
- AI derivation, results, evidence: WAIT_FOR_F04 or later.
- PENDING as a separate phase: no F02 producer (OR-I).
- Previous-state provenance (OR-C). Challenge authorship origin (OR-D).

## Totals (final tree)
- vitest **170** passed.
- Isolated mocked lane **81** passed (39 existing + 21 SF-01 × 2).
- Isolated real stack **10** passed (6 F02 regression + 4 SF-01).
- eslint and tsc clean; `next build` 8 routes; `git diff --check` clean.


===== docs/implementation/field-reports/SF-01/STATUS.md =====

# FIELD STATUS

## Field
SF-01 — SYMBIOTIC FRONTEND FOUNDATION (pulled forward)

## Governing architecture
`docs/implementation/frontend/21_SYMBIOTIC_FRONTEND_ARCHITECTURE.md` (doc 21).
Persisted with SF-01 on branch `frontend-symbiotic` (human decision SF01-HD-4). SFE execution law: 20.

## Semantic regime
The pre-Session Relational Interaction Field (21 §48 Stage 1 + Stage 3 primitives):
PF-01 Field Frame, CF-01 Position, CF-02 Context Establishment, and the CF-07 / CF-08 / CF-09
grammar (affordance, effect and boundary, proof depth). SF-01 does not replace F11 and invents no
F11 semantics (21 §44 F11-R01..R04).

## Status
**FIELD_GREEN_WITH_DISCLOSED_CEILINGS — AWAITING HUMAN FIELD REVIEW.** Not committed. No commit, tag
or push without explicit approval. The isolated real-stack proof exists (SF01-HD-2 satisfied).

| Lane | Result (final tree) |
|---|---|
| L0/L1/L2 vitest | 170 passed (98 baseline + 72 SF-01) |
| L3/L4 isolated mocked browser (`playwright.sf01.config.ts`, own server :3301, dead-proxy fail-closed) | 81 passed (39 existing F01/F02 unchanged + 21 SF-01 × desktop + Pixel 7) |
| L3 RED against the pre-SF-01 pages (bea864b export) | 19 failed / 2 passed (isolation harness; CF-07 rule already held by F02) |
| L5 eslint / tsc / `next build` / static gates / diff gate | clean / clean / 8 routes / 13 passed / contact zone, backend, migrations, deps, existing tests untouched |
| L6 isolated environment (`nquiry-sf01`, no host ports) | guard PASS; DB principals; migrations static + live PASS on an empty DB (head b3d8e5f0a2c7) |
| L7 isolated real stack (`scripts/run_sf01_real_stack.sh`) | **10/10 passed**, run twice; the second run is on the final tree (F02 flow + a11y + WU-02.12 closure + SF-01 × desktop + Pixel 7) |

Review artefacts: FIELD_REVIEW.md, CHATGPT_REVIEW.txt, PROOF_MATRIX.md, visual/ (10 real-stack PNGs).

## Work Units
| WU | Title | Report |
|---|---|---|
| SF01.0 | Bootstrap reconstruction, human decisions, environment baseline | WU-SF01.0.md |
| SF01.1 | Effect & Boundary grammar (pure) | WU-SF01.1.md |
| SF01.2 | Position: Relation Trace (pure) | WU-SF01.2.md |
| SF01.3 | Semantic primitives | WU-SF01.3.md |
| SF01.4 | Adoption on pre-Session surfaces + isolated mocked lane | WU-SF01.4.md |
| SF01.5 | Static architecture gates | WU-SF01.5.md |
| SF01.6 | Isolated real-stack environment + L7 spec (prepared) | WU-SF01.6.md |
| SF01.7 | Isolated real-stack execution; application repair (proof-depth marker) + environment repair (output ownership) | WU-SF01.7.md |

## Human decisions (2026-09-24)
- **SF01-HD-1**: SF-01 is authorized as the pulled-forward Symbiotic Frontend Foundation governed by doc 21. It does not replace F11.
- **SF01-HD-2**: L6/L7 only in an isolated frontend real-stack environment (own compose project identity, ports, database). Do not interfere with the running F03 environment. L0–L5 proceed. No Field PASS before the isolated proof.
- **SF01-HD-3**: F03 contact zone EXCLUDED. No F03 contract may be modified, inferred, duplicated or locally stabilized (capture, QuestionBurst, PARTICIPATION, manual completion, F03 capability mapping, re-read, DTOs, real-stack acceptance). All of it stays WAIT_FOR_F03.
- **SF01-HD-4**: Doc 21 governs SF-01 and belongs to the SF-01 branch. It is persisted with SF-01, not published separately first.
- **SF01-HD-5** (Case-3, answered 2026-09-24): ledger reconciliation (16 §41, 20 §15) is DEFERRED to the post-F03 synchronization step, because the REC-/NQ-DEC- sequence is shared with the in-progress F03. The decisions are recorded here with the exact text to reconcile (below). 16 and 20 stay untouched on this branch. This is a documented deviation from the "same Work Unit" clause of 20 §14.
- **Integration law**: when F03 becomes PUBLISHED_FIELD, STOP before F03 integration → reconstruct F03 → synchronize this branch with the published F03 commit → contract and dependency DeepSweep → only then may WAIT_FOR_F03 relations become candidates.

## Pending ledger reconciliation (execute at post-F03 sync, SF01-HD-5)
Allocate the next free numbers after F03's own entries, then add to 16 §41 (+ §6 table, YAML, counts) and 20 §15:
1. REC-?? / NQ-DEC-??: SF-01 authorized as pulled-forward Symbiotic Frontend Foundation under doc 21; F11 unchanged (SF01-HD-1).
2. REC-?? / NQ-DEC-??: Real-stack proof for frontend-only Fields runs in an isolated environment (own project, DB, no shared ports) (SF01-HD-2).
3. REC-?? / NQ-DEC-??: Frontend Fields may not modify, infer, duplicate or stabilize an unpublished Field's contracts; contact-zone exclusion (SF01-HD-3).
4. REC-??: Doc 21 status as governing frontend architecture, persisted with SF-01 (SF01-HD-4); reconcile PF-01/CF-01..09 with the 19 F00–F12 DAG (open relation OR-A).
5. REC-??: The ledger deferral itself (SF01-HD-5).

## Upstream dependencies
F02 (published `2f33be1`, identity record `bea864b`). F03 in progress (external; not inspected).

## Downstream
Stage 2 (CF-03 Session page adoption) and every WAIT_FOR_F03 relation: only after F03 is published and the integration law has run.


===== docs/implementation/field-reports/SF-01/WU-SF01.0.md =====

# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.0 — Bootstrap reconstruction, human decisions, environment baseline

## Mission
Before any code: reconstruct the current frontend against doc 21 (PF-01, CF-01..09) and the published F02 truth.
Classify every relation as SAFE_TO_IMPLEMENT_NOW / WAIT_FOR_F03 / WAIT_FOR_F04_OR_LATER, and find the
first broken frontend relation. Read-only. F03 WIP was not inspected.

## Parent / current Field
Parent: PF-01 (doc 21 §7). Current: pre-Session regime on published F02 (`bea864b`).

## Reconstruction result
- The frontend has two strata: the F01/F02 governed path (`inquiryClient` envelope, server capabilities, `expectedVersion` + Idempotency-Key, canonical re-read) and the PKG-28/29 legacy `/decision` surface.
- Verified absent: client authority inference, client next-state computation, optimistic canonical mutation, timers, and AI on the governed path.
- **First Broken Relation:** `CANONICAL CONTEXT/STATE → HUMAN POSITION`. The route/page, not the canonical relation, composes the field.
  - Position was page navigation: literal crumb arrays (`AppShell`), and a crumb like "Workspaces › Session" was shown while nothing was confirmed.
  - The Session state was a value inside a layout that did not change with state.
- Downstream symptoms of that break:
  - proof flattened into width;
  - a single page-level `outcome` slot, so residue survived later intents;
  - the effect lifecycle collapsed to a `busy` flag;
  - "re-read" was claimed before the re-read happened (Workspace/Challenge pages);
  - mutation network loss read "Nothing is assumed to have changed" (falsifier 17);
  - the keyless F01 founding invited "Please try again";
  - Session identity was invented as `Session {i+1}`;
  - on mobile, phases were hidden by index.

## Classification
- **SAFE_TO_IMPLEMENT_NOW:** Field Frame; Relation Trace (pre-Session; the Session primitive is built but not adopted); effect lifecycle; unknown consequence on mutation network loss (C3-01); commit marker and reconstruction honesty (C3-06); boundary taxonomy (21 §39); affordance grammar; proof depth D2/D3; origin grammar (applied only to SYSTEM STATE); typography, motion and responsive order.
- **WAIT_FOR_F03:** capture, the QuestionBurst projection beyond F02, the participant/PARTICIPATION projection, manual completion, the frozen source, the CLOSED-capture kind, F03 re-read and outcome mapping, lanes G/H, Stage 2 adoption on the Session page, and everything in the contact zone.
- **WAIT_FOR_F04_OR_LATER:** AI derivation, results, provider ceilings, AI provenance, evidence, the legacy `/decision` re-homing (F07), and F11 closure.

## Human decisions used
SF01-HD-1..4 (given after this reconstruction), and SF01-HD-5 (Case-3 raised in this WU: ledger numbering is shared with F03, so reconciliation is deferred). See STATUS.md.

## Environment baseline (L-1)
- `npm ci`: 395 packages; `package-lock.json` sha256 identical before and after (`eb6e3ac3…`).
- Baseline gates at `bea864b`: eslint clean, tsc clean, vitest **98 passed** (equal to F02's record).
- Running F03 environment observed read-only: compose project `nquiry` on :3000 / :8000 / :15432.
- The existing mocked lane (`playwright.config.ts`, `reuseExistingServer` on :3000) would therefore test the F03 web build, so SF-01 uses its own isolated lane (WU-SF01.4).

## Limitations / ceilings
Doc 21 §4 lists "manual completion" and "immutable original text" as existing fits. They are decided (HD-9, NQ-DEC-017/002) but not materialized in the F02 runtime or UI. Not treated as present.

## Git state
Read-only WU. No change.

## Result
PASS (reconstruction). The Case-3 ledger boundary was closed by SF01-HD-5.


===== docs/implementation/field-reports/SF-01/WU-SF01.1.md =====

# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.1 — Effect & Boundary grammar (pure)

## Mission
Give every settled outcome its own consequence semantics, and model the effect lifecycle as a pure
relation reducer (21 §14, §17, §22, §39; CF-08; C3-01; C3-06).

## Relation materialized
`REQUEST → OUTCOME(kind) → CONSEQUENCE (committed | none | unknown) → RECONSTRUCTION (reading | done | failed)`

## Files changed
- NEW `apps/web/lib/field/outcomeSemantics.ts`
  - `SETTLED_KINDS` is closed to the published F02 envelope plus `network_failure`; an unknown kind throws.
  - `describeOutcome(kind, path)` gives the §39 title, consequence, `announce` (status/alert), `retainIntent` and `reconcileFirst`.
- NEW `apps/web/lib/field/effectLifecycle.ts`
  - `effectReducer`: possible → requested → settled → reconstruction.
  - `intentKeyFor` retains the Idempotency-Key per relation while the consequence is unknown.
  - `blocksConsequence` blocks while a request is requested, reading or failed.
- NEW `apps/web/tests/field/outcomeSemantics.test.ts` (12), `apps/web/tests/field/effectLifecycle.test.ts` (14).

## Test-first intent
- **TRUE:**
  - one distinct title per kind;
  - commit is the only committed consequence;
  - network loss or INDETERMINATE on a mutation is `unknown`, retains the intent and reconciles first;
  - a read has no consequence;
  - a new request replaces the previous outcome;
  - a committed outcome whose re-read failed keeps blocking dependent effects (C3-06).
- **IMPOSSIBLE:**
  - F17 "network failure ⇒ nothing happened";
  - F18 INDETERMINATE read as failure;
  - F21/F22 collapse;
  - settle without request;
  - a second request in flight;
  - a request while the re-read is running;
  - an unknown kind.

## RED → GREEN
- RED: both suites failed at import (module absent, the RED-by-absence class disclosed in F02).
- Non-vacuity: the F17 predicate, run against the F02 text "The server could not be reached. Nothing is assumed to have changed.", returns `true`. It catches the real pre-SF-01 wording.
- GREEN: 26 passed.

## Implementation notes
- **PENDING (21 §17) is deliberately not a phase.** The F02 transport is one synchronous request/response and projects no "accepted, not committed" signal, so showing PENDING would display certainty the system does not provide (DISPLAYED CERTAINTY ≤ RECONSTRUCTABLE CERTAINTY). Case 1, derived from 21 §3; recorded as open relation OR-I.
- **Server INDETERMINATE now also retains the intent key** (F02 pages rotated it). A new key after an unproven commit could duplicate the effect; 21 §14 says "prevent blind duplicate consequence".

## DeepSweep
- Reconstruction chain: changed relation (effect semantics) → parent CF-08 → siblings CF-07 (blocking) and CF-09 (reconstruction) → governance/authority unchanged (no authority computed) → persistence/API unchanged → frontend (consumed in WU-SF01.3/4) → tests.
- Inverse: a visible `data-consequence="unknown"` ← `describeOutcome(network_failure | indeterminate, mutation)` ← a transport rejection or the server's 503 envelope.

## Git state
Uncommitted, nothing staged.

## Result
PASS.


===== docs/implementation/field-reports/SF-01/WU-SF01.2.md =====

# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.2 — Position: Relation Trace (pure)

## Mission
Repair the First Broken Relation at its root. Position is derived from the confirmed canonical
projection as a Relation Trace, not assembled as page navigation (21 §12, CF-01, CF-02, §14 NOT_FOUND,
falsifier 32).

## Relation materialized
`established parent → established child → current relation → lawful possible relation`, built only
from confirmed coordinates.

## Files changed
- NEW `apps/web/lib/field/position.ts`: `accessTrace`, `workspaceNameTrace`, `workspaceTrace(overview)`, `challengeTrace(detail)`, and `sessionTrace(position)`.
  - `sessionTrace` is a primitive only. It is NOT adopted, because the Session page is in the F03 contact zone.
  - Inputs are the published F02 types (`WorkspaceOverview`, `ChallengeDetail`, `SessionPosition`, `Capability`), imported read-only.
- NEW `apps/web/tests/field/position.test.ts` (12). Fixtures mirror `inquiry_queries` field for field.

## Test-first intent
- **TRUE:**
  - access context alone before confirmation;
  - Workspace → possible or unavailable Challenge relation, from `createChallenge`;
  - Challenge → possible or unavailable Session relation, from `openSession`, with the server reason code;
  - the Session primitive carries its establishing Command, or `null` when none is recorded.
- **IMPOSSIBLE:**
  - a Session coordinate in any pre-Session trace;
  - a future relation carrying an `href`;
  - more than one current coordinate;
  - a linked current coordinate;
  - an invented Challenge title.

## RED → GREEN
- RED: module absent.
- GREEN: 12 passed. Fixture typing was corrected once (inference of a default parameter was too narrow); the test logic was unchanged.

## Ceilings
- The previous state is not projected by F02 (`establishedBy` has no state-before), so the trace cannot show it. Open relation OR-C.
- `phases` (enum-index linear) is intentionally not used as trace history (OR-E).

## DeepSweep
- Chain: CF-01 → PF-01 → CF-02 (pre-Session truth) → authority unchanged (capabilities only select possible vs unavailable; nothing is computed) → API unchanged → pages (WU-SF01.4).
- Inverse: a trace segment ← `workspace` / `challenge` / `capabilities` of a confirmed F02 read ← canonical rows.

## Git state
Uncommitted.

## Result
PASS.


===== docs/implementation/field-reports/SF-01/WU-SF01.3.md =====

# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.3 — Semantic primitives

## Mission
Compile the doc-21 §36 semantic roles that SF-01 needs into primitives whose distinctions survive with
no CSS (21 §31, §35).

## Files changed (all NEW)
- `apps/web/components/field/RelationTrace.tsx`: `nav[aria-label="Inquiry position"] > ol`.
  - Current coordinate: `aria-current="location"`, never a link.
  - Established parents are links. Future relations are text with their status in words.
  - The status word sits outside the link, so a link's accessible name is exactly its context name.
- `apps/web/components/field/FieldFrame.tsx`:
  - `FieldFrame`: skip link, brand, trace and exit (slot, default Logout) outside `<main data-field-regime>`.
  - `FieldZone`: `data-field-zone` centre / near / outer / depth.
  - `FieldLayout`: DOM order = relational order = mobile order. Secondary column optional.
- `apps/web/components/field/EffectSurface.tsx`:
  - `EffectIntent`: REQUESTED, not committed, `role=status`.
  - `EffectOutcome` (Commit Marker + Boundary Surface): `data-outcome`, `data-consequence`, `data-reconstruction`, §39 title, reason code, consequence line, reconstruction line, and "Re-read current state" after a failed re-read. Legacy hooks `reasonTestId` / `committedTestId`.
  - `ReconstructionNote`: marks the view as last confirmed.
- `apps/web/components/field/ReadBoundary.tsx`: read-path boundary. No effect claim; only confirmed context is kept.
- `apps/web/components/field/ProofDepth.tsx`: native `<details>`, D2 verify / D3 reconstruct. Closed by default, no trap, opens in place.
- `apps/web/components/field/Origin.tsx`:
  - `OriginMark` covers the four origin classes, each with an accessible origin name. AI-derived throws without `lineage`.
  - `StateName` renders SYSTEM STATE.
- `apps/web/tests/field/primitives.test.tsx` (21, static markup, no CSS).
- CSS: see WU-SF01.4 (append-only).

## Test-first intent
- **TRUE:** every settled kind is distinct in text and attributes; the commit marker claims a re-read only when it is done; C3-06 wording; ReadBoundary claims no effect; proof is closed by default; origin is carried in words; the Frame adds no `h1` and keeps position before `<main>`.
- **IMPOSSIBLE:** a breadcrumb; a linked future; an outcome rendered for another relation; "nothing changed" on network loss; AI-derived without lineage; human-source and AI-derived sharing markup.

## RED → GREEN
- RED: modules absent. GREEN: 21 passed.
- **Disclosed deviation:** `ReconstructionNote` and its test (plus the FieldFrame tests) were added in the same step, so no RED was demonstrated for those four tests.
- `next/link` renders in static markup without the router; `LogoutButton` needs the App Router, hence the `exit` slot.

## Scope boundary
The origin grammar is applied only to SYSTEM STATE. Human Source content is F03; AI-derived is F04; evidence is F05/F06. The Challenge framing is not marked HUMAN, because authorship is not projected (OR-D); marking it would display certainty that cannot be reconstructed.

## Git state
Uncommitted.

## Result
PASS.


===== docs/implementation/field-reports/SF-01/WU-SF01.4.md =====

# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.4 — Adoption on the pre-Session surfaces + isolated mocked lane (L3/L4)

## Mission
Make canonical context shape the pre-Session field. Workspaces, Workspace and Challenge are composed
by Field Frame + Relation Trace + zones + effect relations. Page literals no longer compose them.

## Files changed
- NEW `apps/web/lib/field/useEffectField.ts`: runs one effect relation.
  - Flow: request → send → settle → navigate to the new context OR canonical re-read.
  - Keyed and keyless relations are separate at type level. A synchronous `inFlight` guard blocks double submit. A thrown `send` is INDETERMINATE.
  - `settleCommand` maps the F02 envelope.
- REWRITE `apps/web/app/workspaces/page.tsx`: access regime.
  - Keyless F01 founding: transport loss vs unrecognized response is told apart by a tracking `fetchImpl` passed to the unchanged F01 client, giving `network_failure` vs `indeterminate`.
  - The list is re-read after any outcome. No "try again". The previously unhandled list-read rejection now renders a read boundary.
- REWRITE `apps/web/app/workspaces/[workspaceId]/page.tsx`: Workspace regime.
  - Trace from overview, else the orientation name, else access context.
  - Centre: Challenges. Near: frame a Challenge (keyed) and add a member (F01, keyless).
  - Outer: your standing and the members. Depth D2: held authority classes.
  - A failed re-read keeps the last confirmed projection, marked.
- REWRITE `apps/web/app/workspaces/[workspaceId]/challenges/[challengeId]/page.tsx`: Challenge regime.
  - Trace with the Session relation possible or unavailable.
  - Sessions named by server projection ("Session opened <time>" + SYSTEM STATE), no `Session {i+1}`.
  - Open Session and the grant are keyed effect relations. Controllers moved to proof depth D2.
  - NOT_FOUND keeps only the access context.
- MOD `apps/web/app/globals.css`: **append-only** (1 hunk at EOF, 0 removed lines).
  - Adds typographic roles, edge grammar, trace, field layout, effect, boundary and reconstruction surfaces, proof depth, `.visually-hidden`, `relation-settle` motion (disabled under reduced motion by the existing F02 rule).
  - One rule, drafted then removed before any test, dimmed last-confirmed content with opacity (a contrast/axe risk; the meaning is in words).
- NEW `apps/web/playwright.sf01.config.ts`: isolated mocked lane.
  - Own `next dev` on :3301 with `reuseExistingServer: false`.
  - Unmocked requests go to a dead proxy (Playwright's Chromium proxies loopback, so `localhost:8000` never reaches a running API). Only :3301 is bypassed.
  - Projects: desktop runs all mocked specs; mobile (Pixel 7) runs the SF-01 specs.
- NEW `apps/web/tests/e2e/sf01-field.spec.ts`: 21 tests.

## Preserved contracts (unchanged tests prove it)
- One `h1` per page.
- Exact texts: `orientation-role` / `-governance-capable` / `-denied`, `create-workspace-error`, `add-member-error`.
- `add-member-success`, `command-outcome[data-outcome]` (unique per page, because one current effect per surface), `challenge-create-unavailable`, `session-create-unavailable`, `load-failure`, `orientation-rejected` / `-error`.
- All labels and button names used by the F02 real-stack specs. Button labels no longer change to "Creating…"/"Adding…"; REQUESTED is announced by `EffectIntent` instead.

## Test-first intent (L3)
- **TRUE:**
  - isolation fails closed;
  - the trace comes from the projection; the loading trace is access only; NOT_FOUND invents nothing;
  - Workspace Challenge relation is possible; Session identity is server-projected;
  - an unavailable relation shows the server reason and no control;
  - REQUESTED ≠ COMMITTED;
  - C3-01 unknown consequence with re-read and the same key on repeat;
  - INDETERMINATE retains the key and a definitive outcome releases it;
  - the marker claims a re-read only after it happened;
  - C3-06 committed + unreadable → last-confirmed view, dependent effects blocked, manual re-read;
  - keyless founding → unknown, re-read, no "try again";
  - an unrecognized response → INDETERMINATE;
  - DENIED / REJECTED / FAILED_PRECOMMIT / INDETERMINATE are each distinct;
  - proof opens by keyboard in place;
  - relational order and no overflow;
  - reduced motion keeps meaning.
- **IMPOSSIBLE:** as above, inverted.

## RED → GREEN
- **RED:** the SF-01 spec ran against the pre-SF-01 pages (`git archive bea864b` into the session scratchpad, own `npm ci` from the same lockfile, own server :3302), desktop: **19 failed / 2 passed**.
  - The two passes are expected: the isolation harness, and the CF-07 rule F02 already satisfied (it acts as a regression guard here).
- **GREEN:** isolated lane **81 passed** (39 existing mocked F01/F02 specs unchanged + 21 SF-01 × 2 projects). vitest 170. eslint and tsc clean.
- One lint repair: React Compiler `set-state-in-effect` flagged an `async` loader invoked from an effect. It was rewritten in F02's promise-chain form; behavior is unchanged.

## Lane side effects (disclosed, reverted)
`next dev` (v16) generated `apps/web/AGENTS.md` and `apps/web/CLAUDE.md`, and rewrote `apps/web/next-env.d.ts` (`.next/types` → `.next/dev/types`).
- None of these existed or differed before the run.
- Generated at 20:50:49 by this lane; removed, and `next-env.d.ts` restored with `git checkout`.
- The same generation happens on every `next dev` run in this tree. Re-check `git status` after each lane.

## Accessibility / responsive
- Structural: one `h1`; `nav` "Inquiry position" with `aria-current="location"`; `role=status` for commit and request; `role=alert` for boundaries; native disclosure; the reason code is in text; status words sit outside the links.
- Responsive: the layout is single-column at ≤ 860px with DOM order = relational order, asserted by bounding boxes on Pixel 7. No overflow on desktop or mobile. axe runs in L7 (prepared).

## Residual divergence (disclosed, F03 contact zone)
The Session page still renders with F02 `AppShell` breadcrumbs, F02 `Outcome` and `OUTCOME_TEXT`, which includes "Nothing is assumed to have changed" for mutation network loss (falsifier 17), plus the index-based mobile phase hiding. It is re-homed only in Stage 2 after F03 is published (SF01-HD-3).

## DeepSweep
- Chain: position (CF-01) → PF-01 → CF-02 surfaces → CF-07 (server capabilities only; `governanceCapable` from the F01 server projection) → CF-08 (effect relations) → CF-09 (depth) → API unchanged → persistence unchanged → tests.
- Inverse (Challenge page, possible Session relation): trace segment `session/possible` ← `capabilities.openSession.available` ← `_holds(SESSION_CONTROL_RIGHT, CHALLENGE:<id>)` in `inquiry_queries.challenge_detail` ← an ACTIVE binding.

## Git state
Uncommitted, nothing staged.

## Result
PASS (L3/L4).


===== docs/implementation/field-reports/SF-01/WU-SF01.5.md =====

# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.5 — Static architecture gates (L5)

## Mission
Make the MUST_REMAIN_IMPOSSIBLE list mechanically checkable over every SF-01 source file.

## Files changed
- NEW `apps/web/tests/field/gates.test.ts` (13): six gates, each first proven non-vacuous against a violating sample, plus a file-set completeness check (≥ 13 files, named anchors).
- Comments are stripped before matching, so documentation may name what it forbids.

## Gates
1. No timer semantics (`setTimeout` / `setInterval`).
2. No role- or viewer-flag authority inference (`role ===`, `viewer.role`, `isGovernanceRoot`, `isSessionController`).
3. No F03 vocabulary (Burst, capture, participant / PARTICIPATION, CLOSE_QUESTION_GENERATION, original text, freeze): WAIT_FOR_F03.
4. No AI invocation.
5. No client persistence of state (`localStorage` / `sessionStorage` / `indexedDB`).
6. No import from the F03 contact zone (Session page, F02 `Outcome`).

## Further L5 results
- eslint clean; tsc clean; `next build` compiled, 8 routes (same as F02).
- **Diff gate vs `bea864b`**: tracked changes are exactly the 3 pages + `globals.css`. The following are untouched:
  - Session page, `lib/api/**`, `components/f02/**`, legacy components;
  - `packages/**`, `apps/api/**`, `apps/worker/**`, `migrations/**`;
  - root / web `package.json`, `package-lock.json`;
  - every existing test file (e2e, real-stack, lib, components);
  - `docs/architecture/**`;
  - the existing Playwright configs and `next.config.ts`.
- `git diff --check` clean.

## RED → GREEN
- Predicate RED: each sample violation matches its gate.
- GREEN: 13 passed.

## Git state
Uncommitted.

## Result
PASS.


===== docs/implementation/field-reports/SF-01/WU-SF01.6.md =====

# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.6 — Isolated real-stack environment + L7 spec (PREPARED, NOT RUN)

## Mission
Prepare L6/L7 in an environment isolated from the running F03 stack (SF01-HD-2) without touching the
contact zone. No Field PASS until it has run.

## Boundary found
The API's CORS origin is fixed to `http://localhost:3000` (`apps/api/src/nquiry_api/main.py:91`).
- `apps/api` is outside SF-01's scope, so "same stack on other host ports" would break every credentialed browser call unless the API were changed.
- Resolution (Case 2: a functionally interchangeable isolation means, changing no semantics): **network-namespace isolation**. The ports keep their numbers but are private to the SF-01 namespace; no host port is published.

## Files changed (all NEW)
- `infra/sf01/compose.yaml`
  - Project `nquiry-sf01`; own volume `sf01_postgres_data`; **no host ports**.
  - `runner` runs this tree's API (:8000), Next.js (:3000) and Chromium inside one private namespace; `postgres` is the isolated DB.
- `infra/sf01/runner.Dockerfile`
  - Python 3.13 (pyproject) + Node 22 binaries copied from the official image (no curl-to-shell).
  - `pip install .`, `npm ci` from the lockfile, Playwright Chromium.
- `infra/sf01/runner.Dockerfile.dockerignore`: Dockerfile-scoped, so no other image's build context changes.
- `infra/sf01/run-in-namespace.sh`: DB principals (`db_roles.sql`) → migrations → uvicorn → next dev → the whole real-stack lane (F02 regression + SF-01), desktop + mobile.
- `scripts/run_sf01_real_stack.sh`: host entry.
  - Guards, before anything starts: resolved project == `nquiry-sf01`, and no service publishes a port.
  - Fresh SF-01 DB per run (removes only `nquiry-sf01` volumes). Output goes to `apps/web/test-results/sf01-real-stack/` (gitignored).
- `apps/web/tests/real-stack/sf01-field.real.spec.ts` (2 tests × 2 projects; no network interception, global setup enforces it):
  - trace rebuilt identically after reload;
  - Challenge relation unavailable for the Owner, possible for the Facilitator;
  - Session relation unavailable → possible only through a real grant;
  - no Session coordinate before CreateSession;
  - commit markers after the re-read;
  - authority proof by keyboard;
  - **real transport loss** (browser offline mode): unknown consequence → last-confirmed view → manual re-read → same-intent repeat → exactly ONE Challenge;
  - axe 0 serious/critical and no overflow on every SF-01 surface;
  - reduced motion keeps meaning (malformed id → `rejected`, verified in `http/workspaces.py` → `_malformed_input_response`).

## Validation done (no containers started)
- `bash -n` on both scripts: OK.
- `docker compose -p nquiry-sf01 -f infra/sf01/compose.yaml config`: name `nquiry-sf01`, services `postgres, runner`, ports none, volume `sf01_postgres_data`.
- Running containers after this WU: only the F03 project's (`nquiry-api-1`, `nquiry-postgres-1`, `nquiry-web-1`), untouched.
- tsc and eslint clean on the new spec.

## Not yet proven (must be proven by running)
Image build, migrations on an empty DB, Chromium in the container, CORS inside the namespace, and every L7 assertion. The first run may surface environment defects; they would be fixed inside `infra/sf01/` only.

## Git state
Uncommitted.

## Result
PREPARED in this WU. Executed in WU-SF01.7: 10/10 GREEN twice (the second run on the final tree after
one application and one environment repair). The "Not yet proven" list above is now proven; see WU-SF01.7.


===== docs/implementation/field-reports/SF-01/WU-SF01.7.md =====

# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.7 — Isolated real-stack execution (L6/L7), defects found and repaired

## Mission
Run L6/L7 exactly as prepared in WU-SF01.6, in the isolated environment only (SF01-HD-2).
- An application defect is traced to its First Broken Relation and repaired inside SF-01.
- An environment defect is repaired inside `infra/sf01` only.
- The F03 contact zone is not crossed and F03 is not integrated.

## Runs
| Run | Tree | Result |
|---|---|---|
| L7 run 1 | SF-01 as of WU-SF01.6 | **10/10 passed**, exit 0 (F02 a11y, F02 flow, WU-02.12 closure, 2 × SF-01; desktop + Pixel 7) |
| L7 run 2 (final) | after the two repairs below | **10/10 passed**, exit 0 |

Both runs:
- `SF01_GUARD: project nquiry-sf01, no host ports`;
- `MIGRATION_STATIC_CHECK::PASS (22 revisions, single head b3d8e5f0a2c7)`;
- `MIGRATION_LIVE_CHECK::PASS` on the empty isolated DB, after `db_roles.sql`.

The environment starts from an empty DB each run, and only `nquiry-sf01` volumes are removed. After each run, only the F03 project's containers exist, untouched:
- `nquiry-api-1` / `nquiry-web-1` have run continuously since 17:50Z;
- `nquiry-worker-1` exited at 17:50:17Z, 0.24 s after it started (the no-op worker skeleton), 79 min before run 1 began at 19:09:25Z.

## Defect 1: APPLICATION (found by visual proof, not by a test)
- **Symptom:** in the run-1 screenshots, the closed proof disclosures ("Who holds Session control for this Challenge", "Authority you hold here") had no visible open/closed marker, so they looked like static headings.
- **First Broken Relation:** `PROOF DEPTH → PERCEIVABLE ACTIVATION TARGET` (21 §35: "reasons and proof are explicit activation targets", no hover).
  - The SF-01 CSS set `summary { display: flex }`, which removes the native `list-item` marker.
  - Keyboard and screen-reader semantics were intact (native `<details>`), so every test passed. Only sighted users lost the relation.
- **Test first:** the L3 proof-depth test now requires a visible `::before` marker that changes between closed and open.
  - RED: 2 failed (desktop + mobile, `content: "none"`).
- **Root repair** (`globals.css`, SF-01 section): explicit ▸ / ▾ marker, decorative for assistive tech (`content: "▸" / ""`), since `<details>` already exposes the state. The summary also takes the action color.
  - GREEN: isolated mocked lane 81/81; L7 run 2 10/10; visually verified (`visual/desktop-03`, `visual/desktop-04`).
- **Propagation:** `ProofDepth` is the only disclosure primitive; the Workspace and Challenge proof zones are repaired by the same rule.

## Defect 2: ENVIRONMENT
- **Symptom:** after run 1, the mocked lane failed at start with `EACCES: unlink … test-results/sf01-real-stack/f02-visual/…png`.
- **First Broken Relation:** runner output ↔ host workspace ownership. The runner runs as root and wrote root-owned files into the bind mount, so the other lanes could not clean `test-results/`.
- **Repair (infra/sf01 only):** `run-in-namespace.sh` records the owner of the mounted output directory, which the host wrapper creates as the host user, and `chown`s everything back on exit (EXIT trap).
  - The files already root-owned were handed back once with a one-shot container that mounted only that directory.
  - After run 2: 0 non-user-owned files.

## Lane side effects (unchanged, disclosed)
- Every host `next dev` run of the mocked lane regenerates `apps/web/AGENTS.md` / `CLAUDE.md` and rewrites `next-env.d.ts`. They were removed and restored after every run; the final tree is clean.
- The mocked lane wipes `apps/web/test-results/` at start, so raw L7 output is transient. The final screenshots are curated into `visual/` (10 PNGs, 1.7 MB).

## Proof ceilings
- The web server under L7 is `next dev` (same as the F02 real-stack lane), not a production server. `next build` is proven separately (L5).
- L7 RED against the pre-SF-01 pages was **not** run. Non-vacuity of the SF-01 assertions is proven at L3 (19/21 RED on the `bea864b` pages). The L7 spec asserts the same relations with the real stack underneath.

## Git state
Uncommitted, nothing staged.

## Result
PASS: L6/L7 GREEN in the isolated environment on the final tree.
