/**
 * CYAN-ENTRY-01 falsifiers: the entry path of a person without an identity is derived only from the parsed provider
 * contact; the operator relation is always stated; no provider is named by the frontend; no control, link or form
 * exists; nothing claims that this deployment admits new identities, success, authority, membership or a role.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { EntryPath } from "../../components/field/EntryPath";
import { parseProviderList } from "../../lib/api/authClient";
import { entryPathFrom, providerWords } from "../../lib/field/entryPath";
import { NO_PROVIDER_CONTACT, providerContactFrom } from "../../lib/field/providerContact";

const WEB = join(__dirname, "..", "..");
const code = (p: string) => readFileSync(join(WEB, p), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
const DERIVATION = code("lib/field/entryPath.ts");
const COMPONENT = code("components/field/EntryPath.tsx");
const PAGE = code("app/login/page.tsx");

const LIVE = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] };
const TWO = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }, { providerId: "acme", label: "Acme ID", proofClass: "TEST_PROVIDER" }] };
const render = (list: unknown) => renderToStaticMarkup(<EntryPath entry={entryPathFrom(list === null ? NO_PROVIDER_CONTACT : providerContactFrom(parseProviderList(list), "/"))} />);

describe("E1 provider entry only from the parsed provider list; labels are the server's", () => {
  it("one listed provider → the provider sentence names its label; the operator sentence; the link sentence", () => {
    const entry = entryPathFrom(providerContactFrom(parseProviderList(LIVE), "/"));
    expect(entry.providers.map((p) => p.providerId)).toEqual(["google"]);
    expect(entry.operator).toBe("HOST_OPERATOR");
    const html = render(LIVE);
    expect(html).toContain('data-testid="access-entry"');
    expect(html).toContain('data-providers="1"');
    expect(html).toContain('data-testid="entry-provider"');
    expect(html).toContain("Continue with Google:");
    expect(html).toContain('data-testid="entry-operator"');
    expect(html).toContain("created by the operator of this deployment");
    expect(html).toContain('data-testid="entry-link"');
    expect(html).toContain("add Google under Access security");
    expect(html).toContain("does not attach it to an existing account");
  });
  it("two listed providers → both labels, joined as the server gave them, the non-production one not hidden", () => {
    expect(providerWords(parseProviderList(TWO).providers)).toBe("Google or Acme ID");
    const html = render(TWO);
    expect(html).toContain("Continue with Google or Acme ID:");
    expect(html).toContain('data-providers="2"');
  });
  it("no provider (none / empty / failed discovery) → the operator sentence only; no provider name anywhere", () => {
    for (const list of [null, { kind: "ok", providers: [] }]) {
      const html = render(list);
      expect(html).toContain('data-providers="0"');
      expect(html).toContain('data-testid="entry-operator"');
      expect(html).not.toContain('data-testid="entry-provider"');
      expect(html).not.toContain('data-testid="entry-link"');
      expect(html).not.toMatch(/google/i);
    }
    expect(providerWords([])).toBe("");
  });
});

describe("E2 words only: no control, no form, no invented policy, success, authority or role", () => {
  it("the section carries no interactive element and no navigation", () => {
    for (const list of [LIVE, TWO, null]) {
      const html = render(list);
      expect(html).not.toMatch(/<a\b|<button\b|<form\b|<input\b/);
    }
  });
  it("the provider sentence is conditional on the server's decision and never states that this deployment admits new identities", () => {
    const html = render(LIVE);
    expect(html).toMatch(/decided by the server when you continue/);
    expect(html).toMatch(/no identity is created/);
    expect(html).not.toMatch(/you can (register|sign up|create)|registration is (open|allowed)|self[- ]registration/i);
    expect(html).not.toMatch(/success|welcome|authori|role|membership|permission|grant/i);
  });
  it("LINK != LOGIN is stated: continuing with a provider on the login never attaches it", () => {
    expect(render(LIVE)).toMatch(/Continuing with a provider here does not attach it/);
  });
});

describe("E3 source laws", () => {
  it("the derivation is pure and names no provider; the component names no provider", () => {
    expect(DERIVATION).not.toMatch(/fetch|react|google/i);
    expect(COMPONENT).not.toMatch(/google|fetch/i);
  });
  it("the login page derives the entry from the SAME parsed provider contact it renders", () => {
    expect(PAGE).toMatch(/<EntryPath entry=\{entryPathFrom\(providerContact\)\} \/>/);
    expect(PAGE).toMatch(/<ProviderContact contact=\{providerContact\} \/>/);
  });
});
