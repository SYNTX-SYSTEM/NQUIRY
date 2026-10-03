"""AUTH PROVIDER_BOOTSTRAP: PROVIDER_PROFILE_INCOMPLETE failure class (24 §11.14, §13.10)

Revision ID: d2f4a6b8c1e3
Revises: c1e3a5b7d9f2
Create Date: 2026-10-04 00:00:00.000000

Extends `oidc_auth_transactions.failure_reason` by PROVIDER_PROFILE_INCOMPLETE:
a verified provider credential without a display-name claim cannot bootstrap
an NQUIRY identity, because the identity's display name is never invented
(no email local-part, no placeholder). No table, no row change.
"""

from __future__ import annotations

from alembic import op

revision = "d2f4a6b8c1e3"
down_revision = "c1e3a5b7d9f2"
branch_labels = None
depends_on = None

_REASONS_BEFORE = (
    "'MISSING_TRANSACTION', 'EXPIRED_TRANSACTION', 'INVALID_STATE', "
    "'USER_AGENT_BINDING_MISSING', 'USER_AGENT_BINDING_MISMATCH', 'PURPOSE_MISMATCH', "
    "'INITIATING_USER_MISMATCH', 'ALREADY_PROCESSING', 'ALREADY_COMPLETED', "
    "'CANCELLED_TERMINAL', 'FAILED_TERMINAL', 'EXPIRED', 'MISSING_PKCE_VERIFIER', "
    "'TOKEN_EXCHANGE_REJECTED', 'TOKEN_EXCHANGE_OUTCOME_UNCERTAIN', "
    "'INVALID_ID_TOKEN_SIGNATURE', 'INVALID_ISSUER', 'INVALID_AUDIENCE', 'EXPIRED_ID_TOKEN', "
    "'INVALID_NONCE', 'PROVIDER_SUBJECT_MISSING', 'PROVIDER_SUBJECT_COLLISION', "
    "'PROVIDER_ACCESS_DENIED', 'USER_CANCEL', 'PROVIDER_FAILURE', 'MALFORMED_CALLBACK', "
    "'REDIRECT_TARGET_REJECTED', 'ACCOUNT_CREATION_POLICY_UNRESOLVED', "
    "'ACCOUNT_LINK_AUTHORITY_FAILURE', 'LOCAL_EFFECT_FAILURE', 'AUTHENTICATION_METHOD_REVOKED', "
    "'PROVIDER_EMAIL_MISSING', 'PROVIDER_EMAIL_UNVERIFIED', 'EMAIL_COLLISION', 'ACCOUNT_DISABLED'"
)
_REASONS_AFTER = _REASONS_BEFORE + ", 'PROVIDER_PROFILE_INCOMPLETE'"


def _replace_reason_check(reasons: str) -> None:
    op.drop_constraint(
        "ck_oidc_auth_transactions_failure_reason", "oidc_auth_transactions", type_="check"
    )
    op.create_check_constraint(
        "ck_oidc_auth_transactions_failure_reason",
        "oidc_auth_transactions",
        f"failure_reason IS NULL OR failure_reason IN ({reasons})",
    )


def upgrade() -> None:
    _replace_reason_check(_REASONS_AFTER)


def downgrade() -> None:
    op.execute(
        "UPDATE oidc_auth_transactions SET failure_reason = 'ACCOUNT_CREATION_POLICY_UNRESOLVED' "
        "WHERE failure_reason = 'PROVIDER_PROFILE_INCOMPLETE'"
    )
    _replace_reason_check(_REASONS_BEFORE)
