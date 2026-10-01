"use client";

/**
 * WU-AUTH-12 (24 §16.2, §14.4, §29): recovery request. Unauthenticated. The
 * server answers the same `ok` for every well-formed address whether or not
 * an identity can recover (24 §45.2), so this page reports "if an account can
 * be recovered with this address, a message was sent" and nothing more.
 */
import { type FormEvent, useState, useSyncExternalStore } from "react";
import { startRecovery } from "../../lib/api/authClient";

type State =
  | { readonly kind: "idle" }
  | { readonly kind: "sent"; readonly email: string }
  | { readonly kind: "unavailable" }
  | { readonly kind: "unreachable" };

export default function RecoverPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [state, setState] = useState<State>({ kind: "idle" });
  // Until React owns the form, typed text would be lost at hydration and a
  // submit would be the browser's own GET with the address in the URL; the
  // controls wait for hydration.
  const ready = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      const result = await startRecovery(email);
      setState(result.kind === "ok" ? { kind: "sent", email } : { kind: "unavailable" });
    } catch {
      setState({ kind: "unreachable" });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <h1>Recover access</h1>
      <p>
        Enter the verified email address of your account. If an account can be recovered with it, you will
        receive a message with a link to choose a new password.
      </p>
      <form onSubmit={onSubmit} aria-label="Recover access">
        <div>
          <label htmlFor="recover-email">Email</label>
          <input
            id="recover-email"
            data-testid="recover-email"
            type="email"
            autoComplete="username"
            required
            disabled={!ready}
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>
        <button type="submit" data-testid="recover-submit" disabled={!ready || submitting}>
          {submitting ? "Sending…" : "Send recovery email"}
        </button>
      </form>
      {state.kind === "sent" ? (
        <p role="status" data-testid="recover-sent">
          If an account can be recovered with {state.email}, a message was sent. Nothing has changed yet.
        </p>
      ) : null}
      {state.kind === "unavailable" ? (
        <p role="alert" data-testid="recover-unavailable">
          Account recovery is not available in this environment.
        </p>
      ) : null}
      {state.kind === "unreachable" ? (
        <p role="alert" data-testid="recover-unreachable">
          Unable to reach the server.
        </p>
      ) : null}
      <p>
        <a href="/login">Back to login</a>
      </p>
    </main>
  );
}
