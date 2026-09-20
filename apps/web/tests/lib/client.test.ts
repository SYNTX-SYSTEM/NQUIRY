import { describe, expect, it, vi } from "vitest";
import { fetchSessionView, parseSessionReadResult } from "../../lib/api/client";
import type { WorkspaceId, SessionId } from "../../lib/api/types";

const WORKSPACE_ID = "ws-1" as WorkspaceId;
const SESSION_ID = "sess-1" as SessionId;

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });
}

const DECISION_UNDER_CONSIDERATION = {
  decisionId: "d-1",
  challengeId: "c-1",
  decisionQuestionRef: null,
  decisionQuestionText: "Which approach?",
  options: ["Option A", "Option B"],
  criteria: ["Cost", "Speed"],
  selectedOption: null,
  rationale: null,
  confidence: null,
  state: "UNDER_CONSIDERATION",
  decidedByUserId: null,
  decisionAuthorityBindingId: "binding-1",
  aiRecommendationConsumedRef: null,
  decidedAt: null,
};

const AI_RECOMMENDATION = {
  generationId: "gen-1",
  summary: "Consider Option A for lower cost.",
};

const OK_BODY = {
  kind: "ok",
  data: {
    workspaceId: WORKSPACE_ID,
    challenge: { challengeId: "c-1", workspaceId: WORKSPACE_ID, title: "Title", description: null },
    session: { sessionId: SESSION_ID, challengeId: "c-1", workspaceId: WORKSPACE_ID, state: "QUESTION_CAPTURE" },
    burst: {
      burstId: "b-1",
      sessionId: SESSION_ID,
      state: "ACTIVE",
      mode: "HUMAN_ONLY",
      questions: [{ questionId: "q-1", originalText: "Why?", origin: "HUMAN" }],
    },
    decision: DECISION_UNDER_CONSIDERATION,
    aiRecommendation: AI_RECOMMENDATION,
  },
};

describe("fetchSessionView", () => {
  it("issues a GET to the workspace/session path and parses an ok result", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(OK_BODY));

    const result = await fetchSessionView(WORKSPACE_ID, SESSION_ID, fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining(`/workspaces/${WORKSPACE_ID}/sessions/${SESSION_ID}`),
      expect.objectContaining({ headers: { Accept: "application/json" } }),
    );
    expect(result.kind).toBe("ok");
  });

  it("URL-encodes identifiers so a crafted id cannot alter the request path", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(OK_BODY));
    const hostileWorkspaceId = "../../admin" as WorkspaceId;

    await fetchSessionView(hostileWorkspaceId, SESSION_ID, fetchImpl);

    const calledUrl = fetchImpl.mock.calls[0][0] as string;
    expect(calledUrl).toContain(encodeURIComponent(hostileWorkspaceId));
    expect(calledUrl).not.toContain("/../../admin/");
  });
});

describe("parseSessionReadResult", () => {
  it("parses a full ok body with a non-null burst", async () => {
    const result = parseSessionReadResult(OK_BODY);
    expect(result.kind).toBe("ok");
    if (result.kind === "ok") {
      expect(result.data.burst?.questions).toHaveLength(1);
    }
  });

  it("parses an ok body with a null burst", () => {
    const body = { ...OK_BODY, data: { ...OK_BODY.data, burst: null } };
    const result = parseSessionReadResult(body);
    expect(result.kind).toBe("ok");
    if (result.kind === "ok") {
      expect(result.data.burst).toBeNull();
    }
  });

  it("parses a denied body", () => {
    const result = parseSessionReadResult({ kind: "denied", result: "REQUIRE", reasonCode: "BND-017" });
    expect(result).toEqual({ kind: "denied", result: "REQUIRE", reasonCode: "BND-017" });
  });

  it("parses an indeterminate body", () => {
    const result = parseSessionReadResult({ kind: "indeterminate", blockedTargetRef: "recovery:abc" });
    expect(result).toEqual({ kind: "indeterminate", blockedTargetRef: "recovery:abc" });
  });

  it("fails closed on an unrecognized kind rather than defaulting to ok", () => {
    expect(() => parseSessionReadResult({ kind: "allow-everything" })).toThrow(TypeError);
  });

  it("fails closed on a missing kind", () => {
    expect(() => parseSessionReadResult({})).toThrow(TypeError);
  });

  it("fails closed on a denied body with an unrecognized result value", () => {
    expect(() => parseSessionReadResult({ kind: "denied", result: "ALLOW", reasonCode: "x" })).toThrow(TypeError);
  });

  it("fails closed on a denied body missing reasonCode", () => {
    expect(() => parseSessionReadResult({ kind: "denied", result: "DENY" })).toThrow(TypeError);
  });

  it("fails closed on an indeterminate body missing blockedTargetRef", () => {
    expect(() => parseSessionReadResult({ kind: "indeterminate" })).toThrow(TypeError);
  });

  it("fails closed on a non-object body", () => {
    expect(() => parseSessionReadResult(null)).toThrow(TypeError);
    expect(() => parseSessionReadResult("ok")).toThrow(TypeError);
  });

  it("fails closed when a nested question is missing a required field", () => {
    const body = {
      ...OK_BODY,
      data: {
        ...OK_BODY.data,
        burst: { ...OK_BODY.data.burst, questions: [{ questionId: "q-1", origin: "HUMAN" }] },
      },
    };
    expect(() => parseSessionReadResult(body)).toThrow(TypeError);
  });

  // Retrofit (external review): the nested closed-vocabulary fields
  // (SessionState/BurstState/BurstMode/QuestionOrigin) were previously
  // only compile-time-cast, never runtime-checked -- these four prove
  // each one now fails closed on an unrecognized value, matching this
  // module's own "fails closed on any unrecognized response shape"
  // claim.
  it("fails closed on an unrecognized nested SessionState value", () => {
    const body = { ...OK_BODY, data: { ...OK_BODY.data, session: { ...OK_BODY.data.session, state: "FOOBAR" } } };
    expect(() => parseSessionReadResult(body)).toThrow(TypeError);
  });

  it("fails closed on an unrecognized nested BurstState value", () => {
    const body = { ...OK_BODY, data: { ...OK_BODY.data, burst: { ...OK_BODY.data.burst, state: "FOOBAR" } } };
    expect(() => parseSessionReadResult(body)).toThrow(TypeError);
  });

  it("fails closed on an unrecognized nested BurstMode value", () => {
    const body = { ...OK_BODY, data: { ...OK_BODY.data, burst: { ...OK_BODY.data.burst, mode: "FOOBAR" } } };
    expect(() => parseSessionReadResult(body)).toThrow(TypeError);
  });

  it("fails closed on an unrecognized nested QuestionOrigin value", () => {
    const body = {
      ...OK_BODY,
      data: {
        ...OK_BODY.data,
        burst: {
          ...OK_BODY.data.burst,
          questions: [{ questionId: "q-1", originalText: "x", origin: "FOOBAR" }],
        },
      },
    };
    expect(() => parseSessionReadResult(body)).toThrow(TypeError);
  });
});
