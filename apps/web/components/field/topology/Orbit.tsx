"use client";
/**
 * SF-02/SF-03/SF-04 Living Field Entity Layer + Relational Current System (22 §11.2–§11.4, §13–§15; doc 23 §6–§8;
 * doc 25 §7, §8).
 *
 * One orbit is ONE `<ul>` in semantic order (the order of `nodes`), so keyboard and screen-reader order never follow
 * the geometry (22 §34.1). Geometry comes from the content-aware layout of the enclosing `Topology`
 * (`lib/field/geometry.ts`): px offsets from the stage centre (`--x`, `--y`), visual mass (`--mass`), deterministic
 * organic offsets. Semantic visuals come from the Projection Authority Layer (`lib/field/projection.ts`): the node's
 * `orbitBand`, `semanticWeight` (→ mass), `visualTone`, and the relation's visual class + direction (→ current
 * motion). Every projected value carries provenance; the rule ids are written to `data-provenance` so a review can
 * read the chain on the DOM (doc 25 §5.4 Z9, §16.6). No visual is inferred from position, motion or looks.
 *
 * Relation currents are one `aria-hidden` SVG in stage pixels: a soft arc per relation (deterministic bend from the
 * node key) with a base path, an active current layer and endpoint resonance; the visual class (`reciprocal`,
 * `directional`, `latent`, `context`) and direction are DOM attributes the stylesheet animates — the canonical
 * relation decides the motion, never the reverse (doc 25 §8.2). The same relation is in the node's text marker and
 * `data-node-state`, so the SVG is never the only carrier (22 §35.3).
 *
 * Node anatomy (doc 25 §7.2): aura → membrane (`.node-body`) → internal surface → label containment → role indicator.
 * A node is a link (relation to enter), a button (effect to request) or plain text (relation only). Hover/focus are
 * projection-local encounters handled by the stage (doc 25 §13); a click never selects a node into truth here — it
 * navigates or requests, and the route/commit decides.
 */
import Link from "next/link";
import { useEffect, useRef, type ReactNode } from "react";
import { estimateCoreBox, layoutField, organicOffset, seeds, type Box, type NodeContent, type RingLayout } from "../../../lib/field/geometry";
import { assertProvenance, projectNode, projectRelation, type ProjectedSemanticNode, type ProjectedSemanticRelation } from "../../../lib/field/projection";
import { relationOfOrbit, type OrbitKind } from "../../../lib/field/reciprocity";
import type { Emphasis, NodeState, PathState } from "../../../lib/field/topology";
import { NOMINAL_STAGE, useFieldLayout, useReportBoxes, useStageMode } from "./FieldStage";

export type OrbitNode = {
  readonly key: string;
  readonly state: NodeState;
  /** Path state from the core to this node (22 §11.4); defaults from the node state. */
  readonly path?: PathState;
  readonly label: ReactNode;
  readonly meta?: ReactNode;
  readonly href?: string;
  readonly onActivate?: () => void;
  readonly disabled?: boolean;
  /** Visible action label for an effect node (e.g. "Open Session"); the button's accessible name. */
  readonly actionLabel?: string;
  readonly reason?: string | null;
  readonly size?: "md" | "sm" | "dot";
  /** Presentation weight from gravity (doc 23 §13.5); never hides the label. */
  readonly emphasis?: Emphasis;
  readonly ariaCurrent?: "step" | "true";
  readonly testId?: string;
  readonly labelVisibility?: "visible" | "assistive";
  readonly describedBy?: string;
  /** Overrides the default state word (e.g. "passed" / "later" for lifecycle phases). Always text. */
  readonly markerText?: string;
  /** Number of canonical relations this entity holds to the core context (relation density, doc 25 §7.3). */
  readonly relationCount?: number;
};

const MARKER: Readonly<Record<NodeState, string>> = {
  established: "established",
  current: "current",
  possible: "possible",
  unavailable: "not available",
  denied: "denied",
  loading: "pending",
  unknown: "unknown",
  frozen: "frozen",
  human: "human",
  governance: "authority",
  future: "later",
};

function defaultPath(state: NodeState): PathState {
  switch (state) {
    case "possible":
    case "unavailable":
    case "denied":
    case "loading":
    case "current":
    case "established":
      return state;
    case "governance":
      return "governance";
    case "frozen":
    case "human":
    case "unknown":
      return "established";
    case "future":
      return "dependency";
  }
}

function textOf(node: ReactNode): string {
  if (node == null || typeof node === "boolean") return "";
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(textOf).join("");
  if (typeof node === "object" && "props" in node) {
    const props = (node as { props?: { children?: ReactNode } }).props;
    return textOf(props?.children);
  }
  return "";
}

/** Long technical tokens (AUTHORITY_CLASS_NAMES) may wrap after an underscore instead of mid-word (doc 23 §6.4). */
function breakable(meta: ReactNode): ReactNode {
  return typeof meta === "string" ? meta.replace(/_/g, "_​") : meta;
}

/** The content the geometry estimates for a node, with its projected weight and band (doc 25 §7.3–§7.4). */
export function nodeContent(n: OrbitNode, kind: OrbitKind = "containment"): NodeContent {
  const projected = projectNode({ key: n.key, kind, state: n.state, label: textOf(n.label), relationCount: n.relationCount });
  return {
    key: n.key,
    label: n.onActivate && n.actionLabel ? n.actionLabel : textOf(n.label),
    meta: n.meta ? textOf(n.meta) : undefined,
    size: n.size ?? "md",
    weight: projected.semanticWeight.value,
    band: projected.orbitBand.value,
  };
}

function provenanceOf(node: ProjectedSemanticNode): string {
  const ids = [node.semanticWeight, node.orbitBand, node.visualTone].map((v) => (v.provenance.kind === "projection-rule" ? v.provenance.ruleId : v.provenance.kind));
  return ids.join(";");
}

function relationProvenance(rel: ProjectedSemanticRelation): string {
  return rel.type.provenance.kind === "projection-rule" ? `${rel.type.provenance.ruleId}:${rel.type.provenance.sources.join(",")}` : rel.type.provenance.kind;
}

/** A soft arc from the core to the node: the bend is deterministic per node key (doc 25 §8.3 "curved, never harsh"). */
export function arcPath(cx: number, cy: number, x: number, y: number, key: string, start: number): string {
  const sx = cx + (x - cx) * start;
  const sy = cy + (y - cy) * start;
  const mx = (sx + x) / 2;
  const my = (sy + y) / 2;
  const dx = x - sx;
  const dy = y - sy;
  const len = Math.hypot(dx, dy) || 1;
  const bend = (organicOffset(key).angleDeg / 11) * 0.12 * len; // ±12 % of the length at most
  const px = mx - (dy / len) * bend;
  const py = my + (dx / len) * bend;
  return `M ${sx.toFixed(1)} ${sy.toFixed(1)} Q ${px.toFixed(1)} ${py.toFixed(1)} ${x.toFixed(1)} ${y.toFixed(1)}`;
}

export function Orbit({
  kind,
  ring,
  heading,
  nodes,
  testId,
  listAriaLabel,
}: {
  readonly kind: OrbitKind;
  /** Ring index (1 = inner). */
  readonly ring: 1 | 2;
  readonly heading: string;
  readonly nodes: readonly OrbitNode[];
  readonly testId?: string;
  readonly listAriaLabel?: string;
}) {
  const layout = useFieldLayout();
  const report = useReportBoxes();
  const mode = useStageMode();
  const listRef = useRef<HTMLUListElement>(null);
  // doc 23 §7.1: after render, the RENDERED frames (position-independent: content-sized) refine the estimate once
  useEffect(() => {
    const list = listRef.current;
    if (!list || !report || mode !== "orbit") return;
    const boxes: Record<string, Box> = {};
    for (const li of list.querySelectorAll<HTMLElement>(":scope > li.node")) {
      const key = li.dataset.key;
      const body = li.querySelector<HTMLElement>(".node-body");
      if (!key || !body) continue;
      const r = body.getBoundingClientRect();
      if (r.width > 0 && r.height > 0) boxes[key] = { w: Math.ceil(r.width), h: Math.ceil(r.height) };
    }
    if (Object.keys(boxes).length > 0) report(boxes);
  });
  // Without an enclosing Topology (isolated primitive tests) the orbit lays itself out on a nominal stage.
  const standalone = layout ? null : layoutField({ core: estimateCoreBox({ title: "" }), rings: [nodes.map((n) => nodeContent(n, kind))], stage: NOMINAL_STAGE });
  const stage = layout?.stage ?? NOMINAL_STAGE;
  const ringLayout: RingLayout | undefined = layout ? layout.rings[ring - 1] : standalone?.rings[0];
  const cx = stage.w / 2;
  const cy = stage.h / 2;
  const coreHalf = Math.min(layout?.core.w ?? 196, layout?.core.h ?? 196) / 2;
  const relation = relationOfOrbit(kind);
  const projected = nodes.map((n) => {
    const node = projectNode({ key: n.key, kind, state: n.state, label: textOf(n.label), relationCount: n.relationCount });
    const rel = projectRelation({ id: `core->${n.key}`, kind, state: n.state });
    if (process.env.NODE_ENV !== "production") {
      assertProvenance(node);
      assertProvenance(rel);
    }
    return { node, rel };
  });
  return (
    <>
      <svg className="orbit-paths" data-orbit={kind} viewBox={`0 0 ${stage.w} ${stage.h}`} preserveAspectRatio="none" aria-hidden="true" focusable="false">
        {ringLayout ? <ellipse className="ring" data-orbit={kind} cx={cx} cy={cy} rx={ringLayout.rx} ry={ringLayout.ry} vectorEffect="non-scaling-stroke" /> : null}
        {nodes.map((n, i) => {
          const p = ringLayout?.nodes[i];
          if (!p) return null;
          const { rel } = projected[i];
          const x = cx + p.x;
          const y = cy + p.y;
          const len = Math.hypot(p.x, p.y) || 1;
          const start = Math.min(0.9, coreHalf / len);
          const d = arcPath(cx, cy, x, y, n.key, start);
          return (
            <g
              key={n.key}
              className="relation"
              data-key={n.key}
              data-path={n.path ?? defaultPath(n.state)}
              data-relation-type={rel.type.value}
              data-direction={rel.direction?.value ?? "none"}
              data-provenance={relationProvenance(rel)}
              style={{ ["--w" as string]: String(rel.weight.value) }}
            >
              <path className="path path-base" data-path={n.path ?? defaultPath(n.state)} d={d} vectorEffect="non-scaling-stroke" />
              <circle className="endpoint endpoint-node" cx={x} cy={y} r={3} />
              <circle className="endpoint endpoint-core" cx={cx + (x - cx) * start} cy={cy + (y - cy) * start} r={2.5} />
            </g>
          );
        })}
      </svg>
      {/* the current itself: one small pulse per non-latent relation travelling the same arc on a CSS motion path
          (a transform animation on its own compositor layer — the SVG never repaints for motion; doc 25 §19) */}
      <div className="currents" data-orbit={kind} aria-hidden="true">
        {nodes.map((n, i) => {
          const p = ringLayout?.nodes[i];
          const { rel } = projected[i];
          if (!p || rel.type.value === "latent") return null;
          const x = cx + p.x;
          const y = cy + p.y;
          const len = Math.hypot(p.x, p.y) || 1;
          const start = Math.min(0.9, coreHalf / len);
          return (
            <span
              key={n.key}
              className="current-pulse"
              data-key={n.key}
              data-path={n.path ?? defaultPath(n.state)}
              data-relation-type={rel.type.value}
              data-direction={rel.direction?.value ?? "none"}
              style={{ offsetPath: `path("${arcPath(cx, cy, x, y, n.key, start)}")` }}
            />
          );
        })}
      </div>
      <ul ref={listRef} className="orbit" data-orbit={kind} data-relation={relation} data-testid={testId} aria-label={listAriaLabel ?? heading}>
        {nodes.map((n, i) => {
          const marker = n.markerText ?? MARKER[n.state];
          const p = ringLayout?.nodes[i];
          const { node } = projected[i];
          // The control (link/button) contains ONLY the label, so its accessible name is exactly the node
          // identity; meta and the state marker are siblings inside the frame (22 §14.1, §34.3).
          const main = (
            <span className={`node-label${n.labelVisibility === "assistive" ? " assistive visually-hidden" : ""}`}>
              {n.onActivate && n.actionLabel ? n.actionLabel : n.label}
            </span>
          );
          return (
            <li
              key={n.key}
              className="node"
              data-key={n.key}
              data-node-state={n.state}
              data-node-size={n.size ?? "md"}
              data-emphasis={n.emphasis}
              data-band={node.orbitBand.value}
              data-tone={node.visualTone.value}
              data-role={node.role.value}
              data-provenance={provenanceOf(node)}
              data-testid={n.testId}
              aria-current={n.ariaCurrent}
              style={{
                ["--x" as string]: `${(p?.x ?? 0).toFixed(1)}px`,
                ["--y" as string]: `${(p?.y ?? 0).toFixed(1)}px`,
                ["--mass" as string]: String(p?.scale ?? 1),
                ["--weight" as string]: String(node.semanticWeight.value),
                ["--breath-phase" as string]: (seeds(n.key)[0] * 11).toFixed(2),
              }}
            >
              <div className="node-body">
                <span className="node-aura" aria-hidden="true" />
                {n.href ? (
                  <Link href={n.href} className="node-main" aria-describedby={n.describedBy}>
                    {main}
                  </Link>
                ) : n.onActivate ? (
                  <button type="button" className="node-main" onClick={n.onActivate} disabled={n.disabled} aria-describedby={n.describedBy}>
                    {main}
                  </button>
                ) : (
                  <span className="node-main" aria-describedby={n.describedBy}>
                    {main}
                  </span>
                )}
                {n.meta ? <span className="node-meta">{breakable(n.meta)}</span> : null}
                <span className="node-marker">
                  <span className="node-role" aria-hidden="true" data-role={node.role.value} />
                  <span className="visually-hidden">Relation state: </span>
                  {marker}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </>
  );
}
