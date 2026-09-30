import { describe, expect, it, vi } from "vitest";
import { authProjectionMessage, listProviders, providerStartUrl } from "../../lib/api/authClient";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("listProviders (WU-AUTH-07)", () => {
  it("reads the configured providers from the server", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({ kind: "ok", providers: [{ providerId: "test", label: "Test provider", proofClass: "TEST_PROVIDER" }] }),
    );
    const result = await listProviders(fetchImpl);
    expect(fetchImpl).toHaveBeenCalledWith(expect.stringMatching(/\/auth\/providers$/), expect.objectContaining({ credentials: "include" }));
    expect(result).toEqual({ kind: "ok", providers: [{ providerId: "test", label: "Test provider", proofClass: "TEST_PROVIDER" }] });
  });

  it("an empty list means no provider button, never a default provider", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", providers: [] }));
    expect(await listProviders(fetchImpl)).toEqual({ kind: "ok", providers: [] });
  });

  it.each([{ kind: "ok" }, { kind: "ok", providers: [{ providerId: "x" }] }, { kind: "surprising" }, {}])(
    "fails closed on %j",
    async (body) => {
      const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(body));
      await expect(listProviders(fetchImpl)).rejects.toThrow(TypeError);
    },
  );
});

describe("providerStartUrl", () => {
  it("is the API start contact with the redirect candidate as a query parameter", () => {
    expect(providerStartUrl("test", "/workspaces")).toMatch(/\/auth\/oidc\/test\/start\?next=%2Fworkspaces$/);
  });

  it("encodes the provider id", () => {
    expect(providerStartUrl("a/b", "/")).toContain("/auth/oidc/a%2Fb/start");
  });
});

describe("authProjectionMessage", () => {
  it("maps each known projection and collapses unknown codes to the generic failure", () => {
    expect(authProjectionMessage(null)).toBeNull();
    expect(authProjectionMessage("cancelled")).toMatch(/cancelled/);
    expect(authProjectionMessage("unavailable")).toMatch(/not available/);
    expect(authProjectionMessage("constructor")).toBe(authProjectionMessage("failed"));
    expect(authProjectionMessage("<script>")).toBe(authProjectionMessage("failed"));
  });
});
