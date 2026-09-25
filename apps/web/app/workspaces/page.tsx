"use client";

/**
 * Workspace Overview Field (22 §22.1): the Field of accessible Workspace relations.
 *
 * F01 WU-01.9 relations, unchanged: the real `GET /workspaces` (accessible
 * Workspaces of the authenticated identity) and the real `POST /workspaces`
 * (founding; HARD-DEP-001 Option A: any authenticated identity may found and
 * becomes the governance root). An unauthenticated visitor is redirected to
 * `/login` after the real `GET /auth/me` check.
 *
 * Core = the identity/access position (22 §12.1 → §22.1 "identity/access or
 * selected workspace preview"). Orbit = the founding relation (possible for
 * every authenticated identity, by the repository's own semantics) followed by
 * the accessible Workspaces, each a link into its Field. The founding form is
 * an instrument in the action plane. `POST /workspaces` carries no
 * Idempotency-Key (F01), so a lost response is an UNKNOWN consequence: the
 * list is re-read and the human is never invited to "try again" blindly.
 */
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { EffectIntent, EffectOutcome, ReconstructionNote } from "../../components/field/EffectSurface";
import { ChamberHead, Identifiers } from "../../components/field/chambers";
import { FieldFrame } from "../../components/field/FieldFrame";
import { LogoutButton } from "../../components/LogoutButton";
import { ReadBoundary } from "../../components/field/ReadBoundary";
import { FieldCore } from "../../components/field/topology/FieldCore";
import { FieldStage, Plane, Planes, Topology } from "../../components/field/topology/FieldStage";
import { Orbit, type OrbitNode, nodeContent } from "../../components/field/topology/Orbit";
import { fetchCurrentSession } from "../../lib/api/authClient";
import { createWorkspace, listWorkspaces, type WorkspaceSummary } from "../../lib/api/workspaceClient";
import { accessTrace } from "../../lib/field/position";
import { normalizeWorkspaces } from "../../lib/field/workspaces";

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
  const [identity, setIdentity] = useState<string | null>(null);
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
        setIdentity(result.userId);
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

  const workspaces = state.kind === "ready" ? state.workspaces : [];
  // SF-05 (doc 26 §7): normalization BEFORE geometry — one canonical id → one entity; homonymous names carry their
  // canonical distinguisher (founding time · short id); repeated relations to one Workspace become one node
  const normalized = normalizeWorkspaces(workspaces);
  // the SF-04 access field: the founding relation and every accessible Workspace on ONE containment ring around the
  // access core (restored after the SF-05 ring segmentation and the capsule constellation degraded it)
  const nodes: OrbitNode[] = [
    {
      key: "found",
      state: "possible",
      label: "Found a Workspace",
      actionLabel: "Found a Workspace",
      meta: "possible for every authenticated identity",
      onActivate: () => document.getElementById("workspace-name")?.focus(),
      testId: "found-workspace-node",
    },
    ...normalized.map(
      (ws): OrbitNode => ({
        key: ws.workspaceId,
        state: "established",
        label: ws.name,
        meta: ws.distinguisher ? `Workspace · ${ws.distinguisher}` : "accessible Workspace",
        href: `/workspaces/${ws.workspaceId}`,
        relationCount: ws.relationCount,
      }),
    ),
  ];
  const rings = state.kind === "ready" ? [nodes.map((n) => nodeContent(n, "containment"))] : [];
  const coreState = state.kind === "checking" ? "loading" : state.kind === "ready" ? "current" : "boundary";
  const stateText =
    state.kind === "ready"
      ? `${workspaces.length} accessible ${workspaces.length === 1 ? "Workspace" : "Workspaces"}`
      : state.kind === "checking"
        ? "reading accessible Workspaces…"
        : state.kind.toUpperCase();

  const overviewCore = { title: "Workspaces", stateText, meta: identity ?? undefined };

  return (
    <FieldFrame trace={accessTrace("current")} regime="workspace-access" exit={identity ? <LogoutButton /> : null}>
      <FieldStage layout={state.kind === "ready" ? { core: overviewCore, rings } : undefined} mode={state.kind === "ready" ? undefined : "stack"} surface="workspace-access">
        <Topology layout={{ core: overviewCore, rings }}>
          <FieldCore kind="access" state={coreState} eyebrow="Your access" title={<span id="ws-title">Workspaces</span>} stateText={stateText} meta={identity ? <span className="mono">{identity}</span> : null}>
            <ReconstructionNote field={effect.field} />
          </FieldCore>
          {state.kind === "ready" ? (
            <Orbit kind="containment" ring={1} heading="Accessible Workspaces" nodes={nodes} testId="workspaces-list" listAriaLabel="Accessible Workspaces" />
          ) : null}
        </Topology>

        <Planes header={{ eyebrow: "Grown from", title: "Your access", state: stateText }}>
          <Plane kind="action" labelledBy="create-ws-title">
            <ChamberHead id="create-ws-title" semantic="action" title="Found a Workspace" marker="possible" />
            {state.kind === "checking" ? <p className="projection-pending" data-testid="workspaces-checking">Loading your Workspaces…</p> : null}
            {state.kind === "denied" ? <ReadBoundary kind="denied" reasonCode={state.reasonCode} reasonTestId="workspaces-denied" /> : null}
            {state.kind === "unreachable" ? <ReadBoundary kind="network_failure" reasonCode="NETWORK_FAILURE" /> : null}
            {state.kind === "ready" && workspaces.length === 0 ? (
              <p data-testid="workspaces-empty">You do not have any Workspaces yet.</p>
            ) : null}
            <p className="muted">
              Founding makes you this Workspace&apos;s governance root (HARD-DEP-001, Option A). It does not make you a
              Facilitator. Challenges are framed by Facilitators you add.
            </p>
            <form onSubmit={handleCreate} data-testid="create-workspace-form" id="found-workspace">
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
          </Plane>
          <Plane kind="proof" semantic="identity" labelledBy="access-proof-title">
            <ChamberHead id="access-proof-title" semantic="identity" title="Identity and access" marker={identity ? "authenticated" : undefined} />
            <p className="chamber-lede">Accessible Workspaces are the server&apos;s projection of your current memberships; nothing is inferred here.</p>
            {identity ? <Identifiers items={[{ label: "Authenticated identity", value: identity }]} /> : null}
          </Plane>
        </Planes>
      </FieldStage>
    </FieldFrame>
  );
}
