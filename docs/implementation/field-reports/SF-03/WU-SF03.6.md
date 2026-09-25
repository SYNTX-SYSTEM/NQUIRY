# WORK UNIT REPORT
FIELD: SF-03 — NQIRY SYMBIOTIC SURFACE EVOLUTION
WORK_UNIT: WU-SF03.6 — Surface evolution on the primitives (doc 23 §13, §14)

## What each surface now composes (every relation, capability, command and test id of SF-02 unchanged)
| Surface | Delta materialized |
|---|---|
| Access Field | centred plain identity mark in an `access-rail` above the core; stronger ambient presence (nebula, haze, particles); no topology before identity |
| Workspace Overview | `Topology layout={…}` from the access core + workspace nodes; the founding node stays visually distinct (`possible`, dashed cyan) from established workspace links; instruments (founding · proof) in the constellation grid |
| Workspace Field | challenges (ring 1) and members/authority (ring 2) distributed by content; long names expand frames or reflow; role (meta), governance capability (`You hold` governance node), authority binding and the possible Challenge relation keep distinct node states and markers |
| Challenge Field | fuller use of the width (700+ px column, elliptical breathing), session nodes readable (188 px frames, compact 160 px only when constrained), governance holders on the outer ring with the offset search, the constellation beside it |
| Session Field | all 13 lifecycle phases labelled (`lifecycleEmphasis`: full labels with ordinal for passed / current / next, compact names for later phases in low emphasis); participants and controllers on ring 2; Session topology column 720 px minimum; the active phase instrument first, governance and proof beside it on wide screens |
| Human Question Field | the human plane (input, own questions, count, completion) holds the first instrument column; governance (controller, participants) and proof compose beside it on wide desktop instead of below; participant / controller / owner / governance root remain distinct through node states (`human` / `governance`), markers and the human-position sentence |
| Frozen Question Field | the frozen plane holds the first column; no editable affordance (unchanged F03 markup); authors, verification and proof visible |
| Boundary / loading | unchanged markup on the stack mode (`mode="stack"` passed explicitly while no layout exists) |

## Protected semantics (doc 23 §3) — unchanged by construction
- No page changed a projection read, a command, a capability check, an authority display rule or a visibility rule;
  the only page-level changes are: (a) the `layout` input handed to `FieldStage`/`Topology` (the same node content
  the orbits render), (b) lifecycle node labels/emphasis, (c) removal of the `startDeg` prop (geometry decides).
- Human Question Law: `BurstCapturePanel` untouched; capture still only in QUESTION_GENERATION / ACTIVE
  HUMAN_ONLY; completion still explicit; frozen after commit + re-read (real-stack F03 specs).
- Owner ≠ superuser, role ≠ authority, control ≠ content visibility: the SF-02 harness states 14–24 re-run on
  the SF-03 tree (WU-SF03.8).

## FALSIFIER / RED / GREEN
Regression: the complete mocked lane (F01/F02/SF-01 42 + SF-03 21, desktop + Pixel 7) **102/102**; the isolated real
stack: WU-SF03.7. One SF-01 mocked assertion was updated for the architectural delta, not to accept a regression:
"the core is the visual centre of the topology" previously assumed the fixed 720 px square (`stage.x + 360`); it
now asserts the centre of the measured topology box (doc 23 §7.2).

## Result
PASS pending WU-SF03.7 (real stack) and WU-SF03.8 (evidence).
