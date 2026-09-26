"""Delivery composition for the projection pipeline (WU-PFC-F08-2, F08).

Source: 19_NQUIRY_IMPLEMENTATION_WITH_FRONTEND_RUNNING.md section 28 (TARGET
"exact EventEnvelope -> Worker -> Projection -> Replay/Rebuild");
12_MINIMUM_PROTOTYPE_ARCHITECTURE.md section 17 (COMMAND -> COMMIT -> DURABLE
OUTBOX -> EventEnvelope -> DELIVERY -> PROJECTION UPDATE, one committed event
path, in-process); 09_DATA_EVENT_API_CONTRACTS.md section 73.1 (a projection
consumer may update projection/read models only).

WHY THIS LIVES IN `projection`
--------------------------------------------------------------------
`nquiry_worker` may import `events`, `projection`, `recovery`, `command`,
`commit`, `observability` and `semantic_types` (14 section 3.1), but not
`persistence`. `projection` may import `events` and `persistence`. The
delivery ports (outbox, committed-event source, projection store) are
therefore assembled here. Composing ports is a projection-pipeline concern,
and this module holds no delivery policy.

`DeliveryPorts.isolated()` gives each event's projection write its own
SAVEPOINT. A failing projection store rolls back that one event's projection
change and is reported as the typed `ProjectionStoreFailure`, never as a
catch-all.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import sqlalchemy as sa
from persistence.committed_event_repository import (
    CommittedEventEnvelopeSource,
    SqlAlchemyAggregateOrderedOutbox,
    SqlAlchemyCommittedEventRepository,
)
from persistence.engine import connect
from persistence.projection_repository import SqlAlchemyProjectionRepository

from projection.consumer import ProjectionConsumer


class ProjectionStoreFailure(Exception):
    """One event's projection write could not be stored. Its SAVEPOINT was
    rolled back, and delivery reports the event as not delivered."""


class DeliveryPorts:
    """Everything one delivery pass needs, bound to ONE connection and
    transaction: the outbox (aggregate-ordered due selection), the committed
    Event source, the committed history (replay), and the projection store
    and consumer."""

    def __init__(self, connection: sa.Connection) -> None:
        self.connection = connection
        self.outbox = SqlAlchemyAggregateOrderedOutbox(connection)
        self.envelope_source = CommittedEventEnvelopeSource(connection)
        self.history = SqlAlchemyCommittedEventRepository(connection)
        self.projection = SqlAlchemyProjectionRepository(connection)
        self.consumer = ProjectionConsumer(repository=self.projection)

    @contextmanager
    def isolated(self) -> Iterator[None]:
        try:
            with self.connection.begin_nested():
                yield
        except sa.exc.SQLAlchemyError as exc:
            raise ProjectionStoreFailure(f"{type(exc).__name__}: {exc}") from exc


@contextmanager
def open_delivery() -> Iterator[DeliveryPorts]:
    """One real delivery pass: one connection, one transaction, committed on
    clean exit (`persistence.engine.connect`, fails closed without
    DATABASE_URL). A crash before commit leaves every record undelivered, so
    the next pass redelivers them (at-least-once)."""
    with connect() as connection:
        yield DeliveryPorts(connection)


__all__ = ["DeliveryPorts", "ProjectionStoreFailure", "open_delivery"]
