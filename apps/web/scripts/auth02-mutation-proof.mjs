// AUTH/CYAN-02 mutation proof over providerContact.ts / useProviderContact.ts / ProviderContact.tsx / login page;
// byte-identical restore. Each mutation is one way the contact could stop being "only from parsed provider truth".
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const F = (p) => new URL(`../${p}`, import.meta.url);
const MUTATIONS = [
  { name: "M1 hard-coded availability (contact without a parsed provider)", file: "lib/field/providerContact.ts",
    from: '  if (start.kind !== "available") return NO_PROVIDER_CONTACT;\n  return { kind: "contact", provider: start.provider, url: start.url };',
    to: '  if (start.kind !== "available") return { kind: "contact", provider: { providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }, url: "http://localhost:8000/auth/oidc/google/start?next=%2F" };\n  return { kind: "contact", provider: start.provider, url: start.url };' },
  { name: "M2 fail-open discovery (a thrown parse becomes a contact)", file: "lib/field/providerContact.ts",
    from: '  } catch {\n    return NO_PROVIDER_CONTACT;\n  }',
    to: '  } catch {\n    return { kind: "contact", provider: { providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }, url: "http://localhost:8000/auth/oidc/google/start?next=%2F" };\n  }' },
  { name: "M3 fail-open rendering (the component renders for none)", file: "components/field/ProviderContact.tsx",
    from: '  if (contact.kind !== "contact") return null;\n  const { provider, url } = contact;',
    to: '  const { provider, url } = contact.kind === "contact" ? contact : { provider: { providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }, url: "http://localhost:8000/auth/oidc/google/start?next=%2F" };' },
  { name: "M4 wrong start URL (link route instead of the typed login start)", file: "lib/field/providerContact.ts",
    from: '  return { kind: "contact", provider: start.provider, url: start.url };',
    to: '  return { kind: "contact", provider: start.provider, url: start.url.replace("/start", "/link/start") };' },
  { name: "M5 unsafe next forwarded by the derivation", file: "lib/field/providerContact.ts",
    from: '    return providerContactFrom(await listProviders(fetchImpl), next);',
    to: '    const list = await listProviders(fetchImpl); const p = list.providers.find((x) => x.providerId === "google"); return p ? { kind: "contact", provider: p, url: `http://localhost:8000/auth/oidc/google/start?next=${encodeURIComponent(next)}` } : providerContactFrom(list, next);' },
  { name: "M6 the login page stops consuming the parsed contact", file: "app/login/page.tsx",
    from: '  const providerContact = useProviderContact("/");',
    to: '  const providerContact = { kind: "contact", provider: { providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }, url: "http://localhost:8000/auth/oidc/google/start?next=%2F" } as unknown as ReturnType<typeof useProviderContact>; void useProviderContact;' },
];
const sha = (b) => createHash("sha256").update(b).digest("hex");
const rows = [];
for (const m of MUTATIONS) {
  const file = F(m.file); const original = readFileSync(file); const baseline = sha(original); const text = original.toString("utf8");
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING (mutation not applied)", restored: true }); continue; }
  writeFileSync(file, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["vitest", "run", "tests/field/providerContact.test.tsx", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(file, original);
  const failed = /Tests\s+(\d+) failed/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(file)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED") || !r.restored);
console.log(`${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 ? 0 : 1);
