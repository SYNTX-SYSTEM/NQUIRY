/**
 * SF-01 Position & Orientation (21 §12, CF-01, CF-02): the Relation Trace.
 *
 *   established parent → established child → current relation → lawful possible relation
 *
 * A trace is derived ONLY from a confirmed server projection. A coordinate the
 * server has not confirmed yet (loading, NOT_FOUND, DENIED) is absent, so a
 * failed or pending read reconstructs to the nearest confirmed parent (21 §14).
 *
 * Laws enforced here:
 * - No Session coordinate before a Session exists. Before creation the Session
 *   relation is only `possible` (server capability available) or `unavailable`
 *   (server reason code), never a place.
 * - A future relation never carries an `href` (falsifier 32). Established
 *   parents do: moving between accessible contexts is lawful (21 §29).
 * - The current coordinate is never a link.
 *
 * Inputs are the published F02 projection types, consumed read-only.
 */
import type { Capability, ChallengeDetail, WorkspaceOverview } from "../api/inquiryClient";

export type TraceCoordinate = "access" | "workspace" | "challenge" | "session" | "session-state";
export type TraceStatus = "established" | "current" | "possible" | "unavailable";

export type TraceSegment = {
  readonly coordinate: TraceCoordinate;
  readonly label: string;
  readonly status: TraceStatus;
  readonly href?: string;
  /** Server reason code for an `unavailable` future relation. */
  readonly reasonCode?: string;
  /** Session state only: the committed Command that established it, or null if none is recorded. */
  readonly establishedBy?: string | null;
};

const ACCESS_LABEL = "Workspaces";

export function accessTrace(status: "current" | "established"): TraceSegment[] {
  return status === "current"
    ? [{ coordinate: "access", label: ACCESS_LABEL, status }]
    : [{ coordinate: "access", label: ACCESS_LABEL, status, href: "/workspaces" }];
}

function futureRelation(coordinate: TraceCoordinate, label: string, capability: Capability): TraceSegment {
  return capability.available
    ? { coordinate, label, status: "possible" }
    : { coordinate, label, status: "unavailable", reasonCode: capability.reasonCode ?? undefined };
}

function establishedWorkspace(workspace: { readonly workspaceId: string; readonly name: string }): TraceSegment {
  return {
    coordinate: "workspace",
    label: workspace.name,
    status: "established",
    href: `/workspaces/${encodeURIComponent(workspace.workspaceId)}`,
  };
}

/** The Workspace name alone, when only the F01 orientation read is confirmed. */
export function workspaceNameTrace(name: string): TraceSegment[] {
  return [...accessTrace("established"), { coordinate: "workspace", label: name, status: "current" }];
}

export function workspaceTrace(overview: WorkspaceOverview): TraceSegment[] {
  return [
    ...accessTrace("established"),
    { coordinate: "workspace", label: overview.workspace.name, status: "current" },
    futureRelation("challenge", "New Challenge", overview.capabilities.createChallenge),
  ];
}

export function challengeTrace(detail: ChallengeDetail): TraceSegment[] {
  return [
    ...accessTrace("established"),
    establishedWorkspace(detail.workspace),
    { coordinate: "challenge", label: detail.challenge.title, status: "current" },
    futureRelation("session", "New Session", detail.capabilities.openSession),
  ];
}

/**
 * Exactly what the trace reads, all F02-published coordinates, declared
 * structurally instead of derived from the projection type. Two consequences:
 * the trace and its proof are unaffected when the projection grows (F03 added
 * `serverNow`, `questionSet` and Burst fields: the post-sync First Broken
 * Relation, WU-SF01.8), and the contract test (`SessionPosition` assignable
 * to this) fails if a later Field removes or retypes a field read here.
 */
export type SessionTraceInput = {
  readonly workspace: { readonly workspaceId: string; readonly name: string };
  readonly challenge: { readonly challengeId: string; readonly title: string | null };
  readonly session: { readonly state: string };
  readonly establishedBy: { readonly commandType: string } | null;
};

/**
 * Session trace primitive. NOT adopted on the Session page yet: Session-page
 * integration is Stage 2 and needs its own authorization (SF-01 human
 * decision 3 and the integration law). It reads only the F02-published
 * coordinates.
 */
export function sessionTrace(position: SessionTraceInput): TraceSegment[] {
  const challengeHref = `/workspaces/${encodeURIComponent(position.workspace.workspaceId)}/challenges/${encodeURIComponent(
    position.challenge.challengeId,
  )}`;
  return [
    ...accessTrace("established"),
    establishedWorkspace(position.workspace),
    { coordinate: "challenge", label: position.challenge.title ?? "", status: "established", href: challengeHref },
    { coordinate: "session", label: "Session", status: "established" },
    {
      coordinate: "session-state",
      label: position.session.state,
      status: "current",
      establishedBy: position.establishedBy?.commandType ?? null,
    },
  ];
}
