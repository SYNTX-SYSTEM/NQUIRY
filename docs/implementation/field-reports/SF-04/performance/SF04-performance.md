# SF-04 — WU-12 performance (doc 25 §19: measured, never assumed)
FIELD: SF-04 — NQUIRY SYMBIOTIC FIELD ORGANISM
Method: `browser-evidence/harness/perf-ab.mjs` (the SF-02/SF-03 probe extended): real Chromium, CDP CPU throttling
×4, a `next dev` page server (:3341) whose `/api/*` calls are forwarded to the isolated SF-04 inspection API (:13400),
rAF cadence (median / p90 of 40 frames) on the Access Field, the Workspaces Field and the Challenge Field (the
organism's densest desktop surface with currents, auras, atmosphere and organ), plus click/hover actionability.
Variants inject CSS to isolate one cost at a time. Shared host; the load average is recorded with each run.

## Run 1 (final tree; load ≈ 5)
| Variant | Access rAF | Workspaces rAF | Challenge rAF | login click | hover | trial click |
|---|---|---|---|---|---|---|
| A full (shipped) | 16.7 / 17.4 ms | 31.6 / 54.0 ms | 16.9 / 19.8 ms | 168 ms | 184 ms | 357 ms |
| B no background | 16.7 / 17.3 | 16.9 / 19.1 | 16.8 / 17.2 | 145 | 154 | 319 |
| C no core layers | 16.6 / 20.8 | 21.4 / 25.7 | 16.6 / 17.3 | 269 | 150 | 330 |
| D no currents | 16.7 / 17.3 | 32.7 / 42.7 | 16.1 / 21.7 | 165 | 184 | 320 |
| E no node auras | 16.7 / 17.1 | 24.6 / 28.4 | 18.3 / 22.6 | 190 | 145 | 290 |
| F no atmosphere | 16.6 / 17.0 | 22.0 / 25.3 | 21.0 / 28.7 | 159 | 184 | 357 |
| G no organism animation | 16.7 / 17.2 | 26.0 / 41.8 | 16.6 / 17.5 | 148 | 127 | 305 |
| H static everything | 16.6 / 17.2 | 16.6 / 17.2 | 16.6 / 17.2 | 116 | 91 | 112 |
Reference: SF-03 shipped 16.3 (Access) / 19.2 ms (Workspaces).

## Reading
- The Access Field and the Challenge Field (the organism with currents, three breathing core layers, node auras,
  atmosphere and the organ) hold the 60 Hz cadence at ×4 throttle (16.7–16.9 ms median; p90 ≤ 19.8 ms); relation
  currents cost nothing measurable (D ≈ A).
- The Workspaces Field is the one surface where the organism's breathing layers and the ambient background overlap
  the same region of a short page: 31.6 ms median / 54 ms p90. Removing the background alone restores 16.9 ms; removing
  the core layers, the auras or the atmosphere each recovers 7–10 ms — the cost is the compositing of several large
  translucent, animated layers over each other on that surface, not any single organ. Interaction stays responsive
  (login 168 ms, hover 184 ms, trial click 357 ms at ×4 throttle).
- Run 2 (an attempt to promote the breathing layers with `will-change`, load 4.5 → 8 during the run) was dominated
  by host noise (every variant, including the fully static one, moved by 5–10 ms) and proved nothing; the change was
  reverted so the reviewed tree is the proven tree. Recorded as a human item / follow-up: an adaptive reduction on
  the workspace-access surface (e.g. the ambient nebula paused while the organism breathes, or one fewer breathing
  layer on short pages), to be measured on a quiet host.

## Run 4 (final tree, after the two repaint repairs; load ≈ 5)
| Variant | Access rAF | Workspaces rAF | Challenge rAF | login click | hover | trial click |
|---|---|---|---|---|---|---|
| A full (shipped) | 16.8 / 17.3 ms | 17.2 / 20.7 ms | 16.7 / 17.4 ms | 125 ms | 89 ms | 149 ms |
| B no background | 16.6 / 17.2 | 16.6 / 17.5 | 16.7 / 17.1 | 95 | 70 | 209 |
| C no core layers | 16.7 / 17.0 | 16.6 / 17.4 | 16.7 / 17.3 | 124 | 71 | 190 |
| D no currents (pulses) | 16.7 / 17.4 | 22.1 / 27.7 | 16.6 / 17.1 | 132 | 71 | 177 |
| E no node auras | 16.8 / 17.1 | 16.7 / 18.5 | 16.7 / 17.2 | 123 | 81 | 204 |
| F no atmosphere | 16.7 / 17.1 | 16.6 / 18.9 | 16.8 / 17.4 | 116 | 102 | 189 |
| G no organism animation | 16.6 / 17.1 | 16.7 / 17.6 | 16.7 / 17.4 | 124 | 71 | 176 |
| H static everything | 16.8 / 17.0 | 16.7 / 17.3 | 16.7 / 17.3 | 135 | 68 | 96 |
Repairs between run 1 and run 4 (both measured, doc 25 §19): (1) the relation current was an SVG `stroke-dashoffset`
animation — every dash step repainted the stage-sized SVG (variant D in run 1: −10 ms on the Workspaces field); it is
now one small HTML pulse per non-latent relation on a CSS motion path (transform on its own compositor layer; the SVG
is static). (2) The pressure zone breathed as a second large radial gradient over the aura and the nebula (variant F
in run 1: −15 ms); it is now static presence, the breath lives on the core's aura. Result: every field at the 60 Hz
cadence; interaction back in the SF-03 range. The remaining Workspaces variance (D 22 ms = A without pulses, within
noise of the run) is not reproducible across variants.

## Run 5 (final tree, all three repairs; load ≈ 5)
| Variant | Access rAF | Workspaces rAF | Challenge rAF | login click | hover | trial click |
|---|---|---|---|---|---|---|
| A full (shipped) | 16.6 / 17.4 ms | 16.6 / 19.2 ms | 16.8 / 17.8 ms | 122 ms | 89 ms | 184 ms |
| H static everything | 16.7 / 17.3 | 16.6 / 17.2 | 16.6 / 17.1 | 93 | 80 | 69 |
(B–G within 0.3 ms of A on every field: no single organism layer is measurable any more.)

## Real-stack flow cost (WU-12, doc 25 §19) — the third measured repair
The isolated real-stack lane's F03 protected spec (7 full-page phone screenshots, ~100 actions, 90 s budget) stayed
over budget on the phone project after the two repaint repairs (desktop passed alone in 1.3 min). Its Playwright
trace showed the captures at 5–12 s each (SF-03 tree: 1.2–1.9 s). Full-page capture cost on the frozen Session page
(Pixel 7, SF-04 runtime, min/max of 3):
| Variant | capture |
|---|---|
| SF-03 baseline (runtime :13300) | 1.19 / 1.31 s |
| SF-04 as shipped before the repair | 2.76 / 3.76 s |
| no atmosphere · no core layers · no node auras · no route membranes · no background · all animations off | 2.7 – 3.5 s (no single layer) |
| organ without gradients | 1.40 / 1.59 s |
| organ solid + outer shadow, no inset blur (shipped) | 1.16 / 1.27 s |
Cause: the organ's radial + linear gradients and inset blur rasterize per pixel over the whole 412 × 1500 px membrane
on every capture (and on every scroll repaint on real phones). Repair: a solid membrane surface with the membrane
border and one outer shadow. Result: the isolated real-stack lane 14 / 14 in 8.3 min (F03 protected spec 1.4 / 1.3 min
on desktop / phone; SF-03 final: 6.9 min at load 4).

## Motion budget (doc 25 §18.5, §19)
Breathing 9–18 s, current drift 9 s (one pulse), micro-orbit 48 s, hover 280 / 420 ms, organ emergence 640 ms once,
stabilisation 900 ms; no `filter: blur` over large areas, no DOM particle field, no timers, no JS animation loop.
