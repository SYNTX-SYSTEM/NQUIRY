/**
 * CYAN-PCPG-04 falsifiers 1–16 at component level (static markup, no CSS) plus source laws 11–14, 16 (Architecture
 * 27 v4 §03 Level 0, §06.1, §07, §11.4, §15, §17, §21). Inputs pass the CYAN-PCPG-01 parser and the CYAN-PCPG-02
 * derivation first; the membrane never sees PCPG-R12/1 itself.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { GovernanceMembrane, PROMINENCE } from "../../components/field/GovernanceMembrane";
import { parseGovernanceObservation, type GovernanceObservation } from "../../lib/api/pcpgClient";
import { MEMBRANE_LABELS, MEMBRANE_WORDS, presentationOf, type ObservationPresence } from "../../lib/field/pcpgPresentation";

const WEB = join(__dirname, "..", "..");
const strip = (s: string) => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1").replace(/\{\/\*[\s\S]*?\*\/\}/g, "");
const COMPONENT_SRC = readFileSync(join(WEB, "components", "field", "GovernanceMembrane.tsx"), "utf8");
const PAGE_SRC = readFileSync(join(WEB, "app", "workspaces", "[workspaceId]", "sessions", "[sessionId]", "page.tsx"), "utf8");

const D = (over: Record<string, unknown> = {}) => ({ deltaId: "d-0", operation: "REQUEST_QUESTION_ANALYSIS", executionClass: "PROVIDER_COMPUTATION", target: null, sourceClause: "Analyse the questions", span: [0, 21], currentState: null, result: "INDETERMINATE", reasonCode: "DATA_GOVERNANCE_NOT_MATERIALIZED", flags: [], sessionProofCeiling: "GOVERNED", ...over });
const H = (over: Record<string, unknown> = {}) => D({ deltaId: "d-1", operation: "SELECT_PRIMARY_QUESTION", executionClass: "HUMAN_COMMAND", result: "STATE_BOUNDARY", reasonCode: "SESSION_NOT_IN_QUESTION_SELECTION", ...over });
function wire(deltas: unknown[] = [D()], chain: Record<string, unknown> = {}, cap: Record<string, unknown> = {}, over: Record<string, unknown> = {}): GovernanceObservation {
  return parseGovernanceObservation({
    kind: "current",
    contract: "PCPG-R12/1",
    basis: { rawIntentDigestSha256: "ab".repeat(32), derivationTime: "2026-10-01T11:17:00+00:00" },
    semanticObservation: { ruleSetVersion: "v", clauses: [], actions: [], unknownRelations: [], relationsTouched: [], declaredPurpose: null, semanticPurpose: null, purposeAlignment: null, semanticDrift: false },
    deltas,
    chain: { firstBrokenRelation: null, maximumLegitimateTransition: [], nextValidTransition: null, humanAuthorityRequired: [], partial: false, ...chain },
    capability: { governanceAdmissible: false, governanceAdmissibleReasons: ["MLT_EMPTY"], providerExecutable: false, providerExecutableReasons: ["NO_ELIGIBLE_PROVIDER_ROUTE"], canSend: false, ...cap },
    composedProofCeiling: null,
    ...over,
  });
}
const obs = (o: GovernanceObservation, superseded = false): ObservationPresence => ({ kind: "observation", observation: o, supersededByObjectChange: superseded });
const render = (p: ObservationPresence) => renderToStaticMarkup(<GovernanceMembrane presentation={presentationOf(p)} />);
const label = (html: string) => /data-membrane-label="([A-Z_]+)"/.exec(html)?.[1];
const UNAVAILABLE = obs(parseGovernanceObservation({ kind: "unavailable", reasonCode: "PROJECTION_INCOMPLETE" }));

describe("membrane states (falsifiers 1–8, 15)", () => {
  it("1. a Session with no observation shows only 'No observation' — quiet, no time, no capability words", () => {
    const html = render({ kind: "none" });
    expect(label(html)).toBe("NO_OBSERVATION");
    expect(html).toContain("No observation");
    expect(html).toContain('data-prominence="quiet"');
    expect(html).toContain('data-observation="none"');
    expect(html).not.toMatch(/observed at|Governance admissible|Can send|Send not|Boundary|Authority/);
  });
  it("2. a valid current observation renders exactly the derived membrane label and words", () => {
    const cases: [ObservationPresence, string][] = [
      [obs(wire([H({ result: "ALLOWED", reasonCode: null })])), "OBSERVED"],
      [obs(wire()), "PROVIDER_NOT_EXECUTABLE"],
      [obs(wire([H()], { partial: true })), "PARTIAL"],
      [obs(wire([H()], { firstBrokenRelation: { predecessor: null, broken: H() } })), "BOUNDARY_REACHED"],
      [obs(wire([H()], { humanAuthorityRequired: [{ deltaId: "d-1", result: "AUTHORITY_BOUNDARY", reasonCode: null }] })), "HUMAN_AUTHORITY_REQUIRED"],
      [UNAVAILABLE, "GOVERNANCE_UNAVAILABLE"],
      [obs(wire(), true), "SUPERSEDED"],
    ];
    for (const [presence, expected] of cases) {
      const html = render(presence);
      expect(label(html)).toBe(expected);
      expect(html).toContain(`>${MEMBRANE_WORDS[expected as keyof typeof MEMBRANE_WORDS]}<`);
      expect(html).toContain(`data-prominence="${PROMINENCE[expected as keyof typeof PROMINENCE]}"`);
    }
    expect(render(obs(wire()))).toContain("observed at");
    expect(Object.keys(PROMINENCE).sort()).toEqual([...MEMBRANE_LABELS].sort());
  });
  it("3./4. unavailable is 'Governance unavailable': not denied, no synthesized capability, boundary, authority, provider, proof or SEND words", () => {
    const html = render(UNAVAILABLE);
    expect(label(html)).toBe("GOVERNANCE_UNAVAILABLE");
    expect(html).toContain("Governance unavailable");
    expect(html).not.toMatch(/[Dd]enied|DENIED|Boundary|Authority required|Provider|admissible|Can send|Send|proof|observed at/);
    expect(html).toContain('data-observation="unavailable"');
    expect(render({ kind: "malformed" })).toContain("Governance unavailable");
  });
  it("5. Superseded has exactly the CYAN-PCPG-02 precedence: above FBR and HAR, below unavailable; canSend is said as absent", () => {
    const fbr = { firstBrokenRelation: { predecessor: null, broken: H({ result: "AUTHORITY_BOUNDARY" }) }, humanAuthorityRequired: [{ deltaId: "d-1", result: "AUTHORITY_BOUNDARY", reasonCode: null }] };
    expect(label(render(obs(wire([H({ result: "AUTHORITY_BOUNDARY" })], fbr), true)))).toBe("SUPERSEDED");
    expect(label(render(obs(wire([H({ result: "AUTHORITY_BOUNDARY" })], fbr), false)))).toBe("HUMAN_AUTHORITY_REQUIRED");
    expect(label(render({ kind: "observation", observation: UNAVAILABLE.kind === "observation" ? UNAVAILABLE.observation : (null as never), supersededByObjectChange: true }))).toBe("GOVERNANCE_UNAVAILABLE");
    const html = render(obs(wire([], {}, { canSend: true }), true));
    expect(html).toContain("Can send: absent (observation superseded).");
    expect(html).toContain('data-observation="superseded"');
  });
  it("6. 'Human Authority required' appears only from the derived input (AUTHORITY_BOUNDARY FBR or non-empty HAR)", () => {
    expect(render(obs(wire([H({ result: "AUTHORITY_BOUNDARY" })])))).not.toContain("Human Authority required");
    expect(render(obs(wire([H({ reasonCode: "HUMAN_AUTHORITY_REQUIRED" })])))).not.toContain("Human Authority required");
    const html = render(obs(wire([H()], { humanAuthorityRequired: [{ deltaId: "d-1", result: "GOVERNANCE_BOUNDARY", reasonCode: null }] })));
    expect(html).toContain("Human Authority required");
    expect(html).toContain('data-human-authority="required"');
    expect(render({ kind: "none" })).not.toContain("data-human-authority");
  });
  it("7. 'Boundary reached' appears only from a first broken relation", () => {
    expect(render(obs(wire([H({ result: "DENIED" })])))).not.toContain("Boundary reached");
    expect(render(obs(wire([H()], { partial: true })))).not.toContain("Boundary reached");
    expect(render(obs(wire([H()], { firstBrokenRelation: { predecessor: null, broken: H() } })))).toContain("Boundary reached");
  });
  it("8. 'Provider not executable' states two crossed facts and implies no provider call, selection, authorization or send", () => {
    const html = render(obs(wire()));
    expect(html).toContain("Provider not executable");
    expect(html).toContain("Provider executable: false (NO_ELIGIBLE_PROVIDER_ROUTE).");
    expect(html).toContain("Send not materialized.");
    expect(html).not.toMatch(/attempted|selected|authorized|Send allowed|Ready to send|<button|<a |<form/);
    expect(render(obs(wire([], {}, { providerExecutable: true, providerExecutableReasons: [] })))).not.toContain("Provider not executable");
  });
  it("15. a null proof ceiling stays unknown: the membrane shows no ceiling at all and never says proven, trusted, confidence, evidence or provenance", () => {
    const html = render(obs(wire([D({ sessionProofCeiling: null })], {}, {}, { composedProofCeiling: null })));
    expect(html).not.toMatch(/GOVERNED|proven|trusted|confidence|evidence|provenance|proof/i);
  });
});

describe("the membrane renders nothing it may not (falsifiers 9, 10, 16)", () => {
  it("9./10. canSend never creates a SEND control; the membrane never creates an action, button, link, form or input", () => {
    for (const presence of [obs(wire([], {}, { canSend: true })), obs(wire([], {}, { canSend: false })), { kind: "none" } as const, UNAVAILABLE]) {
      const html = render(presence);
      expect(html).not.toMatch(/<button|<a |<form|<input|<select|<textarea|onClick|role="button"|href=/);
      expect(html).not.toMatch(/Send allowed|Ready to send|sendGate|SEND gate/);
    }
    const t = render(obs(wire([], {}, { canSend: true })));
    expect(t).toContain("Can send: true (projection only).");
    expect(t).toContain("Send not materialized.");
  });
  it("16. the membrane shows no provenance or evidence: only the derived words, the observed-at time and the capability facts", () => {
    const html = render(obs(wire([D(), H()], { firstBrokenRelation: { predecessor: D(), broken: H() } })));
    expect(html).not.toMatch(/digest|rawIntent|deltaId|d-0|d-1|SELECT_PRIMARY_QUESTION|REQUEST_QUESTION_ANALYSIS|provenance|evidence/);
    expect(html).toContain("Boundary reached");
    expect(html).toContain("observed at");
  });
});

describe("membrane laws in the source (falsifiers 11–14, 17–19)", () => {
  const src = strip(COMPONENT_SRC);
  it("11./12. the component reads no raw PCPG-R12/1 and re-runs no derivation: it imports only presentation types", () => {
    expect(COMPONENT_SRC).toMatch(/import type \{[^}]*ObservationPresentation[^}]*\} from "\.\.\/\.\.\/lib\/field\/pcpgPresentation"/);
    expect(src).not.toMatch(/pcpgClient|parseGovernanceObservation|parsePromptObservation|submitPromptObservation|governanceObservation|"PCPG-R12\/1"|membraneLabel\(|presentationOf\(|categoriesOf|attachPresentation|firstBrokenRelation|humanAuthorityRequired\.length|chain\./);
  });
  it("13./14. the component reads no auth role, membership, binding or actor identity, and reconstructs no authority", () => {
    // `role="status"` is the ARIA landmark of the strip, not a user role: the law forbids reading or comparing a role
    expect(src).not.toMatch(/\.role\b|\brole\s*[!=]==?|viewer\.|isGovernanceRoot|isSessionController|\/auth\/me|authClient|bindingId|binding|membership|actorId|userId|holder|grantor/);
  });
  it("17./18. the Session organism stays the primary UI: the membrane is a child of the object core; no new page, route or dashboard", () => {
    // successor truth (CYAN-PCPG-05): the presence now comes from the observation state machine; the membrane stays
    // the single object-level consumer inside the core, fed by presentationOf only
    expect(PAGE_SRC).toMatch(/<ReconstructionNote field=\{effect\.field\} \/>\s*<GovernanceMembrane presentation=\{governance\} \/>\s*<\/FieldCore>/);
    expect(PAGE_SRC.match(/<GovernanceMembrane/g)?.length).toBe(1);
    expect(PAGE_SRC).toContain("const governance = presentationOf(observationPresence);");
    expect(PAGE_SRC).not.toMatch(/submitPromptObservation|parsePromptObservation|pcpgClient/);
  });
  it("19. attachment targets remain unrendered: no component or page imports the attachment relation", () => {
    expect(PAGE_SRC).not.toMatch(/pcpgAttachment|attachPresentation/);
    // successor truth (CYAN-PCPG-06): the membrane itself still never attaches; placement lives in GovernanceAttachment
    expect(COMPONENT_SRC).not.toMatch(/pcpgAttachment|attachPresentation|data-governance-attachment/);
  });
});
