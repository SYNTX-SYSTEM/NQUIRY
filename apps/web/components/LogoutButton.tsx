"use client";

/**
 * Local-login field (`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`).
 *
 * A minimal, reusable logout control -- the Session-view route
 * (`app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx`) has no
 * other reachable path back to `/login` once a visitor has been
 * redirected straight there from `/` (`NEXT_PUBLIC_DEFAULT_WORKSPACE_ID`/
 * `NEXT_PUBLIC_DEFAULT_SESSION_ID`). Calls the real `POST /auth/logout`
 * route, then navigates to `/login` -- never assumes success locally
 * without awaiting the real response.
 */
import { useRouter } from "next/navigation";
import { logout } from "../lib/api/authClient";

export function LogoutButton() {
  const router = useRouter();

  return (
    <button
      type="button"
      className="button secondary"
      data-testid="logout-button"
      onClick={() => {
        logout().then(() => router.replace("/login"));
      }}
    >
      Log out
    </button>
  );
}
