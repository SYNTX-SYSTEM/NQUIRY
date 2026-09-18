"""events: EventEnvelope and outbox contracts.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : EventEnvelope and outbox contracts.
    May depend on      : semantic_types.
    Must not depend on : command mutation internals.
    Canonical write    : outbox only.

PKG-12 SCOPE (Build Phase 4, "Audit and outbox contracts"):
    outbox.py -- DeliveryStatus (09 section 15.1's exact 3-value closed
                 vocabulary), OutboxRecord (09 section 15's exact field
                 list), OutboxRepository (the transactional-outbox port).

`envelope.py` (EventEnvelope) remains PKG-20's scope (Phase 8, 14
section 48's file-level map) -- nothing here constructs or references a
concrete domain Event, only the durable delivery-tracking record for
one once it exists. `packages/persistence/outbox_repository.py`
implements the durable storage for `OutboxRepository`, the same
one-directional dependency pattern already established for `command`/
`domain`/`governance`.
"""
