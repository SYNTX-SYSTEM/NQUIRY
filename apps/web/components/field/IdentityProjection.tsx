/**
 * AUTH/CYAN-IDENTITY-01: the current authentication relation inside the existing "Identity and access" proof
 * chamber. Four lines at most, each present only when its authoritative read legitimately produced it:
 * Authenticated identity (the canonical id, a token) · Current authentication (local password, or the server-owned
 * provider label / raw provider id) · Provider account (a provider-method attribute, said so in words) · Session
 * (current · authenticated, with the canonical instants as data). No role, authority, membership, capability, name,
 * avatar or control. The human-facing NQUIRY display name is NOT_MATERIALIZED.
 */
import { authenticationWords, type IdentityProjection as IdentityProjectionValue } from "../../lib/field/identityProjection";
import { Identifiers } from "./chambers";

export function IdentityProjection({ projection }: { readonly projection: IdentityProjectionValue }) {
  if (projection.identity.kind !== "authenticated") return null;
  const { session, authentication, providerAccount } = projection;
  return (
    <div className="identity-projection" data-testid="identity-projection">
      <Identifiers items={[{ label: "Authenticated identity", value: projection.identity.userId, testId: "identity-user-id" }]} />
      {authentication.kind === "via" || providerAccount.kind === "email" || session.kind === "current" ? (
        <dl className="auth-relation" data-testid="auth-relation">
          {authentication.kind === "via" ? (
            <div className="auth-line" data-testid="auth-method" data-method-type={authentication.methodType} data-method-status={authentication.status}>
              <dt>Current authentication</dt>
              <dd>
                <span className="auth-words" data-label-kind={authentication.label.kind} data-provider-id={authentication.label.kind === "provider" ? authentication.label.providerId : undefined}>
                  {authenticationWords(authentication.label)}
                </span>
              </dd>
            </div>
          ) : null}
          {providerAccount.kind === "email" ? (
            <div className="auth-line" data-testid="auth-provider-account" data-provider-id={providerAccount.providerId}>
              <dt>Provider account</dt>
              <dd>
                <span className="mono">{providerAccount.email}</span>
                <span className="auth-note"> · an attribute of the provider method, not your nquiry identity</span>
              </dd>
            </div>
          ) : null}
          {session.kind === "current" ? (
            <div className="auth-line" data-testid="auth-session" data-session-id={session.sessionId} data-issued-at={session.issuedAt} data-expires-at={session.expiresAt}>
              <dt>Session</dt>
              <dd>current · authenticated</dd>
            </div>
          ) : null}
        </dl>
      ) : null}
    </div>
  );
}
