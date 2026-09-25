# WORK UNIT REPORT
FIELD: SF-03 — NQIRY SYMBIOTIC SURFACE EVOLUTION
WORK_UNIT: WU-SF03.2 — Content-aware, topology-aware, viewport-aware, collision-resistant Field geometry (doc 23 §7; FBR-23-03, FBR-23-06)

## MUST BECOME TRUE
1. Geometry is DERIVED from content: each node's frame is estimated from what it renders (label, meta, size class),
   the core's frame from its title/state/meta; the ring radius follows the frames (never the reverse).
2. Angular allocation is weighted: a node's share of the circle is proportional to the arc its frame needs at its
   angle (wide frames near the top/bottom, tall frames at the sides) plus a gap; order stays clockwise from the top.
3. Rings never share a spoke: an outer ring starts half an inner share later and a deterministic offset search
   (0, ±8 … ±48°) picks the first collision-free start; residual spoke coincidences are nudged (+5°, order-preserving).
4. Collision resistance: a ring grows until no frame touches another frame, an inner ring's frame or the core;
   when the stage WIDTH is exhausted the ring grows into a taller ellipse (the box height follows the content);
   when that is exhausted too the overflow is reported and the content is never shrunk.
5. Viewport awareness: the topology box's width is the grid column (700 px minimum on desktop, ~800+ on wide
   screens, full width on tablet), its height follows the content (`--stage-h`); the layout is recomputed from the
   measured box (ResizeObserver) — same content + same box ⇒ same layout; an elliptical stretch uses only room the
   box actually has; `BREATHE` fractions (0.29 / 0.41 of the shorter side) give breathing room whenever space exists.
6. Determinism: no DOM, clock or randomness in `lib/field/geometry.ts`; the server and the client derive the same
   layout for the nominal box; the mode (orbit / stack) is decided from the content on the viewport CLASS's decision
   stage (`desktop` 700×1400, `wide` 820×1500), so it never depends on the mode itself (no loop).
7. Compaction before collapse: when wide (md) frames cannot fit, they compact (earlier wrapping at 160 px) before
   the relational stack becomes the representation (doc 23 §7.6); type size never changes.

## MUST REMAIN IMPOSSIBLE
- A fixed node width (falsifier 11); a ring radius chosen before the content; random or unstable geometry (16);
  proximity implying authority (17: gravity carriers are unchanged — size/intensity/label weight, never distance
  by authority); a node overlapping another or the core (12–13); text shrunk to fit (8).

## FALSIFIER / RED / GREEN (L0, `tests/field/geometry.test.ts`, 11 cases; `tests/field/sf03-primitives.test.tsx`)
| Test | RED before | Repair |
|---|---|---|
| frames grow with content and wrap at the size maximum; meta/marker add height; deterministic | module absent | `estimateNodeBox`, `estimateCoreBox` |
| every node without overlap and without touching the core (7 + 2 nodes, real Challenge content) | first implementation: cross-ring overlap (an outer node at an angle touched an inner node although the radii were "separated by heights") | collision loop checks the core and every previously placed ring |
| wide nodes get more arc | absent | weighted allocation |
| clockwise order from the start angle | absent | allocation keeps order |
| outer nodes never on an inner spoke; rings separated | absent | half-share start + offset search + nudge |
| radius follows required circumference; larger stage ⇒ larger radius | absent | `required`, `BREATHE` |
| elliptical stretch into the longer axis stays inside the box | absent | `ex/ey` bounded by room |
| identical layout for identical input | — | pure function |
| overflow reported, content keeps its size; compact frames on a narrow stage | absent | `fits`, `compact` |
| SSR markup: px offsets per node, one path per node, one ellipse per ring, no inline width, `data-fit` | absent | `Orbit` renders from the `Topology` layout context |

Browser-level RED found by the stress spec (`tests/e2e/sf03-field.spec.ts`) and repaired at the root:
- workspace stress content did not fit at 700 px because the inner ring's minimum radius used the core's corner
  distance + the tallest frame (worst case); root: the minimum is now soft (core's longer side + gap) and the
  collision loop provides the real distance → r1 299 → 224 px for the same content.
- nine wide Sessions + two long-name controllers at 700 px: the ring grew past the width; root: growth goes into
  the vertical axis once the width is exhausted, and md frames compact before the stack becomes the representation.
- the mode decision must not depend on the measured topology box (which the mode changes) — root: decided from
  the stage width's viewport class on a fixed decision stage.

## Real content on the review runtime (dev server + isolated API, measured)
| Surface / viewport | topology box | fit | overlaps | escaping text |
|---|---|---|---|---|
| Challenge 1280×860 | 700×700 | fits (compact frames) | 0 | 0 |
| Session 1280×860 | 720×700 | fits | 0 | 0 |
| Session 1600×900 | 825×740 | fits | 0 | 0 |
| Workspace 1600×900 | 792×740 | fits | 0 | 0 |
| Session Pixel 7 | stack | — | 0 | 0 |

## Client refinement from rendered frames (doc 23 §7.1) — added after evidence run-3
Estimates (even conservative ones, ×1.06 width / ×1.04 height, capitals ×1.22) cannot know the real glyphs. After
render, each `Orbit` reports its rendered `.node-body` frames (content-sized, hence position-independent) to the
`Topology` (`useReportBoxes`); the layout is recomputed with the rendered frames (`layoutField({ measured })`), and
the box height is DERIVED during render from (width, content, rendered frames) with a circular layout — a pure
function, so a taller box never changes it and the refinement converges in one step. Frames (nodes and the core) are owned by `FieldStage`, enter the mode decision, and are reported only in
orbit mode (in the stack the rows are full width and would feed back); a decision that switches to the stack keeps the
frames it decided on. The fit verdict tolerates 12 px of reach into
the stage's outer gap (`FIT_TOLERANCE`, less than the grid gap). Long authority tokens get a zero-width break after
each `_` in `.node-meta`, so `WORKSPACE_GOVERNANCE_RIGHT` wraps at an underscore, never mid-word (doc 23 §6.4).

Defects found on the way (recorded in WU-SF03.8): D-SF03-3 (a radius step that left the width was still taken →
never take it, grow vertically instead), D-SF03-4 (the needed height was latched from an earlier, empty layout
because the child orbit reported before the parent's layout ref updated → the height is now derived, not stored).

## Removed
`orbitPositions`, `outerRingStartDeg`, `topologyMode`, `ORBIT_CAPACITY` (SF-02 unit-circle geometry) and their
tests: superseded by `geometry.ts`; keeping them would have been dead code with tests that prove nothing the app
uses.

## Result
PASS (L0 + L1); browser proof in WU-SF03.7/8.
