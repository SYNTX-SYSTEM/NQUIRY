import { describe, expect, it, vi } from "vitest";
import {
  addMember,
  createWorkspace,
  fetchWorkspaceOrientation,
  listWorkspaces,
  revokeAuthorityBinding,
} from "../../lib/api/workspaceClient";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("createWorkspace", () => {
  it("POSTs the name to /workspaces with credentials included", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", workspaceId: "ws-1" }));

    const result = await createWorkspace("My Workspace", fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/workspaces"),
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ name: "My Workspace" }),
      }),
    );
    expect(result).toEqual({ kind: "ok", workspaceId: "ws-1" });
  });

  it("parses a rejected response (e.g. empty name) without throwing", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "rejected", reasonCode: "WORKSPACE_NAME_REQUIRED" }));

    const result = await createWorkspace("", fetchImpl);

    expect(result).toEqual({ kind: "rejected", reasonCode: "WORKSPACE_NAME_REQUIRED" });
  });

  it("fails closed on an unrecognized response shape", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "surprising" }));

    await expect(createWorkspace("X", fetchImpl)).rejects.toThrow(TypeError);
  });
});

describe("listWorkspaces", () => {
  it("issues a credentialed GET to /workspaces", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", workspaces: [] }));

    const result = await listWorkspaces(fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/workspaces"),
      expect.objectContaining({ credentials: "include" }),
    );
    expect(result).toEqual({ kind: "ok", workspaces: [] });
  });

  it("parses a real list of workspace summaries", async () => {
    const workspace = {
      workspaceId: "ws-1",
      name: "Team",
      ownerId: "user-1",
      createdAt: "2026-01-01T00:00:00Z",
    };
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", workspaces: [workspace] }));

    const result = await listWorkspaces(fetchImpl);

    expect(result).toEqual({ kind: "ok", workspaces: [workspace] });
  });

  it("fails closed on a missing kind", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({}));

    await expect(listWorkspaces(fetchImpl)).rejects.toThrow(TypeError);
  });
});

describe("fetchWorkspaceOrientation", () => {
  it("issues a credentialed GET to /workspaces/{workspaceId}", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        kind: "ok",
        workspace: { workspaceId: "ws-1", name: "Team", ownerId: "u-1", createdAt: "2026-01-01T00:00:00Z" },
        role: "Owner",
        heldAuthorityClasses: ["WORKSPACE_GOVERNANCE_RIGHT"],
        authorized: true,
        governanceCapable: true,
      }),
    );

    const result = await fetchWorkspaceOrientation("ws-1", fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/workspaces/ws-1"),
      expect.objectContaining({ credentials: "include" }),
    );
    expect(result).toEqual({
      kind: "ok",
      workspace: { workspaceId: "ws-1", name: "Team", ownerId: "u-1", createdAt: "2026-01-01T00:00:00Z" },
      role: "Owner",
      heldAuthorityClasses: ["WORKSPACE_GOVERNANCE_RIGHT"],
      authorized: true,
      governanceCapable: true,
    });
  });

  it("parses a denied response (not a member) without throwing", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "denied", result: "DENY", reasonCode: "NOT_A_WORKSPACE_MEMBER" }));

    const result = await fetchWorkspaceOrientation("ws-1", fetchImpl);

    expect(result).toEqual({ kind: "denied", reasonCode: "NOT_A_WORKSPACE_MEMBER" });
  });

  it("never sends the workspaceId anywhere but the URL path (no client-side authority guess)", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        kind: "denied",
        result: "DENY",
        reasonCode: "WORKSPACE_NOT_FOUND",
      }),
    );

    await fetchWorkspaceOrientation("forged-id", fetchImpl);

    const [, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(init.body).toBeUndefined();
  });
});

describe("addMember", () => {
  it("POSTs userId/role to /workspaces/{workspaceId}/members with credentials included", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok" }));

    const result = await addMember("ws-1", "user-2", "Contributor", fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/workspaces/ws-1/members"),
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        body: JSON.stringify({ userId: "user-2", role: "Contributor" }),
      }),
    );
    expect(result).toEqual({ kind: "ok" });
  });

  it("parses a denied response without throwing", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "denied", result: "DENY", reasonCode: "BND_004_DENIED" }));

    const result = await addMember("ws-1", "user-2", "Contributor", fetchImpl);

    expect(result).toEqual({ kind: "denied", reasonCode: "BND_004_DENIED" });
  });

  it("parses a rejected response (e.g. Owner role refused) without throwing", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "rejected", reasonCode: "OWNER_ROLE_NOT_ASSIGNABLE:..." }));

    const result = await addMember("ws-1", "user-2", "Owner", fetchImpl);

    expect(result).toEqual({ kind: "rejected", reasonCode: "OWNER_ROLE_NOT_ASSIGNABLE:..." });
  });
});

describe("revokeAuthorityBinding", () => {
  it("POSTs to the revoke route with credentials included and no body", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok" }));

    const result = await revokeAuthorityBinding("ws-1", "binding-1", fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/workspaces/ws-1/authority-bindings/binding-1/revoke"),
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
    expect(result).toEqual({ kind: "ok" });
  });

  it("parses the governance-root-orphaning refusal without throwing", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "rejected", reasonCode: "GOVERNANCE_ROOT_ORPHANING_REFUSED:..." }));

    const result = await revokeAuthorityBinding("ws-1", "binding-1", fetchImpl);

    expect(result).toEqual({ kind: "rejected", reasonCode: "GOVERNANCE_ROOT_ORPHANING_REFUSED:..." });
  });

  it("fails closed on an unrecognized response shape", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "surprising" }));

    await expect(revokeAuthorityBinding("ws-1", "binding-1", fetchImpl)).rejects.toThrow(TypeError);
  });
});
