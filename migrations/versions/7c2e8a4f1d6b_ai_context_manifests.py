"""ai context manifests

Revision ID: 7c2e8a4f1d6b
Revises: 4a7c1e9f2b3d
Create Date: 2026-09-21 12:00:00.000000

PKG-19 scope (14_IMPLEMENTATION_SEQUENCE.md section 9:
"007_ai_operational | generations, manifests, derived artifacts |
depends on: 004,006"). PKG-18 materialized the
`ai_generations`/`ai_derived_artifacts` half; this migration closes the
bucket with `ai_context_manifests` (14 PKG-19's own OBJECTIVE:
"AIContextManifest allowlist builder").

Table created:

- `ai_context_manifests` (09 section 54: exact field list). No 09-level
  DATA CONTRACT gives `source_classifications`/`excluded_context_classes`
  a closed vocabulary, so both are plain `TEXT[]` -- the same
  "example"/no-definitive-closure treatment `source_references.source_type`
  (PKG-16) already established. `coach_mode` is CHECK-constrained to
  08 section 10's own exact 7-value closed list ("LEVEL 1 defines").
  `input_artifact_refs_with_versions` is `JSONB` -- the identical
  compound "ref AND version" list shape
  `evidence_set_references.member_evidence_id_and_version_list`
  (PKG-16) already used for the same reason (09's own field name
  names a compound, not a scalar array). `UNIQUE(id, workspace_id)`
  anchors the retrofitted `ai_generations.ai_context_manifest_id`
  foreign key below.

Retrofitted this migration (composite FK, now that
`ai_context_manifests` exists):

- `ai_generations.ai_context_manifest_id -> ai_context_manifests(id,
  workspace_id)` -- previously a disclosed forward-reference gap
  (PKG-18, this package's own predecessor).

No `ai_gateway_writer` DB-principal/GRANT is created here, consistent
with every migration since `001` (deferred to `012_security_events_rls`).
No cascading delete anywhere (14 section 49 default). Schema downgrade
is infrastructure rollback only, not domain rollback (14 section 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7c2e8a4f1d6b"
down_revision: str | None = "4a7c1e9f2b3d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 08 section 4's exact 16-value closed vocabulary (sections 23-38).
_AI_OPERATION_IDS = tuple(f"AIOP-{n:03d}" for n in range(1, 17))
# 08 section 10's exact 7-value closed vocabulary.
_COACH_MODES = (
    "SILENT",
    "REFLECTIVE",
    "CHALLENGER",
    "SOCRATIC",
    "FACILITATOR",
    "RESEARCHER",
    "STRATEGIST",
)


def _in_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{v}'" for v in values)


def upgrade() -> None:
    op.create_table(
        "ai_context_manifests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("ai_operation_id", sa.Text(), nullable=False),
        sa.Column("ai_operation_contract_version", sa.Text(), nullable=False),
        sa.Column("requesting_actor_ref", sa.Text(), nullable=False),
        sa.Column("input_artifact_refs_with_versions", postgresql.JSONB(), nullable=False),
        sa.Column("source_classifications", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("method_ref", sa.Text(), nullable=True),
        sa.Column("coach_mode", sa.Text(), nullable=True),
        sa.Column("burst_mode", sa.Text(), nullable=True),
        sa.Column(
            "excluded_context_classes",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("assembled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("context_fingerprint", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_ai_context_manifests"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_ai_context_manifests_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            f"ai_operation_id IN ({_in_list(_AI_OPERATION_IDS)})",
            name="ck_ai_context_manifests_ai_operation_id",
        ),
        sa.CheckConstraint(
            f"coach_mode IS NULL OR coach_mode IN ({_in_list(_COACH_MODES)})",
            name="ck_ai_context_manifests_coach_mode",
        ),
        sa.UniqueConstraint("id", "workspace_id", name="uq_ai_context_manifests_id_workspace"),
    )
    op.create_index("ix_ai_context_manifests_workspace", "ai_context_manifests", ["workspace_id"])

    # Retrofit: `ai_context_manifests` now exists.
    op.create_foreign_key(
        "fk_ai_generations_context_manifest_workspace",
        "ai_generations",
        "ai_context_manifests",
        ["ai_context_manifest_id", "workspace_id"],
        ["id", "workspace_id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_ai_generations_context_manifest_workspace", "ai_generations", type_="foreignkey"
    )

    op.drop_index("ix_ai_context_manifests_workspace", table_name="ai_context_manifests")
    op.drop_table("ai_context_manifests")
