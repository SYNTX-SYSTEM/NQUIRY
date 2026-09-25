# SF-05 — test surfaces, RED history and lane results
FIELD: NQUIRY Symbiotic Frontend Human Review Repair (doc 26)

## New / changed test surfaces
| Surface | Kind | Count | Pins |
|---|---|---|---|
| `tests/field/workspaces.test.ts` | L0 (new) | 7 | normalization by `workspace.id`, homonym distinguishers, no dedup by name/identity, stable order, ring segmentation without duplication |
| `tests/field/sf05-primitives.test.tsx` | L0 (new) | 9 | Plane semantic class; authority chain order/scope type; participation marks; provenance spine order; identifier tokens (separator breaks, copy, never a title); boundary classes + `Unavailable` grammar (no alert role); chamber head |
| `tests/field/fieldEvent.test.ts` | L0 (new) | 4 | event only after committed + re-read done + described relation; never for failures; stable id |
| `tests/field/sf03-primitives.test.tsx`, `sf04-primitives.test.tsx` | L0 (updated) | — | `data-semantic` on the plane; style regex tolerant of `--breath-phase` |
| `tests/e2e/sf05-field.spec.ts` | L3 (new) | 36 per run (desktop 18 + phone 18, 6 desktop-only cases skipped on the phone) | Workspace normalization (merge, homonyms, no collapse, two rings, columns, stability, narrow); chambers (classes/tones, authority chain SESSION scope + `data-held`, participation marks, spine, tokens `keep-all` + copy, boundary classes differ + no alert, frozen artifact chamber, confirmation chamber); commit resonance (gated re-read, scope text, pointer-inert, animation, proof line, leaves; denied → none; reduced motion step hold); breadcrumb (1280 one line, current complete, identity centred, logout clear, titles; 1024 long name); login (idle/attention/focus, pending verdict, denial boundary, reduced motion); Decision Surface (frame, chambers, NON_PROOF, no action in main, trace; denied boundary); intensification (breathing out of phase, encounter strengthens pulse + chamber, reduced motion) |
| `tests/e2e/sf04-field.spec.ts` | L3 (updated) | — | chamber law re-bound: faint ≤ 1 px low-alpha membrane, no outer shadow, translucent fill (doc 26 §17) |
| `playwright.sf01.config.ts` | config | — | phone project `testMatch: /sf0[1345]-/` |
| harness `SF-05/browser-evidence/harness/review-harness.mjs` | H | 68 states | SF-04 states 1–53 (Workspace check normalized; chamber law re-bound; grant event + confirmation checks added) + SF-05 states 54–68 |

## RED history
| Lane | RED | FBR | Root repair |
|---|---|---|---|
| L0 workspaces.test | distinguisher wording ("25 Sept, 08:25") | test wording vs Intl output | regex tolerant of the locale comma |
| L0 gates | "no role- or viewer-flag authority inference" on the members roster (`m.role === "Owner"`) | a role compared as a gate-shaped expression | `roleRelation()` lookup table (a role is a membership mark, never compared) |
| L0 gates | "no timer semantics" on `FieldEvent` (`setTimeout`) | HD-11 gate | the event's life is one CSS animation; dismissed on `animationend`; reduced motion: motionless step animation of the same length |
| L3 sf05 run 1 | login attention: animated particle opacity sampled | the drift animation owns per-particle opacity | attention on the GROUP's opacity (0.35 → 1) |
| L3 full run 1 | sf01 `granted by Root` text | chain spans without whitespace in the accessibility text | explicit spaces between chain roles and values |
| L3 full run 1 | sf04 chamber `borderTop 0px` | chambers now faint membranes (doc 26 §17) | SF-04 law re-bound (≤ 1 px, alpha < 0.2, no outer shadow, translucent) |
| L3 full run 1 | sf05 login focus while the pointer stayed on Login | test pointer state | move the pointer before focusing |
| L3 full run 1 | sf03 stress: route nodes clipped (`scroll:route-node`) | `min-width: 0` let a route node shrink below its status word | route nodes shrink through their label's ellipsis only |
| L3 subset 2 | sf03 stress: 64 / 597 px horizontal overflow | the current segment (a 150-character Challenge title) never compressed | proportional shrink with label ellipsis; current keeps ≥ 22ch; future status words visually hidden below 1500 px (still in the accessibility tree) |

| P run 1 · L7 run 1 | perf: every field +7 ms at ×4 throttle (variant K "no dense stars" restored 16.6 ms); real stack: f02/f03 accessibility specs RED (axe `color-contrast` serious on the Session field; a keyboard-reachable control without a visible outline) | (1) an SVG `<g>` with `opacity` renders through an offscreen buffer every frame; (2) the decision-entry marker (small type in `--blue-deep`) at contrast 3; (3) `.chamber input:focus-visible { outline: none }` | (1) per-particle `fill-opacity` (no group opacity); (2) decision-entry tone `--blue` (AA); (3) outline kept on chamber controls (doc 26 §34) |
| H run 1 | crashed at the SF-03 reciprocity state: `.plane[data-plane="governance"]` resolved to two elements (authority + participation chambers) | harness locator | `.first()` |

| H run-3 | 62/68: reason-text checks read the class word (harness reads re-bound to `.boundary-text`); wide stress route node clipped its status word; login-focus read mid-transition; tablet column threshold | (a) status words of future relations were visible ≥ 1500 px and could be clipped inside a shrinking route node; (b)/(c) harness calibration | future-relation status words accessibility-tree only on every desktop width (dashed edge + title carry them); harness waits for the transition; tablet threshold 3 columns |
| L3 full run 3 (load 21) | sf03 stress Workspace field: one node overlap | load-induced frame measurement race (passes 3/3 in isolation and in runs 2 and 4 at load ≤ 7) | recorded as OV (host load); no code change |

| H run-3 screenshots (58, 65) | Workspace overview with 18 Workspaces still a two-per-row waterfall at 1280 px (stack capsules 224 px wide in a 650 px column); the authority class tag wrapped mid-token inside the chain | capsule width vs column width; `overflow-wrap: anywhere` inherited by the tag | stack capsules 196 px (three per row; four on tablets); the tag is one token (`keep-all`, nowrap); route-node minimum 9ch |

| L3 final run 2 / H run-5 | sf04 compact phone overflow 39 px; five phone session states overflow 39 px, "text:chain-value tag authority" escaping | `white-space: nowrap` on the authority class tag could not fit a phone chamber | the class breaks only at its own underscores (`<wbr>`), never mid-word |
| P chain 5/6 | Workspaces field 27 ms and Challenge 20.7 ms at ×4 (SF-04: 16.6 / 16.8); variants C/G/I isolated the node breathing (scale) and the tall constellation | a transform-scale animation re-rasterizes every aura layer per frame; a 24-capsule stack breathing | breathing by opacity only; no breathing in the compressed constellation → run 6: 16.6 / 17.6 / 16.7 ms |
| H run-6 screenshot 58 | Workspace overview still one–two capsules per row at 24 Workspaces | `width: auto` made each capsule (li) as wide as its unwrapped text (up to 640 px) while its membrane stayed 196 px | capsules size to their membrane (`width: max-content; max-width: 196px`), phones alike |
| L3 final run 2 | sf03 "identity centred" `toBeVisible` timeout once | passes 3/3 in isolation; load-induced | recorded as OV |

| L3 final run 3 / H run-7 | phone Workspace overview 492 px overflow, compact Challenge 12 px, desktop columns | `width: max-content` on the capsule made the whole stage as wide as the longest unwrapped name (intrinsic min-content of the column flex) | `width: fit-content` (longest word floor, 196 px / viewport ceiling); phone rows may be one capsule wide (spec/harness thresholds: desktop ≥ 3 columns) |
| L3 final runs 2–3 | sf03 "identity centred": `toBeVisible` timeout once; `getByRole('link', 'nquiry')` matched two elements once — passes 5/5 in isolation and in every subset run | not reproducible outside the full parallel lane | recorded as OV (host load / parallel lane) |

| P chain 8 | Workspaces field (24-capsule constellation) 21.7 ms median at ×4 (variant C "no core layers" 16.3) | the core's transform animations (rings, membrane, orbit dot) over a 3 500 px stack | no core transform animations in the compressed constellation (the aura's opacity breath stays) → probe: 17.0 ms |

| H run-9 | state 51 (phone Session): core rings / membrane / micro-orbit no longer breathe; state 57 (wide overview): "≥ 4 columns" false | the stack core motion law silenced the core anatomy on phones (doc 25 §6 law broken for no measurable gain: 20.9 vs 21.7 ms); the wide threshold "4" was a run-8 artefact (a centred two-capsule last row counted as extra x-columns) | core anatomy motion restored in the constellation (only the node auras stay still); harness rule: desktop and wide ≥ 3 columns (same constellation column width) |

## Results on the final tree (chain 10, 2026-09-25 19:21–19:36)
| Lane | Result |
|---|---|
| L0 vitest | 287 / 287 (25 files; SF-05 adds workspaces 7 · sf05-primitives 9 · fieldEvent 4; sf03/sf04 primitives updated) |
| L5 | tsc 0 errors · eslint clean (React Compiler rules) |
| L3 mocked | 168 / 168 — desktop 1280 + Pixel 7, 2.7 min (sf05 36 cases incl. reduced motion; sf04 30; sf01/sf03/decision/etc. regression) |
| L7 real stack | F03 protected human question spec alone 2 / 2 (2.6 min, load ≈ 5) · full lane: 12 / 14 in 9.5 min (full parallel lane, load ≈ 6): the F03 protected human question spec (desktop + mobile) hit its 90 s budget while taking a screenshot, exactly as in chain 5; it passes alone 2 / 2 on this tree (11 min earlier) and in every isolated run since chain 6 — recorded as observation 7, not a regression |
| H harness | 68 / 68 (run-10; SF-04 states 1–53 + SF-05 54–68; runtime rebuilt from this tree, 30 same-named Workspaces in the scenario) |
| P perf-ab | access 16.7 ms · Challenge 16.9 ms · Workspaces overview 22.8 ms (30-capsule constellation) rAF median at ×4; hover 138 ms; trial click 315 ms (see FIELD_REVIEW.md §3) |
