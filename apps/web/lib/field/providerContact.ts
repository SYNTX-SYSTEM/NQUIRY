/**
 * AUTH/CYAN-02: the provider contact of the Access Field, derived ONLY from the parsed `/auth/providers` response
 * (AUTH/CYAN-01 contract). Pure: no React, no fetch of its own, no inference.
 *
 *   ProviderListResult ──googleLoginStart──▶ { kind: "contact", provider, url }   (parsed list names google)
 *   anything else      ────────────────────▶ { kind: "none" }                     (fail closed)
 *
 * "anything else" is every unknown, malformed, denied, unavailable or failed discovery: `discoverProviderContact`
 * turns every throw of the typed client (MalformedAuthResponse, UnsafeNextTarget, network failure, non-JSON) into
 * `none`. GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN: a contact is a configured start URL, never a proven login.
 * LOGIN != LINK: only the LOGIN start builder exists here; no link, no account creation, no methods, no sessions.
 */
import { googleLoginStart, listProviders, type ProviderListResult, type ProviderSummary } from "../api/authClient";

export type ProviderContact =
  | { readonly kind: "none" }
  | { readonly kind: "contact"; readonly provider: ProviderSummary; readonly url: string };

export const NO_PROVIDER_CONTACT: ProviderContact = { kind: "none" };

/** The contact for a PARSED provider list, or none. The only path to a contact. */
export function providerContactFrom(list: ProviderListResult, next: string): ProviderContact {
  const start = googleLoginStart(list, next);
  if (start.kind !== "available") return NO_PROVIDER_CONTACT;
  return { kind: "contact", provider: start.provider, url: start.url };
}

/** Discovery through the typed client; every failure class is `none` (never a thrown or invented availability). */
export async function discoverProviderContact(next: string, fetchImpl: typeof fetch = fetch): Promise<ProviderContact> {
  try {
    return providerContactFrom(await listProviders(fetchImpl), next);
  } catch {
    return NO_PROVIDER_CONTACT;
  }
}
