"""burst and membership

Revision ID: d8a1147fde30
Revises: 33e1d1feed5b
Create Date: 2026-09-18 11:00:00.000000

PKG-07 scope (14_IMPLEMENTATION_SEQUENCE.md §9's conceptual
"004_burst_question" bucket lists "creates: bursts, questions, lineage,
memberships | depends on: 003" as one summary row; PKG-06 materialized
the questions/lineage half, this migration completes the bucket with
`question_bursts`/`burst_question_memberships` -- the same
one-conceptual-bucket-across-two-Alembic-revisions split PKG-02/PKG-05/
PKG-06 already established for `facilitator_scope_bindings` and this
package's own predecessor tables.

Retrofit: `uq_sessions_id_workspace` on `sessions`
---------------------------------------------------
`sessions` (migration `d467112ce46d`, PKG-05) had no `UNIQUE(id,
workspace_id)` anchor of its own -- nothing needed one yet, since PKG-05
only needed `sessions` to be the *target* of `challenges`' own anchor,
never the anchor itself. `question_bursts` (below) needs to compose a
Workspace-consistency composite FK against `sessions`, exactly the
pattern `sessions` itself already uses against `challenges` -- so this
migration adds the missing anchor. This is additive schema evolution on
a predecessor's table (permitted: 14 §9's migration chain is meant to
grow this way), not a rewrite of `d467112ce46d`'s own DDL.

Tables created:

- `question_bursts` (02 §13, 03 §19, 09 §29): the protected raw-capture
  process object. `state` is CHECK-constrained to 03 §19.1's 4 values.
  `mode` is CHECK-constrained twice: once to 09 §29.1's full 3-value
  approved vocabulary (`ck_question_bursts_mode`), and a second,
  separately named constraint restricting production rows in *this*
  package's scope to exactly `HUMAN_ONLY`
  (`ck_question_bursts_mode_human_only_scope`) -- 08 §12.2/12.3 leave
  Mode B ("Prototype inclusion remains unresolved") and Mode C
  unimplemented here; a future package implementing them removes only
  the second constraint, never the first (the approved vocabulary
  itself is not in question). `workspace_id` is the same constrained
  denormalization pattern as `sessions`/`questions`: a composite FK
  `(session_id, workspace_id) -> sessions(id, workspace_id)` makes a
  Burst claiming a different Workspace than its Session structurally
  unrepresentable.

  Deliberately NOT created: `configured_duration_ref`/`value` or
  `timer_basis_ref`. 03 §21 (CONFLICT-007) and §22 (GAP-03-002) leave
  Burst duration/timer semantics unresolved and explicitly forbid
  inventing them before closure; this package implements "Manual
  authorized completion only. No automatic timer."

  `frozen_membership_fingerprint` materializes 14 §19's
  `[IMPLEMENTATION CHOICE]`: "canonical sorted serialization of
  membership IDs plus Question content versions. Hash establishes
  identity/integrity relation only" -- populated exactly once, at
  COMPLETE_BURST, by application code computing it from durable
  membership rows already committed (`packages/persistence/burst_repository.py`
  documents the exact algorithm). CHECK-paired with `state='COMPLETED'`
  as a direct biconditional (03 §19.5: raw membership is frozen exactly
  when, and only when, the Burst is COMPLETED).

- `burst_question_memberships` (02 §17, 09 §30): the frozen
  raw-capture relation. TWO composite FKs -- `(question_burst_id,
  workspace_id)` and `(question_id, workspace_id)`, both against a
  parent table's own `(id, workspace_id)` anchor -- force the Burst and
  its captured Question to share one Workspace, the identical
  cross-Workspace-lineage-prevention pattern PKG-06 established for
  `question_lineage`. `UNIQUE(question_id)` (declared inline on the
  column in `persistence/tables.py`, expressed as a table-level
  constraint here): 03 TRN-Q-001 creates a Question and its Burst
  capture membership together, as one capture event -- a Question
  belongs to at most one originating Burst capture, ever.
  `capture_origin` is CHECK-constrained twice, mirroring `mode` above:
  once to `questions.origin`'s full 4-value approved vocabulary (the
  same shared vocabulary, not a new one -- see `domain.burst_membership`'s
  docstring), and a second, separately named constraint restricting
  this package's own captures to exactly `HUMAN` (09 §30's
  "AI-origin mode contribution" is Mode B/C territory, out of scope
  here). `capture_actor_user_id`/`capture_origin` are CHECK-paired with
  the identical biconditional PKG-06 established for
  `questions.author_user_id`/`origin`.

Triggers (14 §7.3, same pattern as PKG-05/06's migrations):

1. `trg_question_bursts_enforce_initial_state` (BEFORE INSERT): a new
   Burst must be PREPARED (03 TRN-BURST-001 NEXT STATE).

2. `trg_question_bursts_enforce_transition` (BEFORE UPDATE): if
   `OLD.state = 'COMPLETED'`, reject the update unconditionally --
   *any* field, not only `state` (03 §19.5: COMPLETED is terminal, and
   `frozen_membership_fingerprint` must never change once set).
   Otherwise, if `state` changes, the `(OLD.state, NEW.state)` pair
   must appear in 03 §20's 5-pair allow-list (which includes
   TRN-BURST-005's two legal sources, `ACTIVE -> COMPLETED` and
   `PAUSED -> COMPLETED`), and `record_version` must strictly advance
   -- identical discipline to `sessions`' own transition trigger
   (PKG-05).

3. `trg_burst_memberships_enforce_freeze` (BEFORE INSERT OR DELETE):
   looks up the referenced `question_bursts.state` for `NEW.question_burst_id`
   (INSERT) or `OLD.question_burst_id` (DELETE); if it is `COMPLETED`,
   rejects the operation. This is the direct enforcement of the
   mandatory adversarial attacks "add raw member after freeze" and
   "remove member after freeze", and of 06 §14's DENY: "After
   COMPLETED: new raw-set membership."

4. `trg_burst_memberships_enforce_immutable` (BEFORE UPDATE): rejects
   every update unconditionally -- no field of a specific capture event
   is ever legitimately mutable (mirrors `question_lineage`'s identical
   full-row immutability trigger, PKG-06).

No cascading delete anywhere (14 §49 default). Schema downgrade is
infrastructure rollback only, not domain rollback (14 §9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d8a1147fde30"
down_revision: str | None = "33e1d1feed5b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 03 §19.1.
_BURST_STATES = ("PREPARED", "ACTIVE", "PAUSED", "COMPLETED")

# 09 §29.1's full approved vocabulary.
_BURST_MODES = ("HUMAN_ONLY", "HUMAN_PLUS_AI", "AI_CHALLENGE_AFTER_HUMANS")

# domain.question.QuestionOrigin / questions.origin's shared vocabulary.
_QUESTION_ORIGINS = ("HUMAN", "AI", "IMPORTED", "INFERRED")

# 03 §20's 5 transitions, expanded so TRN-BURST-005's two sources each
# appear as their own pair.
_LEGAL_BURST_TRANSITIONS_SQL = ", ".join(
    f"('{source}', '{target}')"
    for source, target in (
        ("PREPARED", "ACTIVE"),
        ("ACTIVE", "PAUSED"),
        ("PAUSED", "ACTIVE"),
        ("ACTIVE", "COMPLETED"),
        ("PAUSED", "COMPLETED"),
    )
)


def upgrade() -> None:
    op.create_unique_constraint("uq_sessions_id_workspace", "sessions", ["id", "workspace_id"])

    op.create_table(
        "question_bursts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("mode", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("frozen_membership_fingerprint", sa.Text(), nullable=True),
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id", name="pk_question_bursts"),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name="fk_question_bursts_workspace", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "workspace_id"],
            ["sessions.id", "sessions.workspace_id"],
            name="fk_question_bursts_session_workspace",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("id", "workspace_id", name="uq_question_bursts_id_workspace"),
        sa.CheckConstraint(
            "state IN (" + ", ".join(f"'{s}'" for s in _BURST_STATES) + ")",
            name="ck_question_bursts_state",
        ),
        sa.CheckConstraint(
            "mode IN (" + ", ".join(f"'{m}'" for m in _BURST_MODES) + ")",
            name="ck_question_bursts_mode",
        ),
        sa.CheckConstraint("mode = 'HUMAN_ONLY'", name="ck_question_bursts_mode_human_only_scope"),
        sa.CheckConstraint(
            "(state = 'COMPLETED') = (frozen_membership_fingerprint IS NOT NULL)",
            name="ck_question_bursts_freeze_requires_completed",
        ),
        sa.CheckConstraint(
            "completed_at IS NULL OR state = 'COMPLETED'",
            name="ck_question_bursts_completed_at_requires_completed",
        ),
        sa.CheckConstraint(
            "record_version >= 1", name="ck_question_bursts_record_version_positive"
        ),
    )
    op.create_index("ix_question_bursts_session", "question_bursts", ["session_id"])
    op.create_index("ix_question_bursts_workspace", "question_bursts", ["workspace_id"])

    op.create_table(
        "burst_question_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("question_burst_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("captured_order", sa.Integer(), nullable=False),
        sa.Column(
            "captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("capture_actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("capture_origin", sa.Text(), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id", name="pk_burst_question_memberships"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_burst_memberships_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["question_burst_id", "workspace_id"],
            ["question_bursts.id", "question_bursts.workspace_id"],
            name="fk_burst_memberships_burst_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["question_id", "workspace_id"],
            ["questions.id", "questions.workspace_id"],
            name="fk_burst_memberships_question_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["capture_actor_user_id"],
            ["users.id"],
            name="fk_burst_memberships_capture_actor",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("question_id", name="uq_burst_memberships_question"),
        sa.CheckConstraint(
            "capture_origin IN (" + ", ".join(f"'{o}'" for o in _QUESTION_ORIGINS) + ")",
            name="ck_burst_memberships_capture_origin",
        ),
        sa.CheckConstraint(
            "capture_origin = 'HUMAN'", name="ck_burst_memberships_capture_origin_human_only_scope"
        ),
        sa.CheckConstraint(
            "(capture_origin = 'HUMAN') = (capture_actor_user_id IS NOT NULL)",
            name="ck_burst_memberships_human_origin_requires_actor",
        ),
        sa.CheckConstraint("captured_order >= 0", name="ck_burst_memberships_captured_order_valid"),
        sa.CheckConstraint(
            "record_version >= 1", name="ck_burst_memberships_record_version_positive"
        ),
    )
    op.create_index("ix_burst_memberships_burst", "burst_question_memberships", ["question_burst_id"])

    # Trigger 1: 03 TRN-BURST-001 NEXT STATE: PREPARED.
    op.execute(
        """
        CREATE FUNCTION trg_question_bursts_enforce_initial_state() RETURNS trigger AS $$
        BEGIN
            IF NEW.state <> 'PREPARED' THEN
                RAISE EXCEPTION
                    'question burst must be created in PREPARED (03 TRN-BURST-001), got %',
                    NEW.state;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_question_bursts_enforce_initial_state
        BEFORE INSERT ON question_bursts
        FOR EACH ROW EXECUTE FUNCTION trg_question_bursts_enforce_initial_state();
        """
    )

    # Trigger 2: 03 section 19.5 (COMPLETED terminal, full-row) + 03
    # section 20 topology (state-change pairs) + 14 section 26
    # (record_version must advance).
    op.execute(
        f"""
        CREATE FUNCTION trg_question_bursts_enforce_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.state = 'COMPLETED' THEN
                RAISE EXCEPTION
                    'question burst is COMPLETED and immutable (03 section 19.5)';
            END IF;
            IF NEW.state IS DISTINCT FROM OLD.state THEN
                IF NOT ((OLD.state, NEW.state) IN ({_LEGAL_BURST_TRANSITIONS_SQL})) THEN
                    RAISE EXCEPTION
                        'illegal burst transition % -> % (03 section 20)',
                        OLD.state, NEW.state;
                END IF;
                IF NEW.record_version <= OLD.record_version THEN
                    RAISE EXCEPTION
                        'burst state change must advance record_version (14 section 26), % -> %',
                        OLD.record_version, NEW.record_version;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_question_bursts_enforce_transition
        BEFORE UPDATE ON question_bursts
        FOR EACH ROW EXECUTE FUNCTION trg_question_bursts_enforce_transition();
        """
    )

    # Trigger 3: mandatory adversarial attacks "add raw member after
    # freeze" (INSERT) and "remove member after freeze" (DELETE); 06
    # section 14 DENY "After COMPLETED: new raw-set membership."
    op.execute(
        """
        CREATE FUNCTION trg_burst_memberships_enforce_freeze() RETURNS trigger AS $$
        DECLARE
            burst_state TEXT;
            target_burst_id UUID;
        BEGIN
            IF TG_OP = 'DELETE' THEN
                target_burst_id := OLD.question_burst_id;
            ELSE
                target_burst_id := NEW.question_burst_id;
            END IF;
            SELECT state INTO burst_state FROM question_bursts WHERE id = target_burst_id;
            IF burst_state = 'COMPLETED' THEN
                RAISE EXCEPTION
                    'burst % is COMPLETED; raw membership is frozen (03 section 19.5, 06 section 14)',
                    target_burst_id;
            END IF;
            IF TG_OP = 'DELETE' THEN
                RETURN OLD;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_burst_memberships_enforce_freeze
        BEFORE INSERT OR DELETE ON burst_question_memberships
        FOR EACH ROW EXECUTE FUNCTION trg_burst_memberships_enforce_freeze();
        """
    )

    # Trigger 4: no field of a capture-event relation is ever
    # legitimately mutable (mirrors question_lineage, PKG-06).
    op.execute(
        """
        CREATE FUNCTION trg_burst_memberships_enforce_immutable() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'burst_question_memberships rows are immutable; create a new relation instead';
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_burst_memberships_enforce_immutable
        BEFORE UPDATE ON burst_question_memberships
        FOR EACH ROW EXECUTE FUNCTION trg_burst_memberships_enforce_immutable();
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_burst_memberships_enforce_immutable ON burst_question_memberships;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_burst_memberships_enforce_immutable();")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_burst_memberships_enforce_freeze ON burst_question_memberships;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_burst_memberships_enforce_freeze();")
    op.execute("DROP TRIGGER IF EXISTS trg_question_bursts_enforce_transition ON question_bursts;")
    op.execute("DROP FUNCTION IF EXISTS trg_question_bursts_enforce_transition();")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_question_bursts_enforce_initial_state ON question_bursts;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_question_bursts_enforce_initial_state();")
    op.drop_index("ix_burst_memberships_burst", table_name="burst_question_memberships")
    op.drop_table("burst_question_memberships")
    op.drop_index("ix_question_bursts_workspace", table_name="question_bursts")
    op.drop_index("ix_question_bursts_session", table_name="question_bursts")
    op.drop_table("question_bursts")
    op.drop_constraint("uq_sessions_id_workspace", "sessions", type_="unique")
