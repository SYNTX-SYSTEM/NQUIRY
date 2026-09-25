/**
 * SF-04 (L1): the Symbiotic Field Organism's anatomy rendered to static markup, WITHOUT CSS (doc 25 §6–§12, §16).
 * Every semantic distinction asserted here survives with styling stripped; motion and encounter behaviour are proven
 * in the mocked browser lane (`tests/e2e/sf04-field.spec.ts`).
 *
 * Falsifiers (doc 25 §21.11): 1–3 (projection provenance on the DOM), 5 (organ is one body, not cards), 6 (context
 * organ never creates state: it only displays and hosts), 8 (trace = route nodes, never a breadcrumb), 9 (no
 * spinner in the core), 10 (semantic order = DOM order), 14 (accessibility: aria-live organ, textual states).
 */
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { RelationTrace } from "../../components/field/RelationTrace";
import { FieldCore } from "../../components/field/topology/FieldCore";
import { FieldStage, Plane, Planes, Topology } from "../../components/field/topology/FieldStage";
import { Orbit, arcPath, nodeContent, type OrbitNode } from "../../components/field/topology/Orbit";
import { challengeTrace } from "../../lib/field/position";

const core = { title: "Why did activation stall after onboarding?", stateText: "3 Sessions", meta: "SF-04 Inspection" };
const sessions: OrbitNode[] = [
  { key: "new", state: "possible", label: "New Session", actionLabel: "Open Session", onActivate: () => undefined, meta: "possible next relation", testId: "new-session-node" },
  { key: "s1", state: "established", label: "Session opened Sep 25, 2026, 2:25 AM", meta: "QUESTION_CAPTURE", href: "/s1" },
  { key: "s2", state: "unavailable", label: "Session opened Sep 25, 2026, 2:34 AM", meta: "QUESTION_CAPTURE" },
];
const governance: OrbitNode[] = [{ key: "g1", state: "governance", label: "Inspect Facilitator", meta: "SESSION_CONTROL_RIGHT · granted by Inspect Owner", size: "sm", relationCount: 2 }];
const participants: OrbitNode[] = [{ key: "h1", state: "human", label: "Facilitator Fay", meta: "participant", size: "sm" }];

function field(): string {
  return renderToStaticMarkup(
    <FieldStage mode="orbit" surface="challenge">
      <Topology layout={{ core, rings: [sessions.map((n) => nodeContent(n, "containment")), governance.map((n) => nodeContent(n, "governance"))] }}>
        <FieldCore kind="challenge" state="current" eyebrow="Challenge" title={core.title} stateText={core.stateText} meta={core.meta} />
        <Orbit kind="containment" ring={1} heading="Sessions" nodes={sessions} testId="sessions-list" />
        <Orbit kind="governance" ring={2} heading="Session control" nodes={governance} testId="challenge-governance-orbit" />
      </Topology>
      <Planes header={{ eyebrow: "Grown from", title: core.title, state: core.stateText }}>
        <Plane kind="action" labelledBy="a">
          <h2 id="a">Open a Session</h2>
        </Plane>
        <Plane kind="governance" labelledBy="g">
          <h2 id="g">Governance</h2>
          <span data-relation-key="g1">Inspect Facilitator</span>
        </Plane>
        <Plane kind="proof" labelledBy="p">
          <h2 id="p">Proof</h2>
        </Plane>
      </Planes>
    </FieldStage>,
  );
}

describe("Semantic Core Organism (doc 25 §6)", () => {
  it("has the anatomy layers aura → resonance rings → membrane → nucleus → micro-orbit, all decorative, and the identity as text", () => {
    const html = field();
    const order = ["core-aura", "core-rings", "core-membrane", "core-orbit-trace", "core-nucleus"].map((c) => html.indexOf(`class="${c}"`));
    expect(order.every((i) => i >= 0)).toBe(true);
    expect([...order].sort((a, b) => a - b)).toEqual(order);
    expect(html.match(/class="core-ring" data-ring="\d"/g)).toHaveLength(3);
    expect(html).toMatch(/class="core-aura" aria-hidden="true"/);
    expect(html).toMatch(/class="core-rings" aria-hidden="true"/);
    expect(html).toContain('class="core-state">3 Sessions');
    expect(html).toMatch(/<h1 id="challenge-core-title" class="core-title">Why did activation stall/);
  });
  it("carries the canonical state as an attribute AND as text; the core never spins (falsifier 9)", () => {
    const html = field();
    expect(html).toMatch(/class="core" data-core-kind="challenge" data-core-state="current"/);
    expect(html).not.toMatch(/spinner|progress/i);
  });
});

describe("Living Field Entity Layer (doc 25 §7): projected weight, band, tone and provenance on every node", () => {
  it("writes orbitBand, visualTone, role and the rule chain to the DOM; weight becomes mass, never a width", () => {
    const html = field();
    expect(html).toMatch(/class="node" data-key="new" data-node-state="possible"[^>]*data-band="inner" data-tone="living" data-role="core-adjacent" data-provenance="RULE-W;RULE-B;RULE-T"/);
    expect(html).toMatch(/data-key="s2"[^>]*data-tone="boundary"/);
    expect(html).toMatch(/data-key="g1"[^>]*data-band="middle" data-tone="stable" data-role="secondary"/);
    expect(html).toMatch(/data-key="new"[^>]*style="[^"]*--mass:\s*[\d.]+;--weight:\s*0\.9(;|")/);
    expect(html).not.toMatch(/class="node"[^>]*style="[^"]*width/);
  });
  it("has the node anatomy aura → membrane body → label → role indicator, with the relation state always in text", () => {
    const html = field();
    const node = html.slice(html.indexOf('class="node" data-key="s1"'), html.indexOf('class="node" data-key="s2"'));
    expect(node).toMatch(/<div class="node-body"><span class="node-aura" aria-hidden="true"><\/span><a [^>]*href="\/s1"[^>]*class="node-main"|<div class="node-body"><span class="node-aura" aria-hidden="true"><\/span><a [^>]*class="node-main"[^>]*href="\/s1"/);
    expect(node).toMatch(/<span class="node-role" aria-hidden="true" data-role="primary"><\/span><span class="visually-hidden">Relation state: <\/span>established/);
  });
  it("relation density raises the weight (a controller who is also a participant is heavier), never the label length", () => {
    const one = nodeContent({ ...governance[0], relationCount: 1 }, "governance").weight;
    const two = nodeContent(governance[0], "governance").weight;
    expect(two).toBeGreaterThan(one!);
    expect(nodeContent({ ...governance[0], label: "x".repeat(300), relationCount: 1 }, "governance").weight).toBe(one);
  });
});

describe("Relational Current System (doc 25 §8): the canonical relation decides the visual class, direction and layers", () => {
  it("renders one relation group per node with a curved base path, endpoint resonance, and a pulse per non-latent relation", () => {
    const html = field();
    expect(html.match(/<g class="relation"/g)).toHaveLength(4);
    expect(html.match(/<path class="path path-base" data-path="[a-z]+" d="M [\d. ]+ Q [\d. ]+ [\d. ]+"/g)).toHaveLength(4);
    // the travelling current is an HTML pulse on a CSS motion path (the SVG stays static); latent relations have none
    expect(html.match(/<span class="current-pulse" data-key="[^"]+" data-path="[a-z]+" data-relation-type="(directional|reciprocal|context)"[^>]*style="offset-path:path\(&quot;M [\d. ]+ Q [\d. ]+ [\d. ]+&quot;\)"/g)).toHaveLength(3);
    expect(html).not.toContain('class="current-pulse" data-key="s2"');
    expect(html.match(/class="endpoint endpoint-node"/g)).toHaveLength(4);
    expect(html).not.toMatch(/<line /);
  });
  it("a possible effect is a directional current core→node; an established containment is directional; governance flows node→core; a boundary is latent", () => {
    const html = field();
    expect(html).toMatch(/class="relation" data-key="new" data-path="possible" data-relation-type="directional" data-direction="source-to-target" data-provenance="RULE-R:canonical-relation:containment,canonical-state:possible"/);
    expect(html).toMatch(/data-key="s1" data-path="established" data-relation-type="directional" data-direction="source-to-target"/);
    expect(html).toMatch(/data-key="s2" data-path="unavailable" data-relation-type="latent" data-direction="none"/);
    expect(html).toMatch(/data-key="g1" data-path="governance" data-relation-type="directional" data-direction="target-to-source"/);
  });
  it("participation is reciprocal because the canonical relation is mutual; tension is never rendered (falsifiers 2, 3)", () => {
    const html = renderToStaticMarkup(<Orbit kind="participation" ring={2} heading="Participants" nodes={participants} />);
    expect(html).toMatch(/data-key="h1" data-path="established" data-relation-type="reciprocal" data-direction="bidirectional"/);
    expect(field()).not.toContain('data-relation-type="tension"');
    expect(html).not.toContain('data-relation-type="tension"');
  });
  it("the arc bend is deterministic per node key and bounded (never a harsh straight connector, never random)", () => {
    const a = arcPath(400, 400, 600, 300, "s1", 0.4);
    expect(arcPath(400, 400, 600, 300, "s1", 0.4)).toBe(a);
    expect(a).not.toBe(arcPath(400, 400, 600, 300, "s2", 0.4));
    const [, px, py] = a.match(/Q (-?[\d.]+) (-?[\d.]+)/)!;
    const sx = 400 + 200 * 0.4;
    const sy = 400 - 100 * 0.4;
    const mx = (sx + 600) / 2;
    const my = (sy + 300) / 2;
    const len = Math.hypot(600 - sx, 300 - sy);
    expect(Math.hypot(Number(px) - mx, Number(py) - my)).toBeLessThanOrEqual(0.12 * len + 0.2);
  });
});

describe("Contextual Semantic Organ (doc 25 §10): one body, chambers, membrane header, relation tokens", () => {
  it("is one aside grown from the active state with a live region and the state it grew from in text", () => {
    const html = field();
    expect(html).toMatch(/<aside class="organ" aria-label="Active semantic context" aria-live="polite" data-testid="context-organ"><div class="organ-bridge" aria-hidden="true"><\/div><header class="organ-header"/);
    expect(html).toContain('<p class="eyebrow">Grown from</p><p class="organ-title">Why did activation stall after onboarding?</p><p class="organ-state">3 Sessions</p>');
    expect(html.match(/<aside /g)).toHaveLength(1);
  });
  it("its instruments are chambers of the organ in semantic order (primary → relational → logic), not independent cards", () => {
    const html = field();
    const chambers = [...html.matchAll(/class="plane chamber" data-plane="(\w+)" data-chamber="(\w+)"/g)].map((m) => `${m[1]}:${m[2]}`);
    expect(chambers).toEqual(["action:primary", "governance:relational", "proof:logic"]);
    expect(html.indexOf('class="organ"')).toBeGreaterThan(html.indexOf('class="orbit" data-orbit="governance"'));
  });
  it("a relation token names the field entity it mirrors (reciprocity key), and the organ carries no state of its own", () => {
    const html = field();
    expect(html).toContain('<span data-relation-key="g1">Inspect Facilitator</span>');
    expect(html).toContain('data-key="g1"');
    expect(html).not.toMatch(/class="organ"[^>]*data-(state|selected|active)=/);
  });
});

describe("Traversal Trace (doc 25 §11): route nodes with an active membrane, a chip on phones, never a breadcrumb", () => {
  const trace = challengeTrace({
    workspace: { workspaceId: "w1", name: "Conversion inquiry", governedFounding: true },
    challenge: { challengeId: "c1", title: "Why signups dropped", description: null, createdAt: "2026-09-24T10:00:00Z" },
    sessions: [],
    sessionControllers: [],
    members: [],
    capabilities: {
      openSession: { available: false, reasonCode: "NO_CHALLENGE_SESSION_CONTROL:c1", reason: "…" },
      grantSessionControl: { available: false, reasonCode: "NOT_GOVERNANCE_ROOT", reason: "…" },
    },
  });
  const html = renderToStaticMarkup(<RelationTrace segments={trace} />);
  it("renders every coordinate as a route node with a membrane layer; the current node is marked structurally", () => {
    expect(html.match(/class="route-node"/g)).toHaveLength(trace.length);
    expect(html.match(/class="route-membrane" aria-hidden="true"/g)).toHaveLength(trace.length);
    expect(html).toMatch(/class="route-node" data-coordinate="challenge" data-status="current" aria-current="location"/);
    expect(html).not.toMatch(/breadcrumb/i);
  });
  it("offers the phone chip toggle (expanded state is local UI, aria-expanded + aria-controls) before the route list", () => {
    expect(html).toMatch(/<button type="button" class="trace-chip-toggle" aria-expanded="false" aria-controls="[^"]+"/);
    expect(html.indexOf("trace-chip-toggle")).toBeLessThan(html.indexOf("<ol"));
    expect(html).toContain("Show the route");
    expect(html).not.toMatch(/class="trace"[^>]*data-expanded/);
  });
  it("keeps the SF-01 contract: links only established parents, status words outside the link", () => {
    expect(html.match(/href=/g)).toHaveLength(2);
    expect(html).toContain("(not available now)");
  });
});

describe("Field stage projected state (doc 25 §13, §16.2): at rest nothing is encountered and the medium is present", () => {
  it("renders the atmosphere layers first (decorative) and no encounter attributes at rest", () => {
    const html = field();
    expect(html).toMatch(/class="field-stage"[^>]*style="--vec-x:\s*0;--vec-y:\s*0;--vec-on:\s*0">/);
    expect(html).toMatch(/class="topology"[^>]*><div class="stage-atmosphere" aria-hidden="true" data-testid="stage-atmosphere"><div class="pressure-zone"><\/div><div class="resonance-wash"><\/div><\/div><section class="core"/);
    expect(html).not.toMatch(/data-hover-key|data-encounter|data-resonating/);
  });
});
