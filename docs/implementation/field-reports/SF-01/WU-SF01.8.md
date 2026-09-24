# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.8 — Sync with published F03 (integration law steps 1–3)

## Authorization and scope
`F03_FRONTEND_SYNC_APPROVED`: the published-F03 branch sync ONLY.
- In scope: reconstruct F03 → synchronize the branch → post-sync DeepSweep.
- NOT in scope:
  - ledger reconciliation (WAIT_FOR_F04_ARCHITECTURE_RECONCILIATION: REC-018..027 and NQ-DEC-044..051 are claimed by the concurrent, uncommitted F04 architecture field);
  - Stage 2 (Session page);
  - F04; any `BEGIN_ANALYSIS`;
  - commit, tag, push.

## Published F03 (reconstructed read-only before the sync)
- `origin/master` = `c9d86bab` = remote `master` (`ls-remote`; no fetch needed).
- `field-F03` → `0d59ae3f` (signature good).
- Merge base `bea864b`.
- Terminal state:
  - capture happens in Session `QUESTION_GENERATION` with the Burst ACTIVE HUMAN_ONLY (PARTICIPATION authority);
  - `CMD_COMPLETE_BURST` (TRN-SESS-005 + TRN-BURST-005, one bundle, HD-9) gives Burst COMPLETED, a frozen fingerprinted membership, and Session `QUESTION_CAPTURE`;
  - the Field ends there. No `BEGIN_ANALYSIS` / TRN-SESS-006 is projected anywhere (F04).
- Doc 21's `CLOSE_QUESTION_GENERATION` = F03's published `COMPLETE_BURST` / `CMD_COMPLETE_BURST` (name only; 21 §38).

## Sync performed (uncommitted)
- `git merge --no-ff --no-commit c9d86bab`: preserves the reviewed SF-01 commits `447b24e` and `c944b95` (no rebase, 19 §16).
- 82 paths merged automatically. **1 textual conflict**: `apps/web/app/globals.css`. Both Fields appended at base line 424, with no shared selector.
  - Resolution: the published F03 file, followed by the SF-01 block, both byte-verified.
  - Result: 694 lines = 424 base + 27 F03 + 243 SF-01.
- Fidelity of the staged merge:
  - vs published F03 it differs by exactly the SF-01 file set (51); vs SF-01 HEAD by exactly the F03 file set (83);
  - every file other than `globals.css` is byte-identical to its source side;
  - backend, API, worker and migrations are identical to published F03.

## First Broken Relation found by the synced tree
**`PUBLISHED F03 SessionPosition PROJECTION → SF-01 TRACE PROOF FIXTURE`.**
- F03 extended `SessionPosition` with the required `serverNow`, `questionSet` and three Burst fields. The SF-01 test fixture was typed as the whole F02 projection.
- The merge was textually clean but broke typechecking. RED on the real synced tree:
  - `tsc`: 1 error (`tests/field/position.test.ts:41`, TS2739);
  - `next build`: "Failed to type check".
- `sessionTrace` itself was semantically correct: it only reads F02-stable coordinates.

**Root repair (type-only, unstaged, separate from the pure merge):**
- `SessionTraceInput` is declared **structurally**: exactly `workspace.{workspaceId, name}`, `challenge.{challengeId, title}`, `session.state`, `establishedBy?.commandType`.
- `sessionTrace` takes it. The fixture is trimmed to it.
- A type-level contract test asserts that the published `SessionPosition` stays assignable to it.

**Self-review correction:** the first repair draft used `Pick<SessionPosition, …>`. A scratch check proved that contract is vacuous: it passes even when a later projection retypes `session.state`. The structural version fails on that mutation (TS2344) and passes on the published F03 shape.

**Runtime neutrality proof:** `position.ts` compiled to JavaScript (comments removed) is byte-identical between the committed SF-01 version (`c944b95`) and the final version. The repair is type-only. The only other changed file is a test.

## Proof ladder (synced + repaired tree)
| Lane | Result |
|---|---|
| tsc | 0 errors (RED before the repair: 1) |
| eslint | 0 findings (a transient unused-import warning from the repair was removed) |
| vitest | **196 passed**: SF-01 73 (72 + contract test), F03 25, the rest F01/F02 |
| `next build` | compiled, 8 routes (RED before the repair) |
| SF-01 static gates | 13 passed |
| Diff gate vs published F03 | only SF-01 paths differ; no F03 contact-zone, backend, migration, dependency or ledger file differs; no REC-018..027 / NQ-DEC-044..051 identifier present; no `BEGIN_ANALYSIS` in the frontend; `git diff --check` clean (staged + unstaged) |
| Isolated mocked lane (:3301, dead proxy) | **81 passed** (39 existing F01/F02 + 21 SF-01 × desktop + Pixel 7) on the F03-synced pages, clients and CSS |
| Isolated real stack (`nquiry-sf01`, no host ports) | guard PASS; migrations static + live PASS, **25 revisions, head `f6b2c4d9a318`** on an empty DB; **14/14 passed** on desktop + Pixel 7 (F02 flow, F02 a11y, WU-02.12 closure, F03 protected question field, F03 a11y, SF-01 path, SF-01 reduced motion) |
| axe / keyboard / responsive | covered in the real stack by F02 a11y, F03 a11y (keyboard-only capture and completion) and SF-01 (overflow, relational order, keyboard proof depth): all passed |

The browser lanes ran before the final type-only hardening. The emitted-JS identity above proves they cover this exact runtime.

## Recursive Integration DeepSweep (post-sync)
- **Domain, authority, boundaries, persistence** (F03: PARTICIPATION source, BND-005/008/014, 3 migrations): backend-owned, byte-identical to published F03. Proven at runtime by the F03 real-stack specs inside the isolated stack.
- **Application, API:** envelope vocabulary unchanged; SF-01's closed `SETTLED_KINDS` remains valid; two routes added.
- **Projection:** `workspace_overview` and `challenge_detail` (consumed by SF-01 pages) are unchanged. `session_position` grew, where the FBR was repaired.
- **SF-01 primitives:** `outcomeSemantics`, `effectLifecycle`, `useEffectField`, `EffectSurface`, `ProofDepth`, `Origin` and `RelationTrace` are unchanged; `position` is repaired (type-only).
- **Pre-Session pages:** unchanged, green in both browser lanes.
- **Session page:** F03's version, untouched (Stage 2).

## Inverse Integration DeepSweep
- **Visible pre-Session position:** ← `workspaceTrace` / `challengeTrace` ← unchanged F02 projections ← canonical rows. Real stack: identical trace after reload; Session relation unavailable → possible after a real grant.
- **Future Session-page trace:** ← `sessionTrace` ← `SessionTraceInput` ⊆ published F03 `SessionPosition` (enforced by tsc) ← `establishedBy` (F03 resolves `QUESTION_CAPTURE` → `CMD_COMPLETE_BURST` uniquely) ← BINDING at `SESSION:<id>` (HD-9).
- **Frozen set** (F03 surface, unchanged): ← `questionSet.frozen` ← `verify_frozen_set` ← committed bundle. Proven by the F03 real-stack spec in the isolated stack.

No link requires an unpublished contract.

## Recorded for Stage 2 (not repaired here: out of scope)
From the pre-sync reconstruction, confirmed on the synced tree. None blocks the sync.
- I-4: the F03 capture panel drops its intent key after a server INDETERMINATE (doc 21 §14 / C3-01 require keeping it).
- I-5: the Session page still uses F02's page-level Outcome, including the falsifier-17 wording.
- I-6: the freeze fingerprint and integrity are shown permanently on the surface instead of at depth D2.
- I-7: two origin vocabularies (`data-origin="HUMAN"` + `.verbatim` vs `human-source` + `.t-source`).
- I-8: the SF-01 timer and F03-vocabulary gates need rescoping when the Session page joins the SF-01 sources.
- I-10: two functions named `intentKeyFor`.

## Ledger
Untouched. The pending SF-01 entries (STATUS.md) stay unnumbered. The concurrent claim on REC-018..027 / NQ-DEC-044..051 by the uncommitted F04 architecture field is recorded as WAIT_FOR_F04_ARCHITECTURE_RECONCILIATION.

## Lane side effects
Host `next dev` regenerated `apps/web/AGENTS.md` / `CLAUDE.md` / `next-env.d.ts`; these were removed or restored after the lane. The runner's output was handed back to the host user (0 root-owned files).

## Git state
- Merge in progress (`MERGE_HEAD` = `c9d86bab`), not committed.
- Index: the pure merge (83 paths, including the `globals.css` resolution).
- Unstaged: the root repair (`lib/field/position.ts`, `tests/field/position.test.ts`), this report, and the STATUS.md update.

## Result
PASS: synchronized tree GREEN on the full ladder. Awaiting sync review; no commit.
