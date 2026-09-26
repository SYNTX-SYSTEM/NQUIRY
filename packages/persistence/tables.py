"""SQLAlchemy Core table definitions matching the migration DDL.

These are query-time table definitions, deliberately separate from
`migrations/versions/72e4c8ea6772_semantic_identity_workspace.py`'s own
explicit DDL: a migration is an immutable historical record (14 §9)
and must not depend on application code that changes after the
migration is written. Duplication between a migration's DDL and its
matching query-time `Table` object is the standard SQLAlchemy/Alembic
pattern, not an architecture violation.

Column set matches the migration exactly. See
`72e4c8ea6772_semantic_identity_workspace.py`'s docstring for why
`role`/`organization_id`/`preferences` are absent from `users`, and why
`workspaces.owner_id` is mandatory. See
`01a37c093cd6_membership_governance.py`'s docstring for
`workspace_memberships`/`role_assignments`/`human_authority_bindings`
(including why `facilitator_scope_bindings` is deliberately absent) and
for the two triggers that migration attaches to
`human_authority_bindings` (not representable as SQLAlchemy Core
`Table` metadata — they are pure database-side enforcement, invisible
to and unaffected by this module). See
`d467112ce46d_challenge_session.py`'s docstring for `challenges`/
`sessions` — including why neither `status` nor
`emotional_temperature` exists on `challenges`, why `sessions` carries
a *composite* foreign key into `challenges`, and for the two further
triggers enforcing 03's transition topology, likewise invisible here.
See the PKG-06 migration's docstring for `questions`/`question_lineage`
— including why neither `text` nor `status` exists on `questions`, why
`question_lineage`'s `ai_generation_id` has no foreign key (its target
table does not exist until migration `007_ai_operational`), and for
the immutability triggers on both tables, likewise invisible here.
See the PKG-07 migration's docstring for `question_bursts`/
`burst_question_memberships` — including the retrofitted
`uq_sessions_id_workspace` anchor on `sessions` (added by that
migration, not `d467112ce46d`, because PKG-05 had no consumer for it
yet), why `mode`/`capture_origin` are each CHECK-constrained twice
(once to 09's full approved vocabulary, once to this package's own
Human-only scope restriction), and for the freeze-enforcement
triggers, likewise invisible here.
See the PKG-10 migration's docstring for `commands`/`command_attempts`
— including why `commands` has no foreign key from `command_attempts`'
`commit_id` column (`commit_units` does not exist until migration
`009_commit_audit_outbox`, PKG-13), and for the immutability triggers
on both tables, likewise invisible here.
See the PKG-11 migration's docstring for `idempotency_records` —
including why its primary key is the composite `(workspace_id,
command_type, idempotency_key)` rather than a surrogate id, why its
`outcome` vocabulary deliberately differs from `command_attempts.outcome`,
and for the identity-immutability/outcome-transition triggers, likewise
invisible here.
See the PKG-12 migration's docstring for `audit_events`/`outbox_events`
— including why `audit_events` has no foreign key from `commit_id`
(`commit_units` does not exist until PKG-13's own migration revision,
the second half of the conceptual "009_commit_audit_outbox" bucket),
why `audit_events` is immutable against both UPDATE and DELETE, and for
`outbox_events`' identity-immutability/delivery-status-transition
triggers, likewise invisible here.
See the PKG-13 migration's docstring for `commit_units` — including why
its `target_refs`/`relation_refs`/`governance_refs`/`audit_event_ids`/
`outbox_ids` array columns carry no foreign keys, and for the
retrofitted composite `commit_id` foreign keys this same migration adds
to `command_attempts`, `idempotency_records`, `audit_events`, and
`outbox_events` (each column already existed nullable with no FK,
disclosed forward-reference gaps their own migrations named explicitly).
See the PKG-14 migration's docstring for `question_selections` —
including why `human_authority_binding_id` carries no foreign key, and
for the cardinality-enforcing trigger and partial unique index
(neither representable as SQLAlchemy Core `Table` metadata), likewise
invisible here.
See the PKG-15 migration's docstring for `decisions` — including why
`decision_authority_binding_id` carries no foreign key, and for the two
triggers enforcing 03's Decision transition topology (making `DECIDED`
terminal at the database layer too), likewise invisible here.
See the PKG-16 migration's docstring for `source_references`,
`evidence`, `claim_anchors`, `evidence_relations`, and
`evidence_set_references` — including why `claim_anchors.target_id`
carries no foreign key (a polymorphic reference, same treatment as
`human_authority_bindings.scope_id`), why `evidence_relations.ai_generation_id`
carries no foreign key (its target table does not exist until a future
AI-operational migration), and for the validation-state transition
trigger on `evidence`, likewise invisible here.
See the PKG-18 migration's docstring for `ai_generations` and
`ai_derived_artifacts` — including the retrofitted composite
`ai_generation_id` foreign keys this migration adds to
`question_lineage` (PKG-06) and `evidence_relations` (PKG-16) now that
their long-disclosed forward-reference gap has a real target, why
`ai_generations.output_artifact_ref` carries no foreign key (would
require a circular same-migration dependency, the same disclosed
choice `commit_units.audit_event_ids`/`outbox_ids` already made), and
for the two triggers enforcing 08 section 15's AIGeneration transition
topology, likewise invisible here.
See the PKG-19 migration's docstring for `ai_context_manifests` —
including the retrofitted `ai_generations.ai_context_manifest_id`
foreign key this migration adds now that its own long-disclosed
forward-reference gap (PKG-18) has a real target, and why
`coach_mode` is CHECK-constrained to 08 section 10's own exact 7-value
closed list while `source_classifications`/`excluded_context_classes`
stay plain `TEXT[]`.
See the PKG-21 migration's docstring for `projection_checkpoints`,
`session_read_model`, and `inquiry_read_model` — including why
`inquiry_read_model` is a deliberately generic per-aggregate snapshot
rather than the full InquiryGraph (12's own minimum-prototype scope
excludes that graph entirely), why `session_read_model` carries a real
composite foreign key into `sessions` (the "corrupt projection"
mandatory attack's own structural defense), and why
`checkpoint_version`/`projection_version` are plain integers, never a
`RecordVersion` reuse.
See the PKG-23 migration's docstring for `recovery_records` —
including why `original_attempt_id`/`human_decision_ref` carry no
foreign key (their target tables have no `UNIQUE(id, workspace_id)`
anchor yet), why `original_command_id`/`original_commit_id` DO carry
real composite foreign keys, and for the identity-immutability/
result-transition triggers, likewise invisible here.
See the PKG-24 migration's docstring for `recovery_records.record_version`/
`blocked_target_refs` — a disclosed retrofit closing 14 section 7.1's
own "Version: record_version" gap PKG-23 left open, and the "dependency
blocking metadata" 14 section 29 names, represented without a separate
join table (`is_target_blocked` reads directly against
`result = 'UNRESOLVED' AND :target_ref = ANY (blocked_target_refs)`).
See the PKG-26 migration's docstring for `security_events` — including
why `workspace_id`/`command_id`/`generation_id`/`recovery_id` carry no
foreign key at all (a `SecurityEvent`'s own purpose can be to record a
forged/unresolvable claim), and for the RLS policies this same
migration enables on every Workspace-keyed table above, none of which
is representable as SQLAlchemy Core `Table` metadata either.
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

metadata = sa.MetaData()

users_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("email", sa.Text(), nullable=False, unique=True),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

workspaces_table = sa.Table(
    "workspaces",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column(
        "owner_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    ),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

workspace_memberships_table = sa.Table(
    "workspace_memberships",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
    sa.Column("status", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
)

role_assignments_table = sa.Table(
    "role_assignments",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column(
        "membership_id",
        sa.Uuid(),
        sa.ForeignKey("workspace_memberships.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("role", sa.Text(), nullable=False),
    sa.Column(
        "granted_by_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
)

human_authority_bindings_table = sa.Table(
    "human_authority_bindings",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column(
        "human_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    ),
    sa.Column("authority_class", sa.Text(), nullable=False),
    sa.Column("scope_type", sa.Text(), nullable=False),
    sa.Column("scope_id", sa.Uuid(), nullable=False),
    sa.Column("authority_source", sa.Text(), nullable=False),
    sa.Column(
        "granted_by_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column(
        "revoked_by_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    ),
    sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("state", sa.Text(), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
)

challenges_table = sa.Table(
    "challenges",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("title", sa.Text(), nullable=False),
    sa.Column("description", sa.Text(), nullable=True),
    sa.Column("context", sa.Text(), nullable=True),
    sa.Column("desired_outcome", sa.Text(), nullable=True),
    sa.Column("constraints", sa.Text(), nullable=True),
    sa.Column("stakeholders", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.UniqueConstraint("id", "workspace_id", name="uq_challenges_id_workspace"),
)

sessions_table = sa.Table(
    "sessions",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("challenge_id", sa.Uuid(), nullable=False),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("applied_method_key", sa.Text(), nullable=False),
    sa.Column("applied_method_version", sa.Text(), nullable=False),
    sa.Column("state", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    # The composite FK, not a plain `challenge_id` reference: 09 §27.1
    # permits the denormalized `workspace_id` only under the constraint
    # that it equals the Challenge's Workspace.
    sa.ForeignKeyConstraint(
        ["challenge_id", "workspace_id"],
        ["challenges.id", "challenges.workspace_id"],
        name="fk_sessions_challenge_workspace",
        ondelete="RESTRICT",
    ),
    # Retrofitted by PKG-07's migration (not d467112ce46d, which had no
    # consumer for it yet): anchor for question_bursts' own composite
    # FK into sessions.
    sa.UniqueConstraint("id", "workspace_id", name="uq_sessions_id_workspace"),
)

questions_table = sa.Table(
    "questions",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "challenge_id",
        sa.Uuid(),
        sa.ForeignKey("challenges.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("original_text", sa.Text(), nullable=False),
    sa.Column("normalized_text", sa.Text(), nullable=True),
    sa.Column("origin", sa.Text(), nullable=False),
    sa.Column(
        "author_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    ),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.UniqueConstraint("id", "workspace_id", name="uq_questions_id_workspace"),
    # 02 §14.4 / 09 §27.1-style constrained denormalization: `workspace_id`
    # must equal the Challenge's own Workspace.
    sa.ForeignKeyConstraint(
        ["challenge_id", "workspace_id"],
        ["challenges.id", "challenges.workspace_id"],
        name="fk_questions_challenge_workspace",
        ondelete="RESTRICT",
    ),
)

question_lineage_table = sa.Table(
    "question_lineage",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("parent_question_id", sa.Uuid(), nullable=False),
    sa.Column("child_question_id", sa.Uuid(), nullable=False),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("transformation_type", sa.Text(), nullable=False),
    sa.Column("producer_origin", sa.Text(), nullable=False),
    sa.Column("ai_generation_id", sa.Uuid(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    # Both composite FKs reference the *same* `workspace_id` column on
    # this row, which structurally forces parent and child to share one
    # Workspace -- this is what makes cross-Workspace lineage
    # unrepresentable, not application logic.
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
    # PKG-18: retrofitted now that `ai_generations` exists (previously a
    # disclosed forward-reference gap, PKG-06). A partial-NULL composite
    # FK (MATCH SIMPLE, PostgreSQL's default) is unenforced whenever
    # `ai_generation_id IS NULL` -- the same nullable-composite-FK shape
    # `evidence.source_reference_id` (PKG-16) already uses.
    sa.ForeignKeyConstraint(
        ["ai_generation_id", "workspace_id"],
        ["ai_generations.id", "ai_generations.workspace_id"],
        name="fk_question_lineage_ai_generation_workspace",
        ondelete="RESTRICT",
    ),
)

question_bursts_table = sa.Table(
    "question_bursts",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("session_id", sa.Uuid(), nullable=False),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("state", sa.Text(), nullable=False),
    sa.Column("mode", sa.Text(), nullable=False),
    sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("frozen_membership_fingerprint", sa.Text(), nullable=True),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.UniqueConstraint("id", "workspace_id", name="uq_question_bursts_id_workspace"),
    # F03 WU-03.2 (EC-1, migration e5a1b3c8f204): at most one Burst per Session, ever.
    sa.UniqueConstraint("session_id", name="uq_question_bursts_session"),
    sa.ForeignKeyConstraint(
        ["session_id", "workspace_id"],
        ["sessions.id", "sessions.workspace_id"],
        name="fk_question_bursts_session_workspace",
        ondelete="RESTRICT",
    ),
)

burst_question_memberships_table = sa.Table(
    "burst_question_memberships",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("question_burst_id", sa.Uuid(), nullable=False),
    sa.Column("question_id", sa.Uuid(), nullable=False, unique=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("captured_order", sa.Integer(), nullable=False),
    sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column(
        "capture_actor_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    ),
    sa.Column("capture_origin", sa.Text(), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    # F03 WU-03.2 (FBR-F03-6, migration e5a1b3c8f204): one ordinal per capture event.
    sa.UniqueConstraint(
        "question_burst_id", "captured_order", name="uq_burst_memberships_burst_order"
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
)

commands_table = sa.Table(
    "commands",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("command_type", sa.Text(), nullable=False),
    sa.Column("contract_version", sa.Text(), nullable=False),
    sa.Column("payload_fingerprint", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    # F03 WU-03.4 (migration f6b2c4d9a318): the refs the Command targets (09 §9).
    sa.Column("target_refs", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
    sa.UniqueConstraint("id", "workspace_id", name="uq_commands_id_workspace"),
)

command_attempts_table = sa.Table(
    "command_attempts",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("command_id", sa.Uuid(), nullable=False),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("actor_ref", sa.Text(), nullable=False),
    sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("boundary_evaluation_summary_ref", sa.Uuid(), nullable=True),
    sa.Column("commit_id", sa.Uuid(), nullable=True),
    sa.Column("outcome", sa.Text(), nullable=True),
    sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("failure_code", sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(
        ["command_id", "workspace_id"],
        ["commands.id", "commands.workspace_id"],
        name="fk_command_attempts_command_workspace",
        ondelete="RESTRICT",
    ),
    sa.ForeignKeyConstraint(
        ["commit_id", "workspace_id"],
        ["commit_units.id", "commit_units.workspace_id"],
        name="fk_command_attempts_commit_workspace",
        ondelete="RESTRICT",
    ),
)

idempotency_records_table = sa.Table(
    "idempotency_records",
    metadata,
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
    sa.ForeignKeyConstraint(
        ["commit_id", "workspace_id"],
        ["commit_units.id", "commit_units.workspace_id"],
        name="fk_idempotency_records_commit_workspace",
        ondelete="RESTRICT",
    ),
)

audit_events_table = sa.Table(
    "audit_events",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("event_type", sa.Text(), nullable=False),
    sa.Column("event_schema_version", sa.Text(), nullable=False),
    sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("actor_type", sa.Text(), nullable=False),
    sa.Column("actor_id", sa.Text(), nullable=False),
    sa.Column("command_type", sa.Text(), nullable=False),
    sa.Column("command_id", sa.Uuid(), nullable=False),
    sa.Column("commit_id", sa.Uuid(), nullable=False),
    sa.Column("correlation_id", sa.Uuid(), nullable=False),
    sa.Column("causation_id", sa.Uuid(), nullable=True),
    sa.Column("target_refs", sa.ARRAY(sa.Text()), nullable=False),
    sa.Column("authority_source_ref", sa.Uuid(), nullable=False),
    # F02 HD-6 (migration a7f2c91d4e10): typed provenance. NULL = pre-F02 untyped row.
    sa.Column("authority_source_type", sa.Text(), nullable=True),
    sa.Column("authority_scope_ref", sa.Text(), nullable=True),
    sa.Column("result", sa.Text(), nullable=False),
    sa.Column("human_decision_ref", sa.Uuid(), nullable=True),
    sa.Column("evidence_set_ref", sa.Uuid(), nullable=True),
    sa.Column("state_before_ref", sa.Text(), nullable=True),
    sa.Column("state_after_ref", sa.Text(), nullable=True),
    sa.Column("failure_code", sa.Text(), nullable=True),
    sa.Column("metadata_ref", sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(
        ["command_id", "workspace_id"],
        ["commands.id", "commands.workspace_id"],
        name="fk_audit_events_command_workspace",
        ondelete="RESTRICT",
    ),
    sa.ForeignKeyConstraint(
        ["commit_id", "workspace_id"],
        ["commit_units.id", "commit_units.workspace_id"],
        name="fk_audit_events_commit_workspace",
        ondelete="RESTRICT",
    ),
)

outbox_events_table = sa.Table(
    "outbox_events",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("event_id", sa.Uuid(), nullable=False, unique=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("commit_id", sa.Uuid(), nullable=False),
    sa.Column("event_type", sa.Text(), nullable=False),
    sa.Column("event_payload_ref", sa.Text(), nullable=True),
    sa.Column("delivery_status", sa.Text(), nullable=False),
    sa.Column("delivery_attempt_count", sa.Integer(), nullable=False),
    sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(
        ["commit_id", "workspace_id"],
        ["commit_units.id", "commit_units.workspace_id"],
        name="fk_outbox_events_commit_workspace",
        ondelete="RESTRICT",
    ),
)

committed_events_table = sa.Table(
    "committed_events",
    metadata,
    sa.Column("event_id", sa.Uuid(), primary_key=True),
    sa.Column("event_type", sa.Text(), nullable=False),
    sa.Column("event_schema_version", sa.Text(), nullable=False),
    sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("aggregate_ref", sa.Text(), nullable=False),
    sa.Column("aggregate_version_after_commit", sa.BigInteger(), nullable=False),
    sa.Column("command_id", sa.Uuid(), nullable=False),
    sa.Column("commit_id", sa.Uuid(), nullable=False),
    sa.Column("correlation_id", sa.Uuid(), nullable=False),
    sa.Column("causation_id", sa.Uuid(), nullable=True),
    sa.Column("actor_ref", sa.Text(), nullable=False),
    sa.Column("authority_source_ref", sa.Uuid(), nullable=False),
    sa.Column("payload", postgresql.JSONB(), nullable=False),
    sa.ForeignKeyConstraint(
        ["event_id"],
        ["outbox_events.event_id"],
        name="fk_committed_events_outbox_event",
        ondelete="RESTRICT",
    ),
    sa.ForeignKeyConstraint(
        ["commit_id", "workspace_id"],
        ["commit_units.id", "commit_units.workspace_id"],
        name="fk_committed_events_commit_workspace",
        ondelete="RESTRICT",
    ),
)
"""WU-PFC-F08-1 (F08): one immutable row per outbox record, the exact 09 §16
EventEnvelope. See migration `a9f3c2e81d57` for the outbox binding and the
UPDATE/DELETE rejection triggers."""

commit_units_table = sa.Table(
    "commit_units",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("command_id", sa.Uuid(), nullable=False),
    sa.Column("attempt_id", sa.Uuid(), nullable=False),
    sa.Column("target_refs", sa.ARRAY(sa.Text()), nullable=False),
    sa.Column("relation_refs", sa.ARRAY(sa.Text()), nullable=False),
    sa.Column("governance_refs", sa.ARRAY(sa.Text()), nullable=False),
    sa.Column("audit_event_ids", sa.ARRAY(sa.Uuid()), nullable=False),
    sa.Column("outbox_ids", sa.ARRAY(sa.Uuid()), nullable=False),
    sa.Column("commit_time_proof_ref", sa.Uuid(), nullable=True),
    sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("outcome", sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(
        ["command_id", "workspace_id"],
        ["commands.id", "commands.workspace_id"],
        name="fk_commit_units_command_workspace",
        ondelete="RESTRICT",
    ),
    sa.ForeignKeyConstraint(
        ["attempt_id"], ["command_attempts.id"], name="fk_commit_units_attempt", ondelete="RESTRICT"
    ),
    sa.UniqueConstraint("id", "workspace_id", name="uq_commit_units_id_workspace"),
)

question_selections_table = sa.Table(
    "question_selections",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("session_id", sa.Uuid(), nullable=False),
    sa.Column("question_id", sa.Uuid(), nullable=False),
    sa.Column("selection_type", sa.Text(), nullable=False),
    sa.Column(
        "selected_by_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    # No foreign key: `human_authority_bindings` carries no
    # `UNIQUE(id, workspace_id)` anchor (same disclosed treatment as
    # `audit_events.authority_source_ref`, PKG-12) -- 09 §33.1's own
    # wording, "That stored binding reference does not authorize future
    # changes", confirms this is a proof reference, not a live
    # authorization join.
    sa.Column("human_authority_binding_id", sa.Uuid(), nullable=False),
    sa.Column("selected_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
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
    sa.CheckConstraint(
        "selection_type IN ('COMPELLING', 'PRIMARY')",
        name="ck_question_selections_selection_type",
    ),
    # 09 §33: literal duplicate selection (same Question, same type,
    # same Session) is structurally impossible, not just checked in
    # code -- mandatory adversarial attack "duplicate selection where
    # relation semantics forbid it".
    sa.UniqueConstraint(
        "session_id",
        "question_id",
        "selection_type",
        name="uq_question_selections_session_question_type",
    ),
)

decisions_table = sa.Table(
    "decisions",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("challenge_id", sa.Uuid(), nullable=False),
    sa.Column("decision_question_ref", sa.Uuid(), nullable=True),
    sa.Column("decision_question_text", sa.Text(), nullable=True),
    sa.Column("options", sa.ARRAY(sa.Text()), nullable=False),
    sa.Column("criteria", sa.ARRAY(sa.Text()), nullable=False),
    sa.Column("selected_option", sa.Text(), nullable=True),
    sa.Column("rationale", sa.Text(), nullable=True),
    sa.Column("confidence", sa.Text(), nullable=True),
    sa.Column("state", sa.Text(), nullable=False),
    sa.Column(
        "opened_by_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    # No foreign key: same disclosed treatment as
    # `question_selections.human_authority_binding_id` (PKG-14) --
    # `human_authority_bindings` has no `UNIQUE(id, workspace_id)`
    # anchor, and this is a proof reference, not a live authorization
    # join.
    sa.Column("decision_authority_binding_id", sa.Uuid(), nullable=False),
    sa.Column(
        "decided_by_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    ),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.Column("provenance_ref", sa.Uuid(), nullable=True),
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
    sa.CheckConstraint(
        "state IN ('UNDER_CONSIDERATION', 'DECIDED')",
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

source_references_table = sa.Table(
    "source_references",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
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
    sa.CheckConstraint(
        "origin IN ('HUMAN', 'AI', 'IMPORTED', 'INFERRED', 'SYSTEM_DERIVED')",
        name="ck_source_references_origin",
    ),
    sa.UniqueConstraint("id", "workspace_id", name="uq_source_references_id_workspace"),
)

evidence_table = sa.Table(
    "evidence",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("type", sa.Text(), nullable=False),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("source_reference_id", sa.Uuid(), nullable=True),
    sa.Column(
        "human_source_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    ),
    sa.Column("reliability", sa.Text(), nullable=True),
    sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("validation_state", sa.Text(), nullable=False),
    sa.Column("content_version", sa.BigInteger(), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.Column("supersedes_evidence_id", sa.Uuid(), nullable=True),
    sa.Column("provenance_ref", sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(
        ["source_reference_id", "workspace_id"],
        ["source_references.id", "source_references.workspace_id"],
        name="fk_evidence_source_reference_workspace",
        ondelete="RESTRICT",
    ),
    sa.ForeignKeyConstraint(
        ["supersedes_evidence_id", "workspace_id"],
        ["evidence.id", "evidence.workspace_id"],
        name="fk_evidence_supersedes_workspace",
        ondelete="RESTRICT",
    ),
    sa.CheckConstraint(
        "type IN ('SYSTEM_PROOF', 'DOMAIN_EVIDENCE', 'AI_VALIDATION_PROOF')",
        name="ck_evidence_type",
    ),
    sa.CheckConstraint(
        "validation_state IN ('UNVALIDATED', 'STRUCTURALLY_VALID', 'INVALIDATED', 'UNAVAILABLE')",
        name="ck_evidence_validation_state",
    ),
    sa.UniqueConstraint("id", "workspace_id", name="uq_evidence_id_workspace"),
)

claim_anchors_table = sa.Table(
    "claim_anchors",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("target_type", sa.Text(), nullable=False),
    # No foreign key: polymorphic reference, same treatment as
    # `human_authority_bindings.scope_id` (PKG-02) -- 07 §10.1's own
    # examples span object classes that do not exist yet
    # (Assumption/Experiment/Insight).
    sa.Column("target_id", sa.Uuid(), nullable=False),
    sa.Column("claim_field_or_fragment", sa.Text(), nullable=False),
    sa.Column("target_content_version", sa.BigInteger(), nullable=False),
    sa.Column("content_fingerprint", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.UniqueConstraint("id", "workspace_id", name="uq_claim_anchors_id_workspace"),
)

evidence_relations_table = sa.Table(
    "evidence_relations",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
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
    # PKG-18: retrofitted now that `ai_generations` exists (previously a
    # disclosed forward-reference gap, PKG-16).
    sa.ForeignKeyConstraint(
        ["ai_generation_id", "workspace_id"],
        ["ai_generations.id", "ai_generations.workspace_id"],
        name="fk_evidence_relations_ai_generation_workspace",
        ondelete="RESTRICT",
    ),
    sa.CheckConstraint(
        "relation_type IN "
        "('UNASSESSED', 'SUPPORTS', 'CONTRADICTS', 'CONTEXTUAL', 'DOES_NOT_SUPPORT')",
        name="ck_evidence_relations_relation_type",
    ),
    sa.CheckConstraint(
        "origin IN ('HUMAN', 'AI', 'IMPORTED', 'INFERRED', 'SYSTEM_DERIVED')",
        name="ck_evidence_relations_origin",
    ),
)

evidence_set_references_table = sa.Table(
    "evidence_set_references",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("consumer_type", sa.Text(), nullable=False),
    sa.Column("consumer_id", sa.Text(), nullable=True),
    sa.Column("member_evidence_id_and_version_list", postgresql.JSONB(), nullable=False),
    sa.Column("claim_anchor_refs", sa.ARRAY(sa.Uuid()), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("fingerprint", sa.Text(), nullable=False),
)

ai_generations_table = sa.Table(
    "ai_generations",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
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
    # No foreign key: would require a circular same-migration dependency
    # on `ai_derived_artifacts` (this table is created first). Same
    # disclosed choice `commit_units.audit_event_ids`/`outbox_ids`
    # (PKG-13) already made for an analogous forward self-reference.
    sa.Column("output_artifact_ref", sa.Uuid(), nullable=True),
    sa.Column("failure_code", sa.Text(), nullable=True),
    sa.Column("failure_detail_ref", sa.Text(), nullable=True),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    # F04 WU-04.3 (migration a8d3f1c6e902): the persisted operation
    # authorization OA (§0.1 rules 3/8), identity-immutable.
    sa.Column("session_id", sa.Uuid(), nullable=True),
    sa.Column("operation_authorization_id", sa.Uuid(), nullable=True),
    sa.Column("authorizing_command_id", sa.Uuid(), nullable=True),
    sa.Column("precondition_artifact_ref", sa.Uuid(), nullable=True),
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
    # PKG-19: retrofitted now that `ai_context_manifests` exists
    # (previously a disclosed forward-reference gap, PKG-18).
    sa.ForeignKeyConstraint(
        ["ai_context_manifest_id", "workspace_id"],
        ["ai_context_manifests.id", "ai_context_manifests.workspace_id"],
        name="fk_ai_generations_context_manifest_workspace",
        ondelete="RESTRICT",
    ),
    sa.CheckConstraint(
        "ai_operation_id IN ("
        "'AIOP-001','AIOP-002','AIOP-003','AIOP-004','AIOP-005','AIOP-006','AIOP-007','AIOP-008',"
        "'AIOP-009','AIOP-010','AIOP-011','AIOP-012','AIOP-013','AIOP-014','AIOP-015','AIOP-016')",
        name="ck_ai_generations_ai_operation_id",
    ),
    sa.CheckConstraint(
        "status IN ('REQUESTED', 'RUNNING', 'OUTPUT_RECEIVED', 'VALIDATED', 'REJECTED', 'FAILED')",
        name="ck_ai_generations_status",
    ),
    sa.UniqueConstraint("id", "workspace_id", name="uq_ai_generations_id_workspace"),
)

ai_derived_artifacts_table = sa.Table(
    "ai_derived_artifacts",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("ai_generation_id", sa.Uuid(), nullable=False),
    sa.Column("ai_operation_id", sa.Text(), nullable=False),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("content_fingerprint", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.Column("provenance_ref", sa.Text(), nullable=True),
    # F04 WU-04.3: acceptance facts (append-only; NULL on pre-F04 rows).
    sa.Column("session_id", sa.Uuid(), nullable=True),
    sa.Column("accepted_by_command_id", sa.Uuid(), nullable=True),
    sa.Column("proof_class", sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(
        ["ai_generation_id", "workspace_id"],
        ["ai_generations.id", "ai_generations.workspace_id"],
        name="fk_ai_derived_artifacts_generation_workspace",
        ondelete="RESTRICT",
    ),
    sa.CheckConstraint(
        "ai_operation_id IN ("
        "'AIOP-001','AIOP-002','AIOP-003','AIOP-004','AIOP-005','AIOP-006','AIOP-007','AIOP-008',"
        "'AIOP-009','AIOP-010','AIOP-011','AIOP-012','AIOP-013','AIOP-014','AIOP-015','AIOP-016')",
        name="ck_ai_derived_artifacts_ai_operation_id",
    ),
)

ai_context_manifests_table = sa.Table(
    "ai_context_manifests",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("ai_operation_id", sa.Text(), nullable=False),
    sa.Column("ai_operation_contract_version", sa.Text(), nullable=False),
    sa.Column("requesting_actor_ref", sa.Text(), nullable=False),
    sa.Column("input_artifact_refs_with_versions", postgresql.JSONB(), nullable=False),
    sa.Column("source_classifications", sa.ARRAY(sa.Text()), nullable=False),
    sa.Column("method_ref", sa.Text(), nullable=True),
    sa.Column("coach_mode", sa.Text(), nullable=True),
    sa.Column("burst_mode", sa.Text(), nullable=True),
    sa.Column("excluded_context_classes", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
    sa.Column("assembled_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("context_fingerprint", sa.Text(), nullable=False),
    # F04 WU-04.3/04.4 (FBR-F04-6): the frozen-set binding. Immutable table.
    sa.Column("session_id", sa.Uuid(), nullable=True),
    sa.Column("frozen_set_ref", sa.Text(), nullable=True),
    sa.Column("frozen_set_fingerprint", sa.Text(), nullable=True),
    sa.CheckConstraint(
        "ai_operation_id IN ("
        "'AIOP-001','AIOP-002','AIOP-003','AIOP-004','AIOP-005','AIOP-006','AIOP-007','AIOP-008',"
        "'AIOP-009','AIOP-010','AIOP-011','AIOP-012','AIOP-013','AIOP-014','AIOP-015','AIOP-016')",
        name="ck_ai_context_manifests_ai_operation_id",
    ),
    sa.CheckConstraint(
        "coach_mode IS NULL OR coach_mode IN ("
        "'SILENT','REFLECTIVE','CHALLENGER','SOCRATIC','FACILITATOR','RESEARCHER','STRATEGIST')",
        name="ck_ai_context_manifests_coach_mode",
    ),
    sa.UniqueConstraint("id", "workspace_id", name="uq_ai_context_manifests_id_workspace"),
)

ai_operation_authorizations_table = sa.Table(
    "ai_operation_authorizations",
    metadata,
    # F04 WU-04.3 (PI-4, §0.1): one immutable row per operation authorization
    # OA = (authorizing_command_id, ai_operation_id). Migration a8d3f1c6e902.
    sa.Column("id", sa.Uuid(), primary_key=True),
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
)

ai_validation_proofs_table = sa.Table(
    "ai_validation_proofs",
    metadata,
    # F04 WU-04.3 (09 §56, FBR-F04-4): one immutable proof per generation.
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("workspace_id", sa.Uuid(), nullable=False),
    sa.Column("ai_generation_id", sa.Uuid(), nullable=False, unique=True),
    sa.Column("ai_operation_id", sa.Text(), nullable=False),
    sa.Column("contract_version", sa.Text(), nullable=False),
    sa.Column("validator_version", sa.Text(), nullable=False),
    sa.Column("validation_result", sa.Text(), nullable=False),
    sa.Column("validated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("output_fingerprint", sa.Text(), nullable=False),
    sa.Column("validation_details_ref", sa.Text(), nullable=True),
)

question_clusters_table = sa.Table(
    "question_clusters",
    metadata,
    # F04 WU-04.9 (09 §34; migration c2e7b9a4f513). Append-only.
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("workspace_id", sa.Uuid(), nullable=False),
    sa.Column("session_id", sa.Uuid(), nullable=False),
    sa.Column("challenge_id", sa.Uuid(), nullable=False),
    sa.Column("analysis_generation_id", sa.Uuid(), nullable=False),
    sa.Column("cluster_run_id", sa.Uuid(), nullable=False),
    sa.Column("label", sa.Text(), nullable=True),
    sa.Column("description", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
)

question_cluster_memberships_table = sa.Table(
    "question_cluster_memberships",
    metadata,
    # F04 WU-04.9 (09 §35). Append-only; frozen-set members only (trigger).
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("workspace_id", sa.Uuid(), nullable=False),
    sa.Column("session_id", sa.Uuid(), nullable=False),
    sa.Column("question_cluster_id", sa.Uuid(), nullable=False),
    sa.Column("question_id", sa.Uuid(), nullable=False),
    sa.Column("cluster_run_id", sa.Uuid(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

projection_checkpoints_table = sa.Table(
    "projection_checkpoints",
    metadata,
    sa.Column("projection_name", sa.Text(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
    sa.Column("last_processed_event_id", sa.Uuid(), nullable=True),
    sa.Column("checkpoint_version", sa.BigInteger(), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

session_read_model_table = sa.Table(
    "session_read_model",
    metadata,
    sa.Column("session_id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("current_state", sa.Text(), nullable=False),
    sa.Column("projection_version", sa.BigInteger(), nullable=False),
    sa.Column("last_event_id", sa.Uuid(), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("last_aggregate_version", sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(
        ["session_id", "workspace_id"],
        ["sessions.id", "sessions.workspace_id"],
        name="fk_session_read_model_session_workspace",
        ondelete="RESTRICT",
    ),
)

inquiry_read_model_table = sa.Table(
    "inquiry_read_model",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("aggregate_ref", sa.Text(), nullable=False),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("projection_version", sa.BigInteger(), nullable=False),
    sa.Column("snapshot", postgresql.JSONB(), nullable=False),
    sa.Column("last_event_id", sa.Uuid(), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("last_aggregate_version", sa.BigInteger(), nullable=True),
    sa.UniqueConstraint(
        "aggregate_ref", "workspace_id", name="uq_inquiry_read_model_aggregate_workspace"
    ),
)

recovery_records_table = sa.Table(
    "recovery_records",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("failure_correlation_ref", sa.Uuid(), nullable=False),
    sa.Column("original_command_id", sa.Uuid(), nullable=False),
    sa.Column("original_attempt_id", sa.Uuid(), nullable=False),
    sa.Column("original_commit_id", sa.Uuid(), nullable=True),
    sa.Column("failure_classifications", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
    sa.Column("known_canonical_state_ref", sa.Text(), nullable=True),
    sa.Column("canonical_state_certainty", sa.Text(), nullable=False),
    sa.Column("known_external_consequence_ref", sa.Text(), nullable=True),
    sa.Column("external_consequence_certainty", sa.Text(), nullable=False),
    sa.Column("unknown_consequence_description", sa.Text(), nullable=True),
    sa.Column("last_proven_valid_state_ref", sa.Text(), nullable=True),
    sa.Column("recovery_class", sa.Text(), nullable=False),
    sa.Column("recovery_actor_type", sa.Text(), nullable=False),
    sa.Column("recovery_actor_id", sa.Text(), nullable=False),
    sa.Column("required_authority_ref", sa.Uuid(), nullable=True),
    sa.Column("current_authority_binding_ref", sa.Uuid(), nullable=True),
    sa.Column("human_decision_ref", sa.Uuid(), nullable=True),
    sa.Column("evidence_proof_refs", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
    sa.Column(
        "recovery_command_ids", postgresql.ARRAY(sa.Uuid()), nullable=False, server_default="{}"
    ),
    sa.Column("recovery_attempt_refs", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
    sa.Column("result", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("audit_linkage", sa.Text(), nullable=True),
    sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
    sa.Column(
        "blocked_target_refs", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"
    ),
    sa.ForeignKeyConstraint(
        ["original_command_id", "workspace_id"],
        ["commands.id", "commands.workspace_id"],
        name="fk_recovery_records_original_command_workspace",
        ondelete="RESTRICT",
    ),
    sa.ForeignKeyConstraint(
        ["original_commit_id", "workspace_id"],
        ["commit_units.id", "commit_units.workspace_id"],
        name="fk_recovery_records_original_commit_workspace",
        ondelete="RESTRICT",
    ),
    sa.CheckConstraint("record_version >= 1", name="ck_recovery_records_record_version_positive"),
)

security_events_table = sa.Table(
    "security_events",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    # Deliberately NO ForeignKey on workspace_id -- see
    # `packages/security/events.py`'s own "WHY workspace_id/command_id/
    # generation_id/recovery_id CARRY NO FOREIGN KEY" docstring section:
    # a SecurityEvent's own purpose can be to record a forged/unresolvable
    # claim, which a real FK would make impossible to ever persist.
    sa.Column("workspace_id", sa.Uuid(), nullable=True),
    sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("environment", sa.Text(), nullable=False),
    sa.Column("actor_type", sa.Text(), nullable=False),
    sa.Column("actor_id", sa.Text(), nullable=False),
    sa.Column("trust_boundary", sa.Text(), nullable=False),
    sa.Column("event_type", sa.Text(), nullable=False),
    sa.Column("correlation_id", sa.Uuid(), nullable=False),
    sa.Column("target_ref", sa.Text(), nullable=True),
    sa.Column("command_id", sa.Uuid(), nullable=True),
    sa.Column("generation_id", sa.Uuid(), nullable=True),
    sa.Column("recovery_id", sa.Uuid(), nullable=True),
    sa.Column("observed_facts", sa.Text(), nullable=True),
    sa.Column("uncertain", sa.Boolean(), nullable=False, server_default=sa.false()),
    sa.Column("containment_action", sa.Text(), nullable=True),
    sa.Column("audit_linkage", sa.Text(), nullable=True),
    sa.CheckConstraint(
        "environment IN ('DEVELOPMENT', 'TEST', 'STAGING', 'PRODUCTION')",
        name="ck_security_events_environment",
    ),
    sa.CheckConstraint(
        "trust_boundary IN ("
        "'TB-01','TB-02','TB-03','TB-04','TB-05','TB-06','TB-07','TB-08','TB-09','TB-10',"
        "'TB-11','TB-12','TB-13','TB-14','TB-15','TB-16','TB-17','TB-18','TB-19')",
        name="ck_security_events_trust_boundary",
    ),
)

session_participations_table = sa.Table(
    # F02 WU-02.8 (migration b3d8e5f0a2c7): 09 §28 SessionParticipation RELATION.
    "session_participations",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("session_id", sa.Uuid(), nullable=False),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
    sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column(
        "admitted_by_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(
        ["session_id", "workspace_id"],
        ["sessions.id", "sessions.workspace_id"],
        name="fk_session_participations_session_workspace",
        ondelete="RESTRICT",
    ),
)

local_auth_credentials_table = sa.Table(
    "local_auth_credentials",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    ),
    sa.Column("password_hash", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

local_auth_sessions_table = sa.Table(
    "local_auth_sessions",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
    sa.Column("session_token_hash", sa.Text(), nullable=False, unique=True),
    sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
)

__all__ = [
    "metadata",
    "users_table",
    "workspaces_table",
    "workspace_memberships_table",
    "role_assignments_table",
    "human_authority_bindings_table",
    "challenges_table",
    "sessions_table",
    "questions_table",
    "question_lineage_table",
    "question_bursts_table",
    "burst_question_memberships_table",
    "commands_table",
    "command_attempts_table",
    "idempotency_records_table",
    "audit_events_table",
    "outbox_events_table",
    "commit_units_table",
    "question_selections_table",
    "decisions_table",
    "source_references_table",
    "evidence_table",
    "claim_anchors_table",
    "evidence_relations_table",
    "evidence_set_references_table",
    "ai_generations_table",
    "ai_derived_artifacts_table",
    "ai_context_manifests_table",
    "projection_checkpoints_table",
    "session_read_model_table",
    "inquiry_read_model_table",
    "recovery_records_table",
    "security_events_table",
    "session_participations_table",
    "local_auth_credentials_table",
    "local_auth_sessions_table",
    "ai_operation_authorizations_table",
    "ai_validation_proofs_table",
    "question_clusters_table",
    "question_cluster_memberships_table",
]
