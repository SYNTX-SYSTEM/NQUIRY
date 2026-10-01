// CYAN-PCPG-03 mutation proof over lib/field/pcpgAttachment.ts; byte-identical restore checked by sha256.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const FILE = new URL("../lib/field/pcpgAttachment.ts", import.meta.url);
const MUTATIONS = [
  { name: "M1 UNKNOWN / UNPLACED guessed into QUESTION", from: '? (value as PresentationCategory) : "UNPLACED";', to: '? (value as PresentationCategory) : "QUESTION";' },
  { name: "M2 AUTHORITY forced into a single exclusive target", from: 'BOUNDARY_AREA: ["boundary-marks", "authority-chamber"],', to: 'BOUNDARY_AREA: ["authority-chamber"],' },
  { name: "M3 multiple categories collapsed to one winner", from: "  const attachments = attachmentsOf(cats);\n  return normalize(", to: "  const attachments = attachmentsOf(cats).slice(0, 1);\n  return normalize(" },
  { name: "M4 attachment mapping mutating capability", from: "  return {\n    presentation,\n    deltas,", to: "  const current = presentation.aggregates.current;\n  if (current) (current.capability as { canSend: boolean | null }).canSend = false;\n  return {\n    presentation,\n    deltas," },
  { name: "M5 attachment mapping creating SEND-related state", from: "    structurallyAbsent: PRESENTATION_ATTACHMENTS.filter((a) => absent.has(a)),\n  };", to: '    structurallyAbsent: PRESENTATION_ATTACHMENTS.filter((a) => absent.has(a)),\n    sendGate: "MATERIALIZED",\n  } as never;' },
];
const original = readFileSync(FILE);
const sha = (b) => createHash("sha256").update(b).digest("hex");
const baseline = sha(original);
const rows = [];
for (const m of MUTATIONS) {
  const text = original.toString("utf8");
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING (mutation not applied)", restored: true }); continue; }
  writeFileSync(FILE, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["vitest", "run", "tests/field/pcpgAttachment.test.ts", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(FILE, original);
  const failed = /(\d+) failed/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(FILE)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED"));
console.log(`baseline sha256 ${baseline.slice(0, 16)}; final sha256 ${sha(readFileSync(FILE)).slice(0, 16)}; ${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 && sha(readFileSync(FILE)) === baseline ? 0 : 1);
