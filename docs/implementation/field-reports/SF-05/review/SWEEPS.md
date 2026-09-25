# SF-05 — recursive, inverse and forward sweeps (doc 26 §56)

## Recursive sweep (producer → consumer → parent → siblings → authority → runtime → API → frontend → tests → reports → responsive → reduced motion → evidence → performance)
| Artefact | Consumers | Tests | Evidence | Finding |
|---|---|---|---|---|
| `lib/field/workspaces.ts` | `app/workspaces/page.tsx` (nodes, rings) | workspaces.test (7), sf05 spec Workspace suite | H 57–60 | none |
| `components/field/chambers.tsx` | four field pages, `Unavailable`, `BurstCapturePanel`, `SessionViewContainer` | sf05-primitives (9), sf05 spec chambers suite | H 61–68 | none |
| `Plane` (`data-semantic`) | pages | sf03/sf04/sf05 primitives | H | SF-04 chamber law re-bound (faint membrane) — recorded in tests/SF05-tests.md |
| `lib/field/fieldEvent.ts`, `FieldEvent.tsx` | Workspace, Challenge, Session pages (descriptions at request time) | fieldEvent.test (4), sf05 commit suite | H 12 | Workspaces founding, Challenge framing and Session opening navigate away on commit (no re-read on the origin surface) → no event by design; the destination field is the effect. Recorded as an observation |
| login page + `FieldBackground` dense group | `/login`; every surface's ambient depth | sf05 login suite, auth.spec | H 54–56 | none |
| `RelationTrace` + path CSS | every field page | sf05 breadcrumb suite; sf01/sf03 trace tests | H 66 | none |
| `SessionViewContainer` + decision page | `/decision` | sf05 decision suite; session-view/decision specs | H 68 | none |
| intensification CSS | all fields | sf05 intensification; sf04 spec (30) | P variants I/J/K | none |
| stylesheet residue | — | — | — | unchanged SF-04 ledger: `.card-link`, `.grid-2`, `.orbit-heading`, `.phase-status`, `.plane-column` match no element; the doc 25 §17 tokens `--field-line-idle/latent`, `--field-node-membrane`, `--motion-shimmer`, `--radius-core` still unconsumed; consolidation deferred to after the human review (reviewed tree = proven tree) |
| data-* written but unstyled | review/test-facing (`data-band`, `data-provenance`, `data-scope-type`, `data-binding`, `data-user`, `data-human-only`, `data-verified`, `data-reason-code`, `data-burst-state`, …) | by design | — | none |
| large-area gradients | organ / chambers / access core / decision: none (doc 26 §36) | perf-ab | P | none |
| backend paths (`apps/api`, `packages`, `migrations`) | — | — | — | no diff in this worktree; RED worktree not touched by this run |

## Inverse sweep (VISIBLE EFFECT → consumer → relation → producer → authority → state → root) — see architecture-binding/SF05-WU-26.0-field-reconstruction.md (15 FBR chains) and SF05-WU-26.1-26.9-repairs.md (roots).

## Forward sweep (ROOT → boundary → delta → propagation → re-proof → reconstruction → visible effect)
| Root | Boundary respected | Delta | Propagated to | Re-proof | Visible effect |
|---|---|---|---|---|---|
| normalization producer | no API change, no dedup by name | `normalizeWorkspaces`, `segmentWorkspaces` | overview page, harness check | L0/L3/H | one node per Workspace, distinguishers, two rings |
| chamber grammar | test ids, texts, DOM order, a11y | `chambers.tsx`, `Plane` semantic, CSS | four pages, burst panel, frozen set, `Unavailable`, decision container | L0/L3/H/L7 | one organism of differentiated chambers |
| event derivation | never before re-read, never as truth, no timer | `fieldEvent.ts`, `FieldEvent.tsx`, quiet outcome | three pages | L0/L3/H | bloom after confirmation, proof line stays |
| login attention | no success before verdict | attributes + CSS + dense group | login page, background | L3/H/auth.spec | living entry |
| breadcrumb compression | route meaning, links, a11y text | CSS + titles | every field | L3/H/sf01/sf03 | one path at desktop widths |
| decision container | components/test ids/data | frame + chambers | `/decision` | L3/H/decision + session-view specs | symbiotic surface |
| intensification | no layout shift, no large repaint | CSS + breath phase | all fields | L3/P | alive, calm |
