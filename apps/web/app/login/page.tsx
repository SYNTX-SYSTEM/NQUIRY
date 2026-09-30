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
 *
 * WU-AUTH-07 (24 §24.2, §24.6): provider buttons appear only for providers
 * the server reports as configured (`GET /auth/providers`); each is a plain
 * navigation to the API's start contact. A provider callback that did not end
 * in a session sends the browser back here with `?auth=<projection>`, shown
 * as a safe message; the code itself is never rendered.
 */
import { type FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  authProjectionMessage,
  listProviders,
  login,
  providerStartUrl,
  type ProviderSummary,
} from "../../lib/api/authClient";

type SubmitState = { readonly kind: "idle" } | { readonly kind: "submitting" } | { readonly kind: "error"; readonly message: string };

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [state, setState] = useState<SubmitState>({ kind: "idle" });
  const [providers, setProviders] = useState<readonly ProviderSummary[]>([]);
  const [projection, setProjection] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    // The projection code arrives in the URL from the API's callback redirect.
    Promise.resolve(new URLSearchParams(window.location.search).get("auth")).then((code) => {
      if (!cancelled) {
        setProjection(authProjectionMessage(code));
      }
    });
    listProviders()
      .then((result) => {
        if (!cancelled) {
          setProviders(result.providers);
        }
      })
      .catch(() => {
        // No provider list means no provider button (24 §24.2).
      });
    return () => {
      cancelled = true;
    };
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState({ kind: "submitting" });
    login(email, password)
      .then((result) => {
        if (result.kind === "ok") {
          router.replace("/");
          return;
        }
        // F02 WU-02.12 (FBR-C): a malformed request is not a credential denial.
        setState({
          kind: "error",
          message:
            result.kind === "rejected"
              ? "The login request was invalid. Please enter an email and a password."
              : "Incorrect email or password.",
        });
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
      {projection ? (
        <p role="alert" data-testid="auth-projection">
          {projection}
        </p>
      ) : null}
      {providers.length > 0 ? (
        <section aria-labelledby="providers-heading" data-testid="provider-logins">
          <h2 id="providers-heading">Or sign in with</h2>
          <ul>
            {providers.map((provider) => (
              <li key={provider.providerId}>
                <a
                  className="button secondary"
                  data-testid={`provider-${provider.providerId}`}
                  href={providerStartUrl(provider.providerId, "/")}
                >
                  {provider.label}
                  {provider.proofClass === "TEST_PROVIDER" ? " (TEST_PROVIDER, not production)" : ""}
                </a>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </main>
  );
}
