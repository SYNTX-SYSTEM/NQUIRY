/**
 * Rendered when `fetchSessionView` itself rejects (network failure,
 * non-JSON body, or a `parseSessionReadResult` fail-closed throw) --
 * a case `SessionReadResult` cannot represent, since the request never
 * resolved to a server-shaped verdict at all.
 *
 * RETROFIT: added after external review found `SessionViewContainer`
 * had no `.catch()` on its `fetchSessionView` call -- any fetch
 * failure left the component silently stuck on "Loading..." forever
 * (invisible to the viewer) and was the actual, previously
 * undiagnosed cause of this package's own non-deterministic
 * `unhandledRejection` E2E log lines (an aborted in-flight fetch from
 * a prior navigation, now caught instead of left unhandled). This
 * package's own RECOVERY_PATH claim ("Render denied/blocked/
 * indeterminate distinctly") was incomplete without this fourth,
 * non-server-shaped case.
 *
 * No retry control, consistent with this package's own zero-
 * interactive-action scope (12 §24 items 10-12/15 are PKG-29's own
 * scope).
 *
 * PKG-29 EXTENSION: `message` is now an optional prop (default
 * unchanged from the original PKG-28 text) so `DecisionSection` can
 * reuse this same component for a `recordHumanDecision` network
 * failure (a genuinely different situation -- "your decision
 * submission failed to reach the server", not "the page failed to
 * load") without duplicating this component's own no-retry-control
 * guarantee in a near-identical second file.
 */
export function NetworkErrorBanner({ message = "Unable to load this Session." }: { readonly message?: string }) {
  return (
    <div data-testid="network-error-banner" role="alert">
      {message}
    </div>
  );
}
