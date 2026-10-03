/**
 * AUTH/CYAN-03: the provider-login result boundary inside the Access core. Renders nothing for `none`; for a known
 * projection one boundary line in the core's own boundary vocabulary (`read-boundary`, `role=alert`), carrying the
 * projection word as data. No control, no link, no success state, no authority vocabulary.
 */
import type { AuthBoundary as AuthBoundaryValue } from "../../lib/field/authBoundary";

export function AuthBoundary({ boundary }: { readonly boundary: AuthBoundaryValue }) {
  if (boundary.kind !== "boundary") return null;
  return (
    <p role="alert" id="auth-boundary" data-testid="auth-boundary" className="read-boundary access-auth-boundary" data-projection={boundary.projection}>
      <span className="t-boundary">{boundary.message}</span>
    </p>
  );
}
