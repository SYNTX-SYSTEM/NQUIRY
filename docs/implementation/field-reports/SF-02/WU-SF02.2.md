# WORK UNIT REPORT
FIELD: SF-02 — NQIRY SYMBIOTIC INTERACTION FIELD (materialization of doc 22)
WORK_UNIT: WU-SF02.2 — Topology primitives: Core, Orbit, Node, Relation Path, planes, living background, human position

## Mission
Materialize the topology of 22 §11–§16 and §29–§35 as pure derivation + presentation primitives that every
surface composes: one Core, orbits of Nodes on Relation Paths, depth planes, a living background, and the
orbit-to-stack transformation with DOM order = semantic order = keyboard order.

## MUST BECOME TRUE
1. Topology is DERIVED PROJECTION STATE from authoritative projections by pure functions
   (`lib/field/topology.ts`): unit-circle positions (first node at the top, clockwise), a ring capacity
   (`ORBIT_CAPACITY = 10`) above which the same DOM renders as a relational stack, affordance state from the
   server capability only (`affordanceState`), and lifecycle label density following gravity (`lifecycleLabelDensity`:
   passed, current and the next lawful phase carry a visible label; later phases keep an assistive label, never dropped).
2. The Relation Path states are exactly 22 §11.4 (`PATH_STATES`), and Node states carry a non-colour carrier
   (text marker "Relation state: …" for assistive technology, visible marker text, `data-node-state`).
3. Human position is a LABEL (`lib/field/humanPosition.ts`: "You: Role · governance root · Session controller ·
   Participant"), never a gate; it is the one Field module allowed to read viewer flags (gate allowlist).
4. `FieldStage` / `Topology` / `Planes` / `Plane` (`components/field/topology/FieldStage.tsx`) give one
   `.field-stage[data-topology][data-surface]` grid; `FieldCore` renders the Core with `data-core-kind` and
   `data-core-state` (current / human / frozen / boundary / loading); `Orbit` renders an aria-hidden SVG of ring +
   `line.path[data-path]` and a `<ul class="orbit">` of `li.node` in semantic order, each node a `Link`, a
   `button` or a `span` (`.node-main`) with meta and marker as *siblings* of the control.
5. `FieldBackground` (`components/field/FieldBackground.tsx`) is an `aria-hidden` living background with
   regimes access / challenge / session / human-question / frozen / boundary, mounted by `FieldFrame`.
6. On ≤ 860px or above ring capacity the same DOM is a stack with connectors: uniform rows for every node size,
   assistive labels become visible, the ring's numeric marker of dot nodes is hidden (it would duplicate the label).
7. Reduced motion removes every animation and transition (elements and pseudo-elements) and no meaning.

## MUST REMAIN IMPOSSIBLE
- Geometry from the viewport, the clock or randomness in derivation code (SSR and client derive the same topology).
- A node whose state is carried by colour or position only.
- A control whose accessible name includes its meta or its state (the name is exactly the label).
- A dot node that loses its label (assistive text is always present).
- An orbit that reorders the DOM: keyboard order is always the semantic order of the `<ul>`.

## FALSIFIER / RED / REPAIR / GREEN
| Test | RED | Repair | GREEN |
|---|---|---|---|
| `topology.test.ts` (7): positions on the unit circle, first at top, clockwise; capacity boundary; `affordanceState`; label density (done/current/next visible, others assistive; no current → only done visible) | module absent | `topology.ts` | ✓ |
| `humanPosition.test.ts` (3): role/none, governance root via either projection name, session relations incl. participant | module absent | `humanPosition.ts` (accepts `governanceCapable`, the F01 name, so the workspace page does not read `isGovernanceRoot` — the gate caught that token in the page) | ✓ |
| `primitives.test.tsx`: "a link's or button's accessible name is exactly the node label: meta and state marker are siblings, not children" | RED in the browser (WU-SF02.8 D2: real-stack `getByRole('link', {name: 'Offline attempt', exact: true})` → 0; harness "SF-02 Inspectionaccessible Workspace") and then as a unit test | `Orbit.tsx`: the control contains only the label span; `node-meta` and `node-marker` are siblings | ✓ |
| `primitives.test.tsx`: "every node states its relation in text, in semantic DOM order" | absent | `Orbit.tsx` MARKER map (incl. `future: "later"`) + visually-hidden "Relation state:" | ✓ |
| `tests/e2e/sf01-field.spec.ts` "reduced motion removes animation but not meaning" (extended to `.field-bg::after`, `.drift`, `field-core`, `.orbit-paths .path`) | RED in the browser (WU-SF02.8 D1: harness "expected none, got field-breathe" on `::after`) | `globals.css` reduced-motion rule covers `*::before, *::after` | ✓ (mocked lane) |
| Phone stack uniformity (WU-SF02.8 D3, found on the real-stack mobile screenshot) | `sm` nodes kept their 96px ring width in the stack; dot nodes showed label + duplicated number | media block and `[data-topology="stack"]` rules: every size is a full-width row; dot `node-meta` hidden; verified 13/13 rows at 371px on Pixel 7 | ✓ (dev check + harness run-3) |

## Geometry
Ring radii are CSS custom properties (`--orbit-r-1/2`) applied to `--ox/--oy` unit-circle coordinates; the SVG
uses percentages of a 100-unit viewBox (radii 32.2 / 44.7) so it scales with `--field-size`. The lifecycle ring
of the Session Field uses capacity 13 (all 13 canonical states on one ring with dot density), the relation
rings use the default 10.

## Proof
L0: `topology.test` 7, `humanPosition.test` 3, Orbit/primitives tests in `primitives.test.tsx`. L3 (mocked
lane): responsive and reduced-motion tests over the new selectors (`field-core`, `data-plane`, desktop orbit
assertions). L7 + browser evidence: WU-SF02.7 / WU-SF02.8.

## Result
PASS. Primitives adopted by WU-SF02.3–SF02.6; three visible defects found by browser proof were repaired at
the primitive (root), not per page.
