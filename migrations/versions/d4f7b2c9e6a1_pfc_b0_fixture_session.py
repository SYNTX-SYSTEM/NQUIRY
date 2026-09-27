"""PFC B0: Fixture Session identity (HD-24 / NQ-DEC-052)

Revision ID: d4f7b2c9e6a1
Revises: c3b8e5a1f7d2
Create Date: 2026-09-27 00:00:00.000000

WU-PFC-B0. Human Authority HD-24 (2026-09-27), rules 1-5:
- A Session may be declared a Fixture Session only at Session creation.
- The marker is immutable after creation.
- A normal Session can never become a Fixture Session, and a Fixture Session
  can never become a real Session.
- Every surface that exposes Session proof semantics preserves the Fixture /
  NON_PROOF status.

`sessions.fixture` is NOT NULL, DEFAULT false. Every Session created before
this revision was created without a declaration, so it is a normal (governed)
Session. A BEFORE UPDATE trigger rejects any change to the value, in both
directions, for every writer.

`session_read_model.fixture` is nullable: the projection is derived and
rebuildable (AS-007). It is filled from the SESSION_CREATED event (schema 1.1).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d4f7b2c9e6a1"
down_revision = "c3b8e5a1f7d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("fixture", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute(
        """
        CREATE FUNCTION trg_sessions_fixture_immutable() RETURNS trigger AS $$
        BEGIN
            IF NEW.fixture IS DISTINCT FROM OLD.fixture THEN
                RAISE EXCEPTION
                    'sessions.fixture is fixed at Session creation and can never change '
                    '(HD-24 / NQ-DEC-052)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_sessions_fixture_immutable
        BEFORE UPDATE ON sessions
        FOR EACH ROW EXECUTE FUNCTION trg_sessions_fixture_immutable();
        """
    )
    op.add_column("session_read_model", sa.Column("fixture", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("session_read_model", "fixture")
    op.execute("DROP TRIGGER trg_sessions_fixture_immutable ON sessions")
    op.execute("DROP FUNCTION trg_sessions_fixture_immutable()")
    op.drop_column("sessions", "fixture")
