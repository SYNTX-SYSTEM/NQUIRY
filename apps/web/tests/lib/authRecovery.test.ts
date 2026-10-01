import { describe, expect, it, vi } from "vitest";
import { completeRecovery, startRecovery } from "../../lib/api/authClient";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("startRecovery (WU-AUTH-12)", () => {
  it("POSTs the address and returns the non-enumerating ok", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok" }));
    expect(await startRecovery("Me@Example.test", fetchImpl)).toEqual({ kind: "ok" });
    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringMatching(/\/auth\/recovery\/start$/),
      expect.objectContaining({ method: "POST", body: JSON.stringify({ email: "Me@Example.test" }) }),
    );
  });

  it("keeps unavailable distinct and fails closed on anything else", async () => {
    const unavailable = vi.fn().mockResolvedValue(jsonResponse({ kind: "unavailable", reasonCode: "RECOVERY_NOT_AVAILABLE" }, 503));
    expect(await startRecovery("a@b.test", unavailable)).toEqual({ kind: "unavailable", reasonCode: "RECOVERY_NOT_AVAILABLE" });
    const odd = vi.fn().mockResolvedValue(jsonResponse({ kind: "sent" }));
    await expect(startRecovery("a@b.test", odd)).rejects.toThrow(TypeError);
    const leaking = vi.fn().mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "NO_SUCH_ACCOUNT" }, 403));
    await expect(startRecovery("a@b.test", leaking)).rejects.toThrow(TypeError);
  });
});

describe("completeRecovery (WU-AUTH-12)", () => {
  it("sends id, token and the new password in the body only", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok" }));
    expect(await completeRecovery("r-1", "secret-token", "a brand new passphrase", fetchImpl)).toEqual({ kind: "ok" });
    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).not.toContain("secret-token");
    expect(url).toMatch(/\/auth\/recovery\/complete$/);
    expect(init.body).toBe(JSON.stringify({ recoveryId: "r-1", token: "secret-token", newPassword: "a brand new passphrase" }));
  });

  it.each([
    [{ kind: "denied", reasonCode: "RECOVERY_DENIED" }, 403],
    [{ kind: "rejected", reasonCode: "PASSWORD_INVALID" }, 400],
    [{ kind: "rejected", reasonCode: "MALFORMED_RECOVERY_ID" }, 400],
    [{ kind: "unavailable", reasonCode: "RECOVERY_NOT_AVAILABLE" }, 503],
  ])("keeps %j distinct", async (body, status) => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(body, status));
    expect(await completeRecovery("r", "t", "p", fetchImpl)).toEqual(body);
  });

  it("fails closed on an unrecognized shape", async () => {
    const odd = vi.fn().mockResolvedValue(jsonResponse({ kind: "reset", sessionToken: "x" }));
    await expect(completeRecovery("r", "t", "p", odd)).rejects.toThrow(TypeError);
  });
});
