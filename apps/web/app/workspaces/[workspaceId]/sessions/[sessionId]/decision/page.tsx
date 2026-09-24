/**
 * F02 WU-02.10: MOVED from `/workspaces/{w}/sessions/{s}` to `.../decision`.
 * The canonical Session page is now the governed inquiry-position page. This
 * PKG-28/29 surface (Session view + Decision recording) stays as the Decision
 * surface until F07 re-homes it onto a lawfully reached Decision.
 *
 * 12 §24's own PKG-28 Session-view route. Server Component shell that
 * only extracts the route params and hands them to the real Client
 * Component (`SessionViewContainer`) -- the actual `fetch` happens in
 * the browser, per `lib/api/client.ts`'s own header docstring.
 *
 * Route params are untyped strings from the URL; they are cast to the
 * branded `WorkspaceId`/`SessionId` types here ONLY as an identifier
 * label to pass through to the server -- this route performs no
 * authority decision of its own (this package's own BOUNDARIES line),
 * so there is nothing here for a forged/arbitrary URL segment to
 * bypass: the server's own `SessionReadResult` response is still the
 * only thing ever rendered.
 *
 * LOCAL-LOGIN FIELD UPDATE
 * (`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`): the former
 * `?as=<userId>` query parameter (Architecture 17's disclosed,
 * temporary GAP-14-001 substitute, since this prototype had no login
 * mechanism) is REMOVED -- identity now comes from a real, verified
 * `nquiry_session` cookie (`lib/api/authClient.ts`), never a URL
 * parameter. A visitor with no valid session gets the real `401`/
 * `denied` response `SessionViewContainer` already renders as
 * `DeniedBanner` -- this route still performs no authority decision of
 * its own.
 *
 * `LogoutButton` is included because a visitor whose root route (`/`)
 * redirects straight here (a configured default Session) would
 * otherwise have no reachable way back to `/login`. Deliberately
 * placed in a `<header>` OUTSIDE `<main>`, not alongside
 * `SessionViewContainer` inside it: `tests/e2e/session-view.spec.ts`'s
 * own mandatory attacks assert zero action elements exist within
 * `main` for a denied/blocked/indeterminate response -- a logout
 * control is orthogonal to that invariant (it never touches Session/
 * Decision/boundary state and is always safe regardless of what the
 * server returned), so it belongs in page chrome, not the domain
 * content region those tests scope their proof to.
 */
import type { SessionId, WorkspaceId } from "../../../../../../lib/api/types";
import { LogoutButton } from "../../../../../../components/LogoutButton";
import { SessionViewContainer } from "../../../../../../components/SessionViewContainer";

export default async function SessionPage({
  params,
}: {
  params: Promise<{ workspaceId: string; sessionId: string }>;
}) {
  const { workspaceId, sessionId } = await params;
  return (
    <>
      <header>
        <LogoutButton />
      </header>
      <main>
        <SessionViewContainer workspaceId={workspaceId as WorkspaceId} sessionId={sessionId as SessionId} />
      </main>
    </>
  );
}
