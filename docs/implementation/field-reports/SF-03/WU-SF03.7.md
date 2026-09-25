# WORK UNIT REPORT
FIELD: SF-03 — NQIRY SYMBIOTIC SURFACE EVOLUTION
WORK_UNIT: WU-SF03.7 — Proof ladder, regression protection, performance

## Lanes (commands unchanged from SF-02)
```
(cd apps/web && npx vitest run && npx tsc --noEmit && npx eslint .)                       # L0 / L5
(cd apps/web && npx playwright test --config playwright.sf01.config.ts --output=<scratch>)  # L3 isolated mocked (:3301, dead proxy; mobile project now matches sf01-* and sf03-*)
bash scripts/run_sf01_real_stack.sh                                                        # L6/L7 isolated real stack (run ALONE)
```

## Results on the SF-03 tree
| Lane | Result | Notes |
|---|---|---|
| L0 vitest | **232 / 232** (SF-02: 219; +11 geometry, +8 SF-03 primitives; −6 superseded unit-circle tests) | RED first for every new module (absent module / absent behaviour) |
| L5 tsc / eslint | 0 / clean | React Compiler rule caught one render-time ref access (moved into an effect) |
| L3 mocked, desktop + Pixel 7 | **102 / 102** (81 SF-02 regression + 21 SF-03), final tree | run 1 of the SF-03 spec: 9 RED (real defects: font floors, sm frame width, ring minimum radius, width-exhausted growth, mode/measurement loop; 2 probe artefacts) → run 2: 4 → run 3: 1 (phone md rows) → GREEN; after the evidence-driven D-SF03-4/5 repairs the stress spec found two more desktop cases (core × node overlap, overflow) → GREEN on the final tree |
| L7 isolated real stack, final tree | **14 / 14** (6.9 min) | see the re-run table below for the earlier budget timeouts |
| Performance (perf-ab, ×4 CPU throttle) | Access 16.3 ms · Workspaces 19.2 ms rAF median (SF-02: 16.6 / 29) | WU-SF03.3 |

## L7 re-runs (same lane, same spec; host load from other Fields' containers varied)
| Run | Tree | Host load (1 min avg at start) | Result |
|---|---|---|---|
| 1 | before D-SF03-1..5 | 10–17 | 12/14 (F03 protected desktop + mobile: 90 s budget, 257/338 actions completed, no failed assertion) |
| 2 | after D-SF03-1/2 | ~9.5 | 12/14 (same two timeouts) |
| 3 | after D-SF03-3 | ~9.3 | 13/14 (desktop timeout only) |
| 4 | **final tree** (after D-SF03-4/5) | ~4 | **14/14** (6.9 min) |
The spec's budget is marginal on this shared host; on the final tree at ordinary load it passes. Recorded as OV-4.

## Regression protection (doc 23 §20 falsifiers 51–57)
Every SF-02 contract remains: F01/F02 mocked specs (39), SF-01 mocked spec (42, one assertion updated for the
architectural delta — core centre = topology centre instead of a fixed 720 px square), the F02/F03/SF-01 real-stack
specs (14 / 14 on the final tree; the budget note above), the SF-02 harness states 1–30 re-run as part of the SF-03 harness
(WU-SF03.8). The manual behaviour of the SF-02 human review (open Session, grant, transitions, capture, own-only
visibility, completion, frozen set, denied / rejected / not found / unknown / loading) is exercised by the same
harness path.

## Root repairs made in this Work Unit's RED cycles (First Broken Relation → root)
| Symptom | FBR | Root repair |
|---|---|---|
| 9 SF-03 stress cases RED | TYPE FLOOR → TOKENS (eyebrow 11.2 px, mono 11.15 px) | `--type-*` tokens, `.mono` floor |
| governance meta broke mid-token | FRAME MAXIMUM → CONTENT NEED | sm max 176 px + estimator metric |
| Workspace stress `overflow` | RING MINIMUM → CORE CORNER (over-conservative) | soft minimum + collision loop |
| 9 Sessions overlap at 700 px | WIDTH EXHAUSTED → RADIUS GROWTH | growth into the vertical axis; compact frames; stack as compacted representation |
| node "not stable" (hover timeout) | MEASURED BOX → MODE → BOX (loop) | mode from the viewport class's decision stage; height need from width alone |
| phone md rows 144 px | COMPACT RULE → STACK | compact max-width lifted in the stack |
| SF-01 order assertion | FIXED SQUARE ASSUMPTION | assertion on the measured topology centre |

## Result
PASS on the final tree: L0 232/232 · L5 clean · L3 102/102 · L7 14/14 · evidence run-5 40/40 · perf 16.3 / 19.2 ms rAF at ×4 throttle. Every RED on the way is recorded above with its First Broken Relation.
