"""challenge session

Revision ID: d467112ce46d
Revises: 01a37c093cd6
Create Date: 2026-09-17 20:05:00.000000

PKG-05 scope (14_IMPLEMENTATION_SEQUENCE.md §9: "003_challenge_session
| creates: challenges, sessions | depends on: 001,002 | gate: transition
constraints"). That gate is the reason this migration carries real
enforcement rather than only column definitions: 03's transition
topology has to hold at the database, independently of any application
code, or "ILLEGAL TRANSITION MUST NOT BE ENABLED BY GENERIC SETTER"
would rest entirely on `packages/domain` being the only writer -- which
no schema can guarantee.

Tables created:

- `challenges` (02 §9, 09 §25): the canonical inquiry frame.
  `workspace_id` is a direct FK, which 09 §25.1 explicitly permits
  ("preserves, rather than duplicates ambiguously, that ownership
  relation"). The extra `UNIQUE (id, workspace_id)` exists solely as
  the anchor for `sessions`' composite FK below -- it is redundant with
  the primary key on its own.

  Deliberately NOT created: `status`. LEVEL 1 names `Challenge.status`
  but defines no values; 03 §12.1 refuses to invent one; GAP-02-012 /
  GAP-03-013 (16: NQ-GAP-018) remain OPEN; and 03 §12.2 forbids using
  it as transition guard, authority predicate, boundary predicate or
  prototype acceptance condition -- every use this prototype has.
  09 §25.2 leaves materialization to implementation, so omitting it is
  permitted and is the fail-closed choice. Re-adding it once a real
  vocabulary exists is additive.

  Also deliberately NOT created: any `emotional_temperature` column.
  02 §10.5 leaves its technical role (initial reading / latest-reading
  projection / compatibility field / denormalized value) unresolved and
  delegates to 09; 09 §25 does not resolve it. Picking one would be
  invention. 02 §10 models the real thing as a separate
  `EmotionalTemperatureReading` VALUE_RECORD, and 14 §9 assigns no such
  table to this migration.

- `sessions` (02 §11, 09 §27): the canonical process object owning the
  13-state inquiry machine.

  `workspace_id` is the denormalization 09 §27.1 permits "only if
  constrained to equal Challenge Workspace... It cannot become an
  alternate ownership source." The constraint is the composite foreign
  key `(challenge_id, workspace_id) -> challenges (id, workspace_id)`:
  a Session whose Workspace disagrees with its Challenge's is not
  representable at all. This is declarative, not a trigger, so it
  cannot be disabled per-session or bypassed by a direct write.

  `state` is CHECK-constrained to exactly the 13 values of 03 §13.1 --
  the same closed vocabulary as `domain.session.SessionState`, enforced
  a second time where raw SQL could otherwise coerce an arbitrary
  string.

Triggers (14 §7.3: "application plus trigger/constraint enforcement
where SQL cannot express a cross-table invariant directly"; here the
inexpressible part is a *relation between old and new row values*):

1. `trg_sessions_enforce_initial_state` (BEFORE INSERT): a new Session
   must be DRAFT. 03 TRN-SESS-001 CREATE_SESSION, NEXT STATE: `DRAFT`
   is the machine's only entry point, so a caller-chosen target state
   cannot be smuggled in at creation time.

2. `trg_sessions_enforce_transition` (BEFORE UPDATE): if `state`
   changes, the `(OLD.state, NEW.state)` pair must appear in 03 §13.2's
   chain. Everything else is rejected, which covers all of 03 §16's
   illegal set, 03 §16's general rule ("Skipping a named source state
   is denied by default"), and -- because CLOSED appears as no pair's
   source -- 03 §13.3 / AC-03-001 (a CLOSED Session never reopens; a
   new inquiry cycle creates a new Session under the same Challenge).
   The same trigger requires `record_version` to advance on a state
   change, so a transition cannot be committed while leaving the
   optimistic-concurrency token untouched (14 §26).

The legal pair list below is transcribed from 03 §13.2 and is asserted
against `domain.session_transitions.legal_state_pairs()` by
`tests/transitions/test_session_transition_constraints.py`, so the two
enforcement layers cannot silently drift apart.

No cascading delete anywhere (14 §49 default). Schema downgrade is
infrastructure rollback only, not domain rollback (14 §9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d467112ce46d"
down_revision: str | None = "01a37c093cd6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 03 §13.1, in 03 §13.2's order.
_SESSION_STATES = (
    "DRAFT",
    "SETUP",
    "CHALLENGE_CAPTURE",
    "QUESTION_GENERATION",
    "QUESTION_CAPTURE",
    "ANALYSIS",
    "REFLECTION",
    "QUESTION_SELECTION",
    "INVESTIGATION",
    "EXPERIMENT",
    "ACTION",
    "REVIEW",
    "CLOSED",
)

# 03 §13.2's chain, as (from, to) pairs. CLOSED is absent as a source:
# it is terminal (03 §13.3, AC-03-001).
_LEGAL_TRANSITIONS = tuple(zip(_SESSION_STATES, _SESSION_STATES[1:], strict=False))

_LEGAL_TRANSITIONS_SQL = ", ".join(
    f"('{source}', '{target}')" for source, target in _LEGAL_TRANSITIONS
)


def upgrade() -> None:
    op.create_table(
        "challenges",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("desired_outcome", sa.Text(), nullable=True),
        sa.Column("constraints", sa.Text(), nullable=True),
        sa.Column("stakeholders", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id", name="pk_challenges"),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name="fk_challenges_workspace", ondelete="RESTRICT"
        ),
        # Anchor for sessions' composite FK. Redundant with the PK on
        # its own; it exists so the Workspace equality below can be
        # expressed declaratively.
        sa.UniqueConstraint("id", "workspace_id", name="uq_challenges_id_workspace"),
        sa.CheckConstraint("length(title) > 0", name="ck_challenges_title_not_empty"),
        sa.CheckConstraint("record_version >= 1", name="ck_challenges_record_version_positive"),
    )
    op.create_index("ix_challenges_workspace", "challenges", ["workspace_id"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("challenge_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("applied_method_key", sa.Text(), nullable=False),
        sa.Column("applied_method_version", sa.Text(), nullable=False),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id", name="pk_sessions"),
        # 09 §27.1: the denormalized workspace_id is permitted "only if
        # constrained to equal Challenge Workspace". This composite FK
        # is that constraint.
        sa.ForeignKeyConstraint(
            ["challenge_id", "workspace_id"],
            ["challenges.id", "challenges.workspace_id"],
            name="fk_sessions_challenge_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name="fk_sessions_workspace", ondelete="RESTRICT"
        ),
        sa.CheckConstraint(
            "state IN (" + ", ".join(f"'{s}'" for s in _SESSION_STATES) + ")",
            name="ck_sessions_state",
        ),
        # 03 TRN-SESS-013: "CLOSED must not be used to hide unresolved
        # failure." A closure timestamp may only exist on a Session that
        # actually reached the terminal state.
        sa.CheckConstraint(
            "closed_at IS NULL OR state = 'CLOSED'", name="ck_sessions_closed_at_requires_closed"
        ),
        sa.CheckConstraint(
            "length(applied_method_key) > 0", name="ck_sessions_applied_method_key_not_empty"
        ),
        sa.CheckConstraint("record_version >= 1", name="ck_sessions_record_version_positive"),
    )
    op.create_index("ix_sessions_challenge", "sessions", ["challenge_id"])
    op.create_index("ix_sessions_workspace", "sessions", ["workspace_id"])

    # Trigger 1: 03 TRN-SESS-001 NEXT STATE: DRAFT. The state machine
    # has exactly one entry point; an INSERT naming any other state is
    # a caller-supplied target state, not a transition.
    op.execute(
        """
        CREATE FUNCTION trg_sessions_enforce_initial_state() RETURNS trigger AS $$
        BEGIN
            IF NEW.state <> 'DRAFT' THEN
                RAISE EXCEPTION
                    'session must be created in DRAFT (03 TRN-SESS-001), got %',
                    NEW.state;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_sessions_enforce_initial_state
        BEFORE INSERT ON sessions
        FOR EACH ROW EXECUTE FUNCTION trg_sessions_enforce_initial_state();
        """
    )

    # Trigger 2: 03 §13.2 topology + §16 illegal set + §13.3 terminal
    # CLOSED. Expressed as an explicit pair allow-list so that the
    # database, like `domain.session_transitions`, is default-DENY.
    op.execute(
        f"""
        CREATE FUNCTION trg_sessions_enforce_transition() RETURNS trigger AS $$
        BEGIN
            IF NEW.state IS DISTINCT FROM OLD.state THEN
                IF NOT ((OLD.state, NEW.state) IN ({_LEGAL_TRANSITIONS_SQL})) THEN
                    RAISE EXCEPTION
                        'illegal session transition % -> % (03 section 13.2/16)',
                        OLD.state, NEW.state;
                END IF;
                IF NEW.record_version <= OLD.record_version THEN
                    RAISE EXCEPTION
                        'session state change must advance record_version (14 section 26), % -> %',
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
        CREATE TRIGGER trg_sessions_enforce_transition
        BEFORE UPDATE ON sessions
        FOR EACH ROW EXECUTE FUNCTION trg_sessions_enforce_transition();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_sessions_enforce_transition ON sessions;")
    op.execute("DROP FUNCTION IF EXISTS trg_sessions_enforce_transition();")
    op.execute("DROP TRIGGER IF EXISTS trg_sessions_enforce_initial_state ON sessions;")
    op.execute("DROP FUNCTION IF EXISTS trg_sessions_enforce_initial_state();")
    op.drop_index("ix_sessions_workspace", table_name="sessions")
    op.drop_index("ix_sessions_challenge", table_name="sessions")
    op.drop_table("sessions")
    op.drop_index("ix_challenges_workspace", table_name="challenges")
    op.drop_table("challenges")
