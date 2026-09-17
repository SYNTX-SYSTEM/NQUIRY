"""Deterministic `IdentityPort` test double.

TEST ONLY. Must never be imported by production code — see
`packages/test_support/__init__.py` and
`scripts/check_test_only_imports.py`.

14 §32: "Test adapter is deterministic." This adapter maps
`ExternalCredential.subject` to a `UserId` through an explicit,
test-supplied table — it never invents a mapping and never falls back
to guessing. An unknown subject fails closed (14 non-collapse: "Unknown
consequential semantic input fails closed").
"""

from __future__ import annotations

from security.identity import AuthenticatedPrincipal, ExternalCredential
from semantic_types.ids import UserId


class UnknownSubjectError(ValueError):
    """Raised when a credential's subject has no registered mapping."""


class StaticIdentityPort:
    """An `IdentityPort` backed by an explicit, test-supplied
    subject -> UserId table.

    Deliberately does *not* read `credential.extra_claims` for
    anything but pass-through logging — an authority-shaped claim
    (e.g. `("role", "admin")`) must never influence the resolved
    `AuthenticatedPrincipal` (see `tests/security/test_identity.py`).
    """

    def __init__(self, subject_to_user_id: dict[str, UserId]) -> None:
        self._subject_to_user_id = dict(subject_to_user_id)

    def resolve(self, credential: ExternalCredential) -> AuthenticatedPrincipal:
        try:
            user_id = self._subject_to_user_id[credential.subject]
        except KeyError as exc:
            raise UnknownSubjectError(
                f"no registered UserId for subject {credential.subject!r}"
            ) from exc

        return AuthenticatedPrincipal(
            user_id=user_id,
            authentication_session_ref=credential.session_ref,
            authentication_time=credential.authentication_time,
            issuer_ref=credential.issuer_ref,
        )


__all__ = ["StaticIdentityPort", "UnknownSubjectError"]
