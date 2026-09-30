"""A standards-based OIDC Authorization Code + PKCE provider adapter
(24 §11.1, §11.12, §26.2; WU-AUTH-07).

One class serves every provider: Google is an instance with Google's static
metadata (`google_provider`), the local test issuer is an instance pointed at
an in-process transport. Protocol mechanics that a maintained library owns
are delegated to it (24 §11.12 "Do not hand-roll token validation"): PyJWT
verifies the signature against the provider's JWKS and the `aud` / `exp` /
`iat` claims; this module checks the issuer against the provider's accepted
issuer set, then, and only then, the nonce against the transaction, and
extracts the subject.

Client authentication at the token endpoint is `client_secret_post`. The
adapter keeps no provider access or refresh token (24 §11.20).
"""

from __future__ import annotations

import json
from urllib.parse import urlencode

import httpx
import jwt

from security.oidc_provider import (
    IdTokenInvalid,
    ProviderExchangeRejected,
    ProviderExchangeUncertain,
    VerifiedProviderCredential,
)
from security.oidc_transaction import OidcFailureReason, hash_protocol_value

GOOGLE_ISSUER = "https://accounts.google.com"
_GOOGLE_ACCEPTED_ISSUERS = frozenset({GOOGLE_ISSUER, "accounts.google.com"})
_GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
_GOOGLE_JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
_SCOPE = "openid email profile"
_TIMEOUT_SECONDS = 10.0
_REQUIRED_CLAIMS = ("iss", "aud", "exp", "iat")
# OAuth 2.0 / OIDC error codes that mean the user did not authorize.
_USER_DENIAL_ERRORS = frozenset({"access_denied", "consent_required", "login_required"})


class StandardOidcProvider:
    def __init__(
        self,
        *,
        provider_id: str,
        label: str,
        proof_class: str,
        issuer: str,
        accepted_issuers: frozenset[str],
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        authorization_endpoint: str,
        token_endpoint: str,
        jwks_uri: str,
        http: httpx.Client,
    ) -> None:
        self._provider_id = provider_id
        self._label = label
        self._proof_class = proof_class
        self._issuer = issuer
        self._accepted_issuers = accepted_issuers
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._authorization_endpoint = authorization_endpoint
        self._token_endpoint = token_endpoint
        self._jwks_uri = jwks_uri
        self._http = http
        self._jwks: dict[str, jwt.PyJWK] = {}

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def label(self) -> str:
        return self._label

    @property
    def proof_class(self) -> str:
        return self._proof_class

    @property
    def issuer(self) -> str:
        return self._issuer

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    @property
    def authorization_endpoint(self) -> str:
        return self._authorization_endpoint

    def authorization_url(self, *, state: str, nonce: str, code_challenge: str) -> str:
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self._client_id,
                "redirect_uri": self._redirect_uri,
                "scope": _SCOPE,
                "state": state,
                "nonce": nonce,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }
        )
        return f"{self._authorization_endpoint}?{query}"

    def exchange_code(self, *, code: str, code_verifier: str) -> str:
        try:
            response = self._http.post(
                self._token_endpoint,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self._redirect_uri,
                    "code_verifier": code_verifier,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
                headers={"Accept": "application/json"},
                timeout=_TIMEOUT_SECONDS,
            )
        except httpx.HTTPError as exc:
            raise ProviderExchangeUncertain(type(exc).__name__) from exc
        if response.status_code != 200:
            raise ProviderExchangeRejected(str(response.status_code))
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderExchangeUncertain("malformed token response") from exc
        raw = body.get("id_token") if isinstance(body, dict) else None
        if not isinstance(raw, str) or not raw:
            raise ProviderExchangeRejected("no id_token")
        return raw

    def _key_for(self, raw_id_token: str) -> jwt.PyJWK:
        try:
            header = jwt.get_unverified_header(raw_id_token)
        except jwt.PyJWTError as exc:
            raise IdTokenInvalid(OidcFailureReason.INVALID_ID_TOKEN_SIGNATURE) from exc
        kid = header.get("kid")
        if not isinstance(kid, str):
            raise IdTokenInvalid(OidcFailureReason.INVALID_ID_TOKEN_SIGNATURE)
        if kid not in self._jwks:
            self._jwks = self._fetch_jwks()
        key = self._jwks.get(kid)
        if key is None:
            raise IdTokenInvalid(OidcFailureReason.INVALID_ID_TOKEN_SIGNATURE)
        return key

    def _fetch_jwks(self) -> dict[str, jwt.PyJWK]:
        try:
            response = self._http.get(self._jwks_uri, timeout=_TIMEOUT_SECONDS)
            response.raise_for_status()
            document = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise IdTokenInvalid(OidcFailureReason.PROVIDER_FAILURE) from exc
        keys: dict[str, jwt.PyJWK] = {}
        for entry in document.get("keys", []) if isinstance(document, dict) else []:
            if isinstance(entry, dict) and isinstance(entry.get("kid"), str):
                keys[entry["kid"]] = jwt.PyJWK(entry)
        return keys

    def validate_id_token(
        self, raw_id_token: str, *, expected_nonce_hash: str
    ) -> VerifiedProviderCredential:
        key = self._key_for(raw_id_token)
        try:
            claims = jwt.decode(
                raw_id_token,
                key.key,
                algorithms=["RS256"],
                audience=self._client_id,
                options={"require": list(_REQUIRED_CLAIMS), "verify_iss": False},
            )
        except jwt.ExpiredSignatureError as exc:
            raise IdTokenInvalid(OidcFailureReason.EXPIRED_ID_TOKEN) from exc
        except jwt.InvalidAudienceError as exc:
            raise IdTokenInvalid(OidcFailureReason.INVALID_AUDIENCE) from exc
        except jwt.PyJWTError as exc:
            raise IdTokenInvalid(OidcFailureReason.INVALID_ID_TOKEN_SIGNATURE) from exc
        if claims.get("iss") not in self._accepted_issuers:
            raise IdTokenInvalid(OidcFailureReason.INVALID_ISSUER)
        # Only now is the token trusted; its nonce claim may be read (24 §11.12).
        nonce = claims.get("nonce")
        if not isinstance(nonce, str) or hash_protocol_value(nonce) != expected_nonce_hash:
            raise IdTokenInvalid(OidcFailureReason.INVALID_NONCE)
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise IdTokenInvalid(OidcFailureReason.PROVIDER_SUBJECT_MISSING)
        email = claims.get("email")
        name = claims.get("name")
        return VerifiedProviderCredential(
            provider_id=self._provider_id,
            issuer=self._issuer,
            subject=subject,
            email=email if isinstance(email, str) and email else None,
            email_verified=claims.get("email_verified") is True,
            display_name=name if isinstance(name, str) and name else None,
        )

    def normalize_error(self, error: str) -> OidcFailureReason:
        if error in _USER_DENIAL_ERRORS:
            return OidcFailureReason.USER_CANCEL
        return OidcFailureReason.PROVIDER_FAILURE


def google_provider(
    *, client_id: str, client_secret: str, redirect_uri: str, http: httpx.Client | None = None
) -> StandardOidcProvider:
    """Google with its static OIDC metadata (24 §26.2 "discovery/static
    metadata"): the endpoints are Google's published, stable ones."""
    return StandardOidcProvider(
        provider_id="google",
        label="Google",
        proof_class="PRODUCTION_PROVIDER",
        issuer=GOOGLE_ISSUER,
        accepted_issuers=_GOOGLE_ACCEPTED_ISSUERS,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        authorization_endpoint=_GOOGLE_AUTHORIZATION_ENDPOINT,
        token_endpoint=_GOOGLE_TOKEN_ENDPOINT,
        jwks_uri=_GOOGLE_JWKS_URI,
        http=http or httpx.Client(),
    )


def jwks_document(keys: list[dict[str, object]]) -> str:
    """Renders a JWKS document (used by the local test issuer)."""
    return json.dumps({"keys": keys})


__all__ = [
    "GOOGLE_ISSUER",
    "StandardOidcProvider",
    "google_provider",
    "jwks_document",
]
