# WORK UNIT REPORT
FIELD: SF-04 — NQUIRY SYMBIOTIC FIELD ORGANISM
WORK_UNITS: SF04-WU-05 Contextual Semantic Organ · WU-06 Traversal Trace · WU-07 Atmospheric Medium · WU-08 Encounter cascade · WU-09 Responsive redistribution

## WU-05 — Contextual Semantic Organ (doc 25 §10) — `FieldStage.tsx` (`Planes`, `Plane`), pages, `globals.css`
`Planes` renders ONE `aside.organ[aria-label="Active semantic context"][aria-live="polite"]`: `.organ-bridge`
(decorative relation from the field) → `header.organ-header` (eyebrow "Grown from" · `.organ-title` = the core's
identity · `.organ-state` = the canonical state in words, passed by the page from the same projection the core
renders) → `.organ-body.instruments` with the instruments as chambers: `section.plane.chamber[data-plane][data-chamber]`
(action/human/frozen/boundary → primary; governance → relational; proof/context → logic). The organ's surface is a solid
membrane tone with the membrane border and one outer shadow (full-size gradients and an inset blur rasterized per
pixel over the whole organ — measured 2.5× slower full-page capture on phones — and were removed). Chambers share
that surface (transparent background, no border, no shadow), are divided by membranes (`.plane + .plane::before`) and
carry their relation family as an edge accent (`::after`, `--chamber-tone`) — not stacked cards. The organ emerges
once (`organ-emerge` 640 ms, `--ease-settle`). Relation tokens `[data-relation-key]` mirror field entities inside the
chambers (Challenge: controllers; Workspace: members; Session: controllers + participants). `.plane`, `data-plane`
and `.instruments` are kept as the SF-01/SF-03 contract hooks (wide two-column composition ≥ 1500 px unchanged).
The organ has no state attribute: it displays and hosts; it never selects (falsifier 6).

## WU-06 — Traversal Trace (doc 25 §11) — `components/field/RelationTrace.tsx`, `globals.css`
Route nodes: `li.route-node[data-coordinate][data-status]` with a `.route-membrane` capsule (current: active
membrane, cyan wash, `aura-breathe`; established: quiet; possible/unavailable: dashed); the trace between nodes is the
SF-03 `rail-energy` shimmer bar (`::before`, opacity only). Hover/focus-within brightens a node's membrane. Phone:
the trace compresses to the current node; `button.trace-chip-toggle[aria-expanded][aria-controls]` (+N / −) reveals
the whole route (`data-expanded` on the nav; projection-local UI state). SF-01 contract kept: `nav[aria-label=
"Inquiry position"]`, `ol`, links only for established parents, status words outside the link, `aria-current`.

## WU-07 — Atmospheric Medium (doc 25 §12) — `FieldStage.tsx` (`Topology`), `globals.css`
`.stage-atmosphere` (first child of the field box, `aria-hidden`, pointer-events none): `.pressure-zone` (radial
pressure around the core; static presence — a second large breathing layer measured ~10 ms/frame at ×4 throttle,
the breath lives on the core's aura) and `.resonance-wash` (inert at rest; on encounter it appears and leans
toward `--vec-x/--vec-y`, 420 ms in / 900 ms settle). On phones the medium is fixed behind the constellation. The
SF-03 background field (`.field-bg`) stays the ambient layer beneath (unchanged; nebula cost unchanged).

## WU-08 — Encounter cascade (doc 25 §13) — `FieldStage.tsx`, `globals.css`
`ProjectedFieldState` (`lib/field/projection.ts`: hovered/focused node id, active relation family, hovered context
relation id, unit vector) is the stage's view model. One delegated focus/blur/mouseover/mouseout listener writes
`data-active-relation` (SF-03 family reciprocity, unchanged), `data-hover-key`, `data-encounter` (hover | focus |
context), `--vec-x/--vec-y/--vec-on`, and marks every counterpart of the encountered key with `data-resonating`
(`li.node`, `g.relation`, `[data-relation-key]`) and its chamber with `data-chamber-resonating`. The stylesheet renders
the cascade: node aura + membrane (280 ms in / 420 ms out) → relation current → core lean → organ token + chamber
preview (900 ms settle) → atmosphere wash. Keyboard focus produces the identical attributes (focus parity);
`:focus-visible` rings use `--field-focus-ring` on node controls, trace links, chip and organ controls. Nothing is
requested or selected (proven: no non-GET request during hover; no outcome).

## WU-09 — Responsive redistribution (doc 25 §15) — `globals.css`
| Class | Width | Composition |
|---|---|---|
| desktop | ≥ 1200 px | field box left, organ attached right (bridge); wide ≥ 1500: chambers in two columns |
| tablet | 768–1199 px | field oval on top (≤ 820 px), organ attached below (≤ 960 px), chambers auto-fit |
| mobile | < 768 px | breathing constellation: the core (bounded ≤ 272 px, layers bounded), then each orbit as a wrapping cluster of capsules in semantic order; the organ as a membrane sheet (32 px top radii, edge to edge); the trace as a chip |
| compact | < 390 px | tighter capsules, core ≤ 248 px, same type floors |
The SF-03 threshold weakness (two columns 700 + 400 px demanded ≥ 1124 px inside a 1100–1199 px viewport) is closed:
the desktop composition starts at 1200 px (proven at 1150 and 1024). Stack mode on any width (content that cannot
fit the ring) is the same constellation, never rows.

## RED → root repair (mocked lane runs 1–4)
| Run | RED | First Broken Relation | Root repair |
|---|---|---|---|
| 1 | tablet 1150/1024/800: organ beside, not below | `.organ { grid-column: 2 }` declared after the tablet rule (cascade order) | stage-scoped tablet selector `.field-stage .organ { grid-column: 1 }` |
| 1 | phone: 319–403 px horizontal overflow | constellation nodes `position: relative` kept the orbit offsets `left/top: calc(50% + --x/--y)` | `position: static` in the constellation (phone + stack) |
| 1 | desktop trace count 1 | test read the loading trace before the projection (test-side) | wait for the core |
| 2 | phone: 17–100 px overflow | the stage flips to stack on phones (rendered capsule frames), `stack .core { max-width: none }` stretched the nucleus and its percentage-inset layers past the viewport | stack core bounded to `--core-max`; phone layer insets reduced |
| 3 | 360 px: 6 px overflow | 272 px core × 1.36 aura > 360 | compact `--core-max: 248px` |
| H 1–2 | wide Session/Workspace fields decided the constellation | ESTIMATE → MODE (scaled mass estimate + full organic offsets) | estimate follows the padding law; organic offsets bounded by room (`layoutField`) |
| H 1–2 | phone overflow growing with time | ROTATING LAYER → SCROLLABLE OVERFLOW (micro-orbit) | dot on a motion path; static layer |
| L3 4 | stress Workspace field overflow verdict | NEED ← BOX HEIGHT (oscillation) | need = f(width, content, frames), grown until the layout fits (≤ decision stage) |
| L7 1–2 | F03 protected flow over its 90 s budget | ENCOUNTER → CONTEXT IDENTITY → TOPOLOGY/ORBIT RE-RENDER (geometry recomputed per hover) | stable `MeasureContext` value; memoized geometry derivation |
| L7 3–6 | phone F03 flow still over budget (full-page captures 5–12 s) | ORGAN SURFACE GRADIENTS → PER-PIXEL RASTER over the whole membrane | solid organ surface + outer shadow |
