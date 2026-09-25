# SF-05 — Human frontend review guide (doc 26 §52 evidence · §58 acceptance gate)
Status at hand-off: READY_FOR_HUMAN_FRONTEND_REVIEW (uncommitted tree; not FIELD_GREEN / APPROVED / PUBLISHED / RELEASE_READY)

| Item | Value |
|---|---|
| runtime (rebuilt from this tree; persistent review service) | http://127.0.0.1:13400 |
| identities | owner@inspect.local.test / inspect-owner-2026 · facilitator@inspect.local.test / inspect-fac-2026 · outsider@inspect.local.test / inspect-outsider-2026 |
| evidence (final tree) | `browser-evidence/run-10/` — MANIFEST.md, results.json, `screenshots/NN-viewport-state.png` (68 states: SF-04 1–53 + SF-05 54–68); runs 1–9 are the RED trail |
| harness | `browser-evidence/harness/review-harness.mjs` (+ `setup-scenario.mjs`, `perf-ab.mjs`) |

## Walk (doc 26 §52) → screenshot
| Evidence | Where / what to expect | Screenshot |
|---|---|---|
| login idle · hover · focus | `/login` anonymous: calm; pointer on Log in → the field gathers (dense stars, action glow, membrane); focus in Email → local response, global field calm; no success motion | 54–56 `login-idle` / `login-attention` / `login-focus` |
| Workspace overview with many Workspaces, zero duplicate primary nodes | owner `/workspaces` (14 same-named pairs from the scenario runs): one node per canonical id, "Workspace · founded <time> · <id8>" on every homonym, founding + five on the inner ring, the rest on the outer ring; no waterfall | 57–60 `workspace-overview-many-{wide,desktop,tablet,pixel-7}` |
| Workspace owner / facilitator | chambers action · identity (role facts) · participation (members with role marks; "you") · authority (held bindings) | 61–62 |
| Challenge owner / facilitator | action · authority chain at CHALLENGE scope (granted by → authority → held by → scope) · proof spine + identifiers | 63–64 |
| Session DRAFT / SETUP / CHALLENGE_CAPTURE / QUESTION_GENERATION (owner, facilitator) / QUESTION_CAPTURE / frozen set | the SF-04 flow states 11–29 on the rebuilt runtime (organ v2 in every screenshot); frozen chambers explicitly at 65–67 | 11–29, 65–67 |
| commit resonance event | state 12: the owner's Session grant → after the re-read a bottom-centre bloom "SESSION CONTROL GRANTED · … for this Session"; the chamber keeps a quiet proof line | 12 `session-grant-committed-owner` |
| irreversible confirmation | state 22: the confirmation chamber (irreversible class; becomes immutable / cannot happen afterwards / cancel · commit) | 22 `human-question-field-complete-confirm` |
| Decision Surface | `/workspaces/[w]/sessions/[s]/decision`: field frame, decision core with NON_PROOF, chambers context · evidence · decision; every PKG-28/29 component unchanged | 68 `decision-surface-field-language` |
| reduced motion | 2, 36, 47, 52 (SF-04) and 67 (`session-frozen-chambers-desktop-reduced`): no motion, every meaning | 67 |
| narrow / normal / wide | 44–46, 57–60 (tablet 1024 / phone / compact 360; desktop 1280; wide 1600) | — |

## What to judge (doc 26 §58)
1. Does the right side read as ONE organism of differentiated chambers (not cards, not a sidebar)? Compare with the reference qualities: dark translucent chambers, cyan contours (corner brackets), local nuclei (organ header), luminous relations (authority chain, spine).
2. Is authority visually a relation, apart from role marks and participation marks?
3. Does proof read as provenance (spine) with commit and authority source intact; identifiers contained and copyable?
4. Does the commit moment feel like the field registered a change (bloom, then gone), while proof stays?
5. Does the login feel like entry into a living field without noise?
6. Does the breadcrumb stay one path at 1280 (QUESTION_GENERATION complete)?
7. Is the left field intensified but unchanged in grammar (orbit, currents, pulses, breathing)?
8. Is the Decision Surface symbiotic without any invented chart?
