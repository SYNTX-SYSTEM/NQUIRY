# WORK UNIT REPORT
FIELD: SF-02 — NQIRY SYMBIOTIC INTERACTION FIELD (materialization of doc 22)
WORK_UNIT: WU-SF02.8 — Browser evidence on the integrated stack, visible defects, reviews

## Mission
Prove the visible Field in a real browser against a real, isolated, production-built stack — never a mock —
for every state the mandate names (login, workspace overview, workspace field, challenge field, session field,
question generation, frozen field, governance, denied, rejected, not found, unknown, loading; desktop, Pixel 7,
reduced motion, keyboard, axe), persist the evidence so a reviewer can reconstruct every claim without the
chat, and repair every visible defect at its root.

## Runtime (isolated, production build)
Compose project `nquiry-sf02-inspect` (recipe `infra/sf01/compose.yaml`, unchanged): fresh Postgres (no host
port), this tree's FastAPI, `next build` + `next start`, one same-origin proxy on `127.0.0.1:13200`
(`review/browser-evidence-2026-09-25/runtime/{proxy.mjs,start-inspect.sh}`, mounted read-only; the API's CORS
origin is fixed to `localhost:3000`, owned by another Field's stack). Identities provisioned with the HD-3
DEV-ONLY script (identity + credential only); every relation established through the product:
`owner@inspect.local.test` (founded `SF-02 Inspection`), `facilitator@inspect.local.test` (Facilitator, framed the
Challenge, session control at CHALLENGE and SESSION scope), `outsider@inspect.local.test` (member of nothing).

## Harness
`harness/review-harness.mjs` (Playwright 1.63, real Chromium, **no interception**): 30 recorded states; for each
state it reads the canonical projection from the API with the same cookie, screenshots the page, and checks the
visible relation against the projection (85 explicit checks + axe wcag2a/aa serious/critical + horizontal
overflow + unexpected HTTP status log + effective topology mode from computed style). Session progression
(DRAFT → SETUP → CHALLENGE_CAPTURE → Burst → QUESTION_GENERATION → capture → completion → QUESTION_CAPTURE)
is driven through the UI by the controller. Boundary states: denied (outsider), not found (unknown Challenge
id), rejected (malformed founding), loading (CDP 2 s latency), unknown (offline mutation, same intent key).
Runs are kept: `run-1` (pre-repair), `run-2` (after D1/D2), `run-3` (after D3/D4), `run-4` (aborted, D7), `run-5` (aborted, D8), `run-6` (final tree).
Each run holds `MANIFEST.md` (table: route, viewport, canonical state, identity, expected, observed, PASS/FAIL),
`results.json` (projection + checks + HTTP log per state) and 30 PNGs (~17 MB per run).

## Runs
| Run | Tree | Result |
|---|---|---|
| run-1 | first complete Field | 19/30: D1 (state 5), D2 (7–10), and harness precision defects (readiness waits, effective mode from computed style, expected 400 on the rejected founding, offline prefetch classification, loading capture order) |
| run-2 | after D1/D2 | 30/30 |
| run-3 | after D3/D4 | 30/30 (phone stack checks strengthened: uniform rows, order, frozen structure) |
| run-4 | after D5/D6 | aborted at state 8: the phone core was offset by the ring's 50 % offsets (D7) and its orbit intercepted clicks |
| run-5 | after D7 | aborted at state 11: the ring-2 governance node (taller since D6 wrapped its token) sat on the same spoke as the ring-1 "Open Session" node and intercepted its click (D8) |
| run-6 | final tree (after D8) | 30/30 (85 explicit checks + D3/D8 guards; axe serious/critical 0 on every state; overflow 0; no unexpected HTTP) |

## Visible defects (all repaired at the root; none per page)
| ID | Where found | Symptom | First Broken Relation | Root repair | Regression guard |
|---|---|---|---|---|---|
| D1 | run-1 state 5 (reduced motion) | `.field-bg::after` still animated (`field-breathe`) | REDUCED MOTION → EVERY ANIMATION: the rule covered elements, not pseudo-elements | `*, *::before, *::after { animation: none; transition: none }` | mocked e2e reduced-motion test extended to `::after`, `.drift`, core, paths |
| D2 | run-1 states 7–10; L7 `sf01-field` (link name "Offline attempt" not found) | a node link's accessible name was "SF-02 Inspectionaccessible Workspace" | NODE CONTROL → ACCESSIBLE NAME = LABEL: meta rendered inside the control | `Orbit.tsx`: control contains only the label; meta and marker are siblings | `primitives.test` "accessible name is exactly the node label" |
| D3 | L7 mobile screenshot of the Session Field | phone stack: `sm` nodes 96 px wide (ring width kept), dot nodes full width with label + duplicated number | ORBIT → STACK TRANSFORMATION: size rules of the ring survived the stack | media + `[data-topology="stack"]` rules: every size a uniform full-width row, dot meta hidden | harness phone states: "lifecycle rows uniform and full width (D3)" |
| D4 | L7 `f03-accessibility` mobile: `color-contrast (serious, 3 nodes)` 0.4 s after the Freeze commit | outcome text at partial opacity during `relation-settle` (opacity 0.35 → 1); the 3 nodes = the outcome's three text lines | TEXT-BEARING ANIMATION → CONTRAST AT EVERY INSTANT | `relation-settle` moves/borders only; `node-shimmer` pulses border colour; no opacity animation on text | axe in every harness state; L7 a11y specs (mobile passes since) |
| D5 | L7 `f03-protected-question-field` 90 s timeout (both projects), clicks 2.8–6.3 s | continuously rotating viewport-sized SVG rings + viewport-sized breathing layer + `backdrop-filter` starved the frame budget on software rendering (≈8–10 fps at ×4 throttle) | LIVING BACKGROUND → INTERACTION CAPABILITY (22 §35) | static rings, bounded opacity-only breathing layer, core glow by opacity, no backdrop-filter (WU-SF02.7) | `harness/perf-ab.mjs` (rAF cadence ≤ 30 ms at ×4 throttle) |
| D6 | run-3 state 11 screenshot | the governance node's meta `SESSION_CONTROL_RIGHT` overflowed the node width | NODE META → NODE BOUNDS | `.node-meta { overflow-wrap: anywhere }` | run-5 screenshot 11 (visual) |
| D8 | run-5 state 11 (click on "Open Session" intercepted by the governance node) | ring 1 and ring 2 both start at −90°, so their first nodes share a spoke; with a taller ring-2 node the bodies overlap | RING → RING DISTINCTNESS (22 §13.3): outer nodes must never share an inner node's angle | `orbitPositions(count, startDeg)`; `outerRingStartDeg(innerCount) = −90° + 180°/innerCount`; every ring 2 passes it | `topology.test` (angles never coincide); harness "no two nodes overlap (D8)" on Workspace + Challenge states |
| D7 | ladder run 2: every mobile lane (mocked 8 failed: "subtree intercepts pointer events"; real stack 7 failed: overflow 183 px + timeouts; harness aborted) | the D5 repair made the stacked core `position: relative`, so the ring's `left/top: 50%` applied as relative offsets: the core shifted right/down over the orbit | STACK TRANSFORMATION → RING OFFSETS MUST NOT SURVIVE | `left: auto; top: auto` with the relative position (media block + `[data-topology=stack]`) | mocked e2e "nothing overflows" (mobile) — it is what caught it; harness phone states |

## What the screenshots show (human-review claims)
- The Challenge Field (state 11) is a Field, not a detail page: the Challenge core is central with the Session
  count and Workspace; Sessions and the possible "Open Session" relation orbit it on ring 1 with solid
  (established) / dashed (possible) relation paths; the SESSION_CONTROL_RIGHT holder orbits on ring 2 with its
  grantor; the action / governance / proof planes sit in depth on the right; the background is dark, layered
  and quiet.
- The Session Field (states 14–24) reconstructs the lifecycle: 13 canonical states on a ring with passed /
  current / later markers, human participants and the controller as relation nodes, the Human Question Field
  core (cyan) while the Burst is open, the Frozen Field core (blue) after completion; the committed outcome is
  blue with the re-read line; rejected input is a red boundary with the text retained.
- On Pixel 7 the same DOM is a relational stack (core → lifecycle → active phase → relations → governance →
  proof) with uniform rows and no horizontal overflow.

## Evidence size (disclosed)
Six runs × up to ~17 MB of PNGs are untracked under `review/browser-evidence-2026-09-25/`. The human decides what
to commit; the harness reproduces any run.

## Result
PASS: run-6 30/30 on the final tree (production build, real API, no interception). Six defects D1–D8 (D5 reconstructed by measurement) were found by browser and real-stack proof and repaired at the primitive/stylesheet root, each with a regression guard.
