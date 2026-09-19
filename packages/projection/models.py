"""Projection read-model contracts: SessionReadModel, InquiryReadModel,
ProjectionCheckpoint, and the ProjectionRepository port.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 7.1 (core tables --
`projection_checkpoints`/`session_read_model`/`inquiry_read_model`,
each "Workspace key: yes"), section 8 (`projection_writer` principal:
"Reads: outbox/Event source; Writes: projection only; Forbidden:
canonical/governance/Evidence writes"), section 9 (migration
`010_projection`: "read models, checkpoints", depends on `009`, gate
"rebuild tests"), section 10 ("ProjectionRepository: projection-only
read/write"), section 3.1 (`projection`'s exact allow-list: `events,
projection persistence` -- no `domain`, no `authority`).
09_DATA_EVENT_API_CONTRACTS.md section 123 (Query Projections --
"Session history" is one of the named approved projections).
12_MINIMUM_PROTOTYPE_ARCHITECTURE.md ("Full Inquiry Graph | EXCLUDED |
Projection semantics not required for proof", "DEC-A001 | graph scope |
later"; "Projection | DERIVED | Read model for event replay proof").

WHY `inquiry_read_model` IS A GENERIC PER-AGGREGATE SNAPSHOT, NOT THE
FULL INQUIRY GRAPH
--------------------------------------------------------------------
12's own minimum-prototype table explicitly excludes the full
InquiryGraph (09 section 124's own 9-Thing/Relation node/edge list)
from this build's required proof -- "graph scope: later" (DEC-A001,
still open). 14 section 7.1 nonetheless commits to an
`inquiry_read_model` table existing in migration `010_projection`.
This package therefore builds the table with a deliberately generic,
single-aggregate snapshot shape (`aggregate_ref` + a JSONB `snapshot`),
proving the identical rebuildable/idempotent/replay-safe projection
MECHANISM this package is actually scoped to prove, without inventing
graph node/edge semantics 09/12 do not commit this build phase to.

WHY `current_state`/`snapshot` ARE PLAIN STRING/JSONB, NEVER A CLOSED
DOMAIN ENUM
--------------------------------------------------------------------
`projection`'s own 14 section 3.1 allow-list has no `domain` entry, so
this package cannot import `domain.session.SessionState` or any other
canonical closed type. Same "closed vocabulary enforced elsewhere,
held as inert string here" pattern already used for
`audit.AuditEvent.result`/`command`'s own actor fields -- legitimate
because the value only ever MIRRORS upstream truth, never itself
becomes an authority source (14 PKG-21 AUTHORITY: "Projection never
authority source").

WHY `ProjectionCheckpoint.checkpoint_version`/`*ReadModel.projection_version`
ARE PLAIN INTS, NOT A `RecordVersion` REUSE
--------------------------------------------------------------------
`RecordVersion` (14 section 5.1) is specifically the optimistic-
concurrency counter for a CANONICAL/governance row's own current
version, and must be `>= 1`. A checkpoint counts how many Events THIS
projection has applied so far -- a different concept, whose legitimate
starting point (0, before anything is applied) `RecordVersion` cannot
represent. Reusing it here would blur, not honor, 14's own closed-type
discipline.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from semantic_types.ids import EventId, SessionId, WorkspaceId


@dataclass(frozen=True, slots=True)
class ProjectionCheckpoint:
    """One row of `projection_checkpoints` -- how far one named
    projection has consumed the committed-Event stream for one
    Workspace.
    """

    projection_name: str
    workspace_id: WorkspaceId
    checkpoint_version: int
    updated_at: datetime
    last_processed_event_id: EventId | None = None

    def __post_init__(self) -> None:
        if not self.projection_name:
            raise ValueError("ProjectionCheckpoint.projection_name must be non-empty")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if self.checkpoint_version < 0:
            raise ValueError("ProjectionCheckpoint.checkpoint_version must be >= 0")
        if self.last_processed_event_id is not None and not isinstance(
            self.last_processed_event_id, EventId
        ):
            raise TypeError(
                "last_processed_event_id must be an EventId or None, got "
                f"{type(self.last_processed_event_id)!r}"
            )


@dataclass(frozen=True, slots=True)
class SessionReadModel:
    """One row of `session_read_model` -- 09 section 123's own named
    "Session history" approved projection, mirroring the real
    `sessions` row it is keyed against (a real composite foreign key,
    the structural defense for the "corrupt projection" mandatory
    attack).
    """

    session_id: SessionId
    workspace_id: WorkspaceId
    current_state: str
    projection_version: int
    last_event_id: EventId
    updated_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.session_id, SessionId):
            raise TypeError(f"session_id must be a SessionId, got {type(self.session_id)!r}")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not self.current_state:
            raise ValueError("SessionReadModel.current_state must be non-empty")
        if self.projection_version < 1:
            raise ValueError("SessionReadModel.projection_version must be >= 1")
        if not isinstance(self.last_event_id, EventId):
            raise TypeError(f"last_event_id must be an EventId, got {type(self.last_event_id)!r}")


@dataclass(frozen=True, slots=True)
class InquiryReadModel:
    """One row of `inquiry_read_model` -- a deliberately generic
    per-aggregate snapshot, NOT the full InquiryGraph (see this
    module's own docstring for why).
    """

    id: uuid.UUID
    aggregate_ref: str
    workspace_id: WorkspaceId
    projection_version: int
    snapshot: Mapping[str, object]
    last_event_id: EventId
    updated_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.id, uuid.UUID):
            raise TypeError(f"id must be a uuid.UUID, got {type(self.id)!r}")
        if not self.aggregate_ref:
            raise ValueError("InquiryReadModel.aggregate_ref must be non-empty")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if self.projection_version < 1:
            raise ValueError("InquiryReadModel.projection_version must be >= 1")
        if not isinstance(self.last_event_id, EventId):
            raise TypeError(f"last_event_id must be an EventId, got {type(self.last_event_id)!r}")


@runtime_checkable
class ProjectionRepository(Protocol):
    """14 section 10: "ProjectionRepository: projection-only read/write."
    No method here can reach `sessions`/`questions`/any other canonical
    table for a WRITE -- the composite foreign key on `session_read_model`
    is read-only from this port's own perspective.
    """

    def get_session_read_model(
        self, session_id: SessionId, workspace_id: WorkspaceId
    ) -> SessionReadModel | None: ...

    def upsert_session_read_model(self, model: SessionReadModel) -> None: ...

    def get_inquiry_read_model(
        self, aggregate_ref: str, workspace_id: WorkspaceId
    ) -> InquiryReadModel | None: ...

    def upsert_inquiry_read_model(self, model: InquiryReadModel) -> None: ...

    def get_checkpoint(
        self, projection_name: str, workspace_id: WorkspaceId
    ) -> ProjectionCheckpoint | None: ...

    def advance_checkpoint(
        self, projection_name: str, workspace_id: WorkspaceId, *, last_processed_event_id: EventId
    ) -> None: ...

    def reset_projection(self, projection_name: str, workspace_id: WorkspaceId) -> None:
        """Deletes every read-model row and the checkpoint for one
        named projection in one Workspace -- the mandatory "delete
        projection then rebuild" adversarial attack's own entry point.
        Never touches any canonical table.
        """
        ...


__all__ = [
    "ProjectionCheckpoint",
    "SessionReadModel",
    "InquiryReadModel",
    "ProjectionRepository",
]
