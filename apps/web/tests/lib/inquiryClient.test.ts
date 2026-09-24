/**
 * F02 WU-02.10: the envelope parser keeps every outcome kind distinct, fails
 * closed on unknown bodies, never turns a network failure into a server
 * verdict, and always sends the caller's Idempotency-Key.
 */
import { describe, expect, it, vi } from "vitest";
import { parseCommand, parseQuery, runSessionCommand, createChallenge } from "../../lib/api/inquiryClient";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("envelope parsing", () => {
  it.each(["denied", "rejected", "stale", "blocked", "failed_precommit", "indeterminate", "not_found"])(
    "keeps %s distinct",
    (kind) => {
      expect(parseCommand({ kind, reasonCode: "X" })).toEqual({ kind, reasonCode: "X" });
    },
  );

  it("carries stale detail", () => {
    expect(parseCommand({ kind: "stale", reasonCode: "STALE_VERSION", currentState: "SETUP", currentVersion: 2 })).toEqual({
      kind: "stale",
      reasonCode: "STALE_VERSION",
      currentState: "SETUP",
      currentVersion: 2,
    });
  });

  it("fails closed on an unknown kind or a non-object", () => {
    expect(parseCommand({ kind: "success" }).kind).toBe("indeterminate");
    expect(parseQuery("nope").kind).toBe("indeterminate");
    expect(parseQuery({ kind: "committed" }).kind).toBe("indeterminate");
  });

  it("never treats a query `ok` as a Command commit or vice versa", () => {
    expect(parseCommand({ kind: "ok" }).kind).toBe("indeterminate");
  });
});

describe("transport", () => {
  it("sends the intent key as Idempotency-Key with the expected version", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "committed", replayed: false, position: {} }));
    await runSessionCommand("w", "s", "BEGIN_SETUP", 3, "intent-1", {}, fetchImpl);
    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).toMatch(/\/workspaces\/w\/sessions\/s\/transitions\/begin-setup$/);
    expect((init.headers as Record<string, string>)["Idempotency-Key"]).toBe("intent-1");
    expect(JSON.parse(init.body as string)).toEqual({ expectedVersion: 3 });
    expect(init.credentials).toBe("include");
  });

  it("maps a rejected fetch to network_failure, not to a server verdict", async () => {
    const fetchImpl = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));
    const result = await createChallenge("w", { title: "t", description: "" }, "k", fetchImpl);
    expect(result).toEqual({ kind: "network_failure", reasonCode: "NETWORK_FAILURE" });
  });
});
