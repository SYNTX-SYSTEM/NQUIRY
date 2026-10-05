/**
 * AUTH/CYAN-ACCOUNT-01 falsifiers: the account-security relations derive from the SAME reads as the identity
 * projection; ACTIVE methods only; the current method is the current session's; Remove only while another ACTIVE
 * method remains (24 §14.6 mirrored, never decided); a provider is offered once, by providerId, with a safe return
 * target; sessions carry End except the current one; the `?link=` vocabulary is closed; effects settle verbatim.
 * GOOGLE_BOOTSTRAP (PURPLE CONSUMER_CONTRACT.md §1): a bootstrapped identity is a different principal with its own
 * presentation and a single provider method — nothing merges, compares or prefers identities.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { afterAll, describe, expect, it } from "vitest";

import { AccountSecurity } from "../../components/field/AccountSecurity";
import { parseIdentityPresentation, parseMethodList, parseProviderList, parseSessionList } from "../../lib/api/authClient";
import { endSession, removeMethod, signOutEverywhere } from "../../lib/field/accountEffects";
import { accountSecurityFrom, NO_ACCOUNT_SECURITY } from "../../lib/field/accountSecurity";
import { identityProjectionFrom, type IdentityReads } from "../../lib/field/identityProjection";
import { LINK_BOUNDARY_MESSAGES, linkBoundaryFrom, NO_LINK_BOUNDARY } from "../../lib/field/linkBoundary";

const WEB = join(__dirname, "..", "..");
const code = (p: string) => readFileSync(join(WEB, p), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
const DERIVATION = code("lib/field/accountSecurity.ts");
const EFFECTS = code("lib/field/accountEffects.ts");
const COMPONENT = code("components/field/AccountSecurity.tsx");
const BOUNDARY = code("lib/field/linkBoundary.ts");
const PAGE = code("app/workspaces/page.tsx");

const USER = "7dd6e767-1111-4111-8111-111111111111";
const USER_B = "3f7842f6-2222-4222-8222-222222222222";
const S_CUR = "aaaaaaaa-1111-4111-8111-111111111111";
const S_OLD = "bbbbbbbb-1111-4111-8111-111111111111";
const M_LOCAL = "cccccccc-1111-4111-8111-111111111111";
const M_GOOGLE = "dddddddd-1111-4111-8111-111111111111";
const M_GOOGLE_B = "eeeeeeee-2222-4222-8222-222222222222";
const T0 = "2026-10-01T08:00:00+00:00";
const T1 = "2026-10-03T08:00:00+00:00";
const T2 = "2026-10-04T08:00:00+00:00";
const NEXT = "/workspaces";

const PROVIDERS = parseProviderList({ kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] });
const LOCAL_METHOD = { methodId: M_LOCAL, methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: T0, lastAuthenticatedAt: T0, provider: null };
const GOOGLE_METHOD = { methodId: M_GOOGLE, methodType: "GOOGLE_OIDC", status: "ACTIVE", createdAt: T1, lastAuthenticatedAt: T1, provider: { providerId: "google", email: "person@example.test" } };
const BOTH = parseMethodList({ kind: "ok", methods: [LOCAL_METHOD, GOOGLE_METHOD] });
const LOCAL_ONLY = parseMethodList({ kind: "ok", methods: [LOCAL_METHOD] });
const sessions = (list: ReadonlyArray<{ id: string; current: boolean; methodType: string | null }>) =>
  parseSessionList({ kind: "ok", sessions: list.map((s) => ({ sessionId: s.id, issuedAt: T1, expiresAt: T2, current: s.current, methodType: s.methodType })) });
const IDENTITY_A = parseIdentityPresentation({ kind: "ok", userId: USER, displayName: "Person A", canonicalEmail: "a@example.test" });
const READS: IdentityReads = { me: { kind: "ok", userId: USER }, identity: IDENTITY_A, sessions: sessions([{ id: S_OLD, current: false, methodType: "LOCAL_PASSWORD" }, { id: S_CUR, current: true, methodType: "GOOGLE_OIDC" }]), methods: BOTH, providers: PROVIDERS };

/** GOOGLE_BOOTSTRAP: a different principal, one provider method, name and email copied from the provider at creation. */
const BOOTSTRAP_READS: IdentityReads = {
  me: { kind: "ok", userId: USER_B },
  identity: parseIdentityPresentation({ kind: "ok", userId: USER_B, displayName: "Provider Person", canonicalEmail: "person@example.test" }),
  sessions: sessions([{ id: S_CUR, current: true, methodType: "GOOGLE_OIDC" }]),
  methods: parseMethodList({ kind: "ok", methods: [{ ...GOOGLE_METHOD, methodId: M_GOOGLE_B }] }),
  providers: PROVIDERS,
};

const EFFECTS_IDLE = { blocked: false, onRemoveMethod: () => undefined, onEndSession: () => undefined, onSignOutEverywhere: () => undefined };
const render = (reads: IdentityReads, search = "") => renderToStaticMarkup(<AccountSecurity security={accountSecurityFrom(reads, NEXT)} link={linkBoundaryFrom(search)} effects={EFFECTS_IDLE} />);

describe("A1–A6: the relations from the one set of reads", () => {
  it("A1: two ACTIVE methods → both listed with words and provider account, the session's method current, both removable", () => {
    const s = accountSecurityFrom(READS, NEXT);
    expect(s.methods.map((m) => [m.methodId, m.words, m.providerEmail, m.current, m.removable, m.lastAuthenticatedAt])).toEqual([
      [M_LOCAL, "Local password", null, false, true, T0],
      [M_GOOGLE, "Google", "person@example.test", true, true, T1],
    ]);
  });
  it("A2: a REVOKED method is neither listed nor counted; one ACTIVE method is not removable", () => {
    const revoked = parseMethodList({ kind: "ok", methods: [LOCAL_METHOD, { ...GOOGLE_METHOD, status: "REVOKED" }] });
    const s = accountSecurityFrom({ ...READS, methods: revoked }, NEXT);
    expect(s.methods.map((m) => [m.methodId, m.removable])).toEqual([[M_LOCAL, false]]);
  });
  it("A3: the current method is the ONE ACTIVE method of the current session's type; no current session → none current", () => {
    const noCurrent = accountSecurityFrom({ ...READS, sessions: sessions([{ id: S_OLD, current: false, methodType: "LOCAL_PASSWORD" }]) }, NEXT);
    expect(noCurrent.methods.every((m) => !m.current)).toBe(true);
    const twoOfType = parseMethodList({ kind: "ok", methods: [LOCAL_METHOD, GOOGLE_METHOD, { ...GOOGLE_METHOD, methodId: M_GOOGLE_B }] });
    expect(accountSecurityFrom({ ...READS, methods: twoOfType }, NEXT).methods.every((m) => !m.current)).toBe(true);
  });
  it("A4: an inconsistent entry (provider type without provider attribute) is not presented, not offered for removal", () => {
    const broken = parseMethodList({ kind: "ok", methods: [LOCAL_METHOD, { ...GOOGLE_METHOD, provider: null }] });
    expect(accountSecurityFrom({ ...READS, methods: broken }, NEXT).methods.map((m) => m.methodId)).toEqual([M_LOCAL]);
  });
  it("A5: sessions are listed as read, current flagged, their words from the producing method; a method-less session has none", () => {
    const s = accountSecurityFrom({ ...READS, sessions: sessions([{ id: S_OLD, current: false, methodType: null }, { id: S_CUR, current: true, methodType: "GOOGLE_OIDC" }]) }, NEXT);
    expect(s.sessions.map((x) => [x.sessionId, x.current, x.words])).toEqual([
      [S_OLD, false, null],
      [S_CUR, true, "Google"],
    ]);
  });
  it("A6: /auth/me not ok → the empty field whatever the other reads say; failed relation reads → empty lists, never invented", () => {
    expect(accountSecurityFrom({ ...READS, me: null }, NEXT)).toEqual(NO_ACCOUNT_SECURITY);
    expect(accountSecurityFrom({ ...READS, me: { kind: "denied", reasonCode: "NO_SESSION" } }, NEXT)).toEqual(NO_ACCOUNT_SECURITY);
    const failed = accountSecurityFrom({ ...READS, methods: null, sessions: null }, NEXT);
    expect(failed.methods).toEqual([]);
    expect(failed.sessions).toEqual([]);
    expect(failed.links).toEqual([]); // what is held is unknown → nothing is offered
  });
});

describe("L1–L4: the link offer", () => {
  it("L1: a configured provider the identity holds no ACTIVE method for is offered once, with the typed LINK start action to the page-owned target", () => {
    const s = accountSecurityFrom({ ...READS, methods: LOCAL_ONLY }, NEXT);
    expect(s.links.map((l) => [l.provider.providerId, l.action.method, l.action.action])).toEqual([["google", "POST", "http://localhost:8000/auth/oidc/google/link/start?next=%2Fworkspaces"]]);
  });
  it("L2: a provider already carried by an ACTIVE method (joined on providerId) is not offered; a REVOKED one does not count as held", () => {
    expect(accountSecurityFrom(READS, NEXT).links).toEqual([]);
    const revoked = parseMethodList({ kind: "ok", methods: [LOCAL_METHOD, { ...GOOGLE_METHOD, status: "REVOKED" }] });
    expect(accountSecurityFrom({ ...READS, methods: revoked }, NEXT).links.map((l) => l.provider.providerId)).toEqual(["google"]);
  });
  it("L3: no parsed provider list → no offer; an unsafe return target → no offer (nothing unsafe is ever sent)", () => {
    expect(accountSecurityFrom({ ...READS, methods: LOCAL_ONLY, providers: null }, NEXT).links).toEqual([]);
    expect(accountSecurityFrom({ ...READS, methods: LOCAL_ONLY }, "https://evil.example/").links).toEqual([]);
    expect(accountSecurityFrom({ ...READS, methods: LOCAL_ONLY }, "//evil.example").links).toEqual([]);
  });
  it("L4: the derivation carries no provider literal, no method-type ↔ provider table, no email inference, no role words", () => {
    expect(DERIVATION).not.toMatch(/["'`]Google["'`]|["'`]google["'`]|gmail|GOOGLE_OIDC/i);
    expect(DERIVATION).not.toMatch(/split\("@"\)|\.endsWith\(|domain/i);
    expect(DERIVATION).not.toMatch(/\brole\b|authority|permission|capabilit|membership|owner|facilitator/i);
    expect(DERIVATION).not.toMatch(/mount/i);
  });
});

describe("B1–B3: the ?link= result (closed vocabulary)", () => {
  it("B1: each known word yields its one sentence; only ok is a committed consequence", () => {
    for (const word of ["ok", "already_linked", "collision", "cancelled", "failed"] as const) {
      const r = linkBoundaryFrom(`?link=${word}`);
      expect(r).toEqual({ kind: "result", projection: word, message: LINK_BOUNDARY_MESSAGES[word], settled: word === "ok" ? "committed" : "none" });
    }
  });
  it("B2: missing, unknown, repeated or empty → none (UNKNOWN != OK, UNKNOWN != FAILURE)", () => {
    for (const search of ["", "?x=1", "?link=linked", "?link=ok&link=failed", "?link=", "?link=OK"]) expect(linkBoundaryFrom(search)).toEqual(NO_LINK_BOUNDARY);
  });
  it("B3: no sentence speaks of access, a role or an account creation", () => {
    for (const m of Object.values(LINK_BOUNDARY_MESSAGES)) expect(m).not.toMatch(/\brole\b|authority|permission|access|created an account|registered/i);
    expect(BOUNDARY).not.toMatch(/\brole\b|authority|permission|capabilit|membership/i);
  });
});

describe("C1–C7: the chamber markup", () => {
  it("C1: both methods with Remove, no link offer, two sessions with End only on the other one, Sign out everywhere", () => {
    const html = render(READS);
    expect(html.match(/data-testid="account-method"/g)?.length).toBe(2);
    expect(html.match(/data-testid="account-method-remove"/g)?.length).toBe(2);
    expect(html).not.toContain('data-testid="account-link-form"');
    expect(html).toContain('data-testid="account-method-email"');
    expect(html).toContain("current session");
    expect(html.match(/data-testid="account-method-last-used"/g)?.length).toBe(2); // the server's last-use fact, never computed here
    expect(html).toContain("2026-10-03 08:00:00 UTC");
    expect(html.match(/data-testid="account-session"/g)?.length).toBe(2);
    expect(html.match(/data-testid="account-session-end"/g)?.length).toBe(1);
    expect(html).toContain('data-testid="account-session-current"');
    expect(html).toContain('data-testid="account-sign-out-everywhere"');
    expect(html).toContain("ends this session and 1 other");
  });
  it("C2: GOOGLE_BOOTSTRAP — a different principal: its own presentation, one method, no Remove, the last-method note, no offer for the held provider", () => {
    const p = identityProjectionFrom(BOOTSTRAP_READS);
    expect(p.identity).toEqual({ kind: "authenticated", userId: USER_B, presentation: { kind: "presented", displayName: "Provider Person", canonicalEmail: "person@example.test" } });
    expect(p.providerAccount).toEqual({ kind: "email", providerId: "google", email: "person@example.test" });
    expect(identityProjectionFrom(READS).identity).not.toEqual(p.identity); // nothing merges two principals
    const html = render(BOOTSTRAP_READS);
    expect(html.match(/data-testid="account-method"/g)?.length).toBe(1);
    expect(html).not.toContain('data-testid="account-method-remove"');
    expect(html).toContain('data-testid="account-method-last"');
    expect(html).not.toContain('data-testid="account-link-form"');
    expect(html).toContain("ends this session<");
  });
  it("C3: a local-only identity is offered the configured provider as a form the browser submits (POST to the typed action)", () => {
    const html = render({ ...READS, methods: LOCAL_ONLY, sessions: sessions([{ id: S_CUR, current: true, methodType: "LOCAL_PASSWORD" }]) });
    expect(html).toMatch(/<form [^>]*action="http:\/\/localhost:8000\/auth\/oidc\/google\/link\/start\?next=%2Fworkspaces"[^>]*method="POST"/);
    expect(html).toContain('data-testid="account-link-google"');
    expect(html).toContain("Add Google");
    expect(html).not.toContain("test provider");
  });
  it("C4: a test-class provider is named as such (24 §27: shown, never hidden)", () => {
    const test = parseProviderList({ kind: "ok", providers: [{ providerId: "test", label: "Test issuer", proofClass: "TEST_PROVIDER" }] });
    const html = render({ ...READS, methods: LOCAL_ONLY, providers: test });
    expect(html).toContain('data-proof-class="TEST_PROVIDER"');
    expect(html).toContain("test provider");
  });
  it("C5: failed relation reads → 'could not be read', no control, nothing current", () => {
    const html = render({ ...READS, methods: null, sessions: null });
    expect(html).toContain('data-testid="account-methods-unknown"');
    expect(html).toContain('data-testid="account-sessions-unknown"');
    expect(html).not.toMatch(/account-method-remove|account-session-end|account-sign-out-everywhere/);
  });
  it("C6: the ?link= result renders inside the chamber: ok as status, every other word as alert; none renders nothing", () => {
    expect(render(READS, "?link=ok")).toMatch(/role="status"[^>]*data-testid="link-result"[^>]*data-projection="ok"[^>]*data-settled="committed"/);
    expect(render(READS, "?link=collision")).toMatch(/role="alert"[^>]*data-testid="link-result"[^>]*data-projection="collision"[^>]*data-settled="none"/);
    expect(render(READS, "?link=whatever")).not.toContain('data-testid="link-result"');
  });
  it("C7: no role, authority, permission, recovery, registration, avatar or raw secret word in the chamber or its sources; controls are disabled while an effect is in flight", () => {
    const html = render(READS);
    // `role=` is the ARIA attribute of the result line (status / alert), never a Workspace role word
    expect(html).not.toMatch(/\brole\b(?!=)|authority|permission|capabilit|membership|avatar|password reset|forgot|register|sign up|token|secret/i);
    for (const src of [COMPONENT, DERIVATION, EFFECTS]) expect(src).not.toMatch(/\brole\b(?!=)|authority|permission|capabilit|membership|avatar|recover|register/i);
    const blocked = renderToStaticMarkup(<AccountSecurity security={accountSecurityFrom(READS, NEXT)} link={NO_LINK_BOUNDARY} effects={{ ...EFFECTS_IDLE, blocked: true }} />);
    expect(blocked.match(/<button[^>]*disabled=""/g)?.length).toBe(4);
  });
});

describe("E1–E4: effects settle verbatim (Network Failure != Proof Of No Effect)", () => {
  const json = (status: number, body: unknown): typeof fetch => async () => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
  it("E1: unlink ok → committed with the server's own consequence facts", async () => {
    vi_stub(json(200, { kind: "ok", methodId: M_GOOGLE, sessionsRevoked: 2, currentSessionEnded: true }));
    expect(await removeMethod(M_GOOGLE)).toEqual({ kind: "committed", reasonCode: null, body: { methodId: M_GOOGLE, sessionsRevoked: 2, currentSessionEnded: true } });
  });
  it("E2: LAST_METHOD / UNLINK_DENIED / SESSION_NOT_FOUND pass through as denied with the verbatim reason", async () => {
    vi_stub(json(409, { kind: "denied", reasonCode: "LAST_METHOD" }));
    expect(await removeMethod(M_LOCAL)).toEqual({ kind: "denied", reasonCode: "LAST_METHOD" });
    vi_stub(json(404, { kind: "denied", reasonCode: "SESSION_NOT_FOUND" }));
    expect(await endSession(S_OLD)).toEqual({ kind: "denied", reasonCode: "SESSION_NOT_FOUND" });
  });
  it("E3: a lost response is network_failure; an unrecognized one is indeterminate — never committed, never 'nothing happened'", async () => {
    vi_stub(async () => {
      throw new TypeError("Failed to fetch");
    });
    expect(await signOutEverywhere()).toEqual({ kind: "network_failure", reasonCode: "NETWORK_FAILURE" });
    vi_stub(json(200, { kind: "ok", extra: true }));
    expect(await signOutEverywhere()).toEqual({ kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" });
    vi_stub(async () => new Response("<html>bad gateway</html>", { status: 502, headers: { "content-type": "text/html" } }));
    expect(await endSession(S_OLD)).toEqual({ kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" });
  });
  it("E4: logout-all ok → committed with the revoked count; the page leaves for /login only on a committed session end", async () => {
    vi_stub(json(200, { kind: "ok", revokedSessions: 3 }));
    expect(await signOutEverywhere()).toEqual({ kind: "committed", reasonCode: null, body: { revokedSessions: 3 } });
    expect(PAGE).toMatch(/accountSecurityFrom\(identityField\.reads, mountPath\("\/workspaces"\)\)/);
    expect(PAGE).toMatch(/onCommitted: \(body\) => leaveWhenEnded\(body\.currentSessionEnded\)/);
    expect(PAGE).toMatch(/reconstruct: identityField\.reload/);
    expect(PAGE).toMatch(/title="Access security"/);
    expect(PAGE).not.toMatch(/unlinkMethod|revokeSession|logoutAll|listSessions|listMethods|listProviders/);
  });
});

/** The effects read the global fetch (through the typed client's default); each case installs its own. */
const REAL_FETCH = globalThis.fetch;
function vi_stub(impl: typeof fetch): void {
  globalThis.fetch = impl;
}
afterAll(() => {
  globalThis.fetch = REAL_FETCH;
});
