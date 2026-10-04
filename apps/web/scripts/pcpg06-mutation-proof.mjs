// CYAN-PCPG-06 mutation proof over pcpgRendering.ts / GovernanceAttachment.tsx / GovernancePanel.tsx / page; byte-identical restore.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
const F = (p) => new URL(`../${p}`, import.meta.url);
const D = "lib/field/pcpgRendering.ts";
const MUTATIONS = [
  { name: "M1 INDETERMINATE rendered as denied", file: D, from: '  INDETERMINATE: "indeterminate",', to: '  INDETERMINATE: "denied",' },
  { name: "M2 null target rendered as out of scope", file: D, from: '  if (target === null) return "unresolved";', to: '  if (target === null) return "out of scope";' },
  { name: "M3 marker renders without an observation (fail open)", file: "components/field/GovernanceAttachment.tsx", from: '  if (!rendering) return null;', to: '  if (!rendering) rendering = { area: "derived-chamber", words: "the derived field chamber", deltas: [], firstBrokenHere: false, humanAuthorityHere: false, providerNotExecutable: false, superseded: false, summary: "0 crossed steps placed here" } as never;' },
  { name: "M4 Send presented as disabled", file: D, from: 'export const SEND_NOT_MATERIALIZED = "Send not materialized" as const;', to: 'export const SEND_NOT_MATERIALIZED = "Send disabled" as const;' },
  { name: "M5 marker grows a control", file: "components/field/GovernanceAttachment.tsx", from: '      <ul className="attachment-deltas">', to: '      <button type="button">Approve</button>\n      <ul className="attachment-deltas">' },
  { name: "M6 placement guessed from the clause text", file: D, from: '    const here = attached.deltas.filter((a) => a.targets.some((x) => x.area === t.area))', to: '    const here = attached.deltas.filter((a) => a.targets.some((x) => x.area === t.area) || (t.area === "derived-chamber" && (deltaById.get(a.deltaId)?.sourceClause ?? "").toLowerCase().includes("analyse")) || (t.area === "question-set" && (deltaById.get(a.deltaId)?.sourceClause ?? "").includes("question")))' },
  { name: "M7 supersession ignored by the rendering", file: D, from: '  const superseded = presence.kind === "observation" && presence.supersededByObjectChange;', to: '  const superseded = false;' },
  { name: "M8 HAR becomes an approval control in the panel", file: "components/field/GovernancePanel.tsx", from: '                  <dd data-testid="boundary-har">', to: '                  <dd data-testid="boundary-har"><button type="button">Approve</button>' },
  { name: "M9 unknown operation given a friendly name", file: D, from: '  return operation === null ? "Unknown operation" : operation;', to: '  return operation === null ? "Question analysis" : operation;' },
  { name: "M10 boundary card from the first delta instead of the broken one", file: D, from: '  const fbr = chain.firstBrokenRelation;\n  if (fbr === null) return null;', to: '  const fbr = chain.firstBrokenRelation ?? (chain.maximumLegitimateTransition[0] ? { predecessor: null, broken: chain.maximumLegitimateTransition[0] } : null);\n  if (fbr === null) return null;\n  if (chain.firstBrokenRelation === null && chain.nextValidTransition) return { whatStopped: "", requestedIn: "", why: "", after: "", humanAuthorityRequired: [], placedAt: [], partial: false };' },
  { name: "M11 page bypasses the derivation for the derived chamber", file: "app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx", from: '              <GovernanceAttachment rendering={rendering.byArea["derived-chamber"]} />', to: '              <GovernanceAttachment rendering={rendering.byArea["derived-chamber"] ?? rendering.byArea["question-set"]} />' },
  { name: "M12 FBR flag taken from the result instead of the chain", file: D, from: 'isFirstBroken: delta.deltaId === brokenId,', to: 'isFirstBroken: delta.result !== "ALLOWED" && delta.result !== "INDETERMINATE",' },
];
const sha = (b) => createHash("sha256").update(b).digest("hex");
const rows = [];
for (const m of MUTATIONS) {
  const file = F(m.file); const original = readFileSync(file); const baseline = sha(original); const text = original.toString("utf8");
  if (!text.includes(m.from)) { rows.push({ name: m.name, result: "ANCHOR MISSING (mutation not applied)", restored: true }); continue; }
  writeFileSync(file, text.replace(m.from, m.to));
  const run = spawnSync("npx", ["vitest", "run", "tests/field/pcpgRendering.test.tsx", "tests/field/pcpgAttachment.test.ts", "--reporter=dot"], { encoding: "utf8" });
  writeFileSync(file, original);
  const failed = /Tests\s+(\d+) failed/.exec(run.stdout + run.stderr)?.[1] ?? "0";
  rows.push({ name: m.name, result: run.status !== 0 ? `KILLED (${failed} test(s) failed)` : "SURVIVED", restored: sha(readFileSync(file)) === baseline });
}
for (const r of rows) console.log(`${r.name}: ${r.result}; restored byte-identical: ${r.restored}`);
const survived = rows.filter((r) => !String(r.result).startsWith("KILLED") || !r.restored);
console.log(`${rows.length - survived.length}/${rows.length} mutations killed`);
process.exit(survived.length === 0 ? 0 : 1);
