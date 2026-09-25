# SF-05 PROOF MATRIX — doc 26 §41–§47 falsifiers · §58 acceptance gate
Lanes: L0 vitest (`tests/field/*`) · L3 isolated mocked browser (`tests/e2e/sf05-field.spec.ts` + SF-01/SF-03/SF-04/F01/F02/F03/decision/session-view/workspaces/auth regression, desktop 1280 + Pixel 7) · L7 isolated real stack · H review harness on the rebuilt runtime :13400 (SF-04 states 1–53 + SF-05 states 54–68) · P perf-ab (×4 throttle, variants A–K).

## §41 Workspace falsifiers
| # | FAIL if | Why it cannot occur | Proof |
|---|---|---|---|
| 1 | same `workspace.id` → several indistinguishable primary nodes | `normalizeWorkspaces` merges by id before geometry; the page never maps records 1:1 | L0 workspaces.test; L3 "three records → one node"; H 57–60 "no duplicate node keys" |
| 2 | same Workspace in two stacks | one entity per id, one ring position (segmentation slices, never copies) | L0 `segmentWorkspaces` (every entity once); L3 two rings, unique keys |
| 3 | normalization after layout | the layout input is built from `normalized` only | code path (`app/workspaces/page.tsx`); L0 |
| 4 | layout depends on duplicate entries | duplicates are removed at the producer | L3 merge test |
| 5 | long single vertical list where space exists | two containment rings on the orbit; stack capsules 196 px wide sized to their membrane (three per row in the desktop column, four on tablets) | L3 "≥ 4 columns", "nothing below the field box"; H 57–60 "columns ≥ 4" |
| 6 | label overflows node | SF-03 containment law unchanged | L3 sf03 stress spec; H containment checks |
| 7 | nodes collide | geometry collision loop + room-bounded organic offsets | L3 `nodeOverlaps = 0`; H "no node overlaps" |
| 8 | positions jump on stable re-render | deterministic geometry (hash offsets, stable input order) | L3 "positions equal on reload" |
| 9 | grouping invents semantic categories | rings are geometric segmentation of the server's own order; no category labels | design + L0 |
| 10 | dedup hides different Workspaces with the same name | key = id; homonyms stay and carry founding time · id8 | L0 + L3 "never collapsed" |

## §42 Right-side falsifiers
| # | FAIL if | Why it cannot occur | Proof |
|---|---|---|---|
| 1 | reads as a generic sidebar | one organ: nucleus header, chambers with glyph/title/marker/tone/contour on one surface | L3 organ + chamber suites; H 61–68 screenshots; review guide |
| 2 | authority and role look identical | `AuthorityRelation` (chain, blue, scoped) vs `relation-mark[data-relation-kind=owner|facilitator|contributor]` (dotted, muted) | L0 sf05-primitives; L3 "apart from role and participation" (computed styles differ) |
| 3 | proof and identifiers look identical | `ProvenanceSpine` (points + labels) vs `Identifiers` (mono tokens + copy) in separate sub-chambers | L0; L3 proof/identifiers test |
| 4 | questions and actions look identical | `question-surface` (serif, human seal) vs `chamber-action` (dashed top rule, cyan) | L3 chambers suite |
| 5 | all boundaries look like warnings | eight `data-boundary` classes with distinct edges/tones; no alert role | L0 boundary classes; L3 "boundaries are classed and differ visually" |
| 6 | action remains a form block unrelated to the field | action chambers carry the action glyph, marker (possible/not possible), reciprocity (`data-chamber-resonating`) | L3 encounter (sf04) + intensification test |
| 7 | proof remains raw text | spine + tokens | L3, H 65–67 "spine kinds" |
| 8 | chamber design obscures text | solid surfaces, no blur, type floors kept | H containment on every state; axe |
| 9 | reference image copied literally | no gauges, charts, watermarks, labels from the image; only contour/tone/depth qualities | review guide; H "no chart/gauge invented" (68) |
| 10 | right-side design leaks into the left field | left field CSS untouched except intensification; orbit grammar unchanged | L3 sf04 spec 30/30 regression |
| 11–12 | decorative charts / fake gauges | none exist | H 68 (0 canvas/chart/gauge) |
| 13–14 | motion distracts / causes layout shift | breathing = transform on auras (no layout), events fixed-positioned and pointer-inert | L3 intensification + event tests |
| 15 | reduced motion semantically incomplete | global rule + motionless event hold; every marker is text | L3 reduced-motion tests (login, event, session) ; H 67 |

## §43 Commit event falsifiers
| # | FAIL if | Why it cannot occur | Proof |
|---|---|---|---|
| 1 | event before canonical re-read | `deriveFieldEvent` requires `reconstruction === "done"` | L0 fieldEvent.test; L3 gated re-read test (event absent while held) |
| 2 | success after failed effect | requires `kind === "committed"` | L0; L3 denied → none |
| 3–4 | wrong scope / Challenge control as Session control | descriptions captured per relation at request time with explicit scope text | L3 "for this Challenge", not "for this Session"; H 12 (Session grant → "for this Session") |
| 5 | permanent, cluttering | one CSS animation life (6.8 s) → dismissed on `animationend` | L3 "leaves" (count 0 within 9 s) |
| 6 | blocks interaction | `pointer-events: none`, fixed | L3 computed pointer-events |
| 7 | loud motion | small nucleus/aura/8 particles, organic easing | review; P (no cadence impact) |
| 8 | replaces persistent proof | `command-outcome` persists as a quiet proof line | L3 "proof line stays" |
| 9 | source of truth | derived from the lifecycle after the re-read; read by nothing | design; L0 |
| 10 | generic "Success" | undescribed relation → no event | L0 |

## §44 Login · §45 Breadcrumb · §46 Decision Surface · §47 State
- §44: attention/focus are attributes; the dense group is bounded (10 stars); reduced motion removes all motion (L3 login suite, auth.spec regression; H 54–56).
- §45: one line at 1280 and 1024 with a long Workspace name; current state complete; identity centred; logout clear; titles keep compressed segments inspectable (L3 breadcrumb suite; H 66).
- §46: same components/test ids/data; NON_PROOF in the core; framed and chambered; no chart (L3 decision suite; `session-view.spec`/`decision.spec` regression; H 68).
- §47: no page reads a role/viewer flag as a gate (`gates.test.ts` "no role- or viewer-flag authority inference" GREEN); every state word comes from the projection (SF-01/SF-04 regression lanes; harness projection cross-checks).

## §58 acceptance gate — see FIELD_REVIEW.md (each line bound to a lane result).
