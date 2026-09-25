# WORK UNIT REPORT
FIELD: SF-03 — NQIRY SYMBIOTIC SURFACE EVOLUTION
WORK_UNIT: WU-SF03.4 — Orientation rail: centred NQIRY identity and symbiotic breadcrumb (doc 23 §9–§10; FBR-23-04, FBR-23-07)

## MUST BECOME TRUE
- `FieldFrame` header = one grid `minmax(0,1fr) auto minmax(0,1fr)`: the Relation Trace (left), the identity
  (centre, `justify-self: center`), the exit (right). The identity's centre is within 12 px of the viewport centre on
  desktop regardless of the trace length (stress spec); on ≤ 860 px the rail becomes `identity · exit` over `trace`.
- `components/field/Identity.tsx`: a designed mark (orbital glyph: ring, tilted orbit, cyan core, satellite dot) plus
  the serif wordmark `n·q·uiry` (q in cyan). In the rail it is the link to `/workspaces` with the accessible name
  "nquiry" (unchanged contract for F02/F03 lanes); on the Access Field it is a plain `role="img"` mark above the core
  (no link before an identity relation exists). It is product identity only: no core, no state, no authority, no
  commit meaning (doc 23 §10.2); no test reads it as state.
- The trace (`RelationTrace`, markup unchanged: `nav[aria-label="Inquiry position"]`, `aria-current`, status words)
  becomes the orientation rail: separators are short relation traces (`li + li::before`, a 22×2 px gradient bar) whose
  energy breathes on opacity only (14 s, staggered per segment); the current coordinate glows cyan (`text-shadow`);
  the text never moves (asserted: the current label's bounding box is identical 700 ms apart; `transform: none`,
  no animation on the text element; ≥ 13.5 px).
- Reduced motion: separator animation `none` (global rule).

## MUST REMAIN IMPOSSIBLE
Breadcrumb detached from the Field (19: same depth/border/glow language, energy bound to the rail's separators);
breathing harming readability (20: opacity of a pseudo-element only); characters moving (21); ambiguous current
position (22: `aria-current`, cyan glow, weight); identity as a left-aligned label on desktop (23); identity hiding
navigation (24: three-column grid, trace keeps `minmax(0,1fr)` and wraps).

## Optional reciprocity (doc 23 §9.4)
Not implemented: trace focus → Field layer highlight. The trace's established parents are other surfaces (a link
away), so a same-page reciprocity exists only for the current coordinate (the core), which is already the visual
anchor. Recorded as an open Case-2 option for the human.

## FALSIFIER / RED / GREEN
L3 spec "orientation rail" (2 cases, desktop + Pixel 7 where applicable): RED before (no `identity` test id; separator
`→` text), GREEN after. The SF-02 mocked/real specs that click the "nquiry" link keep passing (name preserved).

## Result
PASS pending the full mocked lane (WU-SF03.7).
