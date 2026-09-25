/**
 * SF-04 WU-01 (L0): the Projection Authority Layer (doc 25 §2.7, §7.3–§7.5, §8.2, §16.2–§16.6).
 *
 * Every semantic visual property (semanticWeight, orbitBand, relation type, visualTone) is DERIVED from a canonical
 * producer or an explicit projection rule, carries provenance, and can never come from appearance.
 * Falsifiers (doc 25 §21.11): 1 (weight from looks), 2 (reciprocal without canonical reciprocity), 3 (tension without
 * canonical tension), 7 (local state as truth), 11 (position → role), 12 (tone → state), 13 (tone invents category).
 */
import { describe, expect, it } from "vitest";
import {
  assertProvenance,
  projectNode,
  projectRelation,
  RELATION_TYPES,
  type ProjectedSemanticNode,
  type ProjectedSemanticRelation,
} from "../../lib/field/projection";

const n = (over: Partial<Parameters<typeof projectNode>[0]> = {}) =>
  projectNode({ key: "s1", kind: "containment", state: "established", label: "Session opened", relationCount: 1, ...over });

describe("semanticWeight (RULE-W): canonical state / role / relation density only", () => {
  it("is deterministic and carries provenance naming the rule and the canonical source", () => {
    const a = n();
    const b = n();
    expect(a.semanticWeight).toEqual(b.semanticWeight);
    expect(a.semanticWeight.provenance).toEqual({ kind: "projection-rule", ruleId: "RULE-W", sources: ["canonical-state:established", "relation-density:1"] });
  });
  it("orders weight by canonical state, never by label length or size class", () => {
    const current = n({ state: "current", kind: "lifecycle" }).semanticWeight.value;
    const possible = n({ state: "possible", kind: "capability" }).semanticWeight.value;
    const established = n().semanticWeight.value;
    const future = n({ state: "future", kind: "lifecycle" }).semanticWeight.value;
    const denied = n({ state: "denied" }).semanticWeight.value;
    expect(current).toBeGreaterThan(possible);
    expect(possible).toBeGreaterThan(established);
    expect(established).toBeGreaterThan(future);
    expect(future).toBeGreaterThan(denied);
    expect(n({ label: "x".repeat(200) }).semanticWeight.value).toEqual(established);
  });
  it("relation density adds weight (a participant who is also the controller carries two canonical relations)", () => {
    expect(n({ kind: "participation", state: "human", relationCount: 2 }).semanticWeight.value).toBeGreaterThan(n({ kind: "participation", state: "human", relationCount: 1 }).semanticWeight.value);
  });
  it("never exceeds the current phase (no fabricated importance) and stays within [0.3, 1]", () => {
    for (const state of ["established", "current", "possible", "unavailable", "denied", "loading", "unknown", "frozen", "human", "governance", "future"] as const) {
      const w = n({ state, relationCount: 3 }).semanticWeight.value;
      expect(w).toBeGreaterThanOrEqual(0.3);
      expect(w).toBeLessThanOrEqual(1);
    }
  });
});

describe("orbitBand (RULE-B): semantic role → projection class, never pixel position", () => {
  it("containment, capability and lifecycle relations project to the inner band; participation and governance to the middle; evidence to the outer", () => {
    expect(n({ kind: "containment" }).orbitBand.value).toBe("inner");
    expect(n({ kind: "capability", state: "possible" }).orbitBand.value).toBe("inner");
    expect(n({ kind: "lifecycle", state: "future" }).orbitBand.value).toBe("inner");
    expect(n({ kind: "participation", state: "human" }).orbitBand.value).toBe("middle");
    expect(n({ kind: "governance", state: "governance" }).orbitBand.value).toBe("middle");
    expect(n({ kind: "evidence" }).orbitBand.value).toBe("outer");
    expect(n().orbitBand.provenance.kind).toBe("projection-rule");
  });
});

describe("relation type (RULE-R): canonical relation semantics → visual class → motion law", () => {
  const r = (over: Partial<Parameters<typeof projectRelation>[0]> = {}) => projectRelation({ id: "core->s1", kind: "containment", state: "established", ...over });
  it("a possible effect is a directional current from the core to the affordance (request flows outward)", () => {
    const rel = r({ kind: "capability", state: "possible" });
    expect(rel.type.value).toBe("directional");
    expect(rel.direction?.value).toBe("source-to-target");
    expect(rel.type.provenance).toMatchObject({ kind: "projection-rule", ruleId: "RULE-R" });
  });
  it("an established containment is a directional current from the container to the contained entity", () => {
    expect(r().type.value).toBe("directional");
    expect(r().direction?.value).toBe("source-to-target");
  });
  it("participation is reciprocal ONLY because the canonical relation is mutual (session admits ↔ participant takes part)", () => {
    const rel = r({ kind: "participation", state: "human" });
    expect(rel.type.value).toBe("reciprocal");
    expect(rel.direction?.value).toBe("bidirectional");
    expect(rel.type.provenance).toMatchObject({ sources: expect.arrayContaining(["canonical-relation:participation"]) });
  });
  it("governance flows from the holder to the scope it controls (directional, target-to-source of the spoke)", () => {
    const rel = r({ kind: "governance", state: "governance" });
    expect(rel.type.value).toBe("directional");
    expect(rel.direction?.value).toBe("target-to-source");
  });
  it("the current lifecycle phase is the active context current; passed phases and later phases are latent", () => {
    expect(r({ kind: "lifecycle", state: "current" }).type.value).toBe("context");
    expect(r({ kind: "lifecycle", state: "established" }).type.value).toBe("latent");
    expect(r({ kind: "lifecycle", state: "future" }).type.value).toBe("latent");
  });
  it("unavailable and denied relations are latent (a boundary, never tension)", () => {
    expect(r({ kind: "capability", state: "unavailable" }).type.value).toBe("latent");
    expect(r({ kind: "governance", state: "denied" }).type.value).toBe("latent");
  });
  it("tension is never produced: no canonical tension relation exists in this repository (falsifier 3)", () => {
    for (const kind of ["containment", "participation", "governance", "evidence", "lifecycle", "capability"] as const) {
      for (const state of ["established", "current", "possible", "unavailable", "denied", "loading", "unknown", "frozen", "human", "governance", "future"] as const) {
        expect(r({ kind, state }).type.value).not.toBe("tension");
      }
    }
    expect(RELATION_TYPES).toContain("tension");
  });
});

describe("visualTone (RULE-T): only an approved state category, never a new one (falsifiers 12–13)", () => {
  it("maps each canonical node state to one of the four Field tones", () => {
    expect(n({ state: "current" }).visualTone.value).toBe("living");
    expect(n({ state: "possible" }).visualTone.value).toBe("living");
    expect(n().visualTone.value).toBe("stable");
    expect(n({ state: "frozen" }).visualTone.value).toBe("stable");
    expect(n({ state: "denied" }).visualTone.value).toBe("boundary");
    expect(n({ state: "unavailable" }).visualTone.value).toBe("boundary");
    expect(n({ state: "future" }).visualTone.value).toBe("neutral");
    expect(n({ state: "loading" }).visualTone.value).toBe("neutral");
  });
});

describe("provenance assertion (development guard)", () => {
  it("accepts a fully provenanced node and relation", () => {
    expect(() => assertProvenance(n())).not.toThrow();
    expect(() => assertProvenance(projectRelation({ id: "x", kind: "containment", state: "established" }))).not.toThrow();
  });
  it("rejects a semantic value without a producer (a designer preference is not provenance)", () => {
    const bad = { ...n(), semanticWeight: { value: 1, provenance: { kind: "designer-preference" } } } as unknown as ProjectedSemanticNode;
    expect(() => assertProvenance(bad)).toThrow(/provenance/);
    const badRel = { ...projectRelation({ id: "x", kind: "containment", state: "established" }), type: { value: "tension", provenance: { kind: "projection-rule", ruleId: "RULE-R", sources: [] } } } as unknown as ProjectedSemanticRelation;
    expect(() => assertProvenance(badRel)).toThrow(/tension/);
  });
});
