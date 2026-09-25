/**
 * SF-02 Field topology derivation (22 §11, §13, §14, §15, §16, §29.2).
 *
 * Pure functions from authoritative projection + presentation constraints to
 * DERIVED PROJECTION STATE. Nothing here reads the viewport, the clock or a
 * random source, so the server and the client derive the same topology
 * (22 §35.7). Geometry (positions, radii) lives in `geometry.ts` (SF-03).
 */
import type { Capability } from "../api/inquiryClient";

/** Relation path states, exactly 22 §11.4. */
export const PATH_STATES = [
  "established",
  "current",
  "possible",
  "unavailable",
  "denied",
  "loading",
  "historical",
  "governance",
  "authority",
  "dependency",
] as const;
export type PathState = (typeof PATH_STATES)[number];

/** Node states, 22 §14.2 (subset used by the Field; each has a non-color carrier). */
export type NodeState =
  | "established"
  | "current"
  | "possible"
  | "unavailable"
  | "denied"
  | "loading"
  | "unknown"
  | "frozen"
  | "human"
  | "governance"
  /** A lawful later lifecycle state (projection status `upcoming`): not a destination, not a boundary. */
  | "future";

/** 22 §10.3 / §10.4: a possible relation exists only when the server projects the capability true. */
export function affordanceState(capability: Capability): "possible" | "unavailable" {
  return capability.available ? "possible" : "unavailable";
}

export type PhaseProjection = { readonly state: string; readonly status: "done" | "current" | "upcoming" };

/**
 * Lifecycle emphasis follows gravity (22 §16.2; doc 23 §13.5): passed phases, the current phase and the next lawful
 * phase carry full emphasis; later phases are low-gravity. Emphasis is presentation weight only — every phase keeps a
 * READABLE label (doc 23 falsifier 42: the lifecycle never becomes a field of unreadable dots).
 */
export type Emphasis = "full" | "low";

export function lifecycleEmphasis(phases: readonly PhaseProjection[]): Map<string, Emphasis> {
  const out = new Map<string, Emphasis>();
  const currentIndex = phases.findIndex((p) => p.status === "current");
  phases.forEach((p, i) => {
    const full = p.status === "done" || p.status === "current" || (currentIndex >= 0 && i === currentIndex + 1);
    out.set(p.state, full ? "full" : "low");
  });
  return out;
}
