/**
 * SF-03 WU-SF03.2 / WU-SF03.5 (L1): the topology primitives render the content-aware layout, the readable lifecycle
 * labels and the reciprocity contract (doc 23 §7, §8, §13.5). Static markup, no CSS; event behaviour is proven in
 * the mocked browser lane (`tests/e2e/sf03-field.spec.ts`).
 */
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { FieldCore } from "../../components/field/topology/FieldCore";
import { FieldStage, Plane, Topology } from "../../components/field/topology/FieldStage";
import { Orbit, nodeContent, type OrbitNode } from "../../components/field/topology/Orbit";
import { estimateCoreBox } from "../../lib/field/geometry";
import { relationOfOrbit, relationOfPlane } from "../../lib/field/reciprocity";
import { lifecycleEmphasis } from "../../lib/field/topology";

const core = { title: "Why did activation stall after onboarding?", stateText: "3 Sessions", meta: "SF-02 Inspection" };
const sessions: OrbitNode[] = [
  { key: "new", state: "possible", label: "New Session", actionLabel: "Open Session", onActivate: () => undefined, meta: "possible next relation", testId: "new-session-node" },
  { key: "s1", state: "established", label: "Session opened Sep 25, 2026, 2:25 AM", meta: "QUESTION_CAPTURE", href: "/s1" },
  { key: "s2", state: "established", label: "Session opened Sep 25, 2026, 2:34 AM", meta: "QUESTION_CAPTURE", href: "/s2" },
];
const governance: OrbitNode[] = [{ key: "g1", state: "governance", label: "Inspect Facilitator", meta: "SESSION_CONTROL_RIGHT · granted by Inspect Owner", size: "sm" }];

function field(): string {
  return renderToStaticMarkup(
    <FieldStage mode="orbit" surface="challenge">
      <Topology layout={{ core, rings: [sessions.map((n) => nodeContent(n, "containment")), governance.map((n) => nodeContent(n, "governance"))] }}>
        <FieldCore kind="challenge" state="current" eyebrow="Challenge" title={core.title} stateText={core.stateText} meta={core.meta} />
        <Orbit kind="containment" ring={1} heading="Sessions" nodes={sessions} testId="sessions-list" />
        <Orbit kind="governance" ring={2} heading="Session control" nodes={governance} testId="challenge-governance-orbit" />
      </Topology>
      <Plane kind="governance" labelledBy="g">
        <h2 id="g">Governance</h2>
      </Plane>
    </FieldStage>,
  );
}

describe("Topology + Orbit render the content-aware geometry (doc 23 §7)", () => {
  it("positions every node by the layout in px from the stage centre (no fixed ring), one path per node, an ellipse per ring", () => {
    const html = field();
    const xs = [...html.matchAll(/--x:\s*(-?\d+(?:\.\d+)?)px;--y:\s*(-?\d+(?:\.\d+)?)px/g)].map((m) => `${m[1]},${m[2]}`);
    expect(xs).toHaveLength(4);
    expect(new Set(xs).size).toBe(4);
    expect(html.match(/<path class="path path-base"/g)).toHaveLength(4); // SF-04: curved relation currents (doc 25 §8)
    expect(html.match(/<ellipse class="ring"/g)).toHaveLength(2);
  });
  it("never sets a fixed width on a node: the frame follows the content (falsifier 11)", () => {
    expect(field()).not.toMatch(/class="node"[^>]*style="[^"]*width/);
  });
  it("exposes the fit verdict on the topology so the stage can fall back to the stack when content cannot fit", () => {
    expect(field()).toMatch(/class="topology" data-fit="(fits|overflow)"/);
  });
  it("names the relation family on the orbit and on the instrument (reciprocity contract)", () => {
    const html = field();
    expect(html).toMatch(/class="orbit" data-orbit="containment" data-relation="action"/);
    expect(html).toMatch(/class="orbit" data-orbit="governance" data-relation="governance"/);
    expect(html).toMatch(/class="plane chamber" data-plane="governance" data-chamber="relational" data-semantic="authority" data-relation="governance"/); // SF-04/SF-05: a semantic chamber of the organ
    expect(relationOfOrbit("lifecycle")).toBe("action");
    expect(relationOfOrbit("participation")).toBe("governance");
    expect(relationOfPlane("human")).toBe("action");
    expect(relationOfPlane("proof")).toBe("proof");
  });
  it("estimates the core from the same content the core renders", () => {
    expect(estimateCoreBox(core).w).toBeGreaterThanOrEqual(196);
    expect(nodeContent(sessions[0]).label).toBe("Open Session");
    expect(nodeContent(sessions[1]).meta).toBe("QUESTION_CAPTURE");
  });
});

describe("lifecycle emphasis (doc 23 §13.5): every phase keeps a readable label; gravity is emphasis, not visibility", () => {
  const phases = ["DRAFT", "SETUP", "CHALLENGE_CAPTURE", "QUESTION_GENERATION", "QUESTION_CAPTURE", "ANALYSIS"].map((state, i) => ({
    state,
    status: (i < 2 ? "done" : i === 2 ? "current" : "upcoming") as "done" | "current" | "upcoming",
  }));
  it("gives full emphasis to passed, current and the next phase, low emphasis to later phases", () => {
    const e = lifecycleEmphasis(phases);
    expect(e.get("DRAFT")).toBe("full");
    expect(e.get("QUESTION_GENERATION")).toBe("full");
    expect(e.get("QUESTION_CAPTURE")).toBe("low");
    expect(e.get("ANALYSIS")).toBe("low");
    expect(e.size).toBe(phases.length);
  });
  it("a low-emphasis node still renders its label visibly (not assistive-only)", () => {
    const html = renderToStaticMarkup(
      <FieldStage mode="orbit" surface="session">
        <Topology layout={{ core, rings: [[{ label: "Analysis", size: "sm" }]] }}>
          <Orbit kind="lifecycle" ring={1} heading="Lifecycle" nodes={[{ key: "a", state: "future", label: "Analysis", size: "sm", emphasis: "low" }]} testId="session-phases" />
        </Topology>
      </FieldStage>,
    );
    expect(html).toMatch(/data-emphasis="low"/);
    expect(html).toMatch(/<span class="node-label">Analysis<\/span>/);
  });
});
