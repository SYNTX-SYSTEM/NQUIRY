# WORK UNIT REPORT
FIELD: CYAN_FRONTEND_SYMBIOSIS (Architecture 27 v4, `b0a5101` on `pfc-integration`)
WORK_UNIT: CYAN-PCPG-03 — Presentation attachment map → current CYAN object structure
DATE: 2026-10-01 · BASE: `checkpoint-CY-PCPG-02` → `34bcc4d1a1c73c7f1c571842169700fa807e0417`

## Current CYAN object (reconstructed before writing)
The primary object is the Session field organism (not the legacy decision surface): core `[data-testid="field-core"]`,
lifecycle ring `session-phases`, path station `relation-trace`, active-phase chamber `active-phase` (semantic
`question` / `frozen` / `action`) holding the burst panel `burst-capture-panel` and the human question set
(`frozen-set`, `own-question`), the Session control chamber `[data-semantic="authority"]`, boundary marks
`[data-boundary]`, the proof chamber `[data-semantic="proof"]` (ProofDepth disclosures = the organism's inspection
depth), the derived chamber `analysis-chamber`, the decision-entry chamber; on the decision surface
(`session-view-ok`) the decision chamber. No deep inspector exists structurally.

## Delta
`apps/web/lib/field/pcpgAttachment.ts` (new): `CYAN_OBJECT_AREAS` (registry of existing identities, with words),
`CYAN_ATTACHMENT_TARGETS` (v4 §06.4 attachment → existing areas; `DEEP_FIELD_INSPECTOR` → [] structurally absent;
`FIELD_PANEL` → proof chamber = the UNPLACED fallback), `validateAttachmentRelation()` (runs at load; fail closed),
`targetsOfAttachment` (unknown attachment → `MalformedAttachmentMap`), `safeCategory` (unknown category → UNPLACED),
`targetsOfCategories` (set, registry order, no ranking), `attachPresentation(presentationOf(...))` (per delta
categories → attachments → targets; union; structurally-absent list; the presentation passed through by reference).
`apps/web/tests/field/pcpgAttachment.test.ts` (new, 18 tests = falsifiers 1–20), `apps/web/scripts/pcpg03-mutation-proof.mjs`
(new), this record. Not touched: `pcpgClient.ts`, `pcpgPresentation.ts`, every component and page, PURPLE, RED, SEND.

## Proof
| Lane | Result |
|---|---|
| Falsifiers 1–20 | 18 / 18 (incl. every target identity verified to occur in the current component/page sources; no component imports the relation) |
| Mutation proof | 5 / 5 killed, file restored byte-identical: M1 UNPLACED → QUESTION · M2 AUTHORITY single exclusive target · M3 categories collapsed to one winner · M4 mapping mutates capability · M5 mapping creates SEND state |
| `tests/field` + `tests/lib` | 332 / 332 |
| Whole unit suite | 362 / 362 |
| `tsc --noEmit`, `eslint` | clean |
| Browser / E2E | not run — no visual component changed |

## Status
FBR-CYAN-PCPG-03: CLOSED. Categories unchanged. UNKNOWN → UNPLACED preserved. Multi-attachment preserved. Governance
semantics unchanged. UI untouched; membrane rendering and attachment rendering not started; PURPLE untouched; SEND not
materialized. Remaining CYAN First Broken Relation: `attachPresentation(...)` → the object membrane (CYAN-PCPG-04) and
the attachment rendering at the targets (CYAN-PCPG-05). Not started.
