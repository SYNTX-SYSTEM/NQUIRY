"""AUTH WU-AUTH-03: local credentials belong to a LOCAL_PASSWORD method (24 §22.4, §28.2)

Revision ID: a2c4e6f8b1d3
Revises: f1a7c3d9b2e4
Create Date: 2026-09-30 00:00:00.000000

`local_auth_credentials.authentication_method_id` (NOT NULL, UNIQUE): the
method a credential belongs to.

- Same user: composite FK (authentication_method_id, user_id) ->
  authentication_methods (id, user_id).
- One credential per method: UNIQUE (24 §22.3).
- The method is a LOCAL_PASSWORD method, and the link and the user of a
  credential never change: trigger, for every writer.

BACKFILL (24 §28.2 "Existing `local_auth_credentials` rows should become
LOCAL_PASSWORD authentication methods"): every existing credential gets one
ACTIVE LOCAL_PASSWORD method of its own user, created at the credential's own
creation time, with provenance `migration:a2c4e6f8b1d3:local-credential:<id>`
(24 §13.10: a migration records its provenance; it proves nothing about the
identity). `password_hash`, `user_id` and both timestamps of every credential
are unchanged; no plaintext is involved. Existing sessions are not touched.

DOWNGRADE removes the link and every LOCAL_PASSWORD method (after the
downgrade nothing relates them to a credential, and a later re-upgrade
backfills them again). Credentials and sessions are preserved, so the
predecessor login keeps working (24 §28.9).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a2c4e6f8b1d3"
down_revision = "f1a7c3d9b2e4"
branch_labels = None
depends_on = None

_PROVENANCE_PREFIX = "migration:a2c4e6f8b1d3:local-credential:"


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_authentication_methods_id_user", "authentication_methods", ["id", "user_id"]
    )
    op.add_column(
        "local_auth_credentials",
        sa.Column("authentication_method_id", sa.Uuid(), nullable=True),
    )
    op.execute(
        f"""
        INSERT INTO authentication_methods
            (id, user_id, method_type, status, created_at, revoked_at,
             last_authenticated_at, provenance_ref)
        SELECT gen_random_uuid(), c.user_id, 'LOCAL_PASSWORD', 'ACTIVE', c.created_at, NULL,
               NULL, '{_PROVENANCE_PREFIX}' || c.id::text
        FROM local_auth_credentials c
        """
    )
    op.execute(
        f"""
        UPDATE local_auth_credentials c
        SET authentication_method_id = m.id
        FROM authentication_methods m
        WHERE m.provenance_ref = '{_PROVENANCE_PREFIX}' || c.id::text
        """
    )
    op.alter_column("local_auth_credentials", "authentication_method_id", nullable=False)
    op.create_unique_constraint(
        "uq_local_auth_credentials_authentication_method_id",
        "local_auth_credentials",
        ["authentication_method_id"],
    )
    op.create_foreign_key(
        "fk_local_auth_credentials_method_same_user",
        "local_auth_credentials",
        "authentication_methods",
        ["authentication_method_id", "user_id"],
        ["id", "user_id"],
        ondelete="RESTRICT",
    )
    op.execute(
        """
        CREATE FUNCTION trg_local_auth_credentials_method() RETURNS trigger AS $$
        DECLARE
            linked_type text;
        BEGIN
            IF TG_OP = 'UPDATE' AND (
                NEW.authentication_method_id IS DISTINCT FROM OLD.authentication_method_id
                OR NEW.user_id IS DISTINCT FROM OLD.user_id
            ) THEN
                RAISE EXCEPTION
                    'local_auth_credentials.authentication_method_id and user_id are immutable';
            END IF;
            SELECT method_type INTO linked_type
            FROM authentication_methods WHERE id = NEW.authentication_method_id;
            IF linked_type IS DISTINCT FROM 'LOCAL_PASSWORD' THEN
                RAISE EXCEPTION
                    'a local credential belongs to a LOCAL_PASSWORD method, not %', linked_type;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_local_auth_credentials_method
        BEFORE INSERT OR UPDATE ON local_auth_credentials
        FOR EACH ROW EXECUTE FUNCTION trg_local_auth_credentials_method();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER trg_local_auth_credentials_method ON local_auth_credentials")
    op.execute("DROP FUNCTION trg_local_auth_credentials_method()")
    op.drop_constraint(
        "fk_local_auth_credentials_method_same_user", "local_auth_credentials", type_="foreignkey"
    )
    op.drop_constraint(
        "uq_local_auth_credentials_authentication_method_id",
        "local_auth_credentials",
        type_="unique",
    )
    op.drop_column("local_auth_credentials", "authentication_method_id")
    op.execute("DELETE FROM authentication_methods WHERE method_type = 'LOCAL_PASSWORD'")
    op.drop_constraint(
        "uq_authentication_methods_id_user", "authentication_methods", type_="unique"
    )
