"use client";

/**
 * WU-AUTH-04 (24 §15.7, §21.2, §24.5): the account security surface for
 * sessions. Lists the caller's own live sessions and lets them revoke one, or
 * all of them.
 *
 * Projection only (24 §24.3). Every fact shown comes from `GET /auth/sessions`;
 * after every revocation the list is read again from the server, never
 * patched locally. "Revoked" is shown only after the server said `ok`. When
 * the server reports that no session authenticates any more (the current
 * session was revoked, here or elsewhere), the page goes to `/login`.
 *
 * WU-AUTH-10 (24 §14.2, §24.5): the identity's authentication methods
 * (`GET /auth/methods`) and, for each configured provider not yet linked, a
 * "Link" action. Linking is a form POST the browser navigates to (the API
 * answers with the provider redirect). The link callback returns here with
 * `?link=<projection>`, shown as a safe message.
 *
 * WU-AUTH-11 (24 §16.1): the identity's verified addresses
 * (`GET /auth/emails`) and a "Send verification email" action for an address
 * (`POST /auth/email/verification/start`). Sending is not verifying: the page
 * says a challenge was sent; the address becomes verified only when the
 * mailed link is completed (`/account/verify-email`).
 */
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "../../../components/f02/AppShell";
import {
  linkProjectionMessage,
  linkStartUrl,
  listMethods,
  listProviders,
  listSessions,
  listVerifiedEmails,
  logoutAll,
  revokeSession,
  startEmailVerification,
  unlinkMethod,
  type MethodSummary,
  type ProviderSummary,
  type SessionListResult,
  type SessionSummary,
  type VerifiedEmailSummary,
} from "../../../lib/api/authClient";

type LoadState =
  | { readonly kind: "loading" }
  | { readonly kind: "ready"; readonly sessions: readonly SessionSummary[] }
  | { readonly kind: "unreachable" };

const METHOD_LABELS: Record<string, string> = {
  LOCAL_PASSWORD: "Email and password",
  GOOGLE_OIDC: "Google",
  TEST_PROVIDER: "Test provider",
};

function methodLabel(methodType: string | null): string {
  if (methodType === null) {
    return "Other proof";
  }
  return METHOD_LABELS[methodType] ?? methodType;
}

/** Providers the identity has no ACTIVE method for yet (a link action per provider). */
function unlinkedProviders(
  providers: readonly ProviderSummary[],
  methods: readonly MethodSummary[],
): readonly ProviderSummary[] {
  const linked = new Set(
    methods.filter((m) => m.status === "ACTIVE" && m.provider !== null).map((m) => m.provider!.providerId),
  );
  return providers.filter((provider) => !linked.has(provider.providerId));
}

/** 24 §14.6: the last ACTIVE method stays; the action is offered only when another remains. */
function activeMethodCount(methods: readonly MethodSummary[]): number {
  return methods.filter((m) => m.status === "ACTIVE").length;
}

function formatTime(value: string): string {
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export default function AccountSecurityPage() {
  const router = useRouter();
  const [state, setState] = useState<LoadState>({ kind: "loading" });
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [methods, setMethods] = useState<readonly MethodSummary[] | null>(null);
  const [providers, setProviders] = useState<readonly ProviderSummary[]>([]);
  const [linkMessage, setLinkMessage] = useState<string | null>(null);
  const [verifiedEmails, setVerifiedEmails] = useState<readonly VerifiedEmailSummary[] | null>(null);
  const [verifyAddress, setVerifyAddress] = useState("");
  const [verifyNotice, setVerifyNotice] = useState<string | null>(null);

  const apply = useCallback(
    (result: SessionListResult) => {
      if (result.kind === "denied") {
        router.replace("/login");
        return;
      }
      setState({ kind: "ready", sessions: result.sessions });
    },
    [router],
  );

  useEffect(() => {
    let cancelled = false;
    listSessions()
      .then((result) => {
        if (!cancelled) {
          apply(result);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setState({ kind: "unreachable" });
        }
      });
    Promise.resolve(new URLSearchParams(window.location.search).get("link")).then((code) => {
      if (!cancelled) {
        setLinkMessage(linkProjectionMessage(code));
      }
    });
    listMethods()
      .then((result) => {
        if (!cancelled && result.kind === "ok") {
          setMethods(result.methods);
        }
      })
      .catch(() => {
        // The method list stays unknown; nothing is assumed.
      });
    listProviders()
      .then((result) => {
        if (!cancelled) {
          setProviders(result.providers);
        }
      })
      .catch(() => {
        // No provider list means no link action (24 §24.2).
      });
    listVerifiedEmails()
      .then((result) => {
        if (!cancelled && result.kind === "ok") {
          setVerifiedEmails(result.emails);
        }
      })
      .catch(() => {
        // The verified-email list stays unknown; nothing is assumed.
      });
    return () => {
      cancelled = true;
    };
  }, [apply]);

  /** Re-reads the list from the server after an action; never patches it locally. */
  async function reload() {
    try {
      apply(await listSessions());
    } catch {
      setState({ kind: "unreachable" });
    }
  }

  async function handleRevoke(session: SessionSummary) {
    setBusy(true);
    setNotice(null);
    setError(null);
    try {
      const result = await revokeSession(session.sessionId);
      if (result.kind === "ok") {
        setNotice(session.current ? "This session was ended." : "The session was ended.");
      } else if (result.kind === "denied" && result.reasonCode === "NO_SESSION") {
        router.replace("/login");
        return;
      } else {
        setError("That session could not be ended. It may already have ended.");
      }
      await reload();
    } catch {
      setError("Unable to reach the server. Nothing was changed as far as this page knows.");
    } finally {
      setBusy(false);
    }
  }

  async function reloadMethods() {
    try {
      const result = await listMethods();
      setMethods(result.kind === "ok" ? result.methods : null);
    } catch {
      setMethods(null);
    }
  }

  async function handleUnlink(method: MethodSummary) {
    setBusy(true);
    setNotice(null);
    setError(null);
    try {
      const result = await unlinkMethod(method.methodId);
      if (result.kind === "ok") {
        if (result.currentSessionEnded) {
          // The method that signed this browser in is gone, and so is this
          // session (24 §18.2 dependent sessions). Sign in again.
          router.replace("/login");
          return;
        }
        setNotice(
          result.sessionsRevoked > 0
            ? `${methodLabel(method.methodType)} was removed and ${result.sessionsRevoked} session(s) signed in with it were ended.`
            : `${methodLabel(method.methodType)} was removed.`,
        );
      } else if (result.kind === "denied" && result.reasonCode === "NO_SESSION") {
        router.replace("/login");
        return;
      } else if (result.kind === "denied" && result.reasonCode === "LAST_METHOD") {
        setError("This is the only way to sign in to this account; it cannot be removed.");
      } else {
        setError("That sign-in method could not be removed. It may already have been removed.");
      }
      await Promise.all([reloadMethods(), reload()]);
    } catch {
      setError("Unable to reach the server. Nothing was changed as far as this page knows.");
    } finally {
      setBusy(false);
    }
  }

  async function handleVerify(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setVerifyNotice(null);
    setError(null);
    try {
      const result = await startEmailVerification(verifyAddress);
      if (result.kind === "ok") {
        setVerifyNotice("A verification email was sent. The address is verified once you open the link.");
      } else if (result.kind === "denied" && result.reasonCode === "NO_SESSION") {
        router.replace("/login");
        return;
      } else if (result.kind === "denied" && result.reasonCode === "VERIFICATION_RESEND_THROTTLED") {
        setError("A verification email was sent a moment ago. Please wait before requesting another.");
      } else if (result.kind === "rejected") {
        setError("Please enter a valid email address.");
      } else if (result.kind === "unavailable") {
        setError("Email verification is not available right now.");
      } else {
        setError("That address cannot be verified for this account.");
      }
    } catch {
      setError("Unable to reach the server. Nothing was changed as far as this page knows.");
    } finally {
      setBusy(false);
    }
  }

  async function handleLogoutAll() {
    setBusy(true);
    setNotice(null);
    setError(null);
    try {
      const result = await logoutAll();
      if (result.kind === "ok" || result.reasonCode === "NO_SESSION") {
        router.replace("/login");
        return;
      }
      setError("The sessions could not be ended.");
    } catch {
      setError("Unable to reach the server. Nothing was changed as far as this page knows.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell crumbs={[{ label: "Workspaces", href: "/workspaces" }, { label: "Account security" }]}>
      <h1>Account security</h1>
      {linkMessage ? (
        <p role="status" data-testid="link-projection">
          {linkMessage}
        </p>
      ) : null}
      <section className="panel" aria-labelledby="methods-heading">
        <h2 id="methods-heading">Ways to sign in</h2>
        {methods === null ? (
          <p data-testid="methods-unknown">The list of sign-in methods is not available.</p>
        ) : (
          <ul data-testid="method-list">
            {methods.map((method) => (
              <li key={method.methodId} data-testid="method-item">
                <strong>{methodLabel(method.methodType)}</strong>
                {method.provider?.email ? <span> ({method.provider.email})</span> : null}
                {method.status !== "ACTIVE" ? <span className="state"> {method.status}</span> : null}
                {method.status === "ACTIVE" ? (
                  <button
                    type="button"
                    className="button secondary"
                    data-testid={`unlink-${method.methodId}`}
                    disabled={busy || activeMethodCount(methods) <= 1}
                    title={
                      activeMethodCount(methods) <= 1
                        ? "The only way to sign in to this account cannot be removed."
                        : undefined
                    }
                    onClick={() => handleUnlink(method)}
                  >
                    Remove
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        )}
        {methods !== null && unlinkedProviders(providers, methods).length > 0 ? (
          <ul data-testid="link-actions">
            {unlinkedProviders(providers, methods).map((provider) => (
              <li key={provider.providerId}>
                <form method="post" action={linkStartUrl(provider.providerId, "/account/security")}>
                  <button type="submit" className="button secondary" data-testid={`link-${provider.providerId}`}>
                    Link {provider.label}
                    {provider.proofClass === "TEST_PROVIDER" ? " (TEST_PROVIDER, not production)" : ""}
                  </button>
                </form>
              </li>
            ))}
          </ul>
        ) : null}
      </section>
      <section className="panel" aria-labelledby="emails-heading">
        <h2 id="emails-heading">Verified email addresses</h2>
        {verifiedEmails === null ? (
          <p data-testid="emails-unknown">The list of verified addresses is not available.</p>
        ) : verifiedEmails.filter((e) => e.active).length === 0 ? (
          <p data-testid="emails-empty">No address is verified for this account yet.</p>
        ) : (
          <ul data-testid="verified-email-list">
            {verifiedEmails
              .filter((e) => e.active)
              .map((e) => (
                <li key={e.email} data-testid="verified-email">
                  {e.email}
                </li>
              ))}
          </ul>
        )}
        <form onSubmit={(event) => void handleVerify(event)} data-testid="verify-form">
          <label htmlFor="verify-address">Email address to verify</label>
          <input
            id="verify-address"
            type="email"
            required
            data-testid="verify-address"
            value={verifyAddress}
            onChange={(event) => setVerifyAddress(event.target.value)}
          />
          <button type="submit" className="button secondary" data-testid="verify-send" disabled={busy}>
            Send verification email
          </button>
        </form>
        {verifyNotice ? (
          <p role="status" data-testid="verify-notice">
            {verifyNotice}
          </p>
        ) : null}
      </section>
      <section className="panel" aria-labelledby="sessions-heading">
        <h2 id="sessions-heading">Active sessions</h2>
        <p>
          Each entry is one signed-in browser. Ending a session signs that browser out. It does not
          change what your account may do in any Workspace.
        </p>
        {state.kind === "loading" ? <p data-testid="sessions-loading">Loading sessions…</p> : null}
        {state.kind === "unreachable" ? (
          <p role="alert" data-testid="sessions-unreachable">
            Unable to reach the server. The session list is unknown.
          </p>
        ) : null}
        {state.kind === "ready" ? (
          <ul data-testid="session-list">
            {state.sessions.map((session) => (
              <li key={session.sessionId} data-testid="session-item">
                <p>
                  <strong>{methodLabel(session.methodType)}</strong>
                  {session.current ? (
                    <span className="state" data-testid="session-current">
                      {" "}
                      This browser
                    </span>
                  ) : null}
                </p>
                <p>
                  Signed in {formatTime(session.issuedAt)}. Ends {formatTime(session.expiresAt)}.
                </p>
                <button
                  type="button"
                  className="button secondary"
                  data-testid="session-revoke"
                  disabled={busy}
                  onClick={() => void handleRevoke(session)}
                >
                  {session.current ? "End this session" : "End session"}
                </button>
              </li>
            ))}
          </ul>
        ) : null}
        <button
          type="button"
          className="button"
          data-testid="logout-all"
          disabled={busy || state.kind !== "ready"}
          onClick={() => void handleLogoutAll()}
        >
          Log out of all sessions
        </button>
        {notice ? (
          <p role="status" data-testid="sessions-notice">
            {notice}
          </p>
        ) : null}
        {error ? (
          <p role="alert" data-testid="sessions-error">
            {error}
          </p>
        ) : null}
      </section>
    </AppShell>
  );
}
