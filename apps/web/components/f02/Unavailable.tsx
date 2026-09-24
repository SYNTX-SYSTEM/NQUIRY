/**
 * Renders a server capability that is NOT available: the server's own reason
 * text, never a client guess. No disabled button is rendered. An unavailable
 * action has no affordance at all, only its reason.
 */
import type { Capability } from "../../lib/api/inquiryClient";

export function Unavailable({ capability, testId }: { readonly capability: Capability; readonly testId: string }) {
  if (capability.available) {
    return null;
  }
  return (
    <p className="unavailable" data-testid={testId} data-reason-code={capability.reasonCode ?? undefined}>
      {capability.reason}
    </p>
  );
}
