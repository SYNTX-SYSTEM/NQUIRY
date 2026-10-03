/**
 * CYAN_IDENTITY_PRESENTATION_CONSUMPTION_01: the "Identity and access" body chamber, the SAME composed field as the
 * rail organism: NQUIRY IDENTITY (displayName primary, canonicalEmail secondary) · TECHNICAL IDENTITY (the canonical
 * userId, inspection depth: a collapsed details element, copyable) · CURRENT AUTHENTICATION (local password, or the
 * server-owned provider label / raw provider id) carrying its provider account beneath it as one object · SESSION.
 * Each line only when its authoritative read produced it. No role, authority, membership, capability, avatar or
 * control. Without an identity presentation the chamber reads "Authenticated" and keeps the technical identity.
 */
import { authenticationWords, type IdentityProjection as IdentityProjectionValue } from "../../lib/field/identityProjection";
import { Identifiers } from "./chambers";

export function IdentityProjection({ projection }: { readonly projection: IdentityProjectionValue }) {
  if (projection.identity.kind !== "authenticated") return null;
  const { identity, session, authentication, providerAccount } = projection;
  const account =
    authentication.kind === "via" && authentication.label.kind === "provider" && providerAccount.kind === "email" && providerAccount.providerId === authentication.label.providerId
      ? { providerId: providerAccount.providerId, label: authentication.label.label, email: providerAccount.email }
      : null;
  const presented = identity.presentation.kind === "presented";
  return (
    <div className="identity-projection" data-testid="identity-projection" data-identity={presented ? "presented" : "technical"}>
      <dl className="auth-relation" data-testid="auth-relation">
        <div className="auth-line identity-who" data-testid="identity-who">
          <dt>nquiry identity</dt>
          <dd>
            {presented ? (
              <>
                <span className="identity-name" data-testid="identity-display-name">{identity.presentation.displayName}</span>
                <span className="identity-email mono" data-testid="identity-canonical-email">{identity.presentation.canonicalEmail}</span>
              </>
            ) : (
              <span className="identity-name" data-testid="identity-unpresented">Authenticated</span>
            )}
          </dd>
        </div>
        <div className="auth-line identity-technical" data-testid="identity-technical">
          <details open={!presented}>
            <summary>
              <dt>Technical identity</dt>
            </summary>
            <dd>
              <Identifiers items={[{ label: "Authenticated identity", value: identity.userId, testId: "identity-user-id" }]} />
            </dd>
          </details>
        </div>
        {authentication.kind === "via" ? (
          <div className="auth-line" data-testid="auth-method" data-method-type={authentication.methodType} data-method-status={authentication.status}>
            <dt>Current authentication</dt>
            <dd>
              <span className="auth-words" data-label-kind={authentication.label.kind} data-provider-id={authentication.label.kind === "provider" ? authentication.label.providerId : undefined}>
                {authenticationWords(authentication.label)}
              </span>
              {account ? (
                <span className="auth-account" data-testid="auth-provider-account" data-provider-id={account.providerId}>
                  <span className="auth-account-label">{account.label === null ? "Provider" : account.label} account</span>
                  <span className="mono auth-account-email">{account.email}</span>
                  <span className="auth-note">a provider-method attribute · not your nquiry identity</span>
                </span>
              ) : null}
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
    </div>
  );
}
