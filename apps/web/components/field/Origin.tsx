/**
 * SF-01 Origin grammar (21 §16, §10 semiotic constants): the four mandatory
 * origin classes. Each carries its origin in words (accessible name), in
 * structure (`data-origin`) and in a typographic role. Color is never the only
 * carrier.
 *
 * SF-01 APPLIES only `system-state` (canonical states). `human-source`,
 * `ai-derived` and `external-evidence` are grammar only: their content belongs
 * to F03 / F04 / F05-F06, which own those relations. AI-derived cannot be
 * rendered without its source lineage (21 §3: AI DERIVED → visible source
 * lineage).
 */
export type OriginClass = "human-source" | "system-state" | "ai-derived" | "external-evidence";

const ORIGIN_NAME: Readonly<Record<OriginClass, string>> = {
  "human-source": "Human source",
  "system-state": "System state",
  "ai-derived": "AI-derived",
  "external-evidence": "External evidence",
};

const TYPE_ROLE: Readonly<Record<OriginClass, string>> = {
  "human-source": "t-source",
  "system-state": "t-system",
  "ai-derived": "t-derived",
  "external-evidence": "t-evidence",
};

export function OriginMark({
  origin,
  lineage,
  children,
}: {
  readonly origin: OriginClass;
  /** Required for `ai-derived`: what it was derived from. */
  readonly lineage?: string;
  readonly children: React.ReactNode;
}) {
  if (origin === "ai-derived" && !lineage) {
    throw new Error("AI-derived content must carry its source lineage");
  }
  const name = origin === "ai-derived" ? `${ORIGIN_NAME[origin]} from ${lineage}` : ORIGIN_NAME[origin];
  return (
    <span className={`origin ${TYPE_ROLE[origin]}`} data-origin={origin}>
      <span className="visually-hidden">{name}: </span>
      {children}
    </span>
  );
}

/** A canonical state name, rendered as SYSTEM STATE (structural, never a chat voice). */
export function StateName({ state }: { readonly state: string }) {
  return (
    <OriginMark origin="system-state">
      <span className="state">{state}</span>
    </OriginMark>
  );
}
