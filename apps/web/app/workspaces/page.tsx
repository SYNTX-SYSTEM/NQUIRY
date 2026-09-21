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
import { LogoutButton } from "../../components/LogoutButton";

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

  if (state.kind === "checking") {
    return (
      <main>
        <p data-testid="workspaces-checking">Loading your Workspaces...</p>
      </main>
    );
  }

  if (state.kind === "denied") {
    return (
      <main>
        <p role="alert" data-testid="workspaces-denied">
          Could not load your Workspaces ({state.reasonCode}).
        </p>
      </main>
    );
  }

  return (
    <main>
      <h1>Your Workspaces</h1>
      {state.workspaces.length === 0 ? (
        <p data-testid="workspaces-empty">You do not have any Workspaces yet.</p>
      ) : (
        <ul data-testid="workspaces-list">
          {state.workspaces.map((workspace) => (
            <li key={workspace.workspaceId}>
              <a href={`/workspaces/${workspace.workspaceId}`}>{workspace.name}</a>
            </li>
          ))}
        </ul>
      )}
      <h2>Found a new Workspace</h2>
      <form onSubmit={handleCreate} data-testid="create-workspace-form">
        <label htmlFor="workspace-name">Name</label>
        <input
          id="workspace-name"
          data-testid="workspace-name-input"
          type="text"
          required
          value={name}
          onChange={(event) => setName(event.target.value)}
        />
        <button type="submit" data-testid="create-workspace-submit" disabled={creating}>
          {creating ? "Creating..." : "Create"}
        </button>
      </form>
      {createError ? (
        <p role="alert" data-testid="create-workspace-error">
          {createError}
        </p>
      ) : null}
      <LogoutButton />
    </main>
  );
}
