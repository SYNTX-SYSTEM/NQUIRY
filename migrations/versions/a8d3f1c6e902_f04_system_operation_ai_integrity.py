"""F04: SYSTEM_OPERATION source, operation authorizations, AI record integrity

Revision ID: a8d3f1c6e902
Revises: f6b2c4d9a318
Create Date: 2026-09-25 00:00:01.000000

F04 WU-04.3 (HD-17, 16 §41 REC-019 / NQ-DEC-045; F04 reconstruction §0.1;
FBR-F04-4, FBR-F04-5, FBR-F04-7, FBR-F04-11..13; pre-implementation bindings
PI-1, PI-4).

1. `audit_events.authority_source_type` gains SYSTEM_OPERATION (the fifth
   typed effect-gate source). Historical rows are untouched.

2. `ai_operation_authorizations` (PI-4): the explicit, immutable operation
   authorization relation OA = (authorizing_command_id, ai_operation_id), one
   row per OA, written once by the commit that creates it (§0.1 rule 8):
   - OA-1 by CMD_BEGIN_ANALYSIS, OA-2 by CMD_REQUEST_QUESTION_ANALYSIS,
     OA-3 by the acceptance of an AIOP-001 artifact X, OA-4 by
     CMD_REQUEST_QUESTION_CLUSTERING;
   - `sequence_no` orders the OAs of one (Session, operation); the latest is
     the only executable one (rule 5). `supersedes_authorization_id` names the
     predecessor, and a trigger requires it to be exactly sequence_no - 1;
   - `chain_root_command_id` is the Session's BEGIN_ANALYSIS (rule 6), checked
     by trigger against the predecessor / X;
   - `request_case` RETRY / RECOVERY (rule 9) is checked by trigger against the
     persisted state of the predecessor at insert time: RETRY needs the
     predecessor consumed by a FAILED / REJECTED generation that
     `retry_of_generation_id` names; RECOVERY needs it unconsumed;
   - `precondition_artifact_ref` = X for AIOP-002 (rule 8), an AIOP-001
     artifact of the same Session; for OA-3, X's generation must carry the
     same authorizing command (R7).
   The table rejects UPDATE and DELETE.

3. `ai_generations` gains the persisted OA fields (session_id,
   operation_authorization_id, authorizing_command_id,
   precondition_artifact_ref), all identity-immutable. UNIQUE
   (authorizing_command_id, ai_operation_id) is rule 3 (at most one generation
   per OA). A partial unique index allows one non-terminal generation per
   (Session, operation). An insert trigger requires the OA to be the latest
   (a superseded OA can never execute) and copies nothing: `retry_of` and X
   must equal the OA's persisted values.

4. `ai_validation_proofs` (09 §56, FBR-F04-4): one immutable proof per
   generation.

5. `ai_context_manifests` become immutable (09 §54.1, FBR-F04-5) and gain the
   frozen-set binding columns (FBR-F04-6): session_id, frozen_set_ref,
   frozen_set_fingerprint.

6. `ai_derived_artifacts` become append-only (FBR-F04-5) and gain the
   acceptance facts: session_id, accepted_by_command_id, proof_class
   (MOCK_NON_PROOF / PROVIDER_OUTPUT, HD-19). One artifact per generation;
   at most one accepted artifact per (Session, operation): one accepted
   AIOP-001 artifact (R2) and one accepted clustering result, whose id is the
   `cluster_run_id` (R8).

Rows written before this revision keep NULL in every new nullable column.
Workspace-scoped RLS (policy `workspace_isolation`) is enabled on the two new
tables, as for every Workspace-scoped table since `047bdf9bc528`.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a8d3f1c6e902"
down_revision = "f6b2c4d9a318"
branch_labels = None
depends_on = None

_RLS_EXPR = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"

_OLD_SOURCE = (
    "authority_source_type IS NULL OR authority_source_type IN "
    "('BINDING','ROLE','FOUNDING','PARTICIPATION')"
)
_NEW_SOURCE = (
    "authority_source_type IS NULL OR authority_source_type IN "
    "('BINDING','ROLE','FOUNDING','PARTICIPATION','SYSTEM_OPERATION')"
)

_IMMUTABLE_TABLES = (
    ("ai_operation_authorizations", "operation authorizations are written once (F04 §0.1 rule 8)"),
    ("ai_validation_proofs", "AI_VALIDATION_PROOF is an immutable proof record (09 §56)"),
    ("ai_context_manifests", "an AIContextManifest is immutable (09 §54.1)"),
    ("ai_derived_artifacts", "accepted AI-derived artifacts are append-only (09 §118)"),
)


def upgrade() -> None:
    # 1. The fifth typed authority source.
    op.drop_constraint("ck_audit_events_authority_source_type", "audit_events", type_="check")
    op.create_check_constraint(
        "ck_audit_events_authority_source_type", "audit_events", _NEW_SOURCE
    )

    # 5/6 first: columns other tables reference.
    op.add_column("ai_context_manifests", sa.Column("session_id", sa.Uuid(), nullable=True))
    op.add_column("ai_context_manifests", sa.Column("frozen_set_ref", sa.Text(), nullable=True))
    op.add_column(
        "ai_context_manifests", sa.Column("frozen_set_fingerprint", sa.Text(), nullable=True)
    )
    op.create_foreign_key(
        "fk_ai_context_manifests_session_workspace",
        "ai_context_manifests",
        "sessions",
        ["session_id", "workspace_id"],
        ["id", "workspace_id"],
        ondelete="RESTRICT",
    )

    op.add_column("ai_derived_artifacts", sa.Column("session_id", sa.Uuid(), nullable=True))
    op.add_column(
        "ai_derived_artifacts", sa.Column("accepted_by_command_id", sa.Uuid(), nullable=True)
    )
    op.add_column("ai_derived_artifacts", sa.Column("proof_class", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_ai_derived_artifacts_proof_class",
        "ai_derived_artifacts",
        "proof_class IS NULL OR proof_class IN ('MOCK_NON_PROOF','PROVIDER_OUTPUT')",
    )
    op.create_check_constraint(
        "ck_ai_derived_artifacts_acceptance_complete",
        "ai_derived_artifacts",
        "(session_id IS NULL AND accepted_by_command_id IS NULL AND proof_class IS NULL)"
        " OR (session_id IS NOT NULL AND accepted_by_command_id IS NOT NULL"
        " AND proof_class IS NOT NULL)",
    )
    op.create_foreign_key(
        "fk_ai_derived_artifacts_session_workspace",
        "ai_derived_artifacts",
        "sessions",
        ["session_id", "workspace_id"],
        ["id", "workspace_id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_ai_derived_artifacts_accepted_by_command",
        "ai_derived_artifacts",
        "commands",
        ["accepted_by_command_id", "workspace_id"],
        ["id", "workspace_id"],
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "uq_ai_derived_artifacts_generation", "ai_derived_artifacts", ["ai_generation_id"]
    )
    op.create_unique_constraint(
        "uq_ai_derived_artifacts_id_workspace_session",
        "ai_derived_artifacts",
        ["id", "workspace_id", "session_id"],
    )
    op.create_index(
        "uq_ai_derived_artifacts_one_accepted_per_session_operation",
        "ai_derived_artifacts",
        ["session_id", "ai_operation_id"],
        unique=True,
        postgresql_where=sa.text("session_id IS NOT NULL"),
    )

    # 2. Operation authorizations.
    op.create_table(
        "ai_operation_authorizations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("ai_operation_id", sa.Text(), nullable=False),
        sa.Column("shape", sa.Text(), nullable=False),
        sa.Column("authorizing_command_id", sa.Uuid(), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("chain_root_command_id", sa.Uuid(), nullable=False),
        sa.Column("request_case", sa.Text(), nullable=True),
        sa.Column("supersedes_authorization_id", sa.Uuid(), nullable=True),
        sa.Column("retry_of_generation_id", sa.Uuid(), nullable=True),
        sa.Column("precondition_artifact_ref", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_ai_operation_authorizations"),
        sa.ForeignKeyConstraint(
            ["session_id", "workspace_id"],
            ["sessions.id", "sessions.workspace_id"],
            name="fk_ai_operation_authorizations_session_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["authorizing_command_id", "workspace_id"],
            ["commands.id", "commands.workspace_id"],
            name="fk_ai_operation_authorizations_command_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["chain_root_command_id", "workspace_id"],
            ["commands.id", "commands.workspace_id"],
            name="fk_ai_operation_authorizations_chain_root_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_authorization_id"],
            ["ai_operation_authorizations.id"],
            name="fk_ai_operation_authorizations_supersedes",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["retry_of_generation_id", "workspace_id"],
            ["ai_generations.id", "ai_generations.workspace_id"],
            name="fk_ai_operation_authorizations_retry_of_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["precondition_artifact_ref", "workspace_id", "session_id"],
            [
                "ai_derived_artifacts.id",
                "ai_derived_artifacts.workspace_id",
                "ai_derived_artifacts.session_id",
            ],
            name="fk_ai_operation_authorizations_precondition_artifact",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "ai_operation_id IN ('AIOP-001','AIOP-002')",
            name="ck_ai_operation_authorizations_operation",
        ),
        sa.CheckConstraint(
            "request_case IS NULL OR request_case IN ('RETRY','RECOVERY')",
            name="ck_ai_operation_authorizations_request_case",
        ),
        sa.CheckConstraint(
            # §0.1 rule 2: the four legal OA shapes, and nothing else.
            "(shape = 'OA-1' AND ai_operation_id = 'AIOP-001' AND sequence_no = 1"
            " AND authorizing_command_id = chain_root_command_id AND request_case IS NULL"
            " AND supersedes_authorization_id IS NULL AND retry_of_generation_id IS NULL"
            " AND precondition_artifact_ref IS NULL)"
            " OR (shape = 'OA-2' AND ai_operation_id = 'AIOP-001' AND sequence_no > 1"
            " AND request_case IS NOT NULL AND supersedes_authorization_id IS NOT NULL"
            " AND precondition_artifact_ref IS NULL)"
            " OR (shape = 'OA-3' AND ai_operation_id = 'AIOP-002' AND sequence_no = 1"
            " AND request_case IS NULL AND supersedes_authorization_id IS NULL"
            " AND retry_of_generation_id IS NULL AND precondition_artifact_ref IS NOT NULL)"
            " OR (shape = 'OA-4' AND ai_operation_id = 'AIOP-002' AND sequence_no > 1"
            " AND request_case IS NOT NULL AND supersedes_authorization_id IS NOT NULL"
            " AND precondition_artifact_ref IS NOT NULL)",
            name="ck_ai_operation_authorizations_shape",
        ),
        sa.CheckConstraint(
            # §0.1 rule 9: retry_of exists exactly for RETRY.
            "(request_case IS NULL AND retry_of_generation_id IS NULL)"
            " OR (request_case = 'RETRY' AND retry_of_generation_id IS NOT NULL)"
            " OR (request_case = 'RECOVERY' AND retry_of_generation_id IS NULL)",
            name="ck_ai_operation_authorizations_retry_lineage",
        ),
        sa.UniqueConstraint(
            "authorizing_command_id",
            "ai_operation_id",
            name="uq_ai_operation_authorizations_oa",
        ),
        sa.UniqueConstraint(
            "session_id",
            "ai_operation_id",
            "sequence_no",
            name="uq_ai_operation_authorizations_sequence",
        ),
        sa.UniqueConstraint(
            "id",
            "workspace_id",
            "session_id",
            "authorizing_command_id",
            "ai_operation_id",
            name="uq_ai_operation_authorizations_identity",
        ),
    )
    op.create_index(
        "ix_ai_operation_authorizations_session",
        "ai_operation_authorizations",
        ["session_id", "ai_operation_id"],
    )

    op.execute(
        """
        CREATE FUNCTION trg_ai_operation_authorizations_chain() RETURNS trigger AS $$
        DECLARE
            pred ai_operation_authorizations%ROWTYPE;
            pred_gen ai_generations%ROWTYPE;
            x_artifact ai_derived_artifacts%ROWTYPE;
            x_gen ai_generations%ROWTYPE;
            x_oa ai_operation_authorizations%ROWTYPE;
        BEGIN
            IF NEW.sequence_no > 1 THEN
                SELECT * INTO pred FROM ai_operation_authorizations
                    WHERE id = NEW.supersedes_authorization_id;
                IF pred.id IS NULL
                    OR pred.session_id <> NEW.session_id
                    OR pred.ai_operation_id <> NEW.ai_operation_id
                    OR pred.sequence_no <> NEW.sequence_no - 1 THEN
                    RAISE EXCEPTION
                        'an operation authorization must supersede exactly its predecessor '
                        '(F04 §0.1 rule 5)';
                END IF;
                IF pred.chain_root_command_id <> NEW.chain_root_command_id THEN
                    RAISE EXCEPTION 'chain root must equal the predecessor chain root (F04 §0.1 rule 6)';
                END IF;
                SELECT * INTO pred_gen FROM ai_generations
                    WHERE operation_authorization_id = pred.id;
                IF NEW.request_case = 'RETRY' THEN
                    IF pred_gen.id IS NULL
                        OR pred_gen.id <> NEW.retry_of_generation_id
                        OR pred_gen.status NOT IN ('FAILED', 'REJECTED') THEN
                        RAISE EXCEPTION
                            'RETRY requires the predecessor authorization consumed by a '
                            'FAILED/REJECTED generation named by retry_of (F04 §0.1 rule 9)';
                    END IF;
                ELSIF NEW.request_case = 'RECOVERY' THEN
                    IF pred_gen.id IS NOT NULL THEN
                        RAISE EXCEPTION
                            'RECOVERY requires the predecessor authorization unconsumed '
                            '(F04 §0.1 rule 9)';
                    END IF;
                END IF;
            END IF;
            IF NEW.precondition_artifact_ref IS NOT NULL THEN
                SELECT * INTO x_artifact FROM ai_derived_artifacts
                    WHERE id = NEW.precondition_artifact_ref;
                IF x_artifact.ai_operation_id <> 'AIOP-001' OR x_artifact.session_id <> NEW.session_id
                THEN
                    RAISE EXCEPTION
                        'precondition artifact must be an accepted AIOP-001 artifact of this '
                        'Session (F04 §0.1 rule 8)';
                END IF;
                SELECT * INTO x_gen FROM ai_generations WHERE id = x_artifact.ai_generation_id;
                SELECT * INTO x_oa FROM ai_operation_authorizations
                    WHERE id = x_gen.operation_authorization_id;
                IF x_oa.id IS NULL OR x_oa.chain_root_command_id <> NEW.chain_root_command_id THEN
                    RAISE EXCEPTION
                        'precondition artifact must resolve to the same BEGIN_ANALYSIS chain '
                        '(F04 §0.1 rule 6)';
                END IF;
                IF NEW.shape = 'OA-3'
                    AND x_gen.authorizing_command_id <> NEW.authorizing_command_id THEN
                    RAISE EXCEPTION
                        'OA-3 must be authorized by the command that authorized X (F04 R7)';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_ai_operation_authorizations_chain
        BEFORE INSERT ON ai_operation_authorizations
        FOR EACH ROW EXECUTE FUNCTION trg_ai_operation_authorizations_chain();
        """
    )

    # 3. Generations carry their operation authorization.
    op.add_column("ai_generations", sa.Column("session_id", sa.Uuid(), nullable=True))
    op.add_column(
        "ai_generations", sa.Column("operation_authorization_id", sa.Uuid(), nullable=True)
    )
    op.add_column("ai_generations", sa.Column("authorizing_command_id", sa.Uuid(), nullable=True))
    op.add_column(
        "ai_generations", sa.Column("precondition_artifact_ref", sa.Uuid(), nullable=True)
    )
    op.create_check_constraint(
        "ck_ai_generations_authorization_complete",
        "ai_generations",
        "(operation_authorization_id IS NULL AND session_id IS NULL"
        " AND authorizing_command_id IS NULL AND precondition_artifact_ref IS NULL)"
        " OR (operation_authorization_id IS NOT NULL AND session_id IS NOT NULL"
        " AND authorizing_command_id IS NOT NULL)",
    )
    op.create_foreign_key(
        "fk_ai_generations_operation_authorization",
        "ai_generations",
        "ai_operation_authorizations",
        [
            "operation_authorization_id",
            "workspace_id",
            "session_id",
            "authorizing_command_id",
            "ai_operation_id",
        ],
        ["id", "workspace_id", "session_id", "authorizing_command_id", "ai_operation_id"],
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "uq_ai_generations_operation_authorization",
        "ai_generations",
        ["authorizing_command_id", "ai_operation_id"],
    )
    op.create_index(
        "uq_ai_generations_one_non_terminal_per_session_operation",
        "ai_generations",
        ["session_id", "ai_operation_id"],
        unique=True,
        postgresql_where=sa.text(
            "session_id IS NOT NULL AND status IN ('REQUESTED','RUNNING','OUTPUT_RECEIVED')"
        ),
    )
    op.execute(
        """
        CREATE FUNCTION trg_ai_generations_authorization() RETURNS trigger AS $$
        DECLARE
            oa ai_operation_authorizations%ROWTYPE;
        BEGIN
            IF NEW.operation_authorization_id IS NULL THEN
                RETURN NEW;
            END IF;
            SELECT * INTO oa FROM ai_operation_authorizations
                WHERE id = NEW.operation_authorization_id;
            IF EXISTS (
                SELECT 1 FROM ai_operation_authorizations later
                WHERE later.session_id = oa.session_id
                  AND later.ai_operation_id = oa.ai_operation_id
                  AND later.sequence_no > oa.sequence_no
            ) THEN
                RAISE EXCEPTION
                    'a superseded operation authorization can never execute (F04 §0.1 rule 5)';
            END IF;
            IF NEW.retry_of_generation_id IS DISTINCT FROM oa.retry_of_generation_id
                OR NEW.precondition_artifact_ref IS DISTINCT FROM oa.precondition_artifact_ref THEN
                RAISE EXCEPTION
                    'generation provenance must equal its operation authorization '
                    '(retry_of, precondition artifact; F04 §0.1 rules 8-9)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_ai_generations_authorization
        BEFORE INSERT ON ai_generations
        FOR EACH ROW EXECUTE FUNCTION trg_ai_generations_authorization();
        """
    )
    op.execute(_transition_function(extended=True))

    # 4. Persisted validation proofs.
    op.create_table(
        "ai_validation_proofs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("ai_generation_id", sa.Uuid(), nullable=False),
        sa.Column("ai_operation_id", sa.Text(), nullable=False),
        sa.Column("contract_version", sa.Text(), nullable=False),
        sa.Column("validator_version", sa.Text(), nullable=False),
        sa.Column("validation_result", sa.Text(), nullable=False),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("output_fingerprint", sa.Text(), nullable=False),
        sa.Column("validation_details_ref", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_ai_validation_proofs"),
        sa.ForeignKeyConstraint(
            ["ai_generation_id", "workspace_id"],
            ["ai_generations.id", "ai_generations.workspace_id"],
            name="fk_ai_validation_proofs_generation_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "validation_result IN ('VALIDATED','REJECTED','INDETERMINATE')",
            name="ck_ai_validation_proofs_result",
        ),
        sa.UniqueConstraint("ai_generation_id", name="uq_ai_validation_proofs_generation"),
    )
    op.create_index("ix_ai_validation_proofs_workspace", "ai_validation_proofs", ["workspace_id"])

    for table, reason in _IMMUTABLE_TABLES:
        op.execute(
            f"""
            CREATE FUNCTION trg_{table}_immutable() RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION '{table}: % rejected; {reason}', TG_OP;
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

    for table in ("ai_operation_authorizations", "ai_validation_proofs"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY workspace_isolation ON {table} "
            f"USING ({_RLS_EXPR}) WITH CHECK ({_RLS_EXPR})"
        )


def _transition_function(*, extended: bool) -> str:
    extra = (
        """
                OR NEW.session_id IS DISTINCT FROM OLD.session_id
                OR NEW.operation_authorization_id IS DISTINCT FROM OLD.operation_authorization_id
                OR NEW.authorizing_command_id IS DISTINCT FROM OLD.authorizing_command_id
                OR NEW.precondition_artifact_ref IS DISTINCT FROM OLD.precondition_artifact_ref"""
        if extended
        else ""
    )
    return f"""
        CREATE OR REPLACE FUNCTION trg_ai_generations_enforce_transition() RETURNS trigger AS $$
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
                OR NEW.correlation_id IS DISTINCT FROM OLD.correlation_id{extra}
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


def downgrade() -> None:
    for table in ("ai_validation_proofs", "ai_operation_authorizations"):
        op.execute(f"DROP POLICY IF EXISTS workspace_isolation ON {table}")
    for table, _ in _IMMUTABLE_TABLES:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_immutable ON {table};")
        op.execute(f"DROP FUNCTION IF EXISTS trg_{table}_immutable();")
    op.drop_index("ix_ai_validation_proofs_workspace", table_name="ai_validation_proofs")
    op.drop_table("ai_validation_proofs")

    op.execute(_transition_function(extended=False))
    op.execute("DROP TRIGGER IF EXISTS trg_ai_generations_authorization ON ai_generations;")
    op.execute("DROP FUNCTION IF EXISTS trg_ai_generations_authorization();")
    op.drop_index(
        "uq_ai_generations_one_non_terminal_per_session_operation", table_name="ai_generations"
    )
    op.drop_constraint(
        "uq_ai_generations_operation_authorization", "ai_generations", type_="unique"
    )
    op.drop_constraint(
        "fk_ai_generations_operation_authorization", "ai_generations", type_="foreignkey"
    )
    op.drop_constraint("ck_ai_generations_authorization_complete", "ai_generations", type_="check")
    for column in (
        "precondition_artifact_ref",
        "authorizing_command_id",
        "operation_authorization_id",
        "session_id",
    ):
        op.drop_column("ai_generations", column)

    op.execute(
        "DROP TRIGGER IF EXISTS trg_ai_operation_authorizations_chain "
        "ON ai_operation_authorizations;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_ai_operation_authorizations_chain();")
    op.drop_index(
        "ix_ai_operation_authorizations_session", table_name="ai_operation_authorizations"
    )
    op.drop_table("ai_operation_authorizations")

    op.drop_index(
        "uq_ai_derived_artifacts_one_accepted_per_session_operation",
        table_name="ai_derived_artifacts",
    )
    op.drop_constraint(
        "uq_ai_derived_artifacts_id_workspace_session", "ai_derived_artifacts", type_="unique"
    )
    op.drop_constraint("uq_ai_derived_artifacts_generation", "ai_derived_artifacts", type_="unique")
    op.drop_constraint(
        "fk_ai_derived_artifacts_accepted_by_command", "ai_derived_artifacts", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_ai_derived_artifacts_session_workspace", "ai_derived_artifacts", type_="foreignkey"
    )
    op.drop_constraint(
        "ck_ai_derived_artifacts_acceptance_complete", "ai_derived_artifacts", type_="check"
    )
    op.drop_constraint("ck_ai_derived_artifacts_proof_class", "ai_derived_artifacts", type_="check")
    for column in ("proof_class", "accepted_by_command_id", "session_id"):
        op.drop_column("ai_derived_artifacts", column)

    op.drop_constraint(
        "fk_ai_context_manifests_session_workspace", "ai_context_manifests", type_="foreignkey"
    )
    for column in ("frozen_set_fingerprint", "frozen_set_ref", "session_id"):
        op.drop_column("ai_context_manifests", column)

    op.drop_constraint("ck_audit_events_authority_source_type", "audit_events", type_="check")
    op.create_check_constraint(
        "ck_audit_events_authority_source_type", "audit_events", _OLD_SOURCE
    )
