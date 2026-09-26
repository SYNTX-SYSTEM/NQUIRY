"""WU-PFC-F08-1 (F08 Consequence Integrity): the durable, immutable Event basis.

Architecture: 19 §28 (F08: "durable immutable Event basis", STORAGE FREEDOM,
"Must reconstruct required historical fields without mutable-current
lookups", TESTS FIRST: commit + crash, exact Event equality, authority revoked
later, aggregate changes later, historical Event unchanged; PASS "No worker
needs to invent missing Event semantics"); 09 §15 (outbox), §16 (the 14-field
EventEnvelope), §17 (AC-09-003 events are post-commit facts), §72 (event
immutability), §174 (event contract template); 10 §17 ("No authoritative Event
may be regenerated from guesswork").

FIRST BROKEN RELATION (before this Work Unit): CommitUnit → durable immutable
Event basis. The outbox row carries delivery bookkeeping only; aggregate_ref,
aggregate_version_after_commit and payload have no durable source, so no exact
EventEnvelope can be reconstructed (`events.envelope` docstring,
`outbox_worker.EventEnvelopeSource` = SUCCESSOR_NOT_BUILT).

MUST BECOME TRUE: every governed commit durably records, in the same
transaction, one immutable committed Event whose 14 envelope fields are exact
committed facts. The envelope of any outbox row is reconstructable from it
alone, without mutable-current lookups.

MUST REMAIN TRUE: every F02/F03/F04 command outcome, audit and outbox write,
idempotency; the 11 named failure-injection points; atomicity.

MUST REMAIN IMPOSSIBLE: a commit without its Event basis; an Event without its
commit; an edited or deleted historical Event; an Event whose payload is outside
its contract; an Event reconstructed from guesswork (outbox rows without a basis
stay unresolvable); user-authored free text copied into an immutable Event.
"""

from __future__ import annotations

import uuid
from typing import Any

import f02_support as f02
import f03_support as f03
import f04_support as f04
import pytest
import sqlalchemy as sa
from commit.coordinator import CommitFailedPrecommit, CommitInjectionPoint
from persistence.tables import audit_events_table, outbox_events_table, sessions_table
from test_support.failure_injector import ScriptedFailureInjector

_EVENTS = "committed_events"


def _events(db: sa.Connection, ws: Any) -> list[Any]:
    rows = db.execute(
        sa.text(f"SELECT * FROM {_EVENTS} WHERE workspace_id = :ws ORDER BY occurred_at, event_id"),
        {"ws": ws.value},
    )
    return list(rows.mappings())


def _outbox(db: sa.Connection, ws: Any) -> list[Any]:
    stmt = sa.select(outbox_events_table).where(outbox_events_table.c.workspace_id == ws.value)
    return list(db.execute(stmt).mappings())


def _source(db: sa.Connection) -> Any:
    from persistence.committed_event_repository import CommittedEventEnvelopeSource

    return CommittedEventEnvelopeSource(db)


def _outbox_record(db: sa.Connection, event_id: uuid.UUID) -> Any:
    from persistence.outbox_repository import SqlAlchemyOutboxRepository

    outbox_id = db.execute(
        sa.select(outbox_events_table.c.id).where(outbox_events_table.c.event_id == event_id)
    ).scalar_one()
    return SqlAlchemyOutboxRepository(db).get(outbox_id)


def _analysed(db: sa.Connection) -> dict[str, Any]:
    """F02 founding .. F03 capture/completion .. F04 BEGIN_ANALYSIS .. the
    MockProvider analysis and clustering commits: every event family produced
    by the accepted predecessor Fields."""
    ctx = f04.analysis_context(db)
    outcome = f04.run(db, ctx, ctx["oa1"])
    assert outcome.status == "ACCEPTED"
    return ctx


# ------------------------------------------------------------ MUST BECOME TRUE


def test_every_commit_has_exactly_one_matching_committed_event(
    db_connection: sa.Connection,
) -> None:
    ctx = _analysed(db_connection)
    outbox = _outbox(db_connection, ctx["ws"])
    events = {e["event_id"]: e for e in _events(db_connection, ctx["ws"])}
    assert outbox and len(events) == len(outbox)
    for row in outbox:
        event = events[row["event_id"]]
        assert event["event_type"] == row["event_type"]
        assert event["commit_id"] == row["commit_id"]
        assert event["occurred_at"] == row["created_at"]


def test_envelope_fields_equal_the_committed_audit_facts(db_connection: sa.Connection) -> None:
    ctx = _analysed(db_connection)
    audits = {
        a["commit_id"]: a
        for a in db_connection.execute(
            sa.select(audit_events_table).where(
                audit_events_table.c.workspace_id == ctx["ws"].value
            )
        ).mappings()
    }
    for event in _events(db_connection, ctx["ws"]):
        audit = audits[event["commit_id"]]
        assert event["command_id"] == audit["command_id"]
        assert event["correlation_id"] == audit["correlation_id"]
        assert event["causation_id"] == audit["causation_id"]
        assert event["actor_ref"] == f"{audit['actor_type']}:{audit['actor_id']}"
        assert event["authority_source_ref"] == audit["authority_source_ref"]
        assert event["event_schema_version"] == "1.0"


def test_aggregate_versions_are_the_committed_row_versions(db_connection: sa.Connection) -> None:
    """Each Session event records the version the Session reached in that commit:
    1 at creation, then consecutive, and the last equals the row's version now."""
    ctx = _analysed(db_connection)
    ref = f"session:{ctx['session'].value}"
    versions = [
        e["aggregate_version_after_commit"]
        for e in _events(db_connection, ctx["ws"])
        if e["aggregate_ref"] == ref
    ]
    current = db_connection.execute(
        sa.select(sessions_table.c.record_version).where(
            sessions_table.c.id == ctx["session"].value
        )
    ).scalar_one()
    # The fixtures run on a fixed clock, so time does not order the commits;
    # the recorded versions must be exactly 1..current, each exactly once.
    assert sorted(versions) == list(range(1, current + 1))


def test_resolved_envelope_is_exact_and_needs_no_current_lookup(
    db_connection: sa.Connection,
) -> None:
    from events.envelope import EventEnvelope

    ctx = _analysed(db_connection)
    source = _source(db_connection)
    for event in _events(db_connection, ctx["ws"]):
        envelope = source.resolve(_outbox_record(db_connection, event["event_id"]))
        assert isinstance(envelope, EventEnvelope)
        assert envelope.event_id.value == event["event_id"]
        assert envelope.event_type == event["event_type"]
        assert envelope.aggregate_ref == event["aggregate_ref"]
        assert (
            envelope.aggregate_version_after_commit.value == event["aggregate_version_after_commit"]
        )
        assert envelope.commit_id.value == event["commit_id"]
        assert envelope.workspace_scope_ref.value == ctx["ws"].value
        assert dict(envelope.payload) == event["payload"]  # type: ignore[call-overload]


def test_session_events_carry_the_state_the_projection_consumes(
    db_connection: sa.Connection,
) -> None:
    """In version order, the Session events carry the state sequence of the
    accepted path (fixed clock: versions, not time, order the commits)."""
    ctx = _analysed(db_connection)
    ref = f"session:{ctx['session'].value}"
    ordered = sorted(
        (e for e in _events(db_connection, ctx["ws"]) if e["aggregate_ref"] == ref),
        key=lambda e: e["aggregate_version_after_commit"],
    )
    assert [e["payload"]["state"] for e in ordered] == [
        "DRAFT",
        "SETUP",
        "CHALLENGE_CAPTURE",
        "QUESTION_GENERATION",
        "QUESTION_CAPTURE",
        "ANALYSIS",
    ]
    for earlier, later in zip(ordered, ordered[1:], strict=False):
        assert later["payload"]["previous_state"] == earlier["payload"]["state"]


# ------------------------------------------------------------ historical truth


def test_later_session_change_leaves_earlier_events_unchanged(db_connection: sa.Connection) -> None:
    ctx = f04.capture_context(db_connection)
    before = {e["event_id"]: dict(e) for e in _events(db_connection, ctx["ws"])}
    f04.begin(db_connection, ctx)  # the Session advances to ANALYSIS
    after = {e["event_id"]: dict(e) for e in _events(db_connection, ctx["ws"])}
    assert set(before) < set(after)
    for event_id, event in before.items():
        assert after[event_id] == event


def test_authority_revoked_later_leaves_the_event_unchanged(db_connection: sa.Connection) -> None:
    """QUESTION_BURST_PREPARED was committed under the Facilitator's SESSION
    binding. Revoking that binding later (real governed Command) changes
    nothing in the historical Event."""
    from application.authority_binding_handler import revoke_human_authority_binding
    from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingVersionReader
    from semantic_types.ids import AttemptId, AuthorityBindingId, CommandId, CommitId, CorrelationId

    ctx = f03.prepared_context(db_connection)
    source = _source(db_connection)
    event = next(
        e for e in _events(db_connection, ctx["ws"]) if e["event_type"] == "QUESTION_BURST_PREPARED"
    )
    before = source.resolve(_outbox_record(db_connection, event["event_id"]))
    p = f02.ports(db_connection)
    revoke_human_authority_binding(
        db_connection,
        actor=f02.human(ctx["owner"]),
        workspace_id=ctx["ws"],
        binding_id=AuthorityBindingId(before.authority_source_ref),
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=f02.NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        workspace_repository=p.workspaces,
        membership_repository=p.memberships,
        authority_binding_repository=p.bindings,
        authority_resolver=p.resolver,
        command_repository=p.commands,
        audit_repository=p.audit,
        outbox_repository=p.outbox,
        commit_repository=p.commits,
        idempotency_port=p.idempotency,
        current_version_reader=SqlAlchemyAuthorityBindingVersionReader(db_connection),
    )
    state = db_connection.execute(
        sa.text("SELECT state FROM human_authority_bindings WHERE id = :b"),
        {"b": before.authority_source_ref},
    ).scalar_one()
    assert state == "REVOKED"
    assert source.resolve(_outbox_record(db_connection, event["event_id"])) == before
    revoked = [
        e
        for e in _events(db_connection, ctx["ws"])
        if e["event_type"] == "CMD_REVOKE_HUMAN_AUTHORITY_BINDING_COMMITTED"
    ]
    assert len(revoked) == 1 and revoked[0]["payload"]["state"] == "REVOKED"


@pytest.mark.parametrize("statement", ["UPDATE {t} SET payload = '{{}}'::jsonb", "DELETE FROM {t}"])
def test_historical_event_is_immutable(db_connection: sa.Connection, statement: str) -> None:
    ctx = f02.inquiry_context(db_connection)
    assert _events(db_connection, ctx["ws"])
    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.text(statement.format(t=_EVENTS) + " WHERE workspace_id = :ws"),
            {"ws": ctx["ws"].value},
        )


# ------------------------------------------------------------ MUST REMAIN IMPOSSIBLE


@pytest.mark.parametrize(
    "point",
    [
        CommitInjectionPoint.AFTER_FIRST_CANONICAL_MUTATION,
        CommitInjectionPoint.AFTER_AUDIT,
        CommitInjectionPoint.BEFORE_OUTBOX,
        CommitInjectionPoint.AFTER_OUTBOX,
        CommitInjectionPoint.BEFORE_DB_COMMIT,
    ],
)
def test_rolled_back_commit_leaves_no_event(
    db_connection: sa.Connection, point: CommitInjectionPoint
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    before = len(_events(db_connection, ctx["ws"]))
    with pytest.raises(CommitFailedPrecommit):
        f03.capture(
            db_connection,
            ctx,
            ctx["participants"][0],
            "Will fail?",
            ident_=f03.keyed_ident(),
            failure_injector=ScriptedFailureInjector(
                fire_at=point, exception=RuntimeError("injected")
            ),
        )
    assert len(_events(db_connection, ctx["ws"])) == before


def test_event_row_cannot_exist_without_its_outbox_and_commit(db_connection: sa.Connection) -> None:
    """An Event is a post-commit fact (AC-09-003): a row whose event_id names no
    outbox record, or whose commit_id names no CommitUnit, is refused by the
    database itself."""
    import json

    ctx = f02.inquiry_context(db_connection)
    (event, *_) = _events(db_connection, ctx["ws"])
    for override in ({"event_id": uuid.uuid4()}, {"commit_id": uuid.uuid4()}):
        forged = dict(event, **override, payload=json.dumps(event["payload"]))
        if "event_id" not in override:
            forged["event_id"] = uuid.uuid4()
        columns = ", ".join(forged)
        values = ", ".join("CAST(:payload AS jsonb)" if k == "payload" else f":{k}" for k in forged)
        with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
            db_connection.execute(
                sa.text(f"INSERT INTO {_EVENTS} ({columns}) VALUES ({values})"), forged
            )


def test_outbox_row_without_basis_is_never_reconstructed(db_connection: sa.Connection) -> None:
    """A pre-F08 outbox row has no exact basis: resolving it fails closed."""
    from events.contracts import EventBasisMissing

    ctx = f02.inquiry_context(db_connection)
    (row, *_) = _outbox(db_connection, ctx["ws"])
    record = _outbox_record(db_connection, row["event_id"])
    db_connection.execute(sa.text(f"ALTER TABLE {_EVENTS} DISABLE TRIGGER USER"))
    db_connection.execute(
        sa.text(f"DELETE FROM {_EVENTS} WHERE event_id = :e"), {"e": row["event_id"]}
    )
    db_connection.execute(sa.text(f"ALTER TABLE {_EVENTS} ENABLE TRIGGER USER"))
    with pytest.raises(EventBasisMissing):
        _source(db_connection).resolve(record)


def test_no_user_authored_free_text_is_copied_into_events(db_connection: sa.Connection) -> None:
    ctx = _analysed(db_connection)
    blob = " ".join(str(e["payload"]) for e in _events(db_connection, ctx["ws"]))
    texts = db_connection.execute(
        sa.text("SELECT original_text FROM questions WHERE workspace_id = :ws"),
        {"ws": ctx["ws"].value},
    ).scalars()
    titles = db_connection.execute(
        sa.text("SELECT title FROM challenges WHERE workspace_id = :ws"), {"ws": ctx["ws"].value}
    ).scalars()
    for text in [*texts, *titles]:
        assert text not in blob


def test_commit_without_event_facts_is_refused(db_connection: sa.Connection) -> None:
    """The coordinator never commits a consequence whose Event basis is missing."""
    from commit.coordinator import MutationOutcome
    from events.contracts import PRODUCTION_EVENT_CONTRACTS, validate_event_facts

    with pytest.raises(Exception, match="EVENT_BASIS_MISSING"):
        validate_event_facts(
            "CHALLENGE_CREATED", MutationOutcome().event, PRODUCTION_EVENT_CONTRACTS
        )


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        ({"challenge_id": "x", "title": "leaked"}, "PAYLOAD_KEYS_MISMATCH"),  # extra key
        ({}, "PAYLOAD_KEYS_MISMATCH"),  # missing key
        ({"challenge_id": 1.5}, "PAYLOAD_VALUE_NOT_SCALAR"),  # non-contract value
    ],
)
def test_payload_outside_its_contract_is_refused(payload: dict[str, Any], reason: str) -> None:
    from events.contracts import (
        PRODUCTION_EVENT_CONTRACTS,
        EventContractViolation,
        EventFacts,
        validate_event_facts,
    )

    facts = EventFacts(aggregate_ref=f"challenge:{uuid.uuid4()}", payload=payload)
    with pytest.raises(EventContractViolation, match=reason):
        validate_event_facts("CHALLENGE_CREATED", facts, PRODUCTION_EVENT_CONTRACTS)


def test_unregistered_event_type_or_wrong_aggregate_is_refused() -> None:
    from events.contracts import (
        PRODUCTION_EVENT_CONTRACTS,
        EventContractViolation,
        EventFacts,
        validate_event_facts,
    )

    good = EventFacts(aggregate_ref=f"challenge:{uuid.uuid4()}", payload={"challenge_id": "x"})
    with pytest.raises(EventContractViolation, match="EVENT_TYPE_WITHOUT_CONTRACT"):
        validate_event_facts("CHALLENGE_DELETED", good, PRODUCTION_EVENT_CONTRACTS)
    wrong = EventFacts(aggregate_ref=f"session:{uuid.uuid4()}", payload={"challenge_id": "x"})
    with pytest.raises(EventContractViolation, match="AGGREGATE_KIND_MISMATCH"):
        validate_event_facts("CHALLENGE_CREATED", wrong, PRODUCTION_EVENT_CONTRACTS)


def test_aggregate_of_another_workspace_is_refused(db_connection: sa.Connection) -> None:
    """An Event can only name an aggregate committed in its own Workspace."""
    from events.contracts import PRODUCTION_EVENT_CONTRACTS
    from persistence.committed_event_repository import (
        AggregateNotCommitted,
        committed_aggregate_version,
    )

    one = f02.inquiry_context(db_connection)
    other = f02.inquiry_context(db_connection)
    with pytest.raises(AggregateNotCommitted):
        committed_aggregate_version(
            db_connection,
            aggregate_ref=f"session:{one['session'].value}",
            workspace_id=other["ws"],
            contract=PRODUCTION_EVENT_CONTRACTS["SESSION_CREATED"],
        )


def test_outbox_record_that_disagrees_with_its_event_is_not_resolved(
    db_connection: sa.Connection,
) -> None:
    import dataclasses

    from events.contracts import EventBasisMissing

    ctx = f02.inquiry_context(db_connection)
    (row, *_) = _outbox(db_connection, ctx["ws"])
    record = _outbox_record(db_connection, row["event_id"])
    source = _source(db_connection)
    assert source.resolve(record).event_id == record.event_id
    from semantic_types.ids import CommitId, WorkspaceId

    for change in (
        {"event_type": "SOMETHING_ELSE"},
        {"workspace_id": WorkspaceId(uuid.uuid4())},
        {"commit_id": CommitId(uuid.uuid4())},
    ):
        forged = dataclasses.replace(record, **change)
        with pytest.raises(EventBasisMissing):
            source.resolve(forged)
