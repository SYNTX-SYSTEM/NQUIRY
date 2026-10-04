/**
 * AUTH/CYAN-ACCOUNT-01: the account-link result of the Workspaces field, derived ONLY from the closed `?link=`
 * vocabulary of AUTH/CYAN-01 (`readLinkProjection`). Pure: no React, no fetch, no inference from query text.
 *
 *   ?link=<known word>   ──▶ { kind: "result", projection, message, settled }   one legitimate sentence per word
 *   missing / unknown / repeated / malformed ──▶ { kind: "none" }              fail closed: nothing is rendered
 *
 * `ok` is the ONE word that names a committed link (a linked method on the CURRENT identity — LINK != LOGIN,
 * LINK != ACCOUNT_CREATION); every other word names a non-effect. UNKNOWN != OK, UNKNOWN != FAILURE.
 */
import { readLinkProjection, type LinkProjection } from "../api/authClient";

export type LinkBoundary =
  | { readonly kind: "none" }
  | { readonly kind: "result"; readonly projection: LinkProjection; readonly message: string; readonly settled: "committed" | "none" };

export const NO_LINK_BOUNDARY: LinkBoundary = { kind: "none" };

/** One sentence per known word (`http_oidc._link_projection`; 24 §14.4–14.5 classes). */
export const LINK_BOUNDARY_MESSAGES: Readonly<Record<LinkProjection, string>> = {
  ok: "The provider account is now linked to your nquiry identity. Signing in through it reaches this identity.",
  already_linked: "This provider account was already linked to your nquiry identity. Nothing was changed.",
  collision: "This provider account is linked to a different nquiry identity. Nothing was changed.",
  cancelled: "The provider link was cancelled. Nothing was changed.",
  failed: "The provider link could not be completed. Nothing was changed.",
};

/** The link result for a location search string, or none. The only path to a result. */
export function linkBoundaryFrom(search: string | URLSearchParams): LinkBoundary {
  const reading = readLinkProjection(search);
  if (reading.kind !== "projection") return NO_LINK_BOUNDARY;
  return { kind: "result", projection: reading.projection, message: LINK_BOUNDARY_MESSAGES[reading.projection], settled: reading.projection === "ok" ? "committed" : "none" };
}
