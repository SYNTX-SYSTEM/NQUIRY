// CYAN-PCPG-05 mutation proof over observation.ts / useObservation.ts / IntentObservationChamber.tsx; byte-identical restore.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const F = (p) => new URL(`../${p}`, import.meta.url);
const MUTATIONS = [
  { name: "M1 provisional governance result while observing", file: "lib/field/observation.ts", from: "    return { ...state, phase: \"observing\", failure: null };", to: "    return { ...state, phase: \"observing\", failure: null, presence: { kind: \"malformed\" } };" },
  { name: "M2 control labelled Send", file: "components/field/IntentObservationChamber.tsx", from: "            Observe\n          </button>", to: "            Send\n          </button>" },
  { name: "M3 chamber role-gated", file: "components/field/IntentObservationChamber.tsx", from: "  const [text, setText] = useState(\"\");", to: "  const role = \"Owner\";\n  if (role !== \"Owner\") return null;\n  const [text, setText] = useState(\"\");" },
  { name: "M4 supersession ignores the canonical versions", file: "lib/field/observation.ts", from: "  const superseded = state.observedVersions !== null && (state.observedVersions.session !== current.session || state.observedVersions.burst !== current.burst);", to: "  const superseded = false;" },
  { name: "M5 raw intent persisted", file: "lib/field/useObservation.ts", from: "      // no persistence: React state only (I-18, HA-PCPG-3)", to: "      localStorage.setItem(\"intent\", rawIntent);" },
];
const sha = (b) => createHash("sha256").update(b).digest("hex");
const rows = [];
for (const m of MUTATIONS) {
  const file = F(m.file); const original = readFileSync(file); const baseline = sha(original); const text = original.toString("utf8");
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING (mutation not applied)", restored: true }); continue; }
  writeFileSync(file, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["vitest", "run", "tests/field/observation.test.ts", "tests/field/intentObservationChamber.test.tsx", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(file, original);
  const failed = /(\d+) failed/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(file)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED") || !r.restored);
console.log(`${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 ? 0 : 1);
