"""decisions

Revision ID: e2f94137f8a9
Revises: d9d99d8d2869
Create Date: 2026-09-19 09:00:00.000000

PKG-15 scope (14_IMPLEMENTATION_SEQUENCE.md section 9: "005_selection_decision
| creates: selections, decisions | depends on: 004,002"). PKG-14 materialized
the `selections` half; this migration completes the bucket with `decisions`
-- the same one-conceptual-bucket-across-two-Alembic-revisions split
PKG-02/PKG-05, PKG-06/PKG-07, PKG-10/PKG-11, PKG-12/PKG-13, and PKG-14/PKG-15
already established, applied a sixth time.

Table created:

- `decisions` (09 section 47: exact field list -- `decision_id` as this
  table's own `id`, `decision_question_ref/text` split into two nullable
  columns, `options`/`criteria` as `ARRAY(TEXT)`, `state` from 03 section
  35.2's exact 2-value closed vocabulary). `workspace_id` is the same
  disclosed technical necessity every other protected table already
  carries.

  Composite FK `(challenge_id, workspace_id) -> challenges(id, workspace_id)`
  makes a cross-Workspace Decision-to-Challenge reference structurally
  unrepresentable. Composite FK `(decision_question_ref, workspace_id) ->
  questions(id, workspace_id)`, nullable, does the same for the optional
  Question reference.

  `decision_authority_binding_id` carries NO foreign key: identical
  disclosed treatment to `question_selections.human_authority_binding_id`
  (PKG-14) and `audit_events.authority_source_ref` (PKG-12) --
  `human_authority_bindings` has no `UNIQUE(id, workspace_id)` anchor, and
  09 section 47's own field is a proof reference, not a live authorization
  join.

  `state` is CHECK-constrained to 03 section 35.2's exact 2-value
  vocabulary. A second CHECK enforces the DECIDED<->attribution
  biconditional at the database layer, mirroring `domain.decision.Decision.__post_init__`'s
  own Python-layer check (03 TRN-DEC-002's own RECOVERY/ROLLBACK
  REQUIREMENT: "Failure must not leave an apparently DECIDED record
  without provable human authority") -- defense in depth, the same
  precedent PKG-06 established for Question's HUMAN-origin/author-id
  biconditional.

  Two triggers enforce 03 section 36's transition topology, mirroring
  `sessions`' own two-trigger precedent (PKG-05) exactly: a new row must
  be created `UNDER_CONSIDERATION` (TRN-DEC-001's own "CURRENT STATE:
  Decision absent" -- there is exactly one entry point), and an UPDATE
  may only move `UNDER_CONSIDERATION -> DECIDED`, never any other pair --
  `DECIDED` is therefore terminal at the database layer too (03 section 38,
  GAP-03-005: "03 does not permit DECIDED -> UNDER_CONSIDERATION as a
  silent rewrite"; since no other post-DECIDED transition is defined
  anywhere in 03, this migration blocks every further UPDATE once
  DECIDED, not merely the one named illegal reversal).

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
revision: str = "e2f94137f8a9"
down_revision: str | None = "d9d99d8d2869"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 03 section 35.2's exact 2-value closed vocabulary.
_DECISION_STATES = ("UNDER_CONSIDERATION", "DECIDED")


def upgrade() -> None:
    op.create_table(
        "decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("challenge_id", sa.Uuid(), nullable=False),
        sa.Column("decision_question_ref", sa.Uuid(), nullable=True),
        sa.Column("decision_question_text", sa.Text(), nullable=True),
        sa.Column("options", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("criteria", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("selected_option", sa.Text(), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Text(), nullable=True),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("opened_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("decision_authority_binding_id", sa.Uuid(), nullable=False),
        sa.Column("decided_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("record_version", sa.BigInteger(), nullable=False),
        sa.Column("provenance_ref", sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_decisions"),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name="fk_decisions_workspace", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["challenge_id", "workspace_id"],
            ["challenges.id", "challenges.workspace_id"],
            name="fk_decisions_challenge_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["decision_question_ref", "workspace_id"],
            ["questions.id", "questions.workspace_id"],
            name="fk_decisions_question_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["opened_by_user_id"],
            ["users.id"],
            name="fk_decisions_opened_by_user",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["decided_by_user_id"],
            ["users.id"],
            name="fk_decisions_decided_by_user",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "state IN (" + ", ".join(f"'{s}'" for s in _DECISION_STATES) + ")",
            name="ck_decisions_state_vocabulary",
        ),
        sa.CheckConstraint(
            "(state = 'DECIDED' AND decided_by_user_id IS NOT NULL "
            "AND decided_at IS NOT NULL AND selected_option IS NOT NULL) "
            "OR (state = 'UNDER_CONSIDERATION' AND decided_by_user_id IS NULL "
            "AND decided_at IS NULL)",
            name="ck_decisions_decided_attribution",
        ),
    )
    op.create_index("ix_decisions_workspace", "decisions", ["workspace_id"])
    op.create_index("ix_decisions_challenge", "decisions", ["challenge_id"])

    # Trigger 1: TRN-DEC-001's own "CURRENT STATE: Decision absent" --
    # exactly one entry point, mirroring trg_sessions_enforce_initial_state.
    op.execute(
        """
        CREATE FUNCTION trg_decisions_enforce_initial_state() RETURNS trigger AS $$
        BEGIN
            IF NEW.state <> 'UNDER_CONSIDERATION' THEN
                RAISE EXCEPTION
                    'decision must be created in UNDER_CONSIDERATION (03 TRN-DEC-001), got %',
                    NEW.state;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_decisions_enforce_initial_state
        BEFORE INSERT ON decisions
        FOR EACH ROW EXECUTE FUNCTION trg_decisions_enforce_initial_state();
        """
    )

    # Trigger 2: 03 section 36/38 topology -- the only legal UPDATE pair
    # is UNDER_CONSIDERATION -> DECIDED; DECIDED is terminal (no further
    # UPDATE of any kind), mirroring trg_sessions_enforce_transition's
    # default-DENY posture.
    op.execute(
        """
        CREATE FUNCTION trg_decisions_enforce_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.state = 'DECIDED' THEN
                RAISE EXCEPTION
                    'decisions: decision % is DECIDED, which is terminal (03 section 38) -- no further update is permitted',
                    OLD.id;
            END IF;
            IF NEW.state IS DISTINCT FROM OLD.state THEN
                IF NOT (OLD.state = 'UNDER_CONSIDERATION' AND NEW.state = 'DECIDED') THEN
                    RAISE EXCEPTION
                        'illegal decision transition % -> % (03 section 36/38)',
                        OLD.state, NEW.state;
                END IF;
                IF NEW.record_version <= OLD.record_version THEN
                    RAISE EXCEPTION
                        'decision state change must advance record_version (14 section 26), % -> %',
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
        CREATE TRIGGER trg_decisions_enforce_transition
        BEFORE UPDATE ON decisions
        FOR EACH ROW EXECUTE FUNCTION trg_decisions_enforce_transition();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_decisions_enforce_transition ON decisions;")
    op.execute("DROP FUNCTION IF EXISTS trg_decisions_enforce_transition();")
    op.execute("DROP TRIGGER IF EXISTS trg_decisions_enforce_initial_state ON decisions;")
    op.execute("DROP FUNCTION IF EXISTS trg_decisions_enforce_initial_state();")
    op.drop_index("ix_decisions_challenge", table_name="decisions")
    op.drop_index("ix_decisions_workspace", table_name="decisions")
    op.drop_table("decisions")
