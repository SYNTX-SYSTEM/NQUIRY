/**
 * SF-05 WU-26.3 (L1): the semantic chamber grammar rendered to static markup, WITHOUT CSS (doc 26 §16–§26).
 * Every distinction asserted here survives with styling stripped: ACTION ≠ AUTHORITY ≠ ROLE ≠ MEMBERSHIP ≠
 * PARTICIPATION ≠ PROOF ≠ IDENTIFIER ≠ BOUNDARY (doc 26 §42 falsifiers 2–5, 7).
 */
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { Unavailable } from "../../components/f02/Unavailable";
import { AuthorityRelation, BoundaryMark, boundaryClassOf, ChamberHead, Identifiers, ParticipationRoster, ProvenanceSpine, Token } from "../../components/field/chambers";
import { Plane } from "../../components/field/topology/FieldStage";

describe("Plane carries its semantic chamber class (doc 26 §17)", () => {
  it("defaults the class from the relation kind and accepts a more specific class; contracts data-plane/data-chamber/data-relation stay", () => {
    const a = renderToStaticMarkup(<Plane kind="governance" labelledBy="x"><h2 id="x">A</h2></Plane>);
    expect(a).toMatch(/class="plane chamber" data-plane="governance" data-chamber="relational" data-semantic="authority" data-relation="governance"/);
    const b = renderToStaticMarkup(<Plane kind="governance" semantic="participation" labelledBy="x"><h2 id="x">B</h2></Plane>);
    expect(b).toContain('data-semantic="participation"');
    expect(b).toContain('<span class="chamber-contour" aria-hidden="true"></span>');
  });
});

describe("Authority is a relation, not a badge (doc 26 §20)", () => {
  const html = renderToStaticMarkup(
    <ul>
      <AuthorityRelation bindingKey="b1" authorityClass="SESSION_CONTROL_RIGHT" holderName="Inspect Facilitator" holderKey="b1" grantedByName="Inspect Owner" scope="CHALLENGE:22222222-2222-4222-8222-222222222222" scopeLabel="this Challenge" held={false} />
    </ul>,
  );
  it("renders SOURCE → AUTHORITY → HOLDER → SCOPE in that order, each in words", () => {
    const order = ["granted by", "authority", "held by", "scope"].map((w) => html.indexOf(`<span class="chain-role">${w}</span>`));
    expect(order.every((i) => i >= 0)).toBe(true);
    expect([...order].sort((a, b) => a - b)).toEqual(order);
    expect(html).toContain("Inspect Owner");
    // the class breaks only at its own underscores (<wbr>), never mid-word
    expect(html).toMatch(/class="chain-value tag authority"><span>SESSION_<wbr\/><\/span><span>CONTROL_<wbr\/><\/span><span>RIGHT<\/span>/);
    expect(html).toContain('data-relation-key="b1">Inspect Facilitator');
    expect(html).toContain("this Challenge");
  });
  it("keeps the scope type on the DOM so CHALLENGE scope never reads as SESSION scope", () => {
    expect(html).toMatch(/class="authority-relation" data-binding="b1" data-scope-type="CHALLENGE" data-held="false"/);
    expect(html).toContain('<code class="token"');
  });
});

describe("Participation: one person, several relations (doc 26 §21)", () => {
  it("renders one entry per person with separate relation marks: role ≠ participant ≠ controller", () => {
    const html = renderToStaticMarkup(
      <ParticipationRoster testId="participants-list" people={[{ userId: "u-fac", name: "Fay", relations: ["facilitator", "participant", "controller"], relationKey: "p-u-fac" }, { userId: "u-c1", name: "Kim", relations: ["contributor"] }]} />,
    );
    expect(html.match(/class="roster-person"/g)).toHaveLength(2);
    expect(html).toContain('<span class="relation-mark" data-relation-kind="facilitator">Facilitator role</span>');
    expect(html).toContain('data-relation-kind="participant">participant</span>');
    expect(html).toContain('data-relation-kind="controller">Session controller</span>');
    expect(html).not.toContain('data-relation-kind="participant">Session controller');
  });
});

describe("Proof is a provenance spine (doc 26 §22) and identifiers stay contained (§23)", () => {
  it("renders the chain in order with commit and authority source present", () => {
    const html = renderToStaticMarkup(
      <ProvenanceSpine testId="session-last-transition" steps={[{ kind: "state", label: "Current state", value: "QUESTION_CAPTURE" }, { kind: "actor", label: "Established by", value: "CMD_COMPLETE_BURST by Fay" }, { kind: "authority", label: "Authority source", value: "SESSION_CONTROL_RIGHT" }, { kind: "commit", label: "Commit", value: <Token value="550446e3-1dce-4cf3-a58d-be57a95d5672" /> }, { kind: "time", label: "At", value: "Sep 25, 2026" }]} />,
    );
    const kinds = [...html.matchAll(/data-kind="(\w+)"/g)].map((m) => m[1]);
    expect(kinds).toEqual(["state", "actor", "authority", "commit", "time"]);
    expect(html).toContain("SESSION_CONTROL_RIGHT");
    expect(html).toContain("550446e3-");
  });
  it("breaks a technical token only at its separators and offers copy without making the id a title", () => {
    const html = renderToStaticMarkup(<Identifiers items={[{ label: "Session", value: "7f262f9b-a1f0-5c57-b183-5290761127c4", testId: "sid" }]} />);
    expect(html).toContain('<dt>Session</dt>');
    expect(html).toContain('<code class="token" data-testid="sid"><span>7f262f9b-<wbr/></span><span>a1f0-<wbr/></span>');
    expect(html).toContain('aria-label="Copy Session"');
    expect(html).not.toMatch(/<h[1-6][^>]*>7f262f9b/);
  });
});

describe("Boundary classes are distinct and never an error (doc 26 §26)", () => {
  it("classifies server reasons by the server's own vocabulary; unknown = currently not possible", () => {
    expect(boundaryClassOf("NO_CHALLENGE_SESSION_CONTROL:c1")).toBe("MISSING_AUTHORITY");
    expect(boundaryClassOf("NOT_GOVERNANCE_ROOT")).toBe("MISSING_AUTHORITY");
    expect(boundaryClassOf("NOT_A_PARTICIPANT")).toBe("MISSING_PARTICIPATION");
    expect(boundaryClassOf("SESSION_NOT_IN_STATE")).toBe("MISSING_PREREQUISITE");
    expect(boundaryClassOf("NOT_RELEVANT_IN_STATE")).toBe("MISSING_PREREQUISITE");
    expect(boundaryClassOf("AI_FORBIDDEN_IN_HUMAN_ONLY_BURST")).toBe("SEMANTIC_PROHIBITION");
    expect(boundaryClassOf("SOMETHING_ELSE")).toBe("CURRENTLY_NOT_POSSIBLE");
    expect(boundaryClassOf(null)).toBe("CURRENTLY_NOT_POSSIBLE");
  });
  it("renders the class in words and structure with the verbatim reason; no alert role", () => {
    const html = renderToStaticMarkup(<Unavailable capability={{ available: false, reasonCode: "NO_CHALLENGE_SESSION_CONTROL:c1", reason: "Opening a Session requires SESSION_CONTROL_RIGHT." }} testId="session-create-unavailable" />);
    expect(html).toMatch(/class="boundary-mark" data-boundary="MISSING_AUTHORITY" data-testid="session-create-unavailable" data-reason-code="NO_CHALLENGE_SESSION_CONTROL:c1"/);
    expect(html).toContain('<span class="boundary-class">missing authority</span>');
    expect(html).toContain("Opening a Session requires SESSION_CONTROL_RIGHT.");
    expect(html).not.toContain('role="alert"');
    const irreversible = renderToStaticMarkup(<BoundaryMark boundary="IRREVERSIBLE_CONFIRMATION">Freezing cannot be undone.</BoundaryMark>);
    expect(irreversible).toContain("irreversible — confirmation required");
  });
});

describe("Chamber head", () => {
  it("names the chamber with a heading and a decorative glyph carrying the semantic class", () => {
    const html = renderToStaticMarkup(<ChamberHead id="t" semantic="question" title="Protected question burst" marker="HUMAN_ONLY" />);
    expect(html).toContain('<svg class="chamber-glyph" viewBox="0 0 20 20" aria-hidden="true" focusable="false" data-semantic="question">');
    expect(html).toContain('<h2 id="t" class="chamber-title">Protected question burst</h2>');
    expect(html).toContain('<span class="chamber-marker">HUMAN_ONLY</span>');
  });
});
