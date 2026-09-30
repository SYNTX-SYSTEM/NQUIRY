"""T9: redirect target validation (24 WU-AUTH-06; §11.17, §21.15, §22.8, §32.8;
FBR-AUTH-015; falsifiers 103, 104).

MUST BECOME TRUE: a redirect target candidate is validated before it is
bound; post-auth, error and cancel redirects go to legitimate local
destinations only; the provider redirect URI and the application redirect
target stay distinct.

MUST REMAIN IMPOSSIBLE: an attacker-controlled absolute URL becomes a
post-auth redirect; a candidate becomes authority by existing; a hostile
candidate reaches the transaction.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from application.oidc_transactions import start_transaction
from persistence.oidc_transaction_repository import SqlAlchemyOidcTransactionRepository
from security.oidc_transaction import OidcTransactionPurpose
from security.redirect_target import (
    SAFE_DEFAULT_DESTINATION,
    RedirectTargetRejected,
    is_legitimate_local_destination,
    resolve_redirect_target,
    validate_redirect_target,
)

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)

HOSTILE = [
    "https://evil.test/",
    "http://evil.test/workspaces",
    "//evil.test/x",
    "/\\evil.test",
    "\\\\evil.test",
    "javascript:alert(1)",
    "data:text/html,x",
    "mailto:x@evil.test",
    " /workspaces",
    "/workspaces\n",
    "/work\rspaces",
    "/work\tspaces",
    "/workspaces\x00",
    "workspaces",
    "",
    "/" + "a" * 2048,
    "/%0d%0aSet-Cookie:x",
    "https:evil.test",
    "/ evil",
    "/wé",
]
LEGITIMATE = [
    "/",
    "/workspaces",
    "/workspaces/9e1f0c7a-4a2b-4d7c-9d1e-2f3a4b5c6d7e",
    "/account/security?tab=sessions",
    "/workspaces#top",
    "/a-b_c.d~e",
    "/x%20y",
]


@pytest.mark.parametrize("candidate", HOSTILE)
def test_hostile_candidates_are_not_legitimate_and_are_rejected(candidate: str) -> None:
    assert not is_legitimate_local_destination(candidate)
    with pytest.raises(RedirectTargetRejected):
        validate_redirect_target(candidate)
    assert resolve_redirect_target(candidate) == SAFE_DEFAULT_DESTINATION


@pytest.mark.parametrize("candidate", LEGITIMATE)
def test_legitimate_local_destinations_pass_unchanged(candidate: str) -> None:
    assert is_legitimate_local_destination(candidate)
    assert validate_redirect_target(candidate) == candidate
    assert resolve_redirect_target(candidate) == candidate


def test_no_candidate_means_the_safe_default() -> None:
    assert resolve_redirect_target(None) == SAFE_DEFAULT_DESTINATION
    assert SAFE_DEFAULT_DESTINATION == "/"
    with pytest.raises(RedirectTargetRejected):
        validate_redirect_target(None)


def test_the_provider_redirect_uri_is_never_a_valid_application_target() -> None:
    """24 §11.17 / falsifier 104: the registered provider redirect URI is an
    absolute URL and can never be bound as a post-auth application target."""
    for uri in (
        "https://nquiry.condyn.eu/auth/google/callback",
        "http://localhost:8000/auth/google/callback",
    ):
        assert not is_legitimate_local_destination(uri)


def test_a_transaction_binds_only_a_validated_target(db_connection: sa.Connection) -> None:
    repository = SqlAlchemyOidcTransactionRepository(db_connection)

    def start(candidate: str | None) -> str:
        started = start_transaction(
            repository,
            provider="TEST_PROVIDER",
            purpose=OidcTransactionPurpose.LOGIN,
            initiating_user_id=None,
            redirect_target=candidate,
            now=_NOW,
            lifetime=timedelta(minutes=10),
        )
        row = db_connection.execute(
            sa.text("SELECT post_auth_redirect_target FROM oidc_auth_transactions WHERE id = :id"),
            {"id": started.transaction_id},
        ).scalar_one()
        assert started.redirect_target == row
        return str(row)

    assert start("/workspaces?x=1") == "/workspaces?x=1"
    assert start(None) == SAFE_DEFAULT_DESTINATION
    for candidate in HOSTILE:
        assert start(candidate) == SAFE_DEFAULT_DESTINATION, candidate
    assert (
        db_connection.execute(
            sa.text(
                "SELECT count(*) FROM oidc_auth_transactions "
                "WHERE post_auth_redirect_target !~ '^/([^/].*)?$'"
            )
        ).scalar_one()
        == 0
    )
