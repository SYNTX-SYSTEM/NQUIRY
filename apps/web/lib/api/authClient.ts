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

// ===========================================================================
// AUTH/CYAN-01 — typed, fail-closed consumption of the live PURPLE AUTH contract.
//
// PRODUCER (reconstructed read-only, never modified here): branch `auth-identity`
// @ aa32c4d4faad23eea0bd3290641e7a66adcf26a9; the live assembly
// `auth-aa32c4d-20261001T081014Z` serves byte-identical contract files
// (`packages/application/http_oidc.py` 95d6d48a…, `http_dispatch.py`,
// `http_revocation.py`, `packages/security/redirect_target.py` adb6c182…,
// `packages/security/auth_methods.py`). The vocabularies below are copied from
// those serializers: PROVIDER_OUTPUT != CYAN_INFERENCE, nothing is widened.
//
// LAWS of this section:
//   AUTHENTICATION != AUTHORIZATION — a parsed principal, method or session is
//     never a permission, a role or an authority (nothing here reads a role).
//   LOGIN != LINK — `/auth/oidc/{p}/start` (LOGIN, unauthenticated, ends at
//     `/login?auth=`) and `/auth/oidc/{p}/link/start` (ACCOUNT_LINK, session
//     required, ends at the bound local target with `?link=`) are distinct
//     builders with distinct projection vocabularies.
//   LINK != ACCOUNT_CREATION — a `link=ok` projection is a linked method on the
//     CURRENT identity; no account is created by this module or that route.
//   GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN — a provider in the parsed list is
//     a configured contact, never a proven callback.
//   UNKNOWN != OK, DENIED != OK — every unknown kind, key, enum value,
//     proofClass, reason code or projection word fails closed
//     (`MalformedAuthResponse` / `unknown`), never to success.
//   Provider availability comes ONLY from the parsed `/auth/providers`
//     response: a `ProviderSummary` carries a module-private brand, so no
//     caller can hand-build one and no builder accepts a bare provider id.
// ===========================================================================

export const AUTH_CONTRACT_PRODUCER = {
  field: "PURPLE_AUTH",
  branch: "auth-identity",
  // WU-AUTH-19/20 + WU-AUTHZ-01 (credential rotation, login lockout, roster administration) on top of HD-AUTH-08;
  // every earlier shape is unchanged — see PURPLE `docs/implementation/field-reports/AUTH/CONSUMER_CONTRACT.md`.
  // `liveAssembly` names what production serves while this consumer is staged.
  commit: "50ccdb0c9167d81773102dc33ff38eed44d321e2",
  liveAssembly: "auth-e069fc1-20261004T140533Z",
} as const;

/** `oidc_provider.proof_class` (24 §27): closed; shown, never hidden, never upgraded. */
export const PROOF_CLASSES = ["PRODUCTION_PROVIDER", "TEST_PROVIDER"] as const;
export type ProofClass = (typeof PROOF_CLASSES)[number];

/** `security/auth_methods.py` (24 §9.1: THE VOCABULARY IS CLOSED). */
export const AUTH_METHOD_TYPES = ["LOCAL_PASSWORD", "GOOGLE_OIDC", "TEST_PROVIDER"] as const;
export type AuthMethodType = (typeof AUTH_METHOD_TYPES)[number];
export const AUTH_METHOD_STATUSES = ["ACTIVE", "REVOKED"] as const;
export type AuthMethodStatus = (typeof AUTH_METHOD_STATUSES)[number];

/** `/login?auth=<projection>` (http_oidc `_login_projection`, `_protocol_steps`). */
export const AUTH_PROJECTIONS = ["cancelled", "provider_unavailable", "provider_error", "failed", "unavailable"] as const;
export type AuthProjection = (typeof AUTH_PROJECTIONS)[number];
/** `<target>?link=<projection>` (http_oidc `_link_projection`, `_link_location`). */
export const LINK_PROJECTIONS = ["ok", "already_linked", "collision", "cancelled", "failed"] as const;
export type LinkProjection = (typeof LINK_PROJECTIONS)[number];

/** Reason codes per contact, exactly as the PURPLE dispatchers emit them. */
export const SESSION_DENIED_REASONS = ["NO_SESSION"] as const;
export const IDENTITY_DENIED_REASONS = ["NO_SESSION"] as const;
export const REVOKE_DENIED_REASONS = ["NO_SESSION", "SESSION_NOT_FOUND"] as const;
export const REVOKE_REJECTED_REASONS = ["MALFORMED_SESSION_ID"] as const;
export const UNLINK_DENIED_REASONS = ["NO_SESSION", "UNLINK_DENIED", "LAST_METHOD"] as const;
export const UNLINK_REJECTED_REASONS = ["MALFORMED_METHOD_ID"] as const;

/**
 * Keys that never belong in a browser-visible AUTH body (24 §24.3: "never a
 * token or a token hash", "never a secret or a subject"). Their presence is a
 * contract violation and fails closed before any field is read.
 */
export const AUTH_FORBIDDEN_KEYS = [
  "sessionToken",
  "session_token",
  "token",
  "tokenHash",
  "token_hash",
  "state",
  "nonce",
  "codeVerifier",
  "code_verifier",
  "codeChallenge",
  "clientSecret",
  "client_secret",
  "password",
  "passwordHash",
  "subject",
  "sub",
  "idToken",
  "id_token",
  "accessToken",
  "access_token",
  "refreshToken",
  "refresh_token",
] as const;

export class MalformedAuthResponse extends TypeError {
  readonly path: string;
  readonly detail: string;
  constructor(path: string, detail: string) {
    super(`malformed AUTH response at ${path}: ${detail}`);
    this.name = "MalformedAuthResponse";
    this.path = path;
    this.detail = detail;
  }
}

/** The redirect-target candidate is not a legitimate local destination (fail closed, nothing is sent). */
export class UnsafeNextTarget extends TypeError {
  constructor() {
    // Carries no part of the candidate: the rejected value is not echoed anywhere.
    super("next target rejected: not a legitimate local destination");
    this.name = "UnsafeNextTarget";
  }
}

const AUTH_FORBIDDEN = new Set<string>(AUTH_FORBIDDEN_KEYS);
const PARSED = Symbol("authClient.parsed");
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

function failAuth(path: string, detail: string): never {
  throw new MalformedAuthResponse(path, detail);
}
function authRecord(value: unknown, path: string): Record<string, unknown> {
  if (!isRecord(value) || Array.isArray(value)) failAuth(path, "expected an object");
  return value;
}
function authExactKeys(rec: Record<string, unknown>, path: string, expected: readonly string[]): void {
  for (const key of Object.keys(rec)) {
    if (AUTH_FORBIDDEN.has(key)) failAuth(`${path}.${key}`, "forbidden key present (a secret, token or subject never reaches the browser)");
    if (!expected.includes(key)) failAuth(`${path}.${key}`, "unexpected key (unknown fields never become auth truth)");
  }
  for (const key of expected) {
    if (!(key in rec)) failAuth(`${path}.${key}`, "required key absent");
  }
}
function authStr(rec: Record<string, unknown>, key: string, path: string): string {
  const v = rec[key];
  if (typeof v !== "string") failAuth(`${path}.${key}`, `expected string, got ${JSON.stringify(v)}`);
  return v;
}
function authClosed<T extends string>(rec: Record<string, unknown>, key: string, path: string, allowed: readonly T[]): T {
  const v = authStr(rec, key, path);
  if (!(allowed as readonly string[]).includes(v)) failAuth(`${path}.${key}`, `value outside the closed vocabulary: ${JSON.stringify(v)}`);
  return v as T;
}
function authBool(rec: Record<string, unknown>, key: string, path: string): boolean {
  const v = rec[key];
  if (typeof v !== "boolean") failAuth(`${path}.${key}`, `expected boolean, got ${JSON.stringify(v)}`);
  return v;
}
function authCount(rec: Record<string, unknown>, key: string, path: string): number {
  const v = rec[key];
  if (typeof v !== "number" || !Number.isInteger(v) || v < 0) failAuth(`${path}.${key}`, `expected a non-negative integer, got ${JSON.stringify(v)}`);
  return v;
}
function authInstant(rec: Record<string, unknown>, key: string, path: string): string {
  const v = authStr(rec, key, path);
  if (Number.isNaN(Date.parse(v))) failAuth(`${path}.${key}`, "expected an ISO-8601 instant");
  return v;
}
function authInstantOrNull(rec: Record<string, unknown>, key: string, path: string): string | null {
  if (rec[key] === null) return null;
  return authInstant(rec, key, path);
}
function authId(rec: Record<string, unknown>, key: string, path: string): string {
  const v = authStr(rec, key, path);
  if (!UUID.test(v)) failAuth(`${path}.${key}`, "expected a UUID");
  return v;
}
function authList(rec: Record<string, unknown>, key: string, path: string): readonly unknown[] {
  const v = rec[key];
  if (!Array.isArray(v)) failAuth(`${path}.${key}`, "expected an array");
  return v;
}
function authKind(body: unknown, path: string): Record<string, unknown> & { kind: string } {
  const rec = authRecord(body, path);
  for (const key of Object.keys(rec)) {
    if (AUTH_FORBIDDEN.has(key)) failAuth(`${path}.${key}`, "forbidden key present (a secret, token or subject never reaches the browser)");
  }
  if (typeof rec.kind !== "string") failAuth(`${path}.kind`, "missing or non-string kind");
  return rec as Record<string, unknown> & { kind: string };
}
function reasonBody<K extends string, R extends string>(
  body: Record<string, unknown> & { kind: string },
  path: string,
  kind: K,
  reasons: readonly R[],
): { readonly kind: K; readonly reasonCode: R } {
  authExactKeys(body, path, ["kind", "reasonCode"]);
  return { kind, reasonCode: authClosed(body, "reasonCode", path, reasons) };
}
async function authBody(response: Response, path: string): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    failAuth(path, "response body is not JSON");
  }
}

// --- providers ---------------------------------------------------------------

/**
 * One configured provider contact as the server reports it. The `PARSED` brand
 * is module-private: a `ProviderSummary` exists only as the output of
 * `parseProviderList`, which is how "availability comes only from the parsed
 * provider response" is enforced at the type level.
 */
export type ProviderSummary = {
  readonly providerId: string;
  readonly label: string;
  readonly proofClass: ProofClass;
  readonly [PARSED]: true;
};
export type ProviderListResult = { readonly kind: "ok"; readonly providers: readonly ProviderSummary[] };

const PROVIDER_KEYS = ["providerId", "label", "proofClass"] as const;

function parseProviderSummary(value: unknown, path: string): ProviderSummary {
  const rec = authRecord(value, path);
  authExactKeys(rec, path, PROVIDER_KEYS);
  const providerId = authStr(rec, "providerId", path);
  if (providerId.length === 0) failAuth(`${path}.providerId`, "empty provider id");
  return {
    providerId,
    label: authStr(rec, "label", path),
    proofClass: authClosed(rec, "proofClass", path, PROOF_CLASSES),
    [PARSED]: true,
  };
}

/** `GET /auth/providers` → `{"kind":"ok","providers":[…]}`; any other kind fails closed. */
export function parseProviderList(body: unknown): ProviderListResult {
  const path = "providers";
  const rec = authKind(body, path);
  if (rec.kind !== "ok") failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)} (the provider list has one shape)`);
  authExactKeys(rec, path, ["kind", "providers"]);
  const providers = authList(rec, "providers", path).map((item, i) => parseProviderSummary(item, `${path}.providers[${i}]`));
  const ids = new Set<string>();
  for (const provider of providers) {
    if (ids.has(provider.providerId)) failAuth(path, `duplicate provider id ${JSON.stringify(provider.providerId)}`);
    ids.add(provider.providerId);
  }
  return { kind: "ok", providers };
}

export async function listProviders(fetchImpl: typeof fetch = fetch): Promise<ProviderListResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/providers`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  return parseProviderList(await authBody(response, "providers"));
}

/** The parsed provider with this id, or null. The only source of availability. */
export function availableProvider(list: ProviderListResult, providerId: string): ProviderSummary | null {
  return list.providers.find((provider) => provider.providerId === providerId) ?? null;
}

// --- next target (security/redirect_target.py, mirrored exactly) -------------

export const MAX_NEXT_TARGET_LENGTH = 1024;
// One leading slash; the next character is printable ASCII but neither "/" nor
// "\\" (no scheme-relative form); the rest is printable ASCII without space or
// backslash. Query and fragment are allowed (they stay local).
const LOCAL_DESTINATION = /^\/(?:[!-.0-9:-[\]-~][!-[\]-~]*)?$/;
// A percent-encoded control character (%00-%1F, %7F) is refused as well.
const ENCODED_CONTROL = /%(?:[01][0-9A-Fa-f]|7[Ff])/;

/** PURPLE's `is_legitimate_local_destination`: a path of this application, nothing else. */
export function isLocalNextTarget(candidate: unknown): candidate is string {
  if (typeof candidate !== "string" || candidate.length === 0) return false;
  if (candidate.length > MAX_NEXT_TARGET_LENGTH) return false;
  if (!LOCAL_DESTINATION.test(candidate)) return false;
  return !ENCODED_CONTROL.test(candidate);
}

function requireLocalNext(candidate: unknown): string {
  if (!isLocalNextTarget(candidate)) throw new UnsafeNextTarget();
  return candidate;
}

// --- LOGIN start / LINK start builders ----------------------------------------

/**
 * `GET /auth/oidc/{provider}/start?next=` — a top-level navigation (the API
 * answers 303 to the provider; a fetch could not follow it). The provider must
 * be a parsed `ProviderSummary`; `next` must be a legitimate local destination
 * or the builder refuses (CYAN refuses where PURPLE would silently fall back
 * to "/": nothing unsafe is ever sent). A login's non-success ends at
 * `/login?auth=<AuthProjection>`.
 */
export function loginStartUrl(provider: ProviderSummary, next: string): string {
  const query = new URLSearchParams({ next: requireLocalNext(next) });
  return `${apiBaseUrl()}/auth/oidc/${encodeURIComponent(provider.providerId)}/start?${query.toString()}`;
}

export type GoogleLoginStart =
  | { readonly kind: "available"; readonly provider: ProviderSummary; readonly url: string }
  | { readonly kind: "unavailable" };

/**
 * The Google login start URL, if and only if the PARSED provider list names
 * `google`. No hard-coded availability: without the parsed entry there is no
 * URL. GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN.
 */
export function googleLoginStart(list: ProviderListResult, next: string): GoogleLoginStart {
  const provider = availableProvider(list, "google");
  if (provider === null) return { kind: "unavailable" };
  return { kind: "available", provider, url: loginStartUrl(provider, next) };
}

export type LinkStartAction = { readonly method: "POST"; readonly action: string };

/**
 * `POST /auth/oidc/{provider}/link/start?next=` — ACCOUNT_LINK for the CURRENT
 * authenticated identity (401 NO_SESSION otherwise; 503 PROVIDER_NOT_CONFIGURED
 * for an unknown provider). A form the browser submits, because the API
 * answers with a redirect to the provider. The outcome returns to `next` with
 * `?link=<LinkProjection>`. LINK != LOGIN and LINK != ACCOUNT_CREATION.
 * `next` is mandatory here: CYAN has no `/account/security` route to default to.
 */
export function linkStartAction(provider: ProviderSummary, next: string): LinkStartAction {
  const query = new URLSearchParams({ next: requireLocalNext(next) });
  return {
    method: "POST",
    action: `${apiBaseUrl()}/auth/oidc/${encodeURIComponent(provider.providerId)}/link/start?${query.toString()}`,
  };
}

// --- projections (vocabulary only: NOT PRESENTED, no words) --------------------

export type ProjectionReading<P extends string> =
  | { readonly kind: "none" }
  | { readonly kind: "projection"; readonly projection: P }
  | { readonly kind: "unknown" };

function readProjection<P extends string>(search: string | URLSearchParams, key: string, allowed: readonly P[]): ProjectionReading<P> {
  const params = typeof search === "string" ? new URLSearchParams(search) : search;
  const values = params.getAll(key);
  if (values.length === 0) return { kind: "none" };
  if (values.length !== 1) return { kind: "unknown" };
  const value = values[0];
  return (allowed as readonly string[]).includes(value) ? { kind: "projection", projection: value as P } : { kind: "unknown" };
}

/** `?auth=` on `/login`: a known word, none, or `unknown` (never mapped to `failed`). */
export function readAuthProjection(search: string | URLSearchParams): ProjectionReading<AuthProjection> {
  return readProjection(search, "auth", AUTH_PROJECTIONS);
}
/** `?link=` on the bound local target: a known word, none, or `unknown` (never mapped to `ok` or `failed`). */
export function readLinkProjection(search: string | URLSearchParams): ProjectionReading<LinkProjection> {
  return readProjection(search, "link", LINK_PROJECTIONS);
}

// --- methods (`GET /auth/methods`) ------------------------------------------------

export type MethodSummary = {
  readonly methodId: string;
  readonly methodType: AuthMethodType;
  readonly status: AuthMethodStatus;
  readonly createdAt: string;
  readonly lastAuthenticatedAt: string | null;
  /** The provider attribute of a provider method; null for a local password. */
  readonly provider: { readonly providerId: string; readonly email: string | null } | null;
};
export type MethodListResult =
  | { readonly kind: "ok"; readonly methods: readonly MethodSummary[] }
  | { readonly kind: "denied"; readonly reasonCode: (typeof SESSION_DENIED_REASONS)[number] };

const METHOD_KEYS = ["methodId", "methodType", "status", "createdAt", "lastAuthenticatedAt", "provider"] as const;
const METHOD_PROVIDER_KEYS = ["providerId", "email"] as const;

function parseMethodSummary(value: unknown, path: string): MethodSummary {
  const rec = authRecord(value, path);
  authExactKeys(rec, path, METHOD_KEYS);
  let provider: MethodSummary["provider"] = null;
  if (rec.provider !== null) {
    const p = authRecord(rec.provider, `${path}.provider`);
    authExactKeys(p, `${path}.provider`, METHOD_PROVIDER_KEYS);
    const email = p.email === null ? null : authStr(p, "email", `${path}.provider`);
    provider = { providerId: authStr(p, "providerId", `${path}.provider`), email };
  }
  return {
    methodId: authId(rec, "methodId", path),
    methodType: authClosed(rec, "methodType", path, AUTH_METHOD_TYPES),
    status: authClosed(rec, "status", path, AUTH_METHOD_STATUSES),
    createdAt: authInstant(rec, "createdAt", path),
    lastAuthenticatedAt: authInstantOrNull(rec, "lastAuthenticatedAt", path),
    provider,
  };
}

export function parseMethodList(body: unknown): MethodListResult {
  const path = "methods";
  const rec = authKind(body, path);
  switch (rec.kind) {
    case "ok": {
      authExactKeys(rec, path, ["kind", "methods"]);
      return { kind: "ok", methods: authList(rec, "methods", path).map((item, i) => parseMethodSummary(item, `${path}.methods[${i}]`)) };
    }
    case "denied":
      return reasonBody(rec, path, "denied", SESSION_DENIED_REASONS);
    default:
      failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)}`);
  }
}

export async function listMethods(fetchImpl: typeof fetch = fetch): Promise<MethodListResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/methods`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  return parseMethodList(await authBody(response, "methods"));
}

// --- sessions (`GET /auth/sessions`, revoke, logout-all) ---------------------------

export type SessionSummary = {
  readonly sessionId: string;
  readonly issuedAt: string;
  readonly expiresAt: string;
  readonly current: boolean;
  /** The authentication method type, or null for a session no method produced. */
  readonly methodType: AuthMethodType | null;
};
export type SessionListResult =
  | { readonly kind: "ok"; readonly sessions: readonly SessionSummary[] }
  | { readonly kind: "denied"; readonly reasonCode: (typeof SESSION_DENIED_REASONS)[number] };
export type SessionRevokeResult =
  | { readonly kind: "ok" }
  | { readonly kind: "denied"; readonly reasonCode: (typeof REVOKE_DENIED_REASONS)[number] }
  | { readonly kind: "rejected"; readonly reasonCode: (typeof REVOKE_REJECTED_REASONS)[number] };
export type LogoutAllResult =
  | { readonly kind: "ok"; readonly revokedSessions: number }
  | { readonly kind: "denied"; readonly reasonCode: (typeof SESSION_DENIED_REASONS)[number] };

const SESSION_KEYS = ["sessionId", "issuedAt", "expiresAt", "current", "methodType"] as const;

function parseSessionSummary(value: unknown, path: string): SessionSummary {
  const rec = authRecord(value, path);
  authExactKeys(rec, path, SESSION_KEYS);
  return {
    sessionId: authId(rec, "sessionId", path),
    issuedAt: authInstant(rec, "issuedAt", path),
    expiresAt: authInstant(rec, "expiresAt", path),
    current: authBool(rec, "current", path),
    methodType: rec.methodType === null ? null : authClosed(rec, "methodType", path, AUTH_METHOD_TYPES),
  };
}

export function parseSessionList(body: unknown): SessionListResult {
  const path = "sessions";
  const rec = authKind(body, path);
  switch (rec.kind) {
    case "ok": {
      authExactKeys(rec, path, ["kind", "sessions"]);
      const sessions = authList(rec, "sessions", path).map((item, i) => parseSessionSummary(item, `${path}.sessions[${i}]`));
      if (sessions.filter((s) => s.current).length > 1) failAuth(path, "more than one session claims to be current");
      return { kind: "ok", sessions };
    }
    case "denied":
      return reasonBody(rec, path, "denied", SESSION_DENIED_REASONS);
    default:
      failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)}`);
  }
}

export function parseSessionRevoke(body: unknown): SessionRevokeResult {
  const path = "revoke";
  const rec = authKind(body, path);
  switch (rec.kind) {
    case "ok":
      authExactKeys(rec, path, ["kind"]);
      return { kind: "ok" };
    case "denied":
      return reasonBody(rec, path, "denied", REVOKE_DENIED_REASONS);
    case "rejected":
      return reasonBody(rec, path, "rejected", REVOKE_REJECTED_REASONS);
    default:
      failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)}`);
  }
}

export function parseLogoutAll(body: unknown): LogoutAllResult {
  const path = "logoutAll";
  const rec = authKind(body, path);
  switch (rec.kind) {
    case "ok":
      authExactKeys(rec, path, ["kind", "revokedSessions"]);
      return { kind: "ok", revokedSessions: authCount(rec, "revokedSessions", path) };
    case "denied":
      return reasonBody(rec, path, "denied", SESSION_DENIED_REASONS);
    default:
      failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)}`);
  }
}

export async function listSessions(fetchImpl: typeof fetch = fetch): Promise<SessionListResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/sessions`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  return parseSessionList(await authBody(response, "sessions"));
}

/** `POST /auth/sessions/{sessionId}/revoke`: the caller's OWN session only (the server decides). */
export async function revokeSession(sessionId: string, fetchImpl: typeof fetch = fetch): Promise<SessionRevokeResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/sessions/${encodeURIComponent(sessionId)}/revoke`, {
    method: "POST",
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  return parseSessionRevoke(await authBody(response, "revoke"));
}

/** `POST /auth/logout-all` (24 §15.7): every session of the caller's identity; the cookie is cleared by the server. */
export async function logoutAll(fetchImpl: typeof fetch = fetch): Promise<LogoutAllResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/logout-all`, {
    method: "POST",
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  return parseLogoutAll(await authBody(response, "logoutAll"));
}

// --- unlink (`POST /auth/methods/{methodId}/unlink`) --------------------------------

export type UnlinkResult =
  | { readonly kind: "ok"; readonly methodId: string; readonly sessionsRevoked: number; readonly currentSessionEnded: boolean }
  | { readonly kind: "denied"; readonly reasonCode: (typeof UNLINK_DENIED_REASONS)[number] }
  | { readonly kind: "rejected"; readonly reasonCode: (typeof UNLINK_REJECTED_REASONS)[number] };

export function parseUnlink(body: unknown): UnlinkResult {
  const path = "unlink";
  const rec = authKind(body, path);
  switch (rec.kind) {
    case "ok":
      authExactKeys(rec, path, ["kind", "methodId", "sessionsRevoked", "currentSessionEnded"]);
      return {
        kind: "ok",
        methodId: authId(rec, "methodId", path),
        sessionsRevoked: authCount(rec, "sessionsRevoked", path),
        currentSessionEnded: authBool(rec, "currentSessionEnded", path),
      };
    case "denied":
      return reasonBody(rec, path, "denied", UNLINK_DENIED_REASONS);
    case "rejected":
      return reasonBody(rec, path, "rejected", UNLINK_REJECTED_REASONS);
    default:
      failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)}`);
  }
}

export async function unlinkMethod(methodId: string, fetchImpl: typeof fetch = fetch): Promise<UnlinkResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/methods/${encodeURIComponent(methodId)}/unlink`, {
    method: "POST",
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  return parseUnlink(await authBody(response, "unlink"));
}

// --- credential rotation (`POST /auth/password/change`, WU-AUTH-19) ----------------------------------------------
//
// The authenticated identity replaces its OWN local password after proving the current one. ROTATION != RECOVERY
// (no e-mail, no challenge; a live session and the credential are the proof). `sessionsRevoked` = the OTHER
// sessions the server ended (the proving session continues). Closed denial / rejection vocabularies copied from
// `http_credential.py`; an unknown reason fails closed.

export const PASSWORD_CHANGE_DENIED_REASONS = ["NO_SESSION", "CURRENT_PASSWORD_INVALID", "NO_LOCAL_CREDENTIAL"] as const;
export const PASSWORD_CHANGE_REJECTED_REASONS = ["PASSWORD_INVALID"] as const;
export type PasswordChangeResult =
  | { readonly kind: "ok"; readonly sessionsRevoked: number }
  | { readonly kind: "denied"; readonly reasonCode: (typeof PASSWORD_CHANGE_DENIED_REASONS)[number] }
  | { readonly kind: "rejected"; readonly reasonCode: (typeof PASSWORD_CHANGE_REJECTED_REASONS)[number] };

export function parsePasswordChange(body: unknown): PasswordChangeResult {
  const path = "passwordChange";
  const rec = authKind(body, path);
  switch (rec.kind) {
    case "ok":
      authExactKeys(rec, path, ["kind", "sessionsRevoked"]);
      return { kind: "ok", sessionsRevoked: authCount(rec, "sessionsRevoked", path) };
    case "denied":
      return reasonBody(rec, path, "denied", PASSWORD_CHANGE_DENIED_REASONS);
    case "rejected":
      return reasonBody(rec, path, "rejected", PASSWORD_CHANGE_REJECTED_REASONS);
    default:
      failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)}`);
  }
}

export async function changePassword(currentPassword: string, newPassword: string, fetchImpl: typeof fetch = fetch): Promise<PasswordChangeResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/password/change`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    credentials: "include",
    body: JSON.stringify({ currentPassword, newPassword }),
  });
  return parsePasswordChange(await authBody(response, "passwordChange"));
}

// --- identity presentation (`GET /auth/identity`, PURPLE_IDENTITY_PRESENTATION_01 @ auth-identity 2ec05c0) -----------
//
// The authenticated self's human-facing NQUIRY identity: `{kind:"ok", userId, displayName, canonicalEmail}` — a
// function of the canonical identity row alone, i.e. of `userId`: identical across every session of ONE identity
// whatever its method, never derived at read time from a credential, a provider profile or an email local part.
// WHICH identity a provider login reaches is PURPLE's resolution, not a law of this read (CONSUMER_CONTRACT.md §1):
// a LINKED subject reaches the identity that linked it (GOOGLE_LINKED: the same presentation as its local login);
// an unbound subject under SELF_REGISTRATION_ALLOWED reaches its OWN bootstrapped identity (GOOGLE_BOOTSTRAP: a
// different userId whose name and canonical email were copied once from the provider's claims at creation).
// `/auth/me` stays the authentication VERDICT. NQUIRY_CANONICAL_EMAIL != PROVIDER_EMAIL (two relations, even when
// equal by value) · DISPLAY_NAME != PROVIDER_DISPLAY_NAME (even when a bootstrap copied it).
// `denied NO_SESSION` is the one class for a missing/expired/revoked session and for a principal without an identity row.

export type IdentityPresentation = { readonly userId: string; readonly displayName: string; readonly canonicalEmail: string };
export type IdentityPresentationResult =
  | ({ readonly kind: "ok" } & IdentityPresentation)
  | { readonly kind: "denied"; readonly reasonCode: (typeof IDENTITY_DENIED_REASONS)[number] };

function authNonEmpty(rec: Record<string, unknown>, key: string, path: string): string {
  const v = authStr(rec, key, path);
  if (v.trim().length === 0) failAuth(`${path}.${key}`, "empty value (nothing is defaulted or derived)");
  return v;
}

export function parseIdentityPresentation(body: unknown): IdentityPresentationResult {
  const path = "identity";
  const rec = authKind(body, path);
  switch (rec.kind) {
    case "ok":
      authExactKeys(rec, path, ["kind", "userId", "displayName", "canonicalEmail"]);
      return { kind: "ok", userId: authId(rec, "userId", path), displayName: authNonEmpty(rec, "displayName", path), canonicalEmail: authNonEmpty(rec, "canonicalEmail", path) };
    case "denied":
      return reasonBody(rec, path, "denied", IDENTITY_DENIED_REASONS);
    default:
      failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)}`);
  }
}

export async function fetchIdentityPresentation(fetchImpl: typeof fetch = fetch): Promise<IdentityPresentationResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/auth/identity`, {
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  return parseIdentityPresentation(await authBody(response, "identity"));
}
