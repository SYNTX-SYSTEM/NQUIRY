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
 * "The real application" landing target, honestly scoped: this
 * prototype has no Workspace-list/dashboard UI or backend Query for
 * one yet (`docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`'s
 * own disclosed "No Challenge/Session-creation UI or HTTP route" gap,
 * unchanged) -- building one now would be exactly the new, undirected
 * product capability that document's own field boundary forbids.
 * `NEXT_PUBLIC_DEFAULT_WORKSPACE_ID`/`NEXT_PUBLIC_DEFAULT_SESSION_ID`
 * (optional, set on the `web` service in `docker-compose.yml`, read by
 * `next dev` at server startup the same way it already reads
 * `NEXT_PUBLIC_API_BASE_URL` when that variable IS set) name the one
 * seeded demo Session (`scripts/seed_local_demo.py`) to land on after
 * login; if unset, a logged-in visitor sees a plain confirmation
 * screen instead of being redirected to a guess.
 */
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LogoutButton } from "../components/LogoutButton";
import { fetchCurrentSession } from "../lib/api/authClient";

type CheckState =
  | { readonly kind: "checking" }
  | { readonly kind: "authenticated"; readonly userId: string }
  | { readonly kind: "redirecting" };

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
        if (DEFAULT_WORKSPACE_ID && DEFAULT_SESSION_ID) {
          setState({ kind: "redirecting" });
          router.replace(`/workspaces/${DEFAULT_WORKSPACE_ID}/sessions/${DEFAULT_SESSION_ID}`);
          return;
        }
        setState({ kind: "authenticated", userId: result.userId });
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
  if (state.kind === "redirecting") {
    return (
      <main>
        <p data-testid="root-redirecting">Logged in. Opening your Session...</p>
      </main>
    );
  }

  return (
    <main>
      <h1>nquiry</h1>
      <p data-testid="root-logged-in">Logged in as {state.userId}.</p>
      <p>
        No default Session is configured for this local instance (set
        `NEXT_PUBLIC_DEFAULT_WORKSPACE_ID`/`NEXT_PUBLIC_DEFAULT_SESSION_ID`, see
        `docs/RUNTIME_OPERATION.md`).
      </p>
      <LogoutButton />
    </main>
  );
}
