# WORK UNIT REPORT
FIELD: SF-03 — NQIRY SYMBIOTIC SURFACE EVOLUTION
WORK_UNIT: WU-SF03.3 — Global living Field (doc 23 §5; FBR-23-01)

## MUST BECOME TRUE
- The Background Presentation Field spans the whole viewport (`position: fixed; inset: 0`, `z-index 0`) behind the
  rail, the topology and the instruments; every primary surface and the Access Field mount it.
- Layers (`components/field/FieldBackground.tsx`, `.field-bg` in `globals.css`): a static depth gradient; a static
  constellation texture (`::before`); **two nebular blobs** (46 / 40 vmax, radial gradients, `will-change: transform`)
  drifting ±2–3 vmax over 150 s / 190 s (`ease-in-out infinite alternate`); **one static haze** (64 vmax); a bounded
  breathing luminosity (`::after`, opacity only, 9 s); three static orbital traces; seven rare particles (SVG circles,
  opacity 0 → 0.55 → 0.15 → 0.7 → 0 over 96 s, staggered). Regime tints per surface class (unchanged from SF-02).
- Ambient motion is presentation only: `aria-hidden`, `pointer-events: none`, no attribute reflects any backend
  state, no check in any test reads it as meaning (doc 23 §5.3).
- Reduced motion: the global rule removes every animation (elements AND pseudo-elements); every layer stays, so
  depth remains (`tests/e2e/sf03-field.spec.ts` "reduced motion keeps every ambient layer (depth) and removes every
  animation": ≥ 5 animated nodes report `animationName: none`, ≥ 2 nebular layers remain displayed).
- Phone: the third trace group and the static haze are hidden (paint area), traces 720 px.

## MUST REMAIN IMPOSSIBLE
A distracting or wallpaper-like background (1–2: two blobs, ≤ 0.24 alpha, minutes-long); ambient motion implying
state (3); reduced motion losing depth (4); background cost harming interaction without adaptive reduction (5).

## PERFORMANCE PROOF (`SF-02/review/browser-evidence-2026-09-25/harness/perf-ab.mjs` method: real Chromium, CDP CPU
throttling ×4, rAF cadence median/p90 over 40 frames on the Access Field and the Workspaces Field, click actionability)
| Variant | Access rAF (median / p90) | Workspaces rAF (median / p90) |
|---|---|---|
| SF-02 final (reference) | 16.6 ms | 29 ms |
| SF-03 first draft: three 54–62 vmax animated blobs | **30.2 / 39.0 ms** | 23.5 / 45.0 ms |
| SF-03 without nebula | 16.0 / 22.4 ms | 16.5 / 23.6 ms |
| **SF-03 reduced (2 animated blobs 46/40 vmax + static haze)** | **16.3 / 22.6 ms** | **19.2 / 29.1 ms** |
| SF-03 reduced without background | 16.7 / 20.0 ms | 16.7 / 20.2 ms |
Degradation order applied (doc 23 §5.5): paint area and layer count first (third blob became static, blobs shrunk);
no semantic layer was touched. Particles and rail energy measured as noise-level. Final ambient cost at ×4 throttle:
≈ 0 ms on the Access Field, ≈ 2.5 ms/frame on the Workspaces Field.

## FALSIFIER / RED / GREEN
L3 spec "the living background spans the viewport behind rail and instruments, moves only ambiently, and is never
content" (fixed, ≥ viewport, animation present with duration ≥ 90 s, `pointer-events: none`, `aria-hidden`) and the
reduced-motion case above. RED before implementation (no `.nebula`), GREEN after; perf RED at the first draft
(30 ms) → GREEN after reduction.

## Result
PASS (measured). Evidence screenshots: WU-SF03.8 ("global living background", "reduced-motion equivalent").
