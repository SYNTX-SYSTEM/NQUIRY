# WORK UNIT REPORT
FIELD: SF-03 — NQIRY SYMBIOTIC SURFACE EVOLUTION
WORK_UNIT: WU-SF03.5 — Instrument constellation and relational reciprocity (doc 23 §8, §11, §12; FBR-23-05)

## MUST BECOME TRUE
- `Planes` renders `.instruments` (a grid, not a flex column). Desktop (1100–1499 px): one column — active
  relation first (DOM order = semantic order). Wide desktop (≥ 1500 px): two columns `minmax(320px,1.15fr)
  minmax(300px,1fr)`; the active-relation instrument (`action` / `human` / `frozen` / `boundary`) holds column 1
  with primary gravity (`grid-row: 1 / span 4`); governance, proof and context compose in column 2 beside it (doc 23
  §11.3, §11.7). Tablet (861–1099 px): the topology takes the width on top (max 820 px), the instruments compose
  below in `repeat(auto-fit, minmax(300px, 1fr))`. Phone: the stack.
- Whole-surface composition (doc 23 §12): `.shell-main` max-width 1880 px (was 1280); the stage grid `minmax(700px,
  1.1fr) minmax(400px, 1fr)` (Session: `minmax(720px, 1.2fr)`); planes share the Field's depth language (gradient
  surface, 16 px radius, layered shadow, blue hairline) instead of flat cards.
- Reciprocity (`FieldStage`, `lib/field/reciprocity.ts`): one delegated `focus` / `blur` / `mouseover` / `mouseout`
  listener names the relation family under attention (`data-active-relation` = action | governance | proof | context)
  from the nearest `[data-relation]` (orbits carry `relationOfOrbit(kind)`: containment/capability/lifecycle → action,
  participation/governance → governance, evidence → proof; planes carry `relationOfPlane(kind)`). CSS responds on
  the family's plane (cyan border + glow), its nodes (cyan border) and its paths (opacity 1, stroke 2) with the
  relation-motion duration (220 ms). Keyboard focus and pointer hover set the identical attribute.
- Presentation only: no state, marker, capability, request or outcome changes (stress spec: hovering the Open-Session
  relation never posts; the unavailable reason stays; the outcome slot stays empty).

## MUST REMAIN IMPOSSIBLE
A default vertical card waterfall on wide desktop (25–26); horizontal composition destroying grouping (27: each
instrument keeps its own headings and content; only placement changes); hiding proof or governance (28–29: both stay
rendered and reachable in every mode); an available action unreachable (30); instruments dominating the Field (31:
the topology column keeps ≥ 52 % of the width; instruments sit in depth); dashboard grammar (32–34); proof or
governance visually disconnected from their relation (35–36: reciprocity connects them); hover implying state or
authority (37–38); focus behaviour inaccessible by keyboard (39).

## FALSIFIER / RED / GREEN
- L1 `tests/field/sf03-primitives.test.tsx`: orbits and planes carry `data-relation`; mapping functions.
- L3 stress spec "instrument constellation and reciprocity": two columns at 1600 px with governance and proof to the
  right of the action instrument (governance above proof), grant and proof reachable; keyboard focus on the grant
  control → `data-active-relation="governance"` and a changed governance border colour, cleared on blur; hover on the
  Open-Session node → `action`, zero POSTs, no outcome. RED before (no attribute, flex column), GREEN after.

## Result
PASS pending the full mocked lane (WU-SF03.7).
