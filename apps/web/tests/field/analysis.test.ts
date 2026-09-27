/**
 * WU-CY-01 (L1): the Session position projection across the ANALYSIS boundary, as pure projection helpers.
 *
 * Producer: RED `checkpoint-PFC-B5` (`7d3f74e4685b821cc948f45e413c1e0c207259d4`), `position.session.proofMode`,
 * `position.session.fixture`, `position.analysis` (`packages/application/analysis_projection.py`) and
 * `actions.BEGIN_ANALYSIS`. The helpers project ONLY what the producer sends: an absent key is "not projected",
 * never a default; no status is invented; the derived artifact's CONTENT is never part of the projection (no AI text
 * is rendered in WU-CY-01).
 */
import { describe, expect, it } from "vitest";
import { analysisFacts, proofModeOf, type AnalysisProjection } from "../../lib/field/analysis";
import { openSession, runSessionCommand } from "../../lib/api/inquiryClient";

const MOCK_MARKER = {
  origin: "AI",
  derived: true,
  kind: "PROPOSAL",
  provider: "mock",
  proof: "MOCK / NON_PROOF",
  isMock: true,
  note: "Produced by the development MockProvider. It is not an analysis of these Questions and is not proof of anything.",
};

function visibleAnalysis(status: string, reasonCode: string | null = null, withArtifact = status === "ACCEPTED"): AnalysisProjection {
  return {
    visible: true,
    audience: "FROZEN_SET_AUDIENCE",
    marker: MOCK_MARKER,
    analysis: {
      status,
      reasonCode,
      artifact: withArtifact
        ? {
            artifactId: "a-1",
            generationId: "g-1",
            proofClass: "MOCK_NON_PROOF",
            isMockNonProof: true,
            acceptedAt: "2026-09-27T10:00:00Z",
            acceptedByCommandId: "c-1",
            marker: MOCK_MARKER,
            content: { items: [{ question_id: "q-1", text: "SENTINEL_DERIVED_TEXT" }] },
          }
        : null,
    },
    clustering: { status: "NOT_RUN", reasonCode: "NO_ACCEPTED_ANALYSIS", runId: null, marker: null, clusters: [] },
    generations: [{ generationId: "g-1", operation: "AIOP-001", status: "ACCEPTED", provider: "mock", model: "mock", failureCode: null, retryOf: null, authorization: null, requestedAt: "2026-09-27T09:59:00Z", completedAt: "2026-09-27T10:00:00Z" }],
  };
}

describe("proofModeOf: the producer's proof mode, never a default", () => {
  it("F03-shaped session (no proofMode): not projected", () => {
    const m = proofModeOf({ sessionId: "s", state: "DRAFT", version: 1, method: "m", createdAt: "t" });
    expect(m.projected).toBe(false);
    expect(m.words).toMatch(/not projected/);
  });
  it("FIXTURE_NON_PROOF is NON_PROOF in words", () => {
    const m = proofModeOf({ sessionId: "s", state: "DRAFT", version: 1, method: "m", createdAt: "t", fixture: true, proofMode: "FIXTURE_NON_PROOF" });
    expect(m).toMatchObject({ projected: true, mode: "FIXTURE_NON_PROOF", nonProof: true });
    expect(m.words).toContain("NON_PROOF");
  });
  it("GOVERNED is not NON_PROOF and stays the producer's word", () => {
    const m = proofModeOf({ sessionId: "s", state: "DRAFT", version: 1, method: "m", createdAt: "t", fixture: false, proofMode: "GOVERNED" });
    expect(m).toMatchObject({ projected: true, mode: "GOVERNED", nonProof: false });
  });
  it("an unknown mode is passed through verbatim and is never called proof", () => {
    const m = proofModeOf({ sessionId: "s", state: "DRAFT", version: 1, method: "m", createdAt: "t", proofMode: "SOMETHING_NEW" });
    expect(m).toMatchObject({ projected: true, mode: "SOMETHING_NEW", nonProof: false });
    expect(m.words).not.toMatch(/\bproof\b(?!.*NON_PROOF)/i);
  });
});

describe("analysisFacts: the derived field as the producer projects it", () => {
  it("absent (F03 producer) and invisible (outside the frozen-set audience) are both null: nothing is shown", () => {
    expect(analysisFacts(undefined)).toBeNull();
    expect(analysisFacts({ visible: false })).toBeNull();
  });
  it("ACCEPTED with a mock artifact: accepted, MOCK / NON_PROOF, provider named, tone stable, generations counted", () => {
    const f = analysisFacts(visibleAnalysis("ACCEPTED"));
    expect(f).toMatchObject({ status: "ACCEPTED", words: "accepted", tone: "stable", proof: "MOCK / NON_PROOF", isMock: true, provider: "mock", artifactAcceptedAt: "2026-09-27T10:00:00Z", clusteringStatus: "NOT_RUN", generations: 1 });
  });
  it("UNAVAILABLE carries the producer's reason code and is a boundary tone, not an error", () => {
    const f = analysisFacts(visibleAnalysis("UNAVAILABLE", "PROVIDER_TIMEOUT", false));
    expect(f).toMatchObject({ status: "UNAVAILABLE", words: "unavailable", reasonCode: "PROVIDER_TIMEOUT", tone: "boundary", artifactAcceptedAt: null });
  });
  it("NOT_BEGUN / NOT_RUN are neutral; PENDING / RUNNING are living", () => {
    expect(analysisFacts(visibleAnalysis("NOT_BEGUN", null, false))?.tone).toBe("neutral");
    expect(analysisFacts(visibleAnalysis("NOT_RUN", null, false))?.tone).toBe("neutral");
    expect(analysisFacts(visibleAnalysis("PENDING", "AUTHORIZATION_NOT_EXECUTED", false))?.tone).toBe("living");
    expect(analysisFacts(visibleAnalysis("RUNNING", null, false))?.tone).toBe("living");
  });
  it("an unknown status is passed through verbatim (no invented vocabulary)", () => {
    expect(analysisFacts(visibleAnalysis("SOMETHING_NEW", null, false))).toMatchObject({ status: "SOMETHING_NEW", words: "SOMETHING_NEW", tone: "neutral" });
  });
  it("MUST REMAIN IMPOSSIBLE: the artifact content never enters the projection", () => {
    const f = analysisFacts(visibleAnalysis("ACCEPTED"));
    expect(f).not.toHaveProperty("content");
    expect(JSON.stringify(f)).not.toContain("SENTINEL_DERIVED_TEXT");
  });
});

describe("client: the pinned producer's routes and body contract", () => {
  function capture() {
    const calls: { url: string; body: unknown }[] = [];
    const fetchImpl = (async (url: string | URL | Request, init?: RequestInit) => {
      calls.push({ url: String(url), body: init?.body ? JSON.parse(String(init.body)) : undefined });
      return new Response(JSON.stringify({ kind: "committed", replayed: false }), { headers: { "content-type": "application/json" } });
    }) as unknown as typeof fetch;
    return { calls, fetchImpl };
  }
  it("BEGIN_ANALYSIS posts to transitions/begin-analysis with the version the viewer saw and the intent key", async () => {
    const { calls, fetchImpl } = capture();
    await runSessionCommand("w", "s", "BEGIN_ANALYSIS", 7, "k", {}, fetchImpl);
    expect(calls[0]?.url).toMatch(/\/workspaces\/w\/sessions\/s\/transitions\/begin-analysis$/);
    expect(calls[0]?.body).toEqual({ expectedVersion: 7 });
  });
  it("openSession sends `fixture: true` only when the human chose a Fixture Session; otherwise the F03 body `{}`", async () => {
    const { calls, fetchImpl } = capture();
    await openSession("w", "c", "k", {}, fetchImpl);
    await openSession("w", "c", "k", { fixture: true }, fetchImpl);
    await openSession("w", "c", "k", { fixture: false }, fetchImpl);
    expect(calls.map((c) => c.body)).toEqual([{}, { fixture: true }, {}]);
  });
});
