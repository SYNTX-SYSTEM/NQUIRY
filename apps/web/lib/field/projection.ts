/**
 * SF-04 Projection Authority Layer (doc 25 §2.7, §4 [7], §5.2, §7.3–§7.5, §8.2, §16.2–§16.6, §21.2).
 *
 *   DOMAIN / GOVERNANCE / APPLICATION TRUTH → CANONICAL FIELD RELATION → CANONICAL STATE
 *   → APPROVED PROJECTION RULE → VISUAL FIELD MODEL → MOTION SEMANTICS → RENDERED EFFECT
 *
 * Everything in this module is DERIVED PROJECTION STATE: pure, deterministic functions from canonical inputs the
 * pages already read (capabilities, projections, lifecycle phases, participants, authority bindings — see
 * SF-02/WU-SF02.0 for the binding of every relation kind to its producer) to the visual semantics the organism
 * renders. Every semantic value is a `ProjectedValue` with `ProjectionProvenance`; nothing here reads the DOM,
 * a pixel position, a viewport, an animation or a designer preference (falsifiers 1, 2, 3, 7, 11, 12, 13).
 *
 * The rules are named so that review can trace any visible mass, band, current or tone back to them:
 *   RULE-W  semanticWeight  ← canonical node state + relation density
 *   RULE-B  orbitBand       ← relation kind (semantic role of the orbit)
 *   RULE-R  relation type   ← relation kind + canonical state (never `tension`: no canonical tension relation exists)
 *   RULE-T  visualTone      ← canonical node state → one of the four approved Field tones (22 §18)
 */
import type { OrbitKind } from "./reciprocity";
import type { NodeState } from "./topology";

export type ProjectionProvenance =
  | { readonly kind: "canonical-state"; readonly sourceId: string }
  | { readonly kind: "canonical-relation"; readonly sourceId: string }
  | { readonly kind: "canonical-authority-result"; readonly sourceId: string }
  | { readonly kind: "canonical-lifecycle-state"; readonly sourceId: string }
  | { readonly kind: "projection-rule"; readonly ruleId: string; readonly sources: readonly string[] }
  | { readonly kind: "projection-local-interaction"; readonly interaction: "hover" | "focus" | "preview" | "viewport" | "reduced-motion" };

export type ProjectedValue<T> = { readonly value: T; readonly provenance: ProjectionProvenance };

export const RELATION_TYPES = ["reciprocal", "directional", "latent", "context", "tension"] as const;
export type RelationType = (typeof RELATION_TYPES)[number];
export type RelationDirection = "source-to-target" | "target-to-source" | "bidirectional";
export type OrbitBand = "inner" | "middle" | "outer";
/** The four approved Field tones (22 §18): cyan living, blue stable, red boundary, neutral. */
export type VisualTone = "living" | "stable" | "boundary" | "neutral";

export type CanonicalNodeInput = {
  readonly key: string;
  /** The orbit's semantic role: which canonical relation family the node belongs to (22 §13.4). */
  readonly kind: OrbitKind;
  /** The canonical node state (22 §14.2), already derived from the projection by the page. */
  readonly state: NodeState;
  readonly label: string;
  /** Number of canonical relations the entity holds to the core context (e.g. participant + controller = 2). */
  readonly relationCount?: number;
};

export type ProjectedSemanticNode = {
  readonly id: string;
  readonly label: string;
  readonly role: ProjectedValue<"core-adjacent" | "primary" | "secondary" | "peripheral">;
  readonly semanticWeight: ProjectedValue<number>;
  readonly orbitBand: ProjectedValue<OrbitBand>;
  readonly visualTone: ProjectedValue<VisualTone>;
  readonly accessibilityLabel: string;
};

export type CanonicalRelationInput = {
  readonly id: string;
  readonly kind: OrbitKind;
  readonly state: NodeState;
};

export type ProjectedSemanticRelation = {
  readonly id: string;
  /** The core context is always the source of a spoke; the node is the target. */
  readonly sourceId: "core";
  readonly targetId: string;
  readonly type: ProjectedValue<RelationType>;
  readonly weight: ProjectedValue<number>;
  readonly direction?: ProjectedValue<RelationDirection>;
  readonly accessibilityLabel: string;
};

/** RULE-W: base weight by canonical state (the current phase is the ceiling; boundaries are the floor). */
const BASE_WEIGHT: Readonly<Record<NodeState, number>> = {
  current: 1,
  possible: 0.9,
  human: 0.72,
  governance: 0.75,
  established: 0.7,
  frozen: 0.7,
  loading: 0.5,
  unknown: 0.45,
  future: 0.45,
  unavailable: 0.5,
  denied: 0.4,
};

export function projectNode(input: CanonicalNodeInput): ProjectedSemanticNode {
  const density = Math.max(1, input.relationCount ?? 1);
  // RULE-W: weight = base(state) + 0.08 per additional canonical relation, capped at the current phase's weight
  const weight = Math.min(BASE_WEIGHT.current, Math.round((BASE_WEIGHT[input.state] + 0.08 * (density - 1)) * 100) / 100);
  const wSources = [`canonical-state:${input.state}`, `relation-density:${density}`];
  const band = orbitBandOf(input.kind);
  return {
    id: input.key,
    label: input.label,
    role: { value: roleOf(input.kind, input.state), provenance: { kind: "projection-rule", ruleId: "RULE-B", sources: [`canonical-relation:${input.kind}`, `canonical-state:${input.state}`] } },
    semanticWeight: { value: weight, provenance: { kind: "projection-rule", ruleId: "RULE-W", sources: wSources } },
    orbitBand: { value: band, provenance: { kind: "projection-rule", ruleId: "RULE-B", sources: [`canonical-relation:${input.kind}`] } },
    visualTone: { value: toneOf(input.state), provenance: { kind: "projection-rule", ruleId: "RULE-T", sources: [`canonical-state:${input.state}`] } },
    accessibilityLabel: `${input.label} (${input.state.replace("_", " ")})`,
  };
}

/** RULE-B: the orbit's semantic role decides the band; the band never decides the role. */
export function orbitBandOf(kind: OrbitKind): OrbitBand {
  switch (kind) {
    case "containment":
    case "capability":
    case "lifecycle":
      return "inner";
    case "participation":
    case "governance":
      return "middle";
    case "evidence":
      return "outer";
  }
}

function roleOf(kind: OrbitKind, state: NodeState): "core-adjacent" | "primary" | "secondary" | "peripheral" {
  if (state === "current" || state === "possible") return "core-adjacent";
  if (orbitBandOf(kind) === "inner") return "primary";
  if (orbitBandOf(kind) === "middle") return "secondary";
  return "peripheral";
}

/** RULE-T: canonical state → approved tone (22 §18); no fifth category can be produced. */
export function toneOf(state: NodeState): VisualTone {
  switch (state) {
    case "current":
    case "possible":
    case "human":
      return "living";
    case "established":
    case "frozen":
    case "governance":
      return "stable";
    case "unavailable":
    case "denied":
    case "unknown":
      return "boundary";
    case "loading":
    case "future":
      return "neutral";
  }
}

/**
 * RULE-R: the canonical relation family and state decide the visual class and direction.
 * - capability `possible`: the request flows from the core to the affordance → directional, source-to-target;
 * - containment `established`: the container holds the entity → directional, source-to-target;
 * - participation (`human`): admission is mutual — the Session admits, the participant takes part (F03 PARTICIPATION
 *   is a typed relation on both sides) → reciprocal, bidirectional;
 * - governance: the holder exerts control over the scope → directional, target-to-source (node → core);
 * - lifecycle `current`: the active context current; passed / later phases: latent traces;
 * - unavailable / denied / loading / unknown: latent (a boundary is not a tension; no canonical tension exists).
 */
export function projectRelation(input: CanonicalRelationInput): ProjectedSemanticRelation {
  const sources = [`canonical-relation:${input.kind}`, `canonical-state:${input.state}`];
  const rule = (type: RelationType, direction?: RelationDirection): ProjectedSemanticRelation => ({
    id: input.id,
    sourceId: "core",
    targetId: input.id.replace(/^core->/, ""),
    type: { value: type, provenance: { kind: "projection-rule", ruleId: "RULE-R", sources } },
    weight: { value: BASE_WEIGHT[input.state], provenance: { kind: "projection-rule", ruleId: "RULE-W", sources: [`canonical-state:${input.state}`] } },
    direction: direction ? { value: direction, provenance: { kind: "projection-rule", ruleId: "RULE-R", sources } } : undefined,
    accessibilityLabel: `${input.kind} relation, ${input.state}`,
  });
  const boundary = input.state === "unavailable" || input.state === "denied" || input.state === "loading" || input.state === "unknown";
  if (boundary) return rule("latent");
  switch (input.kind) {
    case "capability":
      return input.state === "possible" ? rule("directional", "source-to-target") : rule("latent");
    case "containment":
      return input.state === "current" ? rule("context", "bidirectional") : rule("directional", "source-to-target");
    case "participation":
      return rule("reciprocal", "bidirectional");
    case "governance":
      return rule("directional", "target-to-source");
    case "lifecycle":
      return input.state === "current" ? rule("context", "bidirectional") : rule("latent");
    case "evidence":
      return rule("latent");
  }
}

const RULE_IDS = new Set(["RULE-W", "RULE-B", "RULE-R", "RULE-T"]);

function validProvenance(p: ProjectionProvenance | undefined): boolean {
  if (!p || typeof p !== "object") return false;
  switch (p.kind) {
    case "canonical-state":
    case "canonical-relation":
    case "canonical-authority-result":
    case "canonical-lifecycle-state":
      return typeof p.sourceId === "string" && p.sourceId.length > 0;
    case "projection-rule":
      return RULE_IDS.has(p.ruleId) && Array.isArray(p.sources);
    case "projection-local-interaction":
      return ["hover", "focus", "preview", "viewport", "reduced-motion"].includes(p.interaction);
    default:
      return false;
  }
}

/**
 * Development guard (doc 25 §5.4 Z9, §16.6): every semantic value must trace to a canonical producer or an
 * approved rule; a `tension` relation can never be asserted (no canonical tension relation exists here).
 */
export function assertProvenance(projected: ProjectedSemanticNode | ProjectedSemanticRelation): void {
  const fields: [string, ProjectedValue<unknown> | undefined][] =
    "semanticWeight" in projected
      ? [["semanticWeight", projected.semanticWeight], ["orbitBand", projected.orbitBand], ["visualTone", projected.visualTone], ["role", projected.role]]
      : [["type", projected.type], ["weight", projected.weight], ["direction", projected.direction]];
  for (const [name, field] of fields) {
    if (field === undefined) continue;
    if (!validProvenance(field.provenance)) throw new Error(`projection authority: ${name} of ${projected.id} has no valid provenance`);
  }
  if ("type" in projected && projected.type.value === "tension") {
    throw new Error(`projection authority: relation ${projected.id} claims tension, but no canonical tension relation exists`);
  }
}

/** Projection-local interaction state (doc 25 §16.2): a view model, never domain truth. */
export type ProjectedFieldState = {
  readonly hoveredNodeId: string | null;
  readonly focusedNodeId: string | null;
  /** The route decides the active core; a click never selects a node into truth. */
  readonly activeRelation: "action" | "governance" | "proof" | "context" | null;
  readonly hoveredContextRelationId: string | null;
  /** Unit vector from the core to the hovered/focused node (for directional resonance); null at rest. */
  readonly vector: { readonly x: number; readonly y: number } | null;
};

export const REST_FIELD_STATE: ProjectedFieldState = { hoveredNodeId: null, focusedNodeId: null, activeRelation: null, hoveredContextRelationId: null, vector: null };
