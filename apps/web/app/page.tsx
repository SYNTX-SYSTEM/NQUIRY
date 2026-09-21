"use client";

/**
 * Local-login field (`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`).
 *
 * REPLACES the former PKG-00 Phase-0 stub. Root route policy: no valid
 * session -> `/login`; a valid session -> the real application. This
 * is a Client Component (not a Next.js Server Component reading
 * `cookies()`) for the identical reason `client.ts`'s own header
 * docstring already gives for every other real fetch in this codebase:
 * the `nquiry_session` cookie is scoped to the API's own origin
 * (`http://localhost:8000`), not the frontend's
 * (`http://localhost:3000`) -- a Next.js Server Component running
 * during SSR sees only cookies sent TO `localhost:3000` itself, never
 * a different origin's cookie. Only the BROWSER, which already holds
 * the cookie for the correct origin, can ask `GET /auth/me` and get a
 * real answer -- proven by this repository's own existing Playwright
 * E2E convention.
 *
 * "The real application" landing target: `NEXT_PUBLIC_DEFAULT_WORKSPACE_ID`/
 * `NEXT_PUBLIC_DEFAULT_SESSION_ID` (optional, set on the `web` service
 * in `docker-compose.yml`) name one specific seeded demo Session
 * (`scripts/seed_local_demo.py`) to land on directly after login; if
 * unset, a logged-in visitor is sent to `/workspaces` (F01 WU-01.9),
 * the real Workspace list/orientation screen -- no longer a plain
 * placeholder message, now that a real Workspace list/creation route
 * exists (`docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`'s
 * own disclosed "No Challenge/Session-creation UI or HTTP route" gap
 * is now closed for the Workspace half; Challenge/Session
 * creation itself remains unbuilt).
 */
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchCurrentSession } from "../lib/api/authClient";

type CheckState = { readonly kind: "checking" } | { readonly kind: "redirecting" };

const DEFAULT_WORKSPACE_ID = process.env.NEXT_PUBLIC_DEFAULT_WORKSPACE_ID;
const DEFAULT_SESSION_ID = process.env.NEXT_PUBLIC_DEFAULT_SESSION_ID;

export default function Home() {
  const router = useRouter();
  const [state, setState] = useState<CheckState>({ kind: "checking" });

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
        setState({ kind: "redirecting" });
        if (DEFAULT_WORKSPACE_ID && DEFAULT_SESSION_ID) {
          router.replace(`/workspaces/${DEFAULT_WORKSPACE_ID}/sessions/${DEFAULT_SESSION_ID}`);
          return;
        }
        router.replace("/workspaces");
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

  if (state.kind === "checking") {
    return (
      <main>
        <p data-testid="root-checking">Checking session...</p>
      </main>
    );
  }
  return (
    <main>
      <p data-testid="root-redirecting">Logged in. Opening your Workspaces...</p>
    </main>
  );
}
