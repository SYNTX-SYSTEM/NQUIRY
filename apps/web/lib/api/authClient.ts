/**
 * Local-login field (`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`).
 *
 * Real `fetch` calls against `POST /auth/login`, `POST /auth/logout`,
 * `GET /auth/me` -- the same "genuine cross-origin fetch, fail-closed
 * parse of whatever the server actually returns" discipline
 * `client.ts`/`decisionClient.ts` already establish, applied to the
 * three auth routes instead of the two Architecture-17 routes.
 *
 * `credentials: "include"` on every call is load-bearing: without it,
 * the browser neither sends the existing `nquiry_session` cookie
 * cross-origin nor stores a new one `Set-Cookie` tries to set (the
 * `Access-Control-Allow-Credentials: true` the server sends,
 * `apps/api/src/nquiry_api/main.py`, is the other required half of the
 * same mechanism).
 *
 * This module computes no authority of its own -- `login` either
 * succeeds (the server issued a real session) or fails (the server's
 * own `denied` response), and `fetchCurrentSession` is a pure read of
 * whatever the server currently thinks the caller's session is. There
 * is no client-side guess anywhere in this file.
 */
import { apiBaseUrl, isRecord, requireString } from "./client";

export type LoginResult =
  | { readonly kind: "ok"; readonly userId: string }
  | { readonly kind: "denied"; readonly reasonCode: string }
  // F02 WU-02.12 (FBR-C): a malformed login body is REJECTED (400) by the API.
  | { readonly kind: "rejected"; readonly reasonCode: string };

export type CurrentSessionResult =
  | { readonly kind: "ok"; readonly userId: string }
  | { readonly kind: "denied"; readonly reasonCode: string };

export async function login(
  email: string,
  password: string,
  fetchImpl: typeof fetch = fetch,
): Promise<LoginResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });
  const body: unknown = await response.json();
  return parseAuthResult(body);
}

export async function logout(fetchImpl: typeof fetch = fetch): Promise<void> {
  await fetchImpl(`${apiBaseUrl()}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export async function fetchCurrentSession(fetchImpl: typeof fetch = fetch): Promise<CurrentSessionResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/me`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  const body: unknown = await response.json();
  const result = parseAuthResult(body);
  if (result.kind === "rejected") {
    // `GET /auth/me` takes no input, so it has nothing to reject: fail closed.
    throw new TypeError("unexpected 'rejected' from GET /auth/me");
  }
  return result;
}

/**
 * Shared parser for all three routes' own identical two-case shape
 * (`{"kind":"ok","userId":...}` / `{"kind":"denied","reasonCode":...}`)
 * -- fails closed on any unrecognized body, same discipline as
 * `client.ts::parseSessionReadResult`.
 */
function parseAuthResult(body: unknown): LoginResult {
  if (!isRecord(body) || typeof body.kind !== "string") {
    throw new TypeError("auth response body is missing a recognizable 'kind'");
  }
  switch (body.kind) {
    case "ok":
      return { kind: "ok", userId: requireString(body, "userId") };
    case "denied":
      return { kind: "denied", reasonCode: requireString(body, "reasonCode") };
    case "rejected":
      return { kind: "rejected", reasonCode: requireString(body, "reasonCode") };
    default:
      throw new TypeError(`unrecognized auth response kind ${JSON.stringify(body.kind)}`);
  }
}

// --- WU-AUTH-04 (24 §15.7, §24.5): the caller's own sessions ---------------
//
// Projection only. The server decides which sessions exist, which one is the
// current one and whether a revocation happened; nothing here keeps or
// derives session truth. No session token or token hash is ever part of
// these shapes: a listed session is named by its id only.

export type SessionSummary = {
  readonly sessionId: string;
  readonly issuedAt: string;
  readonly expiresAt: string;
  readonly current: boolean;
  /** The authentication method type, or null for a session no method produced. */
  readonly methodType: string | null;
};

export type SessionListResult =
  | { readonly kind: "ok"; readonly sessions: readonly SessionSummary[] }
  | { readonly kind: "denied"; readonly reasonCode: string };

export type SessionRevokeResult =
  | { readonly kind: "ok" }
  | { readonly kind: "denied"; readonly reasonCode: string }
  | { readonly kind: "rejected"; readonly reasonCode: string };

export type LogoutAllResult =
  | { readonly kind: "ok"; readonly revokedSessions: number }
  | { readonly kind: "denied"; readonly reasonCode: string };

function parseSessionSummary(value: unknown): SessionSummary {
  if (!isRecord(value) || typeof value.current !== "boolean") {
    throw new TypeError("session summary is malformed");
  }
  if (value.methodType !== null && typeof value.methodType !== "string") {
    throw new TypeError("session summary has a malformed 'methodType'");
  }
  return {
    sessionId: requireString(value, "sessionId"),
    issuedAt: requireString(value, "issuedAt"),
    expiresAt: requireString(value, "expiresAt"),
    current: value.current,
    methodType: value.methodType,
  };
}

function requireKind(body: unknown): Record<string, unknown> & { kind: string } {
  if (!isRecord(body) || typeof body.kind !== "string") {
    throw new TypeError("auth response body is missing a recognizable 'kind'");
  }
  return body as Record<string, unknown> & { kind: string };
}

export async function listSessions(fetchImpl: typeof fetch = fetch): Promise<SessionListResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/sessions`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  const body = requireKind(await response.json());
  if (body.kind === "denied") {
    return { kind: "denied", reasonCode: requireString(body, "reasonCode") };
  }
  if (body.kind === "ok" && Array.isArray(body.sessions)) {
    return { kind: "ok", sessions: body.sessions.map(parseSessionSummary) };
  }
  throw new TypeError(`unrecognized session list response ${JSON.stringify(body.kind)}`);
}

export async function revokeSession(
  sessionId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<SessionRevokeResult> {
  const response = await fetchImpl(
    `${apiBaseUrl()}/auth/sessions/${encodeURIComponent(sessionId)}/revoke`,
    { method: "POST", headers: { Accept: "application/json" }, credentials: "include" },
  );
  const body = requireKind(await response.json());
  switch (body.kind) {
    case "ok":
      return { kind: "ok" };
    case "denied":
      return { kind: "denied", reasonCode: requireString(body, "reasonCode") };
    case "rejected":
      return { kind: "rejected", reasonCode: requireString(body, "reasonCode") };
    default:
      throw new TypeError(`unrecognized session revoke response ${JSON.stringify(body.kind)}`);
  }
}

export async function logoutAll(fetchImpl: typeof fetch = fetch): Promise<LogoutAllResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/logout-all`, {
    method: "POST",
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  const body = requireKind(await response.json());
  if (body.kind === "denied") {
    return { kind: "denied", reasonCode: requireString(body, "reasonCode") };
  }
  if (body.kind === "ok" && typeof body.revokedSessions === "number") {
    return { kind: "ok", revokedSessions: body.revokedSessions };
  }
  throw new TypeError(`unrecognized logout-all response ${JSON.stringify(body.kind)}`);
}
