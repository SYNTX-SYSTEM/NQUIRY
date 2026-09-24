"use client";

/**
 * F01 WU-01.9 -- "authenticate -> see accessible Workspaces ->
 * establish or enter legitimate Workspace context" (19 SS21's own
 * HUMAN PRODUCT EFFECT chain), the first real screen for it. Calls the
 * real `GET /workspaces` (WU-01.2/WU-01.8) and `POST /workspaces`
 * (WU-01.4b/WU-01.8) routes -- no mock data, no client-side guess at
 * which Workspaces are accessible. An unauthenticated visitor is
 * redirected to `/login`, same check every other real page in this
 * app already performs (`app/page.tsx`'s own `fetchCurrentSession`
 * pattern).
 *
 * `LogoutButton` is included because this page is now the real landing
 * screen `/` redirects a logged-in visitor to whenever no default
 * demo Session is configured -- the same reason the Session-view page
 * carries its own copy (`app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx`'s
 * own docstring).
 */
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchCurrentSession } from "../../lib/api/authClient";
import {
  createWorkspace,
  listWorkspaces,
  type WorkspaceSummary,
} from "../../lib/api/workspaceClient";
import Link from "next/link";
import { AppShell } from "../../components/f02/AppShell";

type LoadState =
  | { readonly kind: "checking" }
  | { readonly kind: "ready"; readonly workspaces: readonly WorkspaceSummary[] }
  | { readonly kind: "denied"; readonly reasonCode: string };

export default function WorkspacesPage() {
  const router = useRouter();
  const [state, setState] = useState<LoadState>({ kind: "checking" });
  const [name, setName] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  function load() {
    listWorkspaces().then((result) => {
      if (result.kind === "ok") {
        setState({ kind: "ready", workspaces: result.workspaces });
      } else {
        setState({ kind: "denied", reasonCode: result.reasonCode });
      }
    });
  }

  useEffect(() => {
    let cancelled = false;
    fetchCurrentSession()
      .then((result) => {
        if (cancelled) {
          return;
        }
        if (result.kind !== "ok") {
          router.replace("/login");
          return;
        }
        load();
      })
      .catch(() => {
        if (!cancelled) {
          router.replace("/login");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [router]);

  function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCreating(true);
    setCreateError(null);
    createWorkspace(name)
      .then((result) => {
        setCreating(false);
        if (result.kind === "ok") {
          setName("");
          router.push(`/workspaces/${result.workspaceId}`);
          return;
        }
        setCreateError(result.reasonCode);
      })
      .catch(() => {
        setCreating(false);
        setCreateError("Unable to reach the server. Please try again.");
      });
  }

  return (
    <AppShell crumbs={[{ label: "Workspaces" }]}>
      <div className="grid-2">
        <section className="panel" aria-labelledby="ws-title">
          <p className="eyebrow">Your inquiry spaces</p>
          <h1 id="ws-title">Workspaces</h1>
          {state.kind === "checking" ? <p data-testid="workspaces-checking">Loading your Workspaces…</p> : null}
          {state.kind === "denied" ? (
            <p role="alert" data-testid="workspaces-denied">
              {state.reasonCode}
            </p>
          ) : null}
          {state.kind === "ready" && state.workspaces.length === 0 ? (
            <p data-testid="workspaces-empty">You do not have any Workspaces yet.</p>
          ) : null}
          {state.kind === "ready" && state.workspaces.length > 0 ? (
            <ul className="plain-list" data-testid="workspaces-list">
              {state.workspaces.map((ws) => (
                <li key={ws.workspaceId}>
                  <Link className="card-link" href={`/workspaces/${ws.workspaceId}`}>
                    {ws.name}
                  </Link>
                </li>
              ))}
            </ul>
          ) : null}
        </section>
        <section className="panel" aria-labelledby="create-ws-title">
          <h2 id="create-ws-title">Found a Workspace</h2>
          <p className="muted">
            Founding makes you this Workspace&apos;s governance root (HARD-DEP-001, Option A). It does not make you a
            Facilitator. Challenges are framed by Facilitators you add.
          </p>
          <form onSubmit={handleCreate} data-testid="create-workspace-form">
            <div className="field">
              <label htmlFor="workspace-name">Workspace name</label>
              <input
                id="workspace-name"
                data-testid="workspace-name-input"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </div>
            <div className="actions-row">
              <button className="button" type="submit" data-testid="create-workspace-submit" disabled={creating}>
                {creating ? "Creating…" : "Create Workspace"}
              </button>
            </div>
          </form>
          {createError !== null ? (
            <p role="alert" data-testid="create-workspace-error">
              {createError}
            </p>
          ) : null}
        </section>
      </div>
    </AppShell>
  );
}
