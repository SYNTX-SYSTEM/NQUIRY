# SF-04 — WU-00: Repository reconstruction, current Field, target Field, gap map, FBRs, Work Units
FIELD: SF-04 — NQUIRY SYMBIOTIC FIELD ORGANISM (materialization of doc 25 on the SF-02/SF-03 tree)

## Phase 0 — protected state (recorded before any change)
HEAD `644e1c8`, branch `frontend-symbiotic`, worktree `/home/codi/Entwicklung/nquiry/worktrees/frontend-symbiotic`,
37 uncommitted paths = the SF-02 + SF-03 materialization (kept; not reset, not discarded). BLUE (F02/F03: `apps/api`,
`packages`, `migrations`, `lib/api/*`, `components/f02|f03/*`) and RED (F04 worktree) untouched. No commit/tag/push.
Doc 25 (`25_NQIRY_SYMBIOTIC_FIELD_ORGANISM_ARCHITECTURE.md`, 4045 lines) read completely and copied into the worktree
byte-identical (sha256 `1e2b4666f587855d…`).

## Phase 2 — repository reconstruction (actual materialization the architecture binds to)
| Doc 25 organ | Actual code today (SF-03) | Producer it projects |
|---|---|---|
| Semantic Core Organism | `components/field/topology/FieldCore.tsx` → `section.core[data-core-state]` (eyebrow, title, state text, meta) + one glow pseudo-element (`core-breathe`, opacity) | page projections: challenge/workspace/session/access (`GET …/overview`, `…/challenges/{c}`, `…/sessions/{s}/position`, `/auth/me`) |
| Living Field Entity Layer | `Orbit.tsx` → `li.node[data-node-state][data-node-size][data-emphasis]` with `.node-body` (label / meta / marker); frames content-sized; positions from `lib/field/geometry.ts` (rendered-frame refinement) | node states from capabilities (`possible/unavailable`), projections (`established`), lifecycle `phases[]` (`current/future`), `participants[]` (`human`), `sessionControllers[]` (`governance`) |
| Relational Current System | `Orbit.tsx` SVG `ellipse.ring` + straight `line.path[data-path]`; CSS: static strokes, `path-pulse` (current), reciprocity opacity/stroke | path state = node state (22 §11.4) |
| Contextual Semantic Organ | `FieldStage.tsx` `Planes` → `.instruments` grid of `section.plane[data-plane=action|human|frozen|governance|proof]` — **dashboard residue: bounded card-like planes** | page instruments: effect surfaces, forms, `ProofDepth`, provenance `dl`, participant/controller lists |
| Traversal Trace | `RelationTrace.tsx` → `nav[aria-label="Inquiry position"] > ol > li[data-coordinate][data-status]` with links / `aria-current`; CSS: breathing separator bars — **generic breadcrumb residue** | `lib/field/position.ts` trace from confirmed projections |
| Atmospheric Field Medium | `FieldBackground.tsx` → `.field-bg[data-regime]` (depth gradient, constellation, 2 drifting nebula blobs + static haze, bounded breathing layer, static traces, 7 particles) — no field-state response | surface class only |
| Projection Authority Layer | implicit: gates (`gates.test.ts`), `humanPosition` (label only), `affordanceState(capability)`; **no explicit provenance model, no semanticWeight/orbitBand/relation-type rules** | — |
| Hover / focus | `FieldStage` delegated focus/hover → `data-active-relation` (family: action/governance/proof) → plane/orbit/path CSS response — **family-level highlight, not an encounter** | projection-local |
| Responsive | grid (≥1100), tablet full-width topology + instruments grid (861–1099), phone stack rows (≤860) — **stack = list rows, not a constellation; organ = stacked sections** | CSS only |
| Motion | `core-breathe`, `field-breathe`, nebula drift, particles, `rail-energy`, `relation-settle`, `path-pulse`; global reduced-motion rule | — |
| Tests / evidence | vitest 232 (`tests/field/*`), mocked lane 102 (`tests/e2e/*` incl. `sf03-field.spec.ts`), real stack 14, SF-03 harness 40 states, perf-ab | — |

## Phase 3 — where the current Field still collapses (doc 25 §3)
- 3.1 dashboard residue: `.instruments` = bounded planes with headings ("Open a Session", "Governance", "Proof") → reads as stacked cards / sidebar; the field and the instruments do not bridge.
- 3.2 static diagram residue: straight spokes from the centre; even angular allocation (content-weighted, but every node of a ring sits on one ellipse); core = rounded label container with one glow.
- 3.3 weak atmosphere: no pressure zones, no active-state wash; the medium does not respond to the field.
- 3.4 conventional breadcrumb: a text rail with `→`-style separator bars; no route nodes, no active membrane, no path shimmer, no compression on mobile beyond wrapping.
- 3.5 motion without meaning: `path-pulse` on the current path only; hover = border/glow colour on a relation family; no relation-type motion; no directional core response.
- Projection authority: node emphasis and sizes come from `size`/`emphasis` props chosen per page; no explicit provenance; no relation-type derivation (no visual relation classes exist yet, so nothing is invented either).

## Phase 4 — target Field (doc 25 §4–§16) bound to this repository
CANONICAL CONTEXT (projections above) → PROJECTION RULES (`lib/field/projection.ts`, explicit, deterministic,
with provenance) → SEMANTIC CORE (`FieldCore`: aura · resonance rings · membrane · nucleus · micro-orbit) ↔ FIELD
ENTITIES (`Orbit` nodes with aura/membrane/surface/label/role indicator; `semanticWeight`, `orbitBand`, `visualTone`,
deterministic organic offsets in `geometry.ts`) ↔ RELATION CURRENTS (SVG curved paths with visual class from the
canonical relation: `directional` / `reciprocal` / `latent` / `context`; **no `tension` — no canonical tension
relation exists in this repository**) ↔ CONTEXTUAL ORGAN (`ContextOrgan`: shell · active-state membrane header ·
primary / relational / governance-logic / action chambers, the same instruments re-homed, relation bridge, relation
tokens) ↔ TRAVERSAL TRACE (`RelationTrace` as route nodes + trace + active membrane + shimmer, mobile chip) ↔
ATMOSPHERIC MEDIUM (`FieldBackground` + pressure zone + resonance wash). Hover/focus = encounter cascade through a
projection-local `FieldState` in `FieldStage` (hovered/focused node key + vector, active relation, hovered context
token); selection = the route (application state), never a click side-effect.

## Phase 5 — First Broken Relations (visible effect → … → FBR → authoritative home → minimum root repair)
| # | Visible effect | FBR | Authoritative home | Minimum root repair |
|---|---|---|---|---|
| FBR-1 | right side reads as stacked cards | STRUCTURAL COMPOSITION: instruments are independent bounded sections | `FieldStage.Planes` / `Plane` + `.plane` CSS | one `ContextOrgan` shell with chambers (Plane → chamber kind), shared organ background, membrane separators, bridge from the core |
| FBR-2 | lines read as static connectors | RELATION → VISUAL CLASS → MOTION LAW is absent (only node state) | `projection.ts` (new) + `Orbit` path rendering | derive `relationType` from the canonical relation (containment/lifecycle/participation/governance/capability + state) → class → current motion (dash drift, direction, endpoint resonance) |
| FBR-3 | nodes on one mechanical ellipse, equal mass | SEMANTIC ROLE → PROJECTION CLASS → GEOMETRY not modelled (only ring index) | `projection.ts` + `geometry.ts` | `orbitBand` + `semanticWeight` per node (explicit rules) → band radius factor, weight scale, deterministic organic offsets (hash of the node key) |
| FBR-4 | core reads as a label badge | CORE ANATOMY absent | `FieldCore` + CSS | aura / rings / membrane / nucleus / micro-orbit layers; directional response to the projection-local vector |
| FBR-5 | hover = colour highlight | ENCOUNTER cascade absent (family-level attribute only) | `FieldStage` state | `FieldState` (hovered/focused key + angle, hovered context token) → node aura, related current, core vector, related nodes, chamber preview, trace shimmer, atmosphere wash — all projection-local |
| FBR-6 | breadcrumb generic | TRAVERSAL TRACE anatomy absent | `RelationTrace` + CSS | route nodes, trace, active membrane, shimmer, hover preview reciprocity, mobile chip |
| FBR-7 | background inert to the field | ATMOSPHERE ↔ FIELD STATE absent | `FieldBackground` + stage CSS vars | pressure zone around the core; resonance wash toward the hovered/active vector (projection-local) |
| FBR-8 | phone = list rows; organ = stacked sections | RESPONSIVE = STACKING | `globals.css` phone rules | breathing constellation (wrapping capsule cluster in semantic order) + membrane sheet organ; tablet oval + attached organ |
| FBR-9 | no explicit provenance | PROJECTION AUTHORITY not instrumented | `projection.ts` | `ProjectedValue<T>` with `ProjectionProvenance`; dev assertion + unit falsifiers (weight/type/tone never without a producer; no tension) |

## Phase 6 — Work Units
| WU | Field | Test surface | Browser proof |
|---|---|---|---|
| SF04-WU-01 Projection authority binding | `lib/field/projection.ts`: `SemanticNode/SemanticRelation/FieldState` types, rules RULE-W (weight), RULE-B (band), RULE-R (relation type), RULE-T (tone), provenance; dev assertion | `tests/field/projection.test.ts` (falsifiers 1–3, 7, 11–13) | harness `projection-provenance` state (every node/path carries `data-provenance`) |
| SF04-WU-02 Semantic core organism | `FieldCore` anatomy + CSS + vector response | `sf04-primitives.test.tsx` (layers present, text readable, no spinner keyframes) | core states idle/hover/context |
| SF04-WU-03 Living field entity geometry | `geometry.ts`: bands, weight scale, organic offsets; `Orbit` anatomy | geometry tests (determinism, no random, band radii, offsets bounded) | stress + review states |
| SF04-WU-04 Relational current system | `Orbit` curved paths, classes, motion CSS, endpoint resonance | primitives test (class per relation, direction attr, no tension) | currents by type, hover activation |
| SF04-WU-05 Contextual semantic organ | `ContextOrgan` (shell/header/chambers/bridge/tokens) replacing `Planes` | primitives + mocked spec (no `.plane` cards; chambers; tokens reciprocity) | organ emergence, scroll, reciprocity |
| SF04-WU-06 Traversal trace | `RelationTrace` anatomy + mobile chip | mocked spec (nav semantics kept; chip; no overflow) | desktop/mobile trace states |
| SF04-WU-07 Atmospheric medium | `FieldBackground` pressure/wash | perf-ab; reduced motion | atmosphere states |
| SF04-WU-08 Hover / focus reciprocity | `FieldStage` `FieldState`, cascade attrs, keyboard parity | mocked spec (cascade attrs; no POST; no state) | encounter states |
| SF04-WU-09 Responsive redistribution | CSS classes desktop/tablet/mobile/compact; constellation; membrane sheet | mocked spec 1024 / 390 | tablet + mobile states |
| SF04-WU-10 Typography/containment | keep SF-03 laws under the new anatomy | stress spec | stress states |
| SF04-WU-11 Accessibility/reduced motion | `aria-live` organ, focus, reduced-motion equivalents | mocked spec + axe | reduced-motion states |
| SF04-WU-12 Performance | perf-ab under throttle (currents, core anatomy, atmosphere) | perf report | — |
| SF04-WU-13 Whole-field integration | pages on the organism; lanes; harness; sweeps | full ladder | full harness |

## Case 3
None foreseen: every delta is presentation with explicit projection rules over existing canonical projections; no new
projection/command/capability; tension relations are simply absent (no canonical producer) — recorded, not invented.
