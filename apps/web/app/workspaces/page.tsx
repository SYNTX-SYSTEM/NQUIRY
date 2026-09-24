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
 * SF-01 (21 §7 PF-01, §12, §17, C3-01): the access context of the
 * Relational Interaction Field. Position is the Relation Trace (access
 * context only: no Workspace is confirmed here). Founding a Workspace is one
 * effect relation. `POST /workspaces` (F01) carries NO Idempotency-Key, so a
 * lost response is an UNKNOWN consequence: the list is re-read and the human
 * is never invited to "try again" blindly (a retry could found a second
 * Workspace). A response outside the F01 vocabulary is INDETERMINATE.
 */
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { EffectIntent, EffectOutcome, ReconstructionNote } from "../../components/field/EffectSurface";
import { FieldFrame, FieldLayout, FieldZone } from "../../components/field/FieldFrame";
import { ReadBoundary } from "../../components/field/ReadBoundary";
import { fetchCurrentSession } from "../../lib/api/authClient";
import { createWorkspace, listWorkspaces, type WorkspaceSummary } from "../../lib/api/workspaceClient";
import { accessTrace } from "../../lib/field/position";
import { type Settlement, useEffectField } from "../../lib/field/useEffectField";

type LoadState =
  | { readonly kind: "checking" }
  | { readonly kind: "ready"; readonly workspaces: readonly WorkspaceSummary[] }
  | { readonly kind: "denied"; readonly reasonCode: string }
  | { readonly kind: "unreachable" };

const CREATE = "create-workspace";

/** Founding over the keyless F01 route; tells transport loss apart from an unrecognized response. */
async function foundWorkspace(name: string): Promise<Settlement<{ readonly workspaceId: string }>> {
  let reached = true;
  const tracked: typeof fetch = (input, init) =>
    fetch(input, init).catch((error: unknown) => {
      reached = false;
      throw error;
    });
  try {
    const result = await createWorkspace(name, tracked);
    return result.kind === "ok"
      ? { kind: "committed", reasonCode: null, body: { workspaceId: result.workspaceId } }
      : { kind: result.kind, reasonCode: result.reasonCode };
  } catch {
    return reached
      ? { kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" }
      : { kind: "network_failure", reasonCode: "NETWORK_FAILURE" };
  }
}

export default function WorkspacesPage() {
  const router = useRouter();
  const [state, setState] = useState<LoadState>({ kind: "checking" });
  const [name, setName] = useState("");
  const effect = useEffectField();

  const load = useCallback(async (): Promise<boolean> => {
    try {
      const result = await listWorkspaces();
      if (result.kind === "ok") {
        setState({ kind: "ready", workspaces: result.workspaces });
        return true;
      }
      setState({ kind: "denied", reasonCode: result.reasonCode });
      return false;
    } catch {
      // Read path: the projection is unavailable. A list confirmed earlier stays,
      // explicitly marked as last confirmed (ReconstructionNote).
      setState((prev) => (prev.kind === "ready" ? prev : { kind: "unreachable" }));
      return false;
    }
  }, []);

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
        void load();
      })
      .catch(() => {
        if (!cancelled) {
          router.replace("/login");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [router, load]);

  function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void effect.run({
      relation: CREATE,
      keyed: false,
      send: () => foundWorkspace(name),
      reconstruct: load,
      onCommitted: (body) => {
        setName("");
        router.push(`/workspaces/${body.workspaceId}`);
        return true;
      },
    });
  }

  return (
    <FieldFrame trace={accessTrace("current")} regime="workspace-access">
      <header className="field-heading">
        <p className="eyebrow">Your inquiry spaces</p>
        <h1 id="ws-title">Workspaces</h1>
      </header>
      <FieldLayout
        primary={
          <>
            <FieldZone zone="centre" labelledBy="ws-title">
              <ReconstructionNote field={effect.field} />
              {state.kind === "checking" ? <p data-testid="workspaces-checking">Loading your Workspaces…</p> : null}
              {state.kind === "denied" ? (
                <ReadBoundary kind="denied" reasonCode={state.reasonCode} reasonTestId="workspaces-denied" />
              ) : null}
              {state.kind === "unreachable" ? <ReadBoundary kind="network_failure" reasonCode="NETWORK_FAILURE" /> : null}
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
            </FieldZone>
            <FieldZone zone="near" labelledBy="create-ws-title">
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
                  <button className="button" type="submit" data-testid="create-workspace-submit" disabled={effect.blocked}>
                    Create Workspace
                  </button>
                </div>
              </form>
              <EffectIntent field={effect.field} relation={CREATE} />
              <EffectOutcome
                field={effect.field}
                relation={CREATE}
                reasonTestId="create-workspace-error"
                onReread={() => void effect.rereadNow(load)}
              />
            </FieldZone>
          </>
        }
      />
    </FieldFrame>
  );
}
