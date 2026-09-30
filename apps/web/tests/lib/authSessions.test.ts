import { describe, expect, it, vi } from "vitest";
import { listSessions, logoutAll, revokeSession } from "../../lib/api/authClient";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

const SESSION = {
  sessionId: "11111111-1111-4111-8111-111111111111",
  issuedAt: "2030-01-01T00:00:00+00:00",
  expiresAt: "2030-01-01T12:00:00+00:00",
  current: true,
  methodType: "LOCAL_PASSWORD",
};

describe("listSessions (WU-AUTH-04)", () => {
  it("issues a credentialed GET to /auth/sessions and returns the server's list", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", sessions: [SESSION] }));

    const result = await listSessions(fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/auth/sessions"),
      expect.objectContaining({ credentials: "include" }),
    );
    expect(result).toEqual({ kind: "ok", sessions: [SESSION] });
  });

  it("accepts a session with no method (proof provenance only)", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "ok", sessions: [{ ...SESSION, methodType: null }] }));
    const result = await listSessions(fetchImpl);
    expect(result.kind === "ok" && result.sessions[0].methodType).toBeNull();
  });

  it("parses a denied (no session) response", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "NO_SESSION" }, 401));
    expect(await listSessions(fetchImpl)).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
  });

  it.each([
    { kind: "ok" },
    { kind: "ok", sessions: "many" },
    { kind: "ok", sessions: [{ ...SESSION, current: "yes" }] },
    { kind: "ok", sessions: [{ ...SESSION, sessionId: 7 }] },
    { kind: "ok", sessions: [{ ...SESSION, methodType: 7 }] },
    { kind: "surprising" },
    {},
  ])("fails closed on an unrecognized body %j", async (body) => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(body));
    await expect(listSessions(fetchImpl)).rejects.toThrow(TypeError);
  });

  it("derives nothing from a token: the list type has no token field", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "ok", sessions: [{ ...SESSION, sessionToken: "leak" }] }));
    const result = await listSessions(fetchImpl);
    expect(result.kind === "ok" && Object.keys(result.sessions[0]).sort()).toEqual(
      ["current", "expiresAt", "issuedAt", "methodType", "sessionId"].sort(),
    );
  });
});

describe("revokeSession (WU-AUTH-04)", () => {
  it("POSTs to /auth/sessions/{id}/revoke with credentials and no body", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok" }));

    const result = await revokeSession(SESSION.sessionId, fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringMatching(new RegExp(`/auth/sessions/${SESSION.sessionId}/revoke$`)),
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
    expect(result).toEqual({ kind: "ok" });
  });

  it("encodes the id so a crafted value cannot change the route", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "rejected", reasonCode: "MALFORMED_SESSION_ID" }, 400));
    const result = await revokeSession("../logout-all", fetchImpl);
    expect(fetchImpl.mock.calls[0][0]).toContain("/auth/sessions/..%2Flogout-all/revoke");
    expect(result).toEqual({ kind: "rejected", reasonCode: "MALFORMED_SESSION_ID" });
  });

  it("keeps denied and rejected distinct and fails closed otherwise", async () => {
    const denied = vi.fn().mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "SESSION_NOT_FOUND" }, 404));
    expect(await revokeSession(SESSION.sessionId, denied)).toEqual({ kind: "denied", reasonCode: "SESSION_NOT_FOUND" });
    const odd = vi.fn().mockResolvedValue(jsonResponse({ kind: "done" }));
    await expect(revokeSession(SESSION.sessionId, odd)).rejects.toThrow(TypeError);
  });
});

describe("logoutAll (WU-AUTH-04)", () => {
  it("POSTs to /auth/logout-all with credentials and reports the server's count", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", revokedSessions: 3 }));

    const result = await logoutAll(fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringMatching(/\/auth\/logout-all$/),
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
    expect(result).toEqual({ kind: "ok", revokedSessions: 3 });
  });

  it("parses denied and fails closed on a missing count", async () => {
    const denied = vi.fn().mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "NO_SESSION" }, 401));
    expect(await logoutAll(denied)).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
    const odd = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok" }));
    await expect(logoutAll(odd)).rejects.toThrow(TypeError);
  });
});
