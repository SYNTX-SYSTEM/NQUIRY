import { describe, expect, it, vi } from "vitest";
import { linkProjectionMessage, linkStartUrl, listMethods, unlinkMethod } from "../../lib/api/authClient";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

const LOCAL = {
  methodId: "11111111-1111-4111-8111-111111111111",
  methodType: "LOCAL_PASSWORD",
  status: "ACTIVE",
  createdAt: "2030-01-01T00:00:00+00:00",
  lastAuthenticatedAt: null,
  provider: null,
};
const PROVIDER = {
  ...LOCAL,
  methodId: "22222222-2222-4222-8222-222222222222",
  methodType: "TEST_PROVIDER",
  lastAuthenticatedAt: "2030-01-01T01:00:00+00:00",
  provider: { providerId: "test", email: "p@example.test" },
};

describe("listMethods (WU-AUTH-10)", () => {
  it("reads the caller's own methods with credentials", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", methods: [LOCAL, PROVIDER] }));
    const result = await listMethods(fetchImpl);
    expect(fetchImpl).toHaveBeenCalledWith(expect.stringMatching(/\/auth\/methods$/), expect.objectContaining({ credentials: "include" }));
    expect(result).toEqual({ kind: "ok", methods: [LOCAL, PROVIDER] });
  });

  it("parses denied", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "NO_SESSION" }, 401));
    expect(await listMethods(fetchImpl)).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
  });

  it.each([
    { kind: "ok" },
    { kind: "ok", methods: [{ ...LOCAL, provider: "google" }] },
    { kind: "ok", methods: [{ ...PROVIDER, provider: { email: "x" } }] },
    { kind: "ok", methods: [{ ...LOCAL, lastAuthenticatedAt: 5 }] },
    { kind: "surprising" },
  ])("fails closed on %j", async (body) => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(body));
    await expect(listMethods(fetchImpl)).rejects.toThrow(TypeError);
  });

  it("carries no secret-shaped field", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "ok", methods: [{ ...LOCAL, passwordHash: "x", providerSubject: "s" }] }));
    const result = await listMethods(fetchImpl);
    expect(result.kind === "ok" && Object.keys(result.methods[0]).sort()).toEqual(
      ["createdAt", "lastAuthenticatedAt", "methodId", "methodType", "provider", "status"],
    );
  });
});

describe("linkStartUrl / linkProjectionMessage", () => {
  it("is the API link-start contact with the redirect candidate", () => {
    expect(linkStartUrl("test", "/account/security")).toMatch(/\/auth\/oidc\/test\/link\/start\?next=%2Faccount%2Fsecurity$/);
  });

  it("maps projections and collapses unknown codes", () => {
    expect(linkProjectionMessage(null)).toBeNull();
    expect(linkProjectionMessage("ok")).toMatch(/linked/);
    expect(linkProjectionMessage("collision")).toMatch(/another account/);
    expect(linkProjectionMessage("hasOwnProperty")).toBe(linkProjectionMessage("failed"));
  });
});

describe("unlinkMethod (WU-AUTH-13)", () => {
  const ok = { kind: "ok", methodId: "m-1", sessionsRevoked: 2, currentSessionEnded: true };

  it("POSTs to the method's unlink contact with credentials and parses the propagation facts", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(ok), { status: 200, headers: { "Content-Type": "application/json" } }),
    );
    const result = await unlinkMethod("m-1", fetchImpl);
    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringMatching(/\/auth\/methods\/m-1\/unlink$/),
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
    expect(result).toEqual(ok);
  });

  it.each([
    [{ kind: "denied", reasonCode: "LAST_METHOD" }, 409],
    [{ kind: "denied", reasonCode: "UNLINK_DENIED" }, 403],
    [{ kind: "denied", reasonCode: "NO_SESSION" }, 401],
    [{ kind: "rejected", reasonCode: "MALFORMED_METHOD_ID" }, 400],
  ])("keeps %j distinct", async (body, status) => {
    const fetchImpl = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } }),
    );
    expect(await unlinkMethod("m-1", fetchImpl)).toEqual(body);
  });

  it("fails closed on an ok without the propagation facts", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ kind: "ok", methodId: "m-1" }), { status: 200, headers: { "Content-Type": "application/json" } }),
    );
    await expect(unlinkMethod("m-1", fetchImpl)).rejects.toThrow(TypeError);
  });
});
