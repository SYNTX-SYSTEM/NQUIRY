"""T2 TRANSITION TEST: migration 003's live PostgreSQL constraint proof.

13 §6 T2 scope: "State fixtures, Commands." Proves the database
enforces 03's topology *independently* of
`domain.session_transitions` -- the registry could be deleted entirely
and these constraints would still hold. Uses `NonProofWorkspaceBootstrap`
only to obtain a real Workspace/owner (13 §5's permitted downstream use:
"Tests built on those fixtures may prove downstream invariants if the
tested invariant does not depend on bootstrap legitimacy"); the
invariant under test here -- Session state topology -- does not depend
on how the Workspace came to exist.

Expect-failure assertions use `connection.begin_nested()` (SAVEPOINT):
PostgreSQL aborts the whole outer transaction after a raised error, and
this file's fixture-provided `db_connection` is itself one transaction
per test (rolled back at teardown), so each `pytest.raises` block that
expects a DB-level failure must be wrapped in its own SAVEPOINT to keep
the transaction usable afterward.

Context-manager order matters here and is easy to get backwards: it
must be `with pytest.raises(...), db_connection.begin_nested():`, not
the reverse. Exit order for a combined `with a, b:` is `b` then `a`; if
`begin_nested()` were listed first (outer) and `pytest.raises` second
(inner), `pytest.raises` would swallow the exception before
`begin_nested()`'s own `__exit__` ever saw it -- so `begin_nested()`
would issue `RELEASE SAVEPOINT` (its no-exception path) against a
connection PostgreSQL has already aborted at the wire level, itself
raising `InFailedSqlTransaction` instead of the SAVEPOINT being rolled
back. Listing `pytest.raises` first (outer) means `begin_nested()`
exits *while the exception is still propagating*, sees it, correctly
issues `ROLLBACK TO SAVEPOINT`, and re-raises -- only then does
`pytest.raises` catch it.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from domain.session import SessionState
from domain.session_transitions import SESSION_TRANSITION_SPECS, legal_state_pairs
from persistence.tables import challenges_table, sessions_table
from semantic_types.id_generator import SystemIdGenerator
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap_workspace(connection: sa.Connection, *, owner_email: str) -> sa.engine.Row:
    bootstrap = NonProofWorkspaceBootstrap(connection, FixedClock(_NOW), _ID_GEN)
    return bootstrap.seed(owner_email=owner_email)


def _insert_challenge(connection: sa.Connection, *, workspace_id) -> object:
    challenge_id = _ID_GEN.new_uuid()
    connection.execute(
        sa.insert(challenges_table).values(
            id=challenge_id,
            workspace_id=workspace_id,
            title="Onboarding drop-off",
            description=None,
            context=None,
            desired_outcome=None,
            constraints=None,
            stakeholders=None,
            created_at=_NOW,
            updated_at=_NOW,
            record_version=1,
        )
    )
    return challenge_id


def _insert_session(
    connection: sa.Connection,
    *,
    challenge_id,
    workspace_id,
    state: str = "DRAFT",
    record_version: int = 1,
) -> object:
    session_id = _ID_GEN.new_uuid()
    connection.execute(
        sa.insert(sessions_table).values(
            id=session_id,
            challenge_id=challenge_id,
            workspace_id=workspace_id,
            applied_method_key="QUESTION_BURST",
            applied_method_version="1.0",
            state=state,
            created_at=_NOW,
            updated_at=_NOW,
            closed_at=None,
            record_version=record_version,
        )
    )
    return session_id


def test_session_created_in_draft_succeeds(db_connection: sa.Connection) -> None:
    result = _bootstrap_workspace(db_connection, owner_email="draft-ok@nonproof.test")
    challenge_id = _insert_challenge(db_connection, workspace_id=result.workspace_id.value)

    session_id = _insert_session(
        db_connection, challenge_id=challenge_id, workspace_id=result.workspace_id.value
    )

    row = db_connection.execute(
        sa.select(sessions_table.c.state).where(sessions_table.c.id == session_id)
    ).scalar_one()
    assert row == "DRAFT"


def test_session_created_outside_draft_is_rejected(db_connection: sa.Connection) -> None:
    """`trg_sessions_enforce_initial_state`: 03 TRN-SESS-001 NEXT STATE
    is DRAFT and the machine's only entry point.
    """
    result = _bootstrap_workspace(db_connection, owner_email="draft-bad@nonproof.test")
    challenge_id = _insert_challenge(db_connection, workspace_id=result.workspace_id.value)

    with (
        pytest.raises(sa.exc.DBAPIError, match="must be created in DRAFT"),
        db_connection.begin_nested(),
    ):
        _insert_session(
            db_connection,
            challenge_id=challenge_id,
            workspace_id=result.workspace_id.value,
            state="SETUP",
        )


def test_direct_enum_coercion_is_rejected_by_the_check_constraint(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: direct enum coercion, proven a
    second time at the schema level -- a raw SQL client bypassing
    `domain.session.SessionState` entirely still cannot write an
    out-of-vocabulary state.
    """
    result = _bootstrap_workspace(db_connection, owner_email="coerce@nonproof.test")
    challenge_id = _insert_challenge(db_connection, workspace_id=result.workspace_id.value)

    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        _insert_session(
            db_connection,
            challenge_id=challenge_id,
            workspace_id=result.workspace_id.value,
            state="TOTALLY_DONE",
        )


def test_cross_workspace_session_target_is_not_representable(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: cross-Workspace target.

    A Session naming a Challenge from Workspace A but a `workspace_id`
    belonging to Workspace B must be structurally impossible: the
    composite foreign key `(challenge_id, workspace_id) -> challenges
    (id, workspace_id)` has no row to match, so PostgreSQL itself
    refuses the insert -- this is not merely "denied by application
    logic that could have a bug".
    """
    workspace_a = _bootstrap_workspace(db_connection, owner_email="cross-a@nonproof.test")
    workspace_b = _bootstrap_workspace(db_connection, owner_email="cross-b@nonproof.test")
    challenge_in_a = _insert_challenge(db_connection, workspace_id=workspace_a.workspace_id.value)

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        _insert_session(
            db_connection,
            challenge_id=challenge_in_a,
            workspace_id=workspace_b.workspace_id.value,
        )


def test_illegal_transition_is_rejected_by_the_transition_trigger(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: illegal transition, at the DB
    layer. DRAFT -> CHALLENGE_CAPTURE is 03 §16's first listed illegal
    pair.
    """
    result = _bootstrap_workspace(db_connection, owner_email="illegal@nonproof.test")
    challenge_id = _insert_challenge(db_connection, workspace_id=result.workspace_id.value)
    session_id = _insert_session(
        db_connection, challenge_id=challenge_id, workspace_id=result.workspace_id.value
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="illegal session transition"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(sessions_table)
            .where(sessions_table.c.id == session_id)
            .values(state="CHALLENGE_CAPTURE", record_version=2)
        )


def test_closed_session_cannot_transition_again(db_connection: sa.Connection) -> None:
    """Novel attack: CLOSED resurrection (AC-03-001). Walk a real
    Session to CLOSED, then attempt one further transition.
    """
    result = _bootstrap_workspace(db_connection, owner_email="resurrect@nonproof.test")
    challenge_id = _insert_challenge(db_connection, workspace_id=result.workspace_id.value)
    session_id = _insert_session(
        db_connection, challenge_id=challenge_id, workspace_id=result.workspace_id.value
    )

    version = 1
    ordered_states = [
        spec.to_state.value
        for spec in sorted(SESSION_TRANSITION_SPECS.values(), key=lambda s: s.transition_id.value)
    ]
    for target in ordered_states[1:]:  # skip DRAFT (already the initial state)
        version += 1
        db_connection.execute(
            sa.update(sessions_table)
            .where(sessions_table.c.id == session_id)
            .values(state=target, record_version=version)
        )

    final_state = db_connection.execute(
        sa.select(sessions_table.c.state).where(sessions_table.c.id == session_id)
    ).scalar_one()
    assert final_state == "CLOSED"

    with (
        pytest.raises(sa.exc.DBAPIError, match="illegal session transition"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(sessions_table)
            .where(sessions_table.c.id == session_id)
            .values(state="DRAFT", record_version=version + 1)
        )


def test_state_change_without_record_version_bump_is_rejected(
    db_connection: sa.Connection,
) -> None:
    """14 §26 optimistic concurrency: a state change must advance
    `record_version`. Otherwise a transition could commit while the
    expected-version compare-and-swap token stayed frozen, defeating
    concurrent-write detection for every subsequent Command.
    """
    result = _bootstrap_workspace(db_connection, owner_email="version@nonproof.test")
    challenge_id = _insert_challenge(db_connection, workspace_id=result.workspace_id.value)
    session_id = _insert_session(
        db_connection, challenge_id=challenge_id, workspace_id=result.workspace_id.value
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="must advance record_version"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(sessions_table)
            .where(sessions_table.c.id == session_id)
            .values(state="SETUP", record_version=1)
        )


def test_updating_a_row_without_changing_state_does_not_require_a_legal_pair(
    db_connection: sa.Connection,
) -> None:
    """Negative control: the transition trigger fires only when `state`
    actually changes (`NEW.state IS DISTINCT FROM OLD.state`) -- an
    unrelated column update (or a no-op state write) must not be
    mistaken for a transition attempt.
    """
    result = _bootstrap_workspace(db_connection, owner_email="noop@nonproof.test")
    challenge_id = _insert_challenge(db_connection, workspace_id=result.workspace_id.value)
    session_id = _insert_session(
        db_connection, challenge_id=challenge_id, workspace_id=result.workspace_id.value
    )

    db_connection.execute(
        sa.update(sessions_table)
        .where(sessions_table.c.id == session_id)
        .values(applied_method_key="QUESTION_BURST_V2")
    )

    row = db_connection.execute(
        sa.select(sessions_table.c.state, sessions_table.c.applied_method_key).where(
            sessions_table.c.id == session_id
        )
    ).one()
    assert row.state == "DRAFT"
    assert row.applied_method_key == "QUESTION_BURST_V2"


def test_registry_and_database_agree_on_every_legal_pair(db_connection: sa.Connection) -> None:
    """Cross-layer proof that `domain.session_transitions.legal_state_pairs()`
    and migration 003's trigger allow-list were not allowed to drift:
    every pair the registry calls state-eligible actually commits
    against the live database, walked as one continuous chain (each
    pair's target becomes the next pair's source, matching how a real
    Session would move through the machine).
    """
    result = _bootstrap_workspace(db_connection, owner_email="agree@nonproof.test")
    challenge_id = _insert_challenge(db_connection, workspace_id=result.workspace_id.value)
    session_id = _insert_session(
        db_connection, challenge_id=challenge_id, workspace_id=result.workspace_id.value
    )

    # The chain is linear (each state has exactly one legal successor,
    # per 03 §13.2), so it can be walked deterministically by following
    # successor links from DRAFT rather than by sorting -- an
    # alphabetical sort would not reproduce 03's order (e.g. "ACTION"
    # sorts before "DRAFT").
    successor_of = {source: target for source, target in legal_state_pairs() if source is not None}
    ordered_pairs = []
    current_source = SessionState.DRAFT
    while current_source in successor_of:
        target = successor_of[current_source]
        ordered_pairs.append((current_source, target))
        current_source = target
    assert len(ordered_pairs) == len(successor_of), "chain walk must visit every legal pair once"

    version = 1
    for source, target in ordered_pairs:
        current = db_connection.execute(
            sa.select(sessions_table.c.state).where(sessions_table.c.id == session_id)
        ).scalar_one()
        assert current == source.value
        version += 1
        db_connection.execute(
            sa.update(sessions_table)
            .where(sessions_table.c.id == session_id)
            .values(state=target.value, record_version=version)
        )

    final_state = db_connection.execute(
        sa.select(sessions_table.c.state).where(sessions_table.c.id == session_id)
    ).scalar_one()
    assert final_state == "CLOSED"
