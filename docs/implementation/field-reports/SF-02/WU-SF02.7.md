# WORK UNIT REPORT
FIELD: SF-02 — NQIRY SYMBIOTIC INTERACTION FIELD (materialization of doc 22)
WORK_UNIT: WU-SF02.7 — Proof ladder: unit, static, isolated mocked browser, isolated real stack; defects found by proof and repaired at the root

## Mission
Run every lane on the SF-02 tree, strictly in isolation (SF01-HD-2: own compose project, no host ports, fresh
DB) and record every RED honestly with its First Broken Relation and root repair. No lane result is a Field
claim; the human review is.

## Lanes and commands
```
(cd apps/web && npx vitest run && npx tsc --noEmit && npx eslint .)                 # L0 / L5
(cd apps/web && npx playwright test --config playwright.sf01.config.ts --output=<scratch>)   # L3 isolated mocked (:3301, dead proxy)
bash scripts/run_sf01_real_stack.sh                                                  # L6/L7 isolated real stack (project nquiry-sf01)
```
After every `next dev` lane: remove `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`, restore `next-env.d.ts`.

## Run history (chronological, every RED disclosed)
| Lane | Tree | Result | Classification |
|---|---|---|---|
| L0 vitest | SF-02 after WU-SF02.6 | 219/219 | — |
| L3 mocked run 1 | same | **78/81**: `auth.spec` logout ×3 "element detached" | application: exit relation rendered before the identity read resolved → root repair in WU-SF02.4 (`exit={null}` while the read is pending) |
| L3 mocked run 2 | after repair | **81/81** | — |
| L3 mocked run 3 | after D1/D2 | aborted at start: `EACCES rmdir test-results/sf01-real-stack/...` | environment: the real-stack runner (running concurrently) holds root-owned output until its exit chown; the mocked lane now writes to `--output=<scratch>` |
| L3 mocked run 4 | same | aborted: "Process from config.webServer was not able to start" | environment: a second `next dev` (my diagnosis server) held the Next 16 dev lock of `apps/web` |
| L7 real stack run 1 | SF-02 before D1–D4 (the run started before those repairs) | **10/14**: `sf01-field` desktop+mobile (accessible name of the Challenge link included its meta) → D2; `f03-accessibility` mobile (`color-contrast serious, 3 nodes` right after the Freeze commit) → D4; `f03-protected-question-field` desktop 90 s timeout | D2, D4 repaired at the primitive (WU-SF02.2 / WU-SF02.1); the timeout is D5 (below) |
| L0 / L5 | final tree before D5 | 219/219, tsc 0, eslint 0 | — |
| L3 mocked (ladder run 1) | same | **81/81** (1.4 min) | — |
| L7 real stack (ladder run 1, lane alone) | same | **12/14**: only `f03-protected-question-field` desktop + mobile, 90 s timeout, every click 2.8–6.3 s in the container | D5 |
| L0 RED non-vacuity | SF-02 unit tests copied onto the pre-SF-02 tree `644e1c8` (throwaway worktree) | 3 files unloadable (`topology`, `humanPosition`, the SF-02 `primitives` imports absent) + 8 failed / 38 passed (the SF-01 assertions the old tree already satisfied) | the new assertions are not vacuous |
| Full ladder run 2 | after D5 (+ D6 added while the mocked stage ran — never again: a source edit during a `next dev` lane) | L0 219/219; **L3 73/81** (8 mobile: "subtree intercepts pointer events", "nothing overflows" 183 px); **L7 7/14** (all mobile + F03 desktop); harness run-4 aborted | D7: the D5 edit made the stacked core `position: relative` without clearing the ring's `left/top: 50%` → the core shifted over the orbit on the phone (WU-SF02.8) |
| Full ladder run 3 | after D7 | L0 219/219; **L3 81/81**; **L7 13/14** (only `f03-protected-question-field` desktop, 90 s budget: 389 actions without a failed assertion, spec total ≈ 103 s); harness run-5 aborted at state 11 (D8) | D8 (WU-SF02.8); the desktop F03 budget: see "F03 desktop budget" below |
| Full ladder run 4 (final tree) | after D8 | L0 219/219, tsc 0, eslint 0; L3 49 failed / 32 passed (dev-server timeouts on unchanged legacy `decision.spec` pages, host load 6–8: environment) → re-run alone: **81/81**; **L7 14/14** (8.5 min); harness run-6 **30/30** | — |

## D5 — APPLICATION (performance is a capability property, 22 §35 / falsifier 75)
- **Symptom:** in the isolated real stack (API + `next dev` + Chromium in one container, software rendering)
  every Playwright action took 2.8–6.3 s (trace timing), so the 25-step F03 spec exceeded its 90 s budget. The
  same spec passed 14/14 on the pre-SF-02 tree; against a local `next dev` + the real API (route-forwarded to
  the isolated inspection API) the same clicks took 200–500 ms.
- **Reconstruction:** A/B measurement (`review/browser-evidence-2026-09-25/harness/perf-ab.mjs`) under CDP CPU
  throttling ×4, real Chromium, `requestAnimationFrame` cadence and click actionability time:
  full page rAF median **96–143 ms** (≈8–10 fps) vs **16.7 ms** with the background hidden. Isolation of the
  cost: three continuously rotating 1400 px SVG ring groups (`field-drift`) = the bulk; the viewport-sized
  breathing gradient (`field-breathe`, `transform: scale`) + the header/plane `backdrop-filter` = the rest;
  `core-breathe` (box-shadow animation) and `path-pulse` minor.
- **First Broken Relation:** LIVING BACKGROUND → INTERACTION CAPABILITY. A presentation layer consumed the frame
  budget that every actionability check (and every human) depends on; on constrained machines a capability
  became slow to reach. 22 §35: motion must never cost capability.
- **Root repair (`globals.css`, presentation only, no meaning changed):** rings are static structure (900 px,
  fixed rotations); the breathing luminosity is a *bounded* 90 vmin layer animating opacity only on its own
  compositor layer; the core glow is a pseudo-element animating opacity (never the core's box-shadow);
  no `backdrop-filter` anywhere (solid translucent header/planes). Measured after the repair (same ×4 throttle):
  login rAF 16.6 ms, Workspaces Field 29 ms (from 143), click actionability 90–170 ms (from 300–650 ms).
- Reduced-motion and identity tests unchanged (the rule set is global); no test asserted the rotation.

## F03 desktop budget (marginal in this container; disclosed)
The published F03 spec `f03-protected-question-field.real.spec.ts` (five identities, 28 clicks, 96 expectations,
13 navigations, 5 full-page screenshots) has a 90 s budget calibrated on the light F02 theme. On the SF-02 tree it
completes every step (389 recorded actions, no failed assertion) in ≈ 103 s on the desktop project of the
isolated container (software rendering, API + `next dev` + Chromium sharing the container's CPU); the mobile
project of the same spec passes. Trace breakdown (ladder run 3): 28 clicks 28.1 s, 5 full-page screenshots 16.1 s
(3.2–3.7 s each: the spec's own visual capture of the long dark Field), expectations 32 s, hooks/logins 13.7 s,
13 navigations 9.7 s. Measured on the production runtime under ×4 CPU throttle, a full-page screenshot of the
Session Field costs 0.7–1.1 s, of which the background gradients are ≈ 0.4 s. In ladder run 4 the same spec passed on the same tree (desktop 1.4 min total incl. setup, within budget): the
budget is marginal in this container, not exceeded by a behaviour. I did not strip the Field's background to fit
a published test's budget, and I did not change the published spec's timeout; whether to raise the F03 spec's
budget for the SF-02 identity is a human decision.

## Environment notes
- The real-stack lane must run **alone**: a first attempt ran concurrently with the mocked lane and a docker
  build (load average > 8 on 8 cores) and is not counted as evidence.
- The runner hands its output back to the host user only at exit; a concurrent lane sees root-owned files.

## Result
PASS on the final tree: L0 219/219 · L5 clean · L3 81/81 · L7 14/14 · evidence run-6 30/30. Every RED on the way is recorded above with its First Broken Relation.
