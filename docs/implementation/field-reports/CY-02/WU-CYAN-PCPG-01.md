# WORK UNIT REPORT
FIELD: CYAN_FRONTEND_SYMBIOSIS (Architecture 27 v4, `b0a5101` on `pfc-integration`)
WORK_UNIT: CYAN-PCPG-01 — PCPG-R12/1 types + client + fail-closed parser
DATE: 2026-10-01

## Header
| Item | Value |
|---|---|
| Authoritative architecture | `docs/architecture/27_NQUIRY_SFE_FRONTEND_SYMBIOSIS_ARCHITECTURE.md` at `b0a5101fb787bd18092b632f0419366b350f110d` (v4, read completely: 1801 lines, sha256 `d102d92d…`) |
| RED producer (contract) | `PCPG-R12/1` = `governanceObservation` in the response of `POST /workspaces/{workspaceId}/prompt-observations`; serializer `application.http_pcpg._governance_observation_wire` at `checkpoint-PFC-PCPG-18` = `41b4324a75077ec33b00ed3a878db7a318fc00d8` (producer side closed per v4 §23) |
| CYAN predecessor | `field-CY-01` → `54f8b4f91b12f7c05c10eb98d6281bbe1ba19859` |
| FBR closed | FBR-CYAN-CONTRACT-01 (no CYAN consumer for PCPG-R12/1): the typed contract, the client call and the fail-closed parser now exist |
| Delta | `apps/web/lib/api/pcpgClient.ts` (new), `apps/web/tests/lib/pcpgClient.test.ts` (new), this record. No UI, no component, no membrane, no panel, no attachment map, no PURPLE, no SEND, no BLUE/RED code merged |
| Claim ceiling | types mirror the serializer; `canSend` is the R-10 projection, never SEND authority; `composedProofCeiling` / `sessionProofCeiling` are the Session-level proof ceiling (partial I-12): `GOVERNED` \| `FIXTURE_NON_PROOF` \| `null`, `null` never promoted; runtime facts of PCPG-18 (target null, flags empty, provider deltas INDETERMINATE, composed ceiling null) are RED truth and are not "fixed" here |

## Contract as typed (v4 §13.2, exact)
`GovernanceObservation = {kind:"unavailable", reasonCode: SEMANTIC_OBSERVATION_UNAVAILABLE | FIELD_RECONSTRUCTION_UNAVAILABLE | PROJECTION_INCOMPLETE} | {kind:"current", contract:"PCPG-R12/1", basis{rawIntentDigestSha256, derivationTime}, semanticObservation{ruleSetVersion, clauses, actions[{clauseIndex, span, clauseText, modality, negated, requestedExecutor, candidateOperation, target, possibleExternalEffect, possibleSecretContent, decisionSubstitutionRequested}], unknownRelations, relationsTouched, declaredPurpose, semanticPurpose, purposeAlignment, semanticDrift}, deltas: DeltaWire[], chain{firstBrokenRelation{predecessor, broken}|null, maximumLegitimateTransition, nextValidTransition, humanAuthorityRequired[{deltaId, result, reasonCode}], partial}, capability{governanceAdmissible, governanceAdmissibleReasons, providerExecutable, providerExecutableReasons, canSend}, composedProofCeiling}`. Outer envelope `PromptObservation` (field, workspace, session|null, rawIntent, rawIntentLength, rawIntentDigestSha256, declaredPurpose, observedAt). Typed return path `PromptObservationResult = ok | malformed(MALFORMED_PROJECTION) | denied | rejected | not_found | indeterminate | network_failure`.

## Fail-closed law as implemented
Inside `governanceObservation` the key set of every object is exact (serializer mirror): an unknown key, a B-10-forbidden key (`eligibleContent`, `providerEligibility`, `sendGate`, `send*`, `evidence*`, `provenance*`, `freshness`, `actorProjection`, `pulse*`, `reconstructionId`, `snapshotId`, `projectionId`, `bindingId`, `authorityBindingId`, `authorityRef`, `holderClass`, `affectedSemanticLoci`, `displaySummary`, `nervePoints`, `statusVector`, `r13`, …), an unknown contract identity, an unknown kind, an unknown closed value, a missing required key or a wrong type aborts the whole observation with `MalformedProjection`; nothing partial is returned; the envelope-level result is `malformed`, distinct from RED's `unavailable`. `null` stays `null`; absent is a failure, not `false`. The client sends exactly `rawIntent`, `sessionId?`, `declaredPurpose?` and no Idempotency-Key (query).

## Proof
| Lane | Result |
|---|---|
| Falsifiers 1–18 (`tests/lib/pcpgClient.test.ts`, 22 tests) | 22 / 22 |
| Client suites `tests/lib` | 115 / 115 |
| Whole unit suite | 324 / 324 (27 files) |
| `tsc --noEmit`, `eslint` on the two files | clean, 0 warnings |
| UI / e2e | untouched (no UI change; `gates.test.ts` field-source set unaffected — `lib/api` is not a field source) |

## Status
FBR-CYAN-CONTRACT-01: CLOSED. UI untouched. Presentation attachment map not started. PURPLE untouched. SEND not materialized.
Remaining CYAN First Broken Relation: parsed `PCPG-R12/1` → CYAN-local derivations (label §06.1, aggregates §06.2, `PresentationCategory` §06.3) → consumer (CYAN-PCPG-02). Not started.
