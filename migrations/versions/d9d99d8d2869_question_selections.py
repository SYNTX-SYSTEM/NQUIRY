"""question selections

Revision ID: d9d99d8d2869
Revises: b06f9a5b3d1b
Create Date: 2026-09-18 20:00:00.000000

PKG-14 scope (14_IMPLEMENTATION_SEQUENCE.md section 9: "005_selection_decision
| creates: selections, decisions | depends on: 004,002"). PKG-14 materializes
the `selections` half only -- `decisions` is deferred to whichever future
package (PKG-15, Human Decision) needs it, the same one-conceptual-bucket-
across-two-Alembic-revisions split PKG-02/PKG-05, PKG-06/PKG-07,
PKG-10/PKG-11, and PKG-12/PKG-13 already established, applied a fifth time.

Table created:

- `question_selections` (09 section 33: exact field list --
  `question_selection_id, session_id, question_id, selection_type,
  selected_by_user_id, human_authority_binding_id, selected_at,
  record_version`; `id` is this table's own `question_selection_id`).
  `workspace_id` is the same disclosed technical necessity 14 section 49
  ("workspace_id on protected records: S") already required for every
  protected table since `sessions`/`questions` -- not an addition to 09's
  contract, the same treatment those two tables already received.

  Composite FKs `(session_id, workspace_id) -> sessions(id, workspace_id)`
  and `(question_id, workspace_id) -> questions(id, workspace_id)` make a
  cross-Workspace Session or Question reference structurally
  unrepresentable, the identical pattern every composite FK in this
  codebase already establishes.

  `human_authority_binding_id` carries NO foreign key: `human_authority_
  bindings` has no `UNIQUE(id, workspace_id)` anchor (it was never given
  one, unlike `sessions`/`questions`/`commands`/`commit_units`), and 09
  section 33.1 itself states "That stored binding reference does not
  authorize future changes" -- this is a proof reference, not a live
  authorization join, the same disclosed treatment
  `audit_events.authority_source_ref` (PKG-12) already established for a
  comparable polymorphic-authority reference.

  `selection_type` is CHECK-constrained to 09 section 33's exact 2-value
  closed vocabulary (`COMPELLING`, `PRIMARY`).

  `UNIQUE(session_id, question_id, selection_type)` makes a literal
  duplicate selection (same Question, same type, same Session)
  structurally impossible -- mandatory adversarial attack "duplicate
  selection where relation semantics forbid it", first line of defense.

  A partial unique index enforces 04 section 42 AUTH-DEP-SEL-002's own
  "No conflicting primary selection unless governed replacement is
  defined" -- at most one `PRIMARY` row may exist per Session; no
  governed-replacement path exists in this build phase, so a second
  PRIMARY attempt is unconditionally rejected, not silently superseded.

  A trigger enforces 04 section 41 AUTH-DEP-SEL-001's own "1 to 3
  compelling Questions" cardinality cap -- a `CHECK` constraint cannot
  express a cross-row COUNT, so this is PL/pgSQL, mirroring the
  precedent PKG-02's `trg_habb_check_grant_preconditions` already
  established for a precondition no foreign key or CHECK can state.

No `governed_commit_writer`/DB-principal separation is created here,
consistent with every migration since `001` (deferred to
`012_security_events_rls`). No cascading delete anywhere (14 section 49
default). Schema downgrade is infrastructure rollback only, not domain
rollback (14 section 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d9d99d8d2869"
down_revision: str | None = "b06f9a5b3d1b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 09 section 33's exact 2-value closed vocabulary.
_SELECTION_TYPES = ("COMPELLING", "PRIMARY")

_MAX_COMPELLING_PER_SESSION = 3


def upgrade() -> None:
    op.create_table(
        "question_selections",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("selection_type", sa.Text(), nullable=False),
        sa.Column("selected_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("human_authority_binding_id", sa.Uuid(), nullable=False),
        sa.Column("selected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_question_selections"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_question_selections_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "workspace_id"],
            ["sessions.id", "sessions.workspace_id"],
            name="fk_question_selections_session_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["question_id", "workspace_id"],
            ["questions.id", "questions.workspace_id"],
            name="fk_question_selections_question_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["selected_by_user_id"],
            ["users.id"],
            name="fk_question_selections_selected_by_user",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "selection_type IN (" + ", ".join(f"'{t}'" for t in _SELECTION_TYPES) + ")",
            name="ck_question_selections_selection_type",
        ),
        sa.UniqueConstraint(
            "session_id",
            "question_id",
            "selection_type",
            name="uq_question_selections_session_question_type",
        ),
    )
    op.create_index("ix_question_selections_workspace", "question_selections", ["workspace_id"])
    op.create_index("ix_question_selections_session", "question_selections", ["session_id"])

    # 04 section 42 AUTH-DEP-SEL-002: at most one PRIMARY selection per
    # Session (no governed-replacement path exists yet).
    op.execute(
        """
        CREATE UNIQUE INDEX uq_question_selections_primary_per_session
        ON question_selections (session_id)
        WHERE selection_type = 'PRIMARY';
        """
    )

    # 04 section 41 AUTH-DEP-SEL-001: 1 to 3 compelling Questions per
    # Session -- a cross-row COUNT, not expressible as a CHECK constraint.
    op.execute(
        f"""
        CREATE FUNCTION trg_question_selections_compelling_cardinality() RETURNS trigger AS $$
        BEGIN
            IF NEW.selection_type = 'COMPELLING' THEN
                IF (
                    SELECT COUNT(*) FROM question_selections
                    WHERE session_id = NEW.session_id
                      AND selection_type = 'COMPELLING'
                ) >= {_MAX_COMPELLING_PER_SESSION} THEN
                    RAISE EXCEPTION
                        'question_selections: Session % already has % COMPELLING'
                        ' selections (04 section 41 cardinality cap)',
                        NEW.session_id, {_MAX_COMPELLING_PER_SESSION};
                END IF;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_question_selections_compelling_cardinality
        BEFORE INSERT ON question_selections
        FOR EACH ROW EXECUTE FUNCTION trg_question_selections_compelling_cardinality();
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_question_selections_compelling_cardinality "
        "ON question_selections;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_question_selections_compelling_cardinality();")
    op.execute("DROP INDEX IF EXISTS uq_question_selections_primary_per_session;")
    op.drop_index("ix_question_selections_session", table_name="question_selections")
    op.drop_index("ix_question_selections_workspace", table_name="question_selections")
    op.drop_table("question_selections")
