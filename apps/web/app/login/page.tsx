"use client";

/**
 * Access Field (22 §21): the Core before identity exists.
 *
 * Local-login field (`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`): a
 * real email/password form calling the real `POST /auth/login`
 * (`lib/api/authClient.ts::login`). No client-side authority decision is made
 * here; the form either establishes a real, server-verified session (redirect to
 * `/`, which re-checks and routes onward) or shows the server's own verdict.
 * `login`'s fail-closed parsing means a malformed/unexpected server response
 * surfaces as a boundary too, never a silent success.
 *
 * Field position: a single centred identity core in a dark, quiet field with
 * no workspace topology (22 §21.3, §21.11). Pending is a request, never an
 * access claim (22 §21.12); failure is a boundary (`role=alert`, associated
 * with the form), never success motion. External providers are NOT established
 * by the repository and therefore not shown (22 §45.1). Submit and retry stay
 * reachable in every mode (22 §21.13–§21.14).
 */
import { type FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { FieldBackground } from "../../components/field/FieldBackground";
import { Identity } from "../../components/field/Identity";
import { login } from "../../lib/api/authClient";

type SubmitState =
  | { readonly kind: "idle" }
  | { readonly kind: "submitting" }
  | { readonly kind: "error"; readonly boundary: "rejected" | "denied" | "network_failure"; readonly message: string };

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [state, setState] = useState<SubmitState>({ kind: "idle" });
  // SF-05 (doc 26 §28): attention and focus are projection-local (HOVER != STATE, FOCUS != STATE): the field
  // gathers around the Login action on hover and the local chamber responds to focus; nothing implies success
  const [attract, setAttract] = useState(false);
  const [focus, setFocus] = useState<"email" | "password" | null>(null);

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
        setState(
          result.kind === "rejected"
            ? { kind: "error", boundary: "rejected", message: "The login request was invalid. Please enter an email and a password." }
            : { kind: "error", boundary: "denied", message: "Incorrect email or password." },
        );
      })
      .catch(() => {
        setState({ kind: "error", boundary: "network_failure", message: "The canonical system could not be reached. No access relation was established." });
      });
  }

  const submitting = state.kind === "submitting";

  return (
    <>
      <FieldBackground regime="access" />
      <header className="access-rail">
        <Identity link={false} />
      </header>
      <main className="access-field" data-field-regime="access" data-attract={attract ? "login" : undefined} data-focus={focus ?? undefined}>
        <section className="access-core" aria-labelledby="access-title" data-testid="access-core" data-core-state={submitting ? "loading" : state.kind === "error" ? "boundary" : "current"}>
          <span className="access-membrane" aria-hidden="true" />
          <p className="eyebrow">Access</p>
          <h1 id="access-title">Log in to nquiry</h1>
          <p className="lede">Identity opens the Field. It grants no Workspace, Challenge or Session authority by itself.</p>
          <form onSubmit={handleSubmit} data-testid="login-form" aria-describedby={state.kind === "error" ? "login-error" : undefined}>
            <div className="field">
              <label htmlFor="login-email">Email</label>
              <input
                id="login-email"
                data-testid="login-email"
                type="email"
                autoComplete="username"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                onFocus={() => setFocus("email")}
                onBlur={() => setFocus(null)}
              />
            </div>
            <div className="field">
              <label htmlFor="login-password">Password</label>
              <input
                id="login-password"
                data-testid="login-password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                onFocus={() => setFocus("password")}
                onBlur={() => setFocus(null)}
              />
            </div>
            <div className="actions-row">
              <button
                className="button access-action"
                type="submit"
                data-testid="login-submit"
                disabled={submitting}
                onMouseEnter={() => setAttract(true)}
                onMouseLeave={() => setAttract(false)}
                onFocus={() => setAttract(true)}
                onBlur={() => setAttract(false)}
              >
                Log in
              </button>
            </div>
          </form>
          {submitting ? (
            <p className="access-status effect-intent" role="status" data-testid="login-pending">
              Requested. Not yet authenticated: the server verifies the credentials.
            </p>
          ) : null}
          {state.kind === "error" ? (
            <p role="alert" id="login-error" data-testid="login-error" className="read-boundary" data-outcome={state.boundary}>
              <span className="t-boundary">{state.message}</span>
            </p>
          ) : null}
        </section>
      </main>
    </>
  );
}
