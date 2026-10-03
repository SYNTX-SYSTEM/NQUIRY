// AUTH/CYAN-IDENTITY-01 mutation proof over identityProjection.ts / IdentityProjection.tsx; byte-identical restore.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const F = (p) => new URL(`../${p}`, import.meta.url);
const D = "lib/field/identityProjection.ts";
const MUTATIONS = [
  { name: "M1 newest session treated as current without current=true", file: D,
    from: '  const currents = reads.sessions !== null && reads.sessions.kind === "ok" ? reads.sessions.sessions.filter((s) => s.current) : [];',
    to: '  const all = reads.sessions !== null && reads.sessions.kind === "ok" ? [...reads.sessions.sessions] : [];\n  const currents = all.length === 0 ? [] : [all.reduce((a, b) => (a.issuedAt > b.issuedAt ? a : b))];' },
  { name: "M2 Google hard-coded from GOOGLE_OIDC", file: D,
    from: '          label: { kind: "provider", providerId, label: known ? known.label : null },',
    to: '          label: { kind: "provider", providerId, label: known ? known.label : method.methodType === "GOOGLE_OIDC" ? "Google" : null },' },
  { name: "M3 provider email presented as the canonical NQUIRY identity", file: "components/field/IdentityProjection.tsx",
    from: '      <Identifiers items={[{ label: "Authenticated identity", value: projection.identity.userId, testId: "identity-user-id" }]} />',
    to: '      <Identifiers items={[{ label: "Authenticated identity", value: providerAccount.kind === "email" ? providerAccount.email : projection.identity.userId, testId: "identity-user-id" }]} />' },
  { name: "M4 role inferred from authentication", file: "components/field/IdentityProjection.tsx",
    from: '              <dd>current · authenticated</dd>',
    to: '              <dd>current · authenticated · role Owner</dd>' },
  { name: "M5 authority inferred from authentication", file: "components/field/IdentityProjection.tsx",
    from: '                  {authenticationWords(authentication.label)}',
    to: '                  {authenticationWords(authentication.label)} (authority holder)' },
  { name: "M6 failed method fetch still renders via Google", file: D,
    from: '  if (session.kind === "current" && session.methodType !== null && reads.methods !== null && reads.methods.kind === "ok") {\n    const method = methodOfSession(reads.methods.methods, session.methodType);',
    to: '  if (session.kind === "current" && session.methodType !== null) {\n    const method = reads.methods !== null && reads.methods.kind === "ok" ? methodOfSession(reads.methods.methods, session.methodType) : { methodId: "", methodType: session.methodType, status: "ACTIVE", createdAt: "", lastAuthenticatedAt: null, provider: session.methodType === "LOCAL_PASSWORD" ? null : { providerId: "google", email: null } };' },
  { name: "M7 unknown methodType mapped to a friendly known value", file: "lib/api/authClient.ts",
    from: '    methodType: authClosed(rec, "methodType", path, AUTH_METHOD_TYPES),\n    status: authClosed(rec, "status", path, AUTH_METHOD_STATUSES),',
    to: '    methodType: ((AUTH_METHOD_TYPES as readonly string[]).includes(String(rec.methodType)) ? rec.methodType : "GOOGLE_OIDC") as AuthMethodType,\n    status: authClosed(rec, "status", path, AUTH_METHOD_STATUSES),' },
  { name: "M8 Google shown when LOCAL_PASSWORD is current (panel reads any linked provider method)", file: "components/field/IdentityPanel.tsx",
    from: '    via && authentication.label.kind === "provider" && providerAccount.kind === "email" && providerAccount.providerId === authentication.label.providerId\n      ? { label: authentication.label.label, email: providerAccount.email }\n      : null;',
    to: '    providerAccount.kind === "email" ? { label: "Google", email: providerAccount.email } : via && authentication.label.kind === "local" ? { label: "Google", email: "linked@example.test" } : null;' },
  { name: "M9 provider email shown when missing (placeholder)", file: "components/field/IdentityPanel.tsx",
    from: '        {account ? (\n          <span className="identity-panel-account" data-testid="identity-panel-account">',
    to: '        {account || via ? (\n          <span className="identity-panel-account" data-testid="identity-panel-account">' },
  { name: "M10 invented human display name", file: "components/field/IdentityPanel.tsx",
    from: '        <span className="identity-panel-eyebrow">{via ? "Signed in with" : "Authenticated"}</span>',
    to: '        <span className="identity-panel-eyebrow">Ottavio Braun · {via ? "Signed in with" : "Authenticated"}</span>' },
  { name: "M11 Logout disconnected from the existing legitimate effect", file: "components/field/IdentityPanel.tsx",
    from: '      <LogoutButton />',
    to: '      <button type="button" className="button secondary" data-testid="logout-button">Log out</button>' },
  { name: "M12 panel email presented as the identity (no account label)", file: "components/field/IdentityPanel.tsx",
    from: '            <span className="identity-panel-account-label">{account.label === null ? "Provider" : account.label} account</span>',
    to: '' },
  { name: "M13 unknown methodType mapped to Local password (parser)", file: "lib/api/authClient.ts",
    from: '    methodType: authClosed(rec, "methodType", path, AUTH_METHOD_TYPES),\n    status: authClosed(rec, "status", path, AUTH_METHOD_STATUSES),',
    to: '    methodType: ((AUTH_METHOD_TYPES as readonly string[]).includes(String(rec.methodType)) ? rec.methodType : "LOCAL_PASSWORD") as AuthMethodType,\n    status: authClosed(rec, "status", path, AUTH_METHOD_STATUSES),' },
  { name: "M14 frontend caches the previous current method across transitions", file: "lib/field/useIdentityProjection.ts", browser: "RECONSTRUCTION",
    from: 'export function useIdentityProjection(userId: string | null): IdentityProjection {\n  const [reads, setReads] = useState<Reads>(PENDING);',
    to: 'let CACHE: Reads | null = null;\nexport function useIdentityProjection(userId: string | null): IdentityProjection {\n  const [reads, setReadsRaw] = useState<Reads>(CACHE ?? PENDING);\n  const setReads = (r: Reads) => { if (CACHE === null) { CACHE = r; setReadsRaw(r); } };' },
  { name: "M15 available Google provider determines the current authentication", file: "lib/field/identityProjection.ts",
    from: '  const currents = reads.sessions !== null && reads.sessions.kind === "ok" ? reads.sessions.sessions.filter((s) => s.current) : [];',
    to: '  const googleAvailable = reads.providers !== null && reads.providers.kind === "ok" && reads.providers.providers.some((p) => p.providerId === "google");\n  const currents = reads.sessions !== null && reads.sessions.kind === "ok" ? reads.sessions.sessions.filter((s) => s.current).map((s) => (googleAvailable ? { ...s, methodType: "GOOGLE_OIDC" as const } : s)) : [];' },
  { name: "M16 provider email forces the Google projection", file: "lib/field/identityProjection.ts",
    from: '    const method = methodOfSession(reads.methods.methods, session.methodType);',
    to: '    const withEmail = reads.methods.methods.find((m) => m.provider !== null && m.provider.email !== null && m.status === "ACTIVE");\n    const method = withEmail ?? methodOfSession(reads.methods.methods, session.methodType);' },
];
const sha = (b) => createHash("sha256").update(b).digest("hex");
const rows = [];
for (const m of MUTATIONS) {
  const file = F(m.file); const original = readFileSync(file); const baseline = sha(original); const text = original.toString("utf8");
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING (mutation not applied)", restored: true }); continue; }
  writeFileSync(file, text.replace(m.from, m.to));
  const run = m.browser
    ? spawnSync("npx", ["playwright", "test", "-c", "playwright.sf01.config.ts", "tests/e2e/cy08-identity.spec.ts", "--project=desktop", "--grep", m.browser, "--output=/tmp/pw-mutation", "--reporter=line"], { encoding: "utf8" })
    : spawnSync("npx", ["vitest", "run", "tests/field/identityProjection.test.tsx", "tests/lib/authClient.test.ts", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(file, original);
  const failed = (m.browser ? /(\d+) failed/ : /Tests\s+(\d+) failed/).exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(file)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED") || !r.restored);
console.log(`${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 ? 0 : 1);
