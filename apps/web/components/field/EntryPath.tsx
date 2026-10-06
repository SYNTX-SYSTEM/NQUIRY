/**
 * CYAN-ENTRY-01: the entry path of a person without an nquiry identity, inside the Access core, below the contacts.
 * Words only — no control, no link, no form: the entry itself is the existing provider contact above, and the local
 * entry is the operator's act. Rendered for every entry projection (the operator relation always exists); the
 * provider sentences only when the server listed a provider; the labels are the server's.
 */
import type { EntryPath as EntryPathValue } from "../../lib/field/entryPath";
import { providerWords } from "../../lib/field/entryPath";

export function EntryPath({ entry }: { readonly entry: EntryPathValue }) {
  const words = providerWords(entry.providers);
  return (
    <section className="access-entry" aria-labelledby="access-entry-title" data-testid="access-entry" data-providers={entry.providers.length}>
      <p className="eyebrow" id="access-entry-title">
        Without an nquiry identity
      </p>
      {entry.providers.length > 0 ? (
        <p className="muted" data-testid="entry-provider">
          Continue with {words}: a provider account this deployment admits becomes your own nquiry identity, named and
          addressed as the provider presents you. Whether this deployment admits a new identity is decided by the
          server when you continue; a refusal is shown here, and no identity is created.
        </p>
      ) : null}
      <p className="muted" data-testid="entry-operator">
        A local password account is created by the operator of this deployment. There is no registration form.
      </p>
      {entry.providers.length > 0 ? (
        <p className="muted" data-testid="entry-link">
          Already have an nquiry account with a password? Log in with it and add {words} under Access security.
          Continuing with a provider here does not attach it to an existing account.
        </p>
      ) : null}
    </section>
  );
}
