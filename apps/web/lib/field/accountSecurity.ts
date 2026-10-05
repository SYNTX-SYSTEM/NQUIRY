/**
 * AUTH/CYAN-ACCOUNT-01: the account-security relations of the authenticated identity (24 §24.5 target UI contacts:
 * list methods · add a provider · remove a method · revoke sessions · sign out everywhere), derived ONLY from the same
 * typed PURPLE reads as the identity projection (`IdentityReads`) — ONE composition, no second fetch, no inference.
 * Pure: no React, no fetch, no mount (the link return target is handed in by the page).
 *
 *   ACTIVE methods (every ACTIVE entry of /auth/methods)   → methods[]: words, provider account, current, removable
 *   sessions (every entry of /auth/sessions)                → sessions[]: issued/expires, current, words
 *   providers (parsed) minus already-held provider methods  → link: the typed LINK start action, or none
 *
 * Laws (PURPLE CONSUMER_CONTRACT.md §3–4): a method is removable only while another ACTIVE method remains — the
 * server's own 24 §14.6 law (`409 LAST_METHOD`), mirrored as an affordance and never decided here; the current
 * session is ended through Log out, never through revoke; a provider that is already an ACTIVE method is not offered
 * again (the server answers `already_linked` anyway). LINK != LOGIN · LINK != ACCOUNT_CREATION · METHOD != ACCESS.
 * Nothing here reads or produces a role, a membership or a right of any kind.
 */
import { linkStartAction, type AuthMethodType, type LinkStartAction, type MethodSummary, type ProviderSummary } from "../api/authClient";
import { type AuthenticationLabel, authenticationWords, type IdentityReads } from "./identityProjection";

export type MethodRelation = {
  readonly methodId: string;
  readonly methodType: AuthMethodType;
  readonly label: AuthenticationLabel;
  readonly words: string;
  /** The provider-method attribute, never the identity. */
  readonly providerEmail: string | null;
  /** The server's own last-use fact of the method (24 §24.5 "last login evidence where safe"), or null. */
  readonly lastAuthenticatedAt: string | null;
  /** The method the current session was produced by (exactly one ACTIVE method of the session's type). */
  readonly current: boolean;
  /** 24 §14.6 mirrored: another ACTIVE method remains. The server decides; this only withholds a futile control. */
  readonly removable: boolean;
};

export type SessionRelation = {
  readonly sessionId: string;
  readonly issuedAt: string;
  readonly expiresAt: string;
  readonly current: boolean;
  readonly words: string | null;
};

/** A configured provider the identity holds no ACTIVE method for, with its typed LINK start action. */
export type LinkOffer = { readonly provider: ProviderSummary; readonly action: LinkStartAction };

export type AccountSecurity = {
  readonly methods: readonly MethodRelation[];
  readonly sessions: readonly SessionRelation[];
  readonly links: readonly LinkOffer[];
  /** WU-AUTH-19: the identity holds an ACTIVE local password it may rotate (the server proves the current one). */
  readonly rotatable: boolean;
};

export const NO_ACCOUNT_SECURITY: AccountSecurity = { methods: [], sessions: [], links: [], rotatable: false };

function labelOf(method: MethodSummary, reads: IdentityReads): AuthenticationLabel | null {
  if (method.methodType === "LOCAL_PASSWORD") return method.provider === null ? { kind: "local" } : null;
  if (method.provider === null) return null;
  const providerId = method.provider.providerId;
  const known = reads.providers !== null && reads.providers.kind === "ok" ? reads.providers.providers.find((p) => p.providerId === providerId) : undefined;
  return { kind: "provider", providerId, label: known ? known.label : null };
}

function methodWords(method: MethodSummary, reads: IdentityReads): string | null {
  const label = labelOf(method, reads);
  return label === null ? null : authenticationWords(label);
}

/**
 * The account-security relations for the reads, or the empty field when `/auth/me` is not `ok` (nothing is shown
 * for a principal that was not verified). `linkNext` is the page-owned local return target of a link.
 */
export function accountSecurityFrom(reads: IdentityReads, linkNext: string): AccountSecurity {
  if (reads.me === null || reads.me.kind !== "ok") return NO_ACCOUNT_SECURITY;
  const methodList = reads.methods !== null && reads.methods.kind === "ok" ? reads.methods.methods : [];
  const active = methodList.filter((m) => m.status === "ACTIVE");
  const sessionList = reads.sessions !== null && reads.sessions.kind === "ok" ? reads.sessions.sessions : [];
  const currents = sessionList.filter((s) => s.current);
  const currentType = currents.length === 1 ? currents[0].methodType : null;
  const ofCurrentType = currentType === null ? [] : active.filter((m) => m.methodType === currentType);

  const methods: MethodRelation[] = [];
  for (const method of active) {
    const label = labelOf(method, reads);
    if (label === null) continue; // an inconsistent entry (24 §9.1) is not presented, let alone offered for removal
    methods.push({
      methodId: method.methodId,
      methodType: method.methodType,
      label,
      words: authenticationWords(label),
      providerEmail: method.provider === null ? null : method.provider.email,
      lastAuthenticatedAt: method.lastAuthenticatedAt,
      current: ofCurrentType.length === 1 && ofCurrentType[0].methodId === method.methodId,
      removable: active.length > 1,
    });
  }

  const sessions: SessionRelation[] = sessionList.map((s) => {
    const producer = s.methodType === null ? [] : methodList.filter((m) => m.methodType === s.methodType && m.status === "ACTIVE");
    return {
      sessionId: s.sessionId,
      issuedAt: s.issuedAt,
      expiresAt: s.expiresAt,
      current: s.current,
      words: producer.length === 1 ? methodWords(producer[0], reads) : null,
    };
  });

  // a provider is offered once: not while an ACTIVE method already carries its providerId (joined on the server's
  // own providerId attribute, never on a method type or an email); without a current methods read nothing is
  // known about what is held, so nothing is offered; an unsafe return target yields no offer
  const links: LinkOffer[] = [];
  if (reads.methods !== null && reads.methods.kind === "ok" && reads.providers !== null && reads.providers.kind === "ok") {
    for (const provider of reads.providers.providers) {
      if (active.some((m) => m.provider !== null && m.provider.providerId === provider.providerId)) continue;
      try {
        links.push({ provider, action: linkStartAction(provider, linkNext) });
      } catch {
        // UnsafeNextTarget: nothing unsafe is ever sent, so nothing is offered
      }
    }
  }
  const rotatable = methods.some((m) => m.label.kind === "local");
  return { methods, sessions, links, rotatable };
}
