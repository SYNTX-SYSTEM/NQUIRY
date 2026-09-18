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
"""

from __future__ import annotations

import sqlalchemy as sa

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
    # No ForeignKey: `ai_generations` (14 §9 migration 007_ai_operational)
    # does not exist yet. Plain nullable reference, same disclosed
    # limitation as `human_authority_bindings.scope_id` (PKG-02).
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
]
