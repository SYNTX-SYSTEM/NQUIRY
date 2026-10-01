"""Anti-CSRF boundary of the HTTP surface (24 §21.6–21.9; WU-AUTH-14).

`guard_request` is the one decision the HTTP adapter's middleware asks before
any unsafe request reaches a route: `None` to proceed, or the (status, body)
of the boundary failure. It runs before body parsing, before session
resolution and before any application module (24 §21.7 "EXPLICIT ANTI-CSRF
VALIDATION → APPLICATION REQUEST"; §21.6 "LOGIN-CSRF BOUNDARY → CREDENTIAL
VALIDATION").

Two refusal classes, by design distinct (24 §21.6 "APPLICATION
AUTHENTICATED-CSRF BOUNDARY != LOCAL LOGIN-CSRF BOUNDARY"):
- `CSRF_REJECTED` for any unsafe request whose browser metadata does not
  attest an allowed or the API's own origin;
- `LOGIN_CSRF_REJECTED` for `POST /auth/login` when that same metadata fails
  OR the request is not `application/json` (the form-shaped submission a
  hostile page can produce).

Configuration: `NQUIRY_ALLOWED_ORIGINS` (comma-separated, explicit; default
`http://localhost:3000`). The same list pins CORS (`main.py`). A wildcard
refuses startup.
"""

from __future__ import annotations

from collections.abc import Mapping

from security.request_security import (
    LOGIN_CONTACT,
    RequestSecurityPolicy,
    Verdict,
    evaluate_unsafe_request,
    is_unsafe_method,
    login_contract_satisfied,
    parse_allowed_origins,
)

CSRF_REJECTED: tuple[int, dict[str, object]] = (
    403,
    {"kind": "denied", "reasonCode": "CSRF_REJECTED"},
)
LOGIN_CSRF_REJECTED: tuple[int, dict[str, object]] = (
    403,
    {"kind": "denied", "reasonCode": "LOGIN_CSRF_REJECTED"},
)


def request_security_from_environment(source: Mapping[str, str]) -> RequestSecurityPolicy:
    return RequestSecurityPolicy(
        allowed_origins=parse_allowed_origins(source.get("NQUIRY_ALLOWED_ORIGINS"))
    )


_policy: RequestSecurityPolicy | None = None


def configure_request_security(policy: RequestSecurityPolicy) -> None:
    global _policy
    _policy = policy


def current_request_security() -> RequestSecurityPolicy:
    if _policy is None:
        raise RuntimeError("request security is not configured")
    return _policy


def guard_request(
    *,
    method: str,
    path: str,
    origin: str | None,
    sec_fetch_site: str | None,
    content_type: str | None,
    own_origin: str,
) -> tuple[int, dict[str, object]] | None:
    """None → proceed. Otherwise the boundary failure to answer with."""
    if not is_unsafe_method(method):
        return None
    verdict: Verdict = evaluate_unsafe_request(
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        own_origin=own_origin,
        policy=current_request_security(),
    )
    if path == LOGIN_CONTACT:
        if not verdict.admitted or not login_contract_satisfied(content_type):
            return LOGIN_CSRF_REJECTED
        return None
    if not verdict.admitted:
        return CSRF_REJECTED
    return None


__all__ = [
    "CSRF_REJECTED",
    "LOGIN_CSRF_REJECTED",
    "configure_request_security",
    "current_request_security",
    "guard_request",
    "request_security_from_environment",
]
