# SF-04 — Accessibility of the organism (doc 25 §18; 22 §34–§35; 21 §31)
FIELD: SF-04 — NQUIRY SYMBIOTIC FIELD ORGANISM

## Laws kept (SF-01/SF-02/SF-03 contracts, re-proven on the final tree)
- DOM order = semantic order = keyboard order (core → current state → human position → effects → relations →
  governance → proof → context); geometry never reorders (22 §34.1). Proven: SF-01 order test (desktop + phone),
  harness keyboard walks on every state (`keyboard.order`).
- Every visual distinction has a textual carrier: node `.node-marker` ("Relation state: …"), core `.core-state`,
  organ `.organ-state`, trace status words; colour, aura, current and motion never carry a meaning alone (22 §35.3).
- A link's/button's accessible name is exactly the entity label; meta and marker are siblings (22 §34.3).

## New in SF-04
| Concern | Mechanism | Proof |
|---|---|---|
| decorative anatomy | every aura, ring, membrane, orbit trace, current, endpoint, bridge, atmosphere layer is `aria-hidden` and `pointer-events: none`; SVG currents are one `aria-hidden` element per orbit | L0 sf04-primitives (attributes); harness axe on every state |
| contextual organ | one `aside[aria-label="Active semantic context"][aria-live="polite"]`: route changes announce the reconstructed context quietly; chambers keep their `section` + headings (`aria-labelledby`), forms and controls unchanged | L0 organ tests; L3 organ tests; harness "one contextual organ: live region" |
| encounter parity | keyboard focus writes the same attributes as pointer hover (`data-encounter="focus"`, same key, same vector, same resonance); `:focus-visible` rings (`--field-focus-ring`, 2 px, offset 2–3 px) on node controls, trace links, chip and organ controls | L3 "keyboard focus produces the identical cascade … focus ring is visible"; harness state 48 + `keyboard.withoutVisibleFocus = []` on every state |
| trace chip (phone) | `button[aria-expanded][aria-controls]` with a visible "+N" and a visually-hidden "Show/Hide the route" name; collapsed route nodes stay in the accessibility tree (visually hidden, links still reachable), never `display: none` | L3 phone trace test; SF-01 mobile trace tests (list-item counts unchanged); harness state 53 |
| reduced motion | the global `prefers-reduced-motion` rule removes every animation and transition (elements and pseudo-elements); every layer, attribute and text stays; encounter attributes still switch (no motion needed to perceive them) | L3 reduced-motion suites (core, organism); harness reduced-motion states 2, 46, 51 |
| legibility | type floors unchanged (node 0.86 rem, sm 0.8 rem, meta 0.74 rem, marker 0.72 rem, eyebrow 11.2 px); mass never scales type; containment probes at 8 widths | sf03 stress spec; sf04 responsive suite; harness containment on every SF-04 state |
| motion fatigue (doc 25 §18.5, §23.10) | breathing 9–18 s, currents 9 s single pulse, micro-orbit 48 s, hover 280/420 ms, organ emergence once (640 ms); no flashing, nothing faster than 3 Hz | stylesheet tokens; perf-ab variant G |

## axe (WCAG 2 A/AA, all impacts) — harness
Recorded per state in `browser-evidence/run-N/results.json` (`axeSeriousCritical`, `axeOther`); a state fails on any
serious/critical violation. Results: see FIELD_REVIEW.md (final run).
