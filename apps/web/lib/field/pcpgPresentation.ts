/**
 * CYAN-PCPG-02: CYAN-local presentation derivations over a parsed `PCPG-R12/1` observation (Architecture 27 v4
 * §06.1–§06.4, §07.4, §08.2, §11.4, §12.1, §14; commit b0a5101).
 *
 * PRIMARY LAW: CYAN may derive PRESENTATION, never GOVERNANCE. Every function here is a pure, deterministic function
 * of already-crossed RED facts (the parsed contract) plus, for "Superseded", one caller-supplied fact about the object
 * (did it change after `basis.derivationTime`). Nothing here reads the server, the session, a role or a timer; nothing
 * is ever sent back; no output changes a capability, a chain or an affordance.
 *
 * Vocabulary law: `PresentationCategory` is UI PLACEMENT METADATA, not a semantic locus, not governance, not authority,
 * not capability. `affectedSemanticLoci` does not exist (v4 §00). `SOURCE_RELATION` is future-only and is not
 * approximated. `canSend` is the R-10 projection and never a SEND gate: "Send not materialized" is keyed to the contract
 * identity, never to a capability value. The proof ceiling is the Session-level proof ceiling (partial I-12): `null`
 * stays unknown and is never promoted; it is never called evidence, provenance, confidence or trust.
 */
import { PCPG_CONTRACT, type DeltaWire, type GovernanceObservation, type GovernanceObservationCurrent, type SessionProofCeiling } from "../api/pcpgClient";

// ---------------------------------------------------------------------------------------------------------------------
// Input: what the presentation layer knows about the observation for the current object (v4 §14)
// ---------------------------------------------------------------------------------------------------------------------

export type ObservationPresence =
  /** No observation has been submitted for this object: no governance statement at all (not current, not allowed). */
  | { readonly kind: "none" }
  /** The response could not be parsed (unknown contract / kind / value): fail closed. */
  | { readonly kind: "malformed" }
  | {
      readonly kind: "observation";
      readonly observation: GovernanceObservation;
      /** CYAN-local fact supplied by the caller: the object changed after `basis.derivationTime`. Never derived here. */
      readonly supersededByObjectChange: boolean;
    };

// ---------------------------------------------------------------------------------------------------------------------
// §06.1 Membrane label (CYAN-local; replaces the removed backend displaySummary)
// ---------------------------------------------------------------------------------------------------------------------

export const MEMBRANE_LABELS = [
  "NO_OBSERVATION",
  "GOVERNANCE_UNAVAILABLE",
  "SUPERSEDED",
  "HUMAN_AUTHORITY_REQUIRED",
  "BOUNDARY_REACHED",
  "PARTIAL",
  "PROVIDER_NOT_EXECUTABLE",
  "OBSERVED",
] as const;
export type MembraneLabel = (typeof MEMBRANE_LABELS)[number];

/** The words of each label (v4 §03 Level 0, §07.1). "Observed" never means "allowed". */
export const MEMBRANE_WORDS: Readonly<Record<MembraneLabel, string>> = {
  NO_OBSERVATION: "No observation",
  GOVERNANCE_UNAVAILABLE: "Governance unavailable",
  SUPERSEDED: "Superseded",
  HUMAN_AUTHORITY_REQUIRED: "Human Authority required",
  BOUNDARY_REACHED: "Boundary reached",
  PARTIAL: "Partial",
  PROVIDER_NOT_EXECUTABLE: "Provider not executable",
  OBSERVED: "Observed",
};

/** The only legitimate sources of "Human Authority required" (v4 §06.1): an AUTHORITY_BOUNDARY FBR or a non-empty HAR. */
function humanAuthorityRequired(o: GovernanceObservationCurrent): boolean {
  const fbrIsAuthority = o.chain.firstBrokenRelation !== null && o.chain.firstBrokenRelation.broken.result === "AUTHORITY_BOUNDARY";
  return fbrIsAuthority || o.chain.humanAuthorityRequired.length > 0;
}

function providerNotExecutable(o: GovernanceObservationCurrent): boolean {
  return !o.capability.providerExecutable && o.deltas.some((d) => d.executionClass === "PROVIDER_COMPUTATION");
}

/** Exactly one label, in the precedence order of v4 §06.1, from crossed facts only. Not canonical truth. */
export function membraneLabel(presence: ObservationPresence): MembraneLabel {
  if (presence.kind === "none") return "NO_OBSERVATION";
  if (presence.kind === "malformed") return "GOVERNANCE_UNAVAILABLE";
  const o = presence.observation;
  if (o.kind === "unavailable") return "GOVERNANCE_UNAVAILABLE";
  if (presence.supersededByObjectChange) return "SUPERSEDED";
  if (humanAuthorityRequired(o)) return "HUMAN_AUTHORITY_REQUIRED";
  if (o.chain.firstBrokenRelation !== null) return "BOUNDARY_REACHED";
  if (o.chain.partial) return "PARTIAL";
  if (providerNotExecutable(o)) return "PROVIDER_NOT_EXECUTABLE";
  return "OBSERVED";
}

// ---------------------------------------------------------------------------------------------------------------------
// §06.2 Aggregates (CYAN-local; deterministic functions of crossed facts; never sent back)
// ---------------------------------------------------------------------------------------------------------------------

export type ObservationAggregate = "none" | "current" | "unavailable" | "superseded";
export type BoundaryAggregate = "PRESENT" | "NONE";
export type HumanAuthorityAggregate = "REQUIRED" | "NOT_REQUIRED";
export type ChainStateAggregate = "BLOCKED" | "PARTIAL" | "COMPLETE";

export const PROOF_CEILING_LABEL = "Session-level proof ceiling (partial I-12)" as const;

/** v4 §12.1: GOVERNED / FIXTURE_NON_PROOF / null = unknown. The words never say proof, proven, provenance or evidence. */
export interface ProofCeilingPresentation {
  readonly label: typeof PROOF_CEILING_LABEL;
  readonly value: SessionProofCeiling | null;
  readonly words: "governed" | "fixture / non-proof" | "unknown";
}

export function proofCeilingPresentation(value: SessionProofCeiling | null): ProofCeilingPresentation {
  const words = value === "GOVERNED" ? "governed" : value === "FIXTURE_NON_PROOF" ? "fixture / non-proof" : "unknown";
  return { label: PROOF_CEILING_LABEL, value: value ?? null, words };
}

/** Aggregates that exist only for a current observation; never synthesized for none / unavailable / malformed. */
export interface CurrentAggregates {
  readonly boundary: BoundaryAggregate;
  readonly humanAuthority: HumanAuthorityAggregate;
  readonly chainState: ChainStateAggregate;
  readonly fbrPresent: boolean;
  readonly partial: boolean;
  readonly providerDeltaPresent: boolean;
  /** "Provider not executable" is a presentation of `capability.providerExecutable = false` with a provider delta present. */
  readonly providerNotExecutable: boolean;
  readonly capability: {
    readonly governanceAdmissible: boolean;
    readonly governanceAdmissibleReasons: readonly string[];
    readonly providerExecutable: boolean;
    readonly providerExecutableReasons: readonly string[];
    /** The R-10 projection as crossed; `null` = treated as absent because the observation is superseded (v4 §21). Never a gate. */
    readonly canSend: boolean | null;
  };
  /** CYAN-local reading (v4 §08.2): delta ids that are members of `chain.maximumLegitimateTransition`. */
  readonly retainedDeltaIds: readonly string[];
  readonly composedProofCeiling: ProofCeilingPresentation;
}

export interface PresentationAggregates {
  readonly observation: ObservationAggregate;
  /** Present exactly when a current observation was parsed (also when superseded); absent otherwise. */
  readonly current?: CurrentAggregates;
}

export function presentationAggregates(presence: ObservationPresence): PresentationAggregates {
  if (presence.kind === "none") return { observation: "none" };
  if (presence.kind === "malformed") return { observation: "unavailable" };
  const o = presence.observation;
  if (o.kind === "unavailable") return { observation: "unavailable" };
  const superseded = presence.supersededByObjectChange;
  const fbrPresent = o.chain.firstBrokenRelation !== null;
  const retained = new Set(o.chain.maximumLegitimateTransition.map((d) => d.deltaId));
  return {
    observation: superseded ? "superseded" : "current",
    current: {
      boundary: fbrPresent ? "PRESENT" : "NONE",
      humanAuthority: o.chain.humanAuthorityRequired.length > 0 ? "REQUIRED" : "NOT_REQUIRED",
      chainState: fbrPresent ? "BLOCKED" : o.chain.partial ? "PARTIAL" : "COMPLETE",
      fbrPresent,
      partial: o.chain.partial,
      providerDeltaPresent: o.deltas.some((d) => d.executionClass === "PROVIDER_COMPUTATION"),
      providerNotExecutable: providerNotExecutable(o),
      capability: {
        governanceAdmissible: o.capability.governanceAdmissible,
        governanceAdmissibleReasons: o.capability.governanceAdmissibleReasons,
        providerExecutable: o.capability.providerExecutable,
        providerExecutableReasons: o.capability.providerExecutableReasons,
        canSend: superseded ? null : o.capability.canSend,
      },
      retainedDeltaIds: o.deltas.filter((d) => retained.has(d.deltaId)).map((d) => d.deltaId),
      composedProofCeiling: proofCeilingPresentation(o.composedProofCeiling),
    },
  };
}

// ---------------------------------------------------------------------------------------------------------------------
// §11.4 SEND: a statement keyed to the contract identity, never to a capability value
// ---------------------------------------------------------------------------------------------------------------------

export interface SendStatement {
  readonly text: "Send not materialized";
  readonly keyedTo: typeof PCPG_CONTRACT;
  readonly reason: "PCPG-R12/1 contains no SEND relation (R-13 not started)";
}

/** Defined for the contract identity only. It takes no capability, so `canSend` cannot reach it. */
export function sendStatement(contract: string): SendStatement | null {
  if (contract !== PCPG_CONTRACT) return null;
  return { text: "Send not materialized", keyedTo: PCPG_CONTRACT, reason: "PCPG-R12/1 contains no SEND relation (R-13 not started)" };
}

/** What a PCPG-R12/1 observation never carries (v4 §03 Level 2, §12): shown as "not materialized", never filled. */
export const NOT_MATERIALIZED = ["SEND relation (R-13)", "evidence", "provenance", "HAR holder classes", "SOURCE_RELATION"] as const;

// ---------------------------------------------------------------------------------------------------------------------
// §06.3 PresentationCategory (CYAN-local UI placement metadata) and §06.4 attachments
// ---------------------------------------------------------------------------------------------------------------------

export const PRESENTATION_CATEGORIES = ["SESSION_STATE", "BURST", "QUESTION", "DECISION", "AUTHORITY", "PROVIDER", "EXTERNAL_OR_DISCLOSURE", "UNPLACED"] as const;
export type PresentationCategory = (typeof PRESENTATION_CATEGORIES)[number];

export const PRESENTATION_ATTACHMENTS = [
  "OBJECT_MEMBRANE",
  "SESSION_STATE_AREA",
  "BURST_AREA",
  "QUESTION_AREA",
  "DECISION_AREA",
  "BOUNDARY_AREA",
  "PROVIDER_RELATED_AREA",
  "FIELD_PANEL",
  "DEEP_FIELD_INSPECTOR",
] as const;
export type PresentationAttachment = (typeof PRESENTATION_ATTACHMENTS)[number];

/**
 * CYAN's copy of the RED operation-index ids it knows how to place (v4 §06.3). Used for placement only. An id not in
 * this map is UNPLACED — never guessed into the closest-looking area.
 */
const OPERATION_PLACEMENT: Readonly<Record<string, readonly Exclude<PresentationCategory, "UNPLACED">[]>> = {
  BEGIN_SETUP: ["SESSION_STATE"],
  BEGIN_CHALLENGE_CAPTURE: ["SESSION_STATE"],
  BEGIN_ANALYSIS: ["SESSION_STATE"],
  BEGIN_REFLECTION: ["SESSION_STATE"],
  BEGIN_QUESTION_SELECTION: ["SESSION_STATE"],
  BEGIN_INVESTIGATION: ["SESSION_STATE"],
  PREPARE_BURST: ["BURST"],
  COMPLETE_BURST: ["BURST"],
  OPEN_QUESTION_GENERATION: ["BURST"],
  CAPTURE_QUESTION: ["QUESTION"],
  SELECT_PRIMARY_QUESTION: ["QUESTION"],
  SELECT_COMPELLING_QUESTION: ["QUESTION"],
  OPEN_DECISION_CONSIDERATION: ["DECISION"],
  RECORD_HUMAN_DECISION: ["DECISION"],
};

export const PRESENTATION_ATTACHMENT_MAP: Readonly<Record<PresentationCategory, readonly PresentationAttachment[]>> = {
  SESSION_STATE: ["SESSION_STATE_AREA"],
  BURST: ["BURST_AREA"],
  QUESTION: ["QUESTION_AREA"],
  DECISION: ["DECISION_AREA"],
  AUTHORITY: ["BOUNDARY_AREA", "DECISION_AREA"],
  PROVIDER: ["PROVIDER_RELATED_AREA"],
  EXTERNAL_OR_DISCLOSURE: ["BOUNDARY_AREA"],
  UNPLACED: ["FIELD_PANEL"],
};

/**
 * The categories of one crossed delta, from `operation`, `executionClass` and `result` only (v4 §06.3). A delta may
 * fall into several categories; placement repeats, it never selects. Empty → UNPLACED. The output is sorted in the
 * fixed vocabulary order so that it is a set: order carries no meaning.
 */
export function categoriesOf(delta: DeltaWire): readonly PresentationCategory[] {
  const cats = new Set<PresentationCategory>();
  if (delta.operation !== null) {
    for (const c of OPERATION_PLACEMENT[delta.operation] ?? []) cats.add(c);
    if (delta.operation.startsWith("GRANT_") || delta.operation.startsWith("REVOKE_")) cats.add("AUTHORITY");
  }
  if (delta.result === "AUTHORITY_BOUNDARY" || delta.result === "HUMAN_ACTION_AVAILABLE") cats.add("AUTHORITY");
  if (delta.executionClass === "PROVIDER_COMPUTATION") cats.add("PROVIDER");
  if (delta.executionClass === "EXTERNAL_EFFECT" || delta.executionClass === "DISCLOSURE") cats.add("EXTERNAL_OR_DISCLOSURE");
  if (cats.size === 0) cats.add("UNPLACED");
  return PRESENTATION_CATEGORIES.filter((c) => cats.has(c));
}

/** The attachments of a category set: the union in the fixed attachment order (a set; order carries no meaning). */
export function attachmentsOf(categories: readonly PresentationCategory[]): readonly PresentationAttachment[] {
  const set = new Set<PresentationAttachment>();
  for (const c of categories) for (const a of PRESENTATION_ATTACHMENT_MAP[c]) set.add(a);
  return PRESENTATION_ATTACHMENTS.filter((a) => set.has(a));
}

// ---------------------------------------------------------------------------------------------------------------------
// The whole derivation for one object (for the future membrane / panel / inspector consumers; no UI here)
// ---------------------------------------------------------------------------------------------------------------------

export interface DeltaPresentation {
  readonly deltaId: string;
  readonly categories: readonly PresentationCategory[];
  readonly attachments: readonly PresentationAttachment[];
  /** CYAN-local reading: the delta is a member of `chain.maximumLegitimateTransition` (v4 §08.2). */
  readonly retained: boolean;
  readonly sessionProofCeiling: ProofCeilingPresentation;
}

export interface ObservationPresentation {
  readonly label: MembraneLabel;
  readonly words: string;
  readonly aggregates: PresentationAggregates;
  /** Per crossed delta, in the producer's order. Empty when there is no current observation. */
  readonly deltas: readonly DeltaPresentation[];
  /** The union of every delta's attachments; the membrane, panel and inspector always show the whole observation. */
  readonly attachments: readonly PresentationAttachment[];
  /** Present exactly when a current observation was parsed: keyed to the contract identity, never to `canSend`. */
  readonly send: SendStatement | null;
  readonly notMaterialized: typeof NOT_MATERIALIZED;
  /** Crossed verbatim for the panel's basis row; `null` without a current observation. */
  readonly basis: { readonly rawIntentDigestSha256: string; readonly derivationTime: string } | null;
}

export function presentationOf(presence: ObservationPresence): ObservationPresentation {
  const label = membraneLabel(presence);
  const aggregates = presentationAggregates(presence);
  const current = presence.kind === "observation" && presence.observation.kind === "current" ? presence.observation : null;
  const retained = new Set(current?.chain.maximumLegitimateTransition.map((d) => d.deltaId) ?? []);
  const deltas: DeltaPresentation[] = (current?.deltas ?? []).map((d) => {
    const categories = categoriesOf(d);
    return { deltaId: d.deltaId, categories, attachments: attachmentsOf(categories), retained: retained.has(d.deltaId), sessionProofCeiling: proofCeilingPresentation(d.sessionProofCeiling) };
  });
  return {
    label,
    words: MEMBRANE_WORDS[label],
    aggregates,
    deltas,
    attachments: attachmentsOf(deltas.flatMap((d) => d.categories)),
    send: current ? sendStatement(current.contract) : null,
    notMaterialized: NOT_MATERIALIZED,
    basis: current ? { rawIntentDigestSha256: current.basis.rawIntentDigestSha256, derivationTime: current.basis.derivationTime } : null,
  };
}
