"use client";

/**
 * Recovery Field, completion (AUTH/CYAN-RECOVERY-01; 24 §17.3, §19.6): the challenge arrives in the mail link
 * (`?recovery=<id>&token=<token>`), is captured ONCE from the location and removed from the address bar
 * (`useMailLink`), and is presented together with the new password. The server's verdict is the only verdict
 * (denied = unknown, expired, used or mismatched — one class). A completed reset creates NO session: the human
 * logs in with the new password.
 */
import Link from "next/link";
import { type FormEvent, useState } from "react";
import { FieldBackground } from "../../../components/field/FieldBackground";
import { Identity } from "../../../components/field/Identity";
import { completeRecovery } from "../../../lib/api/authClient";
import { useMailLink } from "../../../lib/field/mailLink";

type State =
  | { readonly kind: "idle" }
  | { readonly kind: "submitting" }
  | { readonly kind: "done" }
  | { readonly kind: "error"; readonly outcome: "denied" | "rejected" | "unavailable" | "network_failure"; readonly message: string };

const MESSAGES = {
  denied: "This reset link is not valid any more: it was already used, it expired, or it does not match. Request a new one.",
  rejected: "The new password was not accepted. Use at least the required length, without leading or trailing spaces.",
  unavailable: "Password recovery is not available right now. Nothing changed.",
  network_failure: "The canonical system could not be reached. Nothing changed.",
} as const;

export default function RecoverResetPage() {
  const link = useMailLink();
  const recoveryId = link.captured ? link.params.get("recovery") : null;
  const token = link.captured ? link.params.get("token") : null;
  const incomplete = link.captured && (!recoveryId || !token);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [state, setState] = useState<State>({ kind: "idle" });
  const mismatch = confirm.length > 0 && password !== confirm;

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!recoveryId || !token || password !== confirm) return;
    setState({ kind: "submitting" });
    completeRecovery(recoveryId, token, password)
      .then((result) => {
        if (result.kind === "ok") {
          setPassword("");
          setConfirm("");
          setState({ kind: "done" });
          return;
        }
        setState({ kind: "error", outcome: result.kind, message: MESSAGES[result.kind] });
      })
      .catch(() => setState({ kind: "error", outcome: "network_failure", message: MESSAGES.network_failure }));
  }

  return (
    <>
      <FieldBackground regime="access" />
      <header className="access-rail">
        <Identity link={false} />
      </header>
      <main className="access-field" data-field-regime="access">
        <section className="access-core" aria-labelledby="reset-title" data-testid="access-core" data-core-state={state.kind === "submitting" ? "loading" : state.kind === "error" || incomplete ? "boundary" : "current"}>
          <span className="access-membrane" aria-hidden="true" />
          <p className="eyebrow">Access · recovery</p>
          <h1 id="reset-title">Choose a new password</h1>
          {incomplete ? (
            <p role="alert" className="read-boundary" data-testid="reset-incomplete" data-outcome="rejected">
              <span className="t-boundary">This page needs the link from the reset message. Open the link from the e-mail, or request a new one.</span>
            </p>
          ) : null}
          {state.kind === "done" ? (
            <p role="status" className="access-status" data-testid="reset-done">
              Your password was replaced and every earlier session ended.{" "}
              <Link href="/login" data-testid="reset-login">
                Log in
              </Link>{" "}
              with the new password.
            </p>
          ) : (
            <form onSubmit={submit} data-testid="reset-form" autoComplete="off">
              <div className="field">
                <label htmlFor="reset-password">New password</label>
                <input id="reset-password" data-testid="reset-password" type="password" autoComplete="new-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>
              <div className="field">
                <label htmlFor="reset-confirm">New password again</label>
                <input id="reset-confirm" data-testid="reset-confirm" type="password" autoComplete="new-password" required aria-invalid={mismatch || undefined} value={confirm} onChange={(e) => setConfirm(e.target.value)} />
                {mismatch ? (
                  <span className="auth-note" role="alert" data-testid="reset-mismatch">
                    the two passwords differ · nothing was sent
                  </span>
                ) : null}
              </div>
              <div className="actions-row">
                <button className="button access-action" type="submit" data-testid="reset-submit" disabled={state.kind === "submitting" || mismatch || !recoveryId || !token || !password || !confirm}>
                  Set new password
                </button>
              </div>
            </form>
          )}
          {state.kind === "error" ? (
            <p role="alert" className="read-boundary" data-testid="reset-error" data-outcome={state.outcome}>
              <span className="t-boundary">{state.message}</span>
            </p>
          ) : null}
          <p className="muted">
            <Link href="/recover" data-testid="reset-again">
              Request a new link
            </Link>{" "}
            · <Link href="/login">Back to the login</Link>
          </p>
        </section>
      </main>
    </>
  );
}
