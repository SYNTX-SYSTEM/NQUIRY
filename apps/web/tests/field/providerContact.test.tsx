/**
 * AUTH/CYAN-02 falsifiers: the provider contact exists only from parsed live-shaped provider truth; every unknown,
 * malformed, unavailable, denied or failed discovery renders nothing; the control is the typed LOGIN start URL and
 * nothing else; no link, account-creation, role or authority semantics; the login page keeps its local form.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { ProviderContact } from "../../components/field/ProviderContact";
import { googleLoginStart, loginStartUrl, parseProviderList } from "../../lib/api/authClient";
import { discoverProviderContact, NO_PROVIDER_CONTACT, providerContactFrom } from "../../lib/field/providerContact";

const WEB = join(__dirname, "..", "..");
const code = (p: string) => readFileSync(join(WEB, p), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
const COMPONENT = code("components/field/ProviderContact.tsx");
const DERIVATION = code("lib/field/providerContact.ts");
const HOOK = code("lib/field/useProviderContact.ts");
const PAGE = code("app/login/page.tsx");

/** The exact live `GET /auth/providers` body of nquiry.condyn.eu (2026-10-03, read-only probe). */
const LIVE = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] };
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
const render = (contact: Parameters<typeof ProviderContact>[0]["contact"]) => renderToStaticMarkup(<ProviderContact contact={contact} />);

describe("proof 1 + 7: the contact appears only from parsed live-shaped provider truth and uses the typed login-start builder", () => {
  it("derives the contact from the live fixture with the typed LOGIN start URL", () => {
    const list = parseProviderList(LIVE);
    const contact = providerContactFrom(list, "/");
    expect(contact.kind).toBe("contact");
    if (contact.kind !== "contact") throw new Error("unreachable");
    expect(contact.provider.providerId).toBe("google");
    expect(contact.provider.proofClass).toBe("PRODUCTION_PROVIDER");
    expect(contact.url).toBe(loginStartUrl(list.providers[0], "/"));
    expect(contact.url).toBe("http://localhost:8000/auth/oidc/google/start?next=%2F");
  });
  it("renders one navigation to that URL inside the access core vocabulary, labelled by the parsed label", () => {
    const html = render(providerContactFrom(parseProviderList(LIVE), "/"));
    expect(html).toContain('data-testid="provider-contact"');
    expect(html).toMatch(/<a [^>]*class="button secondary access-provider-action"[^>]*href="http:\/\/localhost:8000\/auth\/oidc\/google\/start\?next=%2F"[^>]*>Continue with Google<\/a>/);
    expect(html).toContain('data-testid="provider-google"');
    expect(html).toContain('data-provider-id="google"');
    expect(html).toContain('data-proof-class="PRODUCTION_PROVIDER"');
    expect(html).not.toContain("test provider");
    expect((html.match(/<a /g) ?? []).length).toBe(1);
    expect(html).not.toMatch(/<button|<form|<input/);
  });
  it("discovers through the typed client with credentials and the live fixture", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(json(LIVE));
    const contact = await discoverProviderContact("/", fetchImpl);
    expect(contact.kind).toBe("contact");
    expect(fetchImpl).toHaveBeenCalledWith("http://localhost:8000/auth/providers", expect.objectContaining({ credentials: "include" }));
  });
  it("names a non-production proof class instead of hiding it (24 §27), still from parsed truth only", () => {
    const list = parseProviderList({ kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "TEST_PROVIDER" }] });
    const html = render(providerContactFrom(list, "/"));
    expect(html).toContain('data-proof-class="TEST_PROVIDER"');
    expect(html).toContain("test provider");
  });
});

describe("proof 2 + 10: no hard-coded availability, no inference, no authority", () => {
  it("the derivation, hook and component never name google, a proof class or a provider label as a literal", () => {
    for (const [name, src] of [["derivation", DERIVATION], ["hook", HOOK], ["component", COMPONENT]] as const) {
      expect(src, name).not.toMatch(/["'`]google["'`]/i);
      expect(src, name).not.toMatch(/["'`]Google["'`]/);
      expect(src, name).not.toMatch(/providerId:\s*["']/);
      expect(src, name).not.toMatch(/label:\s*["']/);
    }
    expect(COMPONENT).not.toMatch(/["'`]TEST_PROVIDER["'`]/);
  });
  it("the login page carries no provider literal either: the server answer is the only source", () => {
    expect(PAGE).not.toMatch(/google/i);
    expect(PAGE).not.toMatch(/PRODUCTION_PROVIDER|TEST_PROVIDER|proofClass/);
    expect(PAGE).toMatch(/useProviderContact\(mountPath\("\/"\)\)/); // the mount root (CYAN_REAL_E2E_FIELD_MOUNT_01)
    expect(PAGE).toMatch(/<ProviderContact contact=\{providerContact\} \/>/);
  });
  it("the only path to a contact is googleLoginStart on a parsed list (no URL is hand-built)", () => {
    expect(DERIVATION).toMatch(/googleLoginStart\(list, next\)/);
    expect(DERIVATION).not.toMatch(/\/auth\/oidc|\/start|\/link/);
    expect(COMPONENT).not.toMatch(/\/auth\/oidc|\/start|\/link|apiBaseUrl/);
    expect(HOOK).not.toMatch(/\/auth\/oidc|\/start|\/link|apiBaseUrl/);
  });
  it("no role, authority, viewer or session semantics in the contact sources", () => {
    for (const src of [DERIVATION, HOOK, COMPONENT]) {
      expect(src).not.toMatch(/\brole\b|authority|viewer|isGovernanceRoot|isSessionController|permission/i);
    }
  });
  it("no persistence, no timers, no retry loop", () => {
    for (const src of [DERIVATION, HOOK, COMPONENT]) {
      expect(src).not.toMatch(/localStorage|sessionStorage|indexedDB|setTimeout|setInterval|document\.cookie/);
    }
  });
});

describe("proof 3, 4, 5: fail-closed rendering", () => {
  const closed: ReadonlyArray<[string, unknown]> = [
    ["malformed: unknown proofClass", { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PROVEN_PROVIDER" }] }],
    ["malformed: missing proofClass", { kind: "ok", providers: [{ providerId: "google", label: "Google" }] }],
    ["malformed: extra field", { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER", available: true }] }],
    ["malformed: envelope availability flag", { kind: "ok", providers: [], googleAvailable: true }],
    ["unknown kind", { kind: "providers", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] }],
    ["denied", { kind: "denied", reasonCode: "NO_SESSION" }],
    ["unavailable", { kind: "unavailable", reasonCode: "PROVIDER_NOT_CONFIGURED" }],
    ["empty provider list", { kind: "ok", providers: [] }],
    ["only another provider", { kind: "ok", providers: [{ providerId: "test", label: "Local test issuer", proofClass: "TEST_PROVIDER" }] }],
    ["forbidden key", { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER", clientSecret: "x" }] }],
    ["null body", null],
  ];
  for (const [name, body] of closed) {
    it(`${name} → no contact, nothing rendered`, async () => {
      const contact = await discoverProviderContact("/", vi.fn().mockResolvedValue(json(body)));
      expect(contact).toEqual(NO_PROVIDER_CONTACT);
      expect(render(contact)).toBe("");
    });
  }
  it("non-JSON 503 → no contact", async () => {
    const contact = await discoverProviderContact("/", vi.fn().mockResolvedValue(new Response("<html>503</html>", { status: 503 })));
    expect(contact).toEqual(NO_PROVIDER_CONTACT);
  });
  it("network failure → no contact (never a thrown or invented availability)", async () => {
    const contact = await discoverProviderContact("/", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    expect(contact).toEqual(NO_PROVIDER_CONTACT);
  });
  it("the component renders nothing for none", () => {
    expect(render(NO_PROVIDER_CONTACT)).toBe("");
  });
});

describe("proof 8 + 9: unsafe next stays refused; no link or account-creation behaviour", () => {
  it("an unsafe next target yields no contact (the builder refuses, the derivation fails closed)", async () => {
    expect(() => googleLoginStart(parseProviderList(LIVE), "https://evil.example/")).toThrow();
    expect(await discoverProviderContact("https://evil.example/", vi.fn().mockResolvedValue(json(LIVE)))).toEqual(NO_PROVIDER_CONTACT);
    expect(await discoverProviderContact("//evil.example", vi.fn().mockResolvedValue(json(LIVE)))).toEqual(NO_PROVIDER_CONTACT);
  });
  it("the contact sources never speak of linking, account creation, recovery, methods, sessions, unlink or logout-all", () => {
    for (const src of [DERIVATION, HOOK, COMPONENT, PAGE]) {
      expect(src).not.toMatch(/linkStart|linkStartAction|readLinkProjection|unlinkMethod|listMethods|listSessions|revokeSession|logoutAll|startRecovery|createAccount|sign up|register/i);
    }
    const html = render(providerContactFrom(parseProviderList(LIVE), "/"));
    expect(html).not.toMatch(/link|sign up|create|account|register/i);
  });
});

describe("proof 6: local-password login remains unchanged", () => {
  it("the page keeps the email/password form, the submit control and the F02 login call", () => {
    expect(PAGE).toMatch(/data-testid="login-email"/);
    expect(PAGE).toMatch(/data-testid="login-password"/);
    expect(PAGE).toMatch(/data-testid="login-submit"/);
    expect(PAGE).toMatch(/login\(email, password\)/);
    expect(PAGE).toMatch(/router\.replace\("\/"\)/);
    // the contact is placed after the form, inside the core, before the status/boundary lines
    expect(PAGE.indexOf("</form>")).toBeLessThan(PAGE.indexOf("<ProviderContact"));
    expect(PAGE.indexOf("<ProviderContact")).toBeLessThan(PAGE.indexOf('data-testid="login-pending"'));
  });
});
