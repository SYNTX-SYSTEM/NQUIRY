/**
 * SF-03 content-aware Field geometry (doc 23 §7; doc 22 §11.2, §13, §16.2).
 *
 * DERIVED PRESENTATION STATE, pure and deterministic: from the content each node must carry (label, meta, size
 * class) and the stage box, derive node frames, a weighted angular allocation (wide nodes get more arc), the ring
 * radius the content needs (never the other way round), the separation between rings from their frames, an
 * elliptical stretch that uses the longer stage dimension for breathing room, and a collision check against every
 * other frame and the core. Nothing here reads the DOM, the clock or a random source, so the server and the client
 * derive the same layout (22 §35.7) and the same content always yields the same geometry (doc 23 §7.4).
 *
 * The estimator uses fixed type metrics (the tokens in `globals.css`). It is deliberately a little generous: a
 * frame may be larger than the rendered text, never smaller. Text is never shrunk to fit (doc 23 §6.2); when the
 * stage cannot hold the required geometry the layout reports `fits: false` and the surface chooses a larger stage
 * or the stack representation. The content keeps its size either way.
 *
 * Geometry is expressed in px for the given stage; the renderer converts the ellipse radii to fractions of the real
 * stage box (container-query units), so the same allocation breathes with the viewport (doc 23 §7.2, §7.6).
 */

export type NodeSize = "md" | "sm" | "dot";

export type NodeContent = {
  readonly key?: string;
  readonly label: string;
  readonly meta?: string;
  readonly size?: NodeSize;
  /** SF-04 (doc 25 §7.3): projected semantic weight 0.3–1 → visual mass; from `projection.ts`, never from looks. */
  readonly weight?: number;
  /** SF-04 (doc 25 §7.4): projected orbit band → radius class; from `projection.ts`, never from position. */
  readonly band?: "inner" | "middle" | "outer";
  /** A fixed frame (a family sphere with its satellite cluster): used instead of the text estimate. */
  readonly box?: Box;
};

export type Box = { readonly w: number; readonly h: number };

export type PlacedNode = Box & {
  readonly key: string;
  /** Degrees; -90 = top, increasing clockwise (screen coordinates). */
  readonly angleDeg: number;
  /** Unit vector of the angle (written to CSS as --ox / --oy). */
  readonly ox: number;
  readonly oy: number;
  /** Centre in px relative to the stage centre. */
  readonly x: number;
  readonly y: number;
  /** Visual mass factor from the semantic weight (0.9–1.1); applied to the frame and written as `--mass`. */
  readonly scale: number;
  /** Deterministic organic radius factor (doc 25 §7.7): 1 ± 0.03–0.08, from the node key, never random. */
  readonly radiusFactor: number;
};

export type RingLayout = {
  /** Horizontal / vertical semi-axes in px (a circle when the stage is square). */
  readonly rx: number;
  readonly ry: number;
  /** The circular radius the content required before the elliptical stretch. */
  readonly radius: number;
  readonly maxW: number;
  readonly maxH: number;
  readonly nodes: readonly PlacedNode[];
};

export type StageBox = { readonly w: number; readonly h: number };

export type FieldLayout = {
  readonly stage: StageBox;
  readonly core: Box;
  readonly rings: readonly RingLayout[];
  /** false when the content needs more room than the stage offers (the content keeps its size). */
  readonly fits: boolean;
  /** true when md frames were compacted for a narrow stage (`.topology[data-compact]`). */
  readonly compact: boolean;
};

/** Type metrics per node size (px at the 16px root). Slightly generous by design. */
const METRICS = {
  md: { char: 7.2, line: 18, metaChar: 6.2, metaLine: 15.5, marker: 15, padX: 14, padY: 9, minInner: 64, maxInner: 160, gaps: 4 },
  sm: { char: 6.7, line: 17, metaChar: 6.1, metaLine: 15.5, marker: 15, padX: 11, padY: 6, minInner: 56, maxInner: 170, gaps: 4 },
  dot: { char: 6.4, line: 14, metaChar: 5.8, metaLine: 12, marker: 0, padX: 6, padY: 6, minInner: 20, maxInner: 20, gaps: 0 },
} as const;
/** In a compact stage (narrow column) md frames wrap earlier: the frame compacts, the type does not (doc 23 §7.6). */
const COMPACT_MD_INNER = 132;

const GAP_ALONG_RING = 16; // px between neighbouring frames on the same ring
const GAP_CORE = 20; // px between the core's outer corner and the inner ring's frames
const GAP_RINGS = 24; // px between the frames of two rings
const STAGE_MARGIN = 8; // px kept free at the stage edge
const FIT_TOLERANCE = 12; // px a frame may reach into the stage's outer gap before the layout is called an overflow
const MAX_STRETCH = 1; // rings are circles (human review): no elliptical stretch into the longer stage axis; only an exhausted width grows a ring vertically (below)
/** Breathing-room fractions of the shorter stage side: a ring is never tighter than this when space exists. */
const BREATHE = [0.29, 0.41] as const;
/** Orbit bands (doc 25 §7.6): inner / middle / outer radius fractions of the shorter stage side. */
const BAND_FRACTION = { inner: 0.29, middle: 0.41, outer: 0.53 } as const;

/** FNV-1a hash → two stable unit floats per key: the deterministic organic offset source (doc 25 §7.7; no jitter). */
export function seeds(key: string): [number, number] {
  let h = 0x811c9dc5;
  for (let i = 0; i < key.length; i += 1) {
    h ^= key.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  const a = (h & 0xffff) / 0xffff;
  const b = ((h >>> 16) & 0xffff) / 0xffff;
  return [a, b];
}

/** Doc 25 §7.7 (calmed after human review): angle offset ±2°–5°, radius offset ±3 %–8 %, both fixed per node key —
 * controlled asymmetry, never a clump. */
export function organicOffset(key: string): { readonly angleDeg: number; readonly radiusFactor: number } {
  const [a, b] = seeds(key);
  const angleSign = a < 0.5 ? -1 : 1;
  const radiusSign = b < 0.5 ? -1 : 1;
  const angleDeg = angleSign * (2 + 3 * Math.abs(a * 2 - 1));
  const radiusFactor = 1 + radiusSign * (0.03 + 0.05 * Math.abs(b * 2 - 1));
  return { angleDeg: Math.round(angleDeg * 1000) / 1000, radiusFactor: Math.round(radiusFactor * 10000) / 10000 };
}

/** Doc 25 §7.3: semantic weight → visual mass factor (frame scale), bounded so mass never harms legibility. */
export function massOf(weight: number | undefined): number {
  if (weight === undefined) return 1;
  const clamped = Math.max(0.3, Math.min(1, weight));
  return Math.round((0.9 + 0.2 * ((clamped - 0.4) / 0.6)) * 1000) / 1000;
}

/** Rendered width of a token for an average char width: capitals and underscores are wide, i/l/punctuation narrow. */
function textWidth(text: string, charW: number): number {
  let w = 0;
  for (const ch of text) {
    if (/[A-Z_@#%&]/.test(ch)) w += charW * 1.22;
    else if (/[il.,:;'’|!\s]/.test(ch)) w += charW * 0.52;
    else if (/[mwMW]/.test(ch)) w += charW * 1.35;
    else w += charW;
  }
  return w;
}

function lines(text: string, charW: number, innerW: number): number {
  if (text.length === 0) return 0;
  let n = 1;
  let used = 0;
  for (const word of text.split(/\s+/)) {
    const w = textWidth(word, charW);
    if (w > innerW) {
      // a token longer than the frame wraps anywhere (overflow-wrap: anywhere)
      const rest = innerW - used;
      const carry = Math.max(0, w - rest);
      n += Math.ceil(carry / innerW);
      used = carry % innerW;
      continue;
    }
    const need = used === 0 ? w : used + charW + w;
    if (need > innerW) {
      n += 1;
      used = w;
    } else used = need;
  }
  return n;
}

/** The frame a node needs for its content: legible type first, frame second (doc 23 §6.3). */
export function estimateNodeBox(node: NodeContent, options: { readonly compact?: boolean } = {}): Box {
  const size = node.size ?? "md";
  if (size === "dot") return { w: 32, h: 32 };
  const m = METRICS[size];
  const maxInner = size === "md" && options.compact ? COMPACT_MD_INNER : m.maxInner;
  const labelW = Math.min(maxInner, Math.max(m.minInner, textWidth(node.label, m.char)));
  const metaW = node.meta ? Math.min(maxInner, textWidth(node.meta, m.metaChar)) : 0;
  const inner = Math.max(labelW, metaW, m.minInner);
  const labelLines = lines(node.label, m.char, inner);
  const metaLines = node.meta ? lines(node.meta, m.metaChar, inner) : 0;
  // conservative by design (real glyphs vary): a frame may be estimated larger than rendered, never smaller
  const w = Math.round((inner + 2 * m.padX) * 1.06);
  const h = Math.round((2 * m.padY + labelLines * m.line + metaLines * m.metaLine + m.marker + m.gaps + 2) * 1.04);
  return { w, h };
}

/** A stage narrower than this compacts md frames (matches `.topology[data-compact]` in the stylesheet). */
export const COMPACT_STAGE_WIDTH = 700;

export type CoreContent = { readonly title: string; readonly eyebrow?: string; readonly stateText?: string; readonly meta?: string };

/** The frame the core needs (the title is never clamped; doc 23 §6.2). */
export function estimateCoreBox(core: CoreContent): Box {
  const titleChar = 8.4;
  const titleLine = 22;
  const inner = Math.min(204, Math.max(140, textWidth(core.title, titleChar)));
  const titleLines = lines(core.title, titleChar, inner);
  const metaLines = core.meta ? lines(core.meta, 6.4, inner) : 0;
  const w = Math.max(196, Math.round(inner + 52));
  const h = Math.max(196, Math.round(48 + 14 + titleLines * titleLine + (core.stateText ? 20 : 0) + metaLines * 15 + 8));
  // the nucleus is a circle in the orbit (human review): its frame is the square of its longer side
  const side = Math.max(w, h);
  return { w: side, h: side };
}

const rad = (deg: number) => (deg * Math.PI) / 180;

/** The extent of a frame along the ring's tangent at a given angle (a wide frame needs more arc near the top/bottom). */
function tangentExtent(box: Box, angleDeg: number): number {
  const a = rad(angleDeg);
  return box.w * Math.abs(Math.sin(a)) + box.h * Math.abs(Math.cos(a));
}

type Placed = { readonly x: number; readonly y: number; readonly w: number; readonly h: number };

type FrameBox = Box & { key: string; scale: number; radiusFactor: number };

function place(boxes: readonly FrameBox[], rx: number, ry: number, angles: readonly number[]): PlacedNode[] {
  return boxes.map((b, i) => {
    const a = angles[i];
    const ox = Math.cos(rad(a));
    const oy = Math.sin(rad(a));
    return { ...b, angleDeg: a, ox, oy, x: ox * rx * b.radiusFactor, y: oy * ry * b.radiusFactor };
  });
}

function touch(a: Placed, b: Placed, gap: number): boolean {
  return Math.abs(a.x - b.x) * 2 < a.w + b.w + gap && Math.abs(a.y - b.y) * 2 < a.h + b.h + gap;
}

/** True when any node touches another node of the same ring or any of the `fixed` frames (core, inner rings). */
function anyOverlap(nodes: readonly PlacedNode[], fixed: readonly Placed[], gap: number): boolean {
  for (let i = 0; i < nodes.length; i += 1) {
    for (let j = i + 1; j < nodes.length; j += 1) if (touch(nodes[i], nodes[j], gap)) return true;
    for (const f of fixed) if (touch(nodes[i], f, gap)) return true;
  }
  return false;
}

function exceedsWidth(nodes: readonly PlacedNode[], stage: StageBox): boolean {
  return nodes.some((n) => Math.abs(n.x) + n.w / 2 > stage.w / 2 - STAGE_MARGIN);
}

function exceeds(nodes: readonly PlacedNode[], stage: StageBox): boolean {
  return exceedsWidth(nodes, stage) || nodes.some((n) => Math.abs(n.y) + n.h / 2 > stage.h / 2 - STAGE_MARGIN);
}

function overlapCount(nodes: readonly PlacedNode[], fixed: readonly Placed[], gap: number): number {
  let count = 0;
  for (let i = 0; i < nodes.length; i += 1) {
    for (let j = i + 1; j < nodes.length; j += 1) if (touch(nodes[i], nodes[j], gap)) count += 1;
    for (const f of fixed) if (touch(nodes[i], f, gap)) count += 1;
  }
  return count;
}

/** Deterministic search offsets (degrees) for an outer ring's start angle: the first collision-free one wins. */
const OFFSETS = [0, 8, -8, 16, -16, 24, -24, 32, -32, 40, -40, 48, -48] as const;

/**
 * Weighted angular allocation: each node's share of the circle is proportional to the arc its frame needs at its
 * (provisional) angle plus the gap; nodes are centred in their share, clockwise from `startDeg`, the first node
 * exactly at `startDeg`.
 */
function allocate(boxes: readonly Box[], startDeg: number): { angles: number[]; arcTotal: number } {
  const n = boxes.length;
  if (n === 0) return { angles: [], arcTotal: 0 };
  const even = boxes.map((_, i) => startDeg + (360 * i) / n);
  const arcs = boxes.map((b, i) => tangentExtent(b, even[i]) + GAP_ALONG_RING);
  const arcTotal = arcs.reduce((s, v) => s + v, 0);
  const angles: number[] = [];
  let cursor = 0;
  for (let i = 0; i < n; i += 1) {
    angles.push(startDeg + ((cursor + arcs[i] / 2) / arcTotal) * 360);
    cursor += arcs[i];
  }
  const shift = angles[0] - startDeg;
  return { angles: angles.map((a) => a - shift), arcTotal };
}

/**
 * Balanced interleave for an outer ring (human review: "arrange the fields more beautifully"): each outer node takes
 * the centre of the currently widest free arc between the inner ring's nodes, so an outer family fills the open sides
 * of the field instead of starting at a fixed offset. Deterministic (ties → the gap that starts first), and the
 * returned angles run clockwise from the ring's start, so the semantic order stays clockwise.
 */
function gapSlots(inner: readonly number[], k: number, start: number): number[] {
  const norm = (a: number) => ((a % 360) + 360) % 360;
  const sorted = [...new Set(inner.map((a) => Math.round(norm(a) * 1000) / 1000))].sort((x, y) => x - y);
  if (sorted.length === 0 || k === 0) return [];
  const gaps = sorted.map((s, i) => ({ start: s, size: i + 1 < sorted.length ? sorted[i + 1] - s : sorted[0] + 360 - s, m: 0 }));
  for (let j = 0; j < k; j += 1) {
    let best = gaps[0];
    for (const g of gaps) if (g.size / (g.m + 1) > best.size / (best.m + 1) + 1e-9) best = g;
    best.m += 1;
  }
  const slots = gaps.flatMap((g) => Array.from({ length: g.m }, (_, j) => g.start + (g.size * (j + 1)) / (g.m + 1)));
  const cw = (a: number) => norm(a - start);
  return slots.sort((x, y) => cw(x) - cw(y)).map((a) => start + cw(a));
}

function angularDistance(a: number, b: number): number {
  const d = Math.abs(((a - b) % 360) + 360) % 360;
  return Math.min(d, 360 - d);
}

export function layoutField(input: {
  readonly core: Box;
  readonly rings: readonly (readonly NodeContent[])[];
  /** A square stage (number) or a stage box; the ellipse uses the longer side for breathing room. */
  readonly stage: number | StageBox;
  readonly startDeg?: number;
  /** Force compact md frames (used for the constrained retry). */
  readonly compact?: boolean;
  /** Circle only (no elliptical stretch): used to derive the height the content needs from the width alone. */
  readonly noStretch?: boolean;
  /** Rendered frames by node key (client refinement, doc 23 §7.1): replace the estimates where known. */
  readonly measured?: Readonly<Record<string, Box>>;
}): FieldLayout {
  const stage: StageBox = typeof input.stage === "number" ? { w: input.stage, h: input.stage } : input.stage;
  const compact = input.compact ?? stage.w < COMPACT_STAGE_WIDTH;
  const attempt = (organic: number): FieldLayout => {
    const first = layoutOnce(input, stage, compact, organic);
    // when the wide frames cannot fit the stage, the frames compact (earlier wrapping) before anything overlaps or
    // leaves the stage — the type never shrinks (doc 23 §6.2, §7.6)
    if (!first.fits && !compact) {
      const retry = layoutOnce(input, stage, true, organic);
      const better = countOverlaps(retry) < countOverlaps(first) || (countOverlaps(retry) === countOverlaps(first) && requiredHalfWidth(retry) < requiredHalfWidth(first));
      if (retry.fits || better) return retry;
    }
    return first;
  };
  // organic offsets (doc 25 §7.7) breathe within the room the content leaves: full offsets when they fit, else
  // halved, quartered, none — deterministic, and never the reason a field falls out of its orbit (doc 23 §7.6)
  let best = attempt(1);
  if (best.fits) return best;
  for (const organic of ORGANIC_STEPS) {
    const candidate = attempt(organic);
    if (candidate.fits) return candidate;
    if (countOverlaps(candidate) < countOverlaps(best)) best = candidate;
  }
  return best;
}

const ORGANIC_STEPS = [0.5, 0.25, 0] as const;

function countOverlaps(layout: FieldLayout): number {
  const all: Placed[] = [{ x: 0, y: 0, w: layout.core.w, h: layout.core.h }, ...layout.rings.flatMap((r) => r.nodes)];
  let count = 0;
  for (let i = 0; i < all.length; i += 1) for (let j = i + 1; j < all.length; j += 1) if (touch(all[i], all[j], 0)) count += 1;
  return count;
}

function layoutOnce(
  input: { readonly core: Box; readonly rings: readonly (readonly NodeContent[])[]; readonly startDeg?: number; readonly noStretch?: boolean; readonly measured?: Readonly<Record<string, Box>> },
  stage: StageBox,
  compact: boolean,
  organic = 1,
): FieldLayout {
  const short = Math.min(stage.w, stage.h);
  const sx = input.noStretch ? 1 : Math.min(MAX_STRETCH, stage.w / short);
  const sy = input.noStretch ? 1 : Math.min(MAX_STRETCH, stage.h / short);
  const coreRadius = Math.max(input.core.w, input.core.h) / 2;
  const rings: RingLayout[] = [];
  const fixed: Placed[] = [{ x: 0, y: 0, w: input.core.w, h: input.core.h }];
  let fits = true;
  let innerEdge = coreRadius + GAP_CORE;
  let innerAngles: number[] = [];
  let innerShare = 360;
  const start = input.startDeg ?? -90;

  input.rings.forEach((contents, ringIndex) => {
    const boxes: FrameBox[] = contents.map((c, i) => {
      const key = c.key ?? `${ringIndex}-${i}`;
      const m = input.measured?.[key];
      const scale = massOf(c.weight);
      const est = estimateNodeBox(c, { compact });
      // mass is presence, not type: the stylesheet grows the membrane's padding by 6 px / 4 px per side per unit of
      // (mass − 0.9) and the aura outside the frame; the estimate follows exactly that law (never a scaled frame,
      // which would over-estimate and decide the stack before the rendered frames could refine it)
      const box = c.box ? { w: c.box.w, h: c.box.h } : m && m.w > 0 && m.h > 0 ? { w: m.w, h: m.h } : { w: Math.round(est.w + 12 * (scale - 0.9)), h: Math.round(est.h + 8 * (scale - 0.9)) };
      // heavier entities sit slightly closer to the core (doc 25 §7.6: primary nodes closer, larger)
      const closeness = 1 - 0.05 * ((c.weight ?? 0.7) - 0.7);
      const offset = c.key ? organicOffset(c.key) : { angleDeg: 0, radiusFactor: 1 };
      const radiusFactor = 1 + (offset.radiusFactor - 1) * organic;
      return { ...box, key, scale, radiusFactor: Math.round(radiusFactor * closeness * 10000) / 10000 };
    });
    const band = contents.find((c) => c.band)?.band;
    const maxW = boxes.reduce((m, b) => Math.max(m, b.w), 0);
    const maxH = boxes.reduce((m, b) => Math.max(m, b.h), 0);
    // an outer ring starts half an inner share later, so no outer node sits on the first inner spoke
    const startDeg = ringIndex === 0 ? start : start + innerShare / 2;
    const { angles: weighted, arcTotal } = allocate(boxes, startDeg);
    // an outer ring interleaves into the inner ring's widest free arcs; the inner ring keeps its content-weighted
    // allocation from the top
    const even = ringIndex > 0 && innerAngles.length > 0 ? gapSlots(innerAngles, boxes.length, start) : weighted;
    // deterministic organic angle offsets (doc 25 §7.7): fixed per node key, never random
    const allocated = even.map((a, i) => a + (contents[i].key ? organicOffset(contents[i].key as string).angleDeg * organic : 0));
    // nudge any outer node off an inner spoke (deterministic, order-preserving; doc 23 §7.5)
    const offSpokes = (list: readonly number[]) =>
      ringIndex > 0 && innerAngles.length > 0
        ? list.map((a) => {
            let out = a;
            for (let k = 0; k < 8 && innerAngles.some((ia) => angularDistance(out, ia) < 4); k += 1) out += 5;
            return out;
          })
        : [...list];
    let angles = offSpokes(allocated);
    const required = arcTotal / (2 * Math.PI);
    // the inner ring keeps clear of the core by construction; an outer ring starts just outside the inner ring's
    // radius and the collision loop below moves it out only as far as the ACTUAL frames require (content-aware)
    // soft minimum only: the inner ring clears the core's longer side, an outer ring starts just outside the
    // inner ring; the collision loop below moves a ring out exactly as far as the ACTUAL frames require
    const minRadius = ringIndex === 0 ? innerEdge + 12 : rings[ringIndex - 1].radius + 12;
    // breathing room (doc 23 §7.6) only as far as the stage allows: the largest radius whose frames stay inside
    const fitMax = Math.min((stage.w / 2 - STAGE_MARGIN - maxW / 2) / sx, (stage.h / 2 - STAGE_MARGIN - maxH / 2) / sy);
    const fraction = band ? BAND_FRACTION[band] : (BREATHE[Math.min(ringIndex, BREATHE.length - 1)] ?? BREATHE[BREATHE.length - 1]);
    const breathing = Math.min(short * fraction, Math.max(fitMax, 0));
    let radius = Math.max(required, minRadius, breathing);
    // the elliptical stretch only uses room the stage actually has: a stretched axis never pushes frames out
    const stretch = (axis: number, room: number) => Math.max(1, Math.min(axis, room / Math.max(radius, 1)));
    const ex = stretch(sx, stage.w / 2 - STAGE_MARGIN - maxW / 2);
    const ey = stretch(sy, stage.h / 2 - STAGE_MARGIN - maxH / 2);
    let nodes = place(boxes, radius * ex, radius * ey, angles);
    if (ringIndex > 0 && anyOverlap(nodes, fixed, 8)) {
      // an outer ring first looks for a start angle that clears the inner frames (topology-aware), before it
      // spends radius: the first collision-free offset wins, otherwise the one with the fewest collisions
      let best = { offset: 0, count: overlapCount(nodes, fixed, 8) };
      for (const offset of OFFSETS) {
        const candidate = place(boxes, radius * ex, radius * ey, angles.map((a) => a + offset));
        const count = overlapCount(candidate, fixed, 8);
        if (count < best.count) best = { offset, count };
        if (count === 0) break;
      }
      angles = offSpokes(angles.map((a) => a + best.offset));
      nodes = place(boxes, radius * ex, radius * ey, angles);
    }
    // collision resistance: grow until no frame touches another frame, an inner ring's frame or the core;
    // the stage's WIDTH bounds the growth (the box height follows the content), and an exhausted stage is
    // reported — the content is never shrunk
    // once the WIDTH is exhausted the ring grows into a taller ellipse instead (the box height follows the
    // content); only when that is exhausted too is the overflow reported
    let guard = 0;
    let ky = 1; // extra vertical stretch applied when the width is exhausted
    while (anyOverlap(nodes, fixed, 8) && guard < 140) {
      guard += 1;
      if (!exceedsWidth(nodes, stage)) {
        // a radius step that would leave the width is not taken: growth switches to the vertical axis instead
        const grown = place(boxes, (radius + 6) * ex, (radius + 6) * ey * ky, angles);
        if (!exceedsWidth(grown, stage)) {
          radius += 6;
          nodes = grown;
          continue;
        }
      }
      ky += 0.03;
      if (ky > 2.4) break;
      nodes = place(boxes, radius * ex, radius * ey * ky, angles);
    }
    if (anyOverlap(nodes, fixed, 0) || exceeds(nodes, { w: stage.w + 2 * FIT_TOLERANCE, h: stage.h + 2 * FIT_TOLERANCE })) fits = false;
    rings.push({ rx: Math.round(radius * ex * 100) / 100, ry: Math.round(radius * ey * ky * 100) / 100, radius: Math.round(radius * 100) / 100, maxW, maxH, nodes });
    fixed.push(...nodes);
    innerEdge = radius + maxH / 2 + GAP_RINGS;
    innerAngles = nodes.map((n) => n.angleDeg);
    innerShare = boxes.length > 0 ? 360 / boxes.length : 360;
  });
  return { stage, core: input.core, rings, fits, compact };
}

/** The vertical extent (px) the placed content needs from the stage centre, plus the edge margin. */
export function requiredHalfHeight(layout: FieldLayout): number {
  const nodes = layout.rings.flatMap((r) => r.nodes);
  const half = nodes.reduce((m, n) => Math.max(m, Math.abs(n.y) + n.h / 2), layout.core.h / 2);
  return Math.ceil(half + STAGE_MARGIN + 2);
}

/** The horizontal extent (px) the placed content needs from the stage centre, plus the edge margin. */
export function requiredHalfWidth(layout: FieldLayout): number {
  const nodes = layout.rings.flatMap((r) => r.nodes);
  const half = nodes.reduce((m, n) => Math.max(m, Math.abs(n.x) + n.w / 2), layout.core.w / 2);
  return Math.ceil(half + STAGE_MARGIN + 2);
}

/** Viewport classes (doc 23 §7.4, §14): the same class always yields the same decision. */
export type ViewportClass = "desktop" | "wide";

/** The decision stage per viewport class: the orbit column that class gives the topology, with room to grow tall. */
export const DECISION_STAGE: Readonly<Record<ViewportClass, StageBox>> = {
  desktop: { w: 700, h: 1400 },
  wide: { w: 820, h: 1500 },
};

/** The viewport class from the stage's measured width (the main column; ~48px narrower than the viewport). */
export function viewportClass(stageWidth: number): ViewportClass {
  return stageWidth >= 1400 ? "wide" : "desktop";
}

/**
 * Orbit or stack for a surface, decided from the CONTENT on the viewport class's decision stage (deterministic for
 * the same content and class; the server assumes "desktop"): when the frames cannot be placed without overlap even
 * on a tall ellipse, the relational stack is the compacted representation (doc 23 §7.6, §14) — the content keeps
 * its size. The stage's width does not depend on the mode, so the decision never loops.
 */
export function stageMode(
  core: CoreContent,
  rings: readonly (readonly NodeContent[])[],
  vp: ViewportClass = "desktop",
  frames?: { readonly nodes: Readonly<Record<string, Box>>; readonly core?: Box },
): "orbit" | "stack" {
  const total = rings.reduce((s, r) => s + r.length, 0);
  if (total === 0) return "stack";
  return layoutField({ core: frames?.core ?? estimateCoreBox(core), rings, stage: DECISION_STAGE[vp], measured: frames?.nodes }).fits ? "orbit" : "stack";
}

/**
 * The box height the content needs for a given width, derived from a circular layout (no stretch) so that it is
 * a function of the WIDTH alone: a taller box never changes it, which is what makes the height growth converge.
 */
export function requiredStageHeight(core: Box, rings: readonly (readonly NodeContent[])[], width: number): number {
  const square = layoutField({ core, rings, stage: { w: width, h: Math.max(width, 200) }, noStretch: true });
  return requiredHalfHeight(square) * 2;
}
