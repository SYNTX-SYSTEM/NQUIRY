# SF-04 — Human frontend review guide (visible website; doc 25 §22 review protocol)
FIELD: SF-04 — NQUIRY SYMBIOTIC FIELD ORGANISM · status at hand-off: READY_FOR_HUMAN_FRONTEND_REVIEW (uncommitted tree)

## Where to look
| Item | Value |
|---|---|
| inspection runtime (built from this tree, isolated DB) | http://127.0.0.1:13400 |
| identities | owner@inspect.local.test / inspect-owner-2026 · facilitator@inspect.local.test / inspect-fac-2026 · outsider@inspect.local.test / inspect-outsider-2026 |
| scenario | Workspace "SF-03 Inspection" → Challenge "Why did activation stall after onboarding?" (1 Session, frozen human question set); a STRESS Workspace/Challenge with 104/150-character names |
| evidence run (final tree) | `browser-evidence/run-7/` — `MANIFEST.md`, `results.json`, `screenshots/NN-viewport-state.png` (53 states) |
| earlier runs | run-1 (41/53), run-2 (48/53), run-3…run-6 (53/53, before the height-derivation and performance repairs) — kept as the RED trail |

## Review walk (each item names the doc 25 §22 review it serves and the screenshot to compare with)
1. **Field coherence (§22.1)** — log in as the facilitator, open the Challenge at ≥ 1600 px: `41-wide-organism-challenge-wide.png`.
   Expect: one organism — a nucleus with aura, three irregular resonance rings and a membrane; the "Open Session"
   entity on a dashed directional current, the Session on a solid current, the controller on a governance current
   flowing toward the core; the contextual organ attached at the right with "GROWN FROM … · 1 Session", three
   chambers on one surface with membrane dividers, a bridge from the field. Nothing reads as a panel grid.
2. **Projection authority (§22.2)** — open DevTools on any entity: `data-band`, `data-tone`, `data-role`,
   `data-provenance="RULE-W;RULE-B;RULE-T"`; on any current (`g.relation`): `data-relation-type`, `data-direction`,
   `data-provenance="RULE-R:canonical-relation:…,canonical-state:…"`. Compare with the server projection
   (`GET /api/workspaces/{w}/challenges/{c}`): every entity is a projection element; nothing else exists.
3. **Semantic motion (§22.3)** — watch 30 s: the aura breathes (12 s), rings breathe by ≤ 2.4 %, the micro-orbit
   dot travels once per 48 s; the possible current drifts core → node; the governance current drifts node → core;
   the established Session current drifts core → node. Nothing spins, nothing flashes. Then hover the controller:
   `48-desktop-encounter-pointer-controller.png` — aura + membrane of the entity, its current thickens and speeds,
   the core leans toward it, "Inspect Facilitator" in the Governance chamber resonates, the chamber previews, the
   atmosphere washes toward the entity. Tab to the Session link: the identical cascade with a focus ring
   (`49-desktop-encounter-keyboard-session.png`). Nothing is requested (network tab stays quiet).
4. **Readability (§22.4)** — STRESS Challenge (facilitator) at 1280 and on a phone: `40-pixel-7-stress-…`,
   SF-03 states 37–39; every label complete, nothing below 11.5 px, no frame overlaps.
5. **Dashboard residue (§22.5)** — the organ: no per-chamber borders or shadows; the header names the state it grew
   from; chambers are divided by membranes; on the Session field the primary chamber carries an inset wash for
   human/frozen states (`50-desktop-organism-session-desktop.png`, `35-wide-session-field-wide-frozen.png`).
6. **Organismic presence (§22.6)** — tablet 1024 (`44-tablet-…`): the field oval on top, the organ attached below;
   1150 px (`43-threshold-…`): same, no horizontal overflow (the SF-03 weakness); phone (`45-pixel-7-…`,
   `46-compact-…`): a bounded core organism, capsule clusters in semantic order, the membrane sheet organ, the trace
   chip "+3" that expands the route (`53-pixel-7-trace-chip-expanded-phone.png`).
7. **Authority falsifiers (§22.7)** — as the outsider (states 24–29 in the manifest): denied/rejected/not-found
   boundaries unchanged; no organ chamber offers an effect the server did not project; reduced motion
   (`47-…reduced-motion…`, `52-…reduced-motion…`): every layer and every state word stays, nothing moves.
8. **Session field** — facilitator, the frozen Session (`50-desktop-organism-session-desktop.png`,
   `35-wide-session-field-wide-frozen.png`): the current phase as a breathing context current, passed/later phases
   as latent traces, both participants on reciprocal (alternating) currents, controller mirrored in the organ.

## Human items (recorded, not blockers)
1. Visual sufficiency of semantic weight (aura presence + role indicator + padding; the type never scales).
2. On a 1280 px desktop the Session field with 13 phases decides orbit or constellation from the rendered frames;
   confirm the constellation is acceptable where it occurs (the wide desktop keeps the orbit: states 19, 35, 52).
3. Doc 25 §17 tokens live beside the SF-02 tokens (no removal).
