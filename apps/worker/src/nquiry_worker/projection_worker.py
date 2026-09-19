"""ProjectionWorker: applies committed EventEnvelopes to the real
ProjectionRepository, and drives rebuild/replay.

Source: 10_FAILURE_RECOVERY_ROLLBACK.md section 31 (RC-01 Deterministic
Technical Recovery -- "rebuild projection from committed canonical
state" is a named SYSTEM_SERVICE-eligible example); 09_DATA_EVENT_API_CONTRACTS.md
section 18 (Event Replay Contract -- replay MAY "rebuild projections /
reconstruct read models / verify histories"; replay MAY NOT "invoke
external side effects / submit new consequential Commands automatically
/ re-run AI tools as if newly authorized / advance canonical state");
14_IMPLEMENTATION_SEQUENCE.md section 41 ("event consumer cannot import
direct consequential handler").

WHY THIS FILE IMPORTS ONLY `events`/`projection`/`semantic_types`,
NEVER `command`/`commit`/`persistence`
--------------------------------------------------------------------
Same file-level exclusivity discipline `outbox_worker.py` already
established (PKG-20): `nquiry_worker`'s own package-level ceiling
(`{events, projection, recovery, command, commit, semantic_types}`) is
wide enough for a *future* `recovery_worker.py` sibling, but that does
not mean THIS file may use all of it.
`tests/security/test_projection_worker_exclusivity.py` proves, by
scanning this file's own real AST, that it imports none of `command`,
`commit`, `persistence`.

WHY `apply_batch`/`rebuild` TAKE AN ALREADY-RESOLVED
`Sequence[EventEnvelope]`, NOT A LIVE EventEnvelopeSource
--------------------------------------------------------------------
See `events.envelope`'s own module docstring (PKG-20): no durable path
from a bare `OutboxRecord.commit_id` to a fully historically faithful
`EventEnvelope` exists yet in this codebase. This worker proves the
PROJECTION mechanics (idempotent apply, checkpoint advance, rebuild
reproduces identical state, replay never re-enters a Command/CommitUnit
path) against real, caller-supplied envelopes -- the same disclosed
`SUCCESSOR_NOT_BUILT` boundary `OutboxWorker`'s own `EventEnvelopeSource`
already names, not a new gap this package introduces.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from events.envelope import EventEnvelope
from projection.consumer import ProjectionConsumer, projection_name_for
from projection.models import ProjectionRepository
from semantic_types.ids import WorkspaceId


@dataclass(frozen=True, slots=True)
class ProjectionApplyResult:
    """Outcome of one `ProjectionWorker.apply_batch()`/`rebuild()` call.
    Never a bare count -- each applied `event_id` is individually
    reconstructable, matching this codebase's "no unversioned
    consequential dict payloads" discipline.
    """

    applied_event_ids: tuple[uuid.UUID, ...]


class ProjectionWorker:
    """SYSTEM_SERVICE-class deterministic recovery (10 section 31): this
    worker's own `rebuild()` IS the named "rebuild projection from
    committed canonical state" example. Creates no new domain choice,
    invents no authority, and never re-enters the governed
    Command/CommitUnit write path -- see this module's own docstring
    and `tests/security/test_projection_worker_exclusivity.py` for the
    structural proof.
    """

    def __init__(self, *, repository: ProjectionRepository, consumer: ProjectionConsumer) -> None:
        self._repository = repository
        self._consumer = consumer

    def apply_batch(
        self, envelopes: Sequence[EventEnvelope], *, workspace_id: WorkspaceId
    ) -> ProjectionApplyResult:
        """Applies every envelope, in the given order, then advances
        the checkpoint for whichever named projection each one belongs
        to. Idempotent per envelope: an already-applied `event_id`
        (09 section 15.2, at-least-once redelivery) is a safe no-op at
        both the consumer and the repository layer.
        """
        applied: list[uuid.UUID] = []
        for envelope in envelopes:
            self._consumer.handle(envelope)
            self._repository.advance_checkpoint(
                projection_name_for(envelope),
                workspace_id,
                last_processed_event_id=envelope.event_id,
            )
            applied.append(envelope.event_id.value)
        return ProjectionApplyResult(applied_event_ids=tuple(applied))

    def rebuild(
        self,
        envelopes: Sequence[EventEnvelope],
        *,
        projection_name: str,
        workspace_id: WorkspaceId,
    ) -> ProjectionApplyResult:
        """Mandatory adversarial attack: delete projection then
        rebuild. Wipes every row (and the checkpoint) for exactly one
        named projection, then replays the full given history from
        scratch -- proving the read model is genuinely rebuildable and
        never itself a source of truth (AS-007).
        """
        self._repository.reset_projection(projection_name, workspace_id)
        return self.apply_batch(envelopes, workspace_id=workspace_id)


__all__ = ["ProjectionApplyResult", "ProjectionWorker"]
