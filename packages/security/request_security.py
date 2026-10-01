"""Anti-CSRF verdict for unsafe browser requests (24 §21.6–21.9; WU-AUTH-14).

THE MECHANISM (24 §21.7 "a defensible layered combination"): the explicit
boundary is browser request metadata — the `Origin` header (sent by every
current browser on every POST, from forms and from `fetch`) decided against
an explicit, pinned set of allowed origins plus the API's own origin, with
`Sec-Fetch-Site` deciding when no `Origin` exists. A request carrying neither
header did not come from a browser and holds no cross-site ambient authority
(a non-browser agent sends the cookie it was given on purpose), so it is
admitted as such.

Further layers that exist but are NOT this proof: CORS (24 §21.9: it only
governs which origin may *read*, and simple requests have no preflight),
`SameSite=Lax` on the session cookie (24 §21.7: never the sole boundary), and
the JSON request contract of the `fetch` routes (a cross-site form cannot
produce `application/json`). For the local password login the JSON contract
is made explicit and mandatory (24 §21.6 "request media-type contract"),
because that request is unauthenticated and can create a fresh session.

This module is pure: no cookie, no database, no framework. The verdict is a
function of four strings.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlsplit

DEFAULT_ALLOWED_ORIGINS: tuple[str, ...] = ("http://localhost:3000",)
LOGIN_CONTACT = "/auth/login"
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


class AllowedOriginsInvalid(ValueError):
    """The configured allowed origins are not an explicit, pinned list of
    `scheme://host[:port]` origins (a wildcard, a path, a bare host, `null`)."""


class Verdict(Enum):
    ALLOWED_ORIGIN = "ALLOWED_ORIGIN"  # Origin is one of the configured origins
    SAME_ORIGIN = "SAME_ORIGIN"  # Origin is the API's own, or Sec-Fetch-Site same-origin
    USER_INITIATED = "USER_INITIATED"  # Sec-Fetch-Site none, no Origin (address bar / bookmark)
    NO_BROWSER_METADATA = "NO_BROWSER_METADATA"  # neither header: not a browser
    FOREIGN_ORIGIN = "FOREIGN_ORIGIN"
    NULL_ORIGIN = "NULL_ORIGIN"
    MALFORMED_ORIGIN = "MALFORMED_ORIGIN"
    CROSS_SITE = "CROSS_SITE"  # Sec-Fetch-Site cross-site / same-site / unknown, no Origin

    @property
    def admitted(self) -> bool:
        return self in _ADMITTED


_ADMITTED = frozenset(
    {
        Verdict.ALLOWED_ORIGIN,
        Verdict.SAME_ORIGIN,
        Verdict.USER_INITIATED,
        Verdict.NO_BROWSER_METADATA,
    }
)


@dataclass(frozen=True, slots=True)
class RequestSecurityPolicy:
    """The explicit, pinned browser origins that may issue unsafe requests
    (and read responses: the same list feeds CORS, 24 §21.9)."""

    allowed_origins: tuple[str, ...]


def is_origin(value: str) -> bool:
    """`scheme://host[:port]`, lower-case scheme and host, nothing else."""
    if not value or value == "null" or "*" in value:
        return False
    parts = urlsplit(value)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return False
    if parts.path or parts.query or parts.fragment or parts.username or parts.password:
        return False
    if parts.hostname is None or parts.netloc != parts.netloc.lower():
        return False
    try:
        parts.port  # noqa: B018 -- raises on a malformed port
    except ValueError:
        return False
    return value == f"{parts.scheme}://{parts.netloc}"


def parse_allowed_origins(raw: str | None) -> tuple[str, ...]:
    """`NQUIRY_ALLOWED_ORIGINS`: comma-separated origins. Unset / empty →
    the one local development frontend origin. Anything that is not an
    origin (a wildcard above all, 24 §21.9 falsifier) is refused."""
    if raw is None or not raw.strip():
        return DEFAULT_ALLOWED_ORIGINS
    origins: list[str] = []
    for item in raw.split(","):
        candidate = item.strip()
        if not is_origin(candidate):
            raise AllowedOriginsInvalid(f"not an explicit origin: {candidate!r}")
        if candidate not in origins:
            origins.append(candidate)
    return tuple(origins)


def is_unsafe_method(method: str) -> bool:
    return method.upper() not in _SAFE_METHODS


def evaluate_unsafe_request(
    *,
    origin: str | None,
    sec_fetch_site: str | None,
    own_origin: str,
    policy: RequestSecurityPolicy,
) -> Verdict:
    """The verdict for one unsafe request. `origin` / `sec_fetch_site` are the
    raw header values (None when absent); `own_origin` is the origin the
    request was addressed to."""
    if origin is not None:
        if origin == "null":
            return Verdict.NULL_ORIGIN
        if not is_origin(origin):
            return Verdict.MALFORMED_ORIGIN
        if origin in policy.allowed_origins:
            return Verdict.ALLOWED_ORIGIN
        if origin == own_origin:
            return Verdict.SAME_ORIGIN
        return Verdict.FOREIGN_ORIGIN
    if sec_fetch_site is not None:
        if sec_fetch_site == "same-origin":
            return Verdict.SAME_ORIGIN
        if sec_fetch_site == "none":
            return Verdict.USER_INITIATED
        return Verdict.CROSS_SITE
    return Verdict.NO_BROWSER_METADATA


def login_contract_satisfied(content_type: str | None) -> bool:
    """24 §21.6: the local password login accepts `application/json` only.
    An HTML form (the cross-site submission vehicle) cannot produce it."""
    if content_type is None:
        return False
    media_type = content_type.split(";", 1)[0].strip().lower()
    return media_type == "application/json"


__all__ = [
    "DEFAULT_ALLOWED_ORIGINS",
    "LOGIN_CONTACT",
    "AllowedOriginsInvalid",
    "RequestSecurityPolicy",
    "Verdict",
    "evaluate_unsafe_request",
    "is_origin",
    "is_unsafe_method",
    "login_contract_satisfied",
    "parse_allowed_origins",
]
