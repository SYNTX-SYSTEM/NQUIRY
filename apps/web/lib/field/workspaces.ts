/**
 * SF-05 (doc 26 §7) Workspace projection normalization — the authoritative producer for the Workspace overview.
 *
 * Hard law: ONE CANONICAL WORKSPACE ID → ONE PRIMARY VISIBLE WORKSPACE NODE per projection context. The canonical key
 * is `workspaceId`, never the display name, the array position or the object reference. Repeated records of the
 * same Workspace (several membership relations) merge into one entity that carries its relation count; two
 * different Workspaces that share a display name stay two Workspaces and are DISAMBIGUATED by canonical facts the
 * server already sends (founding time, identity) so that no human can reasonably believe the same Workspace exists
 * twice (doc 26 §7 acceptance question). Normalization happens here, before any geometry; the layout consumes the
 * normalized identities only. Pure: no I/O, no DOM.
 */
export type WorkspaceRecord = {
  readonly workspaceId: string;
  readonly name: string;
  readonly ownerId?: string;
  readonly createdAt?: string;
};

export type NormalizedWorkspace = {
  readonly workspaceId: string;
  readonly name: string;
  readonly ownerId: string | null;
  readonly createdAt: string | null;
  /** How many canonical records (relations) mapped to this Workspace: 1 for a plain membership. */
  readonly relationCount: number;
  /** How many DIFFERENT Workspaces share this display name (1 = unique name). */
  readonly homonyms: number;
  /** Canonical distinguisher shown when the name is not unique (founding time · short id); null when unique. */
  readonly distinguisher: string | null;
  /** The first 8 characters of the canonical id: a stable, human-checkable handle (never the title). */
  readonly shortId: string;
};

const FOUNDED = new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", hour12: false, timeZone: "UTC" });

function foundedText(createdAt: string | null): string | null {
  if (!createdAt) return null;
  const d = new Date(createdAt);
  return Number.isNaN(d.getTime()) ? null : `founded ${FOUNDED.format(d)} UTC`;
}

/** Merge repeated records by `workspaceId` (first-seen order kept), then mark homonymous names. */
export function normalizeWorkspaces(records: readonly WorkspaceRecord[]): NormalizedWorkspace[] {
  const byId = new Map<string, { record: WorkspaceRecord; count: number }>();
  for (const r of records) {
    const seen = byId.get(r.workspaceId);
    if (seen) seen.count += 1;
    else byId.set(r.workspaceId, { record: r, count: 1 });
  }
  const nameCount = new Map<string, number>();
  for (const { record } of byId.values()) nameCount.set(record.name, (nameCount.get(record.name) ?? 0) + 1);
  return [...byId.values()].map(({ record, count }) => {
    const homonyms = nameCount.get(record.name) ?? 1;
    const shortId = record.workspaceId.slice(0, 8);
    const founded = foundedText(record.createdAt ?? null);
    const distinguisher = homonyms > 1 ? [founded, shortId].filter(Boolean).join(" · ") : null;
    return {
      workspaceId: record.workspaceId,
      name: record.name,
      ownerId: record.ownerId ?? null,
      createdAt: record.createdAt ?? null,
      relationCount: count,
      homonyms,
      distinguisher,
      shortId,
    };
  });
}
