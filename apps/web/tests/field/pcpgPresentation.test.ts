/**
 * CYAN-PCPG-02 falsifiers 1–25 (Architecture 27 v4 §06, §07.4, §08.2, §11.4, §12.1, §21; commit b0a5101).
 * Every input is a PCPG-R12/1 wire sample passed through the CYAN-PCPG-01 parser first (integration: nothing reaches
 * a derivation that the parser did not accept), then derived by pure functions.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { MalformedProjection, parseGovernanceObservation, type DeltaWire, type GovernanceObservation } from "../../lib/api/pcpgClient";
import {
  MEMBRANE_LABELS,
  MEMBRANE_WORDS,
  NOT_MATERIALIZED,
  PRESENTATION_ATTACHMENT_MAP,
  PRESENTATION_CATEGORIES,
  PROOF_CEILING_LABEL,
  attachmentsOf,
  categoriesOf,
  membraneLabel,
  presentationAggregates,
  presentationOf,
  proofCeilingPresentation,
  sendStatement,
  type ObservationPresence,
} from "../../lib/field/pcpgPresentation";

const D = (over: Partial<Record<keyof DeltaWire, unknown>> = {}) => ({
  deltaId: "d-0",
  operation: "REQUEST_QUESTION_ANALYSIS",
  executionClass: "PROVIDER_COMPUTATION",
  target: null,
  sourceClause: "Analyse the questions",
  span: [0, 21],
  currentState: "QUESTION_CAPTURE",
  result: "INDETERMINATE",
  reasonCode: "DATA_GOVERNANCE_NOT_MATERIALIZED",
  flags: [],
  sessionProofCeiling: "GOVERNED",
  ...over,
});
const HUMAN = (over: Record<string, unknown> = {}) => D({ deltaId: "d-1", operation: "SELECT_PRIMARY_QUESTION", executionClass: "HUMAN_COMMAND", sourceClause: "pick the primary question", span: [23, 48], result: "STATE_BOUNDARY", reasonCode: "SESSION_NOT_IN_QUESTION_SELECTION", ...over });
function wire(over: Record<string, unknown> = {}, chainOver: Record<string, unknown> = {}, capOver: Record<string, unknown> = {}) {
  return {
    kind: "current",
    contract: "PCPG-R12/1",
    basis: { rawIntentDigestSha256: "ab".repeat(32), derivationTime: "2026-10-01T11:17:00+00:00" },
    semanticObservation: { ruleSetVersion: "26/2026-09-29", clauses: ["Analyse the questions"], actions: [], unknownRelations: [], relationsTouched: ["REQUEST_QUESTION_ANALYSIS"], declaredPurpose: null, semanticPurpose: null, purposeAlignment: null, semanticDrift: false },
    deltas: [D()],
    chain: { firstBrokenRelation: null, maximumLegitimateTransition: [], nextValidTransition: null, humanAuthorityRequired: [], partial: false, ...chainOver },
    capability: { governanceAdmissible: false, governanceAdmissibleReasons: ["MLT_EMPTY"], providerExecutable: false, providerExecutableReasons: ["NO_ELIGIBLE_PROVIDER_ROUTE"], canSend: false, ...capOver },
    composedProofCeiling: null,
    ...over,
  };
}
const parsed = (w: unknown): GovernanceObservation => parseGovernanceObservation(w);
const obs = (w: unknown, superseded = false): ObservationPresence => ({ kind: "observation", observation: parsed(w), supersededByObjectChange: superseded });
const NONE: ObservationPresence = { kind: "none" };
const MALFORMED: ObservationPresence = { kind: "malformed" };
const UNAVAILABLE = obs({ kind: "unavailable", reasonCode: "PROJECTION_INCOMPLETE" });
const deepFreeze = <T,>(v: T): T => {
  if (v && typeof v === "object") {
    Object.freeze(v);
    for (const k of Object.keys(v as object)) deepFreeze((v as Record<string, unknown>)[k]);
  }
  return v;
};

describe("determinism and purity (falsifiers 1, 24)", () => {
  it("1. the same PCPG-R12/1 input always gives identical derivation output, and the input is not mutated", () => {
    const w = wire({ deltas: [D(), HUMAN()] }, { firstBrokenRelation: { predecessor: D(), broken: HUMAN() }, partial: true, humanAuthorityRequired: [{ deltaId: "d-1", result: "STATE_BOUNDARY", reasonCode: "X" }] });
    const input = deepFreeze(obs(w));
    const snapshot = JSON.stringify(input);
    const a = presentationOf(input);
    const b = presentationOf(input);
    expect(a).toEqual(b);
    expect(JSON.stringify(a)).toBe(JSON.stringify(b));
    expect(JSON.stringify(input)).toBe(snapshot);
    expect(presentationOf(obs(wire()))).toEqual(presentationOf(obs(wire())));
  });
  it("24. every label and aggregate is a function of the parsed contract alone: no clock, no network, no storage, no role", () => {
    const src = readFileSync(join(__dirname, "..", "..", "lib", "field", "pcpgPresentation.ts"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
    expect(src).not.toMatch(/Date\.now|new Date|setTimeout|setInterval|fetch\(|localStorage|sessionStorage|document\.|window\.|Math\.random/);
    expect(src).not.toMatch(/\brole\b|viewer\.|isGovernanceRoot|isSessionController|\/auth\/me/);
    expect(src).not.toMatch(/import .* from "\.\.\/api\/(client|inquiryClient|decisionClient)"/);
  });
});

describe("membrane label (falsifiers 2, 3, 5, 6, 7)", () => {
  it("2. the label derives only from parsed contract fields, in the v4 §06.1 precedence", () => {
    expect(membraneLabel(NONE)).toBe("NO_OBSERVATION");
    expect(membraneLabel(MALFORMED)).toBe("GOVERNANCE_UNAVAILABLE");
    expect(membraneLabel(UNAVAILABLE)).toBe("GOVERNANCE_UNAVAILABLE");
    expect(membraneLabel(obs(wire(), true))).toBe("SUPERSEDED");
    expect(membraneLabel(obs(wire({ deltas: [HUMAN({ result: "AUTHORITY_BOUNDARY" })] }, { firstBrokenRelation: { predecessor: null, broken: HUMAN({ result: "AUTHORITY_BOUNDARY" }) } })))).toBe("HUMAN_AUTHORITY_REQUIRED");
    expect(membraneLabel(obs(wire({}, { humanAuthorityRequired: [{ deltaId: "d-0", result: "GOVERNANCE_BOUNDARY", reasonCode: null }] })))).toBe("HUMAN_AUTHORITY_REQUIRED");
    expect(membraneLabel(obs(wire({ deltas: [HUMAN()] }, { firstBrokenRelation: { predecessor: null, broken: HUMAN() }, partial: true })))).toBe("BOUNDARY_REACHED");
    expect(membraneLabel(obs(wire({}, { partial: true })))).toBe("PARTIAL");
    expect(membraneLabel(obs(wire()))).toBe("PROVIDER_NOT_EXECUTABLE");
    expect(membraneLabel(obs(wire({ deltas: [HUMAN({ result: "ALLOWED", reasonCode: null })] })))).toBe("OBSERVED");
    // superseded outranks everything below it, even an FBR
    expect(membraneLabel(obs(wire({ deltas: [HUMAN()] }, { firstBrokenRelation: { predecessor: null, broken: HUMAN() } }), true))).toBe("SUPERSEDED");
    expect(Object.keys(MEMBRANE_WORDS).sort()).toEqual([...MEMBRANE_LABELS].sort());
  });
  it("3. unavailable never synthesizes capability, boundary, authority, provider, ceiling or SEND state", () => {
    const p = presentationOf(UNAVAILABLE);
    expect(p.aggregates).toEqual({ observation: "unavailable" });
    expect(p.aggregates.current).toBeUndefined();
    expect(p.deltas).toEqual([]);
    expect(p.attachments).toEqual([]);
    expect(p.send).toBeNull();
    expect(p.basis).toBeNull();
    expect(JSON.stringify(p)).not.toMatch(/canSend|governanceAdmissible|providerExecutable|PRESENT|REQUIRED|GOVERNED|FIXTURE/);
    expect(presentationOf(MALFORMED).aggregates).toEqual({ observation: "unavailable" });
    expect(presentationOf(NONE).aggregates).toEqual({ observation: "none" });
  });
  it("unavailable is never a denial and no observation is never current", () => {
    expect(membraneLabel(UNAVAILABLE)).not.toBe("BOUNDARY_REACHED");
    expect(JSON.stringify(presentationOf(UNAVAILABLE))).not.toMatch(/DENIED|denied|BLOCKED/);
    expect(presentationAggregates(NONE).observation).toBe("none");
    expect(MEMBRANE_LABELS).not.toContain("DENIED");
    expect(MEMBRANE_LABELS).not.toContain("ALLOWED");
    expect(MEMBRANE_LABELS).not.toContain("CURRENT");
  });
  it("5. Human Authority presentation appears only from an AUTHORITY_BOUNDARY FBR or a non-empty HAR — never from role, reason text or result elsewhere", () => {
    // a delta with result AUTHORITY_BOUNDARY that is NOT the FBR and NOT in HAR does not raise the label
    expect(membraneLabel(obs(wire({ deltas: [HUMAN({ result: "AUTHORITY_BOUNDARY" })] })))).toBe("OBSERVED");
    // reason text alone does nothing
    expect(membraneLabel(obs(wire({ deltas: [HUMAN({ result: "STATE_BOUNDARY", reasonCode: "HUMAN_AUTHORITY_REQUIRED" })] })))).toBe("OBSERVED");
    // governanceAdmissible false alone does nothing
    expect(membraneLabel(obs(wire({ deltas: [HUMAN({ result: "ALLOWED", reasonCode: null })] }, {}, { governanceAdmissible: false })))).toBe("OBSERVED");
    expect(presentationAggregates(obs(wire())).current?.humanAuthority).toBe("NOT_REQUIRED");
    expect(presentationAggregates(obs(wire({}, { humanAuthorityRequired: [{ deltaId: "d-0", result: "AUTHORITY_BOUNDARY", reasonCode: null }] }))).current?.humanAuthority).toBe("REQUIRED");
  });
  it("6. boundary presentation derives only from chain.firstBrokenRelation", () => {
    expect(presentationAggregates(obs(wire({ deltas: [HUMAN({ result: "DENIED" })] }))).current).toMatchObject({ boundary: "NONE", fbrPresent: false, chainState: "COMPLETE" });
    const withFbr = presentationAggregates(obs(wire({ deltas: [HUMAN()] }, { firstBrokenRelation: { predecessor: null, broken: HUMAN() } })));
    expect(withFbr.current).toMatchObject({ boundary: "PRESENT", fbrPresent: true, chainState: "BLOCKED" });
    expect(presentationAggregates(obs(wire({}, { partial: true }))).current).toMatchObject({ boundary: "NONE", chainState: "PARTIAL", partial: true });
  });
  it("7. provider presentation does not imply provider execution authority: it restates two crossed facts and nothing more", () => {
    const a = presentationAggregates(obs(wire())).current;
    expect(a).toMatchObject({ providerDeltaPresent: true, providerNotExecutable: true, capability: { providerExecutable: false, providerExecutableReasons: ["NO_ELIGIBLE_PROVIDER_ROUTE"] } });
    const b = presentationAggregates(obs(wire({}, {}, { providerExecutable: true, providerExecutableReasons: [] }))).current;
    expect(b).toMatchObject({ providerDeltaPresent: true, providerNotExecutable: false });
    expect(JSON.stringify(b)).not.toMatch(/executable":true,"authori|authorized|permitted|EXECUTE/);
    const c = presentationAggregates(obs(wire({ deltas: [HUMAN()] }))).current;
    expect(c).toMatchObject({ providerDeltaPresent: false, providerNotExecutable: false });
    expect(membraneLabel(obs(wire({ deltas: [HUMAN({ result: "ALLOWED", reasonCode: null })] })))).toBe("OBSERVED");
  });
});

describe("SEND law (falsifiers 8, 9)", () => {
  it("8. canSend never creates a SEND affordance or state: true and false present identically, and nothing reads canSend for SEND", () => {
    const f = presentationOf(obs(wire({}, {}, { canSend: false })));
    const t = presentationOf(obs(wire({}, {}, { canSend: true })));
    expect(f.send).toEqual(t.send);
    expect(t.send).toEqual({ text: "Send not materialized", keyedTo: "PCPG-R12/1", reason: "PCPG-R12/1 contains no SEND relation (R-13 not started)" });
    expect(t.aggregates.current?.capability.canSend).toBe(true); // the crossed projection is preserved verbatim …
    expect(JSON.stringify(t)).not.toMatch(/sendGate|SEND_GATE|sendAllowed|Ready to send|Send allowed|Send disabled|Send unavailable/); // … and never becomes a gate
    expect(PRESENTATION_CATEGORIES).not.toContain("SEND");
    expect(Object.values(PRESENTATION_ATTACHMENT_MAP).flat()).not.toContain("SEND_AREA");
  });
  it("9. PCPG-R12/1 always implies no materialized SEND relation; any other contract identity yields no statement", () => {
    expect(sendStatement("PCPG-R12/1")?.text).toBe("Send not materialized");
    expect(sendStatement("PCPG-R12/2")).toBeNull();
    expect(sendStatement("")).toBeNull();
    expect(NOT_MATERIALIZED).toContain("SEND relation (R-13)");
    // a superseded observation treats canSend as absent (null), never as false and never as a gate
    expect(presentationOf(obs(wire({}, {}, { canSend: true }), true)).aggregates.current?.capability.canSend).toBeNull();
  });
});

describe("Session-level proof ceiling (falsifiers 10, 11)", () => {
  it("10. a null proof ceiling remains null and reads unknown — never GOVERNED, never false", () => {
    expect(proofCeilingPresentation(null)).toEqual({ label: PROOF_CEILING_LABEL, value: null, words: "unknown" });
    const p = presentationOf(obs(wire({ deltas: [D({ sessionProofCeiling: null })] })));
    expect(p.aggregates.current?.composedProofCeiling.value).toBeNull();
    expect(p.deltas[0].sessionProofCeiling).toEqual({ label: PROOF_CEILING_LABEL, value: null, words: "unknown" });
    expect(proofCeilingPresentation("GOVERNED")).toEqual({ label: PROOF_CEILING_LABEL, value: "GOVERNED", words: "governed" });
    expect(proofCeilingPresentation("FIXTURE_NON_PROOF")).toEqual({ label: PROOF_CEILING_LABEL, value: "FIXTURE_NON_PROOF", words: "fixture / non-proof" });
  });
  it("11. the proof ceiling is never renamed evidence, provenance, confidence or trust", () => {
    expect(PROOF_CEILING_LABEL).toBe("Session-level proof ceiling (partial I-12)");
    const text = JSON.stringify(presentationOf(obs(wire({ composedProofCeiling: "GOVERNED" }))));
    // "evidence" / "provenance" may appear only inside the not-materialized list, never as a value or a renamed ceiling
    const withoutList = JSON.stringify({ ...presentationOf(obs(wire({ composedProofCeiling: "GOVERNED" }))), notMaterialized: undefined });
    expect(withoutList).not.toMatch(/evidence|provenance|confidence|trust|\bproven\b|"proof":/);
    expect(text).toContain("Session-level proof ceiling (partial I-12)");
  });
});

describe("PresentationCategory (falsifiers 12–20)", () => {
  it("12./13. an unknown or null operation maps to UNPLACED and is never guessed into another category", () => {
    for (const operation of [null, "ADMIT_PARTICIPANT", "CREATE_IMPACT_CHAIN", "SELECT_PRIMARY_QUESTIONS", "select_primary_question", "DO_SOMETHING_NEW", "DECISION", "QUESTION_SET"]) {
      const cats = categoriesOf(parsed(wire({ deltas: [HUMAN({ operation })] })).kind === "current" ? (parsed(wire({ deltas: [HUMAN({ operation })] })) as never as { deltas: DeltaWire[] }).deltas[0] : (null as never));
      expect(cats).toEqual(["UNPLACED"]);
      expect(attachmentsOf(cats)).toEqual(["FIELD_PANEL"]);
    }
    // an unknown operation with a provider execution class is PROVIDER by class, still not guessed into QUESTION/DECISION
    const prov = categoriesOf((parsed(wire({ deltas: [D({ operation: "DO_SOMETHING_NEW" })] })) as never as { deltas: DeltaWire[] }).deltas[0]);
    expect(prov).toEqual(["PROVIDER"]);
    // UNPLACED never co-occurs with a placed category
    for (const w of [wire(), wire({ deltas: [HUMAN()] }), wire({ deltas: [HUMAN({ operation: null, result: "AUTHORITY_BOUNDARY" })] })]) {
      const cats = categoriesOf((parsed(w) as never as { deltas: DeltaWire[] }).deltas[0]);
      expect(cats.includes("UNPLACED") && cats.length > 1).toBe(false);
    }
  });
  it("14./15. a delta may map to several categories; order is the fixed vocabulary order and carries no meaning", () => {
    const d = (parsed(wire({ deltas: [HUMAN({ result: "AUTHORITY_BOUNDARY" })] })) as never as { deltas: DeltaWire[] }).deltas[0];
    expect(categoriesOf(d)).toEqual(["QUESTION", "AUTHORITY"]);
    expect(attachmentsOf(categoriesOf(d))).toEqual(["QUESTION_AREA", "DECISION_AREA", "BOUNDARY_AREA"]);
    expect(attachmentsOf(["AUTHORITY", "QUESTION"])).toEqual(attachmentsOf(["QUESTION", "AUTHORITY"]));
    const grant = (parsed(wire({ deltas: [HUMAN({ operation: "GRANT_SESSION_CONTROL", result: "HUMAN_ACTION_AVAILABLE", reasonCode: null })] })) as never as { deltas: DeltaWire[] }).deltas[0];
    expect(categoriesOf(grant)).toEqual(["AUTHORITY"]);
    const ext = (parsed(wire({ deltas: [D({ operation: "BEGIN_ANALYSIS", executionClass: "EXTERNAL_EFFECT" })] })) as never as { deltas: DeltaWire[] }).deltas[0];
    expect(categoriesOf(ext)).toEqual(["SESSION_STATE", "EXTERNAL_OR_DISCLOSURE"]);
    expect(categoriesOf((parsed(wire({ deltas: [HUMAN({ operation: "RECORD_HUMAN_DECISION" })] })) as never as { deltas: DeltaWire[] }).deltas[0])).toEqual(["DECISION"]);
    expect(categoriesOf((parsed(wire({ deltas: [HUMAN({ operation: "PREPARE_BURST" })] })) as never as { deltas: DeltaWire[] }).deltas[0])).toEqual(["BURST"]);
    expect(categoriesOf((parsed(wire({ deltas: [HUMAN({ operation: "BEGIN_SETUP" })] })) as never as { deltas: DeltaWire[] }).deltas[0])).toEqual(["SESSION_STATE"]);
  });
  it("16. PresentationCategory never enters the wire contract: the parser rejects it anywhere, and the vocabulary is CYAN-only", () => {
    expect(() => parseGovernanceObservation(wire({ presentationCategory: "QUESTION" }))).toThrow(MalformedProjection);
    expect(() => parseGovernanceObservation(wire({ deltas: [D({ categories: ["PROVIDER"] } as never)] }))).toThrow(MalformedProjection);
    expect(() => parseGovernanceObservation(wire({ deltas: [D({ attachments: ["FIELD_PANEL"] } as never)] }))).toThrow(MalformedProjection);
    const clientSrc = readFileSync(join(__dirname, "..", "..", "lib", "api", "pcpgClient.ts"), "utf8");
    expect(clientSrc).not.toMatch(/PresentationCategory|PRESENTATION_CATEGORIES|attachmentsOf|pcpgPresentation/);
  });
  it("17./18. deriving presentation changes neither capability nor chain values", () => {
    const o = parsed(wire({ deltas: [D(), HUMAN()] }, { firstBrokenRelation: { predecessor: D(), broken: HUMAN() }, partial: true }, { canSend: true }));
    const before = JSON.stringify(o);
    const p = presentationOf({ kind: "observation", observation: o, supersededByObjectChange: false });
    expect(JSON.stringify(o)).toBe(before);
    if (o.kind !== "current") throw new Error();
    expect(p.aggregates.current?.capability).toEqual({ ...o.capability });
    expect(p.aggregates.current?.chainState).toBe("BLOCKED");
    expect(o.chain.partial).toBe(true);
    expect(o.capability.canSend).toBe(true);
  });
  it("19./20./21. no affectedSemanticLoci, no SOURCE_RELATION, no authority binding exists in the derivation", () => {
    const full = presentationOf(obs(wire({ deltas: [D(), HUMAN({ result: "AUTHORITY_BOUNDARY" })] }, { humanAuthorityRequired: [{ deltaId: "d-1", result: "AUTHORITY_BOUNDARY", reasonCode: "NO_SESSION_CONTROL" }] })));
    // the not-materialized list may NAME SOURCE_RELATION and HAR holder classes as absent; nothing else may carry them
    expect(full.notMaterialized).toContain("SOURCE_RELATION");
    const text = JSON.stringify({ ...full, notMaterialized: undefined });
    expect(text).not.toMatch(/affectedSemanticLoci|semanticLoc|SOURCE_RELATION|sourceRelation|bindingId|binding|holderClass|holder|grantor|displaySummary/);
    // the production source names SOURCE_RELATION and HAR holder classes in exactly one place: the not-materialized list
    const src = readFileSync(join(__dirname, "..", "..", "lib", "field", "pcpgPresentation.ts"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
    const notMaterializedLine = src.split("\n").filter((l) => l.includes("NOT_MATERIALIZED = ["));
    expect(notMaterializedLine).toHaveLength(1);
    const srcWithoutList = src.replace(notMaterializedLine[0], "");
    expect(srcWithoutList).not.toMatch(/affectedSemanticLoci|SOURCE_RELATION|bindingId|holderClass|displaySummary|nervePoints/);
  });
  it("22./23. no role is inferred and no displaySummary is accepted from the server", () => {
    expect(() => parseGovernanceObservation(wire({ displaySummary: { label: "FIELD_CURRENT" } }))).toThrow(MalformedProjection);
    const src = readFileSync(join(__dirname, "..", "..", "lib", "field", "pcpgPresentation.ts"), "utf8");
    expect(src).not.toMatch(/\brole\s*[!=]==?|viewer\.(role|isGovernanceRoot|isSessionController)|\/auth\/me|authClient/);
  });
  it("4. an unknown reason or closed value cannot enter the derivations, because the parser already fails closed", () => {
    expect(() => obs(wire({ deltas: [D({ result: "MAYBE" })] }))).toThrow(MalformedProjection);
    expect(() => obs({ kind: "unavailable", reasonCode: "OFFLINE" })).toThrow(MalformedProjection);
    expect(() => obs(wire({ composedProofCeiling: "PROVEN" }))).toThrow(MalformedProjection);
  });
});

describe("whole-observation presentation (consumer-facing shape; no UI)", () => {
  it("assembles label, aggregates, per-delta placement, union attachments, send statement, not-materialized list and basis", () => {
    const p = presentationOf(obs(wire({ deltas: [D(), HUMAN()] }, { firstBrokenRelation: { predecessor: D(), broken: HUMAN() }, partial: true, maximumLegitimateTransition: [] })));
    expect(p.label).toBe("BOUNDARY_REACHED");
    expect(p.words).toBe("Boundary reached");
    expect(p.deltas.map((d) => [d.deltaId, d.categories, d.retained])).toEqual([["d-0", ["PROVIDER"], false], ["d-1", ["QUESTION"], false]]);
    expect(p.attachments).toEqual(["QUESTION_AREA", "PROVIDER_RELATED_AREA"]);
    expect(p.send?.keyedTo).toBe("PCPG-R12/1");
    expect(p.notMaterialized).toEqual(["SEND relation (R-13)", "evidence", "provenance", "HAR holder classes", "SOURCE_RELATION"]);
    expect(p.basis).toEqual({ rawIntentDigestSha256: "ab".repeat(32), derivationTime: "2026-10-01T11:17:00+00:00" });
    const retained = presentationOf(obs(wire({ deltas: [HUMAN({ result: "ALLOWED", reasonCode: null })] }, { maximumLegitimateTransition: [HUMAN({ result: "ALLOWED", reasonCode: null })] })));
    expect(retained.deltas[0].retained).toBe(true);
    expect(retained.aggregates.current?.retainedDeltaIds).toEqual(["d-1"]);
  });
});
