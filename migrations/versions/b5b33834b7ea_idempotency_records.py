"""idempotency records

Revision ID: b5b33834b7ea
Revises: b2f3a5d5096c
Create Date: 2026-09-18 14:00:00.000000

PKG-11 scope (14_IMPLEMENTATION_SEQUENCE.md section 9's conceptual
"008_command_attempt_idempotency" bucket lists "creates: commands,
attempts, idempotency | depends on: 001" as one summary row. PKG-10
materialized the commands/command_attempts half; this migration
completes the bucket with `idempotency_records` -- the same
one-conceptual-bucket-across-two-Alembic-revisions split PKG-02/PKG-05/
PKG-06/PKG-07 already established, applied a second time by PKG-10/
PKG-11.

No `commit writer` DB principal or GRANT is created here. 14 section
7.1 names it as the eventual write owner, but every DB-principal/GRANT/
RLS change in this codebase to date is deferred to migration
`012_security_events_rls` -- consistent with `b2f3a5d5096c` and every
migration since `001`.

Table created:

- `idempotency_records` (09 section 11, 14 section 27): the durable
  idempotency identity/lifecycle record. PRIMARY KEY is the composite
  `(workspace_id, command_type, idempotency_key)` -- 14 section 7.3's
  own words: "idempotency uniqueness includes Workspace, command type
  and idempotency key" -- rather than a surrogate id, because that
  triple *is* the identity 09/14 both define; no other table in this
  migration chain has needed a surrogate id for a relation whose
  natural key is already exactly what a consumer looks it up by.

  `command_id` carries a composite FK `(command_id, workspace_id) ->
  commands(id, workspace_id)` (`b2f3a5d5096c`'s own anchor), which
  makes an idempotency record referencing a forged or cross-Workspace
  `command_id` structurally unrepresentable -- the mandatory
  adversarial attack "cross-Workspace key collision" is defended at
  this layer independently of the application-level check in
  `packages/commit/idempotency.py`'s `decide_idempotency_action`.

  `latest_attempt_id` carries a plain (non-composite) FK to
  `command_attempts(id)` -- `command_attempts` has no `UNIQUE(id,
  workspace_id)` anchor of its own (its primary key `id` is already
  globally unique, so a simple FK is sufficient; retrofitting a
  composite anchor there, the way `d8a1147fde30` retrofitted one onto
  `sessions`, is not needed because nothing here composes a
  cross-table Workspace-consistency constraint against it).

  `commit_id` carries no foreign key: `commit_units` (14 section 7.1)
  is not created until migration `009_commit_audit_outbox` (PKG-13) --
  the same disclosed forward-reference gap `command_attempts.commit_id`
  (`b2f3a5d5096c`) already established.

  `outcome` is CHECK-constrained to 09 section 11's exact 4-value
  vocabulary (`IN_PROGRESS`, `FAILED_PRECOMMIT`, `COMMITTED`,
  `INDETERMINATE`) -- deliberately *not* the same 4 values as
  `command_attempts.outcome` (`DENIED` is absent here, `IN_PROGRESS` is
  present instead of it) -- see `packages/commit/idempotency.py`'s
  module docstring for why these are two genuinely distinct
  vocabularies, not a copy-paste of one into the other.

Triggers (14 section 7.3, same pattern as prior migrations):

1. `trg_idempotency_records_enforce_identity_immutable` (BEFORE
   UPDATE): rejects any change to `command_id`, `payload_fingerprint`,
   or `first_seen_at` -- the identity/receipt facts of a logical
   idempotent request never change after its first observation,
   mirroring `command_attempts`' own identity-immutability trigger
   (`b2f3a5d5096c`). (`workspace_id`/`command_type`/`idempotency_key`
   cannot change either, but that is already guaranteed by them being
   the primary key -- an UPDATE changing any of them is a different
   row by definition, not a mutation of this one.)

2. `trg_idempotency_records_enforce_outcome_transition` (BEFORE
   UPDATE): enforces 14 section 27's own transition rules exactly:
   `IN_PROGRESS -> {FAILED_PRECOMMIT, COMMITTED, INDETERMINATE}` and
   `FAILED_PRECOMMIT -> IN_PROGRESS` (a legitimate retry, which must
   also advance `latest_attempt_id`) are the only two legal outward
   moves; `COMMITTED` is fully terminal (09's own "prevent duplicate
   consequence" purpose: a committed idempotency record must never
   change again); `INDETERMINATE` is terminal *from this package's own
   write surface* -- 14 section 27 states only "no blind retry, route
   BND-017/BND-018" for this outcome, defining no legal next state for
   it, so no further transition out of `INDETERMINATE` is permitted by
   this trigger. A future recovery package (PKG-18+, once 10's BND-018
   is actually materialized) may need its own migration to open a
   governed path out of `INDETERMINATE` -- disclosed as a known
   limitation, not silently pre-authorized here.

No cascading delete anywhere (14 section 49 default). Schema downgrade
is infrastructure rollback only, not domain rollback (14 section 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b5b33834b7ea"
down_revision: str | None = "b2f3a5d5096c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 09 section 11's exact 4-value closed vocabulary.
_IDEMPOTENCY_OUTCOMES = ("IN_PROGRESS", "FAILED_PRECOMMIT", "COMMITTED", "INDETERMINATE")

# 14 section 27's exact 2 legal outward transitions.
_LEGAL_OUTCOME_TRANSITIONS_SQL = ", ".join(
    f"('{source}', '{target}')"
    for source, target in (
        ("IN_PROGRESS", "FAILED_PRECOMMIT"),
        ("IN_PROGRESS", "COMMITTED"),
        ("IN_PROGRESS", "INDETERMINATE"),
        ("FAILED_PRECOMMIT", "IN_PROGRESS"),
    )
)


def upgrade() -> None:
    op.create_table(
        "idempotency_records",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("command_type", sa.Text(), nullable=False),
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column("command_id", sa.Uuid(), nullable=False),
        sa.Column("payload_fingerprint", sa.Text(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latest_attempt_id", sa.Uuid(), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("commit_id", sa.Uuid(), nullable=True),
        sa.Column("result_ref", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint(
            "workspace_id", "command_type", "idempotency_key", name="pk_idempotency_records"
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_idempotency_records_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["command_id", "workspace_id"],
            ["commands.id", "commands.workspace_id"],
            name="fk_idempotency_records_command_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["latest_attempt_id"],
            ["command_attempts.id"],
            name="fk_idempotency_records_latest_attempt",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "command_type <> ''", name="ck_idempotency_records_command_type_nonempty"
        ),
        sa.CheckConstraint(
            "idempotency_key <> ''", name="ck_idempotency_records_idempotency_key_nonempty"
        ),
        sa.CheckConstraint(
            "payload_fingerprint <> ''", name="ck_idempotency_records_payload_fingerprint_nonempty"
        ),
        sa.CheckConstraint(
            "outcome IN (" + ", ".join(f"'{o}'" for o in _IDEMPOTENCY_OUTCOMES) + ")",
            name="ck_idempotency_records_outcome_vocabulary",
        ),
        sa.CheckConstraint(
            "(outcome = 'COMMITTED') = (commit_id IS NOT NULL)",
            name="ck_idempotency_records_commit_id_requires_committed",
        ),
        sa.CheckConstraint(
            "result_ref IS NULL OR outcome = 'COMMITTED'",
            name="ck_idempotency_records_result_ref_requires_committed",
        ),
    )
    op.create_index("ix_idempotency_records_command", "idempotency_records", ["command_id"])

    # Trigger 1: identity/receipt fields are immutable once set.
    op.execute(
        """
        CREATE FUNCTION trg_idempotency_records_enforce_identity_immutable() RETURNS trigger AS $$
        BEGIN
            IF NEW.command_id IS DISTINCT FROM OLD.command_id
                OR NEW.payload_fingerprint IS DISTINCT FROM OLD.payload_fingerprint
                OR NEW.first_seen_at IS DISTINCT FROM OLD.first_seen_at
            THEN
                RAISE EXCEPTION
                    'idempotency_records identity/receipt fields are immutable once set';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_idempotency_records_enforce_identity_immutable
        BEFORE UPDATE ON idempotency_records
        FOR EACH ROW EXECUTE FUNCTION trg_idempotency_records_enforce_identity_immutable();
        """
    )

    # Trigger 2: 14 section 27's exact outcome transition topology.
    op.execute(
        f"""
        CREATE FUNCTION trg_idempotency_records_enforce_outcome_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.outcome = 'COMMITTED' THEN
                RAISE EXCEPTION
                    'idempotency_records outcome COMMITTED is terminal (09 section 11)';
            END IF;
            IF OLD.outcome = 'INDETERMINATE' THEN
                RAISE EXCEPTION
                    'idempotency_records outcome INDETERMINATE has no legal next state '
                    'in this package (14 section 27: no blind retry)';
            END IF;
            IF NEW.outcome IS DISTINCT FROM OLD.outcome THEN
                IF NOT ((OLD.outcome, NEW.outcome) IN ({_LEGAL_OUTCOME_TRANSITIONS_SQL})) THEN
                    RAISE EXCEPTION
                        'illegal idempotency outcome transition % -> % (14 section 27)',
                        OLD.outcome, NEW.outcome;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_idempotency_records_enforce_outcome_transition
        BEFORE UPDATE ON idempotency_records
        FOR EACH ROW EXECUTE FUNCTION trg_idempotency_records_enforce_outcome_transition();
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_idempotency_records_enforce_outcome_transition "
        "ON idempotency_records;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_idempotency_records_enforce_outcome_transition();")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_idempotency_records_enforce_identity_immutable "
        "ON idempotency_records;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_idempotency_records_enforce_identity_immutable();")
    op.drop_index("ix_idempotency_records_command", table_name="idempotency_records")
    op.drop_table("idempotency_records")
