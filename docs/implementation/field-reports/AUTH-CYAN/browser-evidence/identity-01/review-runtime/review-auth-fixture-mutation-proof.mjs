// Mutation proof over the review-runtime fixture (runtime-only); byte-identical restore.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const FILE = new URL("./review-auth-fixture.mjs", import.meta.url);
const MUTATIONS = [
  { name: "R1 LOCAL login still produces a GOOGLE_OIDC current session", from: 'if (state === "local") return { kind: "ok", sessions: [{ ...local, current: true }] };', to: 'if (state === "local") return { kind: "ok", sessions: [local, { ...google, current: true }] };' },
  { name: "R2 GOOGLE review state produces LOCAL_PASSWORD", from: 'if (state === "google") return { kind: "ok", sessions: [local, { ...google, current: true }] };', to: 'if (state === "google") return { kind: "ok", sessions: [{ ...local, current: true }, google] };' },
  { name: "R3 unknown transition maps to Google", from: 'return { kind: "ok", sessions: [{ sessionId: S_UNKNOWN, issuedAt: "2026-10-03T18:00:00+00:00", expiresAt: "2026-10-05T18:00:00+00:00", current: true, methodType: null }] };', to: 'return { kind: "ok", sessions: [{ ...google, current: true }] };' },
  { name: "R4 unknown transition maps to Local password", from: 'current: true, methodType: null }] };', to: 'current: true, methodType: "LOCAL_PASSWORD" }] };' },
  { name: "R5 newest issuedAt decides the current session", from: 'if (state === "local") return { kind: "ok", sessions: [{ ...local, current: true }] };', to: 'if (state === "local") { const all = [local, google]; const n = all.reduce((a, b) => (a.issuedAt > b.issuedAt ? a : b)); return { kind: "ok", sessions: all.map((s) => ({ ...s, current: s === n })) }; }' },
  { name: "R6 a bogus cookie value is accepted as a state", from: 'return m && STATES.includes(m[1]) ? m[1] : null;', to: 'return m ? (m[1] === "local" ? "local" : "google") : null;' },
  { name: "R7 linked Google method forces the google state", from: 'return m && STATES.includes(m[1]) ? m[1] : null;', to: 'return "google";' },
];
const sha = (b) => createHash("sha256").update(b).digest("hex");
const original = readFileSync(FILE); const baseline = sha(original); const text = original.toString("utf8");
const rows = [];
for (const m of MUTATIONS) {
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING", restored: true }); continue; }
  writeFileSync(FILE, text.replace(m.from, m.to));
  const run = spawnSync("node", ["--test", "review-auth-fixture.test.mjs"], { encoding: "utf8", cwd: new URL(".", import.meta.url).pathname });
  writeFileSync(FILE, original);
  const failed = /# fail (\d+)/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(FILE)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED") || !r.restored);
console.log(`${rows.length - survived.length}/${rows.length} mutations killed; baseline sha256 ${baseline}`);
process.exit(survived.length === 0 ? 0 : 1);
