/**
 * F02 WU-02.10: MOVED from `/workspaces/{w}/sessions/{s}` to `.../decision`. The canonical Session page is the
 * governed inquiry-position page; this PKG-28/29 surface stays as the Decision surface until F07 re-homes it onto
 * a lawfully reached Decision.
 *
 * Server Component shell that only extracts the route params and hands them to the real Client Component
 * (`SessionViewContainer`) — the actual `fetch` happens in the browser (`lib/api/client.ts`). Route params are untyped
 * strings from the URL, cast to the branded ids ONLY as identifier labels: this route performs no authority decision
 * of its own; the server's own `SessionReadResult` is the only thing ever rendered.
 *
 * Identity comes from the real, verified `nquiry_session` cookie, never a URL parameter (local-login field).
 *
 * SF-05 (doc 26 §31): the container renders the field frame itself (background, orientation rail with the identity
 * and the logout control OUTSIDE `<main>`, the organ grammar inside), so `tests/e2e/session-view.spec.ts`'s proof
 * that no action element exists within `main` for a denied / blocked / indeterminate response keeps its scope.
 */
import type { SessionId, WorkspaceId } from "../../../../../../lib/api/types";
import { SessionViewContainer } from "../../../../../../components/SessionViewContainer";

export default async function SessionPage({
  params,
}: {
  params: Promise<{ workspaceId: string; sessionId: string }>;
}) {
  const { workspaceId, sessionId } = await params;
  return <SessionViewContainer workspaceId={workspaceId as WorkspaceId} sessionId={sessionId as SessionId} />;
}
