"use client";

/**
 * Composes the typed client (`lib/api/client.ts`) with the display
 * components into 12 §24's own full PKG-28 surface. A Client Component
 * (`"use client"`) issuing its `fetch` inside `useEffect` -- see
 * `lib/api/client.ts`'s own header docstring for why this must run in
 * the BROWSER, not during Next.js SSR: Playwright's `page.route()`
 * network interception (this package's own E2E proof mechanism,
 * `tests/e2e/session-view.spec.ts`) can only see requests the browser
 * itself issues.
 *
 * This component is a pure dispatcher over `SessionReadResult`'s own
 * three cases -- it never re-derives or overrides the server's own
 * verdict (this package's own BOUNDARIES line).
 *
 * RETROFIT: `LoadState` now has an explicit `"error"` case, and the
 * `fetchSessionView` call now has a `.catch()`. External review found
 * the original version had neither -- a rejected `fetchSessionView`
 * promise (network failure, aborted request, or a `parseSessionReadResult`
 * fail-closed throw) had no handler at all, so the component stayed on
 * `"loading"` forever, invisible to the viewer, while the browser
 * logged an unhandled promise rejection. See `NetworkErrorBanner`'s
 * own docstring for the full disclosure.
 *
 * PKG-29 EXTENSION: the `ok` branch now also renders `DecisionSection`
 * (12 §24 items 11/12/15) whenever the resolved `SessionView` carries
 * a `decision`/`aiRecommendation` -- itself still a pure pass-through
 * of whatever the server's own response contained, same as every
 * other field this component already renders.
 */
import { useEffect, useState } from "react";
import { fetchSessionView } from "../lib/api/client";
import type { SessionId, SessionReadResult, WorkspaceId } from "../lib/api/types";
import { BurstPanel } from "./BurstPanel";
import { ChallengeSummary } from "./ChallengeSummary";
import { DecisionSection } from "./DecisionSection";
import { DeniedBanner } from "./DeniedBanner";
import { IndeterminateBanner } from "./IndeterminateBanner";
import { NetworkErrorBanner } from "./NetworkErrorBanner";
import { SessionStateBadge } from "./SessionStateBadge";
import { WorkspaceBadge } from "./WorkspaceBadge";

type LoadState =
  | { readonly kind: "loading" }
  | { readonly kind: "error" }
  | { readonly kind: "loaded"; readonly result: SessionReadResult };

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

  if (state.kind === "loading") {
    return <p data-testid="session-view-loading">Loading...</p>;
  }
  if (state.kind === "error") {
    return <NetworkErrorBanner />;
  }

  const result = state.result;
  switch (result.kind) {
    case "ok":
      return (
        <div data-testid="session-view-ok">
          <WorkspaceBadge workspaceId={result.data.workspaceId} />
          <ChallengeSummary challenge={result.data.challenge} />
          <SessionStateBadge state={result.data.session.state} />
          {result.data.burst !== null ? <BurstPanel burst={result.data.burst} /> : null}
          <DecisionSection decision={result.data.decision} aiRecommendation={result.data.aiRecommendation} />
        </div>
      );
    case "denied":
      return <DeniedBanner result={result.result} reasonCode={result.reasonCode} />;
    case "indeterminate":
      return <IndeterminateBanner blockedTargetRef={result.blockedTargetRef} />;
  }
}
