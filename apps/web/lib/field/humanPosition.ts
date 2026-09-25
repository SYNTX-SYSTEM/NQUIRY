/**
 * SF-02 human position (22 §2.6 "visible human position", §32.6 stack order item 3).
 *
 * A LABEL derived from the server projection, never a gate: no control anywhere
 * is conditioned on these values (every affordance comes from a server
 * capability). This is the one Field module allowed to read the viewer flags
 * (tests/field/gates.test.ts allowlist), and it must never call a command.
 */
export type ViewerProjection = {
  readonly userId: string;
  readonly role: string | null;
  readonly isSessionController?: boolean;
  readonly isGovernanceRoot?: boolean;
  /** F01 orientation projection name for the same relation (`GET /workspaces/{w}`). */
  readonly governanceCapable?: boolean;
};

export type HumanPosition = {
  /** Short relation words, in semantic order, e.g. ["Facilitator", "Session controller", "participant"]. */
  readonly relations: readonly string[];
  readonly sentence: string;
};

export function humanPosition(
  viewer: ViewerProjection,
  options: { readonly participantIds?: readonly string[]; readonly scope: "workspace" | "session" },
): HumanPosition {
  const relations: string[] = [];
  relations.push(viewer.role ? `Role: ${viewer.role}` : "No role in this Workspace");
  if (viewer.isGovernanceRoot || viewer.governanceCapable) relations.push("Workspace governance root");
  if (options.scope === "session") {
    relations.push(viewer.isSessionController ? "Session controller" : "Not the Session controller");
    if (options.participantIds) {
      relations.push(options.participantIds.includes(viewer.userId) ? "Participant" : "Not a participant");
    }
  }
  return { relations, sentence: `You: ${relations.join(" · ")}` };
}
