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
 */
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "../../../components/f02/AppShell";
import {
  listSessions,
  logoutAll,
  revokeSession,
  type SessionListResult,
  type SessionSummary,
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
