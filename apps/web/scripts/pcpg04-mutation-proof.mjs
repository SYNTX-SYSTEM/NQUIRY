// CYAN-PCPG-04 mutation proof over components/field/GovernanceMembrane.tsx; byte-identical restore checked by sha256.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const FILE = new URL("../components/field/GovernanceMembrane.tsx", import.meta.url);
const MUTATIONS = [
  { name: "M1 unavailable rendered as denied", from: "  const words = presentation.words;", to: '  const words = presentation.label === "GOVERNANCE_UNAVAILABLE" ? "Denied" : presentation.words;' },
  { name: "M2 Human Authority shown without legitimate derived input", from: '  const humanAuthority = presentation.label === "HUMAN_AUTHORITY_REQUIRED";', to: "  const humanAuthority = true;" },
  { name: "M3 canSend creating a send button", from: "      {/* no control: PCPG-R12/1 has no SEND relation */}", to: '      {current?.capability.canSend ? <button type="button">Send</button> : null}' },
  { name: "M4 component reading raw PCPG-R12/1 instead of presentationOf", from: 'import type { MembraneLabel, ObservationPresentation } from "../../lib/field/pcpgPresentation";', to: 'import type { MembraneLabel, ObservationPresentation } from "../../lib/field/pcpgPresentation";\nimport { parseGovernanceObservation } from "../../lib/api/pcpgClient";\nvoid parseGovernanceObservation;' },
  { name: "M5 membrane label precedence altered (superseded demoted)", from: "  const label = presentation.label;", to: '  const label = presentation.aggregates.observation === "superseded" ? "OBSERVED" : presentation.label;' },
];
const original = readFileSync(FILE);
const sha = (b) => createHash("sha256").update(b).digest("hex");
const baseline = sha(original);
const rows = [];
for (const m of MUTATIONS) {
  const text = original.toString("utf8");
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING (mutation not applied)", restored: true }); continue; }
  writeFileSync(FILE, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["vitest", "run", "tests/field/governanceMembrane.test.tsx", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(FILE, original);
  const failed = /(\d+) failed/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(FILE)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED"));
console.log(`baseline sha256 ${baseline.slice(0, 16)}; final sha256 ${sha(readFileSync(FILE)).slice(0, 16)}; ${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 && sha(readFileSync(FILE)) === baseline ? 0 : 1);
