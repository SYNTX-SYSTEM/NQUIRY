// CYAN-PCPG-02 mutation proof: each narrow mutation of lib/field/pcpgPresentation.ts must make the derivation suite
// fail; the production file is restored byte-identical (sha256-checked) after every mutation.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const FILE = new URL("../lib/field/pcpgPresentation.ts", import.meta.url);
const MUTATIONS = [
  { name: "M1 UNKNOWN operation guessed into a category", from: 'if (cats.size === 0) cats.add("UNPLACED");', to: 'if (cats.size === 0) cats.add("QUESTION");' },
  { name: "M2 canSend treated as SEND authority", from: "send: current ? sendStatement(current.contract) : null,", to: 'send: current ? (current.capability.canSend ? ({ text: "Send allowed", keyedTo: "PCPG-R12/1", reason: "canSend" } as never) : sendStatement(current.contract)) : null,' },
  { name: "M3 null proof ceiling promoted to GOVERNED", from: "return { label: PROOF_CEILING_LABEL, value: value ?? null, words };", to: 'return { label: PROOF_CEILING_LABEL, value: value ?? "GOVERNED", words: value === null ? "governed" : words };' },
  { name: "M4 unavailable treated as a boundary / denial", from: 'if (o.kind === "unavailable") return "GOVERNANCE_UNAVAILABLE";', to: 'if (o.kind === "unavailable") return "BOUNDARY_REACHED";' },
  { name: "M5 Human Authority label without HAR / authority-boundary input", from: "return fbrIsAuthority || o.chain.humanAuthorityRequired.length > 0;", to: "return fbrIsAuthority || o.chain.humanAuthorityRequired.length >= 0;" },
];
const original = readFileSync(FILE);
const sha = (b) => createHash("sha256").update(b).digest("hex");
const baseline = sha(original);
const rows = [];
for (const m of MUTATIONS) {
  const text = original.toString("utf8");
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING (mutation not applied)", restored: true }); continue; }
  writeFileSync(FILE, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["vitest", "run", "tests/field/pcpgPresentation.test.ts", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(FILE, original);
  const restored = sha(readFileSync(FILE)) === baseline;
  const failed = /(\d+) failed/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED"));
console.log(`baseline sha256 ${baseline.slice(0, 16)}; final sha256 ${sha(readFileSync(FILE)).slice(0, 16)}; ${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 && sha(readFileSync(FILE)) === baseline ? 0 : 1);
