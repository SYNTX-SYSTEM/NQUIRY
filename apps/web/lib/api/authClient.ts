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
