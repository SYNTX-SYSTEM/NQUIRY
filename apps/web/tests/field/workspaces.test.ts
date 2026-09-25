/**
 * SF-05 WU-26.1 (L0): Workspace normalization at the producer (doc 26 §7, §41 falsifiers 1–4, 9–10).
 */
import { describe, expect, it } from "vitest";
import { normalizeWorkspaces } from "../../lib/field/workspaces";

const A = { workspaceId: "aaaaaaaa-0000-4000-8000-000000000001", name: "SF-03 Inspection", ownerId: "u1", createdAt: "2026-09-25T08:25:04Z" };
const B = { workspaceId: "bbbbbbbb-0000-4000-8000-000000000002", name: "SF-03 Inspection", ownerId: "u1", createdAt: "2026-09-25T09:03:41Z" };
const C = { workspaceId: "cccccccc-0000-4000-8000-000000000003", name: "Unique name", ownerId: "u2", createdAt: "2026-09-25T10:00:00Z" };

describe("normalizeWorkspaces: one canonical id → one entity", () => {
  it("merges repeated records of the same workspace.id into one entity carrying the relation count (falsifiers 1, 4)", () => {
    const out = normalizeWorkspaces([A, C, A, A]);
    expect(out.map((w) => w.workspaceId)).toEqual([A.workspaceId, C.workspaceId]);
    expect(out[0].relationCount).toBe(3);
    expect(out[1].relationCount).toBe(1);
  });
  it("keeps two different Workspaces with the same display name as two entities, disambiguated by canonical facts (falsifier 10)", () => {
    const out = normalizeWorkspaces([A, B]);
    expect(out).toHaveLength(2);
    expect(out[0].homonyms).toBe(2);
    expect(out[0].distinguisher).toMatch(/^founded 25 Sept,? 08:25 UTC · aaaaaaaa$/);
    expect(out[1].distinguisher).toMatch(/^founded 25 Sept,? 09:03 UTC · bbbbbbbb$/);
    expect(out[0].distinguisher).not.toBe(out[1].distinguisher);
  });
  it("never deduplicates by name: object identity and textual equality do not merge", () => {
    const clone = { ...B };
    expect(normalizeWorkspaces([A, clone, { ...A, name: "SF-03 Inspection" }])).toHaveLength(2);
  });
  it("leaves unique Workspaces unmarked (no distinguisher) and keeps the server's order (stable layout input)", () => {
    const out = normalizeWorkspaces([C, A, B]);
    expect(out.map((w) => w.shortId)).toEqual(["cccccccc", "aaaaaaaa", "bbbbbbbb"]);
    expect(out[0].distinguisher).toBeNull();
    expect(out[0].homonyms).toBe(1);
    expect(normalizeWorkspaces([C, A, B])).toEqual(out);
  });
  it("tolerates records without founding time (short id alone disambiguates)", () => {
    const out = normalizeWorkspaces([{ workspaceId: "x1", name: "n" }, { workspaceId: "x2", name: "n" }]);
    expect(out.map((w) => w.distinguisher)).toEqual(["x1", "x2"]);
  });
});
