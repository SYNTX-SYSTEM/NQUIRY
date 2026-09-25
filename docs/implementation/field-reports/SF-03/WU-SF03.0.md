# WORK UNIT REPORT
FIELD: SF-03 — NQIRY SYMBIOTIC SURFACE EVOLUTION (materialization of doc 23 on the SF-02 Field)
WORK_UNIT: WU-SF03.0 — Baseline reconstruction, delta mapping, Work Unit plan

## Authority
Human instruction `SFE::MATERIALIZE_APPROVED_ARCHITECTURE_DELTA` (2026-09-25, 05:25 CEST): implementation authority
over the worktree `/home/codi/Entwicklung/nquiry/worktrees/frontend-symbiotic` (branch `frontend-symbiotic`); no
publication authority (no commit / tag / push / PUBLISHED / FIELD_GREEN). Protected semantic architecture: doc 22.
Delta authority: `docs/implementation/frontend/23_NQIRY_SYMBIOTIC_SURFACE_EVOLUTION_ARCHITECTURE.md` (2094 lines,
read completely; copied into this worktree byte-identical to the main-checkout copy, sha256 `8aa5b6ecd6b280e8…`).
Doc 22 (5878 lines) re-read completely in this session.

## Baseline (PRE-EXISTING SF-02 materialization — not attributed to SF-03)
- HEAD `644e1c8` (SF-01 + published F03 sync). **29 uncommitted paths** = the SF-02 tree
  (18 modified files under `apps/web`, new `components/field/{FieldBackground,topology/*}`, `lib/field/{topology,humanPosition}`,
  their tests, `docs/implementation/field-reports/SF-01/review/**`, `docs/implementation/field-reports/SF-02/**`, doc 22).
  This tree is the parent Field. It is not reset, discarded or reconstructed from an older commit.
- SF-02 proof on that tree (recorded in `SF-02/STATUS.md`): vitest 219/219, tsc 0, eslint clean, mocked 81/81,
  isolated real stack 14/14, browser evidence run-6 30/30, D1–D8 repaired. Evidence: `SF-02/review/browser-evidence-2026-09-25/`
  (82 MB, runs 1–6). SF-03 evidence goes to `SF-03/review/` and never rewrites SF-02 runs.
- Status at the start of SF-03: READY_FOR_HUMAN_FRONTEND_REVIEW (SF-02); doc 23 §2 records the human review of it.

## Current materialized Field (reconstruction, by root)
| Root (doc 23 §28) | Where it lives today (SF-02) | Contact |
|---|---|---|
| background field | `components/field/FieldBackground.tsx` (aria-hidden; 3 static SVG rings; CSS `.field-bg` gradients, `::before` constellation, `::after` bounded breathing layer, regime tint) | `FieldFrame` mounts it; login mounts it directly |
| typography | `globals.css` tokens (`--font-*`, body 16px), node font 0.82rem (md) / 0.72rem (sm) / 0.66rem (dot), core title clamped to 3 lines (`-webkit-line-clamp`) | every node/core |
| node geometry | `.node { width: var(--node-w) }` fixed 132 / 96 / 40 px; `.node-body` pill | `Orbit.tsx` |
| orbit allocation | `orbitPositions(count, startDeg)` even angular spacing on the unit circle; fixed radii `--orbit-r-1/2` (232 / 322 px) in a fixed `--field-size` 720 px square; `outerRingStartDeg` half-step offset | `lib/field/topology.ts`, `Orbit.tsx` |
| global top rail | `FieldFrame`: `header.shell-header` = brand link (left) · `RelationTrace` · logout | `FieldFrame.tsx`, `.shell-header` |
| breadcrumb | `RelationTrace` (`nav[aria-label="Inquiry position"]`, `→` separators, status words) | `RelationTrace.tsx`, `.trace` |
| instrument composition | `Planes` = `.plane-column` flex column (action → governance → proof) in grid column 2 | `FieldStage.tsx`, pages |
| responsive transformation | `@media (max-width: 860px)` stack + `[data-topology="stack"]` (same DOM) | `globals.css` |
| motion | `core-breathe` (glow opacity), `field-breathe` (bounded layer opacity), `path-pulse` (current path), `relation-settle`, `node-shimmer`; global reduced-motion rule | `globals.css` |
| effect law / semantics | `useEffectField`, `effectLifecycle`, `outcomeSemantics`, `EffectSurface`, `position` (trace), `humanPosition` (label), gates | unchanged by SF-03 |

Binding chain (22 §4.9) is unchanged from `SF-02/WU-SF02.0.md`: every relation → real domain / projection /
capability / authority / command / persistence / frontend / test contact. SF-03 adds no projection, command or
capability; every new visible effect is presentation and terminates in PRESENTATION AUTHORITY (doc 23 §25), except
where it re-expresses an existing authoritative relation (nodes, paths, planes) whose evidence contact is the SF-02
harness + the SF-03 harness extension.

## Doc 23 delta → minimum legitimate roots
| Delta (doc 23) | FBR (doc 23 §16) | Root repaired | WU |
|---|---|---|---|
| 1 global living field | FBR-23-01 | `FieldBackground` + `.field-bg`: nebular blobs on bounded compositor layers, haze, rare particles, static reduced-motion equivalent; measured with `perf-ab.mjs` | SF03.3 |
| 2 typography & containment | FBR-23-02 | tokens (legible minimums), `.node`/`.node-body` content-sized (max-content ≤ max), core without clamp (content-sized rounded core), long identifiers wrap, `-webkit-line-clamp` removed | SF03.1 |
| 3 content-aware geometry | FBR-23-03 | new `lib/field/geometry.ts`: estimated node boxes → weighted angular allocation → ring radius from required circumference → ring separation from box heights → collision-resistant, deterministic; `Orbit` renders from it; container-query units make it viewport-aware | SF03.2 |
| 4 breathing room | FBR-23-06 | stage grid + topology sized from the viewport (container queries), radii as fractions of the topology box | SF03.2 |
| 5 symbiotic breadcrumb | FBR-23-04 | `RelationTrace` → orientation rail (same nav semantics/test ids), separator energy on pseudo-elements, current segment halo, focus reciprocity with the core | SF03.4 |
| 6 centred identity | FBR-23-07 | `FieldFrame` header grid (trace · identity · exit), designed mark (`Identity.tsx`), phone row | SF03.4 |
| 7 instrument constellation | FBR-23-05 | `Planes` → `.instruments` 2-D grid (`grid-template-areas`: active relation spans the first column, governance and proof beside it), active-relation priority | SF03.5 |
| 8 whole-surface symbiosis | FBR-23-05/06 | stage grid proportions, shared depth/border/glow language for planes, background continuity behind rail and instruments | SF03.5/3 |
| 9 relational reciprocity | — (§8) | `FieldStage` delegated focus/hover → `data-active-relation`; CSS responds on paths, nodes, planes; keyboard-equivalent | SF03.5 |

## Protected semantics check (doc 23 §3, doc 22 §43)
No delta touches a projection, command, capability, authority, visibility or lifecycle rule. `lifecycleLabelDensity`
changes meaning from "label visible vs assistive" to "emphasis full vs low": every lifecycle label becomes readable
on desktop (doc 23 §13.5, acceptance item 6). This is presentation (Case 2); the SF-02 unit test is rewritten to assert
the new law (labels never hidden, emphasis derived from gravity) — recorded here, not silently.

## Case 3
None. External providers, analysis contact, participant identity, non-controller explanation, denied vs not found:
unchanged from SF-02 (repository facts). Product identity: the centred NQIRY presentation is explicitly approved by
doc 23 §10; nothing beyond it is introduced (the mark is a link to `/workspaces` named "nquiry", as today).

## Work Unit plan
| WU | Title | MUST BECOME TRUE (headline) | Falsifier (doc 23 §20) |
|---|---|---|---|
| SF03.1 | Typography & containment law | no material text escapes its frame; minimum legible sizes; frames follow content | 6–11, 42 |
| SF03.2 | Content-aware, viewport-aware, collision-resistant geometry | deterministic layout from estimated boxes; no overlap; no core collision; breathing room | 12–18 |
| SF03.3 | Global living field | calm ambient life across the viewport; static depth under reduced motion; measured cost | 1–5 |
| SF03.4 | Orientation rail: centred identity + symbiotic breadcrumb | identity centred on desktop; breadcrumb belongs to the Field; readable; current obvious | 19–24 |
| SF03.5 | Instrument constellation + relational reciprocity | 2-D composition on desktop; grouping preserved; proof/governance reachable; reciprocity by hover and keyboard | 25–39 |
| SF03.6 | Surface evolution (Access, Overview, Workspace, Challenge, Session/Human/Frozen) | each surface composed from the primitives; lifecycle labels readable; phone stack intact | 40–46 |
| SF03.7 | Proof ladder + regression + performance | unit/type/lint, mocked (incl. new stress spec), real stack, perf-ab | 47–57 |
| SF03.8 | Browser evidence (SF-02 harness extended with the 15 acceptance screenshots + stress states), reviews, deep sweeps | evidence reconstructable | 58 |

## Result
Baseline recorded; delta mapped to roots; no Case 3. Proceeding to WU-SF03.2 (geometry, pure, TDD) and WU-SF03.1.
