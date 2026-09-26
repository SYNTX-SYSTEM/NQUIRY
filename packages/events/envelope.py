"""EventEnvelope, EventPublisher and EventConsumer contracts.

Source: 09_DATA_EVENT_API_CONTRACTS.md section 16 (EventEnvelope -- the
exact 14-field list, section 16.1 "Event Means: a committed occurrence
was recorded", section 16.2 "Event Does Not Mean: execute again /
authorize another command / grant authority / prove domain truth"),
section 15.2 (At-Least-Once Delivery -- "consumers must assume
duplicate event delivery is possible ... must not produce duplicate
consequential effects solely because delivery repeats"), section 17
(AC-09-003: "A domain/audit event ... is emitted only from a COMMITTED
CommitUnit"), section 126 (AC-09-011: "serialization validation is
pre-semantic only"); 14_IMPLEMENTATION_SEQUENCE.md section 3.1
(`events`'s exact "semantic_types"-only allow-list), section 28
("EventEnvelope is created from committed fact and includes event_id,
schema version, Workspace, aggregate/version, command_id, commit_id,
correlation_id, causation_id, actor/service and authority source
references"), section 41 ("event consumer cannot import direct
consequential handler").

WHY EventPublisher/EventConsumer LIVE HERE, NOT A SEPARATE FILE
--------------------------------------------------------------------
14's own PKG-20 manifest names "EventPublisher/consumer contracts" as
this package's PUBLIC_INTERFACES with no dedicated file row in 14
section 48's file-level map (only `envelope.py`/`outbox.py` are named
for `packages/events`) -- both contracts are intimately tied to the
one type (`EventEnvelope`) they carry, so they are co-located with it
rather than invented into a new, unnamed file.

WHY `aggregate_version_after_commit` REUSES `RecordVersion`, NOT A NEW TYPE
--------------------------------------------------------------------
14 section 5.4's closed version-type list already names `record_version`
as the generic optimistic-concurrency counter every canonical row
carries -- "the version this aggregate reached once this commit was
applied" is exactly that value, not a new semantic concept.

WHY THIS PACKAGE DOES NOT ITSELF RECONSTRUCT A HISTORICAL EventEnvelope
FROM A BARE `commit_id`
--------------------------------------------------------------------
An `OutboxRecord` (PKG-12/18) durably proves *that* a fact was
committed and *which* CommitUnit produced it, but by itself carries
none of `aggregate_ref`, `aggregate_version_after_commit`,
`correlation_id`, `causation_id`, `actor_ref`, `authority_source_ref`
or `payload` -- 09 section 15's own OutboxRecord field list is
deliberately minimal (delivery bookkeeping only). The durable
`AuditEvent` row `CommitCoordinator` (PKG-13) writes atomically
alongside every `OutboxRecord` DOES carry most of these
(`correlation_id`, `causation_id`, `actor_type`/`actor_id`,
`authority_source_ref`, `command_id`, `commit_id`, `event_type`,
`event_schema_version`, `occurred_at`) -- but `events`'s own 14 section
3.1 allow-list is `semantic_types` only, so this package cannot import
`audit` to perform that join itself without a new, undisclosed
architecture-dependency extension this package's own scope does not
authorize. `aggregate_ref`/`aggregate_version_after_commit`/`payload`
also have no durable source at all yet (no generic "current version of
an arbitrary target_ref" read port exists -- the same class of gap
`evidence.freshness`'s own `current_target_versions` caller-supplied
mapping already disclosed at PKG-17). Building a full, historically
faithful assembler is therefore `SUCCESSOR_NOT_BUILT`, not this
package's job to fabricate around: `apps/worker/src/nquiry_worker/
outbox_worker.py`'s own `EventEnvelopeSource` injection point is where
a future package would supply this join. This package proves the
`EventEnvelope` contract itself (construction, validation, versioned
serialization) and the delivery/idempotency mechanics around it, using
explicit, caller-supplied field values -- never reconstructing from a
real production commit.

SUCCESSOR TRUTH (WU-PFC-F08-1): the historically faithful basis now exists.
Every CommitUnit writes one immutable `committed_events` row whose fields are
exactly this envelope (contracts in `events.contracts`), and
`persistence.committed_event_repository.CommittedEventEnvelopeSource`
reconstructs the envelope from that row alone. This package itself is
unchanged.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from semantic_types.ids import (
    CausationId,
    CommandId,
    CommitId,
    CorrelationId,
    EventId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """09 section 16's exact field list."""

    event_id: EventId
    event_type: str
    event_schema_version: ContractVersion
    occurred_at: datetime
    workspace_scope_ref: WorkspaceId
    aggregate_ref: str
    aggregate_version_after_commit: RecordVersion
    command_id: CommandId
    commit_id: CommitId
    correlation_id: CorrelationId
    actor_ref: str
    authority_source_ref: uuid.UUID
    payload: object
    causation_id: CausationId | None = None

    def __post_init__(self) -> None:
        # Mandatory adversarial attack (P-16, Command != Event): a
        # CommandId/AttemptId/other strong identity structurally cannot
        # masquerade as this Event's own identity -- mirrors
        # `CommandEnvelope.__post_init__`'s identical defense (PKG-10).
        if not isinstance(self.event_id, EventId):
            raise TypeError(f"event_id must be an EventId, got {type(self.event_id)!r}")
        if not self.event_type:
            raise ValueError("EventEnvelope.event_type must be non-empty")
        if not isinstance(self.event_schema_version, ContractVersion):
            raise TypeError(
                "event_schema_version must be a ContractVersion, got "
                f"{type(self.event_schema_version)!r}"
            )
        if not isinstance(self.workspace_scope_ref, WorkspaceId):
            raise TypeError(
                f"workspace_scope_ref must be a WorkspaceId, got {type(self.workspace_scope_ref)!r}"
            )
        if not self.aggregate_ref:
            raise ValueError("EventEnvelope.aggregate_ref must be non-empty")
        if not isinstance(self.aggregate_version_after_commit, RecordVersion):
            raise TypeError(
                "aggregate_version_after_commit must be a RecordVersion, got "
                f"{type(self.aggregate_version_after_commit)!r}"
            )
        if not isinstance(self.command_id, CommandId):
            raise TypeError(f"command_id must be a CommandId, got {type(self.command_id)!r}")
        if not isinstance(self.commit_id, CommitId):
            raise TypeError(f"commit_id must be a CommitId, got {type(self.commit_id)!r}")
        if not isinstance(self.correlation_id, CorrelationId):
            raise TypeError(
                f"correlation_id must be a CorrelationId, got {type(self.correlation_id)!r}"
            )
        if self.causation_id is not None and not isinstance(self.causation_id, CausationId):
            raise TypeError(
                f"causation_id must be a CausationId or None, got {type(self.causation_id)!r}"
            )
        if not self.actor_ref:
            raise ValueError("EventEnvelope.actor_ref must be non-empty")
        if not isinstance(self.authority_source_ref, uuid.UUID):
            raise TypeError(
                f"authority_source_ref must be a uuid.UUID, got {type(self.authority_source_ref)!r}"
            )


def build_event_envelope(
    *,
    event_id: EventId,
    event_type: str,
    event_schema_version: ContractVersion,
    occurred_at: datetime,
    workspace_scope_ref: WorkspaceId,
    aggregate_ref: str,
    aggregate_version_after_commit: RecordVersion,
    command_id: CommandId,
    commit_id: CommitId,
    correlation_id: CorrelationId,
    actor_ref: str,
    authority_source_ref: uuid.UUID,
    payload: object,
    causation_id: CausationId | None = None,
) -> EventEnvelope:
    """Pure constructor -- no I/O, mirrors `ai_gateway.context.
    build_context_manifest`'s own precedent. Every field is an explicit
    caller-supplied value; nothing is guessed or derived from a partial
    record.
    """

    return EventEnvelope(
        event_id=event_id,
        event_type=event_type,
        event_schema_version=event_schema_version,
        occurred_at=occurred_at,
        workspace_scope_ref=workspace_scope_ref,
        aggregate_ref=aggregate_ref,
        aggregate_version_after_commit=aggregate_version_after_commit,
        command_id=command_id,
        commit_id=commit_id,
        correlation_id=correlation_id,
        actor_ref=actor_ref,
        authority_source_ref=authority_source_ref,
        payload=payload,
        causation_id=causation_id,
    )


class EventEnvelopeSerializationError(Exception):
    """Raised by `event_envelope_from_json` for a structurally invalid
    or unsupported-schema-version payload -- 09 section 126 (AC-09-011):
    serialization validation is pre-semantic only, never itself an
    authority/boundary decision.
    """


def event_envelope_to_json(envelope: EventEnvelope) -> str:
    """Versioned wire serialization. `payload` must itself be
    JSON-serializable -- the same constraint `AIValidationProof`'s own
    `raw_content` JSON round-trip already assumes (PKG-18/19).
    """

    return json.dumps(
        {
            "event_id": str(envelope.event_id.value),
            "event_type": envelope.event_type,
            "event_schema_version": envelope.event_schema_version.value,
            "occurred_at": envelope.occurred_at.isoformat(),
            "workspace_scope_ref": str(envelope.workspace_scope_ref.value),
            "aggregate_ref": envelope.aggregate_ref,
            "aggregate_version_after_commit": envelope.aggregate_version_after_commit.value,
            "command_id": str(envelope.command_id.value),
            "commit_id": str(envelope.commit_id.value),
            "correlation_id": str(envelope.correlation_id.value),
            "causation_id": (
                str(envelope.causation_id.value) if envelope.causation_id is not None else None
            ),
            "actor_ref": envelope.actor_ref,
            "authority_source_ref": str(envelope.authority_source_ref),
            "payload": envelope.payload,
        }
    )


def event_envelope_from_json(
    raw: str, *, supported_schema_version: ContractVersion
) -> EventEnvelope:
    """Deserializes and re-validates a wire payload. Rejects a schema
    version this reader was not built to understand rather than
    guessing forward/backward compatibility (09 section 126).
    """

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EventEnvelopeSerializationError(f"malformed EventEnvelope JSON: {exc}") from exc

    try:
        schema_version = ContractVersion(data["event_schema_version"])
        if schema_version != supported_schema_version:
            raise EventEnvelopeSerializationError(
                f"unsupported event_schema_version {schema_version.value!r}, "
                f"expected {supported_schema_version.value!r}"
            )
        return build_event_envelope(
            event_id=EventId(uuid.UUID(data["event_id"])),
            event_type=data["event_type"],
            event_schema_version=schema_version,
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            workspace_scope_ref=WorkspaceId(uuid.UUID(data["workspace_scope_ref"])),
            aggregate_ref=data["aggregate_ref"],
            aggregate_version_after_commit=RecordVersion(data["aggregate_version_after_commit"]),
            command_id=CommandId(uuid.UUID(data["command_id"])),
            commit_id=CommitId(uuid.UUID(data["commit_id"])),
            correlation_id=CorrelationId(uuid.UUID(data["correlation_id"])),
            causation_id=(
                CausationId(uuid.UUID(data["causation_id"]))
                if data.get("causation_id") is not None
                else None
            ),
            actor_ref=data["actor_ref"],
            authority_source_ref=uuid.UUID(data["authority_source_ref"]),
            payload=data["payload"],
        )
    except EventEnvelopeSerializationError:
        raise
    except (KeyError, ValueError, TypeError) as exc:
        raise EventEnvelopeSerializationError(f"malformed EventEnvelope payload: {exc}") from exc


@runtime_checkable
class EventPublisher(Protocol):
    """14's own PKG-20 PUBLIC_INTERFACES: "EventPublisher ... contracts."
    A publish failure must raise, never return a boolean -- mirrors
    `MockProviderAdapter.invoke`'s own exception-not-boolean precedent
    (PKG-19), so a worker cannot silently misinterpret a failed publish
    as delivered.
    """

    def publish(self, envelope: EventEnvelope) -> None: ...


@runtime_checkable
class EventConsumer(Protocol):
    """14's own PKG-20 PUBLIC_INTERFACES: "... consumer contracts." 09
    section 15.2's own obligation is on the CONSUMER, not the
    publisher/worker: "must not produce duplicate consequential effects
    solely because delivery repeats." `handle` returns nothing and
    receives only the already-committed fact -- there is no return
    path back into a Command/CommitUnit, structurally matching 14
    section 41's "event consumer cannot import direct consequential
    handler."
    """

    def handle(self, envelope: EventEnvelope) -> None: ...


__all__ = [
    "EventEnvelope",
    "EventEnvelopeSerializationError",
    "EventPublisher",
    "EventConsumer",
    "build_event_envelope",
    "event_envelope_to_json",
    "event_envelope_from_json",
]
