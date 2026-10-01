/**
 * CYAN-PCPG-05: the actor's raw-intent observation as a CYAN-local state machine (Architecture 27 v4 §01, §04.1, §14,
 * §21, §22; commit b0a5101). Pure: a reducer over typed results of `submitPromptObservation` (CYAN-PCPG-01) plus one
 * derivation of the presentation presence for `presentationOf` (CYAN-PCPG-02).
 *
 * Laws: OBSERVE ≠ EXECUTE, OBSERVE ≠ SEND, RAW INTENT ≠ AUTHORITY. While a request is in flight the presence stays what
 * it was (no provisional governance result). A failed request never replaces a valid observation; a malformed
 * projection fails closed. Supersession is a presentation fact derived from the canonical Session versions remembered
 * at observation time versus the versions of the latest canonical re-read — never from a clock. Nothing is persisted:
 * React state only (I-18, HA-PCPG-3); a reload honestly returns to "No observation".
 */
import type { PromptObservation, PromptObservationResult } from "../api/pcpgClient";
import type { ObservationPresence } from "./pcpgPresentation";

/** The canonical versions of the object at observation time (from the position the page held). */
export type ObjectVersions = { readonly session: number; readonly burst: number | null };

export type ObservationFailure = Exclude<PromptObservationResult, { readonly kind: "ok" }>;

export interface ObservationState {
  /** The presence WITHOUT supersession (that is derived at read time against the latest versions). */
  readonly presence: ObservationPresence;
  /** The whole `ok` envelope of the latest valid observation (observedAt, digest), for the chamber's own facts. */
  readonly envelope: PromptObservation | null;
  readonly observedVersions: ObjectVersions | null;
  readonly phase: "idle" | "observing";
  /** The latest failure; cleared on the next request. A failure never replaces a valid observation. */
  readonly failure: ObservationFailure | null;
}

export const INITIAL_OBSERVATION: ObservationState = { presence: { kind: "none" }, envelope: null, observedVersions: null, phase: "idle", failure: null };

export type ObservationEvent =
  | { readonly type: "requested" }
  | { readonly type: "result"; readonly result: PromptObservationResult; readonly versions: ObjectVersions };

export function observationReducer(state: ObservationState, event: ObservationEvent): ObservationState {
  if (event.type === "requested") {
    // the presence is untouched: the membrane keeps "No observation" (or the previous observation) until a real result
    return { ...state, phase: "observing", failure: null };
  }
  const { result, versions } = event;
  if (result.kind === "ok") {
    return {
      presence: { kind: "observation", observation: result.data.governanceObservation, supersededByObjectChange: false },
      envelope: result.data,
      observedVersions: versions,
      phase: "idle",
      failure: null,
    };
  }
  if (result.kind === "malformed") {
    // fail closed: an unreadable projection cannot stand as a valid observation
    return { presence: { kind: "malformed" }, envelope: null, observedVersions: null, phase: "idle", failure: result };
  }
  // rejected / denied / not_found / indeterminate / network_failure / stale / blocked / failed_precommit:
  // nothing is assumed; the current valid observation (or "none") stays; the failure is shown
  return { ...state, phase: "idle", failure: result };
}

/** The presence the membrane consumes: supersession derived from versions only (no clock), never mutating the observation. */
export function presenceFor(state: ObservationState, current: ObjectVersions): ObservationPresence {
  if (state.presence.kind !== "observation") return state.presence;
  const superseded = state.observedVersions !== null && (state.observedVersions.session !== current.session || state.observedVersions.burst !== current.burst);
  return { kind: "observation", observation: state.presence.observation, supersededByObjectChange: superseded };
}

/** Runs one observation through the reducer: requested → result. The submit function is the PCPG-01 client. */
export async function runObservation(
  dispatch: (event: ObservationEvent) => void,
  submit: () => Promise<PromptObservationResult>,
  versions: ObjectVersions,
): Promise<PromptObservationResult> {
  dispatch({ type: "requested" });
  const result = await submit();
  dispatch({ type: "result", result, versions });
  return result;
}
