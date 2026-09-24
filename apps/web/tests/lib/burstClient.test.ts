/**
 * F03 WU-03.10: the protected-Burst client.
 *
 * MUST BECOME TRUE: capture posts EXACTLY the submitted text (never trimmed,
 * normalized or cased) with the Burst version the viewer saw and the caller's
 * Idempotency-Key; completion posts both versions; each server outcome stays
 * distinct; a rejection reason is explained in plain words.
 * MUST REMAIN IMPOSSIBLE: the client sending an origin / author / mode field;
 * a timer helper that yields a deadline or remaining time (HD-11: presentation
 * only); a rejection code rendered as if it were an authority decision.
 */
import { describe, expect, it, vi } from "vitest";
import { captureBurstQuestion, completeBurst } from "../../lib/api/inquiryClient";
import { BURST_GUIDANCE_SECONDS, elapsedSeconds, explainCaptureRejection, formatElapsed, intentKeyFor } from "../../lib/burst";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("captureBurstQuestion transport", () => {
  it("posts the exact text, the burst version and the intent key, and nothing else", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "committed", replayed: false, questionId: "q", position: {} }));
    const text = "  Why did “it” drop — 如何 ?\n  ";
    await captureBurstQuestion("w", "s", text, 4, "intent-9", fetchImpl);
    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).toMatch(/\/workspaces\/w\/sessions\/s\/burst\/questions$/);
    expect(init.method).toBe("POST");
    expect((init.headers as Record<string, string>)["Idempotency-Key"]).toBe("intent-9");
    const body = JSON.parse(init.body as string) as Record<string, unknown>;
    expect(Object.keys(body).sort()).toEqual(["expectedBurstVersion", "originalText"]);
    expect(body.originalText).toBe(text); // byte-exact: no trim, no normalization
    expect(body.expectedBurstVersion).toBe(4);
    expect(init.credentials).toBe("include");
  });

  it("never sends origin, author or mode", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "committed", questionId: "q", position: {} }));
    await captureBurstQuestion("w", "s", "Why?", 1, "k", fetchImpl);
    const body = JSON.parse((fetchImpl.mock.calls[0] as [string, RequestInit])[1].body as string) as Record<string, unknown>;
    for (const forbidden of ["origin", "authorUserId", "author", "mode", "captureOrigin", "normalizedText"]) {
      expect(Object.keys(body)).not.toContain(forbidden);
    }
  });

  it.each(["denied", "rejected", "stale", "blocked", "failed_precommit", "indeterminate"])(
    "keeps a %s capture outcome distinct",
    async (kind) => {
      const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind, reasonCode: "X" }, 400));
      await expect(captureBurstQuestion("w", "s", "Why?", 1, "k", fetchImpl)).resolves.toMatchObject({ kind, reasonCode: "X" });
    },
  );

  it("maps a rejected fetch to network_failure", async () => {
    const fetchImpl = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));
    await expect(captureBurstQuestion("w", "s", "Why?", 1, "k", fetchImpl)).resolves.toEqual({
      kind: "network_failure",
      reasonCode: "NETWORK_FAILURE",
    });
  });
});

describe("completeBurst transport", () => {
  it("posts the session and burst versions the viewer saw", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "committed", replayed: false, position: {} }));
    await completeBurst("w", "s", 5, 2, "intent-c", fetchImpl);
    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).toMatch(/\/workspaces\/w\/sessions\/s\/transitions\/complete-burst$/);
    expect(JSON.parse(init.body as string)).toEqual({ expectedVersion: 5, expectedBurstVersion: 2 });
    expect((init.headers as Record<string, string>)["Idempotency-Key"]).toBe("intent-c");
  });
});

describe("rejection explanations", () => {
  it("explains a form rejection without implying an authority decision", () => {
    const text = explainCaptureRejection("INPUT_NOT_A_QUESTION");
    expect(text).toMatch(/question mark/i);
    expect(text).toMatch(/nothing was stored/i);
    expect(text).not.toMatch(/denied|forbidden|not allowed to/i);
  });

  it.each(["INPUT_EMPTY", "INPUT_TOO_LONG", "INPUT_NOT_STORABLE"])("explains %s", (code) => {
    expect(explainCaptureRejection(code)).toMatch(/nothing was stored/i);
  });

  it("shows an unknown code verbatim rather than inventing a meaning", () => {
    expect(explainCaptureRejection("SOMETHING_NEW")).toContain("SOMETHING_NEW");
  });
});

describe("timer presentation (HD-11: elapsed only, never a deadline)", () => {
  it("computes elapsed time from the server clock, robust to client clock skew", () => {
    // server says: started 100 s before serverNow. The client clock is 1 h ahead of the server.
    const serverNow = "2026-09-24T10:01:40.000Z";
    const startedAt = "2026-09-24T10:00:00.000Z";
    const loadedAtClientMs = Date.parse("2026-09-24T11:01:40.000Z");
    expect(elapsedSeconds(startedAt, serverNow, loadedAtClientMs, loadedAtClientMs)).toBe(100);
    expect(elapsedSeconds(startedAt, serverNow, loadedAtClientMs, loadedAtClientMs + 5_000)).toBe(105);
  });

  it("never returns a negative elapsed time", () => {
    expect(elapsedSeconds("2026-09-24T10:00:10.000Z", "2026-09-24T10:00:00.000Z", 0, 0)).toBe(0);
  });

  it("formats mm:ss and exposes a guidance constant, not a countdown", () => {
    expect(formatElapsed(0)).toBe("00:00");
    expect(formatElapsed(125)).toBe("02:05");
    expect(BURST_GUIDANCE_SECONDS).toBe(240);
    const exported = Object.keys(require_burst());
    expect(exported.some((name) => /remaining|deadline|countdown|expires/i.test(name))).toBe(false);
  });
});

describe("one intent key per logical capture", () => {
  it("keeps the key for the same text (a retry after no response) and issues a new one for other text", () => {
    let n = 0;
    const make = () => `key-${++n}`;
    const first = intentKeyFor(null, "Why?", make);
    const retry = intentKeyFor(first, "Why?", make);
    const changed = intentKeyFor(first, "Why not?", make);
    expect(retry).toEqual(first);
    expect(changed.key).not.toBe(first.key);
    expect(changed.text).toBe("Why not?");
  });
});

import * as burst from "../../lib/burst";
function require_burst(): Record<string, unknown> {
  return burst as unknown as Record<string, unknown>;
}
