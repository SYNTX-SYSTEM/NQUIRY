# WORK UNIT REPORT
FIELD: SF-03 — NQIRY SYMBIOTIC SURFACE EVOLUTION
WORK_UNIT: WU-SF03.8 — Browser evidence on the integrated stack, visible defects, deep sweeps, review handoff

## Runtime (isolated, production build; SF-02 runtime untouched)
Compose project `nquiry-sf03-inspect` (recipe `infra/sf01/compose.yaml`, unchanged): fresh Postgres (no host port),
this tree's FastAPI, `next build` + `next start`, same-origin proxy `http://127.0.0.1:13300`
(`review/browser-evidence-2026-09-25/runtime/`, mounted read-only). Identities provisioned with the HD-3 DEV-ONLY
script (identity + credential only); every relation established THROUGH THE PRODUCT by
`harness/setup-scenario.mjs` (owner founds → adds the facilitator → facilitator frames → owner grants CHALLENGE session
control), twice: review names (`SF-03 Inspection`, WS `0e4aca27…`, CH `f59774b3…`) and STRESS names (104-character
Workspace name, 150-character Challenge title; WS `c7d64325…`, CH `e959a4ec…`).

## Harness
`harness/review-harness.mjs` = the SF-02 harness (30 regression states, unchanged checks) + the doc 23 acceptance
states: `human-question-field-wide-constellation` (19), `challenge-field-wide-constellation` (32),
`reciprocity-keyboard-focus-governance` (33), `workspace-field-wide-legibility` (34), `session-field-wide-frozen` (35),
`session-field-reduced-motion-depth` (36), `stress-challenge-long-labels-desktop/-wide/-phone`,
`stress-workspace-long-name-desktop` (37–40). New probes: `containment` (same as the stress spec: scroll overflow,
text rects inside frames, smallest font, fit), `identityCentred`, `instrumentColumns`, `ambient` (fixed, covers the
viewport, animated layer count, min cycle length, pointer-events), `railStable` (text box unchanged over 600 ms,
separator animation on the pseudo-element only, text transform none, min font), lifecycle label visibility/size,
`nodeOverlaps`. A third viewport `wide` (1600×900) joins desktop (1280×860) and Pixel 7.

## Runs
| Run | Tree | Result |
|---|---|---|
| run-1 | SF-03 before the last geometry repairs | 39/40: state 33 FAIL — the harness focused a non-focusable governance node (the facilitator holds no grant form); a harness defect. Screenshots also showed D-SF03-1 and D-SF03-2 below |
| run-2 | after D-SF03-1/2 | 39/40: state 8 `effective topology mode` stack on desktop (D-SF03-3) |
| run-3 | after D-SF03-3 | 38/40: states 8 and 39 with one real overlap each (D-SF03-4) |
| run-4 | after D-SF03-4 | 40/40 on the runtime; the mocked stress spec still found two desktop cases (core × node overlap on the stress Workspace; stress Challenge overflow) → D-SF03-5 |
| run-5 | final tree | **40 / 40** (30 SF-02 regression states + 10 doc 23 acceptance states; axe serious/critical 0, overflow 0, no unexpected HTTP, keyboard focus visible everywhere) |

## Visible defects found by the evidence and repaired at the root
| ID | Where | Symptom | First Broken Relation | Root repair | Guard |
|---|---|---|---|---|---|
| D-SF03-1 | run-1 states 32/38 | `SESSION_CONTROL_RIGH T` broke mid-token in the governance node's meta | TEXT WIDTH ESTIMATE → RENDERED WIDTH (capitals and underscores are ~22 % wider than the average glyph) | `textWidth()` weights capitals/underscores ×1.22, narrow glyphs ×0.52; sm frame maximum 192 px (estimator 170 inner) | stress spec + harness containment (no text escaping; frame width ≥ estimate) |
| D-SF03-2 | run-1 state 32 | the dashed "possible" spoke showed through the Open Session frame across its text (doc 23 falsifier 14) | TINTED FRAME → OPAQUE BASE (the tint was the only background) | every tinted node body = tint gradient over the opaque surface | screenshot (run-2 state 32); C |
| harness | state 33 | non-focusable target | — | governance proof disclosure summary is the keyboard entry | — |
| D-SF03-3 | run-2 state 8 (mode stack on desktop for ordinary content) | the last radius step of the collision loop left the width by 2 px → `fits:false` → stack | RADIUS STEP → WIDTH BOUND (checked before, not after) | a step that would leave the width is not taken; growth switches to the vertical axis | geometry probe (review Workspace content fits at 700) |
| D-SF03-5 | mocked stress spec after run-4 (desktop Workspace/Challenge) | the core's rendered frame (long title) was still an estimate; the mode decision ignored rendered frames; the derived height came from the circular layout only | ESTIMATED CORE → RENDERED CORE; DECISION → RENDERED FRAMES; NEED → ACTUAL LAYOUT | the topology measures the core too; the frames are owned by `FieldStage` and enter the mode decision (reported only in orbit mode: no loop); the needed height takes up to two passes with the actual (stretched) layout | stress spec 21/21; run-5 |
| D-SF03-4 | run-3 states 8 and 39 (one real overlap each) | rendered frames larger than the estimate near the width limit; the needed height was latched from an earlier empty layout (child reported before the parent's layout ref updated) | ESTIMATED FRAME → RENDERED FRAME; STORED NEED → DERIVED NEED | rendered frames reported by the orbits refine the layout; conservative estimates; needed height derived during render (pure); `_` break opportunity in meta tokens | run-4 states 8/39; dev probe: 0 overlaps on review + stress Workspace/Challenge at 1280/1600 |

## Doc 23 required evidence (§21) → states
desktop / phone / reduced-motion / real-stack screenshots (1–40; L7 specs keep their own PNGs) · Workspace Field (8,
10, 34, 39) · Challenge Field (11–13, 32, 37–38, 40) · Session Field (14–16, 35–36) · Human Question Field (17–22,
19 wide) · Owner position (7–10, 15, 20, 24, 34) · Facilitator position (11–14, 16–18, 22–23) · Participant position
(20–21) · Controller position (18, 22) · active HUMAN_ONLY (17–21) · post-commit re-read (15, 23–24) · proof
visibility (every state's proof checks) · governance visibility (11, 15, 32–33) · instrument constellation (19, 32,
34–35) · centred identity (32, 34–35, 37–39) · breadcrumb (32) · ambient Field (32, 36).

## Result
PASS: run-5 40/40 on the final tree (production build, real API, no interception). Seven root repairs came out of the evidence and the stress lane (D-SF03-1..5 + two probe artefacts); each is guarded by a spec or a harness check.
