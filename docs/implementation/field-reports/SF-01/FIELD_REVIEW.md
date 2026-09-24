# NQUIRY FIELD REVIEW REPORT

## Field
SF-01: Symbiotic Frontend Foundation (pulled forward). Semantic regime: the pre-Session Relational
Interaction Field (doc 21 §48, Stage 1 plus the Stage 3 primitives).

## Worktree State
*(State at review time, before the Field commit. The approved commit identity is recorded under "Commit Status" below.)*

- Worktree `~/Entwicklung/nquiry-frontend`, branch `frontend-symbiotic`, at `bea864b` (F02 published, identity recorded). SF-01 is uncommitted.
- Index empty. `git diff --check` clean. **NOT COMMITTED.**
- Throughout SF-01, up to and including Field Green, F03 was in progress in a separate worktree and environment (compose project `nquiry`). It was neither inspected nor touched. F03 was published afterwards (see "Post-run timeline").

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

## Post-run timeline (F03 publication, recorded at review closure)
1. **SF-01 reached FIELD_GREEN_WITH_DISCLOSED_CEILINGS while F03 was still in progress, isolated and excluded.** All SF-01 proof (L0–L7, including both isolated real-stack runs) was produced on the base `bea864b`, with the F03 contact zone untouched and no F03 content inspected.
2. **F03 was published afterwards.**
   - Field commit `0d59ae3f9be5f3a3297d43ab55c70005c41aa68d`.
   - Publication record `c9d86bab64505845f406ba43a8c78ac185383680` (= `origin/master`).
   - Signed annotated tag `field-F03`.
   - Verified read-only in the local object store, with no fetch, checkout or content read: the tag peels to `0d59ae3f`, `git verify-tag` reports a good signature, `0d59ae3f` is an ancestor of `c9d86bab`, and the SF-01 base `bea864b` is an ancestor of `0d59ae3f` (a forward sync).
3. **No F03 integration has occurred inside SF-01.** The branch `frontend-symbiotic` is still at `bea864b`. No SF-01 file reads, imports or anticipates any F03 contract, and SF-01's proof and status statements refer to that base only.
4. **The documented post-F03 integration law is now ACTIVE, not yet executed:** reconstruct published F03 → synchronize the frontend branch → contract and dependency DeepSweep → ledger reconciliation (SF01-HD-5) → Stage 2 Session-page integration. Until it has run, every WAIT_FOR_F03 relation stays WAIT_FOR_F03.

## Downstream
- **Integration law, now ACTIVE (F03 published; not yet executed):** STOP → reconstruct F03 → sync this branch with the published commit → contract and dependency DeepSweep → reconcile ledgers (SF01-HD-5) → then Stage 2 (Session page on SF-01 primitives) and the WAIT_FOR_F03 relations.
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
*(At review time: NOT COMMITTED, awaiting human Field Review.)*

Human Field Review: **PASS**. Approved via `FIELD_COMMIT_APPROVED SF-01`.
- **Committed** as `447b24e6177e891e0df12bdf2d9874379af72911` ("field(SF-01): symbiotic frontend foundation on the pre-Session surfaces (FIELD PASS)"):
  - one commit, parent `bea864b`, signed (GPG, good signature);
  - 50 files (46 added, 4 modified), +7871 / −380;
  - branch `frontend-symbiotic`, **local only: not tagged, not pushed**.
- **Kept out of the Field commit**, as its approved exclusions: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md` (absent), generated `next-env.d.ts` changes (none), `test-results/` (gitignored).
- **Review input bundle**: `review/REVIEW_INPUT_BUNDLE.md` is intentional review-input provenance (human decision), kept verbatim (64 831 bytes, sha256 prefix `1693b9768dc61dec`).
  - It was generated at 22:06 from the SF-01 artifacts as they stood before the post-F03 timeline notes, so it records the review input at that moment.
  - The canonical reports are the files in this directory.
  - It was not in the Field commit; the documentation-record commit adds it.
- **Commit identity** recorded after the Field commit, in a separate documentation-only commit (19 §16: the only post-commit change permitted to a historical report). No other content of this report was changed.
- **Timeline preserved:** SF-01 reached Field Green while F03 was excluded; F03 was published afterwards; **F03 integration has still NOT begun.**
  - The SF-01 commits sit on `bea864b`, and the branch is not synchronized with published F03.
  - The integration law (see "Post-run timeline") remains ACTIVE and unexecuted.

## Recommended Status
**FIELD_GREEN_WITH_DISCLOSED_CEILINGS.** The ceilings are Known Limitations 1–9 plus GAP-14-001. All are disclosed, and none hides an SF-01 relation.
