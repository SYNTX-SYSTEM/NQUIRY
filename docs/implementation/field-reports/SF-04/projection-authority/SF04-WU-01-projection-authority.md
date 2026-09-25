# WORK UNIT REPORT
FIELD: SF-04 — NQUIRY SYMBIOTIC FIELD ORGANISM
WORK_UNIT: SF04-WU-01 — Projection Authority Layer (doc 25 §2.7, §5.2–§5.4, §7.3–§7.5, §8.2, §16.2–§16.6)

## Field
`apps/web/lib/field/projection.ts` (new). Pure, deterministic derivation from the canonical inputs the pages already
read (capabilities, projections, lifecycle phases, participants, authority bindings — bound to their producers in
SF-02/WU-SF02.0) to the visual semantics the organism renders. Every semantic value is a `ProjectedValue<T>` with
`ProjectionProvenance`:
| Rule | Derives | From | Never from |
|---|---|---|---|
| RULE-W | `semanticWeight` (0.4–1) | canonical node state (current 1 · possible 0.9 · governance 0.75 · human 0.72 · established/frozen 0.7 · loading/unavailable 0.5 · unknown/future 0.45 · denied 0.4) + 0.08 per additional canonical relation, capped at the current phase | label length, size class, position, looks |
| RULE-B | `orbitBand` | relation family: containment/capability/lifecycle → inner; participation/governance → middle; evidence → outer | pixel position |
| RULE-R | relation `type` + `direction` | family × state: capability possible → directional core→node; containment established → directional core→node; containment/lifecycle current → context (bidirectional); participation → reciprocal bidirectional (F03 PARTICIPATION is typed on both sides); governance → directional node→core; unavailable/denied/loading/unknown → latent; passed/later lifecycle → latent | motion, hover, designer preference |
| RULE-T | `visualTone` | state → living / stable / boundary / neutral (22 §18) | a fifth category |
`assertProvenance()` is the development guard (thrown in `Orbit` outside production): a value without a producer or
an approved rule id, or any relation claiming `tension`, throws.

## Tension
No canonical tension relation exists in this repository (no producer projects conflict/contradiction). The visual
class `tension` therefore exists in the type (`RELATION_TYPES`) but can never be produced — recorded, not invented
(doc 25 §21.11 falsifier 3). Case 3 is not raised: nothing canonical is missing for the approved organism.

## Tests (RED first: module absent → 15 GREEN)
`apps/web/tests/field/projection.test.ts`: weight determinism + provenance shape; weight order by state (never by
label length); relation density; bounds [0.3, 1]; band mapping; relation types per family/state; **tension is never
produced** (every family × every state); tone mapping; provenance guard accepts/rejects (designer preference is not
provenance; tension is rejected).

## On the DOM (WU-03/04 wiring)
`li.node[data-band][data-tone][data-role][data-provenance="RULE-W;RULE-B;RULE-T"]` with `--mass` (geometry) and
`--weight`; `g.relation[data-relation-type][data-direction][data-provenance="RULE-R:canonical-relation:…,canonical-state:…"]`.
A reviewer can read every visual claim's rule on the element (doc 25 §5.4 Z9).

## Result
PASS — 15/15; tsc 0; no DOM read, no viewport, no random, no animation state in the module.
