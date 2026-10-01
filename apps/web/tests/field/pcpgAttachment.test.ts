/**
 * CYAN-PCPG-03 falsifiers 1–20 (Architecture 27 v4 §05.4, §06.4, §13.6, §21): the typed attachment relation from
 * PresentationCategory to the current CYAN object structure. Inputs come through parser (01) and derivation (02).
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { parseGovernanceObservation, type GovernanceObservation } from "../../lib/api/pcpgClient";
import {
  CYAN_ATTACHMENT_TARGETS,
  CYAN_OBJECT_AREAS,
  MalformedAttachmentMap,
  attachPresentation,
  safeCategory,
  targetsOfAttachment,
  targetsOfCategories,
  validateAttachmentRelation,
} from "../../lib/field/pcpgAttachment";
import { PRESENTATION_ATTACHMENTS, PRESENTATION_ATTACHMENT_MAP, PRESENTATION_CATEGORIES, presentationOf, type PresentationAttachment } from "../../lib/field/pcpgPresentation";

const WEB = join(__dirname, "..", "..");
function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((n) => {
    const p = join(dir, n);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
}
const SOURCES = [...walk(join(WEB, "components")), ...walk(join(WEB, "app"))].filter((p) => /\.tsx?$/.test(p)).map((p) => readFileSync(p, "utf8")).join("\n");

const D = (over: Record<string, unknown> = {}) => ({ deltaId: "d-0", operation: "REQUEST_QUESTION_ANALYSIS", executionClass: "PROVIDER_COMPUTATION", target: null, sourceClause: "Analyse the questions", span: [0, 21], currentState: null, result: "INDETERMINATE", reasonCode: "DATA_GOVERNANCE_NOT_MATERIALIZED", flags: [], sessionProofCeiling: "GOVERNED", ...over });
const H = (over: Record<string, unknown> = {}) => D({ deltaId: "d-1", operation: "SELECT_PRIMARY_QUESTION", executionClass: "HUMAN_COMMAND", result: "STATE_BOUNDARY", reasonCode: "X", ...over });
function wire(deltas: unknown[], chain: Record<string, unknown> = {}, cap: Record<string, unknown> = {}) {
  return parseGovernanceObservation({
    kind: "current",
    contract: "PCPG-R12/1",
    basis: { rawIntentDigestSha256: "ab".repeat(32), derivationTime: "2026-10-01T11:17:00+00:00" },
    semanticObservation: { ruleSetVersion: "v", clauses: [], actions: [], unknownRelations: [], relationsTouched: [], declaredPurpose: null, semanticPurpose: null, purposeAlignment: null, semanticDrift: false },
    deltas,
    chain: { firstBrokenRelation: null, maximumLegitimateTransition: [], nextValidTransition: null, humanAuthorityRequired: [], partial: false, ...chain },
    capability: { governanceAdmissible: false, governanceAdmissibleReasons: ["MLT_EMPTY"], providerExecutable: false, providerExecutableReasons: ["NO_ELIGIBLE_PROVIDER_ROUTE"], canSend: false, ...cap },
    composedProofCeiling: null,
  });
}
const present = (o: GovernanceObservation) => presentationOf({ kind: "observation", observation: o, supersededByObjectChange: false });
const areas = (targets: readonly { area: string }[]) => targets.map((t) => t.area);

describe("the relation is explicit, exact and fail-closed (falsifiers 1, 2, 3)", () => {
  it("1. every current PresentationCategory has an explicit attachment relation, and every attachment an explicit (possibly empty) target list", () => {
    for (const c of PRESENTATION_CATEGORIES) {
      expect(PRESENTATION_ATTACHMENT_MAP[c].length).toBeGreaterThan(0);
      for (const a of PRESENTATION_ATTACHMENT_MAP[c]) expect(Array.isArray(CYAN_ATTACHMENT_TARGETS[a])).toBe(true);
    }
    expect(Object.keys(CYAN_ATTACHMENT_TARGETS).sort()).toEqual([...PRESENTATION_ATTACHMENTS].sort());
    expect(() => validateAttachmentRelation()).not.toThrow();
  });
  it("every target is an existing organism identity (its selector occurs in the current component or page sources)", () => {
    for (const t of CYAN_OBJECT_AREAS) {
      for (const sel of t.identity.split(",")) {
        const m = /data-testid="([^"]+)"|data-semantic="([^"]+)"|\[(data-boundary)\]/.exec(sel.trim());
        const token = m?.[1] ?? m?.[2] ?? m?.[3];
        expect(token, sel).toBeDefined();
        expect(SOURCES.includes(`"${token}"`) || SOURCES.includes(`${token}=`) || SOURCES.includes(`${token}:`) || SOURCES.includes(`"${token}`), `${t.area}: ${sel}`).toBe(true);
      }
    }
  });
  it("2. an unknown category cannot be guessed into an existing semantic area: it is UNPLACED → proof chamber only", () => {
    for (const bogus of ["QUESTIONS", "question", "DECISION_TRANSITION", "AUTHORITY_BOUNDARY", "SEND", "", "UNKNOWN"]) {
      expect(safeCategory(bogus)).toBe("UNPLACED");
      expect(areas(targetsOfCategories([bogus]))).toEqual(["proof-chamber"]);
    }
  });
  it("3. UNPLACED resolves only to the defined safe fallback (FIELD_PANEL → proof chamber); never question, boundary or authority", () => {
    expect(PRESENTATION_ATTACHMENT_MAP.UNPLACED).toEqual(["FIELD_PANEL"]);
    expect(areas(targetsOfCategories(["UNPLACED"]))).toEqual(["proof-chamber"]);
    const u = attachPresentation(present(wire([H({ operation: "ADMIT_PARTICIPANT" })])));
    expect(u.deltas[0].categories).toEqual(["UNPLACED"]);
    expect(areas(u.deltas[0].targets)).toEqual(["proof-chamber"]);
    expect(areas(u.targets)).not.toContain("question-set");
    expect(areas(u.targets)).not.toContain("boundary-marks");
    expect(areas(u.targets)).not.toContain("authority-chamber");
  });
  it("an unknown attachment target fails closed and a malformed relation is never silently ignored", () => {
    expect(() => targetsOfAttachment("SEND_AREA" as PresentationAttachment)).toThrow(MalformedAttachmentMap);
    expect(() => targetsOfAttachment("" as PresentationAttachment)).toThrow(MalformedAttachmentMap);
  });
});

describe("legitimate targets per category (falsifiers 4, 5, 6, 7)", () => {
  it("4. QUESTION maps only to the human question set (and nowhere else)", () => {
    expect(areas(targetsOfCategories(["QUESTION"]))).toEqual(["question-set"]);
  });
  it("5. SESSION_STATE maps only to the lifecycle ring, the path station and the active-phase chamber", () => {
    expect(areas(targetsOfCategories(["SESSION_STATE"]))).toEqual(["lifecycle-ring", "path-station", "active-phase-chamber"]);
  });
  it("6. AUTHORITY maps only to boundary/authority and decision presentation targets, never to the question set or the derived chamber", () => {
    const t = areas(targetsOfCategories(["AUTHORITY"]));
    expect(t).toEqual(["authority-chamber", "boundary-marks", "decision-entry-chamber", "decision-chamber"]);
    expect(t).not.toContain("question-set");
    expect(t).not.toContain("derived-chamber");
  });
  it("7. PROVIDER maps only to the derived (provider-related) chamber; EXTERNAL_OR_DISCLOSURE only to the boundary targets", () => {
    expect(areas(targetsOfCategories(["PROVIDER"]))).toEqual(["derived-chamber"]);
    expect(areas(targetsOfCategories(["EXTERNAL_OR_DISCLOSURE"]))).toEqual(["authority-chamber", "boundary-marks"]);
    expect(areas(targetsOfCategories(["BURST"]))).toEqual(["burst-panel"]);
    expect(areas(targetsOfCategories(["DECISION"]))).toEqual(["decision-entry-chamber", "decision-chamber"]);
  });
  it("DEEP_FIELD_INSPECTOR is structurally absent today and is recorded, not guessed", () => {
    expect(CYAN_ATTACHMENT_TARGETS.DEEP_FIELD_INSPECTOR).toEqual([]);
    expect(targetsOfAttachment("DEEP_FIELD_INSPECTOR")).toEqual([]);
  });
});

describe("multiplicity and order (falsifiers 8, 9, 10, 11)", () => {
  it("8. multiple categories produce multiple targets; nothing collapses to one winner", () => {
    const t = areas(targetsOfCategories(["QUESTION", "AUTHORITY"]));
    expect(t).toEqual(["question-set", "authority-chamber", "boundary-marks", "decision-entry-chamber", "decision-chamber"]);
    const a = attachPresentation(present(wire([H({ result: "AUTHORITY_BOUNDARY" })])));
    expect(a.deltas[0].categories).toEqual(["QUESTION", "AUTHORITY"]);
    expect(a.deltas[0].attachments).toEqual(["QUESTION_AREA", "DECISION_AREA", "BOUNDARY_AREA"]);
    expect(areas(a.deltas[0].targets).length).toBe(5);
  });
  it("9. duplicate targets are normalized as a set without loss", () => {
    expect(areas(targetsOfCategories(["AUTHORITY", "EXTERNAL_OR_DISCLOSURE", "DECISION"]))).toEqual(["authority-chamber", "boundary-marks", "decision-entry-chamber", "decision-chamber"]);
    expect(areas(targetsOfCategories(["QUESTION", "QUESTION"]))).toEqual(["question-set"]);
  });
  it("10./11. category order and attachment order change nothing: the result is the same set", () => {
    expect(targetsOfCategories(["AUTHORITY", "QUESTION"])).toEqual(targetsOfCategories(["QUESTION", "AUTHORITY"]));
    expect(targetsOfCategories(["PROVIDER", "SESSION_STATE", "BURST"])).toEqual(targetsOfCategories(["BURST", "PROVIDER", "SESSION_STATE"]));
    expect(targetsOfAttachment("BOUNDARY_AREA")).toEqual(targetsOfAttachment("BOUNDARY_AREA"));
  });
});

describe("no governance change, no new relation (falsifiers 12–19)", () => {
  const observation = wire([D(), H({ result: "AUTHORITY_BOUNDARY" })], { firstBrokenRelation: { predecessor: D(), broken: H({ result: "AUTHORITY_BOUNDARY" }) }, partial: true, humanAuthorityRequired: [{ deltaId: "d-1", result: "AUTHORITY_BOUNDARY", reasonCode: "NO_SESSION_CONTROL" }] }, { canSend: true });
  it("12./13./14./15. attaching alters neither the presentation input nor capability, chain or proof ceiling", () => {
    const p = present(observation);
    const before = JSON.stringify(p);
    const obsBefore = JSON.stringify(observation);
    const a = attachPresentation(p);
    expect(a.presentation).toBe(p);
    expect(JSON.stringify(p)).toBe(before);
    expect(JSON.stringify(observation)).toBe(obsBefore);
    expect(a.presentation.aggregates.current?.capability.canSend).toBe(true);
    expect(a.presentation.aggregates.current?.chainState).toBe("BLOCKED");
    expect(a.presentation.aggregates.current?.composedProofCeiling.value).toBeNull();
    expect(observation.kind === "current" && observation.chain.partial).toBe(true);
  });
  it("16./17. attaching cannot create SEND state or Human Authority state: the output carries no such keys beyond the passed-through presentation", () => {
    const a = attachPresentation(present(wire([D()], {}, { canSend: true })));
    const own = JSON.stringify({ ...a, presentation: undefined });
    expect(own).not.toMatch(/send|SEND|authority|AUTHORITY|humanAuthority|HAR|canSend|gate/);
    expect(a.presentation.send?.text).toBe("Send not materialized");
    expect(a.presentation.label).toBe("PROVIDER_NOT_EXECUTABLE");
  });
  it("18./19. no SOURCE_RELATION and no affectedSemanticLoci anywhere in the relation or its source", () => {
    const a = attachPresentation(present(observation));
    expect(JSON.stringify({ ...a, presentation: undefined })).not.toMatch(/SOURCE_RELATION|sourceRelation|affectedSemanticLoci|semanticLoc|locus/i);
    const src = readFileSync(join(WEB, "lib", "field", "pcpgAttachment.ts"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
    expect(src).not.toMatch(/SOURCE_RELATION|affectedSemanticLoci|canSend|providerExecutable|governanceAdmissible|humanAuthorityRequired|firstBrokenRelation|\brole\b|fetch\(|pcpgClient/);
  });
  it("the relation consumes only presentationOf output: it imports nothing from the client and reads no raw response", () => {
    const src = readFileSync(join(WEB, "lib", "field", "pcpgAttachment.ts"), "utf8");
    expect(src).toMatch(/from "\.\/pcpgPresentation"/);
    expect(src).not.toMatch(/from "\.\.\/api\//);
  });
});

describe("no rendering in this Work Unit (falsifier 20)", () => {
  it("20. no component or page imports the attachment relation or the presentation derivation yet", () => {
    expect(SOURCES).not.toMatch(/pcpgAttachment|pcpgPresentation|attachPresentation|presentationOf\(/);
  });
});
