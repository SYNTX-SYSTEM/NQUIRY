"""AUTH WU-AUTH-09: account creation boundary failure classes (24 §11.14, §32.2)

Revision ID: e6a8c1d3f5b9
Revises: d5f7b9c1e3a7
Create Date: 2026-09-30 00:00:00.000000

Extends `oidc_auth_transactions.failure_reason` by the account creation
boundary's own classes: PROVIDER_EMAIL_MISSING, PROVIDER_EMAIL_UNVERIFIED,
EMAIL_COLLISION (24 §14.5 "Same email on different accounts is not automatic
link"). No table, no row change; the account creation effect itself writes
the existing `users`, `authentication_methods`, `external_provider_identities`
and `security_events` relations.
"""

from __future__ import annotations

from alembic import op

revision = "e6a8c1d3f5b9"
down_revision = "d5f7b9c1e3a7"
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
    "'ACCOUNT_LINK_AUTHORITY_FAILURE', 'LOCAL_EFFECT_FAILURE', 'AUTHENTICATION_METHOD_REVOKED'"
)
_REASONS_AFTER = (
    _REASONS_BEFORE + ", 'PROVIDER_EMAIL_MISSING', 'PROVIDER_EMAIL_UNVERIFIED', 'EMAIL_COLLISION'"
)


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
        "WHERE failure_reason IN "
        "('PROVIDER_EMAIL_MISSING', 'PROVIDER_EMAIL_UNVERIFIED', 'EMAIL_COLLISION')"
    )
    _replace_reason_check(_REASONS_BEFORE)
