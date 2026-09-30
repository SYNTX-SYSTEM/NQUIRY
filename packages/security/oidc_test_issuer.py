"""A local OIDC issuer for development and test (24 §25.3 "fake provider",
§27.1 TEST_PROVIDER; WU-AUTH-07).

It is a real issuer in every protocol respect the adapter depends on: it
signs RS256 ID Tokens with its own RSA key, serves that key as a JWKS, and
runs a token endpoint that checks the authorization code, the PKCE verifier
against the challenge it saw at authorization, the redirect URI and the
client credentials. It differs from a real provider in exactly one respect:
there is no human at the provider. `authorize` is the consent step, called by
a test or by the `/auth/test-provider/authorize` page of a development stack.

It is clearly marked TEST_PROVIDER, its issuer is a reserved local name, and
`application.auth_runtime` refuses to instantiate it outside DEVELOPMENT and
TEST (falsifier 41). It can produce no production proof.

The issuer is reachable only through `transport`, an in-process
`httpx.MockTransport`: no network. Tests may inject defects into the token
it issues, to prove the adapter's validation order.
"""

from __future__ import annotations

import json
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs

import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from security.oidc_standard import StandardOidcProvider
from security.oidc_transaction import derive_code_challenge

TEST_ISSUER = "https://test-provider.nquiry.local"
TEST_CLIENT_ID = "nquiry-test-client"
_TEST_CLIENT_SECRET = "test-provider-local-only"
_CODE_LIFETIME_SECONDS = 600


@dataclass(frozen=True, slots=True)
class ExchangeRecord:
    code: str
    code_verifier: str
    redirect_uri: str
    client_authenticated: bool


@dataclass(slots=True)
class _Authorization:
    nonce: str
    code_challenge: str
    redirect_uri: str
    subject: str
    email: str | None
    defect: str | None
    issued_at: float


@dataclass
class LocalTestIssuer:
    api_base_url: str
    _key: RSAPrivateKey
    _kid: str
    _other_key: RSAPrivateKey
    _authorizations: dict[str, _Authorization] = field(default_factory=dict)
    exchanges: list[ExchangeRecord] = field(default_factory=list)
    last_id_token: str = ""
    on_exchange: Callable[[ExchangeRecord], None] | None = None
    _fail_uncertainly: bool = False

    @classmethod
    def create(cls, *, api_base_url: str = "http://testserver") -> LocalTestIssuer:
        return cls(
            api_base_url=api_base_url.rstrip("/"),
            _key=rsa.generate_private_key(public_exponent=65537, key_size=2048),
            _kid=secrets.token_hex(8),
            _other_key=rsa.generate_private_key(public_exponent=65537, key_size=2048),
        )

    # --- metadata -------------------------------------------------------

    @property
    def issuer(self) -> str:
        return TEST_ISSUER

    @property
    def client_id(self) -> str:
        return TEST_CLIENT_ID

    @property
    def authorization_endpoint(self) -> str:
        return f"{self.api_base_url}/auth/test-provider/authorize"

    @property
    def redirect_uri(self) -> str:
        return f"{self.api_base_url}/auth/oidc/test/callback"

    @property
    def token_endpoint(self) -> str:
        return f"{TEST_ISSUER}/token"

    @property
    def jwks_uri(self) -> str:
        return f"{TEST_ISSUER}/jwks"

    @property
    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self._handle)

    def provider(self) -> StandardOidcProvider:
        """The SAME adapter class a Google configuration uses."""
        return StandardOidcProvider(
            provider_id="test",
            label="Test provider",
            proof_class="TEST_PROVIDER",
            issuer=TEST_ISSUER,
            accepted_issuers=frozenset({TEST_ISSUER}),
            client_id=TEST_CLIENT_ID,
            client_secret=_TEST_CLIENT_SECRET,
            redirect_uri=self.redirect_uri,
            authorization_endpoint=self.authorization_endpoint,
            token_endpoint=self.token_endpoint,
            jwks_uri=self.jwks_uri,
            http=httpx.Client(transport=self.transport),
        )

    # --- the consent step -----------------------------------------------

    def authorize(
        self,
        params: dict[str, str],
        *,
        subject: str,
        email: str | None = None,
        defect: str | None = None,
    ) -> str:
        """The provider-side authorization: the human (or the test) approves
        the request `params` (as sent by the adapter) for `subject`. Returns
        the authorization code the provider would send back."""
        if params.get("response_type") != "code" or params.get("code_challenge_method") != "S256":
            raise ValueError("the request is not Authorization Code + PKCE S256")
        if params.get("client_id") != TEST_CLIENT_ID:
            raise ValueError("unknown client")
        code = secrets.token_urlsafe(24)
        self._authorizations[code] = _Authorization(
            nonce=params["nonce"],
            code_challenge=params["code_challenge"],
            redirect_uri=params["redirect_uri"],
            subject=subject,
            email=email,
            defect=defect,
            issued_at=time.time(),
        )
        return code

    def fail_next_exchange_uncertainly(self) -> None:
        self._fail_uncertainly = True

    # --- the issuer's endpoints -----------------------------------------

    def _jwks(self) -> dict[str, Any]:
        public = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(self._key.public_key()))
        public.update({"kid": self._kid, "use": "sig", "alg": "RS256"})
        return {"keys": [public]}

    def _id_token(self, authorization: _Authorization) -> str:
        now = int(time.time())
        claims: dict[str, Any] = {
            "iss": TEST_ISSUER,
            "aud": TEST_CLIENT_ID,
            "sub": authorization.subject,
            "iat": now,
            "exp": now + 300,
            "nonce": authorization.nonce,
        }
        if authorization.email is not None:
            claims["email"] = authorization.email
            claims["email_verified"] = True
        key = self._key
        defect = authorization.defect
        if defect in ("wrong_signature", "wrong_signature_and_nonce"):
            key = self._other_key
        if defect in ("wrong_nonce", "wrong_signature_and_nonce"):
            claims["nonce"] = "not-the-nonce-of-this-transaction"
        if defect == "wrong_issuer":
            claims["iss"] = "https://another-issuer.nquiry.local"
        if defect == "wrong_audience":
            claims["aud"] = "another-client"
        if defect == "expired":
            claims["iat"] = now - 900
            claims["exp"] = now - 600
        if defect == "no_subject":
            del claims["sub"]
        token = jwt.encode(
            claims,
            key,  # type: ignore[arg-type]  # PyJWT accepts a cryptography private key
            algorithm="RS256",
            headers={"kid": self._kid},
        )
        self.last_id_token = token
        return token

    def _handle(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/jwks" and request.method == "GET":
            return httpx.Response(200, json=self._jwks())
        if request.url.path == "/token" and request.method == "POST":
            return self._token(request)
        return httpx.Response(404)

    def _token(self, request: httpx.Request) -> httpx.Response:
        form = {k: v[0] for k, v in parse_qs(request.content.decode("utf-8")).items()}
        record = ExchangeRecord(
            code=form.get("code", ""),
            code_verifier=form.get("code_verifier", ""),
            redirect_uri=form.get("redirect_uri", ""),
            client_authenticated=(
                form.get("client_id") == TEST_CLIENT_ID
                and form.get("client_secret") == _TEST_CLIENT_SECRET
            ),
        )
        self.exchanges.append(record)
        if self.on_exchange is not None:
            self.on_exchange(record)
        if self._fail_uncertainly:
            self._fail_uncertainly = False
            self._authorizations.pop(record.code, None)  # the code is spent at the provider
            raise httpx.ReadTimeout("the provider did not answer in time", request=request)
        authorization = self._authorizations.pop(record.code, None)  # codes are single use
        if (
            authorization is None
            or form.get("grant_type") != "authorization_code"
            or not record.client_authenticated
            or record.redirect_uri != authorization.redirect_uri
            or derive_code_challenge(record.code_verifier) != authorization.code_challenge
            or time.time() - authorization.issued_at > _CODE_LIFETIME_SECONDS
        ):
            return httpx.Response(400, json={"error": "invalid_grant"})
        return httpx.Response(
            200,
            json={
                "token_type": "Bearer",
                "id_token": self._id_token(authorization),
                "expires_in": 300,
            },
        )


__all__ = ["TEST_CLIENT_ID", "TEST_ISSUER", "ExchangeRecord", "LocalTestIssuer"]
