"""T9 SECURITY TEST: SecurityEvent and SqlAlchemySecurityEventRepository,
against real PostgreSQL.

14 section 46's own repository-topology row assigns
`tests/security/test_events.py` to `packages/security/events.py`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from persistence.security_event_repository import SqlAlchemySecurityEventRepository
from persistence.tables import security_events_table
from security.events import Environment, SecurityEvent, SecurityEventRepository, TrustBoundary
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, SecurityEventId, WorkspaceId
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _event(**overrides: object) -> SecurityEvent:
    base: dict[str, object] = dict(
        security_event_id=SecurityEventId(uuid.uuid4()),
        occurred_at=_NOW,
        environment=Environment.TEST,
        actor_type="SYSTEM_SERVICE",
        actor_id="api-reader-1",
        trust_boundary=TrustBoundary.TB_07_CANONICAL_PERSISTENCE,
        event_type="direct_canonical_write_attempt",
        correlation_id=CorrelationId(uuid.uuid4()),
    )
    base.update(overrides)
    return SecurityEvent(**base)  # type: ignore[arg-type]


def test_security_event_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        _event(occurred_at=datetime(2030, 1, 1))


def test_security_event_rejects_empty_actor_fields() -> None:
    with pytest.raises(ValueError, match="actor_type"):
        _event(actor_type="")
    with pytest.raises(ValueError, match="actor_id"):
        _event(actor_id="")


def test_security_event_rejects_empty_event_type() -> None:
    with pytest.raises(ValueError, match="event_type"):
        _event(event_type="")


def test_security_event_repository_protocol_has_no_update_or_delete_method() -> None:
    """Structural non-collapse proof: "SecurityEvent tamper/rewrite" has
    no method to even attempt through this Protocol."""
    method_names = {name for name in dir(SecurityEventRepository) if not name.startswith("_")}
    assert method_names == {"record", "get", "list_for_correlation"}


def test_record_then_get_round_trip(db_connection: sa.Connection) -> None:
    repo: SecurityEventRepository = SqlAlchemySecurityEventRepository(db_connection)
    event = _event(
        workspace_id=None,
        target_ref="session:1",
        observed_facts="raw INSERT attempted against decisions as api_reader",
        uncertain=False,
        containment_action=None,
        audit_linkage=None,
    )

    repo.record(event)

    assert repo.get(event.security_event_id) == event


def test_record_with_a_forged_unresolvable_workspace_id_succeeds(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: "forged role"/"cross-Workspace
    at every layer" -- a SecurityEvent about a claim against a
    Workspace that does NOT exist must still be recordable (see
    `security.events`'s own "WHY workspace_id ... CARRY NO FOREIGN KEY"
    docstring section) -- the whole point is capturing the forged claim
    itself, not validating it."""
    repo: SecurityEventRepository = SqlAlchemySecurityEventRepository(db_connection)
    forged_workspace_id = WorkspaceId(uuid.uuid4())  # never seeded, does not exist
    event = _event(
        workspace_id=forged_workspace_id,
        event_type="cross_workspace_attempt",
        uncertain=True,
    )

    repo.record(event)

    stored = repo.get(event.security_event_id)
    assert stored is not None
    assert stored.workspace_id == forged_workspace_id
    assert stored.uncertain is True


def test_record_with_a_real_workspace_id_round_trips(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    workspace_id = bootstrap.seed(owner_email="secevent-real-ws@nonproof.test").workspace_id
    repo: SecurityEventRepository = SqlAlchemySecurityEventRepository(db_connection)
    event = _event(workspace_id=workspace_id, event_type="authentication_failure")

    repo.record(event)

    stored = repo.get(event.security_event_id)
    assert stored is not None
    assert stored.workspace_id == workspace_id


def test_list_for_correlation_orders_by_occurred_at(db_connection: sa.Connection) -> None:
    repo: SecurityEventRepository = SqlAlchemySecurityEventRepository(db_connection)
    correlation_id = CorrelationId(uuid.uuid4())
    later = datetime(2030, 1, 1, 0, 5, tzinfo=timezone.utc)
    earlier_event = _event(correlation_id=correlation_id, occurred_at=_NOW, event_type="attempt_1")
    later_event = _event(correlation_id=correlation_id, occurred_at=later, event_type="attempt_2")
    repo.record(later_event)
    repo.record(earlier_event)

    events = repo.list_for_correlation(correlation_id)

    assert [e.event_type for e in events] == ["attempt_1", "attempt_2"]


def test_db_trigger_rejects_update(db_connection: sa.Connection) -> None:
    """Defense-in-depth: even a caller bypassing `SecurityEventRepository`
    entirely (raw SQL) cannot rewrite an established SecurityEvent."""
    repo: SecurityEventRepository = SqlAlchemySecurityEventRepository(db_connection)
    event = _event()
    repo.record(event)

    with (
        pytest.raises(sa.exc.DBAPIError, match="append-only"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(security_events_table)
            .where(security_events_table.c.id == event.security_event_id.value)
            .values(event_type="tampered")
        )


def test_db_trigger_rejects_delete(db_connection: sa.Connection) -> None:
    repo: SecurityEventRepository = SqlAlchemySecurityEventRepository(db_connection)
    event = _event()
    repo.record(event)

    with (
        pytest.raises(sa.exc.DBAPIError, match="cannot be deleted"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.delete(security_events_table).where(
                security_events_table.c.id == event.security_event_id.value
            )
        )


def test_db_check_constraint_rejects_an_unknown_environment(db_connection: sa.Connection) -> None:
    with (
        pytest.raises(sa.exc.DBAPIError, match="ck_security_events_environment"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.insert(security_events_table).values(
                id=uuid.uuid4(),
                occurred_at=_NOW,
                environment="LOCAL_LAPTOP",
                actor_type="SYSTEM_SERVICE",
                actor_id="probe",
                trust_boundary="TB-04",
                event_type="probe",
                correlation_id=uuid.uuid4(),
            )
        )


def test_db_check_constraint_rejects_an_unknown_trust_boundary(
    db_connection: sa.Connection,
) -> None:
    with (
        pytest.raises(sa.exc.DBAPIError, match="ck_security_events_trust_boundary"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.insert(security_events_table).values(
                id=uuid.uuid4(),
                occurred_at=_NOW,
                environment="TEST",
                actor_type="SYSTEM_SERVICE",
                actor_id="probe",
                trust_boundary="TB-99",
                event_type="probe",
                correlation_id=uuid.uuid4(),
            )
        )
