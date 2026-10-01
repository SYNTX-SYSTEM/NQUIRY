"use client";

/**
 * WU-AUTH-12 (24 §16.2, §21.10, §29): recovery completion. The mailed link
 * lands here with `?recovery=<id>&token=<token>`; the page removes both from
 * the URL and history at once, keeps them in memory only, and sends them with
 * the new password to `POST /auth/recovery/complete` when the visitor submits.
 * A completed recovery creates no session (24 §16.2): the visitor logs in.
 */
import { type FormEvent, useEffect, useRef, useState } from "react";
import { completeRecovery } from "../../../lib/api/authClient";

type Proof = { readonly recoveryId: string; readonly token: string };
type State =
  | { readonly kind: "loading" }
  | { readonly kind: "malformed" }
  | { readonly kind: "form" }
  | { readonly kind: "done" }
  | { readonly kind: "denied" }
  | { readonly kind: "password-invalid" }
  | { readonly kind: "unavailable" }
  | { readonly kind: "unreachable" };

export default function RecoveryResetPage() {
  const [proof, setProof] = useState<Proof | null>(null);
  const [state, setState] = useState<State>({ kind: "loading" });
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  // The URL is read once per page load. The material is kept in a ref so that
  // React's development double-mount of effects, which runs after the URL
  // was already cleaned, finds the same proof instead of an empty URL.
  const captured = useRef<Proof | null | undefined>(undefined);

  useEffect(() => {
    if (captured.current === undefined) {
      const params = new URLSearchParams(window.location.search);
      const recoveryId = params.get("recovery");
      const token = params.get("token");
      captured.current = recoveryId && token ? { recoveryId, token } : null;
      // The single-use material leaves the URL bar and the history entry
      // before anything else happens (24 §21.10, §21.17).
      window.history.replaceState(null, "", "/recover/reset");
    }
    const found = captured.current;
    Promise.resolve().then(() => {
      if (found === null) {
        setState({ kind: "malformed" });
        return;
      }
      setProof(found);
      setState({ kind: "form" });
    });
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!proof || submitting) {
      return;
    }
    if (password !== confirm) {
      setState({ kind: "password-invalid" });
      return;
    }
    setSubmitting(true);
    try {
      const result = await completeRecovery(proof.recoveryId, proof.token, password);
      if (result.kind === "ok") {
        setProof(null);
        setPassword("");
        setConfirm("");
        setState({ kind: "done" });
      } else if (result.kind === "rejected" && result.reasonCode === "PASSWORD_INVALID") {
        setState({ kind: "password-invalid" });
      } else if (result.kind === "rejected") {
        setState({ kind: "malformed" });
      } else if (result.kind === "unavailable") {
        setState({ kind: "unavailable" });
      } else {
        setState({ kind: "denied" });
      }
    } catch {
      setState({ kind: "unreachable" });
    } finally {
      setSubmitting(false);
    }
  }

  const showForm = proof !== null && (state.kind === "form" || state.kind === "password-invalid" || state.kind === "unreachable");

  return (
    <main>
      <h1>Choose a new password</h1>
      {state.kind === "loading" ? <p data-testid="reset-loading">Reading the recovery link…</p> : null}
      {state.kind === "malformed" ? (
        <p role="alert" data-testid="reset-malformed">
          This recovery link is incomplete. Request a new one.
        </p>
      ) : null}
      {showForm ? (
        <form onSubmit={onSubmit} aria-label="Choose a new password">
          <div>
            <label htmlFor="reset-password">New password</label>
            <input
              id="reset-password"
              data-testid="reset-password"
              type="password"
              autoComplete="new-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>
          <div>
            <label htmlFor="reset-confirm">Repeat the new password</label>
            <input
              id="reset-confirm"
              data-testid="reset-confirm"
              type="password"
              autoComplete="new-password"
              required
              value={confirm}
              onChange={(event) => setConfirm(event.target.value)}
            />
          </div>
          <button type="submit" data-testid="reset-submit" disabled={submitting}>
            {submitting ? "Saving…" : "Set new password"}
          </button>
        </form>
      ) : null}
      {state.kind === "password-invalid" ? (
        <p role="alert" data-testid="reset-password-invalid">
          The two entries must match and the password must be between 12 and 1024 characters without leading
          or trailing spaces.
        </p>
      ) : null}
      {state.kind === "done" ? (
        <p role="status" data-testid="reset-done">
          Your password was changed and every existing login was ended. <a href="/login">Log in</a> with the
          new password.
        </p>
      ) : null}
      {state.kind === "denied" ? (
        <p role="alert" data-testid="reset-denied">
          This recovery link is not valid. It may have expired or been used already.{" "}
          <a href="/recover">Request a new one.</a>
        </p>
      ) : null}
      {state.kind === "unavailable" ? (
        <p role="alert" data-testid="reset-unavailable">
          Account recovery is not available in this environment.
        </p>
      ) : null}
      {state.kind === "unreachable" ? (
        <p role="alert" data-testid="reset-unreachable">
          Unable to reach the server. Nothing was changed as far as this page knows.
        </p>
      ) : null}
    </main>
  );
}
