"""F03 burst-membership law: ACTIVE-only capture, participation, order, one Burst

Revision ID: e5a1b3c8f204
Revises: c4e9a2b7d135
Create Date: 2026-09-24 00:00:03.000000

F03 WU-03.2 (FBR-F03-2, FBR-F03-6, EC-1 hardening). Persistence homes for
relations the architecture already states:

- `trg_burst_memberships_enforce_freeze` read the Burst state with a plain
  SELECT and refused only COMPLETED. A capture that passed its check while the
  Burst was ACTIVE could commit after a concurrent completion that computed its
  fingerprint without that row (06 BND-008 bypass "retry of late Question after
  COMPLETED"). It also accepted a PREPARED Burst, against TRN-Q-001 ("Burst
  ACTIVE"). It now locks the Burst row (FOR SHARE) and requires state ACTIVE on
  INSERT. The completion handler takes the row lock first (FOR NO KEY UPDATE), so
  the two are mutually exclusive.
- `trg_burst_memberships_enforce_capture_law` (BEFORE INSERT): 04 AUTH-DEP-Q-001
  "Valid SessionParticipation". The capture actor holds a CURRENT
  SessionParticipation in the Burst's Session; the Question is HUMAN-origin,
  authored by that actor, and belongs to the Session's own Challenge. The
  application re-resolves the same authority at commit (BND-014, PARTICIPATION);
  this is the defence at the persistence home.
- `uq_burst_memberships_burst_order`: `captured_order` is the ordinal position of
  a capture event within its Burst.
- `uq_question_bursts_session`: EC-1. 02 §13.4 "QuestionBurst -> exactly one
  Session" plus the strictly-forward 03 topology (a Session opens Question
  Generation at most once) make at most ONE Burst per Session, ever.
  `BurstRepository.get_by_session` relies on `one_or_none`. The former partial
  unique index (`state <> 'COMPLETED'`) would have accepted a new PREPARED row
  after COMPLETED.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e5a1b3c8f204"
down_revision = "c4e9a2b7d135"
branch_labels = None
depends_on = None

_FREEZE_NEW = """
CREATE OR REPLACE FUNCTION trg_burst_memberships_enforce_freeze() RETURNS trigger AS $$
DECLARE
    burst_state TEXT;
    target_burst_id UUID;
BEGIN
    IF TG_OP = 'DELETE' THEN
        target_burst_id := OLD.question_burst_id;
    ELSE
        target_burst_id := NEW.question_burst_id;
    END IF;
    SELECT state INTO burst_state FROM question_bursts WHERE id = target_burst_id FOR SHARE;
    IF burst_state = 'COMPLETED' THEN
        RAISE EXCEPTION
            'burst % is COMPLETED; raw membership is frozen (03 section 19.5, 06 section 14)',
            target_burst_id;
    END IF;
    IF TG_OP = 'INSERT' AND burst_state IS DISTINCT FROM 'ACTIVE' THEN
        RAISE EXCEPTION
            'burst % is % (not ACTIVE); capture requires an ACTIVE burst (03 TRN-Q-001)',
            target_burst_id, burst_state;
    END IF;
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

_FREEZE_OLD = """
CREATE OR REPLACE FUNCTION trg_burst_memberships_enforce_freeze() RETURNS trigger AS $$
DECLARE
    burst_state TEXT;
    target_burst_id UUID;
BEGIN
    IF TG_OP = 'DELETE' THEN
        target_burst_id := OLD.question_burst_id;
    ELSE
        target_burst_id := NEW.question_burst_id;
    END IF;
    SELECT state INTO burst_state FROM question_bursts WHERE id = target_burst_id;
    IF burst_state = 'COMPLETED' THEN
        RAISE EXCEPTION
            'burst % is COMPLETED; raw membership is frozen (03 section 19.5, 06 section 14)',
            target_burst_id;
    END IF;
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

_CAPTURE_LAW = """
CREATE FUNCTION trg_burst_memberships_enforce_capture_law() RETURNS trigger AS $$
DECLARE
    burst_session_id UUID;
    session_challenge_id UUID;
    q_origin TEXT;
    q_author UUID;
    q_challenge_id UUID;
BEGIN
    SELECT b.session_id, s.challenge_id
      INTO burst_session_id, session_challenge_id
      FROM question_bursts b
      JOIN sessions s ON s.id = b.session_id AND s.workspace_id = b.workspace_id
     WHERE b.id = NEW.question_burst_id;
    IF NOT EXISTS (
        SELECT 1 FROM session_participations sp
         WHERE sp.session_id = burst_session_id
           AND sp.workspace_id = NEW.workspace_id
           AND sp.user_id = NEW.capture_actor_user_id
           AND sp.left_at IS NULL
    ) THEN
        RAISE EXCEPTION
            'capture actor % has no current SessionParticipation in the burst''s Session (04 AUTH-DEP-Q-001)',
            NEW.capture_actor_user_id;
    END IF;
    SELECT origin, author_user_id, challenge_id
      INTO q_origin, q_author, q_challenge_id
      FROM questions WHERE id = NEW.question_id;
    IF q_origin IS DISTINCT FROM 'HUMAN' OR q_author IS DISTINCT FROM NEW.capture_actor_user_id THEN
        RAISE EXCEPTION
            'question % must be HUMAN-origin and authored by the capture actor (author %, actor %)',
            NEW.question_id, q_author, NEW.capture_actor_user_id;
    END IF;
    IF q_challenge_id IS DISTINCT FROM session_challenge_id THEN
        RAISE EXCEPTION
            'question % belongs to another Challenge than the burst''s Session', NEW.question_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    op.execute(_FREEZE_NEW)
    op.execute(_CAPTURE_LAW)
    op.execute(
        """
        CREATE TRIGGER trg_burst_memberships_enforce_capture_law
        BEFORE INSERT ON burst_question_memberships
        FOR EACH ROW EXECUTE FUNCTION trg_burst_memberships_enforce_capture_law();
        """
    )
    op.create_unique_constraint(
        "uq_burst_memberships_burst_order",
        "burst_question_memberships",
        ["question_burst_id", "captured_order"],
    )
    op.drop_index("uq_question_bursts_one_open_per_session", table_name="question_bursts")
    op.create_unique_constraint("uq_question_bursts_session", "question_bursts", ["session_id"])


def downgrade() -> None:
    op.drop_constraint("uq_question_bursts_session", "question_bursts", type_="unique")
    op.create_index(
        "uq_question_bursts_one_open_per_session",
        "question_bursts",
        ["session_id"],
        unique=True,
        postgresql_where=sa.text("state <> 'COMPLETED'"),
    )
    op.drop_constraint("uq_burst_memberships_burst_order", "burst_question_memberships", type_="unique")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_burst_memberships_enforce_capture_law ON burst_question_memberships"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_burst_memberships_enforce_capture_law()")
    op.execute(_FREEZE_OLD)
