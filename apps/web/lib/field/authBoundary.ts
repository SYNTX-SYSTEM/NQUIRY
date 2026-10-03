/**
 * AUTH/CYAN-03: the provider-login result boundary of the Access Field, derived ONLY from the closed `?auth=`
 * vocabulary of AUTH/CYAN-01 (`readAuthProjection`). Pure: no React, no fetch, no inference from query text.
 *
 *   ?auth=<known word>   ──▶ { kind: "boundary", projection, message }   one legitimate sentence per word
 *   missing / unknown / repeated / malformed ──▶ { kind: "none" }        fail closed: nothing is rendered
 *
 * Every word is a NON-success of a provider login (http_oidc `_login_projection`): the boundary never synthesizes a
 * success and never speaks of authority (FAILED_LOGIN != DENIED_AUTHORITY, AUTHENTICATION != AUTHORIZATION).
 * UNKNOWN != FAILURE: an unknown word is not presented as "failed"; it is not presented at all.
 */
import { readAuthProjection, type AuthProjection } from "../api/authClient";

export type AuthBoundary =
  | { readonly kind: "none" }
  | { readonly kind: "boundary"; readonly projection: AuthProjection; readonly message: string };

export const NO_AUTH_BOUNDARY: AuthBoundary = { kind: "none" };

/** One sentence per known word (24 §24.6 classes). Each names a non-success and the absence of an access relation. */
export const AUTH_BOUNDARY_MESSAGES: Readonly<Record<AuthProjection, string>> = {
  cancelled: "The provider login was cancelled. No access relation was established.",
  provider_unavailable: "The identity provider is unavailable right now. No access relation was established.",
  provider_error: "The identity provider reported an error. No access relation was established.",
  failed: "The provider login could not be completed. No access relation was established.",
  unavailable: "Signing in with this provider is not available for this account. No access relation was established.",
};

/** The boundary for a location search string, or none. The only path to a boundary. */
export function authBoundaryFrom(search: string | URLSearchParams): AuthBoundary {
  const reading = readAuthProjection(search);
  if (reading.kind !== "projection") return NO_AUTH_BOUNDARY;
  return { kind: "boundary", projection: reading.projection, message: AUTH_BOUNDARY_MESSAGES[reading.projection] };
}
