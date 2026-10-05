/**
 * AUTH/CYAN-ACCOUNT-01: the "Access security" action chamber of the Workspaces field — 24 §24.5's target UI
 * contacts over the ONE composed account-security field (`accountSecurityFrom`, the same reads as the identity
 * organisms): SIGN-IN METHODS (each ACTIVE method with its provider account; Remove while another remains; the
 * link offer for a configured provider not yet held) · SESSIONS (each session; End for every session but the
 * current one, which is ended through Log out) · SIGN OUT EVERYWHERE.
 *
 * Every control names an existing PURPLE effect and nothing else; the words of a refused effect are the server's
 * reason code on the page's effect surface, never a local verdict. A link is a form the browser submits (the API
 * answers with a redirect to the provider) and its result returns as the `?link=` boundary rendered here. No
 * recovery, verification or registration control: those contacts answer `unavailable` on the live producer.
 * The chamber is pure render: the page owns the effect field and the re-read.
 */
import { type FormEvent, useState } from "react";
import type { AccountSecurity as AccountSecurityValue } from "../../lib/field/accountSecurity";
import type { LinkBoundary } from "../../lib/field/linkBoundary";

export type AccountEffects = {
  readonly blocked: boolean;
  readonly onRemoveMethod: (methodId: string) => void;
  readonly onEndSession: (sessionId: string) => void;
  readonly onSignOutEverywhere: () => void;
  /** WU-AUTH-19: current and new password as typed; the page sends them and clears the form on commit. */
  readonly onChangePassword: (currentPassword: string, newPassword: string) => void;
  /** AUTH/CYAN-RECOVERY-01: a verification message for the canonical address. */
  readonly onSendVerification: (email: string) => void;
};

function Moment({ value }: { readonly value: string }) {
  return (
    <time className="mono" dateTime={value}>
      {value.replace("T", " ").replace(/\.\d+/, "").replace(/\+00:00$|Z$/, " UTC")}
    </time>
  );
}

/**
 * WU-AUTH-19: the local password is replaced by its owner after proving the current one (ROTATION != RECOVERY).
 * The confirmation is the only local check (two typed values must agree); every other verdict is the server's
 * (current password, password rules, other sessions ended). Nothing is kept after a commit.
 */
function PasswordRotation({ blocked, onChangePassword }: { readonly blocked: boolean; readonly onChangePassword: (current: string, next: string) => void }) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const mismatch = confirm.length > 0 && next !== confirm;
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (next !== confirm) return;
    onChangePassword(current, next);
    setCurrent("");
    setNext("");
    setConfirm("");
  }
  return (
    <section className="account-section" aria-labelledby="account-password-title" data-testid="account-password">
      <h3 id="account-password-title" className="account-section-title">
        Password
      </h3>
      <form onSubmit={submit} className="account-password-form" data-testid="account-password-form" autoComplete="off">
        <div className="field">
          <label htmlFor="account-current-password">Current password</label>
          <input id="account-current-password" data-testid="account-current-password" type="password" autoComplete="current-password" required value={current} onChange={(e) => setCurrent(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="account-new-password">New password</label>
          <input id="account-new-password" data-testid="account-new-password" type="password" autoComplete="new-password" required minLength={1} value={next} onChange={(e) => setNext(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="account-confirm-password">New password again</label>
          <input id="account-confirm-password" data-testid="account-confirm-password" type="password" autoComplete="new-password" required aria-invalid={mismatch || undefined} value={confirm} onChange={(e) => setConfirm(e.target.value)} />
          {mismatch ? (
            <span className="auth-note" role="alert" data-testid="account-password-mismatch">
              the two new passwords differ · nothing was sent
            </span>
          ) : null}
        </div>
        <div className="actions-row">
          <button type="submit" className="button secondary" data-testid="account-password-submit" disabled={blocked || mismatch || !current || !next || !confirm}>
            Change password
          </button>
          <span className="auth-note">your other sessions end · this one continues</span>
        </div>
      </form>
    </section>
  );
}

export function AccountSecurity({ security, link, effects }: { readonly security: AccountSecurityValue; readonly link: LinkBoundary; readonly effects: AccountEffects }) {
  const { methods, sessions, links } = security;
  const others = sessions.filter((s) => !s.current);
  return (
    <div className="account-security" data-testid="account-security">
      {link.kind === "result" ? (
        <p className="account-link-result t-boundary" role={link.settled === "committed" ? "status" : "alert"} data-testid="link-result" data-projection={link.projection} data-settled={link.settled}>
          {link.message}
        </p>
      ) : null}

      <section className="account-section" aria-labelledby="account-methods-title" data-testid="account-methods">
        <h3 id="account-methods-title" className="account-section-title">
          Sign-in methods
        </h3>
        {methods.length === 0 ? (
          <p className="muted" data-testid="account-methods-unknown">
            Your sign-in methods could not be read. Nothing is shown as current.
          </p>
        ) : (
          <ul className="account-list" data-testid="account-method-list">
            {methods.map((m) => (
              <li key={m.methodId} className="account-item" data-testid="account-method" data-method-id={m.methodId} data-method-type={m.methodType} data-current={m.current ? "true" : undefined}>
                <div className="account-item-body">
                  <span className="account-item-words" data-label-kind={m.label.kind}>
                    {m.words}
                    {m.current ? <span className="account-current"> · current session</span> : null}
                  </span>
                  {m.providerEmail !== null ? (
                    <span className="account-item-account mono" data-testid="account-method-email">
                      {m.providerEmail}
                    </span>
                  ) : null}
                  {m.lastAuthenticatedAt !== null ? (
                    <span className="auth-note" data-testid="account-method-last-used">
                      last used <Moment value={m.lastAuthenticatedAt} />
                    </span>
                  ) : null}
                  {!m.removable ? (
                    <span className="auth-note" data-testid="account-method-last">
                      your only sign-in method · it cannot be removed (24 §14.6)
                    </span>
                  ) : null}
                </div>
                {m.removable ? (
                  <button type="button" className="button secondary account-remove" data-testid="account-method-remove" disabled={effects.blocked} onClick={() => effects.onRemoveMethod(m.methodId)}>
                    Remove
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        )}
        {links.map((offer) => (
          <form key={offer.provider.providerId} method={offer.action.method} action={offer.action.action} className="account-link" data-testid="account-link-form" data-provider-id={offer.provider.providerId} data-proof-class={offer.provider.proofClass}>
            <button type="submit" className="button secondary" data-testid={`account-link-${offer.provider.providerId}`} disabled={effects.blocked}>
              Add {offer.provider.label}
              {offer.provider.proofClass !== "PRODUCTION_PROVIDER" ? <span className="access-provider-class"> · test provider</span> : null}
            </button>
            <span className="auth-note">links a {offer.provider.label} account to this nquiry identity · it creates no account and no access</span>
          </form>
        ))}
      </section>

      {security.verification.kind === "relation" ? (
        <section className="account-section" aria-labelledby="account-email-title" data-testid="account-email" data-verified={security.verification.verified ? "true" : "false"}>
          <h3 id="account-email-title" className="account-section-title">
            E-mail
          </h3>
          <div className="account-item">
            <div className="account-item-body">
              <span className="account-item-words mono" data-testid="account-email-address">
                {security.verification.canonicalEmail}
              </span>
              {security.verification.verified ? (
                <span className="auth-note" data-testid="account-email-verified">
                  verified{security.verification.verifiedAt ? <> · <Moment value={security.verification.verifiedAt} /></> : null}
                  {security.verification.recoveryOffered ? " · it can recover your password" : null}
                </span>
              ) : (
                <span className="auth-note" data-testid="account-email-unverified">
                  not verified{security.verification.recoveryOffered ? " · a lost password can only be recovered through a verified address" : null}
                </span>
              )}
            </div>
            {!security.verification.verified ? (
              <button type="button" className="button secondary" data-testid="account-email-verify" disabled={effects.blocked} onClick={() => effects.onSendVerification((security.verification as { canonicalEmail: string }).canonicalEmail)}>
                Send verification e-mail
              </button>
            ) : null}
          </div>
        </section>
      ) : null}

      {security.rotatable ? <PasswordRotation blocked={effects.blocked} onChangePassword={effects.onChangePassword} /> : null}

      <section className="account-section" aria-labelledby="account-sessions-title" data-testid="account-sessions">
        <h3 id="account-sessions-title" className="account-section-title">
          Sessions
        </h3>
        {sessions.length === 0 ? (
          <p className="muted" data-testid="account-sessions-unknown">
            Your sessions could not be read. Nothing is shown as current.
          </p>
        ) : (
          <ul className="account-list" data-testid="account-session-list">
            {sessions.map((s) => (
              <li key={s.sessionId} className="account-item" data-testid="account-session" data-session-id={s.sessionId} data-current={s.current ? "true" : undefined}>
                <div className="account-item-body">
                  <span className="account-item-words">
                    {s.current ? "This session" : "Another session"}
                    {s.words !== null ? <span className="muted"> · {s.words}</span> : null}
                  </span>
                  <span className="auth-note">
                    since <Moment value={s.issuedAt} /> · until <Moment value={s.expiresAt} />
                  </span>
                </div>
                {s.current ? (
                  <span className="auth-note" data-testid="account-session-current">
                    ended by Log out
                  </span>
                ) : (
                  <button type="button" className="button secondary account-end" data-testid="account-session-end" disabled={effects.blocked} onClick={() => effects.onEndSession(s.sessionId)}>
                    End
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
        {sessions.length > 0 ? (
          <div className="actions-row account-sign-out-all">
            <button type="button" className="button secondary" data-testid="account-sign-out-everywhere" disabled={effects.blocked} onClick={effects.onSignOutEverywhere}>
              Sign out everywhere
            </button>
            <span className="auth-note">{others.length === 0 ? "ends this session" : `ends this session and ${others.length} other${others.length === 1 ? "" : "s"}`}</span>
          </div>
        ) : null}
      </section>
    </div>
  );
}
