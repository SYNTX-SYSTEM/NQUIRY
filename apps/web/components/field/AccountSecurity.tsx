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
import type { AccountSecurity as AccountSecurityValue } from "../../lib/field/accountSecurity";
import type { LinkBoundary } from "../../lib/field/linkBoundary";

export type AccountEffects = {
  readonly blocked: boolean;
  readonly onRemoveMethod: (methodId: string) => void;
  readonly onEndSession: (sessionId: string) => void;
  readonly onSignOutEverywhere: () => void;
};

function Moment({ value }: { readonly value: string }) {
  return (
    <time className="mono" dateTime={value}>
      {value.replace("T", " ").replace(/\.\d+/, "").replace(/\+00:00$|Z$/, " UTC")}
    </time>
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
