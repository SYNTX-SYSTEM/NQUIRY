# SF-04 — test surfaces, RED history and lane results
FIELD: SF-04 — NQUIRY SYMBIOTIC FIELD ORGANISM

## Lanes (commands unchanged from SF-02/SF-03)
```
(cd apps/web && npx vitest run && npx tsc --noEmit && npx eslint .)                        # L0 / L5
(cd apps/web && npx playwright test --config playwright.sf01.config.ts --output=<scratch>)   # L3 isolated mocked (:3301, dead proxy; mobile project matches sf01-/sf03-/sf04-)
bash scripts/run_sf01_real_stack.sh                                                         # L7 isolated real stack (run ALONE)
EVIDENCE_RUN=run-N node docs/implementation/field-reports/SF-04/browser-evidence/harness/review-harness.mjs <ws> <ch> <stressWs> <stressCh>   # H (runtime :13400)
```

## New / changed test surfaces
| Surface | Kind | Count | What it pins |
|---|---|---|---|
| `tests/field/projection.test.ts` | L0 (new) | 15 | RULE-W/B/R/T, provenance, no tension, guard (doc 25 §21.11 falsifiers 1–3, 7, 11–13) |
| `tests/field/geometry.test.ts` › "SF-04 living field entity geometry" | L0 (+4) | 15 total | band radii order, deterministic bounded organic offsets (no random), mass never a band, no overlaps |
| `tests/field/sf04-primitives.test.tsx` | L0 (new) | 16 | core anatomy + text, node anatomy + provenance on the DOM, relation groups (curved, classes, direction, no tension, no `<line>`), arc determinism/bound, organ (one aside, live region, header, chambers in order, tokens, no state), trace route nodes + chip, atmosphere layers + rest state |
| `tests/field/sf03-primitives.test.tsx` | L0 (updated) | 8 | `nodeContent(n, kind)`; `<path class="path path-base">` instead of `<line>`; `plane chamber … data-chamber` (SF-04 delta, annotated) |
| `tests/field/primitives.test.tsx` › SF-02 Orbit nodes | L0 (updated) | — | path count on `class="path path-base"` |
| `tests/e2e/sf04-field.spec.ts` | L3 (new) | 30 per run (desktop 22 + mobile 8 effective; 6 desktop-width cases skipped on mobile) | core breathing bounded (≤ 2.4 % sampled live) and layered; reduced motion; entity attributes + rule chains; motion by class (drift 5–12 s, reverse, alternate, breathe, latent none, no lines); Session context/reciprocal; encounter cascade (pointer: attributes, vector, resonance of node/current/token/chamber, wash, core lean, no request; keyboard parity + focus ring; token → entity); organ (live region, header = core, chambers not cards, request surfaces unchanged); trace (desktop route nodes; phone chip expand); responsive 1600/1280/1200/1150/1024/800 (organ beside/below, containment), phone constellation + membrane sheet, compact 360; atmosphere; reduced motion keeps meaning |
| `tests/e2e/sf03-field.spec.ts` | L3 (updated) | 21 | phone: capsules (≥ 40 px, inside the viewport) instead of ≥ 250 px rows (doc 25 §15.4); probe: material-content scroll metric (decorative layers excluded) and chip-compressed route nodes excluded |
| `playwright.sf01.config.ts` | config | — | mobile project `testMatch: /sf0[134]-/` |

## RED history (every RED → First Broken Relation → root repair)
| Lane | RED | FBR | Root repair |
|---|---|---|---|
| L0 | `projection.ts` absent (15 RED) | — | module written (WU-01) |
| L0 | geometry SF-04 describe (4 RED) | — | bands/mass/offsets (WU-03) |
| L0 | sf04-primitives node anatomy slice | test sliced from the SVG group's `data-key` | slice from `class="node" data-key` |
| L0 | SF-02/SF-03 assertions on `<line>` / `class="plane"` | architectural delta | assertions updated, annotated |
| L3 run 1 | tablet 1150/1024/800: organ beside | cascade order of `.organ { grid-column }` | `.field-stage .organ` in the tablet rule |
| L3 run 1 | phone 319–403 px overflow | constellation nodes kept orbit offsets | `position: static` in constellation/stack |
| L3 run 1 | desktop trace count 1 | test read the loading trace | wait for the core |
| L3 run 2 | phone 17–100 px overflow | stack-mode core `max-width: none` stretched the percentage-inset layers | stack core bounded; phone layer insets |
| L3 run 3 | 360 px: 6 px overflow | 272 px core × 1.36 aura | compact `--core-max: 248px` |
| L3 full run 1 | sf03 containment ×6, sf03 phone, sf01 mobile trace ×4 | probe `scrollWidth` inflated by decorative layers; `display:none` route nodes left the a11y tree | probes measure material content; collapsed route nodes visually hidden (a11y tree kept) |
| L3 full run 2 | sf03/sf04 mobile containment ×5 | probes treated 1 px compressed route nodes as frames | probes skip frames ≤ 1 px |
| H run-1 | 12 FAIL: SF-02 phone-row checks (D3), route-node scroll, chip hidden-count, organ state prefix, chamber inset wash; wide Session "fits" | superseded SF-02/SF-03 checks (constellation, chip a11y tree, inset wash); geometry estimate | harness checks re-bound to doc 25; estimate follows the padding law |
| H run-2 | 5 FAIL: wide Workspace/Session "fits" ×3; stress phone overflow 23 px; encounter wash/lean read too early | organic offsets exceeded the decision stage; rotating micro-orbit layer; transition sampled once | offsets bounded by room; dot on a motion path; harness samples until settled |
| L7 run 1–2 | F03 protected real-stack spec (desktop + mobile): 90 s budget exceeded at the first full-page screenshots (session DRAFT), load 7–10 | CONTEXT VALUE IDENTITY → RE-RENDER → GEOMETRY RECOMPUTE: `FieldStage` created a fresh `MeasureContext` value on every encounter state change, so every hover/focus re-rendered `Topology` (up to 7 × 8 `layoutOnce` passes) and every `Orbit`; the real-stack flow (hundreds of pointer actions) paid it on every action | memoized context value; the geometry derivation memoized on (content, measured box, frames) |
| L7 run 3 + P | CPU-bound real-stack specs 2.5–3.4× slower than on the SF-03 tree (f02/f03 accessibility, inquiry context); perf-ab Workspaces 34 ms | CONTINUOUS REPAINT: the SVG current layer (`stroke-dashoffset` animation) repainted the whole stage-sized SVG every frame (variant D −10 ms); a second large breathing gradient (pressure zone) composited over the aura and the nebula (variant F −15 ms) | currents as HTML pulses on CSS motion paths (compositor transform); pressure zone static |
| L7 runs 4–6 (F03 protected spec alone, phone) | 90 s budget exceeded although every action costs what it costs on SF-03; the Playwright trace shows 7 full-page screenshots at 5–12 s each (SF-03: 1.2–1.9 s) | FULL-SIZE GRADIENT SURFACE: the organ's radial + linear gradients and inset blur rasterize per pixel over a 412 × 1500 px membrane on every capture (variant V23 "no gradients": 3.1 s → 1.4 s; V27 solid + outer shadow: 1.16 s = SF-03 baseline) | solid organ surface; depth from the membrane border and the outer shadow |
| L3 full run 4 | sf03 stress Workspace field: `data-fit="overflow"` at 1280 (mode orbit) | NEED ← BOX HEIGHT: the height derivation started its trials at the box's current height, so a grown box lowered its own need and shrank again (oscillation between 1126 and 1366 px) | the need is derived at exactly the needed height (width + content + frames only), grown in bounded steps up to the tallest decision stage |

## Results on the final tree
| Lane | Result |
|---|---|
| L0 vitest | 267 / 267 (SF-03: 232; +15 projection, +4 geometry, +16 SF-04 primitives) |
| L5 tsc / eslint | 0 / clean |
| L3 mocked (desktop + Pixel 7) | 132 / 132 (run 8, final tree) — earlier runs: 23+7 RED (SF-04 spec alone), 121, 127, 131, 132, 132, 132 |
| L7 isolated real stack | 14 / 14 (run 8, final tree, 8.3 min, load ≈ 4.6) — runs 1–3 (full lane): 12/14 (F03 protected spec over budget at load 7–13); runs 4–7 (spec alone): desktop 1.3–1.4 min PASS, phone over budget → trace → organ-surface repair |
| H harness (states 1–53) | 53 / 53 (run-7, final tree) — runs 1–6: 41, 48, 53, 53, 53, 53 |
