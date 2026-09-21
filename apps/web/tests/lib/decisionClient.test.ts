import { describe, expect, it, vi } from "vitest";
import { parseDecisionActionResult, recordHumanDecision } from "../../lib/api/decisionClient";
import type { DecisionId } from "../../lib/api/types";

const DECISION_ID = "d-1" as DecisionId;

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });
}

const COMMITTED_BODY = {
  kind: "committed",
  decision: {
    decisionId: "d-1",
    challengeId: "c-1",
    decisionQuestionRef: null,
    decisionQuestionText: "Which approach?",
    options: ["Option A", "Option B"],
    criteria: [],
    selectedOption: "Option A",
    rationale: "Lower cost",
    confidence: "high",
    state: "DECIDED",
    decidedByUserId: "u-1",
    decisionAuthorityBindingId: "binding-1",
    aiRecommendationConsumedRef: null,
    decidedAt: "2026-01-01T00:00:00Z",
  },
};

describe("recordHumanDecision", () => {
  it("POSTs to /decisions/{d}/decide with the selected option, rationale, confidence", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(COMMITTED_BODY));

    const result = await recordHumanDecision(DECISION_ID, "Option A", "Lower cost", "high", fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining(`/decisions/${DECISION_ID}/decide`),
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        credentials: "include",
        body: JSON.stringify({ selectedOption: "Option A", rationale: "Lower cost", confidence: "high" }),
      }),
    );
    expect(result.kind).toBe("committed");
  });

  it("URL-encodes the decisionId so a crafted id cannot alter the request path", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(COMMITTED_BODY));
    const hostileDecisionId = "../../admin" as DecisionId;

    await recordHumanDecision(hostileDecisionId, "Option A", null, null, fetchImpl);

    const calledUrl = fetchImpl.mock.calls[0][0] as string;
    expect(calledUrl).toContain(encodeURIComponent(hostileDecisionId));
    expect(calledUrl).not.toContain("/../../admin/");
  });

  /** Local-login field -- see the identical note in
   * `tests/lib/client.test.ts`: identity now comes only from the
   * `nquiry_session` cookie, never a request header. */
  it("sends the request with credentials included and no actor identity header", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(COMMITTED_BODY));

    await recordHumanDecision(DECISION_ID, "Option A", null, null, fetchImpl);

    const [, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(init.credentials).toBe("include");
    const headers = init.headers as Record<string, string>;
    expect(Object.keys(headers)).not.toContain("x-nquiry-actor-user-id");
  });
});

describe("parseDecisionActionResult", () => {
  it("parses a committed body with the fresh, server-returned Decision", () => {
    const result = parseDecisionActionResult(COMMITTED_BODY);
    expect(result.kind).toBe("committed");
    if (result.kind === "committed") {
      expect(result.decision.state).toBe("DECIDED");
      expect(result.decision.selectedOption).toBe("Option A");
    }
  });

  it("parses a denied body", () => {
    const result = parseDecisionActionResult({ kind: "denied", result: "DENY", reasonCode: "NOT_DECISION_RIGHT_HOLDER" });
    expect(result).toEqual({ kind: "denied", result: "DENY", reasonCode: "NOT_DECISION_RIGHT_HOLDER" });
  });

  it("parses an indeterminate body", () => {
    const result = parseDecisionActionResult({ kind: "indeterminate", blockedTargetRef: "recovery:abc" });
    expect(result).toEqual({ kind: "indeterminate", blockedTargetRef: "recovery:abc" });
  });

  it("parses a rejected body (e.g. SelectedOptionNotCandidate)", () => {
    const result = parseDecisionActionResult({ kind: "rejected", reasonCode: "SELECTED_OPTION_NOT_CANDIDATE" });
    expect(result).toEqual({ kind: "rejected", reasonCode: "SELECTED_OPTION_NOT_CANDIDATE" });
  });

  it("fails closed on an unrecognized kind rather than defaulting to committed", () => {
    expect(() => parseDecisionActionResult({ kind: "success" })).toThrow(TypeError);
  });

  it("fails closed on a missing kind", () => {
    expect(() => parseDecisionActionResult({})).toThrow(TypeError);
  });

  it("fails closed on a denied body with an unrecognized result value", () => {
    expect(() => parseDecisionActionResult({ kind: "denied", result: "ALLOW", reasonCode: "x" })).toThrow(TypeError);
  });

  it("fails closed on a rejected body missing reasonCode", () => {
    expect(() => parseDecisionActionResult({ kind: "rejected" })).toThrow(TypeError);
  });

  it("fails closed on a committed body with an invalid nested Decision", () => {
    expect(() => parseDecisionActionResult({ kind: "committed", decision: { decisionId: "d-1" } })).toThrow(TypeError);
  });

  it("fails closed on a committed body whose Decision carries an unrecognized state", () => {
    const body = { kind: "committed", decision: { ...COMMITTED_BODY.decision, state: "FOOBAR" } };
    expect(() => parseDecisionActionResult(body)).toThrow(TypeError);
  });
});
