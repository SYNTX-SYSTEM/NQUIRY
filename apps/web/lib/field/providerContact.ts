/**
 * AUTH/CYAN-02 (generalized by AUTH/CYAN-ACCOUNT-01): the provider contacts of the Access Field, derived ONLY from
 * the parsed `/auth/providers` response (AUTH/CYAN-01 contract). Pure: no React, no fetch of its own, no inference.
 *
 *   ProviderListResult ──loginStartUrl per parsed provider──▶ { kind: "contacts", contacts: [{ provider, url }] }
 *   anything else / empty list ───────────────────────────▶ { kind: "none" }                     (fail closed)
 *
 * Every provider the server names is a contact, with the server's label and its proof class (24 §27: a non-production
 * class is shown, never hidden, never upgraded); no provider id is known here, so none is preferred or assumed
 * (PURPLE CONSUMER_CONTRACT.md §3: the provider list is the truth; production never lists a test issuer).
 * "anything else" is every unknown, malformed, denied, unavailable or failed discovery: `discoverProviderContact`
 * turns every throw of the typed client (MalformedAuthResponse, UnsafeNextTarget, network failure, non-JSON) into
 * `none`. PROVIDER_AVAILABLE != PROVIDER_LOGIN_PROVEN: a contact is a configured start URL, never a proven login.
 * LOGIN != LINK: only the LOGIN start builder exists here; no link, no account creation, no methods, no sessions.
 */
import { listProviders, loginStartUrl, type ProviderListResult, type ProviderSummary } from "../api/authClient";

export type ProviderLoginContact = { readonly provider: ProviderSummary; readonly url: string };
export type ProviderContact = { readonly kind: "none" } | { readonly kind: "contacts"; readonly contacts: readonly ProviderLoginContact[] };

export const NO_PROVIDER_CONTACT: ProviderContact = { kind: "none" };

/** The contacts for a PARSED provider list, or none. The only path to a contact; the builder refuses an unsafe `next`. */
export function providerContactFrom(list: ProviderListResult, next: string): ProviderContact {
  const contacts = list.providers.map((provider) => ({ provider, url: loginStartUrl(provider, next) }));
  return contacts.length === 0 ? NO_PROVIDER_CONTACT : { kind: "contacts", contacts };
}

/** Discovery through the typed client; every failure class is `none` (never a thrown or invented availability). */
export async function discoverProviderContact(next: string, fetchImpl: typeof fetch = fetch): Promise<ProviderContact> {
  try {
    return providerContactFrom(await listProviders(fetchImpl), next);
  } catch {
    return NO_PROVIDER_CONTACT;
  }
}
