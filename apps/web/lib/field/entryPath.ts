/**
 * CYAN-ENTRY-01: the entry path of a person WITHOUT an nquiry identity, derived ONLY from authoritative producer
 * state. Pure: no React, no fetch, no inference.
 *
 *   ProviderContact (the parsed `/auth/providers` answer, AUTH/CYAN-02) ──▶ EntryPath
 *
 * Relations this projects (PURPLE CONSUMER_CONTRACT.md §1 GOOGLE_BOOTSTRAP, §4 "bootstrap is the provider path, not a
 * form"; Architecture 24 §11.14 first provider login / account creation boundary; identity_provisioning.py: a local
 * password account is created only by the host operator, no HTTP route reaches it):
 *   - PROVIDER ENTRY: an unbound provider subject that this deployment admits becomes its own identity (name and
 *     e-mail as the provider presents them). WHETHER a deployment admits it is the server's account-creation policy,
 *     decided at the callback and NOT discoverable through any contact — so the projection stays conditional and the
 *     refusal is the server's `?auth=unavailable` word (AUTH/CYAN-03). PRODUCER_RELATION_UNRESOLVED, preserved: a
 *     discovery contact for the policy (none exists); nothing here states that this deployment admits new identities.
 *   - OPERATOR ENTRY: a local password account is created by the operator of the deployment; there is no form.
 *   - LINK != LOGIN (24 §14.5, §32 "email collision → boundary requiring link/recovery flow"): a provider is attached
 *     to an existing account only from that account's live session (Access security); continuing with a provider on
 *     the login never links.
 * Laws: no provider is named here (labels come from the parsed list, AUTH/CYAN-02); no registration control exists;
 * IDENTITY != AUTHORITY (entry grants nothing); nothing claims success, policy, membership or role.
 */
import type { ProviderSummary } from "../api/authClient";
import type { ProviderContact } from "./providerContact";

export type EntryPath = {
  /** the providers the server listed — the only provider entry there is; empty = no provider entry */
  readonly providers: readonly ProviderSummary[];
  /** the host-operator relation (HD-28): always the one local entry, never a form */
  readonly operator: "HOST_OPERATOR";
};

/** The entry path for a parsed provider contact. The only path to an entry projection. */
export function entryPathFrom(contact: ProviderContact): EntryPath {
  return { providers: contact.kind === "contacts" ? contact.contacts.map((c) => c.provider) : [], operator: "HOST_OPERATOR" };
}

/** The provider labels as the server gave them, joined for one sentence ("A", "A or B", "A, B or C"). */
export function providerWords(providers: readonly ProviderSummary[]): string {
  const labels = providers.map((p) => p.label);
  if (labels.length <= 1) return labels[0] ?? "";
  return `${labels.slice(0, -1).join(", ")} or ${labels[labels.length - 1]}`;
}
