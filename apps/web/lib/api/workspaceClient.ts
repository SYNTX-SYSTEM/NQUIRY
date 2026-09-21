/**
 * F01 WU-01.9 -- real `fetch` calls against the five WU-01.8 HTTP
 * routes (`POST /workspaces`, `GET /workspaces`,
 * `GET /workspaces/{workspaceId}`, `POST /workspaces/{workspaceId}/members`,
 * `POST /workspaces/{workspaceId}/authority-bindings/{bindingId}/revoke`).
 * Same "genuine cross-origin fetch, fail-closed parse of whatever the
 * server actually returns" discipline `client.ts`/`authClient.ts`
 * already establish. `credentials: "include"` on every call for the
 * identical reason `authClient.ts`'s own module docstring gives -- the
 * real `nquiry_session` cookie only travels cross-origin with it.
 *
 * This module computes no authority of its own. Every result type
 * below is a direct, fail-closed narrowing of the real server
 * response; a `denied`/`rejected`/`indeterminate` body is returned to
 * the caller exactly as the server sent it, never upgraded to a
 * client-side guess at success.
 */
import { apiBaseUrl, isRecord, requireString } from "./client";

export type WorkspaceSummary = {
  readonly workspaceId: string;
  readonly name: string;
  readonly ownerId: string;
  readonly createdAt: string;
};

export type CreateWorkspaceResult =
  | { readonly kind: "ok"; readonly workspaceId: string }
  | { readonly kind: "denied"; readonly reasonCode: string }
  | { readonly kind: "rejected"; readonly reasonCode: string };

export type ListWorkspacesResult =
  | { readonly kind: "ok"; readonly workspaces: readonly WorkspaceSummary[] }
  | { readonly kind: "denied"; readonly reasonCode: string };

export type WorkspaceOrientationResult =
  | {
      readonly kind: "ok";
      readonly workspace: WorkspaceSummary;
      readonly role: string;
      readonly heldAuthorityClasses: readonly string[];
      readonly authorized: boolean;
      readonly governanceCapable: boolean;
    }
  | { readonly kind: "denied"; readonly reasonCode: string };

export type GovernanceActionResult =
  | { readonly kind: "ok" }
  | { readonly kind: "denied"; readonly reasonCode: string }
  | { readonly kind: "rejected"; readonly reasonCode: string }
  | { readonly kind: "indeterminate"; readonly blockedTargetRef: string };

export async function createWorkspace(
  name: string,
  fetchImpl: typeof fetch = fetch,
): Promise<CreateWorkspaceResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/workspaces`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    credentials: "include",
    body: JSON.stringify({ name }),
  });
  const body: unknown = await response.json();
  return parseCreateWorkspaceResult(body);
}

export async function listWorkspaces(fetchImpl: typeof fetch = fetch): Promise<ListWorkspacesResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/workspaces`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  const body: unknown = await response.json();
  return parseListWorkspacesResult(body);
}

export async function fetchWorkspaceOrientation(
  workspaceId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<WorkspaceOrientationResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/workspaces/${encodeURIComponent(workspaceId)}`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  const body: unknown = await response.json();
  return parseWorkspaceOrientationResult(body);
}

export async function addMember(
  workspaceId: string,
  userId: string,
  role: string,
  fetchImpl: typeof fetch = fetch,
): Promise<GovernanceActionResult> {
  const response = await fetchImpl(
    `${apiBaseUrl()}/workspaces/${encodeURIComponent(workspaceId)}/members`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      credentials: "include",
      body: JSON.stringify({ userId, role }),
    },
  );
  const body: unknown = await response.json();
  return parseGovernanceActionResult(body);
}

export async function revokeAuthorityBinding(
  workspaceId: string,
  bindingId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<GovernanceActionResult> {
  const response = await fetchImpl(
    `${apiBaseUrl()}/workspaces/${encodeURIComponent(workspaceId)}/authority-bindings/${encodeURIComponent(bindingId)}/revoke`,
    { method: "POST", credentials: "include" },
  );
  const body: unknown = await response.json();
  return parseGovernanceActionResult(body);
}

function parseWorkspaceSummary(value: unknown): WorkspaceSummary {
  if (!isRecord(value)) {
    throw new TypeError("WorkspaceSummary body must be an object");
  }
  return {
    workspaceId: requireString(value, "workspaceId"),
    name: requireString(value, "name"),
    ownerId: requireString(value, "ownerId"),
    createdAt: requireString(value, "createdAt"),
  };
}

function parseCreateWorkspaceResult(body: unknown): CreateWorkspaceResult {
  if (!isRecord(body) || typeof body.kind !== "string") {
    throw new TypeError("CreateWorkspaceResult body is missing a recognizable 'kind'");
  }
  switch (body.kind) {
    case "ok":
      return { kind: "ok", workspaceId: requireString(body, "workspaceId") };
    case "denied":
      return { kind: "denied", reasonCode: requireString(body, "reasonCode") };
    case "rejected":
      return { kind: "rejected", reasonCode: requireString(body, "reasonCode") };
    default:
      throw new TypeError(`unrecognized CreateWorkspaceResult kind ${JSON.stringify(body.kind)}`);
  }
}

function parseListWorkspacesResult(body: unknown): ListWorkspacesResult {
  if (!isRecord(body) || typeof body.kind !== "string") {
    throw new TypeError("ListWorkspacesResult body is missing a recognizable 'kind'");
  }
  switch (body.kind) {
    case "ok": {
      if (!Array.isArray(body.workspaces)) {
        throw new TypeError("ListWorkspacesResult.workspaces must be an array");
      }
      return { kind: "ok", workspaces: body.workspaces.map(parseWorkspaceSummary) };
    }
    case "denied":
      return { kind: "denied", reasonCode: requireString(body, "reasonCode") };
    default:
      throw new TypeError(`unrecognized ListWorkspacesResult kind ${JSON.stringify(body.kind)}`);
  }
}

function parseWorkspaceOrientationResult(body: unknown): WorkspaceOrientationResult {
  if (!isRecord(body) || typeof body.kind !== "string") {
    throw new TypeError("WorkspaceOrientationResult body is missing a recognizable 'kind'");
  }
  switch (body.kind) {
    case "ok": {
      if (
        !Array.isArray(body.heldAuthorityClasses) ||
        !body.heldAuthorityClasses.every((c) => typeof c === "string")
      ) {
        throw new TypeError("WorkspaceOrientationResult.heldAuthorityClasses must be an array of strings");
      }
      if (typeof body.authorized !== "boolean" || typeof body.governanceCapable !== "boolean") {
        throw new TypeError("WorkspaceOrientationResult.authorized/governanceCapable must be booleans");
      }
      return {
        kind: "ok",
        workspace: parseWorkspaceSummary(body.workspace),
        role: requireString(body, "role"),
        heldAuthorityClasses: body.heldAuthorityClasses,
        authorized: body.authorized,
        governanceCapable: body.governanceCapable,
      };
    }
    case "denied":
      return { kind: "denied", reasonCode: requireString(body, "reasonCode") };
    default:
      throw new TypeError(`unrecognized WorkspaceOrientationResult kind ${JSON.stringify(body.kind)}`);
  }
}

function parseGovernanceActionResult(body: unknown): GovernanceActionResult {
  if (!isRecord(body) || typeof body.kind !== "string") {
    throw new TypeError("GovernanceActionResult body is missing a recognizable 'kind'");
  }
  switch (body.kind) {
    case "ok":
      return { kind: "ok" };
    case "denied":
      return { kind: "denied", reasonCode: requireString(body, "reasonCode") };
    case "rejected":
      return { kind: "rejected", reasonCode: requireString(body, "reasonCode") };
    case "indeterminate":
      return { kind: "indeterminate", blockedTargetRef: requireString(body, "blockedTargetRef") };
    default:
      throw new TypeError(`unrecognized GovernanceActionResult kind ${JSON.stringify(body.kind)}`);
  }
}
