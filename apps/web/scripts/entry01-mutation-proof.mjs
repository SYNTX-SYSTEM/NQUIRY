// CYAN-ENTRY-01 mutation proof over entryPath.ts / EntryPath.tsx / login page; vitest-killed; byte-identical restore.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const F = (p) => new URL(`../${p}`, import.meta.url);
const MUTATIONS = [
  { name: "M1 a provider is invented when the server listed none", file: "lib/field/entryPath.ts",
    from: '  return { providers: contact.kind === "contacts" ? contact.contacts.map((c) => c.provider) : [], operator: "HOST_OPERATOR" };',
    to: '  return { providers: contact.kind === "contacts" ? contact.contacts.map((c) => c.provider) : [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }], operator: "HOST_OPERATOR" };' },
  { name: "M2 a registration control appears in the entry", file: "components/field/EntryPath.tsx",
    from: '      <p className="muted" data-testid="entry-operator">',
    to: '      <a href="/register" className="button">Create an account</a>\n      <p className="muted" data-testid="entry-operator">' },
  { name: "M3 the entry claims that this deployment admits new identities", file: "components/field/EntryPath.tsx",
    from: 'Whether this deployment admits a new identity is decided by the\n          server when you continue; a refusal is shown here, and no identity is created.',
    to: 'Self-registration is open on this deployment: you can register with your provider account.' },
  { name: "M4 the operator entry disappears", file: "components/field/EntryPath.tsx",
    from: '      <p className="muted" data-testid="entry-operator">\n        A local password account is created by the operator of this deployment. There is no registration form.\n      </p>',
    to: '' },
  { name: "M5 LINK != LOGIN inverted (continuing attaches the provider)", file: "components/field/EntryPath.tsx",
    from: 'Continuing with a provider here does not attach it to an existing account.',
    to: 'Continuing with a provider here attaches it to your existing account.' },
  { name: "M6 the login page stops deriving the entry from the parsed contact", file: "app/login/page.tsx",
    from: '<EntryPath entry={entryPathFrom(providerContact)} />',
    to: '<EntryPath entry={{ providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }], operator: "HOST_OPERATOR" }} />' },
];
const sha = (b) => createHash("sha256").update(b).digest("hex");
const rows = [];
for (const m of MUTATIONS) {
  const file = F(m.file); const original = readFileSync(file); const baseline = sha(original); const text = original.toString("utf8");
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING", restored: true }); continue; }
  writeFileSync(file, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["vitest", "run", "tests/field/entryPath.test.tsx", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(file, original);
  rows.push({ name: m.name, result: run.status !== 0 ? "KILLED" : "SURVIVED", restored: sha(readFileSync(file)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => r.result !== "KILLED" || !r.restored);
console.log(`${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 ? 0 : 1);
