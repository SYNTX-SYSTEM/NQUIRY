"use client";

/**
 * Local-login field (`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`).
 *
 * A real email/password form, calling the real `POST /auth/login`
 * route (`lib/api/authClient.ts::login`). No client-side authority
 * decision is made here -- this form either successfully establishes a
 * real, server-verified session (redirect to `/`, which re-checks and
 * routes onward) or shows the server's own `denied` response;
 * `login`'s own fail-closed parsing means a malformed/unexpected server
 * response surfaces as a generic error too, never a silent success.
 */
import { type FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "../../lib/api/authClient";

type SubmitState = { readonly kind: "idle" } | { readonly kind: "submitting" } | { readonly kind: "error"; readonly message: string };

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [state, setState] = useState<SubmitState>({ kind: "idle" });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState({ kind: "submitting" });
    login(email, password)
      .then((result) => {
        if (result.kind === "ok") {
          router.replace("/");
          return;
        }
        setState({ kind: "error", message: "Incorrect email or password." });
      })
      .catch(() => {
        setState({ kind: "error", message: "Unable to reach the server. Please try again." });
      });
  }

  const submitting = state.kind === "submitting";

  return (
    <main>
      <h1>Log in to nquiry</h1>
      <form onSubmit={handleSubmit} data-testid="login-form">
        <div>
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            data-testid="login-email"
            type="email"
            autoComplete="username"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>
        <div>
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            data-testid="login-password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>
        <button type="submit" data-testid="login-submit" disabled={submitting}>
          {submitting ? "Logging in..." : "Log in"}
        </button>
      </form>
      {state.kind === "error" ? (
        <p role="alert" data-testid="login-error">
          {state.message}
        </p>
      ) : null}
    </main>
  );
}
