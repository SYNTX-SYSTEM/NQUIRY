"use client";

/**
 * E-mail verification, completion (AUTH/CYAN-RECOVERY-01; 24 §16): the challenge arrives in the mail link
 * (`?challengeId=<id>&token=<token>`), is captured once and removed from the address bar (`useMailLink`), and is
 * sent once while the identity is logged in (the relation is the identity's; without a session the page says to
 * log in and open the link again — the challenge stays valid until it expires). The server's verdict is the only
 * verdict.
 */
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { FieldBackground } from "../../../components/field/FieldBackground";
import { Identity } from "../../../components/field/Identity";
import { completeVerification } from "../../../lib/api/authClient";
import { useMailLink } from "../../../lib/field/mailLink";

type State =
  | { readonly kind: "pending" }
  | { readonly kind: "verified"; readonly email: string }
  | { readonly kind: "no_session" }
  | { readonly kind: "error"; readonly outcome: "denied" | "rejected" | "unavailable" | "network_failure"; readonly message: string };

const MESSAGES = {
  denied: "This verification link is not valid any more: it was already used, it expired, or it belongs to another identity. Send a new one from Access security.",
  rejected: "The link is malformed. Open it exactly as it was sent.",
  unavailable: "E-mail verification is not available right now. Nothing changed.",
  network_failure: "The canonical system could not be reached. Nothing changed.",
} as const;

export default function VerifyEmailPage() {
  const link = useMailLink();
  const challengeId = link.captured ? link.params.get("challengeId") : null;
  const token = link.captured ? link.params.get("token") : null;
  const incomplete = link.captured && (!challengeId || !token);
  const sent = useRef(false);
  const [state, setState] = useState<State>({ kind: "pending" });

  useEffect(() => {
    if (sent.current || !challengeId || !token) return;
    sent.current = true;
    completeVerification(challengeId, token)
      .then((result) => {
        if (result.kind === "ok") setState({ kind: "verified", email: result.email });
        else if (result.kind === "denied" && result.reasonCode === "NO_SESSION") setState({ kind: "no_session" });
        else setState({ kind: "error", outcome: result.kind, message: MESSAGES[result.kind] });
      })
      .catch(() => setState({ kind: "error", outcome: "network_failure", message: MESSAGES.network_failure }));
  }, [challengeId, token]);

  const pending = !incomplete && state.kind === "pending";
  return (
    <>
      <FieldBackground regime="access" />
      <header className="access-rail">
        <Identity link={false} />
      </header>
      <main className="access-field" data-field-regime="access">
        <section className="access-core" aria-labelledby="verify-title" data-testid="access-core" data-core-state={pending ? "loading" : state.kind === "verified" ? "current" : "boundary"}>
          <span className="access-membrane" aria-hidden="true" />
          <p className="eyebrow">Access · e-mail</p>
          <h1 id="verify-title">Verify your e-mail address</h1>
          {pending ? (
            <p role="status" className="access-status" data-testid="verify-pending">
              Checking the link…
            </p>
          ) : null}
          {state.kind === "verified" ? (
            <p role="status" className="access-status" data-testid="verify-done">
              <span className="mono" data-testid="verify-email">
                {state.email}
              </span>{" "}
              is now a verified address of your nquiry identity. It can recover your password.{" "}
              <Link href="/workspaces" data-testid="verify-continue">
                Continue
              </Link>
              .
            </p>
          ) : null}
          {state.kind === "no_session" ? (
            <p role="alert" className="read-boundary" data-testid="verify-no-session" data-outcome="denied">
              <span className="t-boundary">
                Verification happens while you are logged in. <Link href="/login">Log in</Link>, then open the link from the e-mail again.
              </span>
            </p>
          ) : null}
          {incomplete ? (
            <p role="alert" className="read-boundary" data-testid="verify-incomplete" data-outcome="rejected">
              <span className="t-boundary">This page needs the link from the verification message.</span>
            </p>
          ) : null}
          {state.kind === "error" ? (
            <p role="alert" className="read-boundary" data-testid="verify-error" data-outcome={state.outcome}>
              <span className="t-boundary">{state.message}</span>
            </p>
          ) : null}
        </section>
      </main>
    </>
  );
}
