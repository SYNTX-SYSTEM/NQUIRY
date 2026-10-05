"use client";

/**
 * Recovery Field, start (AUTH/CYAN-RECOVERY-01; 24 §17, §45.2; HD-AUTH-10): the human who lost the password of a
 * local account names the address; the server answers the one answer whatever the address (no account existence
 * is disclosed here). RECOVERY != LOGIN: nothing is authenticated on this page. Offered only when the deployment
 * serves recovery (`/auth/contacts`); otherwise the page says so and leads back to the login.
 */
import Link from "next/link";
import { type FormEvent, useState } from "react";
import { FieldBackground } from "../../components/field/FieldBackground";
import { Identity } from "../../components/field/Identity";
import { startRecovery } from "../../lib/api/authClient";
import { recoveryOffered, useAuthContacts } from "../../lib/field/useAuthContacts";

type State =
  | { readonly kind: "idle" }
  | { readonly kind: "submitting" }
  | { readonly kind: "sent" }
  | { readonly kind: "unavailable" }
  | { readonly kind: "network_failure" };

export default function RecoverPage() {
  const [email, setEmail] = useState("");
  const [state, setState] = useState<State>({ kind: "idle" });
  const contacts = useAuthContacts();
  const offered = recoveryOffered(contacts);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState({ kind: "submitting" });
    startRecovery(email)
      .then((result) => setState(result.kind === "ok" ? { kind: "sent" } : { kind: "unavailable" }))
      .catch(() => setState({ kind: "network_failure" }));
  }

  return (
    <>
      <FieldBackground regime="access" />
      <header className="access-rail">
        <Identity link={false} />
      </header>
      <main className="access-field" data-field-regime="access">
        <section className="access-core" aria-labelledby="recover-title" data-testid="access-core" data-core-state={state.kind === "submitting" ? "loading" : state.kind === "unavailable" || state.kind === "network_failure" ? "boundary" : "current"}>
          <span className="access-membrane" aria-hidden="true" />
          <p className="eyebrow">Access · recovery</p>
          <h1 id="recover-title">Reset your password</h1>
          <p className="lede">Name the e-mail address of your nquiry account. If it is a verified address of an account with a password, a reset link is on its way.</p>
          {contacts.kind === "contacts" && !offered ? (
            <p role="alert" className="read-boundary" data-testid="recover-unavailable" data-outcome="unavailable">
              <span className="t-boundary">Password recovery is not offered by this deployment. Ask the operator who created your account.</span>
            </p>
          ) : null}
          {state.kind === "sent" ? (
            <p role="status" className="access-status" data-testid="recover-sent">
              If this address can recover an account, a message with a reset link has been sent. It works once and expires soon. Nothing else changed.
            </p>
          ) : (
            <form onSubmit={submit} data-testid="recover-form">
              <div className="field">
                <label htmlFor="recover-email">Email</label>
                <input id="recover-email" data-testid="recover-email" type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} />
              </div>
              <div className="actions-row">
                <button className="button access-action" type="submit" data-testid="recover-submit" disabled={state.kind === "submitting" || !offered}>
                  Send reset link
                </button>
              </div>
            </form>
          )}
          {state.kind === "unavailable" ? (
            <p role="alert" className="read-boundary" data-testid="recover-error" data-outcome="unavailable">
              <span className="t-boundary">Password recovery is not available right now. Nothing was sent.</span>
            </p>
          ) : null}
          {state.kind === "network_failure" ? (
            <p role="alert" className="read-boundary" data-testid="recover-error" data-outcome="network_failure">
              <span className="t-boundary">The canonical system could not be reached. Nothing was sent.</span>
            </p>
          ) : null}
          <p className="muted">
            <Link href="/login" data-testid="recover-back">
              Back to the login
            </Link>
          </p>
        </section>
      </main>
    </>
  );
}
