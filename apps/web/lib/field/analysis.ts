/**
 * WU-CY-01 (HD-27): the Session position projection across the ANALYSIS boundary, as pure projection helpers.
 *
 * Producer: RED `checkpoint-PFC-B5` → `7d3f74e4685b821cc948f45e413c1e0c207259d4` (`packages/application/
 * inquiry_queries.py` `session_position`: `session.fixture`, `session.proofMode`; `analysis_projection.py`:
 * `position.analysis`). Ceiling of that producer: TECHNICALLY_CLOSED, CHECKPOINTED, not REVIEWED_FIELD, not
 * PUBLISHED_FIELD; MockProvider only, so every derived item is MOCK / NON_PROOF.
 *
 * Laws: only what the producer sends is projected — an absent key is "not projected", never a default; a status the
 * producer does not name is passed through verbatim; the derived artifact's CONTENT is not part of the projection
 * (no AI text is rendered in WU-CY-01); nothing here computes authority or state.
 */
import type { AnalysisProjection, SessionPosition } from "../api/inquiryClient";

export type { AnalysisProjection };
import type { VisualTone } from "./projection";

export type ProofModeProjection =
  | { readonly projected: true; readonly mode: string; readonly nonProof: boolean; readonly words: string }
  | { readonly projected: false; readonly words: string };

/** `position.session.proofMode` in the producer's own words. GOVERNED is not called "proof" either. */
export function proofModeOf(session: SessionPosition["session"]): ProofModeProjection {
  const mode = session.proofMode;
  if (typeof mode !== "string") return { projected: false, words: "not projected by this producer" };
  const nonProof = mode === "FIXTURE_NON_PROOF" || mode.endsWith("NON_PROOF");
  return { projected: true, mode, nonProof, words: nonProof ? `${mode} · a Fixture Session: nothing here is proof` : mode };
}

/** The producer's honest status vocabulary (analysis_projection.py), in words; unknown statuses stay verbatim. */
const STATUS_WORDS: Readonly<Record<string, string>> = {
  NOT_BEGUN: "not begun",
  PENDING: "authorized, not yet executed",
  RUNNING: "running",
  UNAVAILABLE: "unavailable",
  ACCEPTED: "accepted",
  NOT_RUN: "not run",
};
const STATUS_TONE: Readonly<Record<string, VisualTone>> = {
  NOT_BEGUN: "neutral",
  PENDING: "living",
  RUNNING: "living",
  UNAVAILABLE: "boundary",
  ACCEPTED: "stable",
  NOT_RUN: "neutral",
};

export type AnalysisFacts = {
  readonly status: string;
  readonly words: string;
  readonly tone: VisualTone;
  readonly reasonCode: string | null;
  /** The producer's proof marker of the derived field ("MOCK / NON_PROOF" for the MockProvider). */
  readonly proof: string | null;
  readonly provider: string | null;
  readonly note: string | null;
  readonly isMock: boolean;
  readonly artifactAcceptedAt: string | null;
  readonly clusteringStatus: string | null;
  readonly generations: number;
};

/** Null when the producer does not project the derived field (F03 producer) or hides it from this viewer. */
export function analysisFacts(analysis: AnalysisProjection | undefined): AnalysisFacts | null {
  if (!analysis || !analysis.visible) return null;
  const status = analysis.analysis.status;
  const marker = analysis.analysis.artifact?.marker ?? analysis.marker;
  return {
    status,
    words: STATUS_WORDS[status] ?? status,
    tone: STATUS_TONE[status] ?? "neutral",
    reasonCode: analysis.analysis.reasonCode ?? null,
    proof: analysis.analysis.artifact ? marker.proof : null,
    provider: marker.provider ?? null,
    note: marker.note ?? null,
    isMock: marker.isMock === true,
    artifactAcceptedAt: analysis.analysis.artifact?.acceptedAt ?? null,
    clusteringStatus: analysis.clustering?.status ?? null,
    generations: analysis.generations?.length ?? 0,
  };
}
