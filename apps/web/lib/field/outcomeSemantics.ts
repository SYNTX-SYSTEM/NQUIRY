/**
 * SF-01 Effect & Boundary grammar: consequence semantics of a settled outcome
 * (21 §14 boundary taxonomy, §17 effect lifecycle, §39 verdict language, C3-01).
 *
 * Input vocabulary is CLOSED to the published F02 envelope kinds
 * (`application.http_f02`) plus the client-side `network_failure` (no response
 * at all). No later-Field kind is anticipated here. An unknown kind throws, so a
 * caller can never render an unclassified outcome as if it were understood.
 *
 * The path matters only for NETWORK_FAILURE and INDETERMINATE: on a read, the
 * projection is unavailable (no effect exists to be uncertain about); on a
 * mutation, the canonical consequence is UNKNOWN. That is the "Network Failure
 * != Proof Of No Effect" law: a lost response never proves that nothing
 * happened.
 */

export const SETTLED_KINDS = [
  "committed",
  "denied",
  "rejected",
  "stale",
  "blocked",
  "failed_precommit",
  "indeterminate",
  "not_found",
  "network_failure",
] as const;

export type SettledKind = (typeof SETTLED_KINDS)[number];

export type EffectPath = "read" | "mutation";

/** `none`: provably no canonical change. `unknown`: commit certainty unavailable. */
export type Consequence = "committed" | "none" | "unknown";

export type OutcomeSemantics = {
  readonly kind: SettledKind;
  /** 21 §39 verdict language. */
  readonly title: string;
  /** Mutation path only; `null` on a read (a read has no effect consequence). */
  readonly consequence: Consequence | null;
  readonly consequenceText: string | null;
  /** `status` for a commit, `alert` for a boundary interrupting the relation. */
  readonly announce: "status" | "alert";
  /** Keep the same Idempotency-Key: a retry is the same logical Command. */
  readonly retainIntent: boolean;
  /** Re-read the canonical state before the intent may be repeated. */
  readonly reconcileFirst: boolean;
};

const TITLE: Readonly<Record<SettledKind, string>> = {
  committed: "Committed.",
  denied: "This action is not permitted in the current authority and scope.",
  rejected: "This request cannot be accepted in its current form.",
  stale: "The visible state has changed since this action became available.",
  blocked: "This relation cannot continue until the required prerequisite exists.",
  failed_precommit: "The requested change did not commit.",
  indeterminate: "The system cannot currently determine whether the requested change committed.",
  not_found: "The referenced context is not available in the confirmed scope.",
  network_failure: "The canonical system could not be reached.",
};

const CONSEQUENCE_TEXT: Readonly<Record<Consequence, string>> = {
  committed: "The change is canonical.",
  none: "No change was made.",
  unknown: "It is unknown whether the change was made. Check the re-read state before repeating it.",
};

function isSettledKind(kind: string): kind is SettledKind {
  return (SETTLED_KINDS as readonly string[]).includes(kind);
}

export function describeOutcome(kind: SettledKind, path: EffectPath): OutcomeSemantics {
  if (!isSettledKind(kind)) {
    throw new TypeError(`unclassified outcome kind ${JSON.stringify(kind)}`);
  }
  const unknown = kind === "indeterminate" || kind === "network_failure";
  const consequence: Consequence | null =
    path === "read" ? null : kind === "committed" ? "committed" : unknown ? "unknown" : "none";
  const onMutation = path === "mutation";
  return {
    kind,
    title: TITLE[kind],
    consequence,
    consequenceText: consequence === null ? null : CONSEQUENCE_TEXT[consequence],
    announce: kind === "committed" ? "status" : "alert",
    retainIntent: onMutation && unknown,
    reconcileFirst: onMutation && unknown,
  };
}
