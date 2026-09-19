"""ai operational

Revision ID: 4a7c1e9f2b3d
Revises: 321e335bb130
Create Date: 2026-09-20 12:00:00.000000

PKG-18 scope (14_IMPLEMENTATION_SEQUENCE.md section 9:
"007_ai_operational | generations, manifests, derived artifacts |
depends on: 004,006"). This migration materializes only the
`ai_generations`/`ai_derived_artifacts` half of that conceptual bucket
-- 14 PKG-19's own OBJECTIVE ("Exclusive provider path, context
manifest, prompt, validator") assigns `ai_context_manifests` there,
the same one-conceptual-bucket-across-two-Alembic-revisions split
PKG-02/05/06/07/10/11 already established.

Tables created:

- `ai_generations` (09 section 55: exact field list). `ai_operation_id`
  is CHECK-constrained to 08 section 4's own 16-value closed vocabulary
  (sections 23-38 each give one member its own full contract, the
  identical "exhaustively named, not merely illustrative" reading
  `boundaries.types.BoundaryId` already applied to 06's 18 boundaries).
  `status` is CHECK-constrained to 08 section 14 / 14 section 6's exact
  6-value closed vocabulary. `ai_context_manifest_id` carries NO
  foreign key -- `ai_context_manifests` is PKG-19's own table to
  create, the identical disclosed forward-reference shape
  `question_lineage.ai_generation_id` (PKG-06) and
  `evidence_relations.ai_generation_id` (PKG-16) already carried before
  this package existed to close them. `output_artifact_ref` likewise
  carries no foreign key: it would require a circular same-migration
  dependency on `ai_derived_artifacts` (created below, referencing
  `ai_generations` the other way) -- the same disclosed choice
  `commit_units.audit_event_ids`/`outbox_ids` (PKG-13) already made for
  an analogous forward reference with no per-element FK. Composite
  self-referential FK `(retry_of_generation_id, workspace_id) ->
  ai_generations(id, workspace_id)`, nullable (AC-09-022: "AIGeneration
  retry creates new generation while remaining correlated to logical
  operation" -- mirrors `evidence.supersedes_evidence_id`'s own
  self-referential supersession FK, PKG-16). Two triggers enforce 08
  section 15's exact transition topology: creation in `REQUESTED`;
  identity fields (`workspace_id`/`user_id`/`ai_operation_id`/
  `ai_operation_contract_version`/`ai_context_manifest_id`/
  `prompt_version`/`model`/`provider`/`requested_at`/
  `retry_of_generation_id`/`command_id`/`correlation_id`) immutable
  once requested; `VALIDATED`/`REJECTED`/`FAILED` each terminal -- no
  further UPDATE of any kind, mirroring `decisions`'/`question_bursts`'
  own terminal-state precedent.

- `ai_derived_artifacts` (14 section 7.1's own core-tables row; no 09
  DATA CONTRACT names this table's own fields -- GAP-12-008, "Derived
  AI artifact physical type", remains open, home 08/09; see
  `packages/ai_contracts/derived_artifact.py`'s own module docstring
  for why a generic container is this package's own disclosed
  `[IMPLEMENTATION CHOICE]`, not a resolution of that gap). Composite
  FK `(ai_generation_id, workspace_id) -> ai_generations(id,
  workspace_id)`. `ai_operation_id` is CHECK-constrained to the same
  16-value vocabulary as `ai_generations`. No trigger: this table is
  append-only by this package's own repository (no update method), the
  same convention `claim_anchors` (PKG-16) already established.

Retrofitted this migration (composite FKs, now that `ai_generations`
exists):

- `question_lineage.ai_generation_id -> ai_generations(id,
  workspace_id)` -- previously a disclosed forward-reference gap
  (PKG-06).
- `evidence_relations.ai_generation_id -> ai_generations(id,
  workspace_id)` -- previously a disclosed forward-reference gap
  (PKG-16).

No `ai_gateway_writer` DB-principal/GRANT is created here, consistent
with every migration since `001` (deferred to `012_security_events_rls`).
No cascading delete anywhere (14 section 49 default). Schema downgrade
is infrastructure rollback only, not domain rollback (14 section 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4a7c1e9f2b3d"
down_revision: str | None = "321e335bb130"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 08 section 4's exact 16-value closed vocabulary (sections 23-38).
_AI_OPERATION_IDS = tuple(f"AIOP-{n:03d}" for n in range(1, 17))
# 08 section 14 / 14 section 6's exact 6-value closed vocabulary.
_AI_GENERATION_STATUSES = (
    "REQUESTED",
    "RUNNING",
    "OUTPUT_RECEIVED",
    "VALIDATED",
    "REJECTED",
    "FAILED",
)


def _in_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{v}'" for v in values)


def upgrade() -> None:
    op.create_table(
        "ai_generations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("ai_operation_id", sa.Text(), nullable=False),
        sa.Column("ai_operation_contract_version", sa.Text(), nullable=False),
        sa.Column("ai_context_manifest_id", sa.Uuid(), nullable=True),
        sa.Column("prompt_version", sa.Text(), nullable=False),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("output_received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("input_tokens", sa.BigInteger(), nullable=True),
        sa.Column("output_tokens", sa.BigInteger(), nullable=True),
        sa.Column("latency_ms", sa.BigInteger(), nullable=True),
        sa.Column("estimated_cost", sa.Float(), nullable=True),
        sa.Column("retry_of_generation_id", sa.Uuid(), nullable=True),
        sa.Column("command_id", sa.Uuid(), nullable=True),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("output_artifact_ref", sa.Uuid(), nullable=True),
        sa.Column("failure_code", sa.Text(), nullable=True),
        sa.Column("failure_detail_ref", sa.Text(), nullable=True),
        sa.Column("record_version", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_ai_generations"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_ai_generations_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_ai_generations_user", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["command_id", "workspace_id"],
            ["commands.id", "commands.workspace_id"],
            name="fk_ai_generations_command_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["retry_of_generation_id", "workspace_id"],
            ["ai_generations.id", "ai_generations.workspace_id"],
            name="fk_ai_generations_retry_of_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            f"ai_operation_id IN ({_in_list(_AI_OPERATION_IDS)})",
            name="ck_ai_generations_ai_operation_id",
        ),
        sa.CheckConstraint(
            f"status IN ({_in_list(_AI_GENERATION_STATUSES)})",
            name="ck_ai_generations_status",
        ),
        sa.UniqueConstraint("id", "workspace_id", name="uq_ai_generations_id_workspace"),
    )
    op.create_index("ix_ai_generations_workspace", "ai_generations", ["workspace_id"])
    op.create_index("ix_ai_generations_command", "ai_generations", ["command_id"])
    op.create_index("ix_ai_generations_retry_of", "ai_generations", ["retry_of_generation_id"])

    op.create_table(
        "ai_derived_artifacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("ai_generation_id", sa.Uuid(), nullable=False),
        sa.Column("ai_operation_id", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_fingerprint", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False),
        sa.Column("provenance_ref", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_ai_derived_artifacts"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_ai_derived_artifacts_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ai_generation_id", "workspace_id"],
            ["ai_generations.id", "ai_generations.workspace_id"],
            name="fk_ai_derived_artifacts_generation_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            f"ai_operation_id IN ({_in_list(_AI_OPERATION_IDS)})",
            name="ck_ai_derived_artifacts_ai_operation_id",
        ),
    )
    op.create_index("ix_ai_derived_artifacts_workspace", "ai_derived_artifacts", ["workspace_id"])
    op.create_index(
        "ix_ai_derived_artifacts_generation", "ai_derived_artifacts", ["ai_generation_id"]
    )

    # Retrofit: `ai_generations` now exists.
    op.create_foreign_key(
        "fk_question_lineage_ai_generation_workspace",
        "question_lineage",
        "ai_generations",
        ["ai_generation_id", "workspace_id"],
        ["id", "workspace_id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_evidence_relations_ai_generation_workspace",
        "evidence_relations",
        "ai_generations",
        ["ai_generation_id", "workspace_id"],
        ["id", "workspace_id"],
        ondelete="RESTRICT",
    )

    # Trigger 1: 08 section 14.1's own natural entry point -- a
    # governed AI operation request always begins REQUESTED.
    op.execute(
        """
        CREATE FUNCTION trg_ai_generations_enforce_initial_state() RETURNS trigger AS $$
        BEGIN
            IF NEW.status <> 'REQUESTED' THEN
                RAISE EXCEPTION
                    'ai_generations must be created in REQUESTED (08 section 14.1), got %',
                    NEW.status;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_ai_generations_enforce_initial_state
        BEFORE INSERT ON ai_generations
        FOR EACH ROW EXECUTE FUNCTION trg_ai_generations_enforce_initial_state();
        """
    )

    # Trigger 2: 08 section 15's exact transition table. Identity
    # fields are immutable once requested; `VALIDATED`/`REJECTED`/
    # `FAILED` are each terminal (illegal list: "REJECTED -> VALIDATED
    # by silent mutation", "FAILED -> VALIDATED", "REQUESTED ->
    # VALIDATED", "RUNNING -> VALIDATED" -- no legal exit from any
    # terminal state exists at all, not merely a denial of VALIDATED).
    op.execute(
        """
        CREATE FUNCTION trg_ai_generations_enforce_transition() RETURNS trigger AS $$
        BEGIN
            IF NEW.workspace_id IS DISTINCT FROM OLD.workspace_id
                OR NEW.user_id IS DISTINCT FROM OLD.user_id
                OR NEW.ai_operation_id IS DISTINCT FROM OLD.ai_operation_id
                OR NEW.ai_operation_contract_version
                    IS DISTINCT FROM OLD.ai_operation_contract_version
                OR NEW.ai_context_manifest_id IS DISTINCT FROM OLD.ai_context_manifest_id
                OR NEW.prompt_version IS DISTINCT FROM OLD.prompt_version
                OR NEW.model IS DISTINCT FROM OLD.model
                OR NEW.provider IS DISTINCT FROM OLD.provider
                OR NEW.requested_at IS DISTINCT FROM OLD.requested_at
                OR NEW.retry_of_generation_id IS DISTINCT FROM OLD.retry_of_generation_id
                OR NEW.command_id IS DISTINCT FROM OLD.command_id
                OR NEW.correlation_id IS DISTINCT FROM OLD.correlation_id
            THEN
                RAISE EXCEPTION
                    'ai_generations identity fields are immutable once requested (08 section 15)';
            END IF;
            IF OLD.status IN ('VALIDATED', 'REJECTED', 'FAILED') THEN
                RAISE EXCEPTION
                    'ai_generations status % is terminal (08 section 15)', OLD.status;
            END IF;
            IF NEW.status IS DISTINCT FROM OLD.status THEN
                IF NOT (
                    (OLD.status = 'REQUESTED' AND NEW.status = 'RUNNING')
                    OR (OLD.status = 'RUNNING' AND NEW.status IN ('OUTPUT_RECEIVED', 'FAILED'))
                    OR (OLD.status = 'OUTPUT_RECEIVED'
                        AND NEW.status IN ('VALIDATED', 'REJECTED', 'FAILED'))
                ) THEN
                    RAISE EXCEPTION
                        'illegal AIGeneration transition % -> % (08 section 15)',
                        OLD.status, NEW.status;
                END IF;
                IF NEW.record_version <= OLD.record_version THEN
                    RAISE EXCEPTION
                        'ai_generations status change must advance record_version '
                        '(14 section 26), % -> %',
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
        CREATE TRIGGER trg_ai_generations_enforce_transition
        BEFORE UPDATE ON ai_generations
        FOR EACH ROW EXECUTE FUNCTION trg_ai_generations_enforce_transition();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_ai_generations_enforce_transition ON ai_generations;")
    op.execute("DROP FUNCTION IF EXISTS trg_ai_generations_enforce_transition();")
    op.execute("DROP TRIGGER IF EXISTS trg_ai_generations_enforce_initial_state ON ai_generations;")
    op.execute("DROP FUNCTION IF EXISTS trg_ai_generations_enforce_initial_state();")

    op.drop_constraint(
        "fk_evidence_relations_ai_generation_workspace", "evidence_relations", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_question_lineage_ai_generation_workspace", "question_lineage", type_="foreignkey"
    )

    op.drop_index("ix_ai_derived_artifacts_generation", table_name="ai_derived_artifacts")
    op.drop_index("ix_ai_derived_artifacts_workspace", table_name="ai_derived_artifacts")
    op.drop_table("ai_derived_artifacts")

    op.drop_index("ix_ai_generations_retry_of", table_name="ai_generations")
    op.drop_index("ix_ai_generations_command", table_name="ai_generations")
    op.drop_index("ix_ai_generations_workspace", table_name="ai_generations")
    op.drop_table("ai_generations")
