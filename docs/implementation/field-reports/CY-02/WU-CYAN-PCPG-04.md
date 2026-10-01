# WORK UNIT REPORT
FIELD: CYAN_FRONTEND_SYMBIOSIS (Architecture 27 v4, `b0a5101` on `pfc-integration`)
WORK_UNIT: CYAN-PCPG-04 — PCPG-R12/1 presentation → Session object membrane
DATE: 2026-10-01 · BASE: `checkpoint-CY-PCPG-03` → `30e031906576c6b01fe2373f880edb01bc6646f8`

## Delta
| File | Change |
|---|---|
| `apps/web/components/field/GovernanceMembrane.tsx` (new) | the object membrane: `role="status"` strip "Field · <derived words>" (+ "observed at <time>" when a basis exists), `data-membrane-label`, `data-prominence` (v4 §07.4 from the label only: quiet / visible / prominent / explicit), `data-observation`, `data-human-authority`; assistive detail with the crossed capability facts in words (§17) and "Send not materialized." when a current observation exists. Consumes `ObservationPresentation` only (type import); no control of any kind |
| `apps/web/app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx` | `NO_OBSERVATION_YET: ObservationPresence = {kind:"none"}` (v4 §01/§04.1: no standing observation; no intent-submission producer exists on the surface yet) and one `<GovernanceMembrane presentation={presentationOf(NO_OBSERVATION_YET)} />` inside the `FieldCore` children, after `ReconstructionNote` |
| `apps/web/app/globals.css` | one appended block `.governance-membrane` (quiet pill, prominence variants on existing tokens `--blue`, `--muted`, `--ink`, `--attention`, `--ai`; text ≥ 0.78rem; no green) |
| `apps/web/tests/field/governanceMembrane.test.tsx` (new, 14 tests), `apps/web/tests/e2e/cy04-membrane.spec.ts` (new), `apps/web/scripts/pcpg04-mutation-proof.mjs` (new), `apps/web/playwright.sf01.config.ts` (phone project matches `cy04-*`) | proofs |
| `apps/web/tests/field/pcpgAttachment.test.ts` | predecessor falsifier 20 narrowed to its successor truth: the attachment relation stays unimported (PCPG-05); the derivation is now legitimately imported by the page |
| this record + `browser-evidence/pcpg-04/` | screenshots desktop 1280 / Pixel 7, lane summary |
Not touched: `pcpgClient.ts`, `pcpgPresentation.ts`, `pcpgAttachment.ts`, every chamber, ring, path, question / burst / decision / authority / provider / proof surface, boundary marks, PURPLE (login, account, auth methods, logout, sessions, recovery), RED, SEND.

## Proof
| Lane | Result |
|---|---|
| Falsifiers 1–20 (component + source laws) | 14 / 14 |
| Mutation proof (`scripts/pcpg04-mutation-proof.mjs`) | 5 / 5 killed, byte-identical restore (sha256 `55547b82…`): M1 unavailable → "Denied" · M2 Human Authority without derived input · M3 canSend → send button · M4 component importing the raw parser · M5 precedence altered (superseded demoted) |
| `tests/field` + `tests/lib` + `tests/components` | 375 / 375 |
| Narrow browser proof (mocked lane: `cy04-membrane`, `cy01-field`, `sf04-field`, `sf05-field`; desktop 1280 + Pixel 7) | 84 / 84 — membrane inside the core, "No observation", quiet, no control, no governance at any attachment target, prompt-observation query never called, text ≥ 11.5 px, no horizontal overflow |
| `tsc --noEmit`, `eslint` | clean |

## Observations for the Human Visual Authority
- The strip sits on the lower edge of the core sphere (inside the core box, straddling its circular edge) — placement to judge.
- On the live surface the membrane can only read "No observation" until an intent-submission producer exists (next relation); every other state is proven on the component and the mocked lane.
- Pre-existing, unchanged: the centred wordmark overlaps the path's current-state chip at 1280 px.

## Status
FBR-CYAN-PCPG-04: CLOSED. **Human Frontend Acceptance: ACCEPTED (2026-10-01, `HUMAN_REVIEW_RESULT_PCPG-04.md`)** →
FIELD_GREEN_WITH_DISCLOSED_CEILINGS (WU scope); not REVIEWED_FIELD, not PUBLISHED_FIELD. Object membrane MATERIALIZED; label precedence PRESERVED; "No observation"
PRESERVED; governance semantics UNCHANGED; SEND not materialized; attachment rendering NOT STARTED; PURPLE untouched.
This is a material CYAN change: **TECHNICALLY_CLOSED → READY_FOR_HUMAN_FRONTEND_REVIEW** (TECHNICAL PASS ≠ HUMAN VISUAL
ACCEPTANCE; not FIELD_GREEN until you accept it). Remaining CYAN First Broken Relation: the membrane's producer — the
actor's raw-intent submission on the Session object (`submitPromptObservation` → `ObservationPresence`), and the
attachment rendering at the mapped targets (CYAN-PCPG-05). Not started.
