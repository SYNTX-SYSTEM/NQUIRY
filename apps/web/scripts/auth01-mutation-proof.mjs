// AUTH/CYAN-01 mutation proof over lib/api/authClient.ts; byte-identical restore.
// Each mutation is one way the typed contract could silently stop failing closed.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const F = (p) => new URL(`../${p}`, import.meta.url);
const FILE = "lib/api/authClient.ts";
const MUTATIONS = [
  { name: "M1 proofClass widened to any string",
    from: '    proofClass: authClosed(rec, "proofClass", path, PROOF_CLASSES),',
    to: '    proofClass: authStr(rec, "proofClass", path) as ProofClass,' },
  { name: "M2 unknown provider-list kind accepted",
    from: '  if (rec.kind !== "ok") failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)} (the provider list has one shape)`);',
    to: '  void rec.kind;' },
  { name: "M3 unsafe next target forwarded",
    from: '  if (!isLocalNextTarget(candidate)) throw new UnsafeNextTarget();',
    to: '  if (typeof candidate !== "string") throw new UnsafeNextTarget();' },
  { name: "M4 hard-coded Google availability",
    from: '  const provider = availableProvider(list, "google");\n  if (provider === null) return { kind: "unavailable" };',
    to: '  const provider = availableProvider(list, "google") ?? ({ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER", [PARSED]: true } as ProviderSummary);\n  if (provider === null) return { kind: "unavailable" };' },
  { name: "M5 unknown projection mapped to failed",
    from: '  return (allowed as readonly string[]).includes(value) ? { kind: "projection", projection: value as P } : { kind: "unknown" };',
    to: '  return { kind: "projection", projection: ((allowed as readonly string[]).includes(value) ? value : "failed") as P };' },
  { name: "M6 unknown fields tolerated",
    from: '    if (!expected.includes(key)) failAuth(`${path}.${key}`, "unexpected key (unknown fields never become auth truth)");',
    to: '    if (!expected.includes(key)) continue;' },
  { name: "M7 denied methods mapped to an empty ok",
    from: '    case "denied":\n      return reasonBody(rec, path, "denied", SESSION_DENIED_REASONS);\n    default:\n      failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)}`);\n  }\n}\n\nexport async function listMethods',
    to: '    case "denied":\n      return { kind: "ok", methods: [] };\n    default:\n      failAuth(`${path}.kind`, `unknown kind ${JSON.stringify(rec.kind)}`);\n  }\n}\n\nexport async function listMethods' },
  { name: "M8 forbidden (secret/subject) keys tolerated",
    from: '    if (AUTH_FORBIDDEN.has(key)) failAuth(`${path}.${key}`, "forbidden key present (a secret, token or subject never reaches the browser)");\n    if (!expected.includes(key))',
    to: '    if (!expected.includes(key))' },
  { name: "M9 unknown reason code accepted on denied",
    from: '  return { kind, reasonCode: authClosed(body, "reasonCode", path, reasons) };',
    to: '  return { kind, reasonCode: authStr(body, "reasonCode", path) as R };' },
];
const sha = (b) => createHash("sha256").update(b).digest("hex");
const file = F(FILE);
const original = readFileSync(file);
const baseline = sha(original);
const text = original.toString("utf8");
const rows = [];
for (const m of MUTATIONS) {
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING (mutation not applied)", restored: true }); continue; }
  writeFileSync(file, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["vitest", "run", "tests/lib/authClient.test.ts", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(file, original);
  const failed = /Tests\s+(\d+) failed/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(file)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED") || !r.restored);
console.log(`${rows.length - survived.length}/${rows.length} mutations killed; baseline sha256 ${baseline}`);
process.exit(survived.length === 0 ? 0 : 1);
