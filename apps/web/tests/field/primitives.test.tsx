/**
 * SF-01 WU-SF01.3 (L1): semantic primitives rendered to static markup, i.e. WITHOUT CSS.
 * Every distinction asserted here must survive with styling stripped (21 §31, §35:
 * "no distinction exists only in hue"; falsifiers 21, 22, 24, 28).
 */
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { EffectIntent, EffectOutcome, ReconstructionNote } from "../../components/field/EffectSurface";
import { FieldFrame, FieldLayout, FieldZone } from "../../components/field/FieldFrame";
import { OriginMark, StateName } from "../../components/field/Origin";
import { ProofDepth } from "../../components/field/ProofDepth";
import { ReadBoundary } from "../../components/field/ReadBoundary";
import { RelationTrace } from "../../components/field/RelationTrace";
import { effectReducer, INITIAL_EFFECT_FIELD, type EffectEvent, type EffectField } from "../../lib/field/effectLifecycle";
import { SETTLED_KINDS } from "../../lib/field/outcomeSemantics";
import { challengeTrace } from "../../lib/field/position";

function field(...events: EffectEvent[]): EffectField {
  return events.reduce(effectReducer, INITIAL_EFFECT_FIELD);
}

function textOf(html: string): string {
  return html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}

const REQ: EffectEvent = { type: "request", relation: "rel", intentKey: "k" };

describe("RelationTrace", () => {
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

  it("is an ordered position description, not a breadcrumb", () => {
    expect(html).toContain('aria-label="Inquiry position"');
    expect(html).not.toMatch(/breadcrumb/i);
    expect(html).toMatch(/<ol[ >]/);
  });

  it("marks the current coordinate structurally and in words", () => {
    expect(html).toMatch(/aria-current="location"[^>]*>|data-status="current"/);
    expect(textOf(html)).toContain("Why signups dropped (current position)");
  });

  it("links established parents only; the unavailable Session relation is text with its status", () => {
    expect(html).toContain('href="/workspaces"');
    expect(html).toContain('href="/workspaces/w1"');
    expect(html.match(/href=/g)).toHaveLength(2);
    expect(textOf(html)).toContain("New Session (not available now)");
  });
});

describe("EffectIntent / EffectOutcome", () => {
  it("REQUESTED is announced as not yet committed and carries no outcome", () => {
    const f = field(REQ);
    const intent = renderToStaticMarkup(<EffectIntent field={f} relation="rel" />);
    expect(intent).toContain('data-effect="requested"');
    expect(intent).toContain('role="status"');
    expect(textOf(intent)).toMatch(/not yet committed/i);
    expect(renderToStaticMarkup(<EffectOutcome field={f} relation="rel" />)).toBe("");
  });

  it("renders only for its own relation (outcome stays attached to the relation that caused it)", () => {
    const f = field(REQ, { type: "settle", kind: "denied", reasonCode: "X" });
    expect(renderToStaticMarkup(<EffectOutcome field={f} relation="other" />)).toBe("");
    expect(renderToStaticMarkup(<EffectIntent field={f} relation="rel" />)).toBe("");
  });

  it("every settled kind is distinct in text and data attributes, with consequence and reconstruction", () => {
    const seen = new Set<string>();
    for (const kind of SETTLED_KINDS) {
      const html = renderToStaticMarkup(
        <EffectOutcome field={field(REQ, { type: "settle", kind, reasonCode: kind === "committed" ? null : "RC" })} relation="rel" />,
      );
      expect(html).toContain('data-testid="command-outcome"');
      expect(html).toContain(`data-outcome="${kind}"`);
      expect(html).toMatch(/data-consequence="(committed|none|unknown)"/);
      expect(html).toContain('data-reconstruction="not_started"');
      seen.add(textOf(html));
    }
    expect(seen.size).toBe(SETTLED_KINDS.length);
  });

  it("the commit marker claims a re-read only after the re-read is done", () => {
    const committed = field(REQ, { type: "settle", kind: "committed", reasonCode: null }, { type: "reconstruction", result: "reading" });
    expect(textOf(renderToStaticMarkup(<EffectOutcome field={committed} relation="rel" />))).not.toMatch(/was re-read/);
    const done = effectReducer(committed, { type: "reconstruction", result: "done" });
    expect(textOf(renderToStaticMarkup(<EffectOutcome field={done} relation="rel" />))).toMatch(
      /The state shown was re-read from the canonical source\./,
    );
  });

  it("C3-06: committed + failed reconstruction says committed, never unchanged, and offers a re-read", () => {
    const f = field(
      REQ,
      { type: "settle", kind: "committed", reasonCode: null },
      { type: "reconstruction", result: "reading" },
      { type: "reconstruction", result: "failed" },
    );
    const html = renderToStaticMarkup(<EffectOutcome field={f} relation="rel" onReread={() => undefined} />);
    expect(textOf(html)).toMatch(/The change committed, but the current state could not be re-read/);
    expect(textOf(html)).not.toMatch(/no change|unchanged|did not commit/i);
    expect(html).toContain("Re-read current state");
  });

  it("network failure on a mutation reads as unknown consequence, never as 'nothing changed'", () => {
    const html = renderToStaticMarkup(
      <EffectOutcome field={field(REQ, { type: "settle", kind: "network_failure", reasonCode: "NETWORK_FAILURE" })} relation="rel" />,
    );
    expect(html).toContain('data-consequence="unknown"');
    expect(textOf(html)).not.toMatch(/nothing (is assumed to have )?changed|no change was made/i);
  });

  it("keeps F01 contract hooks: reason element with an exact reason code, and a committed test id", () => {
    const denied = renderToStaticMarkup(
      <EffectOutcome field={field(REQ, { type: "settle", kind: "denied", reasonCode: "BND_004_DENIED" })} relation="rel" reasonTestId="add-member-error" committedTestId="add-member-success" />,
    );
    expect(denied).toMatch(/data-testid="add-member-error"[^>]*>BND_004_DENIED</);
    expect(denied).not.toContain("add-member-success");
    const ok = renderToStaticMarkup(
      <EffectOutcome field={field(REQ, { type: "settle", kind: "committed", reasonCode: null })} relation="rel" reasonTestId="add-member-error" committedTestId="add-member-success" />,
    );
    expect(ok).toContain('data-testid="add-member-success"');
    expect(ok).not.toContain("add-member-error");
  });
});

describe("ReconstructionNote", () => {
  it("marks the projection as last confirmed only when a re-read failed", () => {
    const settled = field(REQ, { type: "settle", kind: "stale", reasonCode: "STALE_VERSION" }, { type: "reconstruction", result: "reading" });
    expect(renderToStaticMarkup(<ReconstructionNote field={settled} />)).toBe("");
    const failed = effectReducer(settled, { type: "reconstruction", result: "failed" });
    const html = renderToStaticMarkup(<ReconstructionNote field={failed} />);
    expect(html).toContain('data-projection="last-confirmed"');
    expect(textOf(html)).toMatch(/Last confirmed state/);
    const done = effectReducer(settled, { type: "reconstruction", result: "done" });
    expect(renderToStaticMarkup(<ReconstructionNote field={done} />)).toBe("");
  });
});

describe("FieldFrame", () => {
  const html = renderToStaticMarkup(
    <FieldFrame trace={[{ coordinate: "access", label: "Workspaces", status: "current" }]} regime="workspace-access" exit={null}>
      <h1>Workspaces</h1>
      <FieldLayout
        primary={<FieldZone zone="centre" label="c">centre</FieldZone>}
        secondary={<FieldZone zone="depth" label="d">depth</FieldZone>}
      />
    </FieldFrame>,
  );

  it("puts position in the header and the active regime on <main>", () => {
    expect(html.indexOf('aria-label="Inquiry position"')).toBeLessThan(html.indexOf("<main"));
    expect(html).toContain('data-field-regime="workspace-access"');
    expect(html).toContain('href="#main"');
  });

  it("DOM order is the relational order: position → centre → depth", () => {
    expect(html.indexOf("Inquiry position")).toBeLessThan(html.indexOf('data-field-zone="centre"'));
    expect(html.indexOf('data-field-zone="centre"')).toBeLessThan(html.indexOf('data-field-zone="depth"'));
  });

  it("adds no heading of its own (the page keeps exactly one h1)", () => {
    expect(html.match(/<h1/g)).toHaveLength(1);
  });
});

describe("ReadBoundary", () => {
  it("names the read boundary without claiming any effect", () => {
    const html = renderToStaticMarkup(<ReadBoundary kind="not_found" reasonCode="CHALLENGE_NOT_FOUND" />);
    expect(html).toContain('data-outcome="not_found"');
    expect(html).toContain('role="alert"');
    expect(textOf(html)).toContain("The referenced context is not available in the confirmed scope.");
    expect(textOf(html)).not.toMatch(/committed|no change/i);
  });

  it("puts the exact reason code in an element that can carry a legacy test id", () => {
    const html = renderToStaticMarkup(<ReadBoundary kind="denied" reasonCode="NOT_A_WORKSPACE_MEMBER" reasonTestId="orientation-denied" />);
    expect(html).toMatch(/data-testid="orientation-denied"[^>]*>NOT_A_WORKSPACE_MEMBER</);
  });
});

describe("ProofDepth", () => {
  it("is closed-by-default native disclosure (keyboard reachable, no trap, returns in place)", () => {
    const html = renderToStaticMarkup(
      <ProofDepth depth="D2" title="Authority for opening Sessions">
        <p>binding</p>
      </ProofDepth>,
    );
    expect(html).toMatch(/^<details[^>]*data-depth="D2"/);
    expect(html).not.toMatch(/<details[^>]*\sopen/);
    expect(html).toMatch(/<summary[^>]*>.*Authority for opening Sessions/);
    expect(textOf(html)).toContain("proof, verify");
    expect(html).toContain("binding");
  });
});

describe("Origin grammar", () => {
  it("each origin class carries an accessible origin name, not only a style", () => {
    expect(textOf(renderToStaticMarkup(<OriginMark origin="system-state">DRAFT</OriginMark>))).toBe("System state: DRAFT");
    expect(textOf(renderToStaticMarkup(<OriginMark origin="human-source">q</OriginMark>))).toBe("Human source: q");
    expect(textOf(renderToStaticMarkup(<OriginMark origin="external-evidence">e</OriginMark>))).toBe("External evidence: e");
  });

  it("AI-derived cannot render without source lineage (AI DERIVED → visible source lineage)", () => {
    const html = renderToStaticMarkup(
      <OriginMark origin="ai-derived" lineage="frozen question set">x</OriginMark>,
    );
    expect(textOf(html)).toBe("AI-derived from frozen question set: x");
    expect(() => renderToStaticMarkup(<OriginMark origin="ai-derived">x</OriginMark>)).toThrow();
  });

  it("human source and AI-derived never share markup identity", () => {
    const h = renderToStaticMarkup(<OriginMark origin="human-source">x</OriginMark>);
    const a = renderToStaticMarkup(<OriginMark origin="ai-derived" lineage="s">x</OriginMark>);
    expect(h).toContain('data-origin="human-source"');
    expect(a).toContain('data-origin="ai-derived"');
  });

  it("StateName renders a canonical state as system state", () => {
    const html = renderToStaticMarkup(<StateName state="DRAFT" />);
    expect(html).toContain('data-origin="system-state"');
    expect(textOf(html)).toBe("System state: DRAFT");
  });
});
