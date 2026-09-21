import { describe, expect, it, vi } from "vitest";
import { fetchCurrentSession, login, logout } from "../../lib/api/authClient";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("login", () => {
  it("POSTs email/password to /auth/login with credentials included", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", userId: "u-1" }));

    const result = await login("demo@nonproof.test", "secret-pw", fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/auth/login"),
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ email: "demo@nonproof.test", password: "secret-pw" }),
      }),
    );
    expect(result).toEqual({ kind: "ok", userId: "u-1" });
  });

  it("parses a denied response without throwing", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "INVALID_CREDENTIALS" }, 401));

    const result = await login("demo@nonproof.test", "wrong", fetchImpl);

    expect(result).toEqual({ kind: "denied", reasonCode: "INVALID_CREDENTIALS" });
  });

  it("fails closed on an unrecognized response shape rather than defaulting to ok", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "surprising" }));

    await expect(login("demo@nonproof.test", "pw", fetchImpl)).rejects.toThrow(TypeError);
  });

  it("fails closed on a missing kind", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({}));

    await expect(login("demo@nonproof.test", "pw", fetchImpl)).rejects.toThrow(TypeError);
  });

  it("never sends the password as a URL query parameter", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", userId: "u-1" }));

    await login("demo@nonproof.test", "super-secret-value", fetchImpl);

    const calledUrl = fetchImpl.mock.calls[0][0] as string;
    expect(calledUrl).not.toContain("super-secret-value");
  });
});

describe("fetchCurrentSession", () => {
  it("issues a credentialed GET to /auth/me", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", userId: "u-1" }));

    const result = await fetchCurrentSession(fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/auth/me"),
      expect.objectContaining({ credentials: "include" }),
    );
    expect(result).toEqual({ kind: "ok", userId: "u-1" });
  });

  it("parses a denied (no session) response", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "NO_SESSION" }, 401));

    const result = await fetchCurrentSession(fetchImpl);

    expect(result).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
  });
});

describe("logout", () => {
  it("POSTs to /auth/logout with credentials included", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok" }));

    await logout(fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/auth/logout"),
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
  });
});
