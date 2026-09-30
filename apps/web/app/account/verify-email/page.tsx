"use client";

/**
 * WU-AUTH-11 (24 §16.1, §24.5, §29): the verification completion surface. The
 * mailed link lands here with `?challenge=<id>&token=<token>`; the page sends
 * both to `POST /auth/email/verification/complete` once and shows the server's
 * outcome. The token is used only for that request; it is not stored and not
 * echoed (24 §21.10, §24.6). Completion needs the identity's own session: an
 * unauthenticated visitor is sent to `/login` and can return afterwards.
 */
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "../../../components/f02/AppShell";
import { completeEmailVerification } from "../../../lib/api/authClient";

type State =
  | { readonly kind: "working" }
  | { readonly kind: "verified"; readonly email: string }
  | { readonly kind: "denied" }
  | { readonly kind: "malformed" }
  | { readonly kind: "unavailable" }
  | { readonly kind: "unreachable" };

export default function VerifyEmailPage() {
  const router = useRouter();
  const [state, setState] = useState<State>({ kind: "working" });
  // A completion is a single-use proof: this page sends it exactly once per
  // load, also under React's development double-mount of effects. The one
  // request is kept in a ref so a remount observes the same outcome.
  const request = useRef<{ key: string; promise: ReturnType<typeof completeEmailVerification> } | null>(null);

  useEffect(() => {
    let cancelled = false;
    const params = new URLSearchParams(window.location.search);
    const challenge = params.get("challenge");
    const token = params.get("token");
    if (!challenge || !token) {
      Promise.resolve().then(() => {
        if (!cancelled) {
          setState({ kind: "malformed" });
        }
      });
      return () => {
        cancelled = true;
      };
    }
    const key = `${challenge}\u0000${token}`;
    if (request.current === null || request.current.key !== key) {
      request.current = { key, promise: completeEmailVerification(challenge, token) };
    }
    request.current.promise
      .then((result) => {
        if (cancelled) {
          return;
        }
        // The single-use material has done its work: it leaves the URL bar
        // and the history entry (24 §21.10, §21.17).
        window.history.replaceState(null, "", "/account/verify-email");
        if (result.kind === "ok") {
          setState({ kind: "verified", email: result.email });
        } else if (result.kind === "denied" && result.reasonCode === "NO_SESSION") {
          router.replace("/login");
        } else if (result.kind === "rejected") {
          setState({ kind: "malformed" });
        } else if (result.kind === "unavailable") {
          setState({ kind: "unavailable" });
        } else {
          setState({ kind: "denied" });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setState({ kind: "unreachable" });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [router]);

  return (
    <AppShell crumbs={[{ label: "Account security", href: "/account/security" }, { label: "Verify email" }]}>
      <h1>Verify email</h1>
      {state.kind === "working" ? <p data-testid="verify-working">Checking the verification link…</p> : null}
      {state.kind === "verified" ? (
        <p role="status" data-testid="verify-ok">
          {state.email} is verified for your account.
        </p>
      ) : null}
      {state.kind === "denied" ? (
        <p role="alert" data-testid="verify-denied">
          This verification link is not valid. It may have expired, been used already, or belong to another
          account. Request a new one from Account security.
        </p>
      ) : null}
      {state.kind === "malformed" ? (
        <p role="alert" data-testid="verify-malformed">
          This verification link is incomplete.
        </p>
      ) : null}
      {state.kind === "unavailable" ? (
        <p role="alert" data-testid="verify-unavailable">
          Email verification is not available right now.
        </p>
      ) : null}
      {state.kind === "unreachable" ? (
        <p role="alert" data-testid="verify-unreachable">
          Unable to reach the server. Nothing was changed as far as this page knows.
        </p>
      ) : null}
    </AppShell>
  );
}
