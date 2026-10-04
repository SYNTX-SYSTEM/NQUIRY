/**
 * AUTH/CYAN-02 (generalized by AUTH/CYAN-ACCOUNT-01): the external-provider contacts inside the Access Field core.
 * Renders nothing for `none`; for contacts, one plain navigation per parsed provider to its typed LOGIN start URL
 * (the API answers with a redirect to the provider). It is a part of the existing login field, not a second login
 * surface: no panel, no route, no management. The proof class is carried as data and named only when it is not the
 * production class (24 §27: shown, never hidden).
 */
import type { ProviderContact as ProviderContactValue } from "../../lib/field/providerContact";

export function ProviderContact({ contact }: { readonly contact: ProviderContactValue }) {
  if (contact.kind !== "contacts") return null;
  return (
    <div className="access-provider" data-testid="provider-contact">
      <p className="access-provider-rule" aria-hidden="true">
        <span>or</span>
      </p>
      {contact.contacts.map(({ provider, url }) => (
        <a
          key={provider.providerId}
          className="button secondary access-provider-action"
          href={url}
          data-testid={`provider-${provider.providerId}`}
          data-provider-id={provider.providerId}
          data-proof-class={provider.proofClass}
        >
          Continue with {provider.label}
          {provider.proofClass !== "PRODUCTION_PROVIDER" ? <span className="access-provider-class"> · test provider</span> : null}
        </a>
      ))}
    </div>
  );
}
