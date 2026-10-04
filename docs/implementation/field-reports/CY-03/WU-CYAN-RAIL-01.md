# WORK UNIT REPORT
FIELD: CYAN_FRONTEND_SYMBIOSIS (Architecture 27 v4, `b0a5101` on `pfc-integration`) — organism rail (doc 26 §29–§30 breadcrumb field path)
WORK_UNIT: CYAN-RAIL-01 — the route never crosses the centred mark
DATE: 2026-10-04 · BASE: `checkpoint-CY-PCPG-06` `c2a5426` (+ record `9a643ca`)
AUTHORITY: the human mandate of 2026-10-04 (reconstruct the complete real frontend Field; derive the work from the reconstructed Field and its real relations; after every material Effect reconstruct the resulting state); the human's observation during the PCPG-04 review ("the rail's current trace chip overlaps the centred wordmark at 1280 px"), recorded as "observed, not changed" in `CY-02/browser-evidence/pcpg-06/SUMMARY.md`. No RED, PURPLE, Google, nginx or production relation is touched; RED pin for the local lanes `checkpoint-PFC-PCPG-18` `41b4324` unchanged.

## Field reconstruction (before the delta)
| Relation | State at the base |
|---|---|
| Header grid: route column · centred identity mark · exit (SF-06) | the mark is centred by the grid; the route column's width is **derived** from the grid (viewport − mark − exit), never the other way round |
| Route (`.trace ol`, five stations: Workspaces · Workspace · Challenge · Session · lifecycle state) | `flex-wrap: nowrap` (SF-05 `globals.css` ≈3336); every station `flex: 1 1 auto; min-width: 9ch` (≈3340); the current station `min-width: min(100%, 22ch)` (≈3357), raised to `calc(22ch + 36px)` in the SF-06 era (≈4991) |
| Sum of the station minimums | 4 × 9ch + 22ch + 36px + connectors + paddings ≈ 760–800 px at 16 px ≥ the route column at 1024–1440 px (the column is ≈ 330–520 px) |
| **Effect** | the `ol` overflowed its column to the right and the current chip was drawn over the centred wordmark (1024–1440 px); the chip read "ANALYSIS" complete, but **on top of the mark** |
| Falsifiers | `sf05-field` §29–§30 measured only that the route is one line and the current label complete; no law measured the stations against the mark; the human saw the defect before any lane did |
First broken relation: the station minimums were **constants** (9ch, 22ch + 36px) instead of being derived from the column the grid gives the route. Repair: no station reserves more than it needs — the current station reserves exactly its label, the established stations reserve exactly their marker — and the structure itself tightens when the column is narrow.

## Delta (CYAN only)
| File | Change |
|---|---|
| `apps/web/app/globals.css` | block **CYAN-RAIL-01** (end of file, desktop ≥ 768 px): `.shell-header .trace` becomes a size container; `.trace ol { max-width: 100% }`; every station `min-width: calc(1ch + 42px)` (its marker and paddings); the current station `flex-grow: 2; flex-shrink: 0.001; flex-basis: auto; width: max-content; min-width: 0; max-width: 100%` (basis = its complete label; a negligible shrink factor, so the established stations give way first and are frozen at their minimum before the current station gives a pixel; only a title longer than the whole route truncates); the current label `flex: none; width: max-content; max-width: calc(100% + 1px)` (its box carries its own text advance — a box short by a fraction of a pixel already drew the ellipsis on the complete word "ANALYSIS"); `@container (max-width: 560px)` tightens paddings, margins and the connector width and removes the gap. The SF-05 comment names its successor. |
| `apps/web/tests/e2e/cy10-rail.spec.ts` (new, 24 desktop cases) | law: at 1024 / 1180 / 1280 / 1366 / 1440 / 1600 px × ANALYSIS, QUESTION_GENERATION, QUESTION_GENERATION with long Workspace and Challenge names, CHALLENGE_CAPTURE with long names — five stations on one line, **every station's right edge ≤ the mark's left edge**, the mark centred (< 6 px), the exit right of the mark, the current label complete (`scrollWidth`, and sub-pixel: the label box carries the text advance), the Challenge link keeps its `title`, no station below 13.5 px |
| `apps/web/playwright.sf01.config.ts` | mobile regex includes `cy10` (the cases skip themselves on Pixel 7: desktop law) |
| `apps/web/scripts/rail01-mutation-proof.mjs` (new) | 4 browser-killed mutations over the rule, byte-identical restore |
Not changed: the route's content, order, markers, titles, the mark, the exit, the SF-05/SF-06 rules themselves (they stay as the base layer and are overridden by the later cascade), the Pixel 7 rail.

## Laws and where they hold
| Law | Materialization |
|---|---|
| The route never crosses the centred mark | cy10 (every `li.right ≤ identity.x + 1`), review runtime measurements below |
| The current station is complete whenever the route can hold it | cy10 (`scrollWidth` + sub-pixel advance), R1, R4 |
| Established stations compress before the current one and stay inspectable | cy10 (`title` on the Challenge link), R2 |
| The structure tightens before the words do | R3 (container query) |
| The mark stays centred; the exit stays clear | cy10 (< 6 px; `identity.right ≤ logout.x + 1`) |

## Proof
| Lane | Result |
|---|---|
| Browser law `cy10-rail` (desktop) | **24 / 24** |
| Preservation `cy10`, `sf01`, `sf03`, `sf04`, `sf05`, `cy01-field`, `cy04-membrane` (desktop + Pixel 7) with the final CSS | **171 passed, 51 pre-existing skips, 0 failed** |
| Full unit suite | **661 / 661** |
| `tsc --noEmit` | clean |
| `eslint .` | 0 errors, 1 pre-existing warning (`components/field/Identity.tsx` `<img>`) |
| Mutation proof `scripts/rail01-mutation-proof.mjs` | **4 / 4 killed** (R1 fixed 22ch reservation returns: 4 failed; R2 9ch minimum returns: 6; R3 container tightening removed: 7; R4 label box no longer carries the advance: 24), `globals.css` byte-identical before and after (`a8836048…`) |
| Review runtime `127.0.0.1:13500` (real session, RED `checkpoint-PFC-PCPG-18`) | current station box 1024: 331–434 (103 px), 1280: 459–562 (103 px), 1440: 521–642 (121 px); fits left of the mark at all three; overlap false; label box 79.53 px = text advance 79.53 px (before the label rule 79.48 vs 79.53 → ellipsis on the complete word) — `browser-evidence/rail-01/SUMMARY.md` |
| Lane hygiene findings | (1) a root-owned stale `apps/web/test-results/sf01-real-stack` (27 Sep, a container run) blocks Playwright's output cleanup → the lanes run with `--output` in the session scratchpad; not a product defect. (2) `next dev` 16.3.5 writes `apps/web/AGENTS.md`, `CLAUDE.md` and rewrites `next-env.d.ts` to `.next/dev/types`; tool-generated, left uncommitted, not part of this delta. |

## Status
CYAN-RAIL-01: TECHNICALLY CLOSED → **READY_FOR_HUMAN_FRONTEND_REVIEW** (visual: review runtime `127.0.0.1:13500`,
any Session at 1024–1440 px; the established stations now read as "W…", "On…", "Where doe…" with their titles — the
human is the Visual Authority on whether that compression is acceptable or the column should be given more of the
header). Not FIELD_GREEN until accepted; not REVIEWED_FIELD, not PUBLISHED_FIELD, not live (`/cy-review` candidate
and `/` unchanged).

## Checkpoint
| | Value |
|---|---|
| Field commit | `3a2931930775c39637bf7ec8f534596543302fd5` (tree `5c6140b3d9ec0f4922ba3f001cdaa14fb4c22d70`) |
| Tag | `checkpoint-CY-RAIL-01` → tag object `2f58df1ff2c8ac10a0eb04bf9a202acfeb1fcee5` → `3a29319`; pushed |
| RED pin (local lanes) | `checkpoint-PFC-PCPG-18` → `41b4324a75077ec33b00ed3a878db7a318fc00d8` (unchanged) |
