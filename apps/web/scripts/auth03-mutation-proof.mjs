// AUTH/CYAN-03 mutation proof over authBoundary.ts / AuthBoundary.tsx / login page; byte-identical restore.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const F = (p) => new URL(`../${p}`, import.meta.url);
const MUTATIONS = [
  { name: "M1 unknown → visible (unknown word presented as failed)", file: "lib/field/authBoundary.ts",
    from: '  if (reading.kind !== "projection") return NO_AUTH_BOUNDARY;',
    to: '  if (reading.kind === "none") return NO_AUTH_BOUNDARY;\n  if (reading.kind === "unknown") return { kind: "boundary", projection: "failed", message: AUTH_BOUNDARY_MESSAGES.failed };' },
  { name: "M2 failed → success (a success sentence synthesized)", file: "lib/field/authBoundary.ts",
    from: '  failed: "The provider login could not be completed. No access relation was established.",',
    to: '  failed: "You are signed in with the provider. Welcome back.",' },
  { name: "M3 malformed/missing → visible (component renders for none)", file: "components/field/AuthBoundary.tsx",
    from: '  if (boundary.kind !== "boundary") return null;\n  return (',
    to: '  const shown = boundary.kind === "boundary" ? boundary : { kind: "boundary", projection: "failed", message: "The provider login could not be completed. No access relation was established." };\n  boundary = shown;\n  return (' },
  { name: "M4 bypass of the typed vocabulary (own query parsing)", file: "lib/field/authBoundary.ts",
    from: '  const reading = readAuthProjection(search);\n  if (reading.kind !== "projection") return NO_AUTH_BOUNDARY;\n  return { kind: "boundary", projection: reading.projection, message: AUTH_BOUNDARY_MESSAGES[reading.projection] };',
    to: '  const raw = new URLSearchParams(search).get("auth");\n  if (raw === null) return NO_AUTH_BOUNDARY;\n  const projection = raw as AuthProjection;\n  return { kind: "boundary", projection, message: AUTH_BOUNDARY_MESSAGES[projection] ?? "The provider login could not be completed. No access relation was established." };' },
  { name: "M5 page presents the boundary while a local request is in flight", file: "app/login/page.tsx",
    from: '  const providerBoundary = state.kind === "idle" ? authBoundary : { kind: "none" as const };',
    to: '  const providerBoundary = authBoundary;' },
  { name: "M6 page makes the core a success state for a projection", file: "app/login/page.tsx",
    from: 'providerBoundary.kind === "boundary" ? "boundary" : "current"',
    to: 'providerBoundary.kind === "boundary" ? "success" : "current"' },
];
const sha = (b) => createHash("sha256").update(b).digest("hex");
const rows = [];
for (const m of MUTATIONS) {
  const file = F(m.file); const original = readFileSync(file); const baseline = sha(original); const text = original.toString("utf8");
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING (mutation not applied)", restored: true }); continue; }
  writeFileSync(file, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["vitest", "run", "tests/field/authBoundary.test.tsx", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(file, original);
  const failed = /Tests\s+(\d+) failed/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(file)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED") || !r.restored);
console.log(`${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 ? 0 : 1);
