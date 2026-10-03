/**
 * AUTH/CYAN-IDENTITY-01 falsifiers: /auth/me is the only identity source; the current session only from
 * current=true; the method only as the one ACTIVE method of the session's type; the provider label only from parsed
 * provider truth; the provider email a method attribute; every malformed/unavailable read fails closed; no role,
 * authority, permission, name or avatar; the Workspaces page keeps its access projection and the exit.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { IdentityProjection } from "../../components/field/IdentityProjection";
import { parseMethodList, parseProviderList, parseSessionList } from "../../lib/api/authClient";
import { authenticationWords, identityProjectionFrom, LOCAL_PASSWORD_LABEL, NO_IDENTITY_PROJECTION, type IdentityReads } from "../../lib/field/identityProjection";

const WEB = join(__dirname, "..", "..");
const code = (p: string) => readFileSync(join(WEB, p), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
const DERIVATION = code("lib/field/identityProjection.ts");
const HOOK = code("lib/field/useIdentityProjection.ts");
const COMPONENT = code("components/field/IdentityProjection.tsx");
const PAGE = code("app/workspaces/page.tsx");

const USER = "7dd6e767-1111-4111-8111-111111111111";
const S_CUR = "aaaaaaaa-1111-4111-8111-111111111111";
const S_OLD = "bbbbbbbb-1111-4111-8111-111111111111";
const M_LOCAL = "cccccccc-1111-4111-8111-111111111111";
const M_GOOGLE = "dddddddd-1111-4111-8111-111111111111";
const T0 = "2026-10-01T08:00:00+00:00";
const T1 = "2026-10-03T08:00:00+00:00";
const T2 = "2026-10-04T08:00:00+00:00";

const PROVIDERS = parseProviderList({ kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] });
const METHODS = parseMethodList({
  kind: "ok",
  methods: [
    { methodId: M_LOCAL, methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: T0, lastAuthenticatedAt: T0, provider: null },
    { methodId: M_GOOGLE, methodType: "GOOGLE_OIDC", status: "ACTIVE", createdAt: T1, lastAuthenticatedAt: T1, provider: { providerId: "google", email: "person@example.test" } },
  ],
});
const sessions = (list: ReadonlyArray<{ id: string; current: boolean; methodType: string | null; issuedAt?: string }>) =>
  parseSessionList({ kind: "ok", sessions: list.map((s) => ({ sessionId: s.id, issuedAt: s.issuedAt ?? T1, expiresAt: T2, current: s.current, methodType: s.methodType })) });
const GOOGLE_READS: IdentityReads = { me: { kind: "ok", userId: USER }, sessions: sessions([{ id: S_OLD, current: false, methodType: "LOCAL_PASSWORD", issuedAt: T0 }, { id: S_CUR, current: true, methodType: "GOOGLE_OIDC" }]), methods: METHODS, providers: PROVIDERS };
const LOCAL_READS: IdentityReads = { ...GOOGLE_READS, sessions: sessions([{ id: S_CUR, current: true, methodType: "LOCAL_PASSWORD" }]) };
const render = (reads: IdentityReads) => renderToStaticMarkup(<IdentityProjection projection={identityProjectionFrom(reads)} />);

describe("proofs 1–7: the relation from authoritative reads", () => {
  it("a Google session: identity, current session, GOOGLE_OIDC via the server-owned label Google, provider email as attribute", () => {
    const p = identityProjectionFrom(GOOGLE_READS);
    expect(p.identity).toEqual({ kind: "authenticated", userId: USER });
    expect(p.session).toEqual({ kind: "current", sessionId: S_CUR, issuedAt: T1, expiresAt: T2, methodType: "GOOGLE_OIDC" });
    expect(p.authentication).toEqual({ kind: "via", methodType: "GOOGLE_OIDC", status: "ACTIVE", lastAuthenticatedAt: T1, label: { kind: "provider", providerId: "google", label: "Google" } });
    expect(p.providerAccount).toEqual({ kind: "email", providerId: "google", email: "person@example.test" });
    expect(authenticationWords(p.authentication.kind === "via" ? p.authentication.label : { kind: "local" })).toBe("Google");
  });
  it("a LOCAL_PASSWORD session: the legitimate local label, no provider account", () => {
    const p = identityProjectionFrom(LOCAL_READS);
    expect(p.session.kind === "current" && p.session.methodType).toBe("LOCAL_PASSWORD");
    expect(p.authentication).toEqual({ kind: "via", methodType: "LOCAL_PASSWORD", status: "ACTIVE", lastAuthenticatedAt: T0, label: { kind: "local" } });
    expect(p.providerAccount).toEqual({ kind: "none" });
    expect(authenticationWords({ kind: "local" })).toBe(LOCAL_PASSWORD_LABEL);
    expect(render(LOCAL_READS)).toContain(">Local password<");
    expect(render(LOCAL_READS)).not.toContain("Provider account");
  });
  it("/auth/me is the only source of identity: without it nothing is projected, whatever the other reads say", () => {
    for (const me of [null, { kind: "denied", reasonCode: "NO_SESSION" } as const]) {
      expect(identityProjectionFrom({ ...GOOGLE_READS, me })).toEqual(NO_IDENTITY_PROJECTION);
      expect(renderToStaticMarkup(<IdentityProjection projection={identityProjectionFrom({ ...GOOGLE_READS, me })} />)).toBe("");
    }
  });
  it("the current session comes only from current=true: the newest, the last and the method's lastAuthenticatedAt never decide", () => {
    const none = identityProjectionFrom({ ...GOOGLE_READS, sessions: sessions([{ id: S_OLD, current: false, methodType: "LOCAL_PASSWORD", issuedAt: T0 }, { id: S_CUR, current: false, methodType: "GOOGLE_OIDC", issuedAt: T1 }]) });
    expect(none.session).toEqual({ kind: "none" });
    expect(none.authentication).toEqual({ kind: "none" });
    expect(none.providerAccount).toEqual({ kind: "none" });
    expect(none.identity.kind).toBe("authenticated");
    const olderIsCurrent = identityProjectionFrom({ ...GOOGLE_READS, sessions: sessions([{ id: S_OLD, current: true, methodType: "LOCAL_PASSWORD", issuedAt: T0 }, { id: S_CUR, current: false, methodType: "GOOGLE_OIDC", issuedAt: T1 }]) });
    expect(olderIsCurrent.session.kind === "current" && olderIsCurrent.session.sessionId).toBe(S_OLD);
    expect(olderIsCurrent.authentication.kind === "via" && olderIsCurrent.authentication.label).toEqual({ kind: "local" });
  });
  it("the method relation is the one ACTIVE method of the session's type: two candidates or a revoked one → no claim", () => {
    const twoGoogle = parseMethodList({ kind: "ok", methods: [...METHODS.kind === "ok" ? METHODS.methods : [], { methodId: "eeeeeeee-1111-4111-8111-111111111111", methodType: "GOOGLE_OIDC", status: "ACTIVE", createdAt: T1, lastAuthenticatedAt: null, provider: { providerId: "google", email: "other@example.test" } }] });
    expect(identityProjectionFrom({ ...GOOGLE_READS, methods: twoGoogle }).authentication).toEqual({ kind: "none" });
    const revoked = parseMethodList({ kind: "ok", methods: [{ methodId: M_GOOGLE, methodType: "GOOGLE_OIDC", status: "REVOKED", createdAt: T1, lastAuthenticatedAt: T1, provider: { providerId: "google", email: "person@example.test" } }] });
    const p = identityProjectionFrom({ ...GOOGLE_READS, methods: revoked });
    expect(p.authentication).toEqual({ kind: "none" });
    expect(p.providerAccount).toEqual({ kind: "none" });
    expect(p.session.kind).toBe("current");
  });
  it("a session without a method type yields no authentication claim", () => {
    const p = identityProjectionFrom({ ...GOOGLE_READS, sessions: sessions([{ id: S_CUR, current: true, methodType: null }]) });
    expect(p.session.kind).toBe("current");
    expect(p.authentication).toEqual({ kind: "none" });
  });
});

describe("proofs 4, 10, 11: the provider label only from parsed provider truth; unknown never becomes friendly", () => {
  it("providers unavailable → the raw provider id, never an invented Google", () => {
    for (const providers of [null, parseProviderList({ kind: "ok", providers: [] })]) {
      const p = identityProjectionFrom({ ...GOOGLE_READS, providers });
      expect(p.authentication.kind === "via" && p.authentication.label).toEqual({ kind: "provider", providerId: "google", label: null });
      expect(render({ ...GOOGLE_READS, providers })).not.toMatch(/>Google</);
      expect(render({ ...GOOGLE_READS, providers })).toContain('data-label-kind="provider" data-provider-id="google">google<');
    }
  });
  it("the label joins on providerId, not on methodType or email domain", () => {
    const relabelled = parseProviderList({ kind: "ok", providers: [{ providerId: "google", label: "Google Workspace", proofClass: "PRODUCTION_PROVIDER" }] });
    expect(render({ ...GOOGLE_READS, providers: relabelled })).toContain(">Google Workspace<");
    const other = parseProviderList({ kind: "ok", providers: [{ providerId: "test", label: "Local test issuer", proofClass: "TEST_PROVIDER" }] });
    expect(render({ ...GOOGLE_READS, providers: other })).not.toMatch(/>Google</);
    expect(render({ ...GOOGLE_READS, providers: other })).toContain(">google<");
  });
  it("a provider-type method without its provider attribute is inconsistent → no claim", () => {
    const broken = parseMethodList({ kind: "ok", methods: [{ methodId: M_GOOGLE, methodType: "GOOGLE_OIDC", status: "ACTIVE", createdAt: T1, lastAuthenticatedAt: T1, provider: null }] });
    expect(identityProjectionFrom({ ...GOOGLE_READS, methods: broken }).authentication).toEqual({ kind: "none" });
  });
  it("the sources carry no provider literal, no friendly fallback table and no email-domain inference", () => {
    for (const [name, src] of [["derivation", DERIVATION], ["hook", HOOK], ["component", COMPONENT]] as const) {
      expect(src, name).not.toMatch(/["'`]Google["'`]|["'`]google["'`]|gmail|@google|googlemail/i);
      expect(src, name).not.toMatch(/split\("@"\)|\.endsWith\(|domain/i);
      expect(src, name).not.toMatch(/displayName|avatar|initials|fullName|firstName/);
    }
    expect(DERIVATION).not.toMatch(/GOOGLE_OIDC["']?\s*:\s*["']/);
  });
});

describe("proofs 8–9: malformed or unavailable reads fail closed", () => {
  it("sessions null → no session, no authentication, no provider account; identity stays", () => {
    const p = identityProjectionFrom({ ...GOOGLE_READS, sessions: null });
    expect(p).toEqual({ ...NO_IDENTITY_PROJECTION, identity: { kind: "authenticated", userId: USER } });
  });
  it("sessions denied → the same", () => {
    expect(identityProjectionFrom({ ...GOOGLE_READS, sessions: { kind: "denied", reasonCode: "NO_SESSION" } }).session).toEqual({ kind: "none" });
  });
  it("methods null or denied → session stays, no 'via' claim, no provider account", () => {
    for (const methods of [null, { kind: "denied", reasonCode: "NO_SESSION" } as const]) {
      const p = identityProjectionFrom({ ...GOOGLE_READS, methods });
      expect(p.session.kind).toBe("current");
      expect(p.authentication).toEqual({ kind: "none" });
      expect(p.providerAccount).toEqual({ kind: "none" });
      expect(render({ ...GOOGLE_READS, methods })).not.toContain("Current authentication");
    }
  });
  it("the typed parsers refuse malformed sessions and methods before the derivation sees them", () => {
    expect(() => parseSessionList({ kind: "ok", sessions: [{ sessionId: S_CUR, issuedAt: T1, expiresAt: T2, current: true, methodType: "MAGIC" }] })).toThrow();
    expect(() => parseSessionList({ kind: "ok", sessions: [{ sessionId: S_CUR, issuedAt: T1, expiresAt: T2, current: true, methodType: null }, { sessionId: S_OLD, issuedAt: T1, expiresAt: T2, current: true, methodType: null }] })).toThrow();
    expect(() => parseMethodList({ kind: "ok", methods: [{ methodId: M_LOCAL, methodType: "APPLE_OIDC", status: "ACTIVE", createdAt: T0, lastAuthenticatedAt: null, provider: null }] })).toThrow();
    expect(() => parseMethodList({ kind: "ok", methods: [{ methodId: M_LOCAL, methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: T0, lastAuthenticatedAt: null, provider: null, role: "Owner" }] })).toThrow();
  });
});

describe("proofs 5, 12–14: markup — attribute, not canonical identity; no role, authority, permission, name", () => {
  it("renders the four lines for a Google session with the canonical id as the only identity token", () => {
    const html = render(GOOGLE_READS);
    expect(html).toContain('data-testid="identity-projection"');
    expect(html).toMatch(/<dt>Authenticated identity<\/dt>/);
    expect(html).toContain(`data-testid="identity-user-id"`);
    // the identity token carries the canonical id and never an email (PROVIDER_EMAIL != CANONICAL_IDENTITY)
    const token = /<code class="token" data-testid="identity-user-id">([\s\S]*?)<\/code>/.exec(html)?.[1] ?? "";
    expect(token.replace(/<[^>]+>/g, "")).toBe(USER);
    expect(token).not.toContain("@");
    expect(html).toContain('data-testid="auth-method" data-method-type="GOOGLE_OIDC" data-method-status="ACTIVE"');
    expect(html).toContain("<dt>Current authentication</dt>");
    expect(html).toContain('data-label-kind="provider" data-provider-id="google">Google<');
    expect(html).toContain('data-testid="auth-provider-account" data-provider-id="google"');
    expect(html).toContain("<dt>Provider account</dt>");
    expect(html).toContain("person@example.test");
    expect(html).toContain("not your nquiry identity");
    expect(html).toContain(`data-testid="auth-session" data-session-id="${S_CUR}" data-issued-at="${T1}" data-expires-at="${T2}"`);
    expect(html).toContain("<dt>Session</dt><dd>current · authenticated</dd>");
    // the email never stands where the identity stands
    expect(html.indexOf("Authenticated identity")).toBeLessThan(html.indexOf("person@example.test"));
    expect(html).not.toMatch(/<dt>Authenticated identity<\/dt><dd>[^<]*person@example/);
  });
  it("exposes no role, authority, permission, membership, capability, name or avatar", () => {
    for (const reads of [GOOGLE_READS, LOCAL_READS]) {
      const html = render(reads);
      expect(html).not.toMatch(/\brole\b|owner|facilitator|contributor|authority|permission|capabilit|governance|member|controller|avatar|display ?name/i);
      expect(html).not.toMatch(/<a |<button(?![^>]*copy-token)|<form|<input|<select/);
    }
    for (const src of [DERIVATION, HOOK, COMPONENT]) {
      expect(src).not.toMatch(/\brole\b|isGovernanceRoot|isSessionController|authority|permission|capabilit|membership/i);
    }
    expect(DERIVATION).not.toMatch(/sort\(|\[\s*[a-z]+\.length\s*-\s*1\s*\]|lastAuthenticatedAt\s*[<>]/);
  });
  it("renders nothing for an unauthenticated projection", () => {
    expect(renderToStaticMarkup(<IdentityProjection projection={NO_IDENTITY_PROJECTION} />)).toBe("");
  });
});

describe("proofs 15–16: the Workspaces page keeps its access projection, the exit and the /auth/me gate", () => {
  it("the page still gates on fetchCurrentSession, keeps the orbit, the founding form and the Logout exit", () => {
    expect(PAGE).toMatch(/fetchCurrentSession\(\)/);
    expect(PAGE).toMatch(/router\.replace\("\/login"\)/);
    expect(PAGE).toMatch(/testId="workspaces-list"/);
    expect(PAGE).toMatch(/data-testid="create-workspace-form"/);
    expect(PAGE).toMatch(/exit=\{identity \? <LogoutButton \/> : null\}/);
    expect(PAGE).toMatch(/useIdentityProjection\(identity\)/);
    expect(PAGE).toMatch(/title="Identity and access"/);
    expect(PAGE).toMatch(/<IdentityProjection projection=\{identityProjection\} \/>/);
    expect(PAGE).not.toMatch(/listSessions|listMethods|listProviders/);
  });
});
