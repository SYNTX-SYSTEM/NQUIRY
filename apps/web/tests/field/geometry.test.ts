/**
 * SF-03 WU-SF03.2 (L0): content-aware, topology-aware, deterministic Field geometry (doc 23 §7).
 *
 * Falsifiers 12–18: nodes overlap; nodes collide with the Core; same-spoke stacking; random or unstable
 * geometry; false gravity by proximity; compressed Field in a large viewport.
 */
import { describe, expect, it } from "vitest";
import { estimateCoreBox, estimateNodeBox, layoutField, type NodeContent } from "../../lib/field/geometry";

function node(label: string, opts: Partial<NodeContent> = {}): NodeContent {
  return { label, size: "md", ...opts };
}

function overlaps(a: { x: number; y: number; w: number; h: number }, b: { x: number; y: number; w: number; h: number }): boolean {
  return Math.abs(a.x - b.x) * 2 < a.w + b.w && Math.abs(a.y - b.y) * 2 < a.h + b.h;
}

describe("estimateNodeBox (frames follow content, doc 23 §6.3)", () => {
  it("grows with the label and wraps at the size's maximum width instead of shrinking the text", () => {
    const short = estimateNodeBox(node("Draft"));
    const long = estimateNodeBox(node("Why did activation stall after onboarding for enterprise customers?"));
    expect(long.w).toBeGreaterThan(short.w);
    expect(long.w).toBeLessThanOrEqual(estimateNodeBox(node("x".repeat(400))).w);
    expect(long.h).toBeGreaterThan(short.h);
  });
  it("adds meta and marker lines to the height", () => {
    const bare = estimateNodeBox(node("Session"));
    const withMeta = estimateNodeBox(node("Session", { meta: "SESSION_CONTROL_RIGHT · granted by Inspect Owner" }));
    expect(withMeta.h).toBeGreaterThan(bare.h);
  });
  it("is deterministic", () => {
    const a = estimateNodeBox(node("Facilitator Fay", { meta: "Facilitator", size: "sm" }));
    const b = estimateNodeBox(node("Facilitator Fay", { meta: "Facilitator", size: "sm" }));
    expect(a).toEqual(b);
  });
});

describe("layoutField (doc 23 §7.3–§7.5)", () => {
  const core = estimateCoreBox({ title: "Why did activation stall after onboarding?", eyebrow: "Challenge", stateText: "3 Sessions", meta: "SF-02 Inspection" });

  it("places every node on its ring without any pair overlapping and without touching the core", () => {
    const ring1 = [node("Open Session", { meta: "possible next relation" }), ...Array.from({ length: 6 }, (_, i) => node(`Session opened Sep 25, 2026, ${i + 1}:0${i} AM`, { meta: "QUESTION_CAPTURE" }))];
    const ring2 = [node("Inspect Facilitator", { meta: "SESSION_CONTROL_RIGHT · granted by Inspect Owner", size: "sm" }), node("Inspect Owner", { meta: "Owner", size: "sm" })];
    const layout = layoutField({ core, rings: [ring1, ring2], stage: 900 });
    const boxes = layout.rings.flatMap((r) => r.nodes);
    for (let i = 0; i < boxes.length; i += 1) {
      for (let j = i + 1; j < boxes.length; j += 1) {
        expect(overlaps(boxes[i], boxes[j]), `${boxes[i].key} overlaps ${boxes[j].key}`).toBe(false);
      }
      expect(overlaps(boxes[i], { x: 0, y: 0, w: core.w, h: core.h }), `${boxes[i].key} touches the core`).toBe(false);
    }
  });

  it("weights the angular share by the node's extent, so wide nodes get more arc (content-aware)", () => {
    const layout = layoutField({ core, rings: [[node("A"), node("A very long label that needs a wide frame around it, really wide"), node("B"), node("C")]], stage: 900 });
    const a = layout.rings[0].nodes.map((n) => n.angleDeg);
    const share = (i: number) => (((a[(i + 1) % 4] - a[i]) % 360) + 360) % 360 + (((a[i] - a[(i - 1 + 4) % 4]) % 360) + 360) % 360;
    expect(share(1)).toBeGreaterThan(share(2));
  });

  it("keeps the semantic order clockwise from the ring's start angle", () => {
    const layout = layoutField({ core, rings: [[node("1"), node("2"), node("3"), node("4"), node("5")]], stage: 900 });
    const angles = layout.rings[0].nodes.map((n) => n.angleDeg);
    for (let i = 1; i < angles.length; i += 1) expect(angles[i]).toBeGreaterThan(angles[i - 1]);
    expect(angles[0]).toBeCloseTo(-90, 6);
  });

  it("never lets an outer node share a spoke with an inner node, and separates the rings by their box heights", () => {
    const ring1 = Array.from({ length: 13 }, (_, i) => node(`${i + 1}. Phase ${i + 1}`, { size: "sm" }));
    const ring2 = [node("Inspect Facilitator", { meta: "participant · Session controller", size: "sm" }), node("Inspect Owner", { meta: "participant", size: "sm" })];
    const layout = layoutField({ core, rings: [ring1, ring2], stage: 900 });
    // rings are separated by their ACTUAL frames (collision loop), not by a worst-case height rule
    expect(layout.rings[1].radius).toBeGreaterThan(layout.rings[0].radius);
    const inner = layout.rings[0].nodes;
    for (const o of layout.rings[1].nodes) for (const i of inner) expect(overlaps(o, i), `${o.key} touches ${i.key}`).toBe(false);
    const innerAngles = layout.rings[0].nodes.map((n) => n.angleDeg);
    for (const o of layout.rings[1].nodes) expect(innerAngles.some((a) => Math.abs(a - o.angleDeg) < 2)).toBe(false);
  });

  it("expands the radius when the nodes need more circumference, and uses a larger stage for breathing room (viewport-aware)", () => {
    const few = layoutField({ core, rings: [[node("A"), node("B"), node("C")]], stage: 720 });
    const many = layoutField({ core, rings: [Array.from({ length: 9 }, (_, i) => node(`Session opened Sep 25, 2026, ${i}:00 AM`, { meta: "DRAFT" }))], stage: 720 });
    expect(many.rings[0].radius).toBeGreaterThan(few.rings[0].radius);
    const roomy = layoutField({ core, rings: [[node("A"), node("B"), node("C")]], stage: 1000 });
    expect(roomy.rings[0].radius).toBeGreaterThan(few.rings[0].radius);
  });

  it("stretches a ring into the longer stage axis for breathing room, staying inside the stage (viewport-aware ellipse)", () => {
    const rings = [[node("Open Session", { meta: "possible next relation" }), ...Array.from({ length: 4 }, (_, i) => node(`Session opened Sep 25, 2026, 2:${i}0 AM`, { meta: "QUESTION_CAPTURE" }))], [node("Inspect Facilitator", { meta: "SESSION_CONTROL_RIGHT · granted by Inspect Owner", size: "sm" })]];
    const wide = layoutField({ core, rings, stage: { w: 760, h: 900 } });
    expect(wide.rings[0].ry).toBeGreaterThan(wide.rings[0].rx);
    for (const n of wide.rings.flatMap((r) => r.nodes)) {
      expect(Math.abs(n.x) + n.w / 2).toBeLessThanOrEqual(380);
      expect(Math.abs(n.y) + n.h / 2).toBeLessThanOrEqual(450);
    }
    expect(wide.fits).toBe(true);
  });

  it("is deterministic and stable: the same content yields the identical layout", () => {
    const rings = [[node("A"), node("B")], [node("C", { size: "sm" })]];
    expect(layoutField({ core, rings, stage: 900 })).toEqual(layoutField({ core, rings, stage: 900 }));
  });

  it("reports a fit that the stage can hold, or flags the overflow instead of shrinking text (falsifier 8)", () => {
    const huge = layoutField({ core, rings: [Array.from({ length: 10 }, (_, i) => node(`A very long session label number ${i} that goes on`, { meta: "QUESTION_GENERATION" }))], stage: 600 });
    expect(typeof huge.fits).toBe("boolean");
    // a narrow stage compacts the frame (earlier wrapping), never the type: every frame is still the estimate
    expect(huge.compact).toBe(true);
    expect(huge.rings[0].nodes.every((n) => n.w >= estimateNodeBox(node("A very long session label number 0 that goes on", { meta: "QUESTION_GENERATION" }), { compact: true }).w - 1)).toBe(true);
    expect(estimateNodeBox(node("A very long session label number 0 that goes on"), { compact: true }).h).toBeGreaterThanOrEqual(estimateNodeBox(node("A very long session label number 0 that goes on")).h);
  });
});

describe("SF-04 living field entity geometry (doc 25 §5.3, §7.6, §7.7)", () => {
  const core = estimateCoreBox({ title: "Why did activation stall after onboarding?" });
  const ring = (band: "inner" | "middle" | "outer", n = 4) => Array.from({ length: n }, (_, i) => node(`Entity ${i}`, { key: `${band}-${i}`, band, weight: 0.7 }));
  it("orbit bands order the radii: inner < middle < outer, for the same content", () => {
    const l = layoutField({ core, rings: [ring("inner"), ring("middle"), ring("outer")], stage: 1100 });
    expect(l.rings[0].radius).toBeLessThan(l.rings[1].radius);
    expect(l.rings[1].radius).toBeLessThan(l.rings[2].radius);
  });
  it("organic offsets are deterministic per node key, bounded (angle ±4–11°, radius ±3–8 %) and never random", () => {
    const a = layoutField({ core, rings: [ring("inner", 6)], stage: 1000 });
    const b = layoutField({ core, rings: [ring("inner", 6)], stage: 1000 });
    expect(a).toEqual(b);
    const nodes = a.rings[0].nodes;
    const even = nodes.map((_, i) => -90 + (360 * i) / nodes.length);
    for (let i = 0; i < nodes.length; i += 1) {
      const dAngle = Math.abs(nodes[i].angleDeg - even[i]);
      expect(dAngle).toBeGreaterThanOrEqual(4 - 1e-6);
      expect(dAngle).toBeLessThanOrEqual(11 + 1e-6);
      const r = Math.hypot(nodes[i].x / (a.rings[0].rx / a.rings[0].radius), nodes[i].y / (a.rings[0].ry / a.rings[0].radius));
      const dr = Math.abs(r - a.rings[0].radius) / a.rings[0].radius;
      expect(dr).toBeGreaterThanOrEqual(0.03 - 1e-6);
      expect(dr).toBeLessThanOrEqual(0.08 + 1e-6);
    }
    expect(new Set(nodes.map((n) => n.angleDeg.toFixed(3))).size).toBe(nodes.length);
  });
  it("semanticWeight scales the frame (visual mass) and never the role or the band; a heavier entity sits slightly closer", () => {
    const light = layoutField({ core, rings: [[node("A", { key: "a", weight: 0.45 }), node("B", { key: "b", weight: 0.45 })]], stage: 1000 });
    const heavy = layoutField({ core, rings: [[node("A", { key: "a", weight: 1 }), node("B", { key: "b", weight: 0.45 })]], stage: 1000 });
    expect(heavy.rings[0].nodes[0].w).toBeGreaterThan(light.rings[0].nodes[0].w);
    expect(heavy.rings[0].nodes[0].scale).toBeGreaterThan(light.rings[0].nodes[0].scale);
    expect(heavy.rings[0].nodes[1].scale).toEqual(light.rings[0].nodes[1].scale);
    expect(Math.hypot(heavy.rings[0].nodes[0].x, heavy.rings[0].nodes[0].y)).toBeLessThanOrEqual(Math.hypot(light.rings[0].nodes[0].x, light.rings[0].nodes[0].y) + 1e-6);
  });
  it("offsets never create an overlap or a core collision (the collision loop still governs)", () => {
    const l = layoutField({ core, rings: [ring("inner", 7), ring("middle", 4)], stage: { w: 900, h: 900 } });
    const all = l.rings.flatMap((r) => r.nodes);
    for (let i = 0; i < all.length; i += 1) for (let j = i + 1; j < all.length; j += 1) expect(overlaps(all[i], all[j])).toBe(false);
    for (const n of all) expect(overlaps(n, { x: 0, y: 0, w: core.w, h: core.h })).toBe(false);
  });
});
