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
import { FOCUS_LENS_ID, useFocusLens, type LensFact } from "./FocusLens";
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
  /** The canonical facts the page already holds for this entry, shown in the focus lens (never inferred). */
  readonly details?: readonly LensFact[];
  /** What selecting the entry does, in words, for the focus lens. */
  readonly lensHint?: string;
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

/**
 * Family sphere (human direction, variant A): one relation family (Challenges, People, Authority, …) is ONE sphere on
 * the ring carrying its canonical count; its entries orbit it as satellites on a small local orbit, facing away from
 * the core. Every satellite is still the entry's own link or button (the semantic list is unchanged); its label is
 * revealed on hover / focus of the satellite or of its sphere. The count is the server's number in words.
 */
export type HubGlyph = "challenges" | "people" | "authority" | "sessions";
export type OrbitHub = {
  /** This family's position on the ring (index into the ring's layout). */
  readonly slot: number;
  readonly key: string;
  readonly label: string;
  readonly count: string;
  readonly glyph: HubGlyph;
};

export const HUB_DIAMETER = 112;
const SATELLITE = 26;
const SATELLITE_GAP = 12;

/** Radius of a family's satellite orbit: clear of the sphere, and long enough for every satellite. */
export function satelliteRadius(n: number): number {
  return Math.round(Math.max(HUB_DIAMETER / 2 + 12 + SATELLITE / 2, (Math.max(n, 1) * (SATELLITE + SATELLITE_GAP)) / (2 * Math.PI)));
}

/** The layout content of a family sphere: a fixed square frame that holds the sphere and its satellite orbit. */
export function hubContent(hub: { readonly key: string; readonly label: string; readonly count: string }, satellites: number): NodeContent {
  const side = 2 * (satelliteRadius(satellites) + SATELLITE / 2 + 4);
  return { key: hub.key, label: hub.label, meta: hub.count, size: "md", weight: 0.8, band: "inner", box: { w: side, h: side } };
}

/** Satellite angles: an arc centred on the direction away from the core (a full circle for many entries). */
function satelliteAngles(n: number, outwardDeg: number): number[] {
  if (n === 0) return [];
  const step = n === 1 ? 0 : Math.min(44, 330 / n);
  return Array.from({ length: n }, (_, i) => outwardDeg + (i - (n - 1) / 2) * step);
}

function HubGlyphIcon({ glyph }: { readonly glyph: HubGlyph }) {
  const common = { viewBox: "0 0 24 24", className: "hub-glyph", "aria-hidden": true, focusable: false } as const;
  switch (glyph) {
    case "people":
      return (
        <svg {...common}>
          <circle cx="9" cy="8" r="3.2" />
          <path d="M3.5 19c.6-3.3 2.8-5 5.5-5s4.9 1.7 5.5 5" />
          <circle cx="16.5" cy="9" r="2.6" />
          <path d="M15.2 14.2c2.6-.3 4.6 1.2 5.3 4.3" />
        </svg>
      );
    case "authority":
      return (
        <svg {...common}>
          <path d="M12 3l7 3v5.5c0 4.3-3 7.7-7 9.5-4-1.8-7-5.2-7-9.5V6l7-3z" />
          <path d="M9 12l2.2 2.2L15.5 10" />
        </svg>
      );
    case "sessions":
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="8" />
          <circle cx="12" cy="12" r="3.5" />
          <path d="M12 4v4.5M12 15.5V20" />
        </svg>
      );
    case "challenges":
      return (
        <svg {...common}>
          <path d="M3 19l6.5-11 3.5 6 2.5-4L21 19H3z" />
          <path d="M9.5 8l1.3 2.3" />
        </svg>
      );
  }
}

/** Decorative moons travelling a ring (aria-hidden; no meaning): deterministic size, speed and phase per ring. */
function ringPath(cx: number, cy: number, rx: number, ry: number): string {
  return `M ${(cx - rx).toFixed(1)} ${cy.toFixed(1)} a ${rx.toFixed(1)} ${ry.toFixed(1)} 0 1 0 ${(2 * rx).toFixed(1)} 0 a ${rx.toFixed(1)} ${ry.toFixed(1)} 0 1 0 ${(-2 * rx).toFixed(1)} 0`;
}
const MOONS: readonly { readonly d: number; readonly t: number; readonly phase: number }[] = [
  { d: 11, t: 140, phase: 0.18 },
  { d: 7, t: 95, phase: 0.63 },
];

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
  hub,
}: {
  readonly kind: OrbitKind;
  /** Ring index (1 = inner). */
  readonly ring: 1 | 2;
  readonly heading: string;
  readonly nodes: readonly OrbitNode[];
  readonly testId?: string;
  readonly listAriaLabel?: string;
  /** Render this orbit as a family sphere with satellites (orbit topology only). */
  readonly hub?: OrbitHub;
}) {
  const layout = useFieldLayout();
  const report = useReportBoxes();
  const lens = useFocusLens();
  const mode = useStageMode();
  const listRef = useRef<HTMLUListElement>(null);
  // doc 23 §7.1: after render, the RENDERED frames (position-independent: content-sized) refine the estimate once
  useEffect(() => {
    const list = listRef.current;
    if (!list || !report || mode !== "orbit" || hub) return;
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
  // family sphere: the ring holds the sphere; the entries sit on its satellite orbit, facing away from the core
  const hubPlace = hub && mode === "orbit" ? ringLayout?.nodes[hub.slot] : undefined;
  const satR = hub ? satelliteRadius(nodes.length) : 0;
  const satellites = hubPlace
    ? satelliteAngles(nodes.length, (Math.atan2(hubPlace.y, hubPlace.x) * 180) / Math.PI).map((a) => {
        const r = (a * Math.PI) / 180;
        return { x: hubPlace.x + Math.cos(r) * satR, y: hubPlace.y + Math.sin(r) * satR };
      })
    : null;
  const drawRing = ringLayout && (!hub || hub.slot === 0);
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
        {drawRing ? <ellipse className="ring" data-orbit={kind} cx={cx} cy={cy} rx={ringLayout.rx} ry={ringLayout.ry} vectorEffect="non-scaling-stroke" /> : null}
        {hubPlace && hub && satellites ? (
          <g className="relation family-relation" data-key={hub.key} data-path="established" data-relation-type={projected[0]?.rel.type.value ?? "directional"} data-direction={projected[0]?.rel.direction?.value ?? "none"}>
            <path className="path path-base" data-path="established" d={arcPath(cx, cy, cx + hubPlace.x, cy + hubPlace.y, hub.key, Math.min(0.9, coreHalf / (Math.hypot(hubPlace.x, hubPlace.y) || 1)))} vectorEffect="non-scaling-stroke" />
            <circle className="satellite-orbit" cx={cx + hubPlace.x} cy={cy + hubPlace.y} r={satR} vectorEffect="non-scaling-stroke" />
          </g>
        ) : null}
        {hubPlace && hub && satellites ? (
          // every entry keeps its own canonical relation current (doc 25 §8): a short curved spoke from its family
          // sphere, turning with the satellites (same glide-and-rest timeline, same origin: the sphere's centre)
          <g className="family-spokes" data-family-key={hub.key} style={{ transformOrigin: `${(cx + hubPlace.x).toFixed(1)}px ${(cy + hubPlace.y).toFixed(1)}px`, ["--orbit-phase" as string]: `${(-seeds(hub.key)[1] * 480).toFixed(1)}s` }}>
            {nodes.map((n, i) => {
              const sp = satellites[i];
              const { rel } = projected[i];
              const d = arcPath(cx + hubPlace.x, cy + hubPlace.y, cx + sp.x, cy + sp.y, n.key, Math.min(0.9, HUB_DIAMETER / 2 / satR));
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
                </g>
              );
            })}
          </g>
        ) : null}
        {!hubPlace && nodes.map((n, i) => {
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
        {drawRing && mode === "orbit"
          ? MOONS.slice(0, ring === 1 ? 2 : 1).map((m, i) => (
              <span
                key={`moon-${i}`}
                className="moon"
                style={{ offsetPath: `path("${ringPath(cx, cy, ringLayout.rx, ringLayout.ry)}")`, ["--moon-d" as string]: `${m.d}px`, animationDuration: `${m.t}s`, animationDelay: `${-m.t * m.phase}s` }}
              />
            ))
          : null}
        {hubPlace && hub && satellites ? (
          <div className="family-currents" style={{ transformOrigin: `${(cx + hubPlace.x).toFixed(1)}px ${(cy + hubPlace.y).toFixed(1)}px`, ["--orbit-phase" as string]: `${(-seeds(hub.key)[1] * 480).toFixed(1)}s` }}>
            {nodes.map((n, i) => {
              const sp = satellites[i];
              const { rel } = projected[i];
              if (rel.type.value === "latent") return null;
              return (
                <span
                  key={n.key}
                  className="current-pulse"
                  data-key={n.key}
                  data-path={n.path ?? defaultPath(n.state)}
                  data-relation-type={rel.type.value}
                  data-direction={rel.direction?.value ?? "none"}
                  style={{ offsetPath: `path("${arcPath(cx + hubPlace.x, cy + hubPlace.y, cx + sp.x, cy + sp.y, n.key, Math.min(0.9, HUB_DIAMETER / 2 / satR))}")` }}
                />
              );
            })}
          </div>
        ) : null}
        {hubPlace && hub ? (
          <span className="current-pulse" data-key={hub.key} data-path="established" data-relation-type="directional" data-direction="source-to-target" style={{ offsetPath: `path("${arcPath(cx, cy, cx + hubPlace.x, cy + hubPlace.y, hub.key, Math.min(0.9, coreHalf / (Math.hypot(hubPlace.x, hubPlace.y) || 1)))}")` }} />
        ) : null}
        {!hubPlace && nodes.map((n, i) => {
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
      {hub ? (
        <div
          className="family-hub"
          data-family={kind}
          data-glyph={hub.glyph}
          data-testid={testId ? `${testId}-hub` : undefined}
          style={{ ["--x" as string]: `${(hubPlace?.x ?? 0).toFixed(1)}px`, ["--y" as string]: `${(hubPlace?.y ?? 0).toFixed(1)}px`, ["--breath-phase" as string]: (seeds(hub.key)[0] * 11).toFixed(2), ["--hub-d" as string]: `${HUB_DIAMETER}px` }}
        >
          <span className="hub-orb" aria-hidden="true" />
          <HubGlyphIcon glyph={hub.glyph} />
          <span className="hub-label">{hub.label}</span>
          <span className="hub-count">{hub.count}</span>
        </div>
      ) : null}
      <ul ref={listRef} className="orbit" data-orbit={kind} data-relation={relation} data-hub={hub ? "true" : undefined} data-testid={testId} aria-label={listAriaLabel ?? heading}>
        {nodes.map((n, i) => {
          const marker = n.markerText ?? MARKER[n.state];
          const p = satellites ? satellites[i] : ringLayout?.nodes[i];
          const { node } = projected[i];
          // The control (link/button) contains ONLY the label, so its accessible name is exactly the node
          // identity; meta and the state marker are siblings inside the frame (22 §14.1, §34.3).
          const sat = satellites ? satellites[i] : null;
          // the focus lens opens for every entry that carries canonical facts (satellites and plain nodes alike)
          const lensContent = (sat && hub) || n.details
            ? {
                key: n.key,
                family: hub?.label ?? heading,
                title: textOf(n.onActivate && n.actionLabel ? n.actionLabel : n.label),
                state: marker,
                tone: node.visualTone.value,
                facts: n.details ?? (n.meta ? [{ label: "Relation", value: textOf(n.meta) }] : []),
                hint: n.lensHint ?? (n.href ? "Select to open" : n.onActivate && !n.disabled ? `Select to ${(n.actionLabel ?? "act").toLowerCase()}` : undefined),
              }
            : null;
          const describedBy = lensContent ? [n.describedBy, FOCUS_LENS_ID].filter(Boolean).join(" ") : n.describedBy;
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
              data-satellite={sat ? "true" : undefined}
              aria-current={n.ariaCurrent}
              onMouseEnter={lensContent && lens ? () => lens.open(lensContent) : undefined}
              onMouseLeave={lensContent && lens ? () => lens.close(n.key) : undefined}
              onFocus={lensContent && lens ? () => lens.open(lensContent) : undefined}
              onBlur={lensContent && lens ? () => lens.close(n.key) : undefined}
              onKeyDown={lensContent && lens ? (e) => (e.key === "Escape" ? lens.close(n.key) : undefined) : undefined}
              style={{
                ["--x" as string]: `${(p?.x ?? 0).toFixed(1)}px`,
                ["--y" as string]: `${(p?.y ?? 0).toFixed(1)}px`,
                ["--mass" as string]: String(p && "scale" in p ? p.scale : 1),
                ["--weight" as string]: String(node.semanticWeight.value),
                ["--breath-phase" as string]: (seeds(n.key)[0] * 11).toFixed(2),
                // a satellite glides and rests around its sphere: the rotation origin is the sphere's centre
                ...(sat && hubPlace && hub
                  ? { ["--ox" as string]: `${(hubPlace.x - sat.x).toFixed(1)}px`, ["--oy" as string]: `${(hubPlace.y - sat.y).toFixed(1)}px`, ["--orbit-phase" as string]: `${(-seeds(hub.key)[1] * 480).toFixed(1)}s` }
                  : {}),
              }}
            >
              <div className="node-body">
                <span className="node-aura" aria-hidden="true" />
                {n.href ? (
                  <Link href={n.href} className="node-main" aria-describedby={describedBy}>
                    {main}
                  </Link>
                ) : n.onActivate ? (
                  <button type="button" className="node-main" onClick={n.onActivate} disabled={n.disabled} aria-describedby={describedBy}>
                    {main}
                  </button>
                ) : (
                  <span className="node-main" aria-describedby={describedBy}>
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
