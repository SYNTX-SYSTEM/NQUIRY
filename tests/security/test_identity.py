"""T9 security tests: AuthenticatedPrincipal / IdentityPort.

Covers two of PKG-01's mandatory adversarial attacks: "token role claim
treated as domain right" and (adapted) "authentication session reuse as
authority".
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from security.identity import AuthenticatedPrincipal, ExternalCredential, IdentityPort
from semantic_types.ids import UserId
from test_support.identity import StaticIdentityPort, UnknownSubjectError


def _credential(subject: str, extra_claims: tuple[tuple[str, str], ...] = ()) -> ExternalCredential:
    return ExternalCredential(
        subject=subject,
        issuer_ref="https://issuer.example.test",
        session_ref=f"session-{subject}",
        authentication_time=datetime(2030, 1, 1, tzinfo=timezone.utc),
        extra_claims=extra_claims,
    )


def test_authenticated_principal_has_no_authority_shaped_field() -> None:
    """Structural non-collapse proof: IDENTITY != AUTHORITY (11 §1 AC-11-001).

    A caller cannot even *express* a role/permission on this type —
    there is no field for it.
    """
    field_names = {f.name for f in dataclasses.fields(AuthenticatedPrincipal)}
    assert field_names == {
        "user_id",
        "authentication_session_ref",
        "authentication_time",
        "issuer_ref",
    }


def test_authenticated_principal_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError):
        AuthenticatedPrincipal(
            user_id=UserId(uuid.uuid4()),
            authentication_session_ref="s1",
            authentication_time=datetime(2030, 1, 1),  # naive, rejected
            issuer_ref="https://issuer.example.test",
        )


def test_static_identity_port_resolves_registered_subject() -> None:
    user_id = UserId(uuid.uuid4())
    port: IdentityPort = StaticIdentityPort({"alice": user_id})

    principal = port.resolve(_credential("alice"))

    assert principal.user_id == user_id
    assert principal.authentication_session_ref == "session-alice"


def test_static_identity_port_fails_closed_on_unknown_subject() -> None:
    port = StaticIdentityPort({})
    with pytest.raises(UnknownSubjectError):
        port.resolve(_credential("unknown-subject"))


def test_token_role_claim_is_not_treated_as_a_domain_right() -> None:
    """Mandatory adversarial attack: "token role claim treated as domain right".

    A malicious/misconfigured credential carries an `admin` role claim.
    The resolved AuthenticatedPrincipal must not expose it anywhere —
    there is no attribute to smuggle it into.
    """
    user_id = UserId(uuid.uuid4())
    port = StaticIdentityPort({"mallory": user_id})

    principal = port.resolve(_credential("mallory", extra_claims=(("role", "admin"),)))

    assert principal.user_id == user_id
    # No such attribute exists at all -- this is a structural guarantee,
    # not a value check.
    assert not hasattr(principal, "role")
    assert not hasattr(principal, "is_admin")
    assert not hasattr(principal, "permissions")


def test_distinct_authentication_sessions_are_not_cached_as_reusable_authority() -> None:
    """Adapted attack: session material is a credential state, not an
    authority record (11 §6 AC-11-002 item 7) -- two distinct sessions
    for the same UserId must resolve to two distinct, independent
    AuthenticatedPrincipal values, not one memoized/reused object.
    """
    user_id = UserId(uuid.uuid4())
    port = StaticIdentityPort({"bob": user_id})

    credential_1 = ExternalCredential(
        subject="bob",
        issuer_ref="https://issuer.example.test",
        session_ref="session-1",
        authentication_time=datetime(2030, 1, 1, tzinfo=timezone.utc),
    )
    credential_2 = ExternalCredential(
        subject="bob",
        issuer_ref="https://issuer.example.test",
        session_ref="session-2",
        authentication_time=datetime(2030, 1, 1, tzinfo=timezone.utc) + timedelta(hours=1),
    )

    principal_1 = port.resolve(credential_1)
    principal_2 = port.resolve(credential_2)

    assert principal_1.user_id == principal_2.user_id == user_id
    assert principal_1.authentication_session_ref != principal_2.authentication_session_ref
    assert principal_1 != principal_2
