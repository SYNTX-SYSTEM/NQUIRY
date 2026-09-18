"""command envelope and attempts

Revision ID: b2f3a5d5096c
Revises: d8a1147fde30
Create Date: 2026-09-18 12:00:00.000000

PKG-10 scope (14_IMPLEMENTATION_SEQUENCE.md §9's conceptual
"008_command_attempt_idempotency" bucket lists "creates: commands,
attempts, idempotency | depends on: 001" as one summary row. This
migration materializes only the `commands`/`command_attempts` half --
PKG-10's own manifest is "Command contracts, registry, attempts and
expected versions" (PUBLIC_INTERFACES: CommandEnvelope, CommandRegistry).
`idempotency_records` is PKG-11's own PUBLIC_INTERFACES
(IdempotencyPort) and is deliberately NOT created here -- the same
one-conceptual-bucket-across-two-Alembic-revisions split PKG-02/PKG-05/
PKG-06/PKG-07 already established for `facilitator_scope_bindings` and
the `question_bursts`/`burst_question_memberships` pair.

No `command_processor`/`commit_writer` DB principal or GRANT is created
here. 14 §7.1 names those as the eventual write owners of these tables,
but every DB-principal/GRANT/RLS change in this codebase so far has been
deferred to migration `012_security_events_rls` ("RLS/policies/grants")
-- no earlier migration has created one either (see `01a37c093cd6`
through `d8a1147fde30`). Disclosed, not silently accepted.

Tables created:

- `commands` (09 §4.3, §9, §59; 14 §7.1): one row per logical
  *command_id* -- the stable identity of one requested consequential
  operation, independent of how many times it is attempted. Columns
  map 09 §9's `command_id`/`workspace_scope_ref`/`command_type`/
  `command_contract_version` plus `payload_fingerprint` (09 §139/
  AC-09-013: the value a reused `command_id` is checked against).
  `UNIQUE(id, workspace_id)` is the same composite-FK anchor pattern
  every prior migration has used (`sessions`, `question_bursts`, ...),
  here so `command_attempts` can force its own Workspace to match its
  parent Command's -- the mandatory adversarial attack "wrong
  Workspace" (reusing a `command_id` under a different Workspace claim)
  is therefore structurally unrepresentable, not just checked in
  application code.

  A row here is immutable once created (trigger 1, below) -- 09 §139:
  "Once accepted as a Command execution attempt: payload fingerprint is
  immutable for that attempt. A changed payload creates a new
  attempt/command." `packages/persistence/command_repository.py`'s own
  `record_attempt` enforces the *application-level* form of this rule
  (raising `CommandPayloadConflict`/`CommandWorkspaceMismatch` before
  ever reaching the database); the trigger is defense-in-depth, the
  same "checked at two independent layers, not layered as a single
  point of failure" discipline the transition triggers in `d467112ce46d`/
  `d8a1147fde30` already established.

- `command_attempts` (09 §4.4, §59): one row per *execution attempt* of
  a Command -- 09 §4.4: "A retry may reuse the same command_id while
  creating a new attempt_id." Columns map 09 §59's
  `CommandExecutionRecord` field list exactly:
  `command_id`/`attempt_id`/`command_type`(implicit via the FK to
  `commands`)/`workspace_id`/`actor_ref`(`actor_ref` here, 09's
  wording)/`received_at`/`boundary_evaluation_summary_ref`/`commit_id`/
  `outcome`/`completed_at`/`failure_code`.

  `commit_id` carries no foreign key: `commit_units` (14 §7.1) is not
  created until migration `009_commit_audit_outbox` (PKG-13). This is
  the same disclosed forward-reference gap `question_lineage`'s
  `ai_generation_id` already established for `ai_generations`
  (migration `007_ai_operational`, PKG-06's docstring) -- a nullable
  column with no FK yet, not a fabricated one pointing nowhere.

  `outcome` is CHECK-constrained to 14 §6's exact 4-value closed
  vocabulary (`DENIED`, `FAILED_PRECOMMIT`, `COMMITTED`,
  `INDETERMINATE`) when non-NULL. It is nullable: no commit coordinator
  exists yet (PKG-13) to ever determine one, so every row this
  package's own tests create necessarily has `outcome IS NULL` at
  creation -- the closed vocabulary stays exactly 4 values (not a 5th
  invented "PENDING"/"RECEIVED" state); "not yet determined" is
  represented by the column's own nullability, the identical modeling
  choice already used for this table's `commit_id`/`completed_at`/
  `failure_code`.

  Trigger 2 enforces that `command_id`/`workspace_id`/`actor_ref`/
  `received_at` never change after insert (an attempt's own identity
  and receipt facts are immutable), and that once `outcome` is set it
  is terminal (09 §18 FAILURE SEMANTICS: none of the 4 outcomes is
  reinterpreted as another). `boundary_evaluation_summary_ref`/
  `commit_id`/`completed_at`/`failure_code` remain legitimately
  settable exactly once, by whichever future package (PKG-13) actually
  determines them -- `packages/persistence/command_repository.py`'s own
  `record_outcome` is built now (14 §10's `CommandRepository` port is a
  single, non-phase-tagged list) but is exercised only by this
  package's own tests, the same disclosed "built but unwired" pattern
  `BurstRepository`'s transition methods (PKG-07) and
  `QuestionRepository.create_root`/`create_derived` (PKG-06) already
  established.

No cascading delete anywhere (14 §49 default). Schema downgrade is
infrastructure rollback only, not domain rollback (14 §9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2f3a5d5096c"
down_revision: str | None = "d8a1147fde30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 14 section 6's exact 4-value closed vocabulary.
_COMMAND_OUTCOMES = ("DENIED", "FAILED_PRECOMMIT", "COMMITTED", "INDETERMINATE")


def upgrade() -> None:
    op.create_table(
        "commands",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("command_type", sa.Text(), nullable=False),
        sa.Column("contract_version", sa.Text(), nullable=False),
        sa.Column("payload_fingerprint", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id", name="pk_commands"),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name="fk_commands_workspace", ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("id", "workspace_id", name="uq_commands_id_workspace"),
        sa.CheckConstraint("command_type <> ''", name="ck_commands_command_type_nonempty"),
        sa.CheckConstraint(
            "contract_version ~ '^[0-9]+(\\.[0-9]+)*$'", name="ck_commands_contract_version_shape"
        ),
        sa.CheckConstraint(
            "payload_fingerprint <> ''", name="ck_commands_payload_fingerprint_nonempty"
        ),
    )
    op.create_index("ix_commands_workspace", "commands", ["workspace_id"])

    op.create_table(
        "command_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("command_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("actor_ref", sa.Text(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("boundary_evaluation_summary_ref", sa.Uuid(), nullable=True),
        sa.Column("commit_id", sa.Uuid(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_code", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_command_attempts"),
        sa.ForeignKeyConstraint(
            ["command_id", "workspace_id"],
            ["commands.id", "commands.workspace_id"],
            name="fk_command_attempts_command_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("actor_ref <> ''", name="ck_command_attempts_actor_ref_nonempty"),
        sa.CheckConstraint(
            "outcome IS NULL OR outcome IN ("
            + ", ".join(f"'{o}'" for o in _COMMAND_OUTCOMES)
            + ")",
            name="ck_command_attempts_outcome_vocabulary",
        ),
        sa.CheckConstraint(
            "completed_at IS NULL OR outcome IS NOT NULL",
            name="ck_command_attempts_completed_requires_outcome",
        ),
    )
    op.create_index("ix_command_attempts_command", "command_attempts", ["command_id"])
    op.create_index("ix_command_attempts_workspace", "command_attempts", ["workspace_id"])

    # Trigger 1: `commands` rows are immutable once created (09 section
    # 139: payload fingerprint immutable per command identity; a
    # changed payload is a new logical Command, never an update to this
    # row).
    op.execute(
        """
        CREATE FUNCTION trg_commands_enforce_immutable() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'commands rows are immutable; a changed command creates a new command_id '
                '(09 section 139)';
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_commands_enforce_immutable
        BEFORE UPDATE ON commands
        FOR EACH ROW EXECUTE FUNCTION trg_commands_enforce_immutable();
        """
    )

    # Trigger 2: attempt identity/receipt facts are immutable; outcome
    # is terminal once set (09 section 18: none of the 4 outcomes is
    # reinterpreted as another).
    op.execute(
        """
        CREATE FUNCTION trg_command_attempts_enforce_immutable() RETURNS trigger AS $$
        BEGIN
            IF NEW.command_id IS DISTINCT FROM OLD.command_id
                OR NEW.workspace_id IS DISTINCT FROM OLD.workspace_id
                OR NEW.actor_ref IS DISTINCT FROM OLD.actor_ref
                OR NEW.received_at IS DISTINCT FROM OLD.received_at
            THEN
                RAISE EXCEPTION
                    'command_attempts identity/receipt fields are immutable once set';
            END IF;
            IF OLD.outcome IS NOT NULL AND NEW.outcome IS DISTINCT FROM OLD.outcome THEN
                RAISE EXCEPTION
                    'command_attempts outcome is terminal once set (09 section 18)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_command_attempts_enforce_immutable
        BEFORE UPDATE ON command_attempts
        FOR EACH ROW EXECUTE FUNCTION trg_command_attempts_enforce_immutable();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_command_attempts_enforce_immutable ON command_attempts;")
    op.execute("DROP FUNCTION IF EXISTS trg_command_attempts_enforce_immutable();")
    op.execute("DROP TRIGGER IF EXISTS trg_commands_enforce_immutable ON commands;")
    op.execute("DROP FUNCTION IF EXISTS trg_commands_enforce_immutable();")
    op.drop_index("ix_command_attempts_workspace", table_name="command_attempts")
    op.drop_index("ix_command_attempts_command", table_name="command_attempts")
    op.drop_table("command_attempts")
    op.drop_index("ix_commands_workspace", table_name="commands")
    op.drop_table("commands")
