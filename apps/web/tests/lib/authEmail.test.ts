import { describe, expect, it, vi } from "vitest";
import { completeEmailVerification, listVerifiedEmails, startEmailVerification } from "../../lib/api/authClient";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("startEmailVerification (WU-AUTH-11)", () => {
  it("POSTs the address with credentials and returns the challenge id, never a token", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", challengeId: "c-1", expiresAt: "2030-01-01T00:30:00+00:00" }));
    const result = await startEmailVerification("Me@Example.test", fetchImpl);
    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringMatching(/\/auth\/email\/verification\/start$/),
      expect.objectContaining({ method: "POST", credentials: "include", body: JSON.stringify({ email: "Me@Example.test" }) }),
    );
    expect(result).toEqual({ kind: "ok", challengeId: "c-1", expiresAt: "2030-01-01T00:30:00+00:00" });
    expect(Object.keys(result)).not.toContain("token");
  });

  it.each([
    [{ kind: "denied", reasonCode: "VERIFICATION_RESEND_THROTTLED" }, 429],
    [{ kind: "rejected", reasonCode: "EMAIL_INVALID" }, 400],
    [{ kind: "unavailable", reasonCode: "EMAIL_DELIVERY_NOT_CONFIGURED" }, 503],
  ])("keeps %j distinct", async (body, status) => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(body, status));
    expect(await startEmailVerification("a@b.test", fetchImpl)).toEqual(body);
  });

  it("fails closed on an unrecognized shape", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok" }));
    await expect(startEmailVerification("a@b.test", fetchImpl)).rejects.toThrow(TypeError);
  });
});

describe("completeEmailVerification (WU-AUTH-11)", () => {
  it("POSTs challenge id and token in the body only", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", email: "a@b.test" }));
    const result = await completeEmailVerification("c-1", "secret-token", fetchImpl);
    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).not.toContain("secret-token");
    expect(init.body).toBe(JSON.stringify({ challengeId: "c-1", token: "secret-token" }));
    expect(result).toEqual({ kind: "ok", email: "a@b.test" });
  });

  it("parses denied and fails closed otherwise", async () => {
    const denied = vi.fn().mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "VERIFICATION_DENIED" }, 403));
    expect(await completeEmailVerification("c", "t", denied)).toEqual({ kind: "denied", reasonCode: "VERIFICATION_DENIED" });
    const odd = vi.fn().mockResolvedValue(jsonResponse({ kind: "verified" }));
    await expect(completeEmailVerification("c", "t", odd)).rejects.toThrow(TypeError);
  });
});

describe("listVerifiedEmails", () => {
  it("reads the caller's verified addresses", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({ kind: "ok", emails: [{ email: "a@b.test", verifiedAt: "2030-01-01T00:00:00+00:00", active: true }] }),
    );
    const result = await listVerifiedEmails(fetchImpl);
    expect(result).toEqual({ kind: "ok", emails: [{ email: "a@b.test", verifiedAt: "2030-01-01T00:00:00+00:00", active: true }] });
  });

  it("fails closed on a malformed entry", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", emails: [{ email: "a@b.test" }] }));
    await expect(listVerifiedEmails(fetchImpl)).rejects.toThrow(TypeError);
  });
});
