"""session participation relation + one open Burst per Session

Revision ID: b3d8e5f0a2c7
Revises: a7f2c91d4e10
Create Date: 2026-09-24 00:00:01.000000

F02 WU-02.8.

`session_participations` materializes 09 §28 (DATA CONTRACT:
SessionParticipation, RELATION: session_participation_id, session_id,
user_id, joined_at, left_at, record_version) and 02 §12 (User <-> Session
relation; "Participation does not imply operation authority"). Admission
authority is the human operator's HD-7 decision (16 §41 REC-006): the
Session controller admits an active Workspace member. The DB enforces
only structural truth:

- `workspace_id` is the constrained denormalization every Workspace-keyed
  table carries. The composite FK to `sessions(id, workspace_id)` makes a
  cross-Workspace participation row impossible.
- `trg_session_participation_requires_membership` (BEFORE INSERT): the
  participant must hold an ACTIVE membership in that Workspace. Same
  shape as `trg_habb_check_grant_preconditions` (05 GOV-005).
- At most one CURRENT participation per (session, user): partial UNIQUE
  WHERE left_at IS NULL.
- RLS: identical `workspace_isolation` policy as the 29 tables of
  migration 047bdf9bc528 (fail-closed default).

`uq_question_bursts_one_open_per_session`: 03 TRN-SESS-004 DENY condition
"Competing active Burst" and TRN-BURST-001 ("QuestionBurst belongs to
that Session"), plus `BurstRepository.get_by_session`'s `one_or_none`
assumption. At most one non-COMPLETED Burst per Session. Enforced here so
two concurrent PREPARE_BURST commits cannot both succeed.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b3d8e5f0a2c7"
down_revision = "a7f2c91d4e10"
branch_labels = None
depends_on = None

_RLS_EXPR = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"


def upgrade() -> None:
    op.create_table(
        "session_participations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column(
            "workspace_id",
            sa.Uuid(),
            sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "admitted_by_user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("record_version", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id", "workspace_id"],
            ["sessions.id", "sessions.workspace_id"],
            name="fk_session_participations_session_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("record_version >= 1", name="ck_session_participations_version"),
    )
    op.create_index(
        "uq_session_participations_current",
        "session_participations",
        ["session_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("left_at IS NULL"),
    )
    op.create_index("ix_session_participations_workspace", "session_participations", ["workspace_id"])
    op.execute(
        """
        CREATE FUNCTION trg_session_participation_requires_membership() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM workspace_memberships
                WHERE workspace_id = NEW.workspace_id
                  AND user_id = NEW.user_id
                  AND status = 'ACTIVE'
            ) THEN
                RAISE EXCEPTION
                    'session participation requires ACTIVE workspace_membership (F02 HD-7), user %',
                    NEW.user_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_session_participation_requires_membership
        BEFORE INSERT ON session_participations
        FOR EACH ROW EXECUTE FUNCTION trg_session_participation_requires_membership();
        """
    )
    op.execute("ALTER TABLE session_participations ENABLE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY workspace_isolation ON session_participations "
        f"USING ({_RLS_EXPR}) WITH CHECK ({_RLS_EXPR})"
    )
    op.create_index(
        "uq_question_bursts_one_open_per_session",
        "question_bursts",
        ["session_id"],
        unique=True,
        postgresql_where=sa.text("state <> 'COMPLETED'"),
    )


def downgrade() -> None:
    op.drop_index("uq_question_bursts_one_open_per_session", table_name="question_bursts")
    op.execute("DROP POLICY IF EXISTS workspace_isolation ON session_participations")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_session_participation_requires_membership ON session_participations"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_session_participation_requires_membership()")
    op.drop_index("ix_session_participations_workspace", table_name="session_participations")
    op.drop_index("uq_session_participations_current", table_name="session_participations")
    op.drop_table("session_participations")
