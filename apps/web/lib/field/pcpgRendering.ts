/**
 * CYAN-PCPG-06 — rendering derivation for Architecture 27 v4 levels 0.5 (action-adjacent attachment), 1 (contextual
 * governance panel) and 2 (deep field inspection), plus the §09.3 boundary card. Pure and deterministic: it reads the
 * ObservationPresence (crossed PCPG-R12/1 facts), the CYAN-local presentation (§06) and the CYAN-local attachment
 * relation (§13.6) and produces WORDS and PLACEMENTS. It never derives a governance consequence, never names a
 * backend component, never produces an affordance.
 *
 *   PCPG-R12/1 + presentationOf + attachPresentation
 *   → AreaRendering per existing object area (what crossed steps are placed there, in words)
 *   → BoundaryCard (what stopped · requested in · why · after · Human Authority required for · placed at)
 *   → PanelModel (label · capability axes · basis · semantic observation · attachments · deltas · chain · HAR ·
 *                 provider / send · Session-level proof ceiling · not materialized)
 *
 * Laws (v4 §21): INDETERMINATE is never "denied"; `target` null is "unresolved", never "out of scope"; `operation`
 * null is "Unknown operation"; a superseded observation keeps its words and says so; SEND is "not materialized";
 * HAR never yields a control; PRESENTATION LOCATION != GOVERNANCE TRUTH.
 */
import type { ChainWire, DeltaWire, GovernanceObservationCurrent } from "../api/pcpgClient";
import { attachPresentation, CYAN_OBJECT_AREAS, type AttachedPresentation, type CyanObjectArea } from "./pcpgAttachment";
import {
  type ObservationPresence,
  type ObservationPresentation,
  type PresentationCategory,
  type ProofCeilingPresentation,
  proofCeilingPresentation,
} from "./pcpgPresentation";

// ---------------------------------------------------------------------------------------------------------------------
// Words for crossed values (closed vocabularies → human words; never a new fact)
// ---------------------------------------------------------------------------------------------------------------------

export const RESULT_WORDS: Readonly<Record<DeltaWire["result"], string>> = {
  ALLOWED: "allowed",
  HUMAN_ACTION_AVAILABLE: "a human action is available",
  STATE_BOUNDARY: "state boundary",
  AUTHORITY_BOUNDARY: "authority boundary",
  DATA_BOUNDARY: "data boundary",
  GOVERNANCE_BOUNDARY: "governance boundary",
  DENIED: "denied",
  INDETERMINATE: "indeterminate",
};

export const EXECUTION_WORDS: Readonly<Record<DeltaWire["executionClass"], string>> = {
  PROVIDER_COMPUTATION: "provider computation",
  HUMAN_COMMAND: "human command",
  EXTERNAL_EFFECT: "external effect",
  DISCLOSURE: "disclosure",
  UNKNOWN: "unknown execution class",
};

/** `operation` null = UNKNOWN (v4 §08.1); the id is RED's own operation-index id, shown verbatim. */
export function operationWords(operation: string | null): string {
  return operation === null ? "Unknown operation" : operation;
}
/** `target` null is unresolved, never out of scope (v4 §21). */
export function targetWords(target: string | null): string {
  if (target === null) return "unresolved";
  if (target === "OUT_OF_SCOPE") return "out of scope";
  return target;
}
export function resultWords(delta: Pick<DeltaWire, "result" | "reasonCode">): string {
  return delta.reasonCode === null ? RESULT_WORDS[delta.result] : `${RESULT_WORDS[delta.result]} · ${delta.reasonCode}`;
}
/** One line per crossed delta: "<operation> · <execution class> — <result · reasonCode>". */
export function deltaLine(delta: DeltaWire): string {
  return `${operationWords(delta.operation)} · ${EXECUTION_WORDS[delta.executionClass]} — ${resultWords(delta)}`;
}
export const SEND_NOT_MATERIALIZED = "Send not materialized" as const;
export const PROVIDER_NOT_EXECUTABLE = "Provider not executable" as const;

// ---------------------------------------------------------------------------------------------------------------------
// Area rendering (level 0.5)
// ---------------------------------------------------------------------------------------------------------------------

export interface PlacedDelta {
  readonly delta: DeltaWire;
  readonly categories: readonly PresentationCategory[];
  /** CYAN-local reading (v4 §08.2): member of chain.maximumLegitimateTransition. */
  readonly retained: boolean;
  readonly isFirstBroken: boolean;
  readonly humanAuthorityRequired: boolean;
  readonly line: string;
}

export interface AreaRendering {
  readonly area: CyanObjectArea;
  /** The area's words from the attachment map (never a backend name). */
  readonly words: string;
  readonly deltas: readonly PlacedDelta[];
  readonly firstBrokenHere: boolean;
  readonly humanAuthorityHere: boolean;
  /** PROVIDER_RELATED_AREA with providerExecutable = false and a provider delta present (v4 §07.4, §11.3). */
  readonly providerNotExecutable: boolean;
  readonly superseded: boolean;
  /** Short words for the marker: "n crossed step(s) placed here". */
  readonly summary: string;
}

export interface BoundaryCard {
  readonly whatStopped: string; // "<operation> · <execution class>"
  readonly requestedIn: string; // sourceClause verbatim
  readonly why: string; // "<result> · <reasonCode>"
  readonly after: string; // predecessor operation or "first in chain"
  readonly humanAuthorityRequired: readonly { readonly deltaId: string; readonly words: string }[];
  readonly placedAt: readonly string[]; // area words
  readonly partial: boolean;
}

export interface PanelDeltaRow {
  readonly deltaId: string;
  readonly line: string;
  readonly sourceClause: string;
  readonly span: readonly [number, number];
  readonly target: string;
  readonly currentState: string | null;
  readonly flags: readonly string[];
  readonly categories: readonly PresentationCategory[];
  readonly placedAt: readonly string[];
  readonly retained: boolean;
  readonly sessionProofCeiling: ProofCeilingPresentation;
}

export interface PanelModel {
  readonly label: string;
  readonly observation: ObservationPresentation["aggregates"]["observation"];
  readonly capability: readonly { readonly axis: string; readonly words: string }[];
  readonly basis: { readonly digest: string; readonly derivationTime: string } | null;
  readonly semantic: {
    readonly ruleSetVersion: string;
    readonly clauses: readonly string[];
    readonly relationsTouched: readonly string[];
    readonly unknownRelations: readonly string[];
    readonly declaredPurpose: string | null;
    readonly semanticPurpose: string | null;
    readonly purposeAlignment: string;
    readonly semanticDrift: boolean;
  } | null;
  readonly deltas: readonly PanelDeltaRow[];
  readonly boundary: BoundaryCard | null;
  readonly nextValidTransition: string | null;
  readonly chainPartial: boolean | null;
  readonly provider: { readonly notExecutable: boolean; readonly reasons: readonly string[]; readonly send: typeof SEND_NOT_MATERIALIZED } | null;
  readonly proofCeiling: ProofCeilingPresentation | null;
  readonly notMaterialized: ObservationPresentation["notMaterialized"];
  readonly superseded: boolean;
  /** §17 accessible sentences, in order. */
  readonly spoken: readonly string[];
}

export interface GovernanceRendering {
  readonly areas: readonly AreaRendering[];
  readonly byArea: Readonly<Partial<Record<CyanObjectArea, AreaRendering>>>;
  readonly boundary: BoundaryCard | null;
  readonly panel: PanelModel;
  readonly attached: AttachedPresentation;
}

const AREA_WORDS = new Map<CyanObjectArea, string>(CYAN_OBJECT_AREAS.map((t) => [t.area, t.words]));

function currentOf(presence: ObservationPresence): GovernanceObservationCurrent | null {
  return presence.kind === "observation" && presence.observation.kind === "current" ? presence.observation : null;
}

function boundaryCardOf(chain: ChainWire, placedAt: (deltaId: string) => readonly string[]): BoundaryCard | null {
  const fbr = chain.firstBrokenRelation;
  if (fbr === null) return null;
  return {
    whatStopped: `${operationWords(fbr.broken.operation)} · ${EXECUTION_WORDS[fbr.broken.executionClass]}`,
    requestedIn: fbr.broken.sourceClause,
    why: resultWords(fbr.broken),
    after: fbr.predecessor === null ? "first in chain" : operationWords(fbr.predecessor.operation),
    humanAuthorityRequired: chain.humanAuthorityRequired.map((h) => ({ deltaId: h.deltaId, words: h.reasonCode === null ? h.result : `${h.result} · ${h.reasonCode}` })),
    placedAt: placedAt(fbr.broken.deltaId),
    partial: chain.partial,
  };
}

/** The whole rendering for one object. Deterministic; the only inputs are the crossed facts and the CYAN-local maps. */
export function governanceRendering(presence: ObservationPresence, presentation: ObservationPresentation): GovernanceRendering {
  const attached = attachPresentation(presentation);
  const current = currentOf(presence);
  const superseded = presence.kind === "observation" && presence.supersededByObjectChange;
  const deltaById = new Map<string, DeltaWire>((current?.deltas ?? []).map((d) => [d.deltaId, d]));
  const harIds = new Set((current?.chain.humanAuthorityRequired ?? []).map((h) => h.deltaId));
  const brokenId = current?.chain.firstBrokenRelation?.broken.deltaId ?? null;
  const placedAtWords = (deltaId: string): readonly string[] =>
    (attached.deltas.find((d) => d.deltaId === deltaId)?.targets ?? []).map((t) => t.words);

  const placed: PlacedDelta[] = attached.deltas.flatMap((a) => {
    const delta = deltaById.get(a.deltaId);
    if (!delta) return [];
    const pres = presentation.deltas.find((p) => p.deltaId === a.deltaId);
    return [{ delta, categories: a.categories, retained: pres?.retained ?? false, isFirstBroken: delta.deltaId === brokenId, humanAuthorityRequired: harIds.has(delta.deltaId), line: deltaLine(delta) }];
  });

  const providerNotExecutable = presentation.aggregates.current?.providerNotExecutable ?? false;
  const areas: AreaRendering[] = CYAN_OBJECT_AREAS.flatMap((t) => {
    const here = attached.deltas.filter((a) => a.targets.some((x) => x.area === t.area)).map((a) => placed.find((p) => p.delta.deltaId === a.deltaId)).filter((p): p is PlacedDelta => p !== undefined);
    if (here.length === 0) return [];
    const n = here.length;
    return [{
      area: t.area,
      words: t.words,
      deltas: here,
      firstBrokenHere: here.some((p) => p.isFirstBroken),
      humanAuthorityHere: here.some((p) => p.humanAuthorityRequired),
      providerNotExecutable: t.area === "derived-chamber" && providerNotExecutable && here.some((p) => p.categories.includes("PROVIDER")),
      superseded,
      summary: `${n} crossed ${n === 1 ? "step" : "steps"} placed here`,
    }];
  });
  const byArea: Partial<Record<CyanObjectArea, AreaRendering>> = {};
  for (const a of areas) byArea[a.area] = a;

  const boundary = current ? boundaryCardOf(current.chain, placedAtWords) : null;
  const cap = presentation.aggregates.current?.capability ?? null;
  const panel: PanelModel = {
    label: presentation.words,
    observation: presentation.aggregates.observation,
    capability: cap
      ? [
          { axis: "Governance admissible", words: `${cap.governanceAdmissible ? "true" : "false"}${cap.governanceAdmissibleReasons.length ? ` · ${cap.governanceAdmissibleReasons.join(", ")}` : ""}` },
          { axis: "Provider executable", words: `${cap.providerExecutable ? "true" : "false"}${cap.providerExecutableReasons.length ? ` · ${cap.providerExecutableReasons.join(", ")}` : ""}` },
          { axis: "Can send", words: cap.canSend === null ? "absent (observation superseded)" : `${cap.canSend ? "true" : "false"} · ${SEND_NOT_MATERIALIZED}` },
        ]
      : [],
    basis: presentation.basis ? { digest: presentation.basis.rawIntentDigestSha256, derivationTime: presentation.basis.derivationTime } : null,
    semantic: current
      ? {
          ruleSetVersion: current.semanticObservation.ruleSetVersion,
          clauses: current.semanticObservation.clauses,
          relationsTouched: current.semanticObservation.relationsTouched,
          unknownRelations: current.semanticObservation.unknownRelations,
          declaredPurpose: current.semanticObservation.declaredPurpose,
          semanticPurpose: current.semanticObservation.semanticPurpose,
          purposeAlignment: current.semanticObservation.purposeAlignment ?? "not determinable",
          semanticDrift: current.semanticObservation.semanticDrift,
        }
      : null,
    deltas: (current?.deltas ?? []).map((d) => {
      const pres = presentation.deltas.find((p) => p.deltaId === d.deltaId);
      return {
        deltaId: d.deltaId,
        line: deltaLine(d),
        sourceClause: d.sourceClause,
        span: d.span,
        target: targetWords(d.target),
        currentState: d.currentState,
        flags: d.flags,
        categories: pres?.categories ?? [],
        placedAt: placedAtWords(d.deltaId),
        retained: pres?.retained ?? false,
        sessionProofCeiling: pres?.sessionProofCeiling ?? proofCeilingPresentation(d.sessionProofCeiling),
      };
    }),
    boundary,
    nextValidTransition: current?.chain.nextValidTransition ? deltaLine(current.chain.nextValidTransition) : null,
    chainPartial: current ? current.chain.partial : null,
    provider: current ? { notExecutable: providerNotExecutable, reasons: current.capability.providerExecutableReasons, send: SEND_NOT_MATERIALIZED } : null,
    proofCeiling: presentation.aggregates.current?.composedProofCeiling ?? null,
    notMaterialized: presentation.notMaterialized,
    superseded,
    spoken: spokenSentences(presentation, current, boundary, superseded),
  };
  return { areas, byArea, boundary, panel, attached };
}

/** v4 §17: crossed facts and their meaning, in sentences; no position words. */
function spokenSentences(presentation: ObservationPresentation, current: GovernanceObservationCurrent | null, boundary: BoundaryCard | null, superseded: boolean): readonly string[] {
  const out: string[] = [`Governance for this session: ${presentation.words}.`];
  if (!current) return out;
  if (superseded) out.push(`Observed at ${current.basis.derivationTime}; the Session changed afterwards.`);
  const cap = current.capability;
  out.push(`Governance admissible: ${cap.governanceAdmissible}.${cap.governanceAdmissibleReasons.length ? ` Reasons: ${cap.governanceAdmissibleReasons.join(", ")}.` : ""}`);
  out.push(`Provider executable: ${cap.providerExecutable}.${cap.providerExecutableReasons.length ? ` Reasons: ${cap.providerExecutableReasons.join(", ")}.` : ""}`);
  out.push(`Can send: ${cap.canSend}. Send relation not materialized.`);
  if (boundary) out.push(`First broken relation: ${boundary.whatStopped}, ${boundary.why}.`);
  if (current.chain.humanAuthorityRequired.length > 0) out.push(`Human authority required for ${current.chain.humanAuthorityRequired.length} requested ${current.chain.humanAuthorityRequired.length === 1 ? "step" : "steps"}.`);
  if (current.chain.partial) out.push("Chain partial.");
  const ceiling = presentation.aggregates.current?.composedProofCeiling;
  if (ceiling) out.push(`Session-level proof ceiling, partial: ${ceiling.words}.`);
  return out;
}

export function areaWords(area: CyanObjectArea): string {
  return AREA_WORDS.get(area) ?? area;
}
