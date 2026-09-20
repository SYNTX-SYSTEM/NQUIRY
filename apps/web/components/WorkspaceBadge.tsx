/**
 * 12 §24 item 1: "authenticated Workspace context" -- a passive
 * display of which Workspace the currently-rendered data belongs to.
 *
 * WHY THIS NEVER LETS A VIEWER TYPE OR SWITCH A WORKSPACE ID
 * --------------------------------------------------------------------
 * This package's own BOUNDARIES line ("Server responses only, no
 * client authority calculation") means the Workspace shown here is
 * always exactly the `workspaceId` the SERVER's own `SessionView`
 * response carried, never a value this component invented, defaulted,
 * or let a viewer edit -- there is deliberately no input element here
 * at all. This is what the "forged Workspace in client" E2E attack
 * proof (`tests/e2e/session-view.spec.ts`) exercises: even if the
 * PAGE URL names one Workspace, only the value inside the server's own
 * resolved response body is ever rendered.
 */
import type { WorkspaceId } from "../lib/api/types";

export function WorkspaceBadge({ workspaceId }: { readonly workspaceId: WorkspaceId }) {
  return (
    <span data-testid="workspace-badge" title="Workspace">
      Workspace: {workspaceId}
    </span>
  );
}
