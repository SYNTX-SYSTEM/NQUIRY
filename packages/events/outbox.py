"""OutboxRecord and the transactional-outbox OutboxRepository port.

Source: 09_DATA_EVENT_API_CONTRACTS.md section 15 (Transactional Outbox
Contract -- the exact field list, section 15.1 the 3-value
`delivery_status` closed vocabulary, section 15.2 "At-Least-Once
Delivery"), section 122 (AC-09-010: "A message broker need not be
synchronously available for canonical commit if the required event is
durably stored in the transactional outbox"); 14_IMPLEMENTATION_SEQUENCE.md
section 3.1 (`events`'s exact "semantic_types"-only allow-list), section
7.1 (outbox_events table row: "commit writer, then outbox worker
delivery fields only" -- two disjoint field groups, one write owner
each), section 7.3 ("outbox_events.event_id is unique"), section 10
(OutboxRepository: "append in CommitUnit, delivery-state update by
worker").

WHY `outbox_id` IS A BARE `uuid.UUID`, NOT A NEW CLOSED SEMANTIC TYPE
--------------------------------------------------------------------
14 section 5's closed identity list does not name an "OutboxId" --
`EventId` (the *content* identity this row tracks delivery for) already
exists and is used for that. `outbox_id` (the *row's own* operational
identity, distinct from the event it describes -- 09 section 14 lists
them as two separate fields) has no assigned strong type of its own;
inventing one here would violate the closed list (14 section 5). Same
precedent as `CommandEnvelope.authority_context_ref`/
`Bnd005Input.scope_id`: a generic operational identifier with no
existing closed type uses a bare `uuid.UUID`.

WHY `event_payload_ref` IS OPTIONAL
--------------------------------------------------------------------
No `EventEnvelope`/event payload store exists yet (`packages/events/
envelope.py` is Phase 8, PKG-20's own scope -- 14 section 48's file-level
map). A reference to content that has nowhere to point yet is
legitimately absent, not a value this package can honestly fabricate.

WHY DELIVERY-TRACKING FIELDS ARE THE ONLY MUTABLE ONES
--------------------------------------------------------------------
14 section 7.1's own write-owner column for `outbox_events` --
"commit writer, then outbox worker delivery fields only" -- names two
disjoint field groups with two different legitimate writers. This
package cannot create the DB-principal separation itself (deferred to
migration `012_security_events_rls`, same disclosed gap as every prior
package), but the migration's own identity-immutability trigger locks
every field except `delivery_status`/`delivery_attempt_count`/
`next_attempt_at`/`delivered_at`, which is the field-level half of that
same write-owner split.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

from semantic_types.ids import CommitId, EventId, WorkspaceId


class DeliveryStatus(Enum):
    """09 section 15.1's exact 3-value closed vocabulary. "Delivery
    Status Is Not Domain State" -- none of these values affects whether
    the domain commit occurred.
    """

    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED_DELIVERY = "FAILED_DELIVERY"


@dataclass(frozen=True, slots=True)
class OutboxRecord:
    """09 section 15's exact field list, plus `workspace_id` (14
    section 7.1's own Workspace-keyed requirement for this table --
    a technical isolation column 09's minimal semantic list does not
    itemize but 14 structurally requires, the same disclosed addition
    PKG-11 made for `idempotency_records`).
    """

    outbox_id: uuid.UUID
    event_id: EventId
    workspace_id: WorkspaceId
    commit_id: CommitId
    event_type: str
    created_at: datetime
    delivery_status: DeliveryStatus
    delivery_attempt_count: int
    event_payload_ref: str | None = None
    next_attempt_at: datetime | None = None
    delivered_at: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.outbox_id, uuid.UUID):
            raise TypeError(f"outbox_id must be a uuid.UUID, got {type(self.outbox_id)!r}")
        if not isinstance(self.event_id, EventId):
            raise TypeError(f"event_id must be an EventId, got {type(self.event_id)!r}")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.commit_id, CommitId):
            raise TypeError(f"commit_id must be a CommitId, got {type(self.commit_id)!r}")
        if not self.event_type:
            raise ValueError("OutboxRecord.event_type must be non-empty")
        if not isinstance(self.delivery_status, DeliveryStatus):
            raise TypeError(
                f"delivery_status must be a DeliveryStatus, got {type(self.delivery_status)!r}"
            )
        if self.delivery_attempt_count < 0:
            raise ValueError("OutboxRecord.delivery_attempt_count must be >= 0")
        # 09 section 15: "delivered_at" only means something once
        # DELIVERED -- mirrors IdempotencyRecord's commit_id/COMMITTED
        # biconditional (PKG-11).
        if (self.delivery_status is DeliveryStatus.DELIVERED) != (self.delivered_at is not None):
            raise ValueError(
                "OutboxRecord.delivered_at must be set if and only if delivery_status is DELIVERED"
            )


@runtime_checkable
class OutboxRepository(Protocol):
    """14 section 10: "append in CommitUnit, delivery-state update by
    worker." No method here undoes or re-triggers the canonical
    mutation the record describes -- 09 section 122: broker/delivery
    failure "does not roll back already COMMITTED canonical state."
    """

    def append(self, record: OutboxRecord) -> None: ...

    def get(self, outbox_id: uuid.UUID) -> OutboxRecord | None: ...

    def mark_delivered(self, outbox_id: uuid.UUID, *, delivered_at: datetime) -> None: ...

    def mark_failed_delivery(self, outbox_id: uuid.UUID, *, next_attempt_at: datetime) -> None: ...


__all__ = ["DeliveryStatus", "OutboxRecord", "OutboxRepository"]
