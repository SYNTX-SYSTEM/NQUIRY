"use client";
/**
 * SF-02/SF-03/SF-04 Field stage (22 §16.4, §32; doc 23 §7, §8, §11, §12; doc 25 §13, §16.2).
 *
 * The stage holds, in DOM = semantic = keyboard order (22 §34.1, §32.6):
 *   Core → current state → human position → effects → direct relations → governance → proof → context.
 * `Topology` and the context organ (`Planes`) are only PLACEMENT slots. On wide viewports the core and the rings are
 * positioned inside the topology box (content-aware geometry) and the contextual organ is attached beside it; on
 * tablets the organ attaches below; on phones the same DOM is a breathing constellation with a membrane sheet.
 * Nothing about system possibility changes with the mode (22 §2.4; doc 25 §15.2).
 *
 * Projected field state (doc 25 §16.2 `FieldState`): a VIEW MODEL, never domain truth. One delegated focus/hover
 * listener records the projection-local encounter — the relation family under attention, the hovered/focused node
 * key, the unit vector from the core to that node, or the hovered context relation token — and writes it to the DOM
 * (`data-active-relation`, `data-hover-key`, `data-encounter`, `--vec-x/--vec-y/--vec-on`) and marks the resonating
 * counterparts (`data-resonating`). The stylesheet renders the encounter cascade (doc 25 §13.1). It sets no state,
 * implies no authority, sends no request, and is identical for keyboard focus and pointer (doc 25 §13.2, §13.4).
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { DECISION_STAGE, estimateCoreBox, layoutField, requiredHalfHeight, stageMode, viewportClass, type Box, type CoreContent, type FieldLayout, type NodeContent, type StageBox, type ViewportClass } from "../../../lib/field/geometry";
import { REST_FIELD_STATE, type ProjectedFieldState } from "../../../lib/field/projection";
import type { SemanticChamber } from "../chambers";
import type { RelationFamily } from "../../../lib/field/reciprocity";

const RELATION_ATTR = "data-relation";

function relationUnder(target: EventTarget | null): RelationFamily | null {
  if (!(target instanceof Element)) return null;
  const owner = target.closest(`[${RELATION_ATTR}]`);
  return (owner?.getAttribute(RELATION_ATTR) as RelationFamily | null) ?? null;
}

type Encounter = { readonly nodeKey: string | null; readonly tokenKey: string | null; readonly vector: { readonly x: number; readonly y: number } | null };
const NO_ENCOUNTER: Encounter = { nodeKey: null, tokenKey: null, vector: null };

/** The field entity under attention (a node) or the context relation token under attention. */
function encounterUnder(target: EventTarget | null): Encounter {
  if (!(target instanceof Element)) return NO_ENCOUNTER;
  const node = target.closest<HTMLElement>("li.node[data-key]");
  if (node) {
    const x = parseFloat(node.style.getPropertyValue("--x")) || 0;
    const y = parseFloat(node.style.getPropertyValue("--y")) || 0;
    const len = Math.hypot(x, y);
    return { nodeKey: node.dataset.key ?? null, tokenKey: null, vector: len > 0 ? { x: x / len, y: y / len } : null };
  }
  const token = target.closest<HTMLElement>("[data-relation-key]");
  if (token) return { nodeKey: null, tokenKey: token.dataset.relationKey ?? null, vector: null };
  return NO_ENCOUNTER;
}

function escapeKey(key: string): string {
  return typeof CSS !== "undefined" && typeof CSS.escape === "function" ? CSS.escape(key) : key.replace(/["\\]/g, "\\$&");
}

export function FieldStage({
  mode,
  layout,
  surface,
  children,
}: {
  /** Explicit mode (loading / boundary states); otherwise decided from `layout` and the viewport class. */
  readonly mode?: "orbit" | "stack";
  readonly layout?: TopologyInput;
  readonly surface: string;
  readonly children: ReactNode;
}) {
  const [field, setField] = useState<ProjectedFieldState>(REST_FIELD_STATE);
  const ref = useRef<HTMLDivElement>(null);
  const [vp, setVp] = useState<ViewportClass>("desktop");
  // rendered frames (doc 23 §7.1): content-sized, so independent of position; reported only in orbit mode, so a
  // decision that switches to the stack keeps the frames it decided on — no feedback loop
  const [frames, setFrames] = useState<MeasuredFrames>({ nodes: {} });
  const framesRef = useRef<MeasuredFrames>({ nodes: {} });
  const report = useCallback((next: Partial<MeasuredFrames>) => {
    const prev = framesRef.current;
    const nodes = next.nodes ? { ...prev.nodes, ...next.nodes } : prev.nodes;
    const core = next.core ?? prev.core;
    const same = Object.keys(nodes).every((k) => prev.nodes[k] && prev.nodes[k].w === nodes[k].w && prev.nodes[k].h === nodes[k].h) && Object.keys(nodes).length === Object.keys(prev.nodes).length && (core?.w === prev.core?.w && core?.h === prev.core?.h);
    if (same) return;
    framesRef.current = { nodes, core };
    setFrames(framesRef.current);
  }, []);
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver((entries) => {
      const w = entries[0]?.contentRect.width ?? 0;
      if (w > 0) setVp((prev) => (prev === viewportClass(w) ? prev : viewportClass(w)));
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  // resonating counterparts (doc 25 §13.1): the node, its relation current and the organ's relation tokens that
  // share the encountered key; the chamber holding a resonating token previews
  const resonanceKey = field.hoveredNodeId ?? field.focusedNodeId ?? field.hoveredContextRelationId;
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    for (const marked of el.querySelectorAll<HTMLElement>("[data-resonating]")) marked.removeAttribute("data-resonating");
    for (const chamber of el.querySelectorAll<HTMLElement>("[data-chamber-resonating]")) chamber.removeAttribute("data-chamber-resonating");
    if (!resonanceKey) return;
    const k = escapeKey(resonanceKey);
    for (const match of el.querySelectorAll<HTMLElement>(`li.node[data-key="${k}"], g.relation[data-key="${k}"], .current-pulse[data-key="${k}"], [data-relation-key="${k}"]`)) {
      match.setAttribute("data-resonating", "true");
      const chamber = match.closest<HTMLElement>("[data-chamber]");
      if (chamber) chamber.setAttribute("data-chamber-resonating", "true");
    }
  }, [resonanceKey]);
  const encounter = (target: EventTarget | null, how: "hover" | "focus") => {
    const family = relationUnder(target);
    const e = encounterUnder(target);
    setField((prev) => ({
      ...prev,
      activeRelation: family ?? (how === "hover" ? prev.activeRelation : null),
      hoveredNodeId: how === "hover" ? e.nodeKey : prev.hoveredNodeId,
      focusedNodeId: how === "focus" ? e.nodeKey : prev.focusedNodeId,
      hoveredContextRelationId: e.tokenKey,
      vector: e.vector ?? (e.tokenKey ? prev.vector : null),
    }));
  };
  const decided = mode ?? (layout ? stageMode(layout.core, layout.rings, vp, frames) : "stack");
  const attentionKey = field.hoveredNodeId ?? field.focusedNodeId ?? null;
  // a stable context value: an encounter re-renders the stage's own attributes only — never the topology's
  // geometry or the orbits (the measured frames change only when a frame changes)
  const measureValue = useMemo(() => ({ frames, report }), [frames, report]);
  return (
    <ModeContext.Provider value={decided}>
    <MeasureContext.Provider value={measureValue}>
    <div
      ref={ref}
      className="field-stage"
      data-topology={decided}
      data-viewport={vp}
      data-surface={surface}
      data-testid="field-stage"
      data-active-relation={field.activeRelation ?? undefined}
      data-hover-key={attentionKey ?? undefined}
      data-encounter={field.focusedNodeId ? "focus" : field.hoveredNodeId ? "hover" : field.hoveredContextRelationId ? "context" : undefined}
      style={{ ["--vec-x" as string]: String(field.vector?.x ?? 0), ["--vec-y" as string]: String(field.vector?.y ?? 0), ["--vec-on" as string]: field.vector ? "1" : "0" }}
      onFocus={(e) => encounter(e.target, "focus")}
      onBlur={() => setField((prev) => ({ ...prev, activeRelation: null, focusedNodeId: null, hoveredContextRelationId: null, vector: prev.hoveredNodeId ? prev.vector : null }))}
      onMouseOver={(e) => encounter(e.target, "hover")}
      onMouseOut={(e) => {
        const from = relationUnder(e.target);
        const to = relationUnder(e.relatedTarget);
        const next = encounterUnder(e.relatedTarget);
        setField((prev) => ({
          ...prev,
          activeRelation: from && from !== to ? to : prev.activeRelation,
          hoveredNodeId: next.nodeKey,
          hoveredContextRelationId: next.tokenKey,
          vector: next.vector ?? (prev.focusedNodeId ? prev.vector : null),
        }));
      }}
    >
      {children}
    </div>
    </MeasureContext.Provider>
    </ModeContext.Provider>
  );
}

const ModeContext = createContext<"orbit" | "stack">("orbit");

export type MeasuredFrames = { readonly nodes: Readonly<Record<string, Box>>; readonly core?: Box };

export type TopologyInput = {
  readonly core: CoreContent;
  readonly rings: readonly (readonly NodeContent[])[];
};

const LayoutContext = createContext<FieldLayout | null>(null);

/** Rendered frames (nodes, core) and the report callback; `null` outside a FieldStage. */
const MeasureContext = createContext<{ readonly frames: MeasuredFrames; readonly report: (next: Partial<MeasuredFrames>) => void } | null>(null);

export function useReportBoxes(): ((boxes: Readonly<Record<string, Box>>) => void) | null {
  const ctx = useContext(MeasureContext);
  const report = ctx?.report;
  return useMemo(() => (report ? (nodes: Readonly<Record<string, Box>>) => report({ nodes }) : null), [report]);
}

export function useStageMode(): "orbit" | "stack" {
  return useContext(ModeContext);
}

/** The tallest decision stage (doc 23 §7.6): the box never grows beyond the height the mode was decided on. */
const MAX_STAGE_HEIGHT = Math.max(...Object.values(DECISION_STAGE).map((s) => s.h));

/** Nominal stage box used before the client has measured the real one (and on the server). */
export const NOMINAL_STAGE: StageBox = { w: 760, h: 800 };

export function useFieldLayout(): FieldLayout | null {
  return useContext(LayoutContext);
}

/**
 * The positioned box that holds the core and its rings. Geometry is derived from the CONTENT (labels, meta, sizes,
 * projected weights and bands)
 * and the box: on the server and at hydration from the nominal box, then from the measured box (ResizeObserver),
 * so the same content and the same viewport class always yield the same layout (doc 23 §7.2, §7.4).
 */
export function Topology({ layout, nominal = NOMINAL_STAGE, children }: { readonly layout?: TopologyInput; readonly nominal?: StageBox; readonly children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const mode = useContext(ModeContext);
  const measure = useContext(MeasureContext);
  const frames = measure?.frames;
  const [measured, setMeasured] = useState<StageBox | null>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver((entries) => {
      const box = entries[0]?.contentRect;
      if (!box || box.width < 80 || box.height < 80) return;
      const next = { w: Math.round(box.width), h: Math.round(box.height) };
      setMeasured((prev) => (prev && prev.w === next.w && prev.h === next.h ? prev : next));
      // the rendered core frame (content-sized) refines its estimate, in orbit mode only
      const core = el.querySelector<HTMLElement>(":scope > .core");
      if (core && getComputedStyle(core).position === "absolute") {
        const r = core.getBoundingClientRect();
        if (r.width > 0 && r.height > 0) measure?.report({ core: { w: Math.ceil(r.width), h: Math.ceil(r.height) } });
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [measure]);
  const base = measured ?? nominal;
  // The box's WIDTH is the viewport's (grid column); its HEIGHT follows the content when the content needs more
  // than the stylesheet's default (frames follow content, doc 23 §6.3). Pure derivation, memoized on its inputs
  // (content, measured box, rendered frames): an encounter never recomputes the geometry. The circular need first,
  // then the actual (stretched, organic) layout at exactly that height: the need grows until the layout fits, in
  // bounded steps, never beyond the tallest decision stage (where the mode was decided). The need depends on the
  // width, the content and the frames only — never on the box's current height — so a grown box can never lower
  // its own need (no oscillation, doc 23 §7.4).
  const { neededH, computed, measuredCount } = useMemo(() => {
    const measuredBoxes = frames?.nodes ?? {};
    const measuredCore = frames?.core;
    const coreBox = layout ? (measured && measuredCore ? measuredCore : estimateCoreBox(layout.core)) : null;
    let need = 0;
    if (layout && coreBox && measured && measured.w >= 560) {
      need = requiredHalfHeight(layoutField({ core: coreBox, rings: layout.rings, stage: { w: measured.w, h: Math.max(measured.w, 200) }, noStretch: true, measured: measuredBoxes })) * 2;
      for (let pass = 0; pass < 6; pass += 1) {
        const trial = layoutField({ core: coreBox, rings: layout.rings, stage: { w: measured.w, h: need }, measured: measuredBoxes });
        if (trial.fits) break;
        const next = Math.max(requiredHalfHeight(trial) * 2, need + 48);
        if (next > MAX_STAGE_HEIGHT) break;
        need = next;
      }
    }
    const stage = { w: base.w, h: Math.max(base.h, need) };
    const result: FieldLayout | null = layout && coreBox ? layoutField({ core: coreBox, rings: layout.rings, stage, measured: measured ? measuredBoxes : undefined }) : null;
    return { neededH: need, computed: result, measuredCount: Object.keys(measuredBoxes).length };
  }, [layout, frames, measured, base.w, base.h]);
  return (
    <LayoutContext.Provider value={computed}>
      <div
        ref={ref}
        className="topology"
        data-fit={computed ? (mode === "stack" || (measured && measured.w < 560) ? "stack" : computed.fits ? "fits" : "overflow") : undefined}
        data-measured={measured ? "true" : undefined}
        data-compact={computed?.compact && mode === "orbit" ? "true" : undefined}
        data-needed-h={neededH > 0 ? String(neededH) : undefined}
        data-boxes={String(measuredCount)}
        style={neededH > 0 && measured ? { ["--stage-h" as string]: `${neededH}px` } : undefined}
      >
        {/* atmospheric medium of the field box (doc 25 §12): a pressure zone around the core and a resonance wash
            that leans toward the encounter vector; decorative, opacity/transform only, no meaning of its own */}
        <div className="stage-atmosphere" aria-hidden="true" data-testid="stage-atmosphere">
          <div className="pressure-zone" />
          <div className="resonance-wash" />
        </div>
        {children}
      </div>
    </LayoutContext.Provider>
  );
}

/* ------------------------------------------------------------------ Contextual Semantic Organ (doc 25 §10) */

export type OrganHeader = {
  readonly eyebrow: string;
  readonly title: ReactNode;
  /** The canonical state in words (never invented by the organ). */
  readonly state?: ReactNode;
};

/**
 * The contextual semantic organ: ONE body grown from the active field state (the route's core), with chambers
 * (`Plane`) in semantic order. It displays canonical context and hosts request surfaces; it is never an authority
 * source (doc 25 §10.3). The `aria-live="polite"` region announces reconstruction quietly (doc 25 §18.4); the
 * membrane header names the state it grew from; the bridge is decorative.
 */
export function Planes({ header, children }: { readonly header?: OrganHeader; readonly children: ReactNode }) {
  return (
    <aside className="organ" aria-label="Active semantic context" aria-live="polite" data-testid="context-organ">
      <div className="organ-bridge" aria-hidden="true" />
      {header ? (
        <header className="organ-header" data-testid="organ-header">
          <p className="eyebrow">{header.eyebrow}</p>
          <p className="organ-title">{header.title}</p>
          {header.state ? <p className="organ-state">{header.state}</p> : null}
        </header>
      ) : null}
      <div className="instruments organ-body">{children}</div>
    </aside>
  );
}

export type PlaneKind = "action" | "governance" | "proof" | "human" | "frozen" | "boundary" | "context";
export type ChamberKind = "primary" | "relational" | "logic" | "action";

/** Doc 25 §10.2: the instruments are chambers of one organ (primary / relational / governance-logic / action). */
const PLANE_CHAMBER: Readonly<Record<PlaneKind, ChamberKind>> = {
  action: "primary",
  human: "primary",
  frozen: "primary",
  boundary: "primary",
  governance: "relational",
  proof: "logic",
  context: "logic",
};

const PLANE_RELATION: Readonly<Record<PlaneKind, RelationFamily>> = {
  action: "action",
  human: "action",
  frozen: "action",
  boundary: "action",
  governance: "governance",
  proof: "proof",
  context: "context",
};

/** Doc 26 §17: the default semantic class of a plane kind; pages pass `semantic` where the class is more specific. */
const PLANE_SEMANTIC: Readonly<Record<PlaneKind, SemanticChamber>> = {
  action: "action",
  human: "question",
  frozen: "frozen",
  boundary: "boundary",
  governance: "authority",
  proof: "proof",
  context: "context",
};

export function Plane({
  kind,
  semantic,
  labelledBy,
  label,
  testId,
  children,
}: {
  readonly kind: PlaneKind;
  /** The semantic chamber class (doc 26 §17); defaults from the relation kind. */
  readonly semantic?: SemanticChamber;
  readonly labelledBy?: string;
  readonly label?: string;
  readonly testId?: string;
  readonly children: ReactNode;
}) {
  return (
    <section
      className="plane chamber"
      data-plane={kind}
      data-chamber={PLANE_CHAMBER[kind]}
      data-semantic={semantic ?? PLANE_SEMANTIC[kind]}
      data-relation={PLANE_RELATION[kind]}
      aria-labelledby={labelledBy}
      aria-label={label}
      data-testid={testId}
    >
      <span className="chamber-contour" aria-hidden="true" />
      {children}
    </section>
  );
}
