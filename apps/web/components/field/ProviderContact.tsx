/**
 * AUTH/CYAN-02: the external-provider contact inside the Access Field core. Renders nothing for `none`; for a
 * contact, one plain navigation to the typed LOGIN start URL (the API answers with a redirect to the provider).
 * It is a part of the existing login field, not a second login surface: no panel, no route, no management.
 * The proof class is carried as data and named only when it is not the production class (24 §27: shown, never hidden).
 */
import type { ProviderContact as ProviderContactValue } from "../../lib/field/providerContact";

export function ProviderContact({ contact }: { readonly contact: ProviderContactValue }) {
  if (contact.kind !== "contact") return null;
  const { provider, url } = contact;
  return (
    <div className="access-provider" data-testid="provider-contact">
      <p className="access-provider-rule" aria-hidden="true">
        <span>or</span>
      </p>
      <a
        className="button secondary access-provider-action"
        href={url}
        data-testid={`provider-${provider.providerId}`}
        data-provider-id={provider.providerId}
        data-proof-class={provider.proofClass}
      >
        Continue with {provider.label}
        {provider.proofClass !== "PRODUCTION_PROVIDER" ? <span className="access-provider-class"> · test provider</span> : null}
      </a>
    </div>
  );
}
