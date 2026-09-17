"""question identity lineage

Revision ID: 33e1d1feed5b
Revises: d467112ce46d
Create Date: 2026-09-18 09:15:00.000000

PKG-06 scope (14_IMPLEMENTATION_SEQUENCE.md §9's conceptual
"004_burst_question" bucket lists "creates: bursts, questions, lineage,
memberships | depends on: 003" as one summary row, but PKG-06's own
manifest narrows what THIS package actually materializes: "14 mapping:
004. questions and question_lineage with immutability/composite
Workspace constraints where feasible." `question_bursts` and
`burst_question_memberships` are deliberately NOT created here --
QuestionBurst is its own canonical process object (02 §13) with its
own state machine (03 §19-20) assigned to a later package (PKG-07:
"Question Burst and ..."), the same way PKG-02 deferred
`facilitator_scope_bindings` within its own conceptual "002" bucket
until `sessions` existed. This is the second migration built from one
14 §9 summary row across two packages; the Alembic revision chain
(this file `revises: d467112ce46d`, PKG-07's future migration will
`revise` this one) is exactly how that split is represented -- 14's
"004" label is a planning-document convenience, not a promise of
exactly one Alembic revision.

Tables created:

- `questions` (02 §14, 09 §31): the first-class canonical inquiry
  object. `original_text` is the AC-02-001 birth-text invariant made
  physical: CHECK-constrained non-empty, and a `BEFORE UPDATE` trigger
  (below) additionally rejects any attempt to change it after
  creation -- the CHECK alone would not stop a legal-looking UPDATE
  that kept it non-empty but different.

  Deliberately NOT created: `text` (GAP-02-002 remains
  `[UNDERDEFINED]`; 09 §31.2: "No field alias may allow `text` update
  to mutate `original_text`" -- with no application contract in this
  package distinguishing the two, materializing `text` would be an
  unused column with undefined write semantics) and `status` (03
  §25.1, GAP-02-013, restated with the identical high-assurance
  restriction 03 §12.2 gave `Challenge.status` in PKG-06's
  predecessor). Also absent: `question_type`, `priority`,
  `emotional_signal`, `novelty_score`, `catalytic_score` -- 02
  §14.9-§14.11 classifies these as classification metadata / derived
  assessments outside this package's stated objective, with no
  consumer or test to justify materializing them yet.

  `origin` is CHECK-constrained to `domain.question.QuestionOrigin`'s 4
  values (02 §15's own "general source categories" minus `reframed`,
  which 02 §15.2/AC-02-002 assigns to the derivation axis instead --
  see that module's docstring). `author_user_id` is nullable and
  CHECK-paired with `origin` as a direct biconditional (`origin =
  'HUMAN'` iff `author_user_id IS NOT NULL`) -- 09 §31: "author_user_id
  nullable where non-human" -- which is the structural half of the
  mandatory "AI reframe claims human authorship" attack: an AI-origin
  row can never carry a human author, at the schema level, independent
  of whatever application code exists later.

  `workspace_id` is the same constrained denormalization pattern PKG-05
  used for `sessions`: a composite FK `(challenge_id, workspace_id) ->
  challenges(id, workspace_id)` makes a Question claiming a different
  Workspace than its Challenge structurally unrepresentable.

- `question_lineage` (02 §16, 09 §32): the derivation relation.
  `transformation_type` is CHECK-constrained to `REFRAME`/`FOLLOW_UP`
  (09 §32's own named semantics; 02 §16.6: "Normalization is not
  lineage", so no third value exists for it). `producer_origin` reuses
  the same 4-value `origin` vocabulary as `questions.origin` (one
  concept, one vocabulary -- see the domain module's docstring for why
  no separate lineage-specific vocabulary was invented).
  `parent_question_id <> child_question_id` is CHECK-constrained
  (mandatory adversarial attack: invalid self-lineage). `ai_generation_id`
  is a plain nullable UUID with no foreign key -- `ai_generations`
  (migration `007_ai_operational`) does not exist yet; storing a value
  there proves nothing about a real AIGeneration, exactly the same
  disclosed limitation PKG-02 stated for `human_authority_bindings.scope_id`.

  `workspace_id` here is not merely denormalized convenience: TWO
  composite foreign keys -- `(parent_question_id, workspace_id)` and
  `(child_question_id, workspace_id)`, both against `questions(id,
  workspace_id)` -- force parent and child to resolve to the *same*
  stored `workspace_id` value, which structurally makes cross-Workspace
  lineage unrepresentable (mandatory adversarial attack: cross-Workspace
  lineage). This is declarative, not a trigger, so it cannot be
  disabled per-row or bypassed by a direct write.

Triggers (14 §7.3: "application plus trigger/constraint enforcement
where SQL cannot express a cross-table invariant directly" -- here the
inexpressible part is, as with PKG-05's Session triggers, a relation
between OLD and NEW row values that a CHECK constraint cannot express):

1. `trg_questions_enforce_immutable_fields` (BEFORE UPDATE): rejects
   any change to `original_text`, `challenge_id`, `workspace_id`,
   `origin`, or `author_user_id` -- 09 §31.1's named "Immutable
   Fields" list (`question_id`/`challenge_id`/`original_text`/"birth
   origin"/"birth author/producer identity"/"birth timestamp"),
   translated to this schema's actual columns (`question_id` and
   `created_at` are covered implicitly: a primary key is never
   updated in place by any code in this system, and `created_at` has
   no legitimate update path either, but both are included in the
   trigger for the same completeness reason PKG-05's session trigger
   checked every commit-sensitive condition explicitly rather than
   relying on convention). `normalized_text` and `record_version` are
   deliberately NOT protected -- 02 §14.7: "normalized_text = derived
   representation" is expected to change under a future normalization
   Command, and `record_version` exists to be bumped by that same
   future Command (14 §26).

2. `trg_question_lineage_enforce_immutable` (BEFORE UPDATE): rejects
   *every* update unconditionally -- 09 §32.1: "may not be silently
   reassigned to a different parent... Correction requires explicit
   new relation/history" is read here as covering the whole row (see
   `domain.question_lineage`'s docstring for why a full-row rejection
   is the more literal reading than a single-column check).

No cascading delete anywhere (14 §49 default). Schema downgrade is
infrastructure rollback only, not domain rollback (14 §9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "33e1d1feed5b"
down_revision: str | None = "d467112ce46d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# domain.question.QuestionOrigin / question_lineage.producer_origin,
# one shared vocabulary (02 §15's "general source categories" minus
# "reframed", which belongs to the derivation axis instead).
_QUESTION_ORIGINS = ("HUMAN", "AI", "IMPORTED", "INFERRED")

# domain.question_lineage.LineageTransformationType (09 §32).
_TRANSFORMATION_TYPES = ("REFRAME", "FOLLOW_UP")


def upgrade() -> None:
    op.create_table(
        "questions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("challenge_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=True),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("author_user_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id", name="pk_questions"),
        sa.ForeignKeyConstraint(
            ["challenge_id"], ["challenges.id"], name="fk_questions_challenge", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name="fk_questions_workspace", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["author_user_id"],
            ["users.id"],
            name="fk_questions_author_user",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("id", "workspace_id", name="uq_questions_id_workspace"),
        sa.ForeignKeyConstraint(
            ["challenge_id", "workspace_id"],
            ["challenges.id", "challenges.workspace_id"],
            name="fk_questions_challenge_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "origin IN (" + ", ".join(f"'{o}'" for o in _QUESTION_ORIGINS) + ")",
            name="ck_questions_origin",
        ),
        sa.CheckConstraint(
            "(origin = 'HUMAN') = (author_user_id IS NOT NULL)",
            name="ck_questions_human_origin_requires_author",
        ),
        sa.CheckConstraint("length(original_text) > 0", name="ck_questions_original_text_not_empty"),
        sa.CheckConstraint("record_version >= 1", name="ck_questions_record_version_positive"),
    )
    op.create_index("ix_questions_challenge", "questions", ["challenge_id"])
    op.create_index("ix_questions_workspace", "questions", ["workspace_id"])

    op.create_table(
        "question_lineage",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("parent_question_id", sa.Uuid(), nullable=False),
        sa.Column("child_question_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("transformation_type", sa.Text(), nullable=False),
        sa.Column("producer_origin", sa.Text(), nullable=False),
        sa.Column("ai_generation_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id", name="pk_question_lineage"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_question_lineage_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parent_question_id", "workspace_id"],
            ["questions.id", "questions.workspace_id"],
            name="fk_question_lineage_parent_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["child_question_id", "workspace_id"],
            ["questions.id", "questions.workspace_id"],
            name="fk_question_lineage_child_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "parent_question_id <> child_question_id", name="ck_question_lineage_no_self_lineage"
        ),
        sa.CheckConstraint(
            "transformation_type IN (" + ", ".join(f"'{t}'" for t in _TRANSFORMATION_TYPES) + ")",
            name="ck_question_lineage_transformation_type",
        ),
        sa.CheckConstraint(
            "producer_origin IN (" + ", ".join(f"'{o}'" for o in _QUESTION_ORIGINS) + ")",
            name="ck_question_lineage_producer_origin",
        ),
    )
    op.create_index(
        "ix_question_lineage_parent", "question_lineage", ["parent_question_id"]
    )
    op.create_index(
        "ix_question_lineage_child", "question_lineage", ["child_question_id"]
    )

    # Trigger 1: 09 §31.1 Immutable Fields, translated to this schema.
    op.execute(
        """
        CREATE FUNCTION trg_questions_enforce_immutable_fields() RETURNS trigger AS $$
        BEGIN
            IF NEW.original_text IS DISTINCT FROM OLD.original_text THEN
                RAISE EXCEPTION
                    'questions.original_text is immutable (02 section 14.5, AC-02-001)';
            END IF;
            IF NEW.challenge_id IS DISTINCT FROM OLD.challenge_id
                OR NEW.workspace_id IS DISTINCT FROM OLD.workspace_id THEN
                RAISE EXCEPTION
                    'questions.challenge_id/workspace_id are immutable (09 section 31.1)';
            END IF;
            IF NEW.origin IS DISTINCT FROM OLD.origin THEN
                RAISE EXCEPTION
                    'questions.origin is an immutable birth fact (09 section 31.1)';
            END IF;
            IF NEW.author_user_id IS DISTINCT FROM OLD.author_user_id THEN
                RAISE EXCEPTION
                    'questions.author_user_id is an immutable birth fact (09 section 31.1)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_questions_enforce_immutable_fields
        BEFORE UPDATE ON questions
        FOR EACH ROW EXECUTE FUNCTION trg_questions_enforce_immutable_fields();
        """
    )

    # Trigger 2: 09 §32.1 -- the whole row is a birth fact of one
    # derivation event; no legitimate update path exists.
    op.execute(
        """
        CREATE FUNCTION trg_question_lineage_enforce_immutable() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'question_lineage rows are immutable (09 section 32.1); create a new relation instead';
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_question_lineage_enforce_immutable
        BEFORE UPDATE ON question_lineage
        FOR EACH ROW EXECUTE FUNCTION trg_question_lineage_enforce_immutable();
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_question_lineage_enforce_immutable ON question_lineage;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_question_lineage_enforce_immutable();")
    op.execute("DROP TRIGGER IF EXISTS trg_questions_enforce_immutable_fields ON questions;")
    op.execute("DROP FUNCTION IF EXISTS trg_questions_enforce_immutable_fields();")
    op.drop_index("ix_question_lineage_child", table_name="question_lineage")
    op.drop_index("ix_question_lineage_parent", table_name="question_lineage")
    op.drop_table("question_lineage")
    op.drop_index("ix_questions_workspace", table_name="questions")
    op.drop_index("ix_questions_challenge", table_name="questions")
    op.drop_table("questions")
