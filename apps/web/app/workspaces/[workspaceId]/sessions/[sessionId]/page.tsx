/**
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
 */
import type { SessionId, WorkspaceId } from "../../../../../lib/api/types";
import { SessionViewContainer } from "../../../../../components/SessionViewContainer";

export default async function SessionPage({
  params,
}: {
  params: Promise<{ workspaceId: string; sessionId: string }>;
}) {
  const { workspaceId, sessionId } = await params;
  return (
    <main>
      <SessionViewContainer workspaceId={workspaceId as WorkspaceId} sessionId={sessionId as SessionId} />
    </main>
  );
}
