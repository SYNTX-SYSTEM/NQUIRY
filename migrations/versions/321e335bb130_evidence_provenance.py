"""evidence provenance

Revision ID: 321e335bb130
Revises: e2f94137f8a9
Create Date: 2026-09-19 12:00:00.000000

PKG-16 scope (14_IMPLEMENTATION_SEQUENCE.md section 9:
"006_evidence_provenance | source refs, evidence, anchors, relations,
sets | depends on: 001"). Unlike every migration since PKG-02, this
bucket is materialized in ONE revision, not split across two packages
-- 14 assigns the entire 006 bucket to this single package (contrast
005_selection_decision, split PKG-14/PKG-15).

Tables created:

- `source_references` (09 section 40: exact field list). `origin` is
  CHECK-constrained to 07 section 24's own 5-value closed vocabulary
  (`domain.question.QuestionOrigin`'s own 4 LEVEL-1 categories plus
  `SYSTEM_DERIVED`). `source_type`/`validation_status` are deliberately
  plain `TEXT` with NO CHECK constraint -- 07/09 both use "examples"/
  "may include" language for these two fields, not the same definitive
  closure 07 section 2 gives Evidence's own `type` or 14 section 6
  gives `validation_state`; see `packages/evidence/models.py`'s own
  module docstring for the full reasoning. `UNIQUE(id, workspace_id)`
  is the composite-FK anchor `evidence.source_reference_id` targets.

- `evidence` (09 section 41: exact field list). `type` and
  `validation_state` are each CHECK-constrained to their own closed
  vocabularies (07 section 2; 14 section 6's own "Evidence validation"
  entry). Composite FK `(source_reference_id, workspace_id) ->
  source_references(id, workspace_id)`, nullable. Composite
  self-referential FK `(supersedes_evidence_id, workspace_id) ->
  evidence(id, workspace_id)`, nullable, for AC-07-001's own
  supersession mechanism -- both make a cross-Workspace reference
  structurally unrepresentable. `content_version`/`record_version` are
  two distinct BIGINT counters (see `evidence.models.Evidence`'s own
  module docstring for why they are not the same field). A trigger
  enforces creation in `UNVALIDATED` and 07 section 7's own transition
  topology (`INVALIDATED` effectively terminal -- no outgoing pair is
  legal from it), mirroring `sessions`'/`decisions`' own two-trigger
  precedent.

- `claim_anchors` (09 section 43: exact field list, "not a canonical
  domain object"). `target_id` carries NO foreign key -- a polymorphic
  reference to object classes that do not all exist yet
  (Assumption/Experiment/Insight), the identical disclosed treatment
  `human_authority_bindings.scope_id` (PKG-02) already established.
  `UNIQUE(id, workspace_id)` anchors `evidence_relations.claim_anchor_id`'s
  own composite FK. No trigger: 07 section 43.1 makes this table
  append-only by convention ("If target content changes, create a new
  ClaimAnchor") -- there is no update method anywhere in this
  package's own repository to enforce against, mirroring
  `question_lineage`'s own precedent (PKG-06).

- `evidence_relations` (09 section 44: exact field list, plus the
  disclosed `workspace_id` technical necessity). `relation_type` and
  `origin` are each CHECK-constrained to their own closed vocabularies.
  Composite FKs to `evidence` and `claim_anchors`. `ai_generation_id`
  carries no foreign key -- `ai_generations` does not exist until a
  future AI-operational migration, the identical disclosed limitation
  `question_lineage.ai_generation_id` (PKG-06) already established.

- `evidence_set_references` (09 section 45: exact field list, "does
  not itself become Evidence"). `member_evidence_id_and_version_list`
  is `JSONB` -- 09's own field name is a compound "id AND version"
  list, not a simple scalar array; `[IMPLEMENTATION CHOICE]`, the same
  "hybrid typed JSONB" treatment 14 section 22 itself names for
  provenance-adjacent structured data. `claim_anchor_refs` is
  `ARRAY(UUID)`, mirroring `commit_units.audit_event_ids`/`outbox_ids`'
  own precedent for an unbounded opaque-ref list with no per-element
  foreign key.

No `governed_commit_writer`/DB-principal separation is created here,
consistent with every migration since `001` (deferred to
`012_security_events_rls`). No cascading delete anywhere (14 section 49
default). Schema downgrade is infrastructure rollback only, not domain
rollback (14 section 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "321e335bb130"
down_revision: str | None = "e2f94137f8a9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 07 section 24's exact 5-value closed vocabulary.
_PROVENANCE_ORIGINS = ("HUMAN", "AI", "IMPORTED", "INFERRED", "SYSTEM_DERIVED")
# 07 section 2 / 14 section 6's exact closed vocabularies.
_EVIDENCE_TYPES = ("SYSTEM_PROOF", "DOMAIN_EVIDENCE", "AI_VALIDATION_PROOF")
_EVIDENCE_VALIDATION_STATES = ("UNVALIDATED", "STRUCTURALLY_VALID", "INVALIDATED", "UNAVAILABLE")
_EVIDENCE_RELATION_TYPES = ("UNASSESSED", "SUPPORTS", "CONTRADICTS", "CONTEXTUAL", "DOES_NOT_SUPPORT")


def _in_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{v}'" for v in values)


def upgrade() -> None:
    op.create_table(
        "source_references",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("locator", sa.Text(), nullable=False),
        sa.Column("external_id", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("content_fingerprint", sa.Text(), nullable=True),
        sa.Column("snapshot_ref", sa.Text(), nullable=True),
        sa.Column("created_by_ref", sa.Text(), nullable=False),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("validation_status", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_source_references"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_source_references_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            f"origin IN ({_in_list(_PROVENANCE_ORIGINS)})",
            name="ck_source_references_origin",
        ),
        sa.UniqueConstraint("id", "workspace_id", name="uq_source_references_id_workspace"),
    )
    op.create_index(
        "ix_source_references_workspace", "source_references", ["workspace_id"]
    )

    op.create_table(
        "evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_reference_id", sa.Uuid(), nullable=True),
        sa.Column("human_source_user_id", sa.Uuid(), nullable=True),
        sa.Column("reliability", sa.Text(), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("validation_state", sa.Text(), nullable=False),
        sa.Column("content_version", sa.BigInteger(), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False),
        sa.Column("supersedes_evidence_id", sa.Uuid(), nullable=True),
        sa.Column("provenance_ref", sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_evidence"),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name="fk_evidence_workspace", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["source_reference_id", "workspace_id"],
            ["source_references.id", "source_references.workspace_id"],
            name="fk_evidence_source_reference_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["human_source_user_id"],
            ["users.id"],
            name="fk_evidence_human_source_user",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_evidence_id", "workspace_id"],
            ["evidence.id", "evidence.workspace_id"],
            name="fk_evidence_supersedes_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(f"type IN ({_in_list(_EVIDENCE_TYPES)})", name="ck_evidence_type"),
        sa.CheckConstraint(
            f"validation_state IN ({_in_list(_EVIDENCE_VALIDATION_STATES)})",
            name="ck_evidence_validation_state",
        ),
        sa.UniqueConstraint("id", "workspace_id", name="uq_evidence_id_workspace"),
    )
    op.create_index("ix_evidence_workspace", "evidence", ["workspace_id"])
    op.create_index("ix_evidence_source_reference", "evidence", ["source_reference_id"])

    op.create_table(
        "claim_anchors",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("target_type", sa.Text(), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("claim_field_or_fragment", sa.Text(), nullable=False),
        sa.Column("target_content_version", sa.BigInteger(), nullable=False),
        sa.Column("content_fingerprint", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_claim_anchors"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_claim_anchors_workspace",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("id", "workspace_id", name="uq_claim_anchors_id_workspace"),
    )
    op.create_index("ix_claim_anchors_workspace", "claim_anchors", ["workspace_id"])
    op.create_index("ix_claim_anchors_target", "claim_anchors", ["target_type", "target_id"])

    op.create_table(
        "evidence_relations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("evidence_id", sa.Uuid(), nullable=False),
        sa.Column("evidence_content_version", sa.BigInteger(), nullable=False),
        sa.Column("claim_anchor_id", sa.Uuid(), nullable=False),
        sa.Column("relation_type", sa.Text(), nullable=False),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("producer_ref", sa.Text(), nullable=False),
        sa.Column("ai_generation_id", sa.Uuid(), nullable=True),
        sa.Column("human_adoption_ref", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_evidence_relations"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_evidence_relations_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["evidence_id", "workspace_id"],
            ["evidence.id", "evidence.workspace_id"],
            name="fk_evidence_relations_evidence_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["claim_anchor_id", "workspace_id"],
            ["claim_anchors.id", "claim_anchors.workspace_id"],
            name="fk_evidence_relations_claim_anchor_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            f"relation_type IN ({_in_list(_EVIDENCE_RELATION_TYPES)})",
            name="ck_evidence_relations_relation_type",
        ),
        sa.CheckConstraint(
            f"origin IN ({_in_list(_PROVENANCE_ORIGINS)})",
            name="ck_evidence_relations_origin",
        ),
    )
    op.create_index("ix_evidence_relations_workspace", "evidence_relations", ["workspace_id"])
    op.create_index("ix_evidence_relations_evidence", "evidence_relations", ["evidence_id"])
    op.create_index(
        "ix_evidence_relations_claim_anchor", "evidence_relations", ["claim_anchor_id"]
    )

    op.create_table(
        "evidence_set_references",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("consumer_type", sa.Text(), nullable=False),
        sa.Column("consumer_id", sa.Text(), nullable=True),
        sa.Column("member_evidence_id_and_version_list", postgresql.JSONB(), nullable=False),
        sa.Column("claim_anchor_refs", sa.ARRAY(sa.Uuid()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fingerprint", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_evidence_set_references"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_evidence_set_references_workspace",
            ondelete="RESTRICT",
        ),
    )
    op.create_index(
        "ix_evidence_set_references_workspace", "evidence_set_references", ["workspace_id"]
    )

    # Trigger 1: 07 section 6.1's own natural entry point -- structural
    # validation is a deterministic POST-creation check, so a newly
    # captured Evidence record starts UNVALIDATED.
    op.execute(
        """
        CREATE FUNCTION trg_evidence_enforce_initial_state() RETURNS trigger AS $$
        BEGIN
            IF NEW.validation_state <> 'UNVALIDATED' THEN
                RAISE EXCEPTION
                    'evidence must be created in UNVALIDATED (07 section 6.1), got %',
                    NEW.validation_state;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_evidence_enforce_initial_state
        BEFORE INSERT ON evidence
        FOR EACH ROW EXECUTE FUNCTION trg_evidence_enforce_initial_state();
        """
    )

    # Trigger 2: 07 section 7's exact transition table -- content
    # (`type`/`content`/`source_reference_id`/`human_source_user_id`/
    # `content_version`/`supersedes_evidence_id`) is immutable once set
    # (AC-07-001); only `validation_state`/`reliability`/`provenance_ref`
    # may change, and only along the approved pairs.
    op.execute(
        """
        CREATE FUNCTION trg_evidence_enforce_transition() RETURNS trigger AS $$
        BEGIN
            IF NEW.type IS DISTINCT FROM OLD.type
                OR NEW.content IS DISTINCT FROM OLD.content
                OR NEW.source_reference_id IS DISTINCT FROM OLD.source_reference_id
                OR NEW.human_source_user_id IS DISTINCT FROM OLD.human_source_user_id
                OR NEW.content_version IS DISTINCT FROM OLD.content_version
                OR NEW.supersedes_evidence_id IS DISTINCT FROM OLD.supersedes_evidence_id
            THEN
                RAISE EXCEPTION
                    'evidence content/identity fields are immutable once captured (AC-07-001)';
            END IF;
            IF NEW.validation_state IS DISTINCT FROM OLD.validation_state THEN
                IF NOT (
                    (OLD.validation_state = 'UNVALIDATED' AND NEW.validation_state IN ('STRUCTURALLY_VALID', 'INVALIDATED', 'UNAVAILABLE'))
                    OR (OLD.validation_state = 'STRUCTURALLY_VALID' AND NEW.validation_state IN ('INVALIDATED', 'UNAVAILABLE'))
                    OR (OLD.validation_state = 'UNAVAILABLE' AND NEW.validation_state IN ('STRUCTURALLY_VALID', 'INVALIDATED'))
                ) THEN
                    RAISE EXCEPTION
                        'illegal evidence validation transition % -> % (07 section 7)',
                        OLD.validation_state, NEW.validation_state;
                END IF;
                IF NEW.record_version <= OLD.record_version THEN
                    RAISE EXCEPTION
                        'evidence validation change must advance record_version (14 section 26), % -> %',
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
        CREATE TRIGGER trg_evidence_enforce_transition
        BEFORE UPDATE ON evidence
        FOR EACH ROW EXECUTE FUNCTION trg_evidence_enforce_transition();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_evidence_enforce_transition ON evidence;")
    op.execute("DROP FUNCTION IF EXISTS trg_evidence_enforce_transition();")
    op.execute("DROP TRIGGER IF EXISTS trg_evidence_enforce_initial_state ON evidence;")
    op.execute("DROP FUNCTION IF EXISTS trg_evidence_enforce_initial_state();")

    op.drop_index("ix_evidence_set_references_workspace", table_name="evidence_set_references")
    op.drop_table("evidence_set_references")

    op.drop_index("ix_evidence_relations_claim_anchor", table_name="evidence_relations")
    op.drop_index("ix_evidence_relations_evidence", table_name="evidence_relations")
    op.drop_index("ix_evidence_relations_workspace", table_name="evidence_relations")
    op.drop_table("evidence_relations")

    op.drop_index("ix_claim_anchors_target", table_name="claim_anchors")
    op.drop_index("ix_claim_anchors_workspace", table_name="claim_anchors")
    op.drop_table("claim_anchors")

    op.drop_index("ix_evidence_source_reference", table_name="evidence")
    op.drop_index("ix_evidence_workspace", table_name="evidence")
    op.drop_table("evidence")

    op.drop_index("ix_source_references_workspace", table_name="source_references")
    op.drop_table("source_references")
