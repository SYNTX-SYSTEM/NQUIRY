"""T9 security tests: local password hashing and session-token
primitives (`packages/security/local_auth.py`).

This is the "deterministic test adapter" half of 14 §32's own
authorized pair ("pluggable OIDC adapter plus deterministic test
adapter [IMPLEMENTATION CHOICE]"), hardened into a REAL local login —
closes the disclosed GAP-14-001 weakness that
`application.http_dispatch.resolve_actor` trusted a bare,
cryptographically-unverified request header (Architecture 17 /
FULLSTACK-RUNTIME-ACCEPTANCE report §14 KNOWN LIMITATIONS). GAP-14-001
itself (real OIDC provider selection) remains open; this module never
talks to an external identity provider.

Pure-Python, no DB — these are the crypto/token primitives only. The
concrete repository adapters live in
`packages/persistence/local_auth_repository.py` (DB-backed, tested in
`tests/e2e/test_auth_handler.py`).
"""

from __future__ import annotations

import pytest
from security.local_auth import (
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)


def test_hash_password_produces_a_pbkdf2_encoded_string() -> None:
    encoded = hash_password("correct horse battery staple")
    parts = encoded.split("$")
    assert len(parts) == 4
    algorithm, iterations, salt_hex, digest_hex = parts
    assert algorithm == "pbkdf2_sha256"
    assert int(iterations) >= 600_000
    bytes.fromhex(salt_hex)
    bytes.fromhex(digest_hex)


def test_hash_password_never_stores_the_plaintext() -> None:
    encoded = hash_password("hunter2")
    assert "hunter2" not in encoded


def test_two_hashes_of_the_same_password_are_not_equal() -> None:
    """Distinct random salts per call — a mandatory adversarial property:
    an attacker with DB read access cannot spot two users sharing a
    password by comparing stored hashes."""
    first = hash_password("shared-password")
    second = hash_password("shared-password")
    assert first != second


def test_verify_password_accepts_the_correct_password() -> None:
    encoded = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", encoded) is True


def test_verify_password_rejects_the_wrong_password() -> None:
    encoded = hash_password("correct horse battery staple")
    assert verify_password("wrong password", encoded) is False


def test_verify_password_rejects_a_case_variant() -> None:
    encoded = hash_password("Correct Horse")
    assert verify_password("correct horse", encoded) is False


@pytest.mark.parametrize(
    "garbage",
    [
        "",
        "not-encoded-at-all",
        "pbkdf2_sha256$notanumber$aa$bb",
        "bcrypt$600000$aa$bb",
        "pbkdf2_sha256$600000$not-hex$bb",
        "pbkdf2_sha256$600000$aa$not-hex",
    ],
)
def test_verify_password_fails_closed_on_a_malformed_encoded_hash(garbage: str) -> None:
    """Adversarial: a corrupted/tampered/foreign-format stored hash must
    never be treated as a match, and must never raise past this
    boundary (a raised exception here would crash the login request
    instead of failing the login) -- fails closed either way."""
    assert verify_password("anything", garbage) is False


def test_hash_password_rejects_an_empty_password() -> None:
    with pytest.raises(ValueError):
        hash_password("")


def test_generate_session_token_produces_distinct_high_entropy_tokens() -> None:
    tokens = {generate_session_token() for _ in range(50)}
    assert len(tokens) == 50
    for token in tokens:
        assert len(token) >= 32


def test_hash_session_token_is_deterministic_for_the_same_token() -> None:
    token = generate_session_token()
    assert hash_session_token(token) == hash_session_token(token)


def test_hash_session_token_never_stores_the_raw_token() -> None:
    token = generate_session_token()
    assert token not in hash_session_token(token)


def test_hash_session_token_differs_for_different_tokens() -> None:
    a = generate_session_token()
    b = generate_session_token()
    assert hash_session_token(a) != hash_session_token(b)
