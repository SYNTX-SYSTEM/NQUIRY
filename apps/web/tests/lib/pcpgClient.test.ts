/**
 * CYAN-PCPG-01 falsifiers (Architecture 27 v4 §13, §21, §24; commit b0a5101): the PCPG-R12/1 typed client and
 * fail-closed parser. Fixtures mirror the RED serializer `application.http_pcpg._governance_observation_wire` at
 * `checkpoint-PFC-PCPG-18` (41b4324) key for key.
 */
import { describe, expect, it, vi } from "vitest";
import {
  B10_FORBIDDEN_KEYS,
  MalformedProjection,
  PCPG_CONTRACT,
  parseGovernanceObservation,
  parsePromptObservation,
  submitPromptObservation,
} from "../../lib/api/pcpgClient";

const DELTA = {
  deltaId: "d-0",
  operation: "REQUEST_QUESTION_ANALYSIS",
  executionClass: "PROVIDER_COMPUTATION",
  target: null,
  sourceClause: "Analyse the questions",
  span: [0, 21],
  currentState: "QUESTION_CAPTURE",
  result: "INDETERMINATE",
  reasonCode: "DATA_GOVERNANCE_NOT_MATERIALIZED",
  flags: [],
  sessionProofCeiling: "GOVERNED",
};
const BROKEN = { ...DELTA, deltaId: "d-1", operation: "SELECT_PRIMARY_QUESTION", executionClass: "HUMAN_COMMAND", sourceClause: "pick the primary question", span: [23, 48], result: "STATE_BOUNDARY", reasonCode: "SESSION_NOT_IN_QUESTION_SELECTION" };
const ACTION = {
  clauseIndex: 0,
  span: [0, 21],
  clauseText: "Analyse the questions",
  modality: "REQUESTED",
  negated: false,
  requestedExecutor: "AI",
  candidateOperation: "REQUEST_QUESTION_ANALYSIS",
  target: null,
  possibleExternalEffect: false,
  possibleSecretContent: false,
  decisionSubstitutionRequested: false,
};
function current(overrides: Record<string, unknown> = {}) {
  return {
    kind: "current",
    contract: "PCPG-R12/1",
    basis: { rawIntentDigestSha256: "3f9a".padEnd(64, "0"), derivationTime: "2026-10-01T11:17:00+00:00" },
    semanticObservation: {
      ruleSetVersion: "26/2026-09-29",
      clauses: ["Analyse the questions", "pick the primary question"],
      actions: [ACTION],
      unknownRelations: [],
      relationsTouched: ["REQUEST_QUESTION_ANALYSIS", "SELECT_PRIMARY_QUESTION"],
      declaredPurpose: null,
      semanticPurpose: null,
      purposeAlignment: null,
      semanticDrift: false,
    },
    deltas: [DELTA, BROKEN],
    chain: {
      firstBrokenRelation: { predecessor: DELTA, broken: BROKEN },
      maximumLegitimateTransition: [],
      nextValidTransition: null,
      humanAuthorityRequired: [{ deltaId: "d-1", result: "STATE_BOUNDARY", reasonCode: "SESSION_NOT_IN_QUESTION_SELECTION" }],
      partial: true,
    },
    capability: {
      governanceAdmissible: false,
      governanceAdmissibleReasons: ["MLT_EMPTY", "OPERATION_CLASS_NOT_ADMITTED"],
      providerExecutable: false,
      providerExecutableReasons: ["NO_ELIGIBLE_PROVIDER_ROUTE"],
      canSend: false,
    },
    composedProofCeiling: null,
    ...overrides,
  };
}
const UNAVAILABLE = { kind: "unavailable", reasonCode: "SEMANTIC_OBSERVATION_UNAVAILABLE" };
function envelope(governanceObservation: unknown, overrides: Record<string, unknown> = {}) {
  return {
    kind: "ok",
    field: "PRE_CALL_PROMPT_GOVERNANCE",
    workspace: { workspaceId: "11111111-1111-4111-8111-111111111111", name: "Onboarding inquiry" },
    session: { sessionId: "55555550-5555-4555-8555-555555555555" },
    rawIntent: "Analyse the questions. pick the primary question",
    rawIntentLength: 48,
    rawIntentDigestSha256: "3f9a".padEnd(64, "0"),
    declaredPurpose: null,
    observedAt: "2026-10-01T11:17:00+00:00",
    governanceObservation,
    ...overrides,
  };
}
/** A copy without one key: "absent" fixtures (absent ≠ null ≠ false). */
const omit = (obj: Record<string, unknown>, key: string): Record<string, unknown> => Object.fromEntries(Object.entries(obj).filter(([k]) => k !== key));
const malformed = (value: unknown) => expect(() => parseGovernanceObservation(value)).toThrow(MalformedProjection);
/** The parser never leaks a partial object: on failure nothing is returned at all. */
const closedFailure = (value: unknown) => {
  let result: unknown = "untouched";
  try {
    result = parseGovernanceObservation(value);
  } catch (e) {
    expect(e).toBeInstanceOf(MalformedProjection);
    return;
  }
  throw new Error(`expected MALFORMED_PROJECTION, got ${JSON.stringify(result)}`);
};

describe("PCPG-R12/1: valid responses parse exactly (falsifiers 1, 2, 9, 10, 11)", () => {
  it("1. a valid current observation parses field for field", () => {
    const go = parseGovernanceObservation(current());
    expect(go).toEqual(current());
    expect(go.kind === "current" && go.contract).toBe(PCPG_CONTRACT);
  });
  it("2. a valid unavailable observation parses with its exact reason code; nothing else is required or allowed", () => {
    expect(parseGovernanceObservation(UNAVAILABLE)).toEqual(UNAVAILABLE);
    for (const code of ["FIELD_RECONSTRUCTION_UNAVAILABLE", "PROJECTION_INCOMPLETE"]) {
      expect(parseGovernanceObservation({ kind: "unavailable", reasonCode: code })).toEqual({ kind: "unavailable", reasonCode: code });
    }
    closedFailure({ kind: "unavailable", reasonCode: "SOMETHING_ELSE" });
    closedFailure({ kind: "unavailable", reasonCode: "PROJECTION_INCOMPLETE", basis: {} });
  });
  it("9. a null proof ceiling stays null (never GOVERNED, never false)", () => {
    const go = parseGovernanceObservation(current({ composedProofCeiling: null }));
    expect(go.kind === "current" ? go.composedProofCeiling : "x").toBeNull();
    const d = parseGovernanceObservation(current({ deltas: [{ ...DELTA, sessionProofCeiling: null }] }));
    expect(d.kind === "current" ? d.deltas[0].sessionProofCeiling : "x").toBeNull();
  });
  it("10. FIXTURE_NON_PROOF stays exact", () => {
    const go = parseGovernanceObservation(current({ composedProofCeiling: "FIXTURE_NON_PROOF", deltas: [{ ...DELTA, sessionProofCeiling: "FIXTURE_NON_PROOF" }] }));
    expect(go.kind === "current" && go.composedProofCeiling).toBe("FIXTURE_NON_PROOF");
    expect(go.kind === "current" && go.deltas[0].sessionProofCeiling).toBe("FIXTURE_NON_PROOF");
  });
  it("11. GOVERNED stays exact; any other ceiling value fails closed", () => {
    const go = parseGovernanceObservation(current({ composedProofCeiling: "GOVERNED" }));
    expect(go.kind === "current" && go.composedProofCeiling).toBe("GOVERNED");
    closedFailure(current({ composedProofCeiling: "PROVEN" }));
    closedFailure(current({ composedProofCeiling: false }));
    closedFailure(current({ deltas: [{ ...DELTA, sessionProofCeiling: "governed" }] }));
  });
  it("null is preserved as null and absent is a failure: null ≠ false, absent ≠ false, unknown ≠ denied", () => {
    const go = parseGovernanceObservation(current());
    if (go.kind !== "current") throw new Error("expected current");
    expect(go.deltas[0].target).toBeNull();
    expect(go.semanticObservation.purposeAlignment).toBeNull();
    expect(go.chain.nextValidTransition).toBeNull();
    expect(go.deltas[0].result).toBe("INDETERMINATE");
    closedFailure(current({ capability: { ...current().capability, canSend: null } }));
    closedFailure(current({ chain: { ...current().chain, partial: null } }));
    closedFailure(current({ chain: omit(current().chain, "partial") }));
  });
});

describe("PCPG-R12/1: fail-closed law (falsifiers 3–8, 12–15)", () => {
  it("3. an unknown contract version fails closed (PCPG-R12/2, PCPG-R12, lowercase, absent)", () => {
    for (const contract of ["PCPG-R12/2", "PCPG-R12", "pcpg-r12/1", "PCPG-R13/1", null, undefined]) {
      closedFailure(current({ contract }));
    }
  });
  it("4. an unknown observation kind fails closed (stale, rejected, allowed, denied, ok, absent)", () => {
    for (const kind of ["stale", "rejected", "allowed", "denied", "ok", "", null, undefined]) {
      closedFailure(current({ kind }));
    }
    closedFailure({ kind: "stale", projectionId: "p", reasonCode: "OBJECT_CHANGED" });
  });
  it("5. an unknown closed enum value fails closed (executionClass, result, modality, requestedExecutor, purposeAlignment, reason code)", () => {
    closedFailure(current({ deltas: [{ ...DELTA, executionClass: "AI_CALL" }] }));
    closedFailure(current({ deltas: [{ ...DELTA, result: "BLOCKED" }] }));
    closedFailure(current({ deltas: [{ ...DELTA, result: "allowed" }] }));
    closedFailure(current({ semanticObservation: { ...current().semanticObservation, actions: [{ ...ACTION, modality: "IMPERATIVE" }] } }));
    closedFailure(current({ semanticObservation: { ...current().semanticObservation, actions: [{ ...ACTION, requestedExecutor: "SYSTEM" }] } }));
    closedFailure(current({ semanticObservation: { ...current().semanticObservation, purposeAlignment: "UNKNOWN" } }));
    closedFailure({ kind: "unavailable", reasonCode: "STALE" });
  });
  it("6. a malformed delta fails closed (missing key, wrong type, bad span, extra key)", () => {
    closedFailure(current({ deltas: [omit(DELTA, "reasonCode")] }));
    closedFailure(current({ deltas: [{ ...DELTA, flags: "none" }] }));
    closedFailure(current({ deltas: [{ ...DELTA, span: [0] }] }));
    closedFailure(current({ deltas: [{ ...DELTA, span: ["0", "21"] }] }));
    closedFailure(current({ deltas: [{ ...DELTA, deltaId: 7 }] }));
    closedFailure(current({ deltas: [{ ...DELTA, retained: true }] }));
    closedFailure(current({ deltas: ["d-0"] }));
    closedFailure(current({ deltas: null }));
  });
  it("7. a malformed chain fails closed (broken absent, FBR as string, HAR entry malformed, MLT not a list)", () => {
    closedFailure(current({ chain: { ...current().chain, firstBrokenRelation: { predecessor: null } } }));
    closedFailure(current({ chain: { ...current().chain, firstBrokenRelation: "d-1" } }));
    closedFailure(current({ chain: { ...current().chain, humanAuthorityRequired: [{ deltaId: "d-1" }] } }));
    closedFailure(current({ chain: { ...current().chain, humanAuthorityRequired: [{ deltaId: "d-1", result: "STATE_BOUNDARY", reasonCode: null, holderClass: "FACILITATOR" }] } }));
    closedFailure(current({ chain: { ...current().chain, maximumLegitimateTransition: {} } }));
    closedFailure(current({ chain: { ...current().chain, chainState: "BLOCKED" } }));
  });
  it("8. a malformed capability fails closed (string booleans, missing reasons, extra axis)", () => {
    closedFailure(current({ capability: { ...current().capability, governanceAdmissible: "false" } }));
    closedFailure(current({ capability: { ...current().capability, providerExecutable: 0 } }));
    closedFailure(current({ capability: omit(current().capability, "providerExecutableReasons") }));
    closedFailure(current({ capability: { ...current().capability, eligibleContent: "TRUE" } }));
    closedFailure(current({ capability: { ...current().capability, sendGate: "NOT_MATERIALIZED" } }));
  });
  it("12. an unexpected eligibleContent is rejected (B-10: the eligible-content set never crosses; no status is derivable)", () => {
    closedFailure(current({ eligibleContent: { eligibleInputs: [] } }));
    closedFailure(current({ eligibleContentSet: {} }));
    closedFailure(current({ providerEligibility: { eligible: true } }));
  });
  it("13. an unexpected sendGate / SEND relation is rejected (R-13 is not materialized; no backend SEND field exists)", () => {
    closedFailure(current({ sendGate: "MATERIALIZED" }));
    closedFailure(current({ send: { allowed: true } }));
    closedFailure(current({ sendRelation: "R-13" }));
    closedFailure(current({ r13: {} }));
  });
  it("14. authority binding ids and holder classes cannot enter the typed contract (anywhere, at any depth)", () => {
    closedFailure(current({ authorityBindingId: "b1" }));
    closedFailure(current({ deltas: [{ ...DELTA, bindingId: "b1" }] }));
    closedFailure(current({ chain: { ...current().chain, humanAuthorityRequired: [{ deltaId: "d-1", result: "AUTHORITY_BOUNDARY", reasonCode: null, harHolderClass: "FACILITATOR" }] } }));
    closedFailure(current({ basis: { ...current().basis, reconstructionId: "r1" } }));
    for (const key of B10_FORBIDDEN_KEYS) closedFailure(current({ [key]: "x" }));
  });
  it("15. unknown future fields cannot silently become governance truth (unexpected keys at any level fail closed)", () => {
    closedFailure(current({ affectedSemanticLoci: ["DECISION_TRANSITION"] }));
    closedFailure(current({ displaySummary: { label: "FIELD_CURRENT" } }));
    closedFailure(current({ statusVector: {} }));
    closedFailure(current({ freshness: { state: "CURRENT" } }));
    closedFailure(current({ anythingNew: 1 }));
    closedFailure(current({ basis: { ...current().basis, snapshotId: "s1" } }));
    closedFailure(current({ semanticObservation: { ...current().semanticObservation, locus: "QUESTION" } }));
  });
  it("a partial result is never returned: the first violation aborts the whole observation", () => {
    malformed(current({ deltas: [DELTA, { ...BROKEN, result: "NOPE" }] }));
  });
});

describe("PCPG-R12/1: the envelope and the client (falsifiers 16–18)", () => {
  it("the outer envelope parses into the typed return path; non-ok envelopes stay closed failure kinds", () => {
    const ok = parsePromptObservation(envelope(current()));
    expect(ok.kind).toBe("ok");
    if (ok.kind !== "ok") throw new Error();
    expect(ok.data.session).toEqual({ sessionId: "55555550-5555-4555-8555-555555555555" });
    expect(ok.data.governanceObservation.kind).toBe("current");
    expect(parsePromptObservation(envelope(current(), { session: null })).kind).toBe("ok");
    expect(parsePromptObservation(envelope(UNAVAILABLE))).toMatchObject({ kind: "ok", data: { governanceObservation: UNAVAILABLE } });
    expect(parsePromptObservation({ kind: "rejected", reasonCode: "RAW_INTENT_REQUIRED" })).toEqual({ kind: "rejected", reasonCode: "RAW_INTENT_REQUIRED" });
    expect(parsePromptObservation({ kind: "denied", reasonCode: "NOT_A_MEMBER" })).toEqual({ kind: "denied", reasonCode: "NOT_A_MEMBER" });
    expect(parsePromptObservation({ kind: "not_found", reasonCode: "WORKSPACE_NOT_FOUND" })).toEqual({ kind: "not_found", reasonCode: "WORKSPACE_NOT_FOUND" });
    expect(parsePromptObservation({ kind: "allowed" }).kind).toBe("indeterminate");
    expect(parsePromptObservation("ok").kind).toBe("indeterminate");
  });
  it("a malformed observation inside an ok envelope is a typed MALFORMED_PROJECTION, not unavailable and not ok", () => {
    const r = parsePromptObservation(envelope(current({ contract: "PCPG-R12/2" })));
    expect(r).toMatchObject({ kind: "malformed", reasonCode: "MALFORMED_PROJECTION" });
    expect(r.kind === "malformed" && r.detail).toMatch(/contract/);
    expect(parsePromptObservation(envelope(current(), { field: "SOMETHING" })).kind).toBe("malformed");
  });
  it("16. client-supplied capability cannot override server output: the request body carries exactly the three inputs", async () => {
    const calls: { url: string; init: RequestInit }[] = [];
    const fetchImpl = (async (url: string | URL | Request, init?: RequestInit) => {
      calls.push({ url: String(url), init: init ?? {} });
      return new Response(JSON.stringify(envelope(current())), { headers: { "content-type": "application/json" } });
    }) as unknown as typeof fetch;
    const input = { rawIntent: "Analyse the questions", sessionId: "55555550-5555-4555-8555-555555555555", canSend: true, capability: { canSend: true }, governanceObservation: { kind: "current" } };
    const result = await submitPromptObservation("11111111-1111-4111-8111-111111111111", input as never, fetchImpl);
    expect(calls[0]?.url).toMatch(/\/workspaces\/11111111-1111-4111-8111-111111111111\/prompt-observations$/);
    expect(calls[0]?.init.method).toBe("POST");
    expect(JSON.parse(String(calls[0]?.init.body))).toEqual({ rawIntent: "Analyse the questions", sessionId: "55555550-5555-4555-8555-555555555555" });
    expect(new Headers(calls[0]?.init.headers).has("Idempotency-Key")).toBe(false);
    expect(result.kind === "ok" && result.data.governanceObservation.kind === "current" && result.data.governanceObservation.capability.canSend).toBe(false);
  });
  it("the client is fail-closed on transport: a thrown fetch is network_failure; a non-JSON body is indeterminate", async () => {
    const thrown = vi.fn().mockRejectedValue(new Error("down")) as unknown as typeof fetch;
    expect(await submitPromptObservation("w", { rawIntent: "x" }, thrown)).toEqual({ kind: "network_failure", reasonCode: "NETWORK_FAILURE" });
    const html = vi.fn().mockResolvedValue(new Response("<html>", { status: 502 })) as unknown as typeof fetch;
    expect(await submitPromptObservation("w", { rawIntent: "x" }, html)).toEqual({ kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" });
  });
  it("17./18. the parser derives nothing: no presentation label, no SEND authority, no aggregate — output keys are exactly the contract's", () => {
    const go = parseGovernanceObservation(current());
    expect(Object.keys(go).sort()).toEqual(["basis", "capability", "chain", "composedProofCeiling", "contract", "deltas", "kind", "semanticObservation"].sort());
    const text = JSON.stringify(go);
    for (const invented of ["label", "Boundary reached", "Observed", "sendGate", "SEND", "canSendAuthority", "allowed", "presentation", "attachment", "boundary\":", "humanAuthority\":", "chainState"]) {
      expect(text).not.toContain(invented);
    }
    // canSend stays the server's boolean; a true value is still only a projection and is never turned into anything else
    const sendable = parseGovernanceObservation(current({ capability: { ...current().capability, canSend: true } }));
    expect(sendable.kind === "current" && sendable.capability.canSend).toBe(true);
    expect(JSON.stringify(sendable)).not.toMatch(/\bgate\b|authori[sz]ed|permission/);
  });
});
