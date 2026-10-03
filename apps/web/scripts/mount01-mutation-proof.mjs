// CYAN_REAL_E2E_FIELD_MOUNT_01 mutation proof (semantic corruptions of the mount relation); byte-identical restore.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const F = (p) => new URL(`../${p}`, import.meta.url);
const MUTATIONS = [
  { name: "M1/M9 frontend mount prefixes the API base", file: "lib/api/client.ts",
    from: 'export function apiBaseUrl(): string {\n  return process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL;',
    to: 'export function apiBaseUrl(): string {\n  return (process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL) + (process.env.NEXT_PUBLIC_FRONTEND_MOUNT ?? "");' },
  { name: "M2 review mount ignored by the build config", file: "next.config.ts",
    from: '  ...(mount === "" ? {} : { basePath: mount }),', to: '' },
  { name: "M3/M12 review mount forced into the default build", file: "next.config.ts",
    from: '  ...(mount === "" ? {} : { basePath: mount }),', to: '  basePath: "/cy-review",' },
  { name: "M4 brand asset hard-coded to the root", file: "components/field/Identity.tsx",
    from: 'src={mountPath("/brand/nquiry-logo.png")}', to: 'src="/brand/nquiry-logo.png"' },
  { name: "M5 login navigation escapes to the root CYAN (raw location write)", file: "components/LogoutButton.tsx",
    from: '        logout().then(() => router.replace("/login"));', to: '        logout().then(() => { window.location.href = "/login"; });' },
  { name: "M6 Workspaces navigation escapes to the root CYAN (raw anchor)", file: "components/field/Identity.tsx",
    from: '    <Link className="identity brand" href="/workspaces" aria-label="nquiry" data-testid="identity">',
    to: '    <a className="identity brand" href="/workspaces" aria-label="nquiry" data-testid="identity">' },
  { name: "M7 auth return target escapes the candidate mount", file: "app/login/page.tsx",
    from: '  const providerContact = useProviderContact(mountPath("/"));', to: '  const providerContact = useProviderContact("/");' },
  { name: "M8 Google callback/start moved beneath the mount", file: "lib/api/authClient.ts",
    from: '  return `${apiBaseUrl()}/auth/oidc/${encodeURIComponent(provider.providerId)}/start?${query.toString()}`;',
    to: '  return `${apiBaseUrl()}${process.env.NEXT_PUBLIC_FRONTEND_MOUNT ?? ""}/auth/oidc/${encodeURIComponent(provider.providerId)}/start?${query.toString()}`;' },
  { name: "M10 frontend mount changes authentication truth", file: "lib/field/identityProjection.ts",
    from: '  if (reads.me === null || reads.me.kind !== "ok") return NO_IDENTITY_PROJECTION;',
    to: '  if (reads.me === null || reads.me.kind !== "ok") return NO_IDENTITY_PROJECTION;\n  if (process.env.NEXT_PUBLIC_FRONTEND_MOUNT) reads = { ...reads, providers: { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" } as never] } };' },
  { name: "M11 candidate build changes provider configuration", file: "next.config.ts",
    from: '  ...(mount === "" ? {} : { basePath: mount }),', to: '  ...(mount === "" ? {} : { basePath: mount, env: { NQUIRY_AUTH_PROVIDER_MODE: "test" } }),' },
  { name: "M13 a mount beneath the API mount accepted", file: "lib/field/mount.ts",
    from: '  if (segments[0] === "api") throw new Error("NEXT_PUBLIC_FRONTEND_MOUNT must not be the API mount (FRONTEND_MOUNT != API_MOUNT)");', to: '' },
];
const sha = (b) => createHash("sha256").update(b).digest("hex");
const rows = [];
for (const m of MUTATIONS) {
  const file = F(m.file); const original = readFileSync(file); const baseline = sha(original); const text = original.toString("utf8");
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING (mutation not applied)", restored: true }); continue; }
  writeFileSync(file, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["vitest", "run", "tests/field/mount.test.tsx", "tests/lib/authClient.test.ts", "tests/field/gates.test.ts", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(file, original);
  const failed = /Tests\s+(\d+) failed/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(file)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED") || !r.restored);
console.log(`${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 ? 0 : 1);
