// CYAN-RAIL-01 mutation proof over the rail rule in globals.css; browser-killed (desktop widths); byte-identical restore.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const FILE = new URL("../app/globals.css", import.meta.url);
const MUTATIONS = [
  { name: "R1 the fixed 22ch reservation returns on the current station", from: '    flex-shrink: 0.001;\n    flex-basis: auto;\n    width: max-content;\n    min-width: 0;', to: '    flex-shrink: 1;\n    flex-basis: auto;\n    width: auto;\n    min-width: min(100%, calc(22ch + 36px));' },
  { name: "R2 established stations cannot compress below 9ch", from: '  .trace li {\n    min-width: calc(1ch + 42px);\n  }', to: '  .trace li {\n    min-width: 9ch;\n  }' },
  { name: "R3 the narrow-container tightening is removed", from: '@container (max-width: 560px) {', to: '@container (max-width: 1px) {' },
  { name: "R4 the current label's box no longer carries its text advance (sub-pixel ellipsis on a complete word)", from: '    flex: none;\n    width: max-content;\n    max-width: calc(100% + 1px);', to: '    flex: 0 1 auto;\n    width: auto;\n    max-width: 100%;' },
];
const sha = (b) => createHash("sha256").update(b).digest("hex");
const original = readFileSync(FILE); const baseline = sha(original); const text = original.toString("utf8");
const rows = [];
for (const m of MUTATIONS) {
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING", restored: true }); continue; }
  writeFileSync(FILE, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["playwright", "test", "-c", "playwright.sf01.config.ts", "tests/e2e/cy10-rail.spec.ts", "--project=desktop", "--output=/tmp/pw-rail-mutation", "--reporter=line"], { encoding: "utf8" });
  writeFileSync(FILE, original);
  const failed = /(\d+) failed/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(FILE)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED") || !r.restored);
console.log(`${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 ? 0 : 1);
