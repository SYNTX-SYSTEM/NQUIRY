/**
 * CYAN_REAL_E2E_FIELD_MOUNT_01 semantic falsifiers: the FRONTEND MOUNT is one CYAN-owned relation (lib/field/mount.ts);
 * the build config, the brand asset and the auth return target derive from it; the API mount, the OIDC start/callback
 * contacts, cookies, provider configuration and authentication truth never do; the default build is unchanged.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";

const WEB = join(__dirname, "..", "..");
const code = (p: string) => readFileSync(join(WEB, p), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");

async function withMount<T>(mount: string | undefined, run: () => Promise<T>): Promise<T> {
  vi.resetModules();
  if (mount === undefined) vi.stubEnv("NEXT_PUBLIC_FRONTEND_MOUNT", "");
  else vi.stubEnv("NEXT_PUBLIC_FRONTEND_MOUNT", mount);
  try {
    return await run();
  } finally {
    vi.unstubAllEnvs();
    vi.resetModules();
  }
}
afterEach(() => vi.unstubAllEnvs());

describe("the mount relation (authoritative home lib/field/mount.ts)", () => {
  it("accepts the root and a path mount; refuses malformed mounts and the API mount (FRONTEND_MOUNT != API_MOUNT)", async () => {
    const { normalizeMount } = await import("../../lib/field/mount");
    expect(normalizeMount(undefined)).toBe("");
    expect(normalizeMount("")).toBe("");
    expect(normalizeMount("/")).toBe("");
    expect(normalizeMount("/cy-review")).toBe("/cy-review");
    expect(normalizeMount("/a/b_c-d")).toBe("/a/b_c-d");
    for (const bad of ["cy-review", "/cy-review/", "//cy-review", "/cy review", "/cy%20review", "/api", "/api/x", "https://x/", "/../x", "/.hidden"]) {
      expect(() => normalizeMount(bad), bad).toThrow();
    }
  });
  it("STATE A · default build: mount is empty, mountPath is the root path, next.config carries no basePath and no other key", async () => {
    await withMount(undefined, async () => {
      const m = await import("../../lib/field/mount");
      expect(m.FRONTEND_MOUNT).toBe("");
      expect(m.mountPath("/brand/nquiry-logo.png")).toBe("/brand/nquiry-logo.png");
      expect(m.mountPath("/")).toBe("/");
      const config = (await import("../../next.config")).default;
      expect(config).toEqual({ reactStrictMode: true });
    });
  });
  it("STATE B · review build: mount /cy-review, basePath /cy-review, mountPath prefixed; nothing else in the config", async () => {
    await withMount("/cy-review", async () => {
      const m = await import("../../lib/field/mount");
      expect(m.FRONTEND_MOUNT).toBe("/cy-review");
      expect(m.mountPath("/brand/nquiry-logo.png")).toBe("/cy-review/brand/nquiry-logo.png");
      expect(m.mountPath("/")).toBe("/cy-review/");
      const config = (await import("../../next.config")).default;
      expect(config).toEqual({ reactStrictMode: true, basePath: "/cy-review" });
      expect(Object.keys(config).sort()).toEqual(["basePath", "reactStrictMode"]);
    });
  });
  it("STATE C/E · the mount never prefixes the API mount or the OIDC contacts (FALSIFIER_01, 07, 08, 09)", async () => {
    await withMount("/cy-review", async () => {
      const { apiBaseUrl } = await import("../../lib/api/client");
      const { parseProviderList, loginStartUrl, linkStartAction, listProviders } = await import("../../lib/api/authClient");
      expect(apiBaseUrl()).toBe("http://localhost:8000");
      const google = parseProviderList({ kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] }).providers[0];
      // the start is a PURPLE /auth contact; the CYAN-owned return target lives beneath the mount
      expect(loginStartUrl(google, "/cy-review/")).toBe("http://localhost:8000/auth/oidc/google/start?next=%2Fcy-review%2F");
      expect(linkStartAction(google, "/cy-review/workspaces").action).toBe("http://localhost:8000/auth/oidc/google/link/start?next=%2Fcy-review%2Fworkspaces");
      const fetchImpl = vi.fn().mockResolvedValue(new Response(JSON.stringify({ kind: "ok", providers: [] }), { headers: { "Content-Type": "application/json" } }));
      await listProviders(fetchImpl);
      expect(fetchImpl.mock.calls[0][0]).toBe("http://localhost:8000/auth/providers");
      expect(String(fetchImpl.mock.calls[0][0])).not.toContain("/cy-review");
    });
  });
});

describe("CYAN-owned locations derive from the mount (FALSIFIER_05, 08, 10)", () => {
  it("the brand asset is served beneath the mount in the review build and at the root in the default build", async () => {
    await withMount("/cy-review", async () => {
      const { Identity } = await import("../../components/field/Identity");
      const html = renderToStaticMarkup(<Identity link={false} />);
      expect(html).toContain('src="/cy-review/brand/nquiry-logo.png"');
      expect(html).toContain('srcSet="/cy-review/brand/nquiry-logo.png 1x, /cy-review/brand/nquiry-logo@2x.png 2x"');
      expect(html).not.toMatch(/src="\/brand/);
    });
    await withMount(undefined, async () => {
      const { Identity } = await import("../../components/field/Identity");
      expect(renderToStaticMarkup(<Identity link={false} />)).toContain('src="/brand/nquiry-logo.png"');
    });
  });
  it("the auth return target of the Access Field is the mount root, never a hard-coded root", () => {
    const page = code("app/login/page.tsx");
    expect(page).toMatch(/useProviderContact\(mountPath\("\/"\)\)/);
    expect(page).not.toMatch(/useProviderContact\("\/"\)/);
  });
  it("no CYAN source keeps a root-hardcoded asset or raw root navigation; routes and links go through Next (basePath-aware)", () => {
    const sources = ["app/login/page.tsx", "app/page.tsx", "app/workspaces/page.tsx", "app/workspaces/[workspaceId]/page.tsx", "components/field/Identity.tsx", "components/field/FieldFrame.tsx", "components/LogoutButton.tsx", "components/field/IdentityPanel.tsx", "components/f02/AppShell.tsx"];
    for (const file of sources) {
      const src = code(file);
      expect(src, file).not.toMatch(/src="\/|srcSet="\/|<a [^>]*href="\/|location\.(assign|href\s*=|replace)|window\.open\(/);
    }
  });
});

describe("the mount changes nothing but CYAN-owned locations (FALSIFIER_11–16)", () => {
  it("authentication, session, provider and identity modules never read the mount (SEMANTIC_ERROR_11)", () => {
    for (const file of ["lib/api/authClient.ts", "lib/api/client.ts", "lib/field/identityProjection.ts", "lib/field/useIdentityProjection.ts", "lib/field/providerContact.ts", "lib/field/useProviderContact.ts", "lib/field/authBoundary.ts", "lib/field/useAuthBoundary.ts", "components/field/IdentityProjection.tsx", "components/field/IdentityPanel.tsx", "components/field/ProviderContact.tsx", "components/field/AuthBoundary.tsx"]) {
      expect(code(file), file).not.toMatch(/mountPath|FRONTEND_MOUNT|NEXT_PUBLIC_FRONTEND_MOUNT|field\/mount/);
    }
  });
  it("the build config touches no API, provider, cookie or Google key and reads no other environment", () => {
    const config = code("next.config.ts");
    expect(config).not.toMatch(/NEXT_PUBLIC_API_BASE_URL|NQUIRY_AUTH_PROVIDER_MODE|NQUIRY_GOOGLE|COOKIE|redirect|rewrites|headers\(|env:/);
    expect(config.match(/process\.env\.[A-Z_]+/g)).toEqual(["process.env.NEXT_PUBLIC_FRONTEND_MOUNT"]);
    expect(code("lib/field/mount.ts").match(/process\.env\.[A-Z_]+/g)).toEqual(["process.env.NEXT_PUBLIC_FRONTEND_MOUNT"]);
  });
  it("identity projection semantics are mount-independent: the same reads give the same projection under both mounts", async () => {
    const reads = {
      me: { kind: "ok", userId: "7dd6e767-1111-4111-8111-111111111111" } as const,
      sessions: { kind: "ok", sessions: [{ sessionId: "aaaaaaaa-1111-4111-8111-111111111111", issuedAt: "2026-10-03T08:00:00+00:00", expiresAt: "2026-10-05T08:00:00+00:00", current: true, methodType: "GOOGLE_OIDC" as const }] } as const,
      methods: { kind: "ok", methods: [{ methodId: "dddddddd-1111-4111-8111-111111111111", methodType: "GOOGLE_OIDC" as const, status: "ACTIVE" as const, createdAt: "2026-10-03T08:00:00+00:00", lastAuthenticatedAt: null, provider: { providerId: "google", email: "person@example.test" } }] } as const,
      providers: null,
    };
    const a = await withMount(undefined, async () => (await import("../../lib/field/identityProjection")).identityProjectionFrom(reads));
    const b = await withMount("/cy-review", async () => (await import("../../lib/field/identityProjection")).identityProjectionFrom(reads));
    expect(b).toEqual(a);
    expect(a.authentication.kind === "via" && a.authentication.label).toEqual({ kind: "provider", providerId: "google", label: null });
  });
});
