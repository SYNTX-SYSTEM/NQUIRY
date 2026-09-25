# WORK UNIT REPORT
FIELD: SF-04 — NQUIRY SYMBIOTIC FIELD ORGANISM
WORK_UNITS: SF04-WU-02 Semantic Core Organism · SF04-WU-03 Living Field Entity Layer · SF04-WU-04 Relational Current System

## WU-02 — Semantic Core Organism (doc 25 §6) — `components/field/topology/FieldCore.tsx`, `globals.css`
Anatomy in DOM order, all decorative layers `aria-hidden`: `.core-aura` → `.core-rings` (3 `.core-ring`, irregular
border radii, phase-shifted −3 s / −6 s, durations 9 / 11.25 / 13.5 s) → `.core-membrane` → `.core-orbit-trace`
(one faint dot travelling an inscribed ellipse by CSS motion path, 48 s; the layer itself never rotates; hidden for
loading/boundary) → `.core-nucleus` (eyebrow · h1/p identity · `.core-state` text ·
meta · children). The `.core` box IS the nucleus frame the geometry measures; the layers never change it.
Motion law: aura breathes by opacity 12 s (`aura-breathe`), rings by scale ≤ 2.4 % (`ring-breathe`), membrane by scale
≤ 1.2 %; the nucleus and the text never animate. Directional response: the aura (10 px) and the rings (6 px) lean
toward the projection-local encounter vector (`--vec-x/--vec-y/--vec-on` from the stage) with `--motion-hover-in`.
State tone via `--core-tone/--core-tone-glow/--core-aura-color` per `data-core-state` (current/human cyan, frozen
blue, boundary red, loading neutral + dashed nucleus). Nothing here creates state (doc 25 §6.3); no spinner.

## WU-03 — Living Field Entity Layer (doc 25 §7) — `lib/field/geometry.ts`, `Orbit.tsx`, `globals.css`
Geometry: `NodeContent.weight/band` (from `projectNode`), `BAND_FRACTION` inner .29 / middle .41 / outer .53 of the
stage as the ring's breathing base, `massOf(weight)` (0.9–1.1) scales the estimated frame, a closeness factor
(1 − 0.05·(weight−0.7)) pulls heavier entities slightly inward, and `organicOffset(key)` (FNV-1a seeded: angle
±4–11°, radius ×(1 ± 0.03–0.08)) breaks the mechanical ellipse deterministically — no random jitter, identical on
every render (tests: determinism, bounds, band radii order, no overlaps, no core collision). The offsets breathe
within the room the content leaves: `layoutField` tries them at full, half, quarter and zero scale and keeps the
first layout that fits, so an organic offset is never the reason a field falls out of its orbit (doc 23 §7.6).
Mass follows the stylesheet's padding law in the estimate (+6/+4 px per side per unit of mass − 0.9), never a scaled
frame — a scaled estimate decided the constellation before the rendered frames could refine it (harness run-1/2).
Node anatomy in DOM order: `.node-aura` (radial tone glow, opacity from `--weight`, `inset` from `--mass`) →
`.node-body` membrane (capsule `--radius-node`, padding from `--mass`; the type never scales — doc 23 §6.1 floors
hold) → `.node-main` (link/button/text) → `.node-meta` → `.node-marker` (`.node-role` indicator + textual state).
Attributes: `data-band`, `data-tone`, `data-role`, `data-provenance`, `--mass`, `--weight`, `relationCount` input.

## WU-04 — Relational Current System (doc 25 §8) — `Orbit.tsx`, `globals.css`
One `aria-hidden` SVG per orbit: the ring ellipse plus one `g.relation` per node (`data-key`, `data-path` = SF-03
path state, `data-relation-type`, `data-direction`, `data-provenance`, `--w`): `path.path.path-base` (a quadratic arc
whose bend is deterministic per key, ≤ 12 % of the length: `arcPath()`), `circle.endpoint-node`,
`circle.endpoint-core` — the SVG is STATIC (it never repaints for motion). The current itself is one HTML
`span.current-pulse` per non-latent relation in `div.currents[aria-hidden]`, travelling the same arc on a CSS motion
path (`offset-path: path(…)`, a transform animation on its own compositor layer). The SF-03 colour law by path state
remains on the base path and colours the pulse. Motion law by class: directional → `current-travel` 9 s source →
target (reverse for target-to-source); reciprocal → alternating travel; context → an 8 px pulse breathing midway
(`current-breathe`); latent → dotted base, no pulse. Encounter: the resonating relation's base thickens, its pulse
brightens and doubles speed, its endpoints grow (r 4.5). No `<line>`. (First materialized as an SVG
`stroke-dashoffset` layer; measured at ~10 ms/frame at ×4 CPU throttle because every dash step repainted the whole
stage-sized SVG — root-repaired to the compositor pulse, WU-12.)

## RED → root repair in these units
| RED | First Broken Relation | Root repair |
|---|---|---|
| unit: node anatomy slice found the SVG group first (test bug) | test sliced from the first `data-key` | slice from `class="node" data-key` |
| SF-02/SF-03 assertions `<line class="path">`, `class="plane"` | architectural delta (curved currents, chambers) | assertions updated and annotated "SF-04" |
| harness run-1/2: wide Workspace/Session fields decided the constellation (SF-03 states 19/34/35 "fits" RED) | ESTIMATE → MODE: mass-scaled estimates and full organic offsets exceeded the decision stage, so no rendered frame was ever reported (frames are reported in orbit mode only) | estimate follows the padding law; organic offsets bounded by room (above) |
| harness run-1/2: phone overflow growing over time (6 → 23 px) | ROTATING LAYER → SCROLLABLE OVERFLOW: the micro-orbit rotated its rectangular layer, whose bounding box swept past the viewport | the dot moves on a motion path; the layer is static |

## Tests
`tests/field/sf04-primitives.test.tsx` (16), `tests/field/geometry.test.ts` (+4), `tests/field/projection.test.ts` (15);
mocked lane `tests/e2e/sf04-field.spec.ts` › Semantic Core Organism (2), Living Field Entities + Relational Currents (3).
