# SF-01 PROOF MATRIX

Every SF-01 claim → governing law (doc 21, falsifier F-n from §42) → the lanes that prove it → RED evidence.

Lanes:
- **L0**: pure vitest.
- **L1**: static markup, no CSS.
- **L3**: isolated MOCKED browser, component contract only (`playwright.sf01.config.ts`, :3301, dead-proxy fail-closed; desktop + Pixel 7).
- **L5**: static gates / build / diff.
- **L7**: isolated REAL stack (`scripts/run_sf01_real_stack.sh`, project `nquiry-sf01`; desktop + Pixel 7).

RED key:
- **A**: module absent before implementation.
- **B**: failed against the pre-SF-01 pages (`bea864b`, L3, 19/21 failed).
- **P**: predicate proven against a planted violation.
- **R**: failed before the WU-SF01.7 repair.
- **—**: none demonstrated (disclosed).

| # | Claim | Law | L0/L1 | L3 | L5 | L7 | RED |
|---|---|---|---|---|---|---|---|
| T1 | Position is a Relation Trace built only from confirmed server projections; loading and NOT_FOUND keep only the confirmed access context | 21 §12, §14, CF-01 | `position.test` (12), `primitives` RelationTrace | trace from projection; unconfirmed → access only; NOT_FOUND invents nothing | — | exact trace data; **reload rebuilds an identical trace** | A, B |
| T2 | No Session coordinate exists before `CreateSession` commits | 21 §12, CF-02 | `position.test` | Challenge / Workspace traces | — | `session-state` absent on the Challenge page | A, B |
| T3 | The Session / Challenge relation is `possible` only when the server projects it, else `unavailable` with the server reason | 21 §12, §13, CF-07 | `position.test` | Workspace possible; Challenge unavailable | — | Owner: Challenge unavailable; Facilitator: possible; Session **unavailable → possible only after a real grant** | A, B |
| T4 | A future relation is never a navigable destination | F32 | `position.test`, `primitives` (2 hrefs only) | future segments have no link | — | (covered by the T1 data) | A, B |
| T5 | Session identity is server-projected (state + opening time), not a client ordinal | CF-02 | — | "Session opened …" + SYSTEM STATE; no "Session 1" | — | same, on a real Session | B |
| T6 | REQUESTED ≠ COMMITTED: no outcome and unchanged canonical state until the server answers | 21 §17, F7, F8 | reducer; `EffectIntent` | held request: intent shown, list unchanged, control disabled | — | — | A, B |
| T7 | "Re-read" is claimed only after the canonical re-read happened | 21 §22, F27 | `primitives` | held re-read: `reading` without the claim → `done` with it | — | commit markers after add-member and grant | A, B |
| T8 | C3-06: a committed but unreadable effect stays committed, the view is marked last-confirmed, dependent effects are blocked, and a manual re-read restores it | 21 §22, C3-06 | reducer; `primitives` | re-read aborted after commit | — | same machinery on the real offline path (network outcome, see T9) | A, B |
| T9 | C3-01: transport loss on a mutation → UNKNOWN consequence (never "nothing changed"), reconciled by re-read; repeating the intent reuses its Idempotency-Key | 21 §14, §39, C3-01, F17 | `outcomeSemantics` (F17 predicate catches the F02 text) | aborted POST → unknown, re-read, same key on repeat | — | **real browser offline** → unknown + last-confirmed → re-read → repeat → **exactly ONE Challenge** | A, B, P |
| T10 | Server INDETERMINATE retains the intent; a definitive outcome releases it | 21 §14, F18 | reducer | indeterminate → same key; denied → new key | — | — | A, B |
| T11 | A response outside the known vocabulary is INDETERMINATE, never a failure | 21 §14 | `useEffectField` (thrown `send`) | 500 text body → indeterminate / unknown | — | — | B |
| T12 | Keyless F01 founding: lost response → unknown, list re-read, never "try again" | C3-01 | — | aborted `POST /workspaces` | — | — | B |
| T13 | Boundary taxonomy: every kind has its own title, consequence and role | 21 §14, §39, F21, F22 | `outcomeSemantics`, `primitives` (9 distinct texts) | denied / rejected / failed_precommit / indeterminate each distinct | — | real `rejected` (malformed id) | A, B |
| T14 | Affordance only from server capability; unavailable → server reason and no control; no role inference | 21 §13, CF-07, F14 | — | unavailable Open Session | gate: no role / viewer-flag comparisons | F02 specs + SF-01 unavailable reason | P (gate); L3 passed on baseline (held since F02) |
| T15 | Proof is depth: D2 closed by default, keyboard-openable in place, focus kept, **visibly openable** | 21 §15, §35, §40, F23, F26 | `primitives` ProofDepth | keyboard open, focus kept, URL / position kept, marker ▸/▾ | — | keyboard open on the real Challenge page; visual check | A, B, **R** |
| T16 | Origin grammar: each class named in words; AI-derived impossible without lineage; Human ≠ AI markup | 21 §16, F11, F24 | `primitives` | SYSTEM STATE on Session items | — | SYSTEM STATE on a real Session | A (grammar only; applied only to SYSTEM STATE) |
| T17 | Relational order: position → active relation → affordance → proof; no horizontal overflow | 21 §30, §34, F28 | `primitives` FieldFrame DOM order | bounding-box order on Pixel 7; overflow ≤ 1 | — | overflow ≤ 1 on every SF-01 surface, desktop + mobile | A, B |
| T18 | Reduced motion removes animation, not meaning | 21 §33, F25 | — | `animation-name: none`, text and role kept | — | same on real outcomes | B |
| T19 | Accessibility: axe WCAG 2 A/AA serious/critical = 0 | 21 §35 | — | — | — | 0 on access, Workspace (owner + member), Challenge, proof open; desktop + mobile | — (F02's negative control proves the axe injection detects violations) |
| T20 | Impossible in SF-01 code: timers, role inference, F03 vocabulary, AI invocation, client persistence, contact-zone imports | SF01-HD-3, 21 §43 | — | — | `gates.test` (13), each predicate P-proven | — | P |
| T21 | F03 contact zone, backend, migrations, deps and existing tests untouched; CSS append-only | SF01-HD-3 | — | — | diff gate vs `bea864b`; `globals.css` 0 removed lines | — | — |
| T22 | No F01/F02 regression | 20 §12 | vitest 98 baseline | 39 existing mocked specs | build 8 routes | F02 flow, a11y, WU-02.12 closure (6/6) | — |
| T23 | Isolation from the running F03 environment | SF01-HD-2 | — | unmocked call to live `:8000` fails closed | — | guard: project `nquiry-sf01`, no host ports; F03 containers untouched | — |

## Not claimed (out of SF-01 scope)
- Session page semantics (F03 contact zone). It still shows the F02 wording "Nothing is assumed to have changed" (F17 residual) until Stage 2 after F03.
- Human Source, freeze, capture, completion: WAIT_FOR_F03.
- AI derivation, results, evidence: WAIT_FOR_F04 or later.
- PENDING as a separate phase: no F02 producer (OR-I).
- Previous-state provenance (OR-C). Challenge authorship origin (OR-D).

## Totals (final tree)
- vitest **170** passed.
- Isolated mocked lane **81** passed (39 existing + 21 SF-01 × 2).
- Isolated real stack **10** passed (6 F02 regression + 4 SF-01).
- eslint and tsc clean; `next build` 8 routes; `git diff --check` clean.
