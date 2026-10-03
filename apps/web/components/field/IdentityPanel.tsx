/**
 * CYAN_IDENTITY_PRESENTATION_CONSUMPTION_01: the identity / logout organism of the orientation rail, ONE composed
 * field: WHO (NQUIRY identity: displayName primary, canonicalEmail secondary) → HOW (signed in with) → THROUGH WHICH
 * PROVIDER (the account of the CURRENT provider method only) → LOGOUT EFFECT (the unchanged `LogoutButton`).
 * Everything comes from the one `identityProjectionFrom` composition; nothing is derived, defaulted or cached here.
 *
 * Fail closed: no identity presentation → "Authenticated" + the short technical id (a provider account is never the
 * identity); no method truth → no "Signed in with"; a linked-but-not-current provider is never named. No name,
 * avatar, initials, menu, settings or management: the orbital mark is ornamental.
 */
import { authenticationWords, type IdentityProjection as IdentityProjectionValue } from "../../lib/field/identityProjection";
import { LogoutButton } from "../LogoutButton";

function OrbitMark() {
  return (
    <span className="identity-panel-orbit" aria-hidden="true">
      <span className="identity-panel-ring" />
      <span className="identity-panel-ring identity-panel-ring-2" />
      <span className="identity-panel-nucleus" />
    </span>
  );
}

export function IdentityPanel({ projection }: { readonly projection: IdentityProjectionValue }) {
  if (projection.identity.kind !== "authenticated") return null;
  const { identity, authentication, providerAccount } = projection;
  const via = authentication.kind === "via";
  const account =
    via && authentication.label.kind === "provider" && providerAccount.kind === "email" && providerAccount.providerId === authentication.label.providerId
      ? { label: authentication.label.label, email: providerAccount.email }
      : null;
  const presented = identity.presentation.kind === "presented";
  return (
    <div className="identity-panel" data-testid="identity-panel" data-method-type={via ? authentication.methodType : undefined} data-identity={presented ? "presented" : "technical"}>
      <OrbitMark />
      <div className="identity-panel-body">
        {presented ? (
          <span className="identity-panel-who" data-testid="identity-panel-who">
            <span className="identity-panel-eyebrow">nquiry identity</span>
            <span className="identity-panel-name" data-testid="identity-panel-name">{identity.presentation.displayName}</span>
            <span className="identity-panel-email mono" data-testid="identity-panel-email">{identity.presentation.canonicalEmail}</span>
          </span>
        ) : (
          <span className="identity-panel-who" data-testid="identity-panel-who">
            <span className="identity-panel-eyebrow">Authenticated</span>
            <span className="identity-panel-method mono" data-testid="identity-panel-identity">
              {identity.userId.slice(0, 8)}…
            </span>
          </span>
        )}
        <span className="identity-panel-how">
          {via ? (
            <>
              <span className="identity-panel-eyebrow">Signed in with</span>
              <span className="identity-panel-method" data-testid="identity-panel-method" data-label-kind={authentication.label.kind}>
                {authenticationWords(authentication.label)}
              </span>
            </>
          ) : presented ? (
            <span className="identity-panel-eyebrow">Authenticated</span>
          ) : null}
          {account ? (
            <span className="identity-panel-account" data-testid="identity-panel-account">
              <span className="identity-panel-account-label">{account.label === null ? "Provider" : account.label} account</span>
              <span className="mono">{account.email}</span>
            </span>
          ) : null}
        </span>
      </div>
      <LogoutButton />
    </div>
  );
}
