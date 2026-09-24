/**
 * SF-01 WU-SF01.2 (L0/L2): Relation Trace derivation from published F02 projections.
 * Governing: 21 §12 (position = relation trace, six coordinates, no fabricated Session),
 * CF-01, CF-02, §14 NOT_FOUND ("reconstruct nearest confirmed parent context"), falsifier 32.
 *
 * Fixtures mirror `application.inquiry_queries` output field-for-field (F02, published).
 */
import { describe, expect, it } from "vitest";
import type { Capability, ChallengeDetail, SessionPosition, WorkspaceOverview } from "../../lib/api/inquiryClient";
import { accessTrace, challengeTrace, sessionTrace, workspaceTrace } from "../../lib/field/position";

const WS = { workspaceId: "11111111-1111-1111-1111-111111111111", name: "Conversion inquiry", governedFounding: true };
const CH = "22222222-2222-2222-2222-222222222222";
const SID = "33333333-3333-3333-3333-333333333333";

const available: Capability = { available: true, reasonCode: null, reason: null };
const unavailable = (code: string, reason: string): Capability => ({ available: false, reasonCode: code, reason });

function overview(createChallenge: Capability = available): WorkspaceOverview {
  return {
    workspace: WS,
    viewer: { userId: "u", role: "Facilitator", isGovernanceRoot: false },
    members: [],
    challenges: [],
    capabilities: { createChallenge, addMember: unavailable("NOT_GOVERNANCE_ROOT", "…") },
  };
}

function detail(openSession: Capability = available): ChallengeDetail {
  return {
    workspace: WS,
    challenge: { challengeId: CH, title: "Signup conversion dropped 18%", description: null, createdAt: "2026-09-24T10:00:00+00:00" },
    sessions: [],
    sessionControllers: [],
    members: [],
    capabilities: { openSession, grantSessionControl: unavailable("NOT_GOVERNANCE_ROOT", "…") },
  };
}

function position(establishedBy: SessionPosition["establishedBy"]): SessionPosition {
  return {
    workspace: WS,
    challenge: { challengeId: CH, title: "Signup conversion dropped 18%", description: null },
    session: { sessionId: SID, state: "SETUP", version: 2, method: "QUESTION_BURST 1.0", createdAt: "2026-09-24T10:05:00+00:00" },
    phases: [],
    burst: null,
    participants: [],
    sessionControllers: [],
    establishedBy,
    viewer: { userId: "u", role: "Facilitator", isSessionController: true, isGovernanceRoot: false },
    actions: {} as SessionPosition["actions"],
    admitCandidates: [],
    grantCandidates: [],
  };
}

describe("MUST BECOME TRUE", () => {
  it("the access context alone is the trace before any context is confirmed", () => {
    expect(accessTrace("current")).toEqual([{ coordinate: "access", label: "Workspaces", status: "current" }]);
    expect(accessTrace("established")).toEqual([
      { coordinate: "access", label: "Workspaces", status: "established", href: "/workspaces" },
    ]);
  });

  it("Workspace: established access → current Workspace → possible Challenge relation when projected", () => {
    const t = workspaceTrace(overview());
    expect(t.map((s) => [s.coordinate, s.status])).toEqual([
      ["access", "established"],
      ["workspace", "current"],
      ["challenge", "possible"],
    ]);
    expect(t[1]).toMatchObject({ label: "Conversion inquiry" });
    expect(t[2]).toMatchObject({ label: "New Challenge" });
    expect(t[2].href).toBeUndefined();
  });

  it("Workspace: an unprojected Challenge relation stays understandable as unavailable, never as possible", () => {
    const t = workspaceTrace(overview(unavailable("NOT_FACILITATOR", "Creating a Challenge requires the Facilitator role")));
    expect(t[2]).toMatchObject({ coordinate: "challenge", status: "unavailable", reasonCode: "NOT_FACILITATOR" });
  });

  it("Challenge: Workspace → Challenge (current) → Session possible, before any Session exists", () => {
    const t = challengeTrace(detail());
    expect(t.map((s) => [s.coordinate, s.status])).toEqual([
      ["access", "established"],
      ["workspace", "established"],
      ["challenge", "current"],
      ["session", "possible"],
    ]);
    expect(t[1]).toMatchObject({ href: `/workspaces/${WS.workspaceId}`, label: "Conversion inquiry" });
    expect(t[2]).toMatchObject({ label: "Signup conversion dropped 18%" });
    expect(t[3]).toMatchObject({ label: "New Session" });
  });

  it("Challenge: Session relation without projected capability is unavailable with the server reason code", () => {
    const t = challengeTrace(detail(unavailable("NO_CHALLENGE_SESSION_CONTROL:x", "Opening a Session requires …")));
    expect(t[3]).toMatchObject({ status: "unavailable", reasonCode: "NO_CHALLENGE_SESSION_CONTROL:x" });
  });

  it("Session (primitive, adoption deferred to post-F03 sync): state is current, establishing transition carried", () => {
    const t = sessionTrace(
      position({
        commandType: "CMD_BEGIN_SETUP",
        actorName: "Fac",
        occurredAt: "2026-09-24T10:06:00+00:00",
        commitId: "c",
        authoritySourceType: "BINDING",
        authoritySourceRef: "b",
        authorityScopeRef: "SESSION:x",
      }),
    );
    expect(t.map((s) => [s.coordinate, s.status])).toEqual([
      ["access", "established"],
      ["workspace", "established"],
      ["challenge", "established"],
      ["session", "established"],
      ["session-state", "current"],
    ]);
    expect(t[4]).toMatchObject({ label: "SETUP", establishedBy: "CMD_BEGIN_SETUP" });
  });

  it("Session: a state without a governed establishing commit says so, it does not invent one", () => {
    const t = sessionTrace(position(null));
    expect(t[4]).toMatchObject({ label: "SETUP", establishedBy: null });
  });
});

describe("MUST REMAIN IMPOSSIBLE", () => {
  it("no Session coordinate exists in any pre-Session trace", () => {
    for (const t of [accessTrace("current"), workspaceTrace(overview()), challengeTrace(detail())]) {
      expect(t.some((s) => s.coordinate === "session-state")).toBe(false);
      expect(t.filter((s) => s.coordinate === "session").every((s) => s.status === "possible" || s.status === "unavailable")).toBe(true);
    }
  });

  it("F32: a future relation is never a navigable destination", () => {
    for (const t of [workspaceTrace(overview()), challengeTrace(detail())]) {
      for (const s of t.filter((x) => x.status === "possible" || x.status === "unavailable")) {
        expect(s.href).toBeUndefined();
      }
    }
  });

  it("exactly one current coordinate per trace", () => {
    for (const t of [accessTrace("current"), workspaceTrace(overview()), challengeTrace(detail())]) {
      expect(t.filter((s) => s.status === "current")).toHaveLength(1);
    }
  });

  it("the current coordinate is never a link (you are already there)", () => {
    for (const t of [accessTrace("current"), workspaceTrace(overview()), challengeTrace(detail())]) {
      expect(t.find((s) => s.status === "current")?.href).toBeUndefined();
    }
  });

  it("a Challenge without a title is not given an invented one", () => {
    const d = detail();
    const t = challengeTrace({ ...d, challenge: { ...d.challenge, title: "" } });
    expect(t[2].label).toBe("");
  });
});
