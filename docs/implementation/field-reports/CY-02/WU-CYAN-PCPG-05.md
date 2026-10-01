# WORK UNIT REPORT
FIELD: CYAN_FRONTEND_SYMBIOSIS (Architecture 27 v4, `b0a5101` on `pfc-integration`)
WORK_UNIT: CYAN-PCPG-05 — Actor raw intent observation → live governance membrane
DATE: 2026-10-01 · BASE: `checkpoint-CY-PCPG-04` → `daeff13f267ff78bf468f871f2e23b993e7150f3`

## Pin transition (local/test lanes only — HD-27 + the CYAN-PCPG-05 authorization)
| | Tag | Tag object | Commit | Tree | Migration head |
|---|---|---|---|---|---|
| previous | `checkpoint-PFC-B5` | `fd3d5600132e4dcb9203702d500daccf4c6d0439` | `7d3f74e4685b821cc948f45e413c1e0c207259d4` | `bc77cc8bb6414e6104aabdd5bd2fb1874f63f750` | `e8c2a5f1b7d4` |
| **new** | `checkpoint-PFC-PCPG-18` | `0e12895fc64299abde1eb5115303f962b1c227af` (signed, good signature) | `41b4324a75077ec33b00ed3a878db7a318fc00d8` | `0631c936f99c9356f6082f05b460815a09632c7b` | `e8c2a5f1b7d4` (no migration delta) |
Delta of the producer between the pins: the PCPG route (`apps/api/.../http/pcpg.py`, `main.py` include), the operator
module (`nquiry_api/operator/create_identity.py`, AC1), the R-01…R-12 application modules, a 7-line change in
`scripts/dev_provision_local_identity.py`; no `apps/web`, no `infra/local`, no migration. Production (nquiry.condyn.eu:
B5 + AC1.1) is untouched; the review runtime `:13500` is rebuilt on the new pin for the human review. Where recorded:
`scripts/run_cy01_real_stack.sh` (PIN_* constants with the history), this record.

## Delta (CYAN)
| File | Change |
|---|---|
| `apps/web/lib/field/observation.ts` (new) | pure state machine: `observationReducer` (requested keeps the presence; ok → observation + versions; malformed → fail closed; every failure keeps the valid observation), `presenceFor` (supersession from canonical `session.version`/`burst.version` only, never a clock), `runObservation` |
| `apps/web/lib/field/useObservation.ts` (new) | React binding; forwards exactly `rawIntent`, `sessionId`, `declaredPurpose?` to `submitPromptObservation`; React state only |
| `apps/web/components/field/IntentObservationChamber.tsx` (new) | the context chamber "Your intent · observed, never sent": textarea (≤ 8000), optional declared purpose (≤ 2000), one control **Observe**, pending state, the legitimate failure presentation with the server's code, the observation's own facts (observed at, digest, view-only note, superseded note); not role-gated |
| `apps/web/app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx` | `useObservation`, `presenceFor(state, {session.version, burst.version})` → `presentationOf` → the membrane; the chamber mounted before the derived chamber |
| `apps/web/app/globals.css` | Session organ placement: `context` row 3, `derived` row 4, `decision-entry` row 5; textarea width |
| `apps/web/scripts/run_cy01_real_stack.sh` | pin moved to PCPG-18 (history kept); migration-head check generalized |
| `apps/web/tests/field/observation.test.ts`, `tests/field/intentObservationChamber.test.tsx`, `tests/e2e/cy05-observation.spec.ts`, `tests/real-stack/cy05-observation.real.spec.ts`, `scripts/pcpg05-mutation-proof.mjs`, `playwright.sf01.config.ts` (phone project `cy0[145]`) | proofs |
| `apps/web/tests/field/governanceMembrane.test.tsx`, `tests/field/pcpgAttachment.test.ts` (unchanged), `tests/e2e/sf05-field.spec.ts` | successor truths: the page's presence now comes from the state machine; the Session organ carries the `context` chamber between proof and decision entry |
Not touched: `pcpgClient.ts`, `pcpgPresentation.ts`, `pcpgAttachment.ts`, `GovernanceMembrane.tsx`, every other chamber, PURPLE, RED, production.

## Proof
| Lane | Result |
|---|---|
| State machine + chamber + membrane successor tests (`tests/field/observation.test.ts`, `intentObservationChamber.test.tsx`, `governanceMembrane.test.tsx`) | 32 / 32 |
| Mutation proof (`scripts/pcpg05-mutation-proof.mjs`) | 5 / 5 killed, byte-identical restore: M1 provisional result while observing · M2 control labelled Send · M3 chamber role-gated · M4 supersession ignoring the canonical versions · M5 raw intent persisted |
| `tests/field` + `tests/lib` + `tests/components` | 393 / 393 |
| Mocked browser lane (`cy05-observation`, `cy04-membrane`, `cy01-field`, `sf04-field`, `sf05-field`; desktop 1280 + Pixel 7) | **96 / 96** — loading gate (membrane unchanged while observing), body exactness `{rawIntent, sessionId}` without Idempotency-Key, Contributor observes (not role-gated), unavailable → "Governance unavailable" only, rejected/denied/not_found/network/malformed never replace the valid observation and keep the text (malformed fails closed), second Observe replaces, committed grant → version 5 → "Superseded" with the observation unchanged, reload → "No observation", no storage, only `position` + `prompt-observations` requested (no provider call), no Send/Run/Execute/Submit-to-AI control, organism primary, no overflow |
| **Real-stack lane against `checkpoint-PFC-PCPG-18`** (`scripts/run_cy01_real_stack.sh --timeout=300000`) | **18 / 18** (desktop + Pixel 7): `cy05-observation.real` — a real intent ("begin the setup of this session") on a real DRAFT Session yields a real PCPG-R12/1 projection and a derived membrane label; the canonical Session (state, version, analysis) is unchanged by observing; an unparseable intent → "Governance unavailable"; a second Observe replaces; after a committed `Begin setup` (version change) → "Superseded" with the digest unchanged; reload → "No observation"; a participant without authority observes too; no storage; no send-like control. Plus `cy01-analysis.real`, F02, F03, SF-01, WU-02.12 — all green on the new pin |
| `tsc --noEmit`, `eslint` | clean |
| Review runtime for the human | `nquiry-cy01-inspect` on `127.0.0.1:13500` rebuilt on the PCPG-18 export + this tree (route `prompt-observations` → 401 unauthenticated; review data unchanged) |
Evidence: `browser-evidence/pcpg-05/` (lane summaries, `producer.json`; screenshots untracked).


## Status
FBR-CYAN-PCPG-05: CLOSED (technically). Raw intent producer MATERIALIZED; observation presence MATERIALIZED; real
PCPG-R12/1 path PROVEN (PCPG-18); supersession PROVEN (versions only); persistence NONE; SEND not materialized;
provider call NONE; R-13 NOT STARTED; production UNTOUCHED (B5 + AC1.1); PURPLE UNTOUCHED.
Material visual CYAN change: **TECHNICALLY_CLOSED → READY_FOR_HUMAN_FRONTEND_REVIEW** (not FIELD_GREEN until accepted).
Remaining CYAN First Broken Relation: `attachPresentation(presentationOf(observation))` → rendering at the mapped
targets (attachment rendering; the deltas' categories → question set, burst panel, ring, authority chamber, boundary
marks, derived chamber, decision entry) — the next Work Unit; not started.

