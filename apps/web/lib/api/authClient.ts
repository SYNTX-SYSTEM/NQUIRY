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

// --- WU-AUTH-07 (24 §24.2): configured external providers ------------------
//
// A provider button exists only for a provider the backend reports as
// configured. The frontend never decides provider availability, and starting
// a provider login is a plain top-level navigation to the API's start
// contact (the API redirects to the provider); nothing about the transaction,
// the state, the nonce or the verifier is ever in frontend state (24 §24.3).

export type ProviderSummary = {
  readonly providerId: string;
  readonly label: string;
  /** "PRODUCTION_PROVIDER" or "TEST_PROVIDER" (24 §27): shown, never hidden. */
  readonly proofClass: string;
};

export type ProviderListResult = { readonly kind: "ok"; readonly providers: readonly ProviderSummary[] };

function parseProviderSummary(value: unknown): ProviderSummary {
  if (!isRecord(value)) {
    throw new TypeError("provider summary is malformed");
  }
  return {
    providerId: requireString(value, "providerId"),
    label: requireString(value, "label"),
    proofClass: requireString(value, "proofClass"),
  };
}

export async function listProviders(fetchImpl: typeof fetch = fetch): Promise<ProviderListResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/providers`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  const body = requireKind(await response.json());
  if (body.kind === "ok" && Array.isArray(body.providers)) {
    return { kind: "ok", providers: body.providers.map(parseProviderSummary) };
  }
  throw new TypeError(`unrecognized provider list response ${JSON.stringify(body.kind)}`);
}

/** The API contact a provider login starts at. `next` is a candidate the server validates. */
export function providerStartUrl(providerId: string, next: string): string {
  const query = new URLSearchParams({ next });
  return `${apiBaseUrl()}/auth/oidc/${encodeURIComponent(providerId)}/start?${query.toString()}`;
}

/** 24 §24.6: the safe projections the callback may send the browser back with. */
export const AUTH_PROJECTIONS = {
  cancelled: "You cancelled the provider login.",
  provider_unavailable: "The identity provider is unavailable right now. Please try again later.",
  provider_error: "The identity provider reported an error.",
  failed: "The provider login could not be completed.",
  unavailable: "Signing in with this provider is not available for this account.",
} as const;

export function authProjectionMessage(code: string | null): string | null {
  if (code === null) {
    return null;
  }
  return Object.prototype.hasOwnProperty.call(AUTH_PROJECTIONS, code)
    ? AUTH_PROJECTIONS[code as keyof typeof AUTH_PROJECTIONS]
    : AUTH_PROJECTIONS.failed;
}

// --- WU-AUTH-10 (24 §14.2, §23.2, §24.5): own authentication methods, linking

export type MethodSummary = {
  readonly methodId: string;
  readonly methodType: string;
  readonly status: string;
  readonly createdAt: string;
  readonly lastAuthenticatedAt: string | null;
  /** The provider attribute of a provider method; null for a local password. */
  readonly provider: { readonly providerId: string; readonly email: string | null } | null;
};

export type MethodListResult =
  | { readonly kind: "ok"; readonly methods: readonly MethodSummary[] }
  | { readonly kind: "denied"; readonly reasonCode: string };

function parseMethodSummary(value: unknown): MethodSummary {
  if (!isRecord(value)) {
    throw new TypeError("method summary is malformed");
  }
  if (value.lastAuthenticatedAt !== null && typeof value.lastAuthenticatedAt !== "string") {
    throw new TypeError("method summary has a malformed 'lastAuthenticatedAt'");
  }
  let provider: MethodSummary["provider"] = null;
  if (value.provider !== null) {
    if (!isRecord(value.provider) || (value.provider.email !== null && typeof value.provider.email !== "string")) {
      throw new TypeError("method summary has a malformed 'provider'");
    }
    provider = { providerId: requireString(value.provider, "providerId"), email: value.provider.email };
  }
  return {
    methodId: requireString(value, "methodId"),
    methodType: requireString(value, "methodType"),
    status: requireString(value, "status"),
    createdAt: requireString(value, "createdAt"),
    lastAuthenticatedAt: value.lastAuthenticatedAt,
    provider,
  };
}

export async function listMethods(fetchImpl: typeof fetch = fetch): Promise<MethodListResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/methods`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  const body = requireKind(await response.json());
  if (body.kind === "denied") {
    return { kind: "denied", reasonCode: requireString(body, "reasonCode") };
  }
  if (body.kind === "ok" && Array.isArray(body.methods)) {
    return { kind: "ok", methods: body.methods.map(parseMethodSummary) };
  }
  throw new TypeError(`unrecognized method list response ${JSON.stringify(body.kind)}`);
}

/**
 * The API contact that starts linking a provider to the current identity. It
 * is a POST the browser navigates to (a form submit), because the API answers
 * with a redirect to the provider; a `fetch` could not follow it.
 */
export function linkStartUrl(providerId: string, next: string): string {
  const query = new URLSearchParams({ next });
  return `${apiBaseUrl()}/auth/oidc/${encodeURIComponent(providerId)}/link/start?${query.toString()}`;
}

/** 24 §24.6: the safe projections the link callback may send the browser back with. */
export const LINK_PROJECTIONS = {
  ok: "The provider was linked to your account.",
  already_linked: "That provider identity was already linked to your account.",
  collision: "That provider identity is linked to another account. Nothing was changed.",
  cancelled: "You cancelled the provider link.",
  failed: "The provider could not be linked.",
} as const;

export function linkProjectionMessage(code: string | null): string | null {
  if (code === null) {
    return null;
  }
  return Object.prototype.hasOwnProperty.call(LINK_PROJECTIONS, code)
    ? LINK_PROJECTIONS[code as keyof typeof LINK_PROJECTIONS]
    : LINK_PROJECTIONS.failed;
}

// --- WU-AUTH-11 (24 §16.1, §24.5): email verification ------------------------

export type VerifiedEmailSummary = { readonly email: string; readonly verifiedAt: string; readonly active: boolean };

export type VerifiedEmailListResult =
  | { readonly kind: "ok"; readonly emails: readonly VerifiedEmailSummary[] }
  | { readonly kind: "denied"; readonly reasonCode: string };

export type VerificationStartResult =
  | { readonly kind: "ok"; readonly challengeId: string; readonly expiresAt: string }
  | { readonly kind: "denied"; readonly reasonCode: string }
  | { readonly kind: "rejected"; readonly reasonCode: string }
  | { readonly kind: "unavailable"; readonly reasonCode: string };

export type VerificationCompleteResult =
  | { readonly kind: "ok"; readonly email: string }
  | { readonly kind: "denied"; readonly reasonCode: string }
  | { readonly kind: "rejected"; readonly reasonCode: string }
  | { readonly kind: "unavailable"; readonly reasonCode: string };

function parseVerifiedEmail(value: unknown): VerifiedEmailSummary {
  if (!isRecord(value) || typeof value.active !== "boolean") {
    throw new TypeError("verified email summary is malformed");
  }
  return { email: requireString(value, "email"), verifiedAt: requireString(value, "verifiedAt"), active: value.active };
}

function parseReasonKind(body: Record<string, unknown> & { kind: string }) {
  if (body.kind === "denied" || body.kind === "rejected" || body.kind === "unavailable") {
    return { kind: body.kind, reasonCode: requireString(body, "reasonCode") } as const;
  }
  return null;
}

export async function listVerifiedEmails(fetchImpl: typeof fetch = fetch): Promise<VerifiedEmailListResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/emails`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  const body = requireKind(await response.json());
  if (body.kind === "denied") {
    return { kind: "denied", reasonCode: requireString(body, "reasonCode") };
  }
  if (body.kind === "ok" && Array.isArray(body.emails)) {
    return { kind: "ok", emails: body.emails.map(parseVerifiedEmail) };
  }
  throw new TypeError(`unrecognized verified email list response ${JSON.stringify(body.kind)}`);
}

export async function startEmailVerification(
  email: string,
  fetchImpl: typeof fetch = fetch,
): Promise<VerificationStartResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/email/verification/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    credentials: "include",
    body: JSON.stringify({ email }),
  });
  const body = requireKind(await response.json());
  const other = parseReasonKind(body);
  if (other) {
    return other;
  }
  if (body.kind === "ok") {
    return { kind: "ok", challengeId: requireString(body, "challengeId"), expiresAt: requireString(body, "expiresAt") };
  }
  throw new TypeError(`unrecognized verification start response ${JSON.stringify(body.kind)}`);
}

export async function completeEmailVerification(
  challengeId: string,
  token: string,
  fetchImpl: typeof fetch = fetch,
): Promise<VerificationCompleteResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/email/verification/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    credentials: "include",
    body: JSON.stringify({ challengeId, token }),
  });
  const body = requireKind(await response.json());
  const other = parseReasonKind(body);
  if (other) {
    return other;
  }
  if (body.kind === "ok") {
    return { kind: "ok", email: requireString(body, "email") };
  }
  throw new TypeError(`unrecognized verification complete response ${JSON.stringify(body.kind)}`);
}
