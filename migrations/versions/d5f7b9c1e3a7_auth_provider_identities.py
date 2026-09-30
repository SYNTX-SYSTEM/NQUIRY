"""AUTH WU-AUTH-08: external_provider_identities (24 §11.13, §13.3, §22.2, §22.3)

Revision ID: d5f7b9c1e3a7
Revises: c4e6a8b1d3f5
Create Date: 2026-09-30 00:00:00.000000

The binding of a provider identity (`provider_issuer + provider_subject`, the
canonical external key; never email) to a canonical identity through one
authentication method.

- UNIQUE (provider_issuer, provider_subject): one identity per provider
  subject (24 §22.3; falsifier 42).
- UNIQUE authentication_method_id: one binding per method; composite FK
  (authentication_method_id, user_id) → authentication_methods (id, user_id):
  the method belongs to the same user.
- The method is a provider method (GOOGLE_OIDC or TEST_PROVIDER), never
  LOCAL_PASSWORD: trigger.
- issuer, subject, method and user of a binding never change (24 §14.7:
  a provider email change updates the attribute, never the link): trigger.
  `revoked_at` is set once (WU-AUTH-13 unlink) and never cleared.
- Provider email / verified / display name are attributes "at last
  authentication" and are refreshed by each provider login.

Also extends `oidc_auth_transactions.failure_reason` by
`AUTHENTICATION_METHOD_REVOKED`: a provider login through a binding whose
method is revoked is its own internal class (24 §32.2 lists a minimum).

Cross-Workspace (no `workspace_id`, no RLS). No DB-principal GRANT here
(WU-AUTH-17). Starts empty: no existing row of any table is read or changed.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d5f7b9c1e3a7"
down_revision = "c4e6a8b1d3f5"
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
    "'ACCOUNT_LINK_AUTHORITY_FAILURE', 'LOCAL_EFFECT_FAILURE'"
)
_REASONS_AFTER = _REASONS_BEFORE + ", 'AUTHENTICATION_METHOD_REVOKED'"


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
    op.create_table(
        "external_provider_identities",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("authentication_method_id", sa.Uuid(), nullable=False, unique=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("provider_issuer", sa.Text(), nullable=False),
        sa.Column("provider_subject", sa.Text(), nullable=False),
        sa.Column("provider_email", sa.Text(), nullable=True),
        sa.Column(
            "provider_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("provider_display_name", sa.Text(), nullable=True),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provenance_ref", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["authentication_method_id", "user_id"],
            ["authentication_methods.id", "authentication_methods.user_id"],
            name="fk_external_provider_identities_method_same_user",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "provider_issuer", "provider_subject", name="uq_external_provider_identities_subject"
        ),
        sa.CheckConstraint(
            "provider_issuer <> '' AND provider_subject <> ''",
            name="ck_external_provider_identities_key",
        ),
        sa.CheckConstraint(
            "provenance_ref <> ''", name="ck_external_provider_identities_provenance"
        ),
    )
    op.create_index(
        "ix_external_provider_identities_user_id", "external_provider_identities", ["user_id"]
    )
    op.execute(
        """
        CREATE FUNCTION trg_external_provider_identities_guard() RETURNS trigger AS $$
        DECLARE
            linked_type text;
        BEGIN
            IF TG_OP = 'UPDATE' THEN
                IF NEW.id IS DISTINCT FROM OLD.id
                   OR NEW.authentication_method_id IS DISTINCT FROM OLD.authentication_method_id
                   OR NEW.user_id IS DISTINCT FROM OLD.user_id
                   OR NEW.provider_issuer IS DISTINCT FROM OLD.provider_issuer
                   OR NEW.provider_subject IS DISTINCT FROM OLD.provider_subject
                   OR NEW.linked_at IS DISTINCT FROM OLD.linked_at
                   OR NEW.provenance_ref IS DISTINCT FROM OLD.provenance_ref THEN
                    RAISE EXCEPTION 'provider identity binding is immutable (24 section 14.7)';
                END IF;
                IF OLD.revoked_at IS NOT NULL AND NEW.revoked_at IS DISTINCT FROM OLD.revoked_at THEN
                    RAISE EXCEPTION 'a revoked provider identity binding stays revoked';
                END IF;
            END IF;
            SELECT method_type INTO linked_type
            FROM authentication_methods WHERE id = NEW.authentication_method_id;
            IF linked_type IS DISTINCT FROM 'GOOGLE_OIDC'
               AND linked_type IS DISTINCT FROM 'TEST_PROVIDER' THEN
                RAISE EXCEPTION
                    'a provider identity belongs to a provider method, not %', linked_type;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_external_provider_identities_guard
        BEFORE INSERT OR UPDATE ON external_provider_identities
        FOR EACH ROW EXECUTE FUNCTION trg_external_provider_identities_guard();
        """
    )
    _replace_reason_check(_REASONS_AFTER)


def downgrade() -> None:
    op.execute(
        "UPDATE oidc_auth_transactions SET failure_reason = 'LOCAL_EFFECT_FAILURE' "
        "WHERE failure_reason = 'AUTHENTICATION_METHOD_REVOKED'"
    )
    _replace_reason_check(_REASONS_BEFORE)
    op.execute(
        "DROP TRIGGER trg_external_provider_identities_guard ON external_provider_identities"
    )
    op.execute("DROP FUNCTION trg_external_provider_identities_guard()")
    op.drop_index(
        "ix_external_provider_identities_user_id", table_name="external_provider_identities"
    )
    op.drop_table("external_provider_identities")
