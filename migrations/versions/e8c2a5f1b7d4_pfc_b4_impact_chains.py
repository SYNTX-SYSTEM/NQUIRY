"""PFC B4: ImpactChain and its answer nodes (09 §48; HD-26 / NQ-DEC-054)

Revision ID: e8c2a5f1b7d4
Revises: d4f7b2c9e6a1
Create Date: 2026-09-27 00:00:04.000000

WU-PFC-B4. The Five-Why ImpactChain (02 §28, 03 §40, 09 §48) under HD-26.

- `impact_chains` (09 §48 aggregate): `session_id`, `selected_question_id`,
  `created_at`, `record_version`, plus the Workspace and the creating human.
  S2(i): exactly one chain per (Session, primary Question) -- unique. The
  anchor must be the Session's PRIMARY QuestionSelection at creation
  (trigger). Every column but `record_version` is immutable, and
  `record_version` may only advance by exactly 1 (one append); DELETE is
  rejected.
- `impact_chain_nodes` (09 §48 owned nodes): `level` 1..5, `answer_content`,
  `author_user_id`, `captured_at`, plus the chain, Session and primary
  Question anchor on every node (HD-26 provenance), bound to the chain by a
  composite FK. S1(i): append-only (UPDATE / DELETE rejected). Levels are
  strictly successive: a node's level must be exactly one more than the
  chain's current highest level (trigger), and each level exists once.
  The node author must be the chain's creator (HD-26: one sole author).

Both tables are Workspace-scoped (RLS `workspace_isolation`). No AI column
exists (HD-26 rule 5).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e8c2a5f1b7d4"
down_revision = "d4f7b2c9e6a1"
branch_labels = None
depends_on = None

_RLS_EXPR = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"
_TABLES = ("impact_chains", "impact_chain_nodes")


def upgrade() -> None:
    op.create_table(
        "impact_chains",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("selected_question_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_impact_chains"),
        sa.ForeignKeyConstraint(
            ["session_id", "workspace_id"],
            ["sessions.id", "sessions.workspace_id"],
            name="fk_impact_chains_session_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["selected_question_id", "workspace_id"],
            ["questions.id", "questions.workspace_id"],
            name="fk_impact_chains_question_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_impact_chains_created_by",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "session_id", "selected_question_id", name="uq_impact_chains_session_primary"
        ),
        sa.UniqueConstraint(
            "id",
            "workspace_id",
            "session_id",
            "selected_question_id",
            "created_by_user_id",
            name="uq_impact_chains_identity",
        ),
        sa.CheckConstraint("record_version >= 1", name="ck_impact_chains_record_version"),
    )
    op.create_table(
        "impact_chain_nodes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("impact_chain_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("selected_question_id", sa.Uuid(), nullable=False),
        sa.Column("level", sa.SmallInteger(), nullable=False),
        sa.Column("answer_content", sa.Text(), nullable=False),
        sa.Column("author_user_id", sa.Uuid(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_impact_chain_nodes"),
        sa.ForeignKeyConstraint(
            [
                "impact_chain_id",
                "workspace_id",
                "session_id",
                "selected_question_id",
                "author_user_id",
            ],
            [
                "impact_chains.id",
                "impact_chains.workspace_id",
                "impact_chains.session_id",
                "impact_chains.selected_question_id",
                "impact_chains.created_by_user_id",
            ],
            name="fk_impact_chain_nodes_chain_identity",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("impact_chain_id", "level", name="uq_impact_chain_nodes_level"),
        sa.CheckConstraint("level BETWEEN 1 AND 5", name="ck_impact_chain_nodes_level"),
        sa.CheckConstraint(
            "length(btrim(answer_content)) > 0", name="ck_impact_chain_nodes_answer_present"
        ),
    )
    op.create_index("ix_impact_chains_session", "impact_chains", ["session_id"])

    op.execute(
        """
        CREATE FUNCTION trg_impact_chains_primary_anchor() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM question_selections
                WHERE session_id = NEW.session_id
                  AND question_id = NEW.selected_question_id
                  AND selection_type = 'PRIMARY'
                  AND selected_by_user_id = NEW.created_by_user_id
            ) THEN
                RAISE EXCEPTION
                    'impact_chains: the anchor must be the Session''s primary Question, '
                    'selected by the chain creator (HD-26)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_impact_chains_primary_anchor
        BEFORE INSERT ON impact_chains
        FOR EACH ROW EXECUTE FUNCTION trg_impact_chains_primary_anchor();
        """
    )
    op.execute(
        """
        CREATE FUNCTION trg_impact_chains_immutable() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'impact_chains: DELETE rejected (HD-26 S1)';
            END IF;
            IF NEW.id IS DISTINCT FROM OLD.id
               OR NEW.workspace_id IS DISTINCT FROM OLD.workspace_id
               OR NEW.session_id IS DISTINCT FROM OLD.session_id
               OR NEW.selected_question_id IS DISTINCT FROM OLD.selected_question_id
               OR NEW.created_by_user_id IS DISTINCT FROM OLD.created_by_user_id
               OR NEW.created_at IS DISTINCT FROM OLD.created_at
               OR NEW.record_version <> OLD.record_version + 1 THEN
                RAISE EXCEPTION
                    'impact_chains: only record_version may advance, by exactly 1 (HD-26 S1, S2)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_impact_chains_immutable
        BEFORE UPDATE OR DELETE ON impact_chains
        FOR EACH ROW EXECUTE FUNCTION trg_impact_chains_immutable();
        """
    )
    op.execute(
        """
        CREATE FUNCTION trg_impact_chain_nodes_successive() RETURNS trigger AS $$
        BEGIN
            PERFORM 1 FROM impact_chains WHERE id = NEW.impact_chain_id FOR UPDATE;
            IF NEW.level <> COALESCE(
                (SELECT MAX(level) FROM impact_chain_nodes
                 WHERE impact_chain_id = NEW.impact_chain_id), 0
            ) + 1 THEN
                RAISE EXCEPTION
                    'impact_chain_nodes: level % is not the next successive level (03 §40)',
                    NEW.level;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_impact_chain_nodes_successive
        BEFORE INSERT ON impact_chain_nodes
        FOR EACH ROW EXECUTE FUNCTION trg_impact_chain_nodes_successive();
        """
    )
    op.execute(
        """
        CREATE FUNCTION trg_impact_chain_nodes_immutable() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'impact_chain_nodes: % rejected; answers are append-only '
                '(HD-26 S1)', TG_OP;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_impact_chain_nodes_immutable
        BEFORE UPDATE OR DELETE ON impact_chain_nodes
        FOR EACH ROW EXECUTE FUNCTION trg_impact_chain_nodes_immutable();
        """
    )
    for table in _TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY workspace_isolation ON {table} "
            f"USING ({_RLS_EXPR}) WITH CHECK ({_RLS_EXPR})"
        )


def downgrade() -> None:
    for table in _TABLES:
        op.execute(f"DROP POLICY IF EXISTS workspace_isolation ON {table}")
    for trigger, table in (
        ("trg_impact_chain_nodes_immutable", "impact_chain_nodes"),
        ("trg_impact_chain_nodes_successive", "impact_chain_nodes"),
        ("trg_impact_chains_immutable", "impact_chains"),
        ("trg_impact_chains_primary_anchor", "impact_chains"),
    ):
        op.execute(f"DROP TRIGGER IF EXISTS {trigger} ON {table};")
        op.execute(f"DROP FUNCTION IF EXISTS {trigger}();")
    op.drop_table("impact_chain_nodes")
    op.drop_index("ix_impact_chains_session", table_name="impact_chains")
    op.drop_table("impact_chains")
