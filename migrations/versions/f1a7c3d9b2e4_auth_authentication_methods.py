"""AUTH WU-AUTH-02: authentication_methods (24 §13.2; FBR-AUTH-002)

Revision ID: f1a7c3d9b2e4
Revises: e8c2a5f1b7d4
Create Date: 2026-09-30 00:00:00.000000

The typed relation between a canonical identity (`users.id`) and a persistent
way it authenticates. One row per method.

- `method_type` is the closed vocabulary of 24 §9.1: LOCAL_PASSWORD,
  GOOGLE_OIDC, TEST_PROVIDER. A recovery challenge, an OIDC transaction, an
  initiating user-agent binding, a PKCE verifier or a CSRF proof is not a
  method (24 §9.1, §13.2) and is refused by the CHECK.
- `status` is ACTIVE or REVOKED; REVOKED exactly when `revoked_at` is set.
- A method is inserted ACTIVE. Its id, user, type, creation time and
  provenance never change. While ACTIVE, only `last_authenticated_at` may
  change, or the method may be revoked. REVOKED is terminal: the row is kept
  as evidence (24 §18.3) and never changes again. Enforced by triggers, for
  every writer.
- At most one ACTIVE LOCAL_PASSWORD method per user (partial unique index;
  24 §22.3 "local password method one active credential per method" builds on
  it in WU-AUTH-03).

Cross-Workspace, like `users` and `local_auth_*`: no `workspace_id`, no RLS
(24 §38 falsifier 64). No DB-principal GRANT is made here: the runtime
principal discipline for all authentication persistence, old and new, is
WU-AUTH-17 (24 §21.18, §28.8), applied once the persistence shape exists.

No existing row of any table is read or changed. `local_auth_credentials` is
related to this table in WU-AUTH-03.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f1a7c3d9b2e4"
down_revision = "e8c2a5f1b7d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "authentication_methods",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("method_type", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_authenticated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provenance_ref", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "method_type IN ('LOCAL_PASSWORD', 'GOOGLE_OIDC', 'TEST_PROVIDER')",
            name="ck_authentication_methods_method_type",
        ),
        sa.CheckConstraint(
            "(status = 'ACTIVE' AND revoked_at IS NULL) "
            "OR (status = 'REVOKED' AND revoked_at IS NOT NULL)",
            name="ck_authentication_methods_status_revocation",
        ),
        sa.CheckConstraint("provenance_ref <> ''", name="ck_authentication_methods_provenance"),
    )
    op.create_index("ix_authentication_methods_user_id", "authentication_methods", ["user_id"])
    op.create_index(
        "uq_authentication_methods_one_active_local_password",
        "authentication_methods",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("method_type = 'LOCAL_PASSWORD' AND status = 'ACTIVE'"),
    )
    op.execute(
        """
        CREATE FUNCTION trg_authentication_methods_initial_state() RETURNS trigger AS $$
        BEGIN
            IF NEW.status <> 'ACTIVE' THEN
                RAISE EXCEPTION
                    'an authentication method is created ACTIVE, not % (24 section 13.2)',
                    NEW.status;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_authentication_methods_initial_state
        BEFORE INSERT ON authentication_methods
        FOR EACH ROW EXECUTE FUNCTION trg_authentication_methods_initial_state();
        """
    )
    op.execute(
        """
        CREATE FUNCTION trg_authentication_methods_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.status = 'REVOKED' THEN
                RAISE EXCEPTION
                    'authentication method % is REVOKED: terminal, kept as evidence '
                    '(24 section 18.3)', OLD.id;
            END IF;
            IF NEW.id IS DISTINCT FROM OLD.id
               OR NEW.user_id IS DISTINCT FROM OLD.user_id
               OR NEW.method_type IS DISTINCT FROM OLD.method_type
               OR NEW.created_at IS DISTINCT FROM OLD.created_at
               OR NEW.provenance_ref IS DISTINCT FROM OLD.provenance_ref THEN
                RAISE EXCEPTION
                    'authentication method identity (id, user_id, method_type, created_at, '
                    'provenance_ref) is immutable';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_authentication_methods_transition
        BEFORE UPDATE ON authentication_methods
        FOR EACH ROW EXECUTE FUNCTION trg_authentication_methods_transition();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER trg_authentication_methods_transition ON authentication_methods")
    op.execute("DROP FUNCTION trg_authentication_methods_transition()")
    op.execute("DROP TRIGGER trg_authentication_methods_initial_state ON authentication_methods")
    op.execute("DROP FUNCTION trg_authentication_methods_initial_state()")
    op.drop_index(
        "uq_authentication_methods_one_active_local_password", table_name="authentication_methods"
    )
    op.drop_index("ix_authentication_methods_user_id", table_name="authentication_methods")
    op.drop_table("authentication_methods")
