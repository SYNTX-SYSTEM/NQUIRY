"""The authentication provider runtime (24 §25.2–25.3, §27.1; WU-AUTH-07).

Settings (environment variables, read once at startup, same discipline as
`analysis_runtime`):

- `NQUIRY_ENVIRONMENT`: DEVELOPMENT / TEST / STAGING / PRODUCTION.
- `NQUIRY_AUTH_PROVIDER_MODE`: comma-separated provider ids to enable.
  `google` enables Google when `NQUIRY_GOOGLE_CLIENT_ID`,
  `NQUIRY_GOOGLE_CLIENT_SECRET` and `NQUIRY_GOOGLE_REDIRECT_URI` are all
  present (an incomplete configuration enables nothing and is reported as
  such); `test` enables the local test provider, in DEVELOPMENT / TEST only.
- `NQUIRY_ACCOUNT_CREATION_POLICY` (24 §11.14; default `DENIED`):
  `SELF_REGISTRATION_ALLOWED` in DEVELOPMENT / TEST only; the other policies
  are refused until their relations exist.
- `NQUIRY_GOOGLE_LINK_REDIRECT_URI` (optional): the ACCOUNT_LINK callback's
  registered URI; default is the login URI with `/link/callback`.
- `NQUIRY_EMAIL_DELIVERY_MODE` (24 §25.2 "email provider config"): `capture`
  enables the in-process local mail sink in DEVELOPMENT / TEST; unset means
  no delivery (verification / recovery unavailable); anything else is refused.
- `NQUIRY_RECOVERY_POLICY` (24 §17.7, §36 #11; default `DENIED`):
  `VERIFIED_EMAIL_SELF_SERVICE` in DEVELOPMENT / TEST only.
- `NQUIRY_PUBLIC_WEB_BASE_URL` (WU-AUTH-14): the browser-facing app origin when it
  differs from the API origin; local post-auth destinations are prefixed with it.
- `NQUIRY_PUBLIC_API_BASE_URL`: where a browser reaches this API (the test
  provider's authorize page and callback live under it); default
  `http://localhost:8000`.
- `NQUIRY_LOGIN_LOCKOUT_FAILURES` / `NQUIRY_LOGIN_LOCKOUT_MINUTES` (WU-AUTH-20,
  24 §21.16 / §36 #17): the CREDENTIAL-key lockout threshold and the window
  = lock duration; defaults 5 / 15 (`security.login_throttle`); the CLIENT
  key locks at ten times the failures. Positive integers, else refused.
- `NQUIRY_ACCOUNT_SECURITY_PATH` (CYAN_PRODUCTION_ROOT_CUTOVER, 2026-10-04):
  the deployed frontend's account-security location — the fallback target of
  an ACCOUNT_LINK projection when no legitimate `next` is known (link start
  without `next`; a link callback whose transaction cannot be bound). A local
  destination (`security/redirect_target`); default `/account/security` (the
  AUTH-line web). The product frontend (CYAN) presents links on `/workspaces`.

FAIL-CLOSED: unset mode means no external provider (login offers none);
`test` outside DEVELOPMENT / TEST raises `LocalProviderForbidden` at startup
(falsifier 41). Enabling Google in production is a human decision (24 §36
#1, #6); this module makes it possible, never default.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import timedelta

from security.account_creation import MATERIALIZED_POLICIES, AccountCreationPolicy
from security.events import Environment
from security.login_throttle import ThrottlePolicy
from security.mail import LocalMailCapture, MailSink
from security.oidc_provider import OidcProvider
from security.oidc_standard import google_provider
from security.oidc_test_issuer import LocalTestIssuer
from security.recovery import RecoveryPolicy
from security.redirect_target import is_legitimate_local_destination
from security.request_security import is_origin

_DEV_ENVIRONMENTS = frozenset({Environment.DEVELOPMENT, Environment.TEST})
_GOOGLE_VARIABLES = (
    "NQUIRY_GOOGLE_CLIENT_ID",
    "NQUIRY_GOOGLE_CLIENT_SECRET",
    "NQUIRY_GOOGLE_REDIRECT_URI",
)


class LocalProviderForbidden(RuntimeError):
    """The test provider was requested outside DEVELOPMENT / TEST."""


class UnknownAuthProvider(RuntimeError):
    """A provider id this runtime does not know; nothing is guessed."""


class AccountCreationPolicyForbidden(RuntimeError):
    """SELF_REGISTRATION_ALLOWED (PROVIDER_BOOTSTRAP) without a declared
    environment: the IDENTITY_CREATED provenance must name its environment
    (AC-11-017). Admitted in every declared environment since HD-AUTH-08
    (2026-10-04), which resolved HA-AUTH-01 for the generic bootstrap class."""


class AccountCreationPolicyNotMaterialized(RuntimeError):
    """A policy whose relation does not exist yet was configured."""


class MailDeliveryForbidden(RuntimeError):
    """The capture sink outside DEVELOPMENT / TEST (24 §25.3)."""


class RecoveryPolicyForbidden(RuntimeError):
    """VERIFIED_EMAIL_SELF_SERVICE outside DEVELOPMENT / TEST (24 §36 #11 undecided)."""


@dataclass(frozen=True)
class AuthRuntime:
    environment: Environment | None
    providers: Mapping[str, OidcProvider] = field(default_factory=dict)
    test_issuer: LocalTestIssuer | None = None
    incomplete: tuple[str, ...] = ()
    """Provider ids that were requested but not fully configured."""
    account_creation_policy: AccountCreationPolicy = AccountCreationPolicy.DENIED
    mail_sink: MailSink | None = None
    """None: no delivery configured, verification and recovery are unavailable
    (24 §36 #16 production delivery is a human decision)."""
    recovery_policy: RecoveryPolicy = RecoveryPolicy.DENIED
    login_throttle: ThrottlePolicy = field(default_factory=ThrottlePolicy)
    """WU-AUTH-20: the login lockout policy (24 §21.16); defaults are the
    fail-closed product policy, per-deployment overrides are a human choice (§36 #17)."""
    account_security_path: str = "/account/security"
    """The deployed frontend's account-security location: the fallback target
    of a link projection when no legitimate `next` is known. Frontend-owned
    fact, configured per deployment (`NQUIRY_ACCOUNT_SECURITY_PATH`)."""
    web_base_url: str | None = None
    """WU-AUTH-14: the browser-facing app's origin, prefixed to every local
    post-authentication destination (login projection, post-login target, link
    projection) when the API is served from another origin than the app (the
    local real stack). None: the app shares the API's origin (the deployment's
    `/api/` proxy) and destinations stay relative."""

    def provider(self, provider_id: str) -> OidcProvider | None:
        return self.providers.get(provider_id)


def auth_runtime_from_environment(
    env: Mapping[str, str] | None = None,
    *,
    test_issuer: LocalTestIssuer | None = None,
    mail_sink: MailSink | None = None,
) -> AuthRuntime:
    source = os.environ if env is None else env
    raw_environment = source.get("NQUIRY_ENVIRONMENT")
    try:
        environment = None if raw_environment is None else Environment(raw_environment)
    except ValueError:
        environment = None
    requested = [
        item.strip().lower()
        for item in source.get("NQUIRY_AUTH_PROVIDER_MODE", "").split(",")
        if item.strip()
    ]
    providers: dict[str, OidcProvider] = {}
    incomplete: list[str] = []
    issuer: LocalTestIssuer | None = None
    for provider_id in requested:
        if provider_id == "google":
            values = {name: source.get(name, "").strip() for name in _GOOGLE_VARIABLES}
            if all(values.values()):
                providers["google"] = google_provider(
                    client_id=values["NQUIRY_GOOGLE_CLIENT_ID"],
                    client_secret=values["NQUIRY_GOOGLE_CLIENT_SECRET"],
                    redirect_uri=values["NQUIRY_GOOGLE_REDIRECT_URI"],
                    link_redirect_uri=source.get("NQUIRY_GOOGLE_LINK_REDIRECT_URI", "").strip()
                    or None,
                )
            else:
                incomplete.append("google")
        elif provider_id == "test":
            if environment not in _DEV_ENVIRONMENTS:
                raise LocalProviderForbidden(
                    "the test provider is DEVELOPMENT / TEST only; refused for "
                    f"NQUIRY_ENVIRONMENT={raw_environment!r} (24 section 27.1)"
                )
            issuer = test_issuer or LocalTestIssuer.create(
                api_base_url=source.get("NQUIRY_PUBLIC_API_BASE_URL", "http://localhost:8000")
            )
            providers["test"] = issuer.provider()
        else:
            raise UnknownAuthProvider(f"unknown authentication provider {provider_id!r}")
    policy = AccountCreationPolicy(source.get("NQUIRY_ACCOUNT_CREATION_POLICY", "DENIED").strip())
    if policy not in MATERIALIZED_POLICIES:
        raise AccountCreationPolicyNotMaterialized(
            f"{policy.value} names a relation that is not materialized; nothing is substituted"
        )
    if policy is AccountCreationPolicy.SELF_REGISTRATION_ALLOWED and environment is None:
        # HD-AUTH-08: provider bootstrap is admitted in every DECLARED
        # environment; without one the creation provenance could not state
        # where the identity was created (AC-11-017), so nothing is admitted.
        raise AccountCreationPolicyForbidden(
            "SELF_REGISTRATION_ALLOWED needs a declared NQUIRY_ENVIRONMENT; "
            f"refused for NQUIRY_ENVIRONMENT={raw_environment!r}"
        )
    delivery_mode = source.get("NQUIRY_EMAIL_DELIVERY_MODE", "").strip().lower()
    sink: MailSink | None = None
    if delivery_mode == "capture":
        if environment not in _DEV_ENVIRONMENTS:
            raise MailDeliveryForbidden(
                "the capture mail sink is DEVELOPMENT / TEST only; refused for "
                f"NQUIRY_ENVIRONMENT={raw_environment!r} (24 section 25.3)"
            )
        sink = mail_sink or LocalMailCapture()
    elif delivery_mode:
        raise ValueError(
            f"unknown NQUIRY_EMAIL_DELIVERY_MODE {delivery_mode!r}: production delivery is a "
            "Human Authority decision (24 section 36 #16); nothing is substituted"
        )
    recovery_policy = RecoveryPolicy(source.get("NQUIRY_RECOVERY_POLICY", "DENIED").strip())
    if (
        recovery_policy is RecoveryPolicy.VERIFIED_EMAIL_SELF_SERVICE
        and environment not in _DEV_ENVIRONMENTS
    ):
        raise RecoveryPolicyForbidden(
            "VERIFIED_EMAIL_SELF_SERVICE is DEVELOPMENT / TEST only until 24 section 36 #11 is "
            f"decided; refused for NQUIRY_ENVIRONMENT={raw_environment!r}"
        )
    web_base_url = source.get("NQUIRY_PUBLIC_WEB_BASE_URL", "").strip() or None
    if web_base_url is not None and not is_origin(web_base_url):
        raise ValueError(
            f"NQUIRY_PUBLIC_WEB_BASE_URL={web_base_url!r} is not an explicit origin "
            "(scheme://host[:port], no path)"
        )
    account_security_path = (
        source.get("NQUIRY_ACCOUNT_SECURITY_PATH", "").strip() or "/account/security"
    )
    if not is_legitimate_local_destination(account_security_path):
        raise ValueError(
            f"NQUIRY_ACCOUNT_SECURITY_PATH={account_security_path!r} is not a local "
            "destination of the application (24 section 11.17)"
        )
    throttle = _throttle_policy(source)
    return AuthRuntime(
        environment=environment,
        providers=providers,
        test_issuer=issuer,
        incomplete=tuple(incomplete),
        account_creation_policy=policy,
        mail_sink=sink,
        recovery_policy=recovery_policy,
        login_throttle=throttle,
        account_security_path=account_security_path,
        web_base_url=web_base_url,
    )


def _throttle_policy(source: Mapping[str, str]) -> ThrottlePolicy:
    defaults = ThrottlePolicy()
    raw_failures = source.get("NQUIRY_LOGIN_LOCKOUT_FAILURES", "").strip()
    raw_minutes = source.get("NQUIRY_LOGIN_LOCKOUT_MINUTES", "").strip()
    try:
        failures = int(raw_failures) if raw_failures else defaults.credential_failures
        minutes = int(raw_minutes) if raw_minutes else None
        if failures < 1 or (minutes is not None and minutes < 1):
            raise ValueError
    except ValueError:
        raise ValueError(
            "NQUIRY_LOGIN_LOCKOUT_FAILURES / NQUIRY_LOGIN_LOCKOUT_MINUTES must be positive integers"
        ) from None
    if minutes is None:
        return ThrottlePolicy(credential_failures=failures)
    window = timedelta(minutes=minutes)
    return ThrottlePolicy(credential_failures=failures, window=window, lock=window)


__all__ = [
    "MailDeliveryForbidden",
    "RecoveryPolicyForbidden",
    "AccountCreationPolicyForbidden",
    "AccountCreationPolicyNotMaterialized",
    "AuthRuntime",
    "LocalProviderForbidden",
    "UnknownAuthProvider",
    "auth_runtime_from_environment",
]
