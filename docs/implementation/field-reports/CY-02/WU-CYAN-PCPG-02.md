# WORK UNIT REPORT
FIELD: CYAN_FRONTEND_SYMBIOSIS (Architecture 27 v4, `b0a5101` on `pfc-integration`)
WORK_UNIT: CYAN-PCPG-02 — PCPG-R12/1 → CYAN-local presentation derivations
DATE: 2026-10-01 · BASE: `checkpoint-CY-PCPG-01` → `6d6c8f822e2a5cee78b7f4b57c6439ed2a8b2cec`

## Header
| Item | Value |
|---|---|
| FBR closed | FBR-CYAN-PCPG-02: parsed PCPG-R12/1 → CYAN-local deterministic derivations → future presentation consumer |
| Delta | `apps/web/lib/field/pcpgPresentation.ts` (new): `membraneLabel` (§06.1 precedence), `presentationAggregates` (§06.2 + provider / FBR / partial / retained / proof-ceiling presentation), `proofCeilingPresentation` (§12.1, label "Session-level proof ceiling (partial I-12)"), `sendStatement` (§11.4, keyed to the contract identity, takes no capability), `NOT_MATERIALIZED`, `PRESENTATION_CATEGORIES` + `categoriesOf` (§06.3; placement map = CYAN copy of RED operation-index ids; empty → UNPLACED), `PRESENTATION_ATTACHMENT_MAP` + `attachmentsOf` (§06.4), `presentationOf` (whole-observation shape for the future membrane / panel / inspector). `apps/web/tests/field/pcpgPresentation.test.ts` (new, 20 tests = falsifiers 1–25), `apps/web/scripts/pcpg02-mutation-proof.mjs` (new), `apps/web/tests/field/gates.test.ts` (law: the module is a projection consumer, so the RED operation ids it copies for placement are permitted there), this record |
| Not touched | wire contract (`pcpgClient.ts` unchanged), every component and page, FieldFrame, Session page, Decision page, PURPLE, SEND, backend |
| Laws held | CYAN derives presentation, never governance: every output is a pure function of the parsed contract (+ one caller-supplied object-change fact for "Superseded"); no clock, network, storage or role; `canSend` preserved verbatim and never read for SEND; "Send not materialized" keyed to `PCPG-R12/1`; `null` ceiling stays unknown; UNPLACED is never guessed; categories are sets (fixed order, no winner); `affectedSemanticLoci` does not exist; `SOURCE_RELATION` named only as not materialized |

## Proof
| Lane | Result |
|---|---|
| Falsifiers 1–25 (`tests/field/pcpgPresentation.test.ts`) | 20 / 20 (parser-integrated: every input passes CYAN-PCPG-01 first) |
| Mutation proof (`scripts/pcpg02-mutation-proof.mjs`) | 5 / 5 killed, production file restored byte-identical (sha256 `72e91f4a…` before and after): M1 UNKNOWN operation guessed into QUESTION · M2 canSend as SEND authority · M3 null ceiling → GOVERNED · M4 unavailable → BOUNDARY_REACHED · M5 HAR label without HAR / authority-boundary input |
| Affected suites `tests/field` + `tests/lib` | 314 / 314 |
| Whole unit suite | 344 / 344 (28 files) |
| `tsc --noEmit`, `eslint` | clean |
| Browser / E2E | not run — no UI change authorized |

## Status
FBR-CYAN-PCPG-02: CLOSED. UI untouched. PURPLE untouched. SEND not materialized. SOURCE_RELATION not materialized.
Remaining CYAN First Broken Relation: `presentationOf(...)` → consumer (membrane / attachment rendering / panel / inspector on the Session and Decision objects) — CYAN-PCPG-03/04/05. Not started.
