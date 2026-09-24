/**
 * F02 WU-02.12 (FBR-C): producer -> consumer outcome vocabulary.
 *
 * MUST BECOME TRUE: every outcome kind a route can actually emit is parsed
 * as that kind by its consumer:
 * - `rejected` from `GET /workspaces/{w}/sessions/{s}` and `GET /workspaces/{w}`
 *   (F02 WU-02.9 E9: malformed input is rejected, not denied);
 * - `rejected` from `POST /auth/login` (framework validation, WU-02.12);
 * - `failed_precommit` from add-member / revoke / decide (WU-02.12: no
 *   longer folded into `rejected`).
 * MUST REMAIN IMPOSSIBLE: a server verdict surfacing as a parse exception
 * (which the UI renders as a network error); an unknown kind defaulting to
 * success.
 */
import { describe, expect, it, vi } from "vitest";
import { login } from "../../lib/api/authClient";
import { parseSessionReadResult } from "../../lib/api/client";
import { parseDecisionActionResult } from "../../lib/api/decisionClient";
import {
  addMember,
  fetchWorkspaceOrientation,
  revokeAuthorityBinding,
} from "../../lib/api/workspaceClient";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("rejected is a verdict, not a transport failure", () => {
  it("session view read parses rejected", () => {
    expect(parseSessionReadResult({ kind: "rejected", reasonCode: "badly formed UUID string" })).toEqual({
      kind: "rejected",
      reasonCode: "badly formed UUID string",
    });
  });

  it("session view read still fails closed on an unknown kind", () => {
    expect(() => parseSessionReadResult({ kind: "failed_precommit", reasonCode: "X" })).toThrow(TypeError);
  });

  it("workspace orientation parses rejected", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "rejected", reasonCode: "badly formed UUID string" }, 400));
    await expect(fetchWorkspaceOrientation("not-a-uuid", fetchImpl)).resolves.toEqual({
      kind: "rejected",
      reasonCode: "badly formed UUID string",
    });
  });

  it("login parses rejected (malformed request body)", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "rejected", reasonCode: "MALFORMED_REQUEST_BODY" }, 400));
    await expect(login("a@b.c", "", fetchImpl)).resolves.toEqual({
      kind: "rejected",
      reasonCode: "MALFORMED_REQUEST_BODY",
    });
  });
});

describe("failed_precommit stays distinct from rejected", () => {
  const body = { kind: "failed_precommit", reasonCode: "SAVEPOINT_ROLLED_BACK" };

  it("add member parses failed_precommit", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(body));
    await expect(addMember("ws", "user", "Contributor", fetchImpl)).resolves.toEqual(body);
  });

  it("revoke parses failed_precommit", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(body));
    await expect(revokeAuthorityBinding("ws", "binding", fetchImpl)).resolves.toEqual(body);
  });

  it("decide parses failed_precommit", () => {
    expect(parseDecisionActionResult(body)).toEqual(body);
  });
});
