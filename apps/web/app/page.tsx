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
 * Landing target (F02 WU-02.10): a logged-in visitor always goes to
 * `/workspaces`, the governed entry point. The former optional redirect to
 * one seeded demo Session (`NEXT_PUBLIC_DEFAULT_WORKSPACE_ID`/
 * `NEXT_PUBLIC_DEFAULT_SESSION_ID`) was removed. That Session is a
 * NON_PROOF fixture, is no longer the landing page, and stays reachable
 * (and labelled) through its Workspace.
 */
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchCurrentSession } from "../lib/api/authClient";

type CheckState = { readonly kind: "checking" } | { readonly kind: "redirecting" };


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
        // F02 seeded-demo law: the entry point is the governed Workspace
        // list. The NON_PROOF demo Session is no longer the landing page
        // (it stays reachable, labelled, through its Workspace).
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
