"use client";

/**
 * F01 WU-01.9 -- "Workspace orientation" (19 SS21's own FRONTEND
 * REQUIREMENTS: "Render separately: authenticated / member / authorized
 * / governance-capable / non-proof demo state"). Calls the real
 * `GET /workspaces/{workspaceId}` route (WU-01.3 + WU-01.7 combined,
 * WU-01.8), which already implies "authenticated"/"member" by ever
 * returning `kind: ok` at all -- this page renders `role`/`authorized`/
 * `governanceCapable` exactly as the server computed them, never a
 * client-side re-derivation. "non-proof demo state" is not rendered:
 * the server itself does not compute it (`capability_projection`'s own
 * module docstring), so there is nothing here to display.
 *
 * A `governanceCapable` visitor additionally sees a real "Add Member"
 * form (`POST .../members`, WU-01.5/WU-01.8) -- the form's own
 * presence is not itself an authority decision (a non-capable visitor
 * simply never sees it); the real BND-004/005 gate on the server is
 * still what actually decides every submission, exactly like every
 * other governed action in this app.
 *
 * This is a Client Component using `useParams()` rather than the
 * Server-Component-shell-plus-Client-Component-container split
 * `app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx` uses --
 * a disclosed, simpler convention for this Work Unit's own two new
 * pages (this one and `app/workspaces/page.tsx`), not a claim that the
 * other pattern was wrong; both achieve the same "fetch happens in the
 * browser" requirement `lib/api/client.ts`'s own docstring explains.
 */
import { type FormEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchCurrentSession } from "../../../lib/api/authClient";
import {
  addMember,
  fetchWorkspaceOrientation,
  type WorkspaceOrientationResult,
} from "../../../lib/api/workspaceClient";

type LoadState =
  | { readonly kind: "checking" }
  | { readonly kind: "loaded"; readonly result: WorkspaceOrientationResult }
  | { readonly kind: "error" };

type AddMemberFormState =
  | { readonly kind: "idle" }
  | { readonly kind: "submitting" }
  | { readonly kind: "done"; readonly message: string }
  | { readonly kind: "error"; readonly message: string };

export default function WorkspaceOrientationPage() {
  const params = useParams<{ workspaceId: string }>();
  const workspaceId = params.workspaceId;
  const router = useRouter();
  const [state, setState] = useState<LoadState>({ kind: "checking" });
  const [newMemberUserId, setNewMemberUserId] = useState("");
  const [newMemberRole, setNewMemberRole] = useState("Contributor");
  const [formState, setFormState] = useState<AddMemberFormState>({ kind: "idle" });

  function load() {
    fetchWorkspaceOrientation(workspaceId)
      .then((result) => setState({ kind: "loaded", result }))
      .catch(() => setState({ kind: "error" }));
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, workspaceId]);

  function handleAddMember(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormState({ kind: "submitting" });
    addMember(workspaceId, newMemberUserId, newMemberRole)
      .then((result) => {
        if (result.kind === "ok") {
          setFormState({ kind: "done", message: "Member added." });
          setNewMemberUserId("");
          load();
          return;
        }
        const message = result.kind === "indeterminate" ? result.blockedTargetRef : result.reasonCode;
        setFormState({ kind: "error", message });
      })
      .catch(() => {
        setFormState({ kind: "error", message: "Unable to reach the server. Please try again." });
      });
  }

  if (state.kind === "checking") {
    return (
      <main>
        <p data-testid="orientation-checking">Loading Workspace...</p>
      </main>
    );
  }
  if (state.kind === "error") {
    return (
      <main>
        <p role="alert" data-testid="orientation-error">
          Unable to reach the server. Please try again.
        </p>
      </main>
    );
  }

  const result = state.result;
  if (result.kind === "denied") {
    return (
      <main>
        <p role="alert" data-testid="orientation-denied">
          {result.reasonCode}
        </p>
      </main>
    );
  }

  return (
    <main>
      <h1 data-testid="orientation-workspace-name">{result.workspace.name}</h1>
      <p data-testid="orientation-role">Your role: {result.role}</p>
      <p data-testid="orientation-authorized">Authorized: {String(result.authorized)}</p>
      <p data-testid="orientation-governance-capable">
        Governance-capable: {String(result.governanceCapable)}
      </p>
      {result.heldAuthorityClasses.length > 0 ? (
        <ul data-testid="orientation-authority-classes">
          {result.heldAuthorityClasses.map((authorityClass) => (
            <li key={authorityClass}>{authorityClass}</li>
          ))}
        </ul>
      ) : null}

      {result.governanceCapable ? (
        <section>
          <h2>Add a member</h2>
          <form onSubmit={handleAddMember} data-testid="add-member-form">
            <label htmlFor="new-member-user-id">User ID</label>
            <input
              id="new-member-user-id"
              data-testid="new-member-user-id-input"
              type="text"
              required
              value={newMemberUserId}
              onChange={(event) => setNewMemberUserId(event.target.value)}
            />
            <label htmlFor="new-member-role">Role</label>
            <select
              id="new-member-role"
              data-testid="new-member-role-select"
              value={newMemberRole}
              onChange={(event) => setNewMemberRole(event.target.value)}
            >
              <option value="Contributor">Contributor</option>
              <option value="Facilitator">Facilitator</option>
            </select>
            <button
              type="submit"
              data-testid="add-member-submit"
              disabled={formState.kind === "submitting"}
            >
              {formState.kind === "submitting" ? "Adding..." : "Add member"}
            </button>
          </form>
          {formState.kind === "done" ? (
            <p data-testid="add-member-success">{formState.message}</p>
          ) : null}
          {formState.kind === "error" ? (
            <p role="alert" data-testid="add-member-error">
              {formState.message}
            </p>
          ) : null}
        </section>
      ) : null}
    </main>
  );
}
