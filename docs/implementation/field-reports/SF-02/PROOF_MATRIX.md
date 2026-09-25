# SF-02 PROOF MATRIX

Every doc 22 falsifier (§41, 1–77) → the lane(s) that would turn it RED → the evidence on the final tree.
This is the INVERSE deep sweep: from the architecture's falsifiers to the repository, not from the code to
the claims.

Lanes:
- **L0**: pure vitest (`apps/web/tests/field/*`, 219 on the final tree; RED non-vacuity of the SF-02 files
  against the pre-SF-02 tree `644e1c8`: see STATUS.md "RED evidence").
- **L3**: isolated MOCKED browser (`playwright.sf01.config.ts`, :3301, dead-proxy fail-closed; desktop + Pixel 7; 81).
- **L5**: static gates (`gates.test.ts`), tsc, eslint.
- **L7**: isolated REAL stack (`scripts/run_sf01_real_stack.sh`, project `nquiry-sf01`, no host ports; desktop + Pixel 7; 14 specs).
- **E**: browser evidence harness on the isolated inspection runtime (`review/browser-evidence-2026-09-25/`,
  30 recorded states; final = run-6), real Chromium, no interception, canonical state read from the API per state.
- **H**: human review of the screenshots (visible-identity claims that no assertion can establish).
- **C**: code-level fact (cited file), disclosed as not machine-proven.

| # | Falsifier | Lane(s) | Evidence on the final tree |
|---|---|---|---|
| 1 | UI claims authority the backend does not establish | L3, L7, E, L5 | every control comes from `capabilities.*` / `actions.*`; gate "no role inference"; E rows 14/16 (unavailable with server reason), F02/F03 real specs (`action-reason-*`) |
| 2 | possible relation while capability false | L0, L3, L7, E | `affordanceState` (topology.test); e2e "unavailable relation renders the server reason and no control"; E rows 8/10/14 |
| 3 | unavailable appears possible | same | node state `unavailable` + reason `describedBy`; no control rendered |
| 4 | topology changes before commit | L3, E | e2e "REQUESTED is not COMMITTED: canonical state unchanged"; E row 21 "no frozen topology before commit" |
| 5 | failed command produces success topology | L3 | e2e boundary taxonomy (denied/rejected/stale/blocked/failed_precommit/indeterminate/not_found): list unchanged, distinct `data-outcome` |
| 6 | re-read disagrees and visible state persists | L0, L3 | C3-06 reducer + `primitives` "marks the projection as last confirmed only when a re-read failed"; e2e C3-06 |
| 7 | loading invents truth | L0, L3, E | `position.test` (loading keeps only the confirmed access context); e2e unconfirmed trace; E row 29 (loading core, trace = access only, no nodes) |
| 8 | unknown looks established | L0, L3, E | `outcomeSemantics` network_failure = unknown consequence; e2e C3-01; E row 30 (offline mutation → unknown, same key) |
| 9 | denied leaks protected context | E, L7 | E row 26 "no Workspace name leaked" + reason = server; F03 real spec cross-read/cross-write denied |
| 10 | rejected collapses into denied | L0, L3, E | `primitives` "every settled kind is distinct"; e2e taxonomy; E rows 17 (rejected) vs 26 (denied) |
| 11 | unavailable collapses into denied | L3, E | unavailable = node + reason (no boundary); denied = boundary core (red); E rows 14 vs 26 |
| 12 | not found leaks stale field state | L3, E | e2e NOT_FOUND reconstructs to the nearest confirmed context; E row 27 (trace = access only, 0 nodes) |
| 13 | read failure uses mutation language | L0 | `outcomeSemantics.test` READ_TITLE for indeterminate on the read path (SF-01 review D-2 closed) |
| 14 | command failure implies commit | L3 | e2e "a proven rollback is shown as failed_precommit, never as a rejection or a success" (F02 spec, unchanged) |
| 15 | mock appears authoritative | L5, E | gate: no F04 vocabulary / no mock provider; E runtime has no mock (real API per state, HTTP log per state) |
| 16 | mock appears as proof | L5 | same gate; the mocked lane is a test lane only (`playwright.sf01.config.ts`) |
| 17 | frozen question becomes editable | L7, E | F03 real spec (frozen set, `frozen-verified`); E rows 22–24 "no capture form; no editable control" |
| 18 | participant sees peer question during own-only active Burst | L7, E | F03 real spec (`body` never contains the peer text); E row 19 "peer question absent" |
| 19 | non-controller receives controller effect | L7 | F03 real spec: participant complete → denied; owner capture → denied (API + UI) |
| 20 | controller affordance for non-controller | L7, E | F03 real spec (`Complete Burst` count 0 for owner; `action-reason-CAPTURE_QUESTION` contains "participant"); E rows 14, 19 |
| 21 | responsive layout changes semantic order | L3, E | e2e "DOM and visual order follow the relation"; E rows 20/24 stack order checks; `Orbit` = one `<ul>` in semantic order (C) |
| 22 | reduced motion changes meaning | L3, E | e2e "reduced motion removes animation but not meaning" (pseudo-elements included after D1); E rows 5/6/13 |
| 23 | orbit proximity implies nonexistent hierarchy | H, C | nodes evenly spaced by index (`orbitPositions`); no adjacency semantics in code; human review of screenshots |
| 24 | relation path without real relation | C, L0 | `Orbit` renders exactly one path per projected node (`Orbit.tsx`); nodes only from projections (pages) |
| 25 | background motion implies state change | C, L3 | `FieldBackground` is `aria-hidden`, regime bound only to the canonical core regime (pages: `regime=`); reduced-motion test removes it; no state check reads it |
| 26 | stale visible topology survives authoritative change | L3, E | every commit re-reads the canonical projection before the commit marker (e2e "commit marker claims a re-read only after"); E row 15 "governance node appears after re-read" |
| 27 | hidden local state overrides backend | L5, L0 | gate: no client persistence; one lifecycle per surface; `useEffectField` re-read is the only source of post-commit state |
| 28 | selection implies authority | L7 | admit select → server verdict (F03 real spec `Admit to Session` enabled only for candidates; committed only by the server) |
| 29 | hover reveals protected content | C, H | no hover-only content; proof is explicit activation (`ProofDepth` = native `<details>`); e2e proof depth by keyboard |
| 30 | green becomes field identity | L5 | gate "green is not a Field identity" over `globals.css` |
| 31 | red for an ordinary active relation | H, C | red tokens only on boundary selectors (`[data-outcome]` boundaries, `data-core-state="boundary"`, `unavailable/denied` markers); `future` lifecycle nodes neutral (`.node[data-node-state="future"]`) |
| 32 | cyan implies success before commit | L3, E | held request shows intent (no outcome, no cyan success); committed = blue; E row 15 "no cyan/green success" |
| 33 | proof inaccessible for a material authority claim | L3, E | e2e "authority proof … opens in place by keyboard"; E "proof reachable" checks; `session-last-transition` always visible |
| 34 | governance collapsed into a generic admin table | H, E | governance ring (holder, granted-by, scope) + governance plane; E rows 11, 15, 22 |
| 35 | Challenge Field looks like a detail page with a list | H, E | E rows 11–13 (PRIMARY): core central, sessions orbit, governance orbit, paths, proof depth, living background |
| 36 | Session Field as static process page | H, E | 13-state lifecycle ring reconstructed from `phases[]`; E rows 14–24 across DRAFT → QUESTION_CAPTURE |
| 37 | human capture relocated into QUESTION_CAPTURE | L7, E | F03 real spec; E row 22/24: no capture form in QUESTION_CAPTURE |
| 38 | QUESTION_CAPTURE treated as active human generation | L7, E | core regime `frozen` in QUESTION_CAPTURE + COMPLETED Burst; `human` only for ACTIVE HUMAN_ONLY |
| 39 | frozen artifact before close-generation commit and re-read | E, L0 | E row 21 (requested, not committed: no frozen set) → row 22 (after commit + re-read); reducer order (settle → reconstruction) |
| 40 | analysis proposal treated as accepted analysis | — | not applicable: no analysis relation exists in this tree (absent, not mocked) |
| 41 | F04 MockProvider ceiling bypassed | L5 | gate: no `MockProvider` / `ai_gateway` / `AIOP` / `BEGIN_ANALYSIS` in Field sources |
| 42 | external auth provider displayed without authority | E | E rows 1/3 "no external provider" (only the local credential form exists) |
| 43 | loading skeleton implies number/identity of relations | E, L3 | E row 29 "no nodes while loading"; `projection-pending` is a text placeholder, never a count |
| 44 | not-found preserves prior entity details | L3, E | as 12 |
| 45 | denied and rejected identical | L0, E | as 10 |
| 46 | boundary red animation flashes | C | no animation on any boundary selector (`globals.css`: boundary core = static box-shadow) |
| 47 | background reduces contrast | E, L7 | axe serious/critical = 0 on all 30 states (contrast computed against the stacked background); D4 repair (no opacity animation on text) |
| 48 | orbit-only geometry carries meaning unavailable to screen readers | L0 | `primitives` "every node states its relation in text"; SVG paths `aria-hidden`; markers "Relation state: …" |
| 49 | keyboard order follows the visual orbit | L0, L3, C | `<ul>` order = semantic order; e2e DOM-order test; L7 keyboard-only specs (F02/F03 a11y) |
| 50 | mobile stack hides governance before an authority-dependent action | E | stack order core → lifecycle → active phase → governance → proof, all rendered (E rows 20/24); the core sentence states the controller relation first |
| 51 | proof drawer traps focus | L0, L3 | `ProofDepth` native `<details>` (no trap, returns in place); e2e keyboard proof test |
| 52 | resize changes semantic state | L0, C | `topology.ts` reads no viewport; stack is CSS-only (`@media`), same DOM (E effectiveMode vs `data-topology`) |
| 53 | local form draft becomes a submitted question without commit | L7, E | F03 real spec (rejected: text retained, `own-questions-empty`); E row 17 "text retained, nothing stored" |
| 54 | pending request displayed as committed | L3, E | e2e REQUESTED ≠ COMMITTED; E row 21 |
| 55 | authority path lacks source/scope | E, L7 | governance nodes carry holder · granted by · scope; `session-last-transition` shows authority source + scope; E row 22 `establishedBy = CMD_COMPLETE_BURST` |
| 56 | grant affordance lacks capability binding | L7, L5 | grant forms only with `capabilities.grantSessionControl` / `actions.GRANT_SESSION_CONTROL`; F02 real spec; gate |
| 57 | role marker inferred from presentation grouping | L0, L5 | `humanPosition` from projection only; gate allowlist |
| 58 | historical path without authoritative history relation | C, L0 | `path: historical` only for `phases[].status === "done"` (server) |
| 59 | verification displayed without source | L7, E | `frozen.verified` + fingerprint from the server (F03 `verify_frozen_set`); E row 22 "verification" |
| 60 | reduced motion removes relation distinction | L3 | e2e reduced-motion test asserts every effect meaning (text + data attributes) with animations off |
| 61 | capability unreachable solely because of viewport/a11y/reduced motion | L7, E | F03 a11y spec on Pixel 7 (keyboard-only capture + completion); E phone rows "capture reachable on phone" |
| 62 | valid effect hidden by responsive compression | E, L7 | as 61 (same DOM, stack transformation; no `display:none` of controls in `@media`) |
| 63 | required proof removed by drawer/panel choice | L3, E | native disclosure in place; "proof reachable" checks |
| 64 | proof presentation changes review meaning without Case 3 | WU-SF02.0 | no Case 3 raised; proof content = server provenance verbatim |
| 65 | primary surface describable as header + cards + forms | H | screenshots 11–13; STATUS "visible identity" |
| 66 | Challenge Field does not make the difference visible | H | same |
| 67 | Session Field collapses into a static page | H, E | as 36 |
| 68 | repository shape assumed without inspection | WU-SF02.0 | binding table (22 §9 relations → real contracts) written before implementation |
| 69 | technical detail escalated to Case 3 | WU-SF02.0 | zero Case 3; 45.1–45.6 closed as Case 1 by repository fact |
| 70 | repository contradiction silently ignored | WU-SF02.0 | protected-semantics check §43: none found; D-2 recorded and repaired |
| 71 | backend semantics rewritten for visual ease | L5, diff | `apps/api/**`, `packages/**`, `migrations/**`, `lib/api/inquiryClient.ts` unchanged (git status) |
| 72 | real relation replaced with mock | L5, E | no mock in Field sources; E uses the real API per state |
| 73 | open relation treated as human-required for lack of a name | WU-SF02.0 | all names resolved by inspection |
| 74 | accessibility mode removes a material authoritative relation | L3, L7 | reduced-motion e2e keeps every meaning; keyboard-only real specs |
| 75 | performance optimization removes capability | C | none performed |
| 76 | mobile removes the controller close action while capable | L7 | F03 a11y spec `mobile` project: controller completes by keyboard on Pixel 7 |
| 77 | reduced motion removes frozen transition meaning | L3, C | frozen meaning = blue core state + "FROZEN" tag + text (no motion carrier); reduced-motion e2e; **not** recorded as a reduced-motion frozen screenshot (disclosed ceiling) |

## Ceilings (disclosed)
- Falsifiers 23, 29, 31, 34, 35, 36, 65, 66, 67 are visible-identity claims: the harness proves structure, the
  screenshots are the evidence, the human review is the verdict.
- No reduced-motion screenshot of the Frozen Field (77) and no reduced-motion Session state in the evidence set;
  the reduced-motion rule is global and tested on the mocked lane.
- L7 runs `next dev` (as the F02/F03 lanes do); the production build is proven by the inspection runtime
  (`next build` + `next start`) under the evidence harness, not by L7.
