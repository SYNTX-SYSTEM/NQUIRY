"""AUTH WU-AUTH-13: account disable; one active binding per subject; ACCOUNT_DISABLED (24 §18)

Revision ID: b9d2f4a6c8e1
Revises: a8c1e3f5b7d9
Create Date: 2026-10-01 00:00:00.000000

Account disable (24 §18.1, §18.2 "If account disabled"): `users.disabled_at`
with `users.disabled_provenance` (both set or both NULL). One-way at the
database (trigger): a disabled identity stays disabled; re-enabling is
administrative recovery (24 §36 #13, not materialized). No session row can be
inserted for a disabled identity (trigger on `local_auth_sessions`): the
"account disable during login" race (24 §33.7) ends without a session even
when the password verified before the disable committed.

Provider unlink (24 §18.2 "If a provider method is unlinked"): the binding is
kept as revoked evidence (24 §18.3), so the full uniqueness of
(issuer, subject) becomes a partial unique index over ACTIVE (unrevoked)
bindings: one identity holds a subject at a time; an unlinked subject may be
linked again as a new method.

`oidc_auth_transactions.failure_reason` gains ACCOUNT_DISABLED: a provider
login that resolves to a disabled identity fails terminally with its own class.

Cross-Workspace (no `workspace_id`, no RLS). No DB-principal GRANT here
(WU-AUTH-17). Existing rows: `disabled_at` NULL for every identity (nobody is
disabled by a migration); every existing binding satisfies the partial index.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b9d2f4a6c8e1"
down_revision = "a8c1e3f5b7d9"
branch_labels = None
depends_on = None

_FAILURE_REASONS_BEFORE = (
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
    "'PROVIDER_EMAIL_MISSING', 'PROVIDER_EMAIL_UNVERIFIED', 'EMAIL_COLLISION'"
)
_FAILURE_REASONS_AFTER = _FAILURE_REASONS_BEFORE + ", 'ACCOUNT_DISABLED'"


def _replace_failure_reason_check(reasons: str) -> None:
    op.drop_constraint(
        "ck_oidc_auth_transactions_failure_reason", "oidc_auth_transactions", type_="check"
    )
    op.create_check_constraint(
        "ck_oidc_auth_transactions_failure_reason",
        "oidc_auth_transactions",
        f"failure_reason IS NULL OR failure_reason IN ({reasons})",
    )


def upgrade() -> None:
    # --- account disable ---------------------------------------------------
    op.add_column("users", sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("disabled_provenance", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_users_disable_provenance",
        "users",
        "(disabled_at IS NULL) = (disabled_provenance IS NULL) "
        "AND (disabled_provenance IS NULL OR disabled_provenance <> '')",
    )
    op.execute(
        """
        CREATE FUNCTION trg_users_disable_one_way() RETURNS trigger AS $$
        BEGIN
            IF OLD.disabled_at IS NOT NULL AND (
                NEW.disabled_at IS DISTINCT FROM OLD.disabled_at
                OR NEW.disabled_provenance IS DISTINCT FROM OLD.disabled_provenance
            ) THEN
                RAISE EXCEPTION
                    'account disable is one-way: identity % stays disabled (24 section 18.3)',
                    OLD.id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_users_disable_one_way
        BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION trg_users_disable_one_way();
        """
    )
    op.execute(
        """
        CREATE FUNCTION trg_local_auth_sessions_no_disabled_identity() RETURNS trigger AS $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM users WHERE id = NEW.user_id AND disabled_at IS NOT NULL
            ) THEN
                RAISE EXCEPTION
                    'no session for a disabled identity % (24 section 18.2, 19.3)', NEW.user_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_local_auth_sessions_no_disabled_identity
        BEFORE INSERT ON local_auth_sessions
        FOR EACH ROW EXECUTE FUNCTION trg_local_auth_sessions_no_disabled_identity();
        """
    )
    # --- one ACTIVE binding per provider subject ---------------------------
    op.drop_constraint(
        "uq_external_provider_identities_subject", "external_provider_identities", type_="unique"
    )
    op.create_index(
        "uq_external_provider_identities_active_subject",
        "external_provider_identities",
        ["provider_issuer", "provider_subject"],
        unique=True,
        postgresql_where=sa.text("revoked_at IS NULL"),
    )
    op.create_index(
        "ix_external_provider_identities_subject",
        "external_provider_identities",
        ["provider_issuer", "provider_subject"],
    )
    # --- failure class -----------------------------------------------------
    _replace_failure_reason_check(_FAILURE_REASONS_AFTER)


def downgrade() -> None:
    op.execute(
        "UPDATE oidc_auth_transactions SET failure_reason = 'AUTHENTICATION_METHOD_REVOKED' "
        "WHERE failure_reason = 'ACCOUNT_DISABLED'"
    )
    _replace_failure_reason_check(_FAILURE_REASONS_BEFORE)
    op.drop_index(
        "ix_external_provider_identities_subject", table_name="external_provider_identities"
    )
    op.drop_index(
        "uq_external_provider_identities_active_subject",
        table_name="external_provider_identities",
    )
    # A downgrade cannot keep two bindings of one subject; the revoked ones go
    # (evidence loss is the downgrade's price, as for every revocation relation).
    op.execute(
        "DELETE FROM external_provider_identities e USING external_provider_identities a "
        "WHERE e.revoked_at IS NOT NULL AND a.revoked_at IS NULL "
        "  AND a.provider_issuer = e.provider_issuer AND a.provider_subject = e.provider_subject"
    )
    op.execute(
        "DELETE FROM external_provider_identities e USING external_provider_identities o "
        "WHERE e.revoked_at IS NOT NULL AND o.revoked_at IS NOT NULL AND e.id <> o.id "
        "  AND o.provider_issuer = e.provider_issuer AND o.provider_subject = e.provider_subject "
        "  AND e.linked_at < o.linked_at"
    )
    op.create_unique_constraint(
        "uq_external_provider_identities_subject",
        "external_provider_identities",
        ["provider_issuer", "provider_subject"],
    )
    op.execute("DROP TRIGGER trg_local_auth_sessions_no_disabled_identity ON local_auth_sessions")
    op.execute("DROP FUNCTION trg_local_auth_sessions_no_disabled_identity()")
    op.execute("DROP TRIGGER trg_users_disable_one_way ON users")
    op.execute("DROP FUNCTION trg_users_disable_one_way()")
    op.drop_constraint("ck_users_disable_provenance", "users", type_="check")
    op.drop_column("users", "disabled_provenance")
    op.drop_column("users", "disabled_at")
