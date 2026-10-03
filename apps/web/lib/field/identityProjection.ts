/**
 * AUTH/CYAN-IDENTITY-01: the human's current authentication relation, derived ONLY from the typed PURPLE read truth
 * of AUTH/CYAN-01 (`/auth/me`, `/auth/sessions`, `/auth/methods`, `/auth/providers`). Pure: no React, no fetch.
 *
 *   AUTHENTICATED PRINCIPAL (/auth/me ok)                 → identity.authenticated(userId)      else: everything none
 *   → CURRENT SESSION  (exactly one session.current)      → session.current(...)                else: none
 *   → AUTHENTICATION METHOD (exactly one ACTIVE method of the current session's methodType)
 *                                                         → authentication.via(...)             else: none
 *   → PROVIDER TRUTH (providers list joined on providerId) → provider label, or null (raw id)   never invented
 *
 * Laws: IDENTITY != ROLE · AUTHENTICATION != AUTHORIZATION · AUTH_METHOD != ACCESS_RIGHT · PROVIDER_EMAIL !=
 * CANONICAL_IDENTITY · SESSION != AUTHORITY · UNKNOWN != INFERRED · GOOGLE_OIDC != GOOGLE_AUTHORITY. Nothing here
 * reads a role, a membership, a capability or an authority; nothing is inferred from timestamps, array order or an
 * email domain. The human-facing NQUIRY display name is NOT_MATERIALIZED: no producer provides it.
 */
import type {
  AuthMethodStatus,
  AuthMethodType,
  CurrentSessionResult,
  MethodListResult,
  MethodSummary,
  ProviderListResult,
  SessionListResult,
} from "../api/authClient";

/** Each read as the typed client returned it, or null when the read threw (malformed, non-JSON, network). */
export type IdentityReads = {
  readonly me: CurrentSessionResult | null;
  readonly sessions: SessionListResult | null;
  readonly methods: MethodListResult | null;
  readonly providers: ProviderListResult | null;
};

export type AuthenticationLabel =
  | { readonly kind: "local" }
  | { readonly kind: "provider"; readonly providerId: string; readonly label: string | null };

export type IdentityProjection = {
  readonly identity: { readonly kind: "none" } | { readonly kind: "authenticated"; readonly userId: string };
  readonly session:
    | { readonly kind: "none" }
    | { readonly kind: "current"; readonly sessionId: string; readonly issuedAt: string; readonly expiresAt: string; readonly methodType: AuthMethodType | null };
  readonly authentication:
    | { readonly kind: "none" }
    | { readonly kind: "via"; readonly methodType: AuthMethodType; readonly status: AuthMethodStatus; readonly lastAuthenticatedAt: string | null; readonly label: AuthenticationLabel };
  /** A provider-method attribute, never the canonical NQUIRY identity. */
  readonly providerAccount: { readonly kind: "none" } | { readonly kind: "email"; readonly providerId: string; readonly email: string };
};

export const NO_IDENTITY_PROJECTION: IdentityProjection = {
  identity: { kind: "none" },
  session: { kind: "none" },
  authentication: { kind: "none" },
  providerAccount: { kind: "none" },
};

/** The one legitimate local-password label (the closed vocabulary's own word, not a provider). */
export const LOCAL_PASSWORD_LABEL = "Local password";

/** The method the current session was produced by: exactly one ACTIVE method of that type, else none. */
function methodOfSession(methods: readonly MethodSummary[], methodType: AuthMethodType): MethodSummary | null {
  const active = methods.filter((m) => m.methodType === methodType && m.status === "ACTIVE");
  return active.length === 1 ? active[0] : null;
}

export function identityProjectionFrom(reads: IdentityReads): IdentityProjection {
  if (reads.me === null || reads.me.kind !== "ok") return NO_IDENTITY_PROJECTION;
  const identity = { kind: "authenticated", userId: reads.me.userId } as const;

  const currents = reads.sessions !== null && reads.sessions.kind === "ok" ? reads.sessions.sessions.filter((s) => s.current) : [];
  const session: IdentityProjection["session"] =
    currents.length === 1
      ? { kind: "current", sessionId: currents[0].sessionId, issuedAt: currents[0].issuedAt, expiresAt: currents[0].expiresAt, methodType: currents[0].methodType }
      : { kind: "none" };

  let authentication: IdentityProjection["authentication"] = { kind: "none" };
  let providerAccount: IdentityProjection["providerAccount"] = { kind: "none" };
  if (session.kind === "current" && session.methodType !== null && reads.methods !== null && reads.methods.kind === "ok") {
    const method = methodOfSession(reads.methods.methods, session.methodType);
    if (method !== null) {
      if (method.methodType === "LOCAL_PASSWORD") {
        if (method.provider === null) {
          authentication = { kind: "via", methodType: method.methodType, status: method.status, lastAuthenticatedAt: method.lastAuthenticatedAt, label: { kind: "local" } };
        }
      } else if (method.provider !== null) {
        const providerId = method.provider.providerId;
        const known = reads.providers !== null && reads.providers.kind === "ok" ? reads.providers.providers.find((p) => p.providerId === providerId) : undefined;
        authentication = {
          kind: "via",
          methodType: method.methodType,
          status: method.status,
          lastAuthenticatedAt: method.lastAuthenticatedAt,
          label: { kind: "provider", providerId, label: known ? known.label : null },
        };
        if (method.provider.email !== null) providerAccount = { kind: "email", providerId, email: method.provider.email };
      }
    }
  }
  return { identity, session, authentication, providerAccount };
}

/** The words for the "Current authentication" line: the local label, the server-owned provider label, or the raw provider id. */
export function authenticationWords(label: AuthenticationLabel): string {
  return label.kind === "local" ? LOCAL_PASSWORD_LABEL : (label.label ?? label.providerId);
}
