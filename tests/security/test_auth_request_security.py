"""T9 (no database): the pure anti-CSRF verdict (24 §21.6–21.9; WU-AUTH-14).

The verdict is a function of the request's browser metadata (`Origin`,
`Sec-Fetch-Site`), the request's own origin and the configured allowed
origins. Nothing else: no cookie, no CORS, no SameSite enters it (24 §21.7
"CORS must not be treated as a substitute", "SameSite must not be the sole
boundary"; both remain additional layers, not this proof).
"""

from __future__ import annotations

import pytest
from security.request_security import (
    LOGIN_CONTACT,
    AllowedOriginsInvalid,
    RequestSecurityPolicy,
    Verdict,
    evaluate_unsafe_request,
    login_contract_satisfied,
    parse_allowed_origins,
)

_POLICY = RequestSecurityPolicy(allowed_origins=("http://localhost:3000",))
_OWN = "http://api.nquiry.test"


def _verdict(origin: str | None = None, site: str | None = None) -> Verdict:
    return evaluate_unsafe_request(
        origin=origin, sec_fetch_site=site, own_origin=_OWN, policy=_POLICY
    )


def test_an_allowed_origin_or_the_api_s_own_origin_is_admitted() -> None:
    assert _verdict("http://localhost:3000") == Verdict.ALLOWED_ORIGIN
    assert _verdict("http://localhost:3000", "cross-site") == Verdict.ALLOWED_ORIGIN
    assert _verdict(_OWN) == Verdict.SAME_ORIGIN


@pytest.mark.parametrize(
    "origin",
    [
        "https://evil.example",
        "http://localhost:3001",
        "http://localhost",
        "https://localhost:3000",
        "null",
        "",
        "not an origin",
        "http://localhost:3000/path",
        "http://localhost:3000.evil.example",
        "HTTP://LOCALHOST:3000",
    ],
)
def test_every_other_origin_is_refused_whatever_fetch_metadata_says(origin: str) -> None:
    for site in (None, "same-origin", "none"):
        assert _verdict(origin, site) in (
            Verdict.FOREIGN_ORIGIN,
            Verdict.NULL_ORIGIN,
            Verdict.MALFORMED_ORIGIN,
        ), (origin, site)


def test_fetch_metadata_decides_when_no_origin_header_exists() -> None:
    assert _verdict(None, "same-origin") == Verdict.SAME_ORIGIN
    assert _verdict(None, "none") == Verdict.USER_INITIATED
    assert _verdict(None, "cross-site") == Verdict.CROSS_SITE
    assert _verdict(None, "same-site") == Verdict.CROSS_SITE  # another port is another origin
    assert _verdict(None, "garbage") == Verdict.CROSS_SITE


def test_no_browser_metadata_at_all_is_a_non_browser_agent() -> None:
    assert _verdict(None, None) == Verdict.NO_BROWSER_METADATA
    assert Verdict.NO_BROWSER_METADATA.admitted


def test_the_admitted_set_is_exactly_the_three_same_or_allowed_origin_verdicts() -> None:
    admitted = {v for v in Verdict if v.admitted}
    assert admitted == {
        Verdict.ALLOWED_ORIGIN,
        Verdict.SAME_ORIGIN,
        Verdict.USER_INITIATED,
        Verdict.NO_BROWSER_METADATA,
    }


def test_the_login_contract_is_json_only() -> None:
    assert LOGIN_CONTACT == "/auth/login"
    assert login_contract_satisfied("application/json")
    assert login_contract_satisfied("application/json; charset=utf-8")
    for content_type in (
        None,
        "",
        "text/plain",
        "application/x-www-form-urlencoded",
        "multipart/form-data; boundary=x",
        "application/jsonx",
        "text/json",
    ):
        assert not login_contract_satisfied(content_type), content_type


def test_allowed_origins_are_explicit_pinned_and_never_a_wildcard() -> None:
    assert parse_allowed_origins(None) == ("http://localhost:3000",)
    assert parse_allowed_origins("") == ("http://localhost:3000",)
    assert parse_allowed_origins("https://nquiry.condyn.eu, http://localhost:13460") == (
        "https://nquiry.condyn.eu",
        "http://localhost:13460",
    )
    for raw in (
        "*",
        "https://*.condyn.eu",
        "https://a.example/",
        "a.example",
        "https://a.example/x",
        "null",
    ):
        with pytest.raises(AllowedOriginsInvalid):
            parse_allowed_origins(raw)
