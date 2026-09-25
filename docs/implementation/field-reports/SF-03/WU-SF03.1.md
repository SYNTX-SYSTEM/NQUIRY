# WORK UNIT REPORT
FIELD: SF-03 — NQIRY SYMBIOTIC SURFACE EVOLUTION
WORK_UNIT: WU-SF03.1 — Typography and semantic containment law (doc 23 §6; FBR-23-02)

## MUST BECOME TRUE
1. Frames follow content: `.node { width: max-content; max-width: <size maximum> }` — no fixed node width; the
   `.node-body` wraps inside (`overflow-wrap: anywhere` for tokens longer than the frame); the core is a content-sized
   rounded shape (`min 196 px`, `max-width 272 px`, `border-radius: 46% / 42%`) whose title is never clamped
   (`-webkit-line-clamp` removed) and never clipped.
2. Legible minimums as tokens: `--type-node 0.86rem` (13.8 px), `--type-node-sm 0.8rem` (12.8 px), `--type-meta
   0.74rem` (11.8 px), `--type-marker 0.74rem`; `.eyebrow` and `.mono` floors at 0.74rem (`max(0.85em, 0.74rem)`);
   every `0.7rem` / `0.72rem` role raised. The stress spec asserts no material text below 11.5 px.
3. Long technical identifiers wrap inside their instrument (`.plane .mono { overflow-wrap: anywhere; word-break:
   break-all }`); every plane has `min-width: 0` so the grid can never force text out.
4. Stronger hierarchy: core title 1.06rem serif; node labels 600 weight; low-emphasis lifecycle labels 500 weight in
   `--ink-soft` (colour and border carry gravity, never size or visibility).
5. The frame estimator (WU-SF03.2) uses the same maxima and metrics as the stylesheet, so geometry and CSS agree.

## MUST REMAIN IMPOSSIBLE
Text crossing a node or panel border (6–7); text made unreadably small to preserve geometry (8); overlap from long
content (9); silent clipping of material text (10); fixed frames when content needs expansion (11).

## FALSIFIER / RED / GREEN
- L3 stress spec `tests/e2e/sf03-field.spec.ts` "typography and containment" (Workspace Overview, Workspace Field,
  Challenge Field with nine Sessions and two long authority holders; desktop + Pixel 7) with a 104-character
  Workspace name, a 150-character Challenge title, a 52-character member name, 40-character authority meta and a
  long unavailable reason: for every `.node-body`, `.core`, `.plane` and trace item, (a) no scroll overflow beyond 2 px,
  (b) every label/meta/marker/title/state/heading/identifier/tag rect inside its frame, (c) no frame overlapping
  another frame or the core, (d) no horizontal page overflow, (e) no material text < 11.5 px, (f) on desktop the layout
  reports `fits`. Plus "a long core title is fully rendered (never clamped or clipped)".
- RED run 1 (9 failures) → roots: (1) `.eyebrow` 11.2 px and `.mono` 11.15 px below the floor → tokens raised;
  (2) governance meta `SESSION_CONTROL_RIGHT` broke mid-token in a 154 px sm frame → sm maximum 176 px and the
  estimator's meta metric 6.4 px/char; (3) geometry roots recorded in WU-SF03.2; (4) two probe artefacts (sub-pixel
  scroll rounding; hidden content of a closed `<details>` reports a rect) → probe tolerance 2 px and closed proof
  depth skipped — these were measurement defects, not Field defects, and are recorded as such.

## Result
PASS pending the full mocked lane and the browser evidence (WU-SF03.7/8).
