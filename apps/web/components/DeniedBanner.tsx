/**
 * 12 §24's own "blocked/denied result surface" -- renders
 * `boundaries.types.BoundaryResult`'s own DENY/REQUIRE/ESCALATE
 * outcomes (06 §2) verbatim, with the server's own `reasonCode`. No
 * retry/override control -- a denied/require/escalate verdict is the
 * server's own resolved authority decision (this package's own
 * BOUNDARIES line: "Server responses only, no client authority
 * calculation"), never something this UI could locally bypass.
 */
export function DeniedBanner({
  result,
  reasonCode,
}: {
  readonly result: "DENY" | "REQUIRE" | "ESCALATE";
  readonly reasonCode: string;
}) {
  return (
    <div data-testid="denied-banner" role="alert">
      <span data-testid="denied-result">{result}</span>
      <span data-testid="denied-reason-code">{reasonCode}</span>
    </div>
  );
}
