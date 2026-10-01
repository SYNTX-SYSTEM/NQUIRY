/**
 * CYAN-PCPG-03: the typed presentation attachment relation — v4 §06.4 attachment categories → the CURRENT CYAN object
 * structure (Architecture 27 v4 §05.4, §06.4, §13.6, §21; commit b0a5101).
 *
 * This module consumes ONLY `presentationOf(observation)` (CYAN-PCPG-02). It never looks at the raw response, never
 * re-runs governance logic, and never infers authority, roles, SEND, provider eligibility, evidence, provenance or
 * SOURCE_RELATION. An attachment target is PRESENTATION METADATA: where a crossed fact may be shown in the organism.
 *
 * ATTACHMENT TARGET != GOVERNANCE TRUTH != AUTHORITY != CAPABILITY != SEMANTIC LOCUS.
 *
 * The targets are the organism's existing identities (chamber classes, core, rings, path, proof depth, boundary marks,
 * decision surface) — nothing is invented to satisfy the architecture. `DEEP_FIELD_INSPECTOR` has no structural home
 * today and is recorded as structurally absent, never guessed. UNPLACED resolves only to the v4-defined fallback
 * (`FIELD_PANEL` → the proof chamber). Multiplicity is preserved: one item may attach to several targets; targets are
 * normalized as a set (fixed registry order) without loss; no category is ranked and no winner is chosen.
 *
 * Nothing here renders. Rendering is CYAN-PCPG-04 (membrane) and CYAN-PCPG-05 (attachment rendering).
 */
import {
  PRESENTATION_ATTACHMENTS,
  PRESENTATION_ATTACHMENT_MAP,
  PRESENTATION_CATEGORIES,
  attachmentsOf,
  type ObservationPresentation,
  type PresentationAttachment,
  type PresentationCategory,
} from "./pcpgPresentation";

export type CyanObjectHost = "session-field" | "decision-surface";

/** The organism's existing areas (identities as they appear in the DOM today). Never a backend name. */
export const CYAN_OBJECT_AREAS = [
  { area: "core", host: "session-field", identity: '[data-testid="field-core"]', words: "the object core" },
  { area: "lifecycle-ring", host: "session-field", identity: '[data-testid="session-phases"]', words: "the lifecycle ring" },
  { area: "path-station", host: "session-field", identity: '[data-testid="relation-trace"]', words: "the current station on the path" },
  { area: "active-phase-chamber", host: "session-field", identity: '[data-testid="active-phase"]', words: "the active-phase chamber" },
  { area: "burst-panel", host: "session-field", identity: '[data-testid="burst-capture-panel"]', words: "the burst panel" },
  { area: "question-set", host: "session-field", identity: '[data-testid="frozen-set"], [data-testid="own-question"]', words: "the human question set" },
  { area: "authority-chamber", host: "session-field", identity: '.plane.chamber[data-semantic="authority"]', words: "the Session control chamber" },
  { area: "boundary-marks", host: "session-field", identity: "[data-boundary]", words: "the boundary marks" },
  { area: "proof-chamber", host: "session-field", identity: '.plane.chamber[data-semantic="proof"]', words: "the proof chamber" },
  { area: "derived-chamber", host: "session-field", identity: '[data-testid="analysis-chamber"]', words: "the derived field chamber" },
  { area: "decision-entry-chamber", host: "session-field", identity: '.plane.chamber[data-semantic="decision-entry"]', words: "the decision entry chamber" },
  { area: "decision-chamber", host: "decision-surface", identity: '[data-testid="session-view-ok"] .plane.chamber[data-semantic="decision-entry"]', words: "the decision chamber of the decision surface" },
] as const;
export type CyanObjectArea = (typeof CYAN_OBJECT_AREAS)[number]["area"];
export type CyanAttachmentTarget = (typeof CYAN_OBJECT_AREAS)[number];

/**
 * v4 attachment category → existing areas. `DEEP_FIELD_INSPECTOR` is structurally absent today (empty, not guessed).
 * `FIELD_PANEL` is the proof chamber: the organism's inspection depth (ProofDepth disclosures) — the v4 fallback home.
 */
export const CYAN_ATTACHMENT_TARGETS: Readonly<Record<PresentationAttachment, readonly CyanObjectArea[]>> = {
  OBJECT_MEMBRANE: ["core"],
  SESSION_STATE_AREA: ["lifecycle-ring", "path-station", "active-phase-chamber"],
  BURST_AREA: ["burst-panel"],
  QUESTION_AREA: ["question-set"],
  DECISION_AREA: ["decision-entry-chamber", "decision-chamber"],
  BOUNDARY_AREA: ["boundary-marks", "authority-chamber"],
  PROVIDER_RELATED_AREA: ["derived-chamber"],
  FIELD_PANEL: ["proof-chamber"],
  DEEP_FIELD_INSPECTOR: [],
};

export class MalformedAttachmentMap extends Error {
  constructor(detail: string) {
    super(`MALFORMED_ATTACHMENT_MAP: ${detail}`);
    this.name = "MalformedAttachmentMap";
  }
}

const AREA_BY_ID = new Map<string, CyanAttachmentTarget>(CYAN_OBJECT_AREAS.map((t) => [t.area, t]));

/** Fail closed on the relation itself: every category mapped, every attachment known, every area existing. */
export function validateAttachmentRelation(): void {
  for (const category of PRESENTATION_CATEGORIES) {
    const attachments = PRESENTATION_ATTACHMENT_MAP[category];
    if (!Array.isArray(attachments) || attachments.length === 0) throw new MalformedAttachmentMap(`category ${category} has no attachment`);
    for (const a of attachments) if (!(PRESENTATION_ATTACHMENTS as readonly string[]).includes(a)) throw new MalformedAttachmentMap(`category ${category} names unknown attachment ${String(a)}`);
  }
  for (const attachment of PRESENTATION_ATTACHMENTS) {
    const areas = CYAN_ATTACHMENT_TARGETS[attachment];
    if (!Array.isArray(areas)) throw new MalformedAttachmentMap(`attachment ${attachment} has no target list`);
    for (const area of areas) if (!AREA_BY_ID.has(area)) throw new MalformedAttachmentMap(`attachment ${attachment} names unknown area ${String(area)}`);
  }
}
validateAttachmentRelation();

/** Targets of one attachment category. An unknown attachment is a malformed relation: fail closed, never ignored. */
export function targetsOfAttachment(attachment: PresentationAttachment): readonly CyanAttachmentTarget[] {
  const areas = CYAN_ATTACHMENT_TARGETS[attachment];
  if (!Array.isArray(areas)) throw new MalformedAttachmentMap(`unknown attachment ${String(attachment)}`);
  return areas.map((area) => {
    const t = AREA_BY_ID.get(area);
    if (!t) throw new MalformedAttachmentMap(`attachment ${attachment} names unknown area ${area}`);
    return t;
  });
}

/** A category value that is not in the vocabulary is treated as UNPLACED — the safe fallback, never a semantic area. */
export function safeCategory(value: string): PresentationCategory {
  return (PRESENTATION_CATEGORIES as readonly string[]).includes(value) ? (value as PresentationCategory) : "UNPLACED";
}

/** Normalize a target list as a set in registry order: duplicates collapse, nothing else changes. */
function normalize(targets: readonly CyanAttachmentTarget[]): readonly CyanAttachmentTarget[] {
  const present = new Set(targets.map((t) => t.area));
  return CYAN_OBJECT_AREAS.filter((t) => present.has(t.area));
}

/** All targets of a category set: multiplicity preserved, no ranking, no winner; unknown categories → UNPLACED. */
export function targetsOfCategories(categories: readonly string[]): readonly CyanAttachmentTarget[] {
  const cats = categories.map(safeCategory);
  const attachments = attachmentsOf(cats);
  return normalize(attachments.flatMap((a) => targetsOfAttachment(a)));
}

export interface DeltaAttachment {
  readonly deltaId: string;
  readonly categories: readonly PresentationCategory[];
  readonly attachments: readonly PresentationAttachment[];
  readonly targets: readonly CyanAttachmentTarget[];
  /** Attachments the organism has no structural home for today (never guessed into another area). */
  readonly structurallyAbsent: readonly PresentationAttachment[];
}

export interface AttachedPresentation {
  /** The CYAN-PCPG-02 derivation, passed through by reference and unaltered. */
  readonly presentation: ObservationPresentation;
  readonly deltas: readonly DeltaAttachment[];
  /** The union of every delta's targets (a set in registry order). */
  readonly targets: readonly CyanAttachmentTarget[];
  readonly structurallyAbsent: readonly PresentationAttachment[];
}

/** The attachment relation for one object, from the presentation derivation only. */
export function attachPresentation(presentation: ObservationPresentation): AttachedPresentation {
  const deltas: DeltaAttachment[] = presentation.deltas.map((d) => {
    const attachments = attachmentsOf(d.categories.map(safeCategory));
    const structurallyAbsent = attachments.filter((a) => CYAN_ATTACHMENT_TARGETS[a].length === 0);
    return { deltaId: d.deltaId, categories: d.categories, attachments, targets: normalize(attachments.flatMap((a) => targetsOfAttachment(a))), structurallyAbsent };
  });
  const absent = new Set(deltas.flatMap((d) => d.structurallyAbsent));
  return {
    presentation,
    deltas,
    targets: normalize(deltas.flatMap((d) => d.targets)),
    structurallyAbsent: PRESENTATION_ATTACHMENTS.filter((a) => absent.has(a)),
  };
}
