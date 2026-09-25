"use client";

/**
 * Composes the typed client (`lib/api/client.ts`) with the display components into 12 §24's own full PKG-28 surface —
 * the Decision Surface (PKG-29). A Client Component issuing its `fetch` inside `useEffect` (see `lib/api/client.ts`),
 * a pure dispatcher over `SessionReadResult`'s own cases: it never re-derives or overrides the server's verdict.
 *
 * SF-05 (doc 26 §31): the surface enters the field language — the same frame, background and organ grammar as the
 * Session Field — WITHOUT changing what it renders: every PKG-28/29 component, test id and text is kept; the
 * NON_PROOF status is written where the Session Field links here; no chart, gauge or metric is invented. In every
 * non-ok case (denied / indeterminate / rejected / network error) `main` still contains no action element.
 */
import { useEffect, useState } from "react";
import { fetchSessionView } from "../lib/api/client";
import type { SessionId, SessionReadResult, WorkspaceId } from "../lib/api/types";
import { LogoutButton } from "./LogoutButton";
import { BurstPanel } from "./BurstPanel";
import { ChallengeSummary } from "./ChallengeSummary";
import { DecisionSection } from "./DecisionSection";
import { DeniedBanner } from "./DeniedBanner";
import { ChamberHead } from "./field/chambers";
import { FieldFrame } from "./field/FieldFrame";
import { FieldCore } from "./field/topology/FieldCore";
import { FieldStage, Plane, Planes } from "./field/topology/FieldStage";
import { IndeterminateBanner } from "./IndeterminateBanner";
import { NetworkErrorBanner } from "./NetworkErrorBanner";
import { SessionStateBadge } from "./SessionStateBadge";
import { WorkspaceBadge } from "./WorkspaceBadge";
import type { TraceSegment } from "../lib/field/position";

type LoadState =
  | { readonly kind: "loading" }
  | { readonly kind: "error" }
  | { readonly kind: "loaded"; readonly result: SessionReadResult };

function decisionTrace(workspaceId: string, sessionId: string, loaded: { readonly challengeTitle: string; readonly state: string } | null): TraceSegment[] {
  const base: TraceSegment[] = [{ coordinate: "access", label: "Workspaces", status: "established", href: "/workspaces" }];
  if (!loaded) return base;
  return [
    ...base,
    { coordinate: "workspace", label: "Workspace", status: "established", href: `/workspaces/${encodeURIComponent(workspaceId)}` },
    { coordinate: "challenge", label: loaded.challengeTitle, status: "established" },
    { coordinate: "session", label: `Session · ${loaded.state}`, status: "established", href: `/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}` },
    { coordinate: "session-state", label: "Decision surface", status: "current" },
  ];
}

export function SessionViewContainer({
  workspaceId,
  sessionId,
}: {
  readonly workspaceId: WorkspaceId;
  readonly sessionId: SessionId;
}) {
  const [state, setState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    fetchSessionView(workspaceId, sessionId)
      .then((result) => {
        if (!cancelled) {
          setState({ kind: "loaded", result });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setState({ kind: "error" });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [workspaceId, sessionId]);

  const ok = state.kind === "loaded" && state.result.kind === "ok" ? state.result.data : null;
  const trace = decisionTrace(workspaceId, sessionId, ok ? { challengeTitle: ok.challenge.title, state: ok.session.state } : null);

  let body: React.ReactNode;
  if (state.kind === "loading") {
    body = <p data-testid="session-view-loading">Loading...</p>;
  } else if (state.kind === "error") {
    body = <NetworkErrorBanner />;
  } else {
    const result = state.result;
    switch (result.kind) {
      case "ok":
        body = (
          <div data-testid="session-view-ok" className="decision-surface">
            <Plane kind="context" semantic="context" labelledBy="decision-context-title">
              <ChamberHead id="decision-context-title" semantic="context" title="Context" marker="NON_PROOF" />
              <WorkspaceBadge workspaceId={result.data.workspaceId} />
              <ChallengeSummary challenge={result.data.challenge} />
              <SessionStateBadge state={result.data.session.state} />
            </Plane>
            {result.data.burst !== null ? (
              <Plane kind="proof" semantic={result.data.burst.state === "COMPLETED" ? "frozen" : "question"} labelledBy="decision-burst-title">
                <ChamberHead id="decision-burst-title" semantic={result.data.burst.state === "COMPLETED" ? "frozen" : "question"} title="Evidence: the Burst" marker={result.data.burst.mode} />
                <BurstPanel burst={result.data.burst} />
              </Plane>
            ) : null}
            <Plane kind="action" semantic="decision-entry" labelledBy="decision-chamber-title">
              <ChamberHead id="decision-chamber-title" semantic="decision-entry" title="Decision" marker="human authority" />
              <DecisionSection decision={result.data.decision} aiRecommendation={result.data.aiRecommendation} />
            </Plane>
          </div>
        );
        break;
      case "denied":
        body = <DeniedBanner result={result.result} reasonCode={result.reasonCode} />;
        break;
      case "indeterminate":
        body = <IndeterminateBanner blockedTargetRef={result.blockedTargetRef} />;
        break;
      case "rejected":
        // F02 WU-02.12 (FBR-C): the server rejected the request as malformed. A verdict, not a network failure, and
        // not an authority denial.
        body = (
          <div data-testid="session-view-rejected" role="alert">
            Rejected: this address does not name a valid Workspace or Session ({result.reasonCode}). No authority decision
            was made.
          </div>
        );
        break;
    }
  }

  return (
    <FieldFrame trace={trace} regime={ok ? "session" : state.kind === "loaded" ? "boundary" : "session"} exit={<LogoutButton />}>
      <FieldStage mode="stack" surface="decision">
        <div className="stack-column">
          <FieldCore
            kind="decision"
            state={ok ? "current" : state.kind === "loading" ? "loading" : "boundary"}
            eyebrow="Decision surface · PKG-29 prototype view"
            title={ok ? ok.challenge.title : state.kind === "loading" ? "Reading the Session…" : "This Session cannot be projected"}
            titleAs="p"
            stateText={ok ? ok.session.state : undefined}
            meta="NON_PROOF: records a human Decision under the server's own authority check; proves nothing beyond what the server returns."
          />
        </div>
        <Planes header={{ eyebrow: "Grown from", title: ok ? ok.challenge.title : "Decision surface", state: ok ? ok.session.state : state.kind === "loading" ? "reading…" : "boundary" }}>{body}</Planes>
      </FieldStage>
    </FieldFrame>
  );
}
