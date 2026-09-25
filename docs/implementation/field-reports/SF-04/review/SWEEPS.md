# SF-04 — recursive and inverse deep sweeps (final tree)
FIELD: SF-04 — NQUIRY SYMBIOTIC FIELD ORGANISM

## Recursive sweep (from the code outward: every SF-04 artefact → its consumer, its test, its evidence)
| Artefact | Consumer | Test | Evidence | Finding |
|---|---|---|---|---|
| `lib/field/projection.ts` | `Orbit` (`projectNode`, `projectRelation`, `assertProvenance`), `FieldStage` (`ProjectedFieldState`) | projection.test (15), sf04-primitives | DOM `data-provenance` on every entity/current (harness organismChecks) | none |
| `lib/field/geometry.ts` (bands, mass law, organic-by-room) | `Topology`/`Orbit`/`stageMode` | geometry.test (15) | wide states 19/34/35 orbit again (run-3/4) | none |
| `FieldCore` layers | pages (unchanged props) | sf04-primitives, sf04 spec core suite | states 41–52 | none |
| `Orbit` currents + anatomy | pages (`nodeContent(n, kind)`) | sf04-primitives, sf04 spec currents suite | states 41–52 | none |
| `FieldStage` encounter + organ + atmosphere | pages (`Planes header`) | sf04-primitives, sf04 spec encounter/organ/atmosphere | states 47–49 | none |
| `RelationTrace` route nodes + chip | `FieldFrame` | sf04-primitives, sf04 spec trace, SF-01 trace tests | states 45/46/53 | none |
| `globals.css` | all | sf03/sf04 computed-style probes; perf-ab | screenshots | **residue**: selectors `.plane-column`, `.stack-column`, `.orbit-heading` (SF-02/SF-03) and `.card-link`, `.grid-2`, `.phase-status` (pre-SF legacy) match no element; doc 25 §17 tokens `--field-line-idle`, `--field-line-latent`, `--field-node-membrane`, `--motion-shimmer`, `--radius-core` are defined but not yet consumed (the SF-02 tone/edge tokens still carry those roles). Recorded, not changed after the evidence runs (a dead selector cannot alter rendering; token consolidation is listed for the human) |
| `data-*` written but without a CSS rule | review/tests only (`data-band`, `data-provenance`, `data-hover-key`, `data-fit`, `data-needed-h`, `data-boxes`, `data-measured`, `data-viewport`, `data-key`, `data-core-kind`) | — | harness/DOM inspection | by design: reviewer-facing and test-facing attributes; styling keys on `data-tone`, `data-relation-type`, `data-direction`, `data-resonating`, `data-encounter`, `data-chamber*`, `data-status`, `data-expanded`, `data-topology`, `data-core-state`, `data-node-*` |

## Inverse sweep (from the architecture and the earlier contracts inward)
| Source | Every item traced to | Finding |
|---|---|---|
| doc 25 §21.11 falsifiers 1–15 | PROOF_MATRIX §A (mechanism + test + evidence per falsifier) | all bound |
| doc 25 §23 non-negotiables 1–25 | PROOF_MATRIX §C | all bound |
| doc 25 §6–§15 organs | WU reports 02–04, 05–09 | all materialized; `tension` intentionally absent (no canonical producer) |
| doc 25 §17 tokens | `:root` | defined; five not yet consumed (above) |
| doc 23 (SF-03) laws | regression: sf03 spec 21/21, harness states 31–40 | two contracts superseded by doc 25 and re-bound (phone rows → capsules; breakpoints 860/1100 → 768/1200), recorded in CHATGPT_REVIEW §3 |
| doc 22 (SF-02) laws | sf01/F01/F02 mocked specs, harness states 1–30, real stack | one assertion re-bound (`<line>` → `<path>`) |
| doc 21 (SF-01) laws | primitives.test, sf01 spec (desktop + phone) | trace semantics kept; chip keeps route nodes in the accessibility tree |
| the mandate's forbidden moves (dashboard in space, prettier sidebar, decorative animation, motion without relation meaning, invented semantics) | PROOF_MATRIX §B | none occurs |

## Deferred ledger (for the human; nothing here blocks the review)
1. Remove the six dead selectors and adopt the five unused §17 tokens in one stylesheet consolidation pass (after the review, so the proven tree stays the reviewed tree).
2. `tension` relation class: wire RULE-R when a canonical producer exists.
3. Semantic-weight visibility (aura/role/padding only) — human judgement.
