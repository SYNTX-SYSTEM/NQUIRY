"""ProjectionConsumer: the real `events.envelope.EventConsumer`
implementation updating `session_read_model`/`inquiry_read_model`.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 48 (file-level map names
this exact file, `packages/projection/consumer.py`, "projection only");
09_DATA_EVENT_API_CONTRACTS.md section 15.2 (At-Least-Once Delivery --
"must not produce duplicate consequential effects solely because
delivery repeats"); 06_BOUNDARY_ARCHITECTURE.md section 13's own BYPASS
PATHS list for BND-007 explicitly names "event consumer projection
writing state" as a FORBIDDEN path -- this consumer writes only to the
two projection tables, never to any canonical `sessions`/`questions`/
etc. row, structurally enforced by `projection`'s own 14 section 3.1
allow-list (`events, persistence` -- no `domain`, no canonical writer).

WHY DISPATCH IS BY `aggregate_ref` STRING PREFIX
--------------------------------------------------------------------
`[IMPLEMENTATION CHOICE]`, disclosed: an `EventEnvelope.aggregate_ref`
of the form `"session:<uuid>"` is routed to `SessionReadModel`; every
other shape falls through to the generic `InquiryReadModel` snapshot.
`"session:<id>"` is the SAME ref format `domain.question_selection.
session_target_ref` already uses for Session targets (PKG-14) --
`projection` cannot import `domain` (14 section 3.1), so this module
recognizes the format by convention rather than by importing that
function, the same one-line-format-not-worth-a-cross-package-import
precedent already accepted for `commit_units.target_refs` string
conventions elsewhere in this codebase.

WHY IDEMPOTENCY IS CHECKED HERE, NOT ONLY AT THE REPOSITORY LAYER
--------------------------------------------------------------------
`_apply_to_session_read_model`/`_apply_to_inquiry_read_model` compare
the envelope's own `event_id` against the read model row's stored
`last_event_id` BEFORE calling the repository -- a genuine at-least-once
redelivery of the identical Event is therefore a safe no-op at the
application layer already, not merely relying on a database-level
guard (though `persistence.projection_repository`'s own upsert is
independently idempotent too, defense-in-depth, matching this
codebase's dominant pattern).
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping

from events.envelope import EventEnvelope
from semantic_types.ids import SessionId

from projection.models import InquiryReadModel, ProjectionRepository, SessionReadModel

_SESSION_AGGREGATE_PREFIX = "session:"

SESSION_PROJECTION_NAME = "session_read_model"
INQUIRY_PROJECTION_NAME = "inquiry_read_model"


def session_aggregate_ref(session_id: SessionId) -> str:
    """Builds the `"session:<uuid>"` aggregate ref this consumer
    recognizes -- see this module's own docstring for why the format
    is a disclosed convention rather than a cross-package import.
    """
    return f"{_SESSION_AGGREGATE_PREFIX}{session_id.value}"


def projection_name_for(envelope: EventEnvelope) -> str:
    """The single source of truth for which named projection (and
    therefore which `projection_checkpoints` row) a given envelope
    belongs to -- shared by `ProjectionConsumer.handle` itself and
    `nquiry_worker.projection_worker.ProjectionWorker` (which needs to
    know this to advance the correct checkpoint), so the two never
    silently drift.
    """
    if envelope.aggregate_ref.startswith(_SESSION_AGGREGATE_PREFIX):
        return SESSION_PROJECTION_NAME
    return INQUIRY_PROJECTION_NAME


class ProjectionConsumer:
    """The real, production `EventConsumer` for this codebase's two
    named read models. Never returns anything, never re-enters a
    Command/CommitUnit path -- `handle`'s own signature and this
    class's method surface carry no such capability at all.
    """

    def __init__(self, *, repository: ProjectionRepository) -> None:
        self._repository = repository

    def handle(self, envelope: EventEnvelope) -> None:
        if projection_name_for(envelope) == SESSION_PROJECTION_NAME:
            self._apply_to_session_read_model(envelope)
        else:
            self._apply_to_inquiry_read_model(envelope)

    def _apply_to_session_read_model(self, envelope: EventEnvelope) -> None:
        session_id = SessionId(uuid.UUID(envelope.aggregate_ref[len(_SESSION_AGGREGATE_PREFIX) :]))
        current = self._repository.get_session_read_model(session_id, envelope.workspace_scope_ref)
        if current is not None and current.last_event_id.value == envelope.event_id.value:
            return  # already applied -- idempotent redelivery, 09 section 15.2
        payload_state = _extract_state(envelope.payload)
        model = SessionReadModel(
            session_id=session_id,
            workspace_id=envelope.workspace_scope_ref,
            current_state=payload_state if payload_state is not None else _fallback_state(current),
            projection_version=1 if current is None else current.projection_version + 1,
            last_event_id=envelope.event_id,
            updated_at=envelope.occurred_at,
        )
        self._repository.upsert_session_read_model(model)

    def _apply_to_inquiry_read_model(self, envelope: EventEnvelope) -> None:
        current = self._repository.get_inquiry_read_model(
            envelope.aggregate_ref, envelope.workspace_scope_ref
        )
        if current is not None and current.last_event_id.value == envelope.event_id.value:
            return  # already applied -- idempotent redelivery, 09 section 15.2
        model = InquiryReadModel(
            id=current.id if current is not None else uuid.uuid4(),
            aggregate_ref=envelope.aggregate_ref,
            workspace_id=envelope.workspace_scope_ref,
            projection_version=1 if current is None else current.projection_version + 1,
            snapshot=_extract_snapshot(envelope.payload),
            last_event_id=envelope.event_id,
            updated_at=envelope.occurred_at,
        )
        self._repository.upsert_inquiry_read_model(model)


def _extract_state(payload: object) -> str | None:
    if isinstance(payload, Mapping) and isinstance(payload.get("state"), str):
        return payload["state"]
    return None


def _fallback_state(current: SessionReadModel | None) -> str:
    # A payload carrying no recognizable "state" key never invents one
    # -- keep whatever was already projected, or an explicit sentinel
    # for a genuinely first-ever projection with no state information.
    return current.current_state if current is not None else "UNKNOWN"


def _extract_snapshot(payload: object) -> Mapping[str, object]:
    if isinstance(payload, Mapping):
        return dict(payload)
    return {"raw": repr(payload)}


__all__ = [
    "SESSION_PROJECTION_NAME",
    "INQUIRY_PROJECTION_NAME",
    "ProjectionConsumer",
    "session_aggregate_ref",
    "projection_name_for",
]
