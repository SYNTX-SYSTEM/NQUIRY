/**
 * CYAN-PCPG-06 falsifiers: the rendering derivation (areas, boundary card, panel model) and the two components, against
 * Architecture 27 v4 §06.3–06.5, §07, §08.3–08.4, §09.2–09.3, §10.3–10.4, §11.3–11.4, §17, §18 (forbidden list), §21.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { GovernanceAttachment } from "../../components/field/GovernanceAttachment";
import { GovernancePanel } from "../../components/field/GovernancePanel";
import type { DeltaWire, GovernanceObservationCurrent } from "../../lib/api/pcpgClient";
import { type ObservationPresence, presentationOf } from "../../lib/field/pcpgPresentation";
import { deltaLine, governanceRendering, operationWords, resultWords, targetWords } from "../../lib/field/pcpgRendering";

const WEB = join(__dirname, "..", "..");
const code = (p: string) => readFileSync(join(WEB, p), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
const DERIVATION = code("lib/field/pcpgRendering.ts");
const ATTACHMENT = code("components/field/GovernanceAttachment.tsx");
const PANEL = code("components/field/GovernancePanel.tsx");
const PAGE = code("app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx");

const PROVIDER: DeltaWire = { deltaId: "d-0", operation: "REQUEST_QUESTION_ANALYSIS", executionClass: "PROVIDER_COMPUTATION", target: null, sourceClause: "Analyse the questions", span: [0, 21], currentState: "QUESTION_CAPTURE", result: "INDETERMINATE", reasonCode: "DATA_GOVERNANCE_NOT_MATERIALIZED", flags: [], sessionProofCeiling: "GOVERNED" };
const HUMAN: DeltaWire = { ...PROVIDER, deltaId: "d-1", operation: "SELECT_PRIMARY_QUESTION", executionClass: "HUMAN_COMMAND", target: "OUT_OF_SCOPE", sourceClause: "pick the primary question", span: [23, 48], result: "STATE_BOUNDARY", reasonCode: "SESSION_NOT_IN_QUESTION_SELECTION" };
const GRANT: DeltaWire = { ...PROVIDER, deltaId: "d-2", operation: "GRANT_SESSION_CONTROL", executionClass: "HUMAN_COMMAND", target: "SESSION:s", sourceClause: "give Constantine control", span: [50, 74], result: "AUTHORITY_BOUNDARY", reasonCode: "NOT_SESSION_CONTROLLER" };
const UNKNOWN: DeltaWire = { ...HUMAN, deltaId: "d-9", operation: null, executionClass: "UNKNOWN", result: "INDETERMINATE", reasonCode: null, sessionProofCeiling: null };
function current(deltas: readonly DeltaWire[], chain: Partial<GovernanceObservationCurrent["chain"]> = {}, providerExecutable = false): GovernanceObservationCurrent {
  return {
    kind: "current", contract: "PCPG-R12/1", basis: { rawIntentDigestSha256: "3f9a".padEnd(64, "0"), derivationTime: "2026-10-01T11:17:00+00:00" },
    semanticObservation: { ruleSetVersion: "26/2026-09-29", clauses: ["Analyse the questions"], actions: [], unknownRelations: [], relationsTouched: ["REQUEST_QUESTION_ANALYSIS"], declaredPurpose: null, semanticPurpose: null, purposeAlignment: null, semanticDrift: false },
    deltas,
    chain: { firstBrokenRelation: null, maximumLegitimateTransition: [], nextValidTransition: null, humanAuthorityRequired: [], partial: false, ...chain },
    capability: { governanceAdmissible: false, governanceAdmissibleReasons: ["MLT_EMPTY"], providerExecutable, providerExecutableReasons: providerExecutable ? [] : ["NO_ELIGIBLE_PROVIDER_ROUTE"], canSend: false },
    composedProofCeiling: "GOVERNED",
  };
}
const presence = (observation: GovernanceObservationCurrent, superseded = false): ObservationPresence => ({ kind: "observation", observation, supersededByObjectChange: superseded });
const render = (p: ObservationPresence) => governanceRendering(p, presentationOf(p));
const html = (node: React.ReactElement) => renderToStaticMarkup(node);

describe("words for crossed values (§21)", () => {
  it("INDETERMINATE is indeterminate, never denied; null target is unresolved, never out of scope; null operation is Unknown operation", () => {
    expect(resultWords(PROVIDER)).toBe("indeterminate · DATA_GOVERNANCE_NOT_MATERIALIZED");
    expect(resultWords({ result: "INDETERMINATE", reasonCode: null })).toBe("indeterminate");
    expect(resultWords({ result: "DENIED", reasonCode: "X" })).toBe("denied · X");
    expect(targetWords(null)).toBe("unresolved");
    expect(targetWords("OUT_OF_SCOPE")).toBe("out of scope");
    expect(targetWords("SESSION:s")).toBe("SESSION:s");
    expect(operationWords(null)).toBe("Unknown operation");
    expect(deltaLine(UNKNOWN)).toBe("Unknown operation · unknown execution class — indeterminate");
    expect(deltaLine(PROVIDER)).toBe("REQUEST_QUESTION_ANALYSIS · provider computation — indeterminate · DATA_GOVERNANCE_NOT_MATERIALIZED");
  });
});

describe("level 0.5 — placement at existing areas (§06.3–06.5, §07, §08.3)", () => {
  it("a provider step is placed at the derived chamber with Provider not executable; nothing elsewhere", () => {
    const r = render(presence(current([PROVIDER])));
    expect(r.areas.map((a) => a.area)).toEqual(["derived-chamber"]);
    expect(r.byArea["derived-chamber"]?.providerNotExecutable).toBe(true);
    expect(r.byArea["derived-chamber"]?.summary).toBe("1 crossed step placed here");
    expect(r.byArea["derived-chamber"]?.deltas[0].line).toContain("indeterminate");
    expect(r.boundary).toBeNull();
  });
  it("a human step maps by operation: SELECT_PRIMARY_QUESTION → the human question set; GRANT_ → boundary + decision areas; the FBR and HAR flags follow the chain, never the text", () => {
    const r = render(presence(current([PROVIDER, HUMAN, GRANT], { firstBrokenRelation: { predecessor: PROVIDER, broken: HUMAN }, humanAuthorityRequired: [{ deltaId: "d-2", result: "AUTHORITY_BOUNDARY", reasonCode: "NOT_SESSION_CONTROLLER" }], partial: true })));
    expect(r.areas.map((a) => a.area).sort()).toEqual(["authority-chamber", "boundary-marks", "decision-chamber", "decision-entry-chamber", "derived-chamber", "question-set"]);
    expect(r.byArea["question-set"]?.firstBrokenHere).toBe(true);
    expect(r.byArea["question-set"]?.deltas.map((d) => d.delta.deltaId)).toEqual(["d-1"]);
    expect(r.byArea["authority-chamber"]?.humanAuthorityHere).toBe(true);
    expect(r.byArea["authority-chamber"]?.deltas.map((d) => d.delta.deltaId)).toEqual(["d-2"]);
    expect(r.byArea["decision-entry-chamber"]?.deltas.map((d) => d.delta.deltaId)).toEqual(["d-2"]);
    expect(r.byArea["derived-chamber"]?.firstBrokenHere).toBe(false);
    // the FBR flag follows chain.firstBrokenRelation only: an AUTHORITY_BOUNDARY result is not "first broken"
    expect(r.byArea["authority-chamber"]?.firstBrokenHere).toBe(false);
    expect(r.byArea["authority-chamber"]?.deltas[0].isFirstBroken).toBe(false);
  });
  it("without a first broken relation nothing is 'first broken' and there is no boundary card, whatever the results or the legitimate transition say", () => {
    const r = render(presence(current([PROVIDER, HUMAN, GRANT], { firstBrokenRelation: null, maximumLegitimateTransition: [PROVIDER], nextValidTransition: HUMAN })));
    expect(r.boundary).toBeNull();
    expect(r.panel.boundary).toBeNull();
    expect(r.areas.every((a) => !a.firstBrokenHere && a.deltas.every((d) => !d.isFirstBroken))).toBe(true);
    expect(r.panel.deltas.find((d) => d.deltaId === "d-0")?.retained).toBe(true);
    expect(r.panel.nextValidTransition).toBe(deltaLine(HUMAN));
  });
  it("an unplaced step (operation null) lands at the proof chamber only (FIELD_PANEL); placement repeats, never selects", () => {
    const r = render(presence(current([UNKNOWN])));
    expect(r.areas.map((a) => a.area)).toEqual(["proof-chamber"]);
    expect(r.panel.deltas[0].placedAt).toEqual(["the proof chamber"]);
    expect(r.panel.deltas[0].categories).toEqual(["UNPLACED"]);
  });
  it("no observation / unavailable / malformed → no area, no boundary, a panel that states the absence only", () => {
    for (const p of [{ kind: "none" } as const, { kind: "malformed" } as const, { kind: "observation", observation: { kind: "unavailable", reasonCode: "SEMANTIC_OBSERVATION_UNAVAILABLE" }, supersededByObjectChange: false } as const]) {
      const r = render(p);
      expect(r.areas).toEqual([]);
      expect(r.boundary).toBeNull();
      expect(r.panel.semantic).toBeNull();
      expect(r.panel.capability).toEqual([]);
      expect(r.panel.spoken).toHaveLength(1);
      expect(html(<GovernanceAttachment rendering={r.byArea["derived-chamber"]} />)).toBe("");
    }
  });
  it("superseded: areas keep their words and say so; canSend is treated as absent", () => {
    const r = render(presence(current([PROVIDER, HUMAN], { firstBrokenRelation: { predecessor: PROVIDER, broken: HUMAN } }), true));
    expect(r.byArea["question-set"]?.superseded).toBe(true);
    expect(r.panel.superseded).toBe(true);
    expect(r.panel.capability.find((c) => c.axis === "Can send")?.words).toBe("absent (observation superseded)");
    expect(r.panel.spoken.join(" ")).toContain("the Session changed afterwards");
  });
});

describe("§09.3 boundary card", () => {
  it("reads what stopped · requested in · why · after · HAR · placement; no holder, binding or grantor", () => {
    const r = render(presence(current([PROVIDER, HUMAN, GRANT], { firstBrokenRelation: { predecessor: PROVIDER, broken: HUMAN }, humanAuthorityRequired: [{ deltaId: "d-2", result: "AUTHORITY_BOUNDARY", reasonCode: "NOT_SESSION_CONTROLLER" }], partial: true })));
    expect(r.boundary).toEqual({
      whatStopped: "SELECT_PRIMARY_QUESTION · human command",
      requestedIn: "pick the primary question",
      why: "state boundary · SESSION_NOT_IN_QUESTION_SELECTION",
      after: "REQUEST_QUESTION_ANALYSIS",
      humanAuthorityRequired: [{ deltaId: "d-2", words: "AUTHORITY_BOUNDARY · NOT_SESSION_CONTROLLER" }],
      placedAt: ["the human question set"],
      partial: true,
    });
    expect(JSON.stringify(r.boundary)).not.toMatch(/holder|binding|grantor/i);
  });
  it("first in chain when the broken delta has no predecessor; Unknown operation when the broken operation is null", () => {
    const r = render(presence(current([UNKNOWN], { firstBrokenRelation: { predecessor: null, broken: UNKNOWN } })));
    expect(r.boundary?.after).toBe("first in chain");
    expect(r.boundary?.whatStopped).toBe("Unknown operation · unknown execution class");
    expect(r.boundary?.why).toBe("indeterminate");
  });
});

describe("components: words only (§10.4, §11.4, §18 forbidden list)", () => {
  const prominent = render(presence(current([PROVIDER, HUMAN, GRANT], { firstBrokenRelation: { predecessor: PROVIDER, broken: HUMAN }, humanAuthorityRequired: [{ deltaId: "d-2", result: "AUTHORITY_BOUNDARY", reasonCode: "NOT_SESSION_CONTROLLER" }] })));
  it("the attachment marker: field word, summary, one line per placed step, marks; prominence from FBR/HAR/provider; no control", () => {
    const q = html(<GovernanceAttachment rendering={prominent.byArea["question-set"]} />);
    expect(q).toContain('data-governance-attachment="question-set"');
    expect(q).toContain('data-prominence="prominent"');
    expect(q).toContain("1 crossed step placed here");
    expect(q).toContain("SELECT_PRIMARY_QUESTION · human command — state boundary · SESSION_NOT_IN_QUESTION_SELECTION");
    expect(q).toContain(">first broken relation<");
    expect(q).not.toMatch(/<button|<a |<input|<form|<select/);
    const d = html(<GovernanceAttachment rendering={prominent.byArea["derived-chamber"]} />);
    expect(d).toContain('data-prominence="explicit"');
    expect(d).toContain("Provider not executable");
    expect(d).toContain("Send not materialized");
    expect(d).not.toMatch(/denied|disabled|Send (allowed|unavailable)|Ready to send/);
    const a = html(<GovernanceAttachment rendering={prominent.byArea["authority-chamber"]} />);
    expect(a).toContain(">Human Authority required<");
    expect(a).not.toMatch(/approve|grant now|<button/i);
  });
  it("the panel: capability axes, basis, semantic observation, deltas with placement, boundary card, provider/send, ceiling, not materialized; no control; spoken facts", () => {
    const p = html(<GovernancePanel panel={prominent.panel} />);
    expect(p).toMatch(/<details class="proof-depth governance-panel" data-testid="governance-panel" data-observation="current">/);
    expect(p).toContain("Field / Governance");
    expect(p).toContain("Governance admissible");
    expect(p).toContain("false · MLT_EMPTY");
    expect(p).toContain("NO_ELIGIBLE_PROVIDER_ROUTE");
    expect(p).toContain('data-testid="governance-send">Send not materialized<');
    expect(p).toContain("3f9a00000000…");
    expect(p).toContain("rule set 26/2026-09-29");
    expect(p).toContain("Shown at: the human question set");
    expect(p).toContain("target: out of scope");
    expect(p).toContain("target: unresolved");
    expect(p).toContain('data-testid="boundary-card"');
    expect(p).toContain("Session-level proof ceiling (partial I-12)");
    expect(p).toContain("SEND relation (R-13) · evidence · provenance · HAR holder classes · SOURCE_RELATION");
    expect(p).not.toMatch(/<button|<a |<input|<form|<select/);
    expect(p).not.toMatch(/DeniedBanner|DecisionSection|BoundaryBanner|GovernancePanel</);
    expect(p).toContain("Governance for this session: Human Authority required.");
    expect(p).toContain("Human authority required for 1 requested step.");
  });
  it("the panel without a current observation states the absence only", () => {
    const none = render({ kind: "none" });
    const p = html(<GovernancePanel panel={none.panel} />);
    expect(p).toContain('data-observation="none"');
    expect(p).toContain("No governance statement is made without a current observation.");
    expect(p).not.toMatch(/Governance admissible|boundary-card|governance-deltas/);
  });
});

describe("source laws (PRESENTATION LOCATION != GOVERNANCE TRUTH; CROSSED FACT != UI COMPONENT)", () => {
  it("no backend component names, no send-like or approval control, no persistence or timers, no truth from the frontend", () => {
    for (const [name, src] of [["derivation", DERIVATION], ["attachment", ATTACHMENT], ["panel", PANEL]] as const) {
      expect(src, name).not.toMatch(/DeniedBanner|DecisionSection|BoundaryBanner|IndeterminateBanner/);
      expect(src, name).not.toMatch(/localStorage|sessionStorage|indexedDB|setTimeout|setInterval|fetch\(/);
      expect(src, name).not.toMatch(/"Send (allowed|disabled|unavailable)"|Ready to send|approve/i);
      expect(src, name).not.toMatch(/\brole\s*[!=]==?|isGovernanceRoot|isSessionController/);
    }
    expect(DERIVATION).not.toMatch(/sourceClause\.(includes|match|toLowerCase)|clauseText\.(includes|match)/); // placement never from text
    expect(ATTACHMENT).not.toMatch(/<button|<a |<input|<form|onClick/);
    expect(PANEL).not.toMatch(/<button|<a |<input|<form|onClick/);
    // the page wires every marker to exactly one derived area, never a fallback, never a guess
    const usages = PAGE.match(/<GovernanceAttachment rendering=\{[^}]*\}/g) ?? [];
    expect(usages.length).toBeGreaterThanOrEqual(7);
    for (const u of usages) expect(u).toMatch(/^<GovernanceAttachment rendering=\{rendering\.byArea\["[a-z-]+"\]\}$/);
    expect(usages.map((u) => /\["([a-z-]+)"\]/.exec(u)?.[1]).sort()).toEqual(["active-phase-chamber", "authority-chamber", "burst-panel", "decision-entry-chamber", "derived-chamber", "proof-chamber", "question-set"]);
    expect(PAGE).toMatch(/panel=\{rendering\.panel\}/);
  });
});
