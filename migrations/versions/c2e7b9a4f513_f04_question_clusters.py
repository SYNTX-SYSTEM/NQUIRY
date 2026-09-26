"""F04: QuestionCluster and QuestionClusterMembership (09 §34 / §35)

Revision ID: c2e7b9a4f513
Revises: a8d3f1c6e902
Create Date: 2026-09-25 00:00:02.000000

F04 WU-04.9 (HD-21, HD-23; pre-implementation binding PI-6).

- `question_clusters` (09 §34, DERIVED_DOMAIN_OBJECT): the 09 fields plus the
  Workspace and Session it belongs to. `cluster_run_id` is the id of the
  accepted AIOP-002 artifact of the run (09 §34.1: a persisted clustering run
  gets a `cluster_run_id`, no destructive overwrite). The composite FK makes a
  cluster impossible without an accepted clustering artifact of the same
  Session, and at most one accepted clustering artifact exists per Session
  (index `uq_ai_derived_artifacts_one_accepted_per_session_operation`), so at
  most one accepted cluster run exists per Session (R8).
- `question_cluster_memberships` (09 §35, RELATION): a membership may name only
  a Question of the Session's frozen Burst (K1; trigger), at most once per run.
  "It never changes Question identity": nothing references Questions for
  write.

Both tables are append-only (UPDATE / DELETE rejected) and Workspace-scoped
(RLS `workspace_isolation`). There is no priority, rank or selection column
(08 §24 FORBIDDEN "grant selection priority"; K5).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c2e7b9a4f513"
down_revision = "a8d3f1c6e902"
branch_labels = None
depends_on = None

_RLS_EXPR = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"
_TABLES = ("question_clusters", "question_cluster_memberships")


def upgrade() -> None:
    op.create_table(
        "question_clusters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("challenge_id", sa.Uuid(), nullable=False),
        sa.Column("analysis_generation_id", sa.Uuid(), nullable=False),
        sa.Column("cluster_run_id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_question_clusters"),
        sa.ForeignKeyConstraint(
            ["session_id", "workspace_id"],
            ["sessions.id", "sessions.workspace_id"],
            name="fk_question_clusters_session_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["challenge_id", "workspace_id"],
            ["challenges.id", "challenges.workspace_id"],
            name="fk_question_clusters_challenge_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["analysis_generation_id", "workspace_id"],
            ["ai_generations.id", "ai_generations.workspace_id"],
            name="fk_question_clusters_generation_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["cluster_run_id", "workspace_id", "session_id"],
            [
                "ai_derived_artifacts.id",
                "ai_derived_artifacts.workspace_id",
                "ai_derived_artifacts.session_id",
            ],
            name="fk_question_clusters_run_artifact",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "id", "workspace_id", "session_id", "cluster_run_id", name="uq_question_clusters_identity"
        ),
    )
    op.create_index("ix_question_clusters_session", "question_clusters", ["session_id"])

    op.create_table(
        "question_cluster_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("question_cluster_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("cluster_run_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_question_cluster_memberships"),
        sa.ForeignKeyConstraint(
            ["question_cluster_id", "workspace_id", "session_id", "cluster_run_id"],
            [
                "question_clusters.id",
                "question_clusters.workspace_id",
                "question_clusters.session_id",
                "question_clusters.cluster_run_id",
            ],
            name="fk_question_cluster_memberships_cluster",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["question_id", "workspace_id"],
            ["questions.id", "questions.workspace_id"],
            name="fk_question_cluster_memberships_question_workspace",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "cluster_run_id", "question_id", name="uq_question_cluster_memberships_run_question"
        ),
    )
    op.create_index(
        "ix_question_cluster_memberships_cluster",
        "question_cluster_memberships",
        ["question_cluster_id"],
    )
    op.execute(
        """
        CREATE FUNCTION trg_question_cluster_memberships_frozen_member() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM burst_question_memberships m
                JOIN question_bursts b ON b.id = m.question_burst_id
                WHERE b.session_id = NEW.session_id
                  AND b.state = 'COMPLETED'
                  AND m.question_id = NEW.question_id
            ) THEN
                RAISE EXCEPTION
                    'a cluster may contain only Questions of the Session''s frozen set (F04 K1)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_question_cluster_memberships_frozen_member
        BEFORE INSERT ON question_cluster_memberships
        FOR EACH ROW EXECUTE FUNCTION trg_question_cluster_memberships_frozen_member();
        """
    )
    for table in _TABLES:
        op.execute(
            f"""
            CREATE FUNCTION trg_{table}_immutable() RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION '{table}: % rejected; a derived cluster run is append-only '
                    '(09 §34.1)', TG_OP;
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_immutable
            BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION trg_{table}_immutable();
            """
        )
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY workspace_isolation ON {table} "
            f"USING ({_RLS_EXPR}) WITH CHECK ({_RLS_EXPR})"
        )


def downgrade() -> None:
    for table in _TABLES:
        op.execute(f"DROP POLICY IF EXISTS workspace_isolation ON {table}")
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_immutable ON {table};")
        op.execute(f"DROP FUNCTION IF EXISTS trg_{table}_immutable();")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_question_cluster_memberships_frozen_member "
        "ON question_cluster_memberships;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_question_cluster_memberships_frozen_member();")
    op.drop_index(
        "ix_question_cluster_memberships_cluster", table_name="question_cluster_memberships"
    )
    op.drop_table("question_cluster_memberships")
    op.drop_index("ix_question_clusters_session", table_name="question_clusters")
    op.drop_table("question_clusters")
