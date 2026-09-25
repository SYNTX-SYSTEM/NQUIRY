# NQUIRY FIELD REVIEW REPORT

## Field
SF-03: NQIRY Symbiotic Surface Evolution — the materialization of doc 23
(`docs/implementation/frontend/23_NQIRY_SYMBIOTIC_SURFACE_EVOLUTION_ARCHITECTURE.md`) on the SF-02 Field, doc 22
remaining the protected semantic architecture.

## Worktree State
- `/home/codi/Entwicklung/nquiry/worktrees/frontend-symbiotic`, branch `frontend-symbiotic`, HEAD `644e1c8`. The
  SF-02 tree (29 uncommitted paths at the start) was the baseline; it was neither reset nor reconstructed. SF-03 adds:
  `apps/web/lib/field/{geometry,reciprocity}.ts`, `components/field/Identity.tsx`, `tests/field/{geometry,sf03-primitives}`,
  `tests/e2e/sf03-field.spec.ts`, `docs/implementation/frontend/23_*.md` (byte-identical copy, sha256 `8aa5b6ecd6b280e8…`),
  `docs/implementation/field-reports/SF-03/**`; and changes `globals.css`, `FieldStage/Orbit/FieldCore` (unchanged API
  for the core), `FieldFrame`, `FieldBackground`, `lib/field/topology.ts`, the five pages, `playwright.sf01.config.ts`,
  `tests/e2e/sf01-field.spec.ts` (one geometric assertion), `tests/field/topology.test.ts` (superseded tests removed).
- **NOT COMMITTED, NOT TAGGED, NOT PUSHED.** No PUBLISHED / FIELD_GREEN claim. BLUE (F02, F03) untouched:
  `apps/api`, `packages`, `migrations`, `lib/api/*`, `components/f02/*`, `components/f03/*` unchanged.

## Field Purpose
Make the already correct Symbiotic Field deeper: alive across the whole viewport, legible everywhere, spatially
composed from its content and the viewport, oriented by a rail that belongs to it, identified at its centre, with
instruments that form one constellation with the topology and respond to the relation under attention — without
changing any projection, command, capability, authority, visibility or lifecycle rule.

## Authoritative Parent
Doc 23 (delta authority, read completely) · doc 22 (protected semantics, re-read completely) · doc 21 / SF-01 ·
20 (SFE) · published F01/F02/F03 contracts (binding unchanged from `SF-02/WU-SF02.0.md`).

## Human decisions used
`SFE::MATERIALIZE_APPROVED_ARCHITECTURE_DELTA` (2026-09-25): materialize the complete delta on the existing SF-02
tree; do not reset it; real backend; preserve protected semantics; no commit / tag / push / PUBLISHED / FIELD_GREEN.

## Case 3
None. Every delta is presentation (doc 23 §18 Case 2); the centred NQIRY identity is the approved product
presentation and nothing beyond it.

## Initial State (SF-02)
Fixed 720 px square, fixed radii, fixed node widths (later lifecycle phases as dots), core title clamped to three
lines, brand label top-left, `→` breadcrumb, instruments as a flex column at the right, bounded background, F02
light-theme minimums in type.

## Final State
- **Geometry from content** (`lib/field/geometry.ts`): estimated frames → weighted angular allocation → ring radius
  from the content → outer-ring offset search and spoke nudge → collision loop against every frame and the core →
  width-bounded growth into a taller ellipse → compact frames → stack as the compacted representation; box height
  follows the content; mode from the viewport class; deterministic and SSR-safe.
- **Typography/containment**: `max-content` frames with size maxima, legible floors (≥ 11.8 px), no clamp, no
  clipping, identifiers wrap.
- **Living Field**: two drifting nebular blobs + static haze + breathing luminosity + traces + rare particles;
  reduced motion keeps every layer; cost measured (rAF 16.3 / 19.2 ms at ×4 throttle).
- **Orientation rail**: trace · centred designed identity · exit; separators breathe on a pseudo-element; text static.
- **Instrument constellation**: grid (2 columns ≥ 1500 px, active relation first, governance/proof beside);
  Field ↔ instrument reciprocity by focus and hover, presentation only.
- **Surfaces**: all 13 lifecycle labels readable; frozen/human planes first; whole viewport (1880 px max).

## Proof (final tree)
| Lane | Result |
|---|---|
| L0 vitest | 232 / 232 |
| L5 tsc / eslint | 0 / clean |
| L3 isolated mocked (81 regression + 21 SF-03; desktop + Pixel 7) | **102 / 102** (2.0 min; 81 SF-02 regression + 21 SF-03 stress/acceptance; desktop + Pixel 7; lane alone) |
| L7 isolated real stack | **14 / 14** (6.9 min, lane alone, host load 4–6; earlier runs on the same lane at load 9–17: 12/14, 12/14, 13/14 — only the F03 protected spec's 90 s budget, no assertion ever failed) |
| E browser evidence (production build, real API; 40 states incl. wide, reduced motion, stress) | run-5 **40 / 40** (30 SF-02 regression states + 10 doc 23 acceptance states; axe serious/critical 0, overflow 0, no unexpected HTTP, keyboard focus visible everywhere) (runs 1–4: 39/40, 39/40, 38/40, 40/40 — each RED a repaired root; run-4 preceded D-SF03-5) |
| P performance (×4 CPU throttle) | Access 16.3 ms · Workspaces 19.2 ms rAF median (SF-02: 16.6 / 29) |

## Defects found by proof and repaired at the root
Font floors (eyebrow/mono), sm frame width, ring minimum radius (core corner), width-exhausted growth, mode ↔
measurement loop (node "not stable"), phone md rows, uppercase token width (D-SF03-1), path through a tinted frame
(D-SF03-2), spoke coincidence after the offset search, a radius step leaving the width (D-SF03-3), estimated vs
rendered frames + a latched height need (D-SF03-4 → rendered-frame refinement, derived height), the core's rendered frame
and the mode decision on rendered frames (D-SF03-5); two probe artefacts
recorded as such (WU-SF03.1/.2/.7/.8).

## Ceilings (disclosed)
- Visible-identity falsifiers (doc 23 §20: 1–2, 14, 17, 19, 26–27, 31–34, 43) are the human's verdict on the run-2 screenshots.
- The isolated real-stack F03 protected spec exceeds its 90 s budget on this host under load (no assertion fails);
  see WU-SF03.7 for the re-run.
- Doc 23 §9.4 breadcrumb → Field reciprocity not implemented (optional).
- The 2-column constellation starts at 1500 px; at 1280 px the instruments compose in one column (OV-1).
- Evidence PNGs (~33 MB per run) are untracked; the human decides what to commit.

## Commit Status
NOT COMMITTED. Awaiting human Field Review.

## Result
**READY_FOR_HUMAN_FRONTEND_REVIEW** — every machine-provable claim of doc 23 is GREEN on the final tree (L0 232, L3 102, L7 14, evidence 40/40, perf measured); the visible-identity falsifiers are the human's verdict on the run-5 screenshots. Not FIELD_GREEN by my declaration.
