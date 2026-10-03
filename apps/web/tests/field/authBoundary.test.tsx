/**
 * AUTH/CYAN-03 falsifiers: every known `?auth=` word renders its one legitimate boundary; missing, unknown, repeated
 * or malformed values render nothing; no success, authority, role or account-link semantics; the boundary is derived
 * only through the typed vocabulary of AUTH/CYAN-01; the login page keeps its local form and the provider contact.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { AuthBoundary } from "../../components/field/AuthBoundary";
import { AUTH_PROJECTIONS, LINK_PROJECTIONS } from "../../lib/api/authClient";
import { AUTH_BOUNDARY_MESSAGES, authBoundaryFrom, NO_AUTH_BOUNDARY } from "../../lib/field/authBoundary";

const WEB = join(__dirname, "..", "..");
const code = (p: string) => readFileSync(join(WEB, p), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
const DERIVATION = code("lib/field/authBoundary.ts");
const HOOK = code("lib/field/useAuthBoundary.ts");
const COMPONENT = code("components/field/AuthBoundary.tsx");
const PAGE = code("app/login/page.tsx");
const render = (search: string) => renderToStaticMarkup(<AuthBoundary boundary={authBoundaryFrom(search)} />);

describe("proof 1: every known AUTH projection renders its legitimate boundary", () => {
  it("the message table covers exactly the closed vocabulary of AUTH/CYAN-01", () => {
    expect(Object.keys(AUTH_BOUNDARY_MESSAGES).sort()).toEqual([...AUTH_PROJECTIONS].sort());
  });
  for (const word of AUTH_PROJECTIONS) {
    it(`?auth=${word} → one boundary line with its sentence, the word as data, no control`, () => {
      const boundary = authBoundaryFrom(`?auth=${word}`);
      expect(boundary).toEqual({ kind: "boundary", projection: word, message: AUTH_BOUNDARY_MESSAGES[word] });
      const html = render(`?auth=${word}`);
      expect(html).toMatch(/^<p role="alert" id="auth-boundary" data-testid="auth-boundary" class="read-boundary access-auth-boundary" data-projection="/);
      expect(html).toContain(`data-projection="${word}"`);
      expect(html).toContain(`<span class="t-boundary">${AUTH_BOUNDARY_MESSAGES[word]}</span>`);
      expect(html).not.toMatch(/<a |<button|<form|<input/);
      expect((html.match(/<p /g) ?? []).length).toBe(1);
    });
  }
  it("every sentence names a non-success and the absence of an access relation; none claims success, authority or a role", () => {
    for (const message of Object.values(AUTH_BOUNDARY_MESSAGES)) {
      expect(message).toMatch(/No access relation was established\.$/);
      expect(message).not.toMatch(/success|signed in|logged in|welcome|authori|role|permission|denied|forbidden|account (was )?created|link/i);
    }
  });
});

describe("proofs 2–5: missing, unknown, malformed and conflicting projections render nothing", () => {
  const nothing: ReadonlyArray<[string, string]> = [
    ["missing (empty search)", ""],
    ["missing (other params only)", "?next=%2F&link=ok"],
    ["link word on the auth key (LOGIN != LINK)", "?auth=ok"],
    ["link word already_linked", "?auth=already_linked"],
    ["unknown word", "?auth=success"],
    ["case variant", "?auth=FAILED"],
    ["trailing space", "?auth=failed%20"],
    ["embedded NUL", "?auth=failed%00"],
    ["script injection", "?auth=%3Cscript%3Ealert(1)%3C%2Fscript%3E"],
    ["empty value", "?auth="],
    ["duplicate identical", "?auth=failed&auth=failed"],
    ["conflicting values", "?auth=failed&auth=cancelled"],
    ["malformed key", "?auth%00=failed"],
    ["key with suffix", "?auth2=failed"],
  ];
  for (const [name, search] of nothing) {
    it(`${name} → none, nothing rendered`, () => {
      expect(authBoundaryFrom(search)).toEqual(NO_AUTH_BOUNDARY);
      expect(render(search)).toBe("");
    });
  }
  it("a URLSearchParams instance is read the same way", () => {
    expect(authBoundaryFrom(new URLSearchParams("auth=cancelled")).kind).toBe("boundary");
    expect(authBoundaryFrom(new URLSearchParams("auth=nope"))).toEqual(NO_AUTH_BOUNDARY);
  });
  it("no LINK word is ever an AUTH boundary (unless it is also an AUTH word)", () => {
    for (const word of LINK_PROJECTIONS) {
      const expected = (AUTH_PROJECTIONS as readonly string[]).includes(word) ? "boundary" : "none";
      expect(authBoundaryFrom(`?auth=${word}`).kind).toBe(expected);
    }
  });
});

describe("proofs 8–11: no synthesized success, no authority/role inference, typed vocabulary only, no linking", () => {
  it("the derivation reads the query only through readAuthProjection and never parses the query itself", () => {
    expect(DERIVATION).toMatch(/readAuthProjection\(search\)/);
    expect(DERIVATION).not.toMatch(/new URLSearchParams|\.get\(|\.getAll\(|split\(|match\(|RegExp/);
    expect(HOOK).not.toMatch(/new URLSearchParams|\.get\(|split\(|match\(/);
    expect(COMPONENT).not.toMatch(/URLSearchParams|location/);
  });
  it("no word maps to another word: unknown is none, not failed", () => {
    expect(DERIVATION).not.toMatch(/\?\?\s*["']failed["']|:\s*["']failed["']\s*[;}]/);
    expect(authBoundaryFrom("?auth=unknown_word")).toEqual(NO_AUTH_BOUNDARY);
  });
  it("no success, authority, role, link or account-creation vocabulary in the sources or markup", () => {
    for (const src of [DERIVATION, HOOK, COMPONENT]) {
      expect(src).not.toMatch(/\brole\s*[!=]==?|authority|viewer|isGovernanceRoot|isSessionController|permission/);
      expect(src).not.toMatch(/linkStart|readLinkProjection|unlinkMethod|listMethods|listSessions|logoutAll|startRecovery|createAccount/);
      expect(src).not.toMatch(/localStorage|sessionStorage|indexedDB|setTimeout|setInterval|document\.cookie|history\.(push|replace)State|router\./);
    }
    for (const word of AUTH_PROJECTIONS) {
      expect(render(`?auth=${word}`)).not.toMatch(/success|data-outcome="committed"|href=/i);
    }
  });
});

describe("proofs 6–7: local password login and the provider contact remain unchanged", () => {
  it("the page keeps the form, the F02 login call, the redirect and the provider contact; the boundary is idle-only and placed after the contact", () => {
    expect(PAGE).toMatch(/data-testid="login-email"/);
    expect(PAGE).toMatch(/data-testid="login-password"/);
    expect(PAGE).toMatch(/data-testid="login-submit"/);
    expect(PAGE).toMatch(/login\(email, password\)/);
    expect(PAGE).toMatch(/router\.replace\("\/"\)/);
    expect(PAGE).toMatch(/useProviderContact\(mountPath\("\/"\)\)/); // the mount root (CYAN_REAL_E2E_FIELD_MOUNT_01)
    expect(PAGE).toMatch(/<ProviderContact contact=\{providerContact\} \/>/);
    expect(PAGE).toMatch(/const providerBoundary = state\.kind === "idle" \? authBoundary : \{ kind: "none" as const \}/);
    expect(PAGE).toMatch(/<AuthBoundary boundary=\{providerBoundary\} \/>/);
    expect(PAGE.indexOf("<ProviderContact")).toBeLessThan(PAGE.indexOf("<AuthBoundary"));
    expect(PAGE.indexOf("<AuthBoundary")).toBeLessThan(PAGE.indexOf('data-testid="login-pending"'));
    // the core's boundary state follows the projection, never a success state
    expect(PAGE).toMatch(/providerBoundary\.kind === "boundary" \? "boundary" : "current"/);
    expect(PAGE).not.toMatch(/"success"|"authenticated"/);
  });
});
