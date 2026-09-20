/**
 * 12 §24 item 14: "INDETERMINATE surface that disables blind retry" --
 * BND-017's own "dependency blocking metadata" concept (14 §29,
 * PKG-24). `blockedTargetRef` is shown so a viewer can see WHAT is
 * blocking resolution, but structurally there is no retry/refresh
 * control anywhere in this component's own output -- proven by
 * `tests/components/IndeterminateBanner.test.tsx` (`canRetry` is not
 * even a prop this component accepts, so there is no code path that
 * could ever render one) and by the E2E "manipulate client capability
 * flag" attack (`tests/e2e/session-view.spec.ts`), which confirms no
 * capability-flag-shaped field exists anywhere in this package's own
 * response type or rendering logic.
 */
export function IndeterminateBanner({ blockedTargetRef }: { readonly blockedTargetRef: string }) {
  return (
    <div data-testid="indeterminate-banner" role="status">
      <span>INDETERMINATE</span>
      <span data-testid="indeterminate-blocked-target-ref">{blockedTargetRef}</span>
    </div>
  );
}
