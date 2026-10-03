/**
 * AUTH/CYAN-IDENTITY-01 (Human Review delta): the identity / logout panel of the orientation rail. A living relation
 * attached to the Field, not a menu: IDENTITY → AUTH METHOD → PROVIDER ATTRIBUTE → LOGOUT EFFECT, in the organism's
 * own surface, glow and type. Everything shown comes from the ONE proven projection (`identityProjectionFrom`); the
 * exit is the existing `LogoutButton` (the legitimate effect on the identity relation), unchanged.
 *
 * Fail closed: no method truth → "Authenticated" + the short canonical id, never "Signed in with …"; a provider
 * email only beside the provider method that is the CURRENT authentication; a linked-but-not-current provider is
 * never named. No name, avatar, initials, menu, settings or management: the orbital mark is ornamental.
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
  const { authentication, providerAccount } = projection;
  const via = authentication.kind === "via";
  const account =
    via && authentication.label.kind === "provider" && providerAccount.kind === "email" && providerAccount.providerId === authentication.label.providerId
      ? { label: authentication.label.label, email: providerAccount.email }
      : null;
  return (
    <div className="identity-panel" data-testid="identity-panel" data-method-type={via ? authentication.methodType : undefined}>
      <OrbitMark />
      <div className="identity-panel-body">
        <span className="identity-panel-eyebrow">{via ? "Signed in with" : "Authenticated"}</span>
        {via ? (
          <span className="identity-panel-method" data-testid="identity-panel-method" data-label-kind={authentication.label.kind}>
            {authenticationWords(authentication.label)}
          </span>
        ) : (
          <span className="identity-panel-method mono" data-testid="identity-panel-identity">
            {projection.identity.userId.slice(0, 8)}…
          </span>
        )}
        {account ? (
          <span className="identity-panel-account" data-testid="identity-panel-account">
            <span className="identity-panel-account-label">{account.label === null ? "Provider" : account.label} account</span>
            <span className="mono">{account.email}</span>
          </span>
        ) : null}
      </div>
      <LogoutButton />
    </div>
  );
}
