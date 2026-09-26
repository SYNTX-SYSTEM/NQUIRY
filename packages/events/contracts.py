"""Durable Event semantic contracts (F08, WU-PFC-F08-1).

Source: 19_NQUIRY_IMPLEMENTATION_WITH_FRONTEND_RUNNING.md section 28 (F08:
"durable Event semantic contract", STORAGE FREEDOM, HISTORICAL EVENT BASIS,
PASS "No worker needs to invent missing Event semantics");
09_DATA_EVENT_API_CONTRACTS.md section 16 (EventEnvelope), section 70/71
(event names describe already approved facts and introduce no transition),
section 72 (immutability; payload schema version may evolve), section 174
(every event specification names EVENT TYPE, SCHEMA VERSION,
AGGREGATE/TARGET, PAYLOAD, REPLAY BEHAVIOR, CONSUMER SIDE-EFFECT POLICY).

WHAT A CONTRACT FIXES
--------------------------------------------------------------------
For every event type a governed Command actually commits today (F02, F03,
F04, plus the PKG-era decision and selection handlers), the contract names
the aggregate kind whose `record_version` the Event records, whether that
aggregate is versioned, and the exact payload keys. The payload carries only
committed structural facts: identities, states, versions, counts,
fingerprints and closed-vocabulary values. It never carries user-authored
free text (Question text, Challenge title or frame, Decision rationale or
option). That text stays in its canonical row. Copying it into an immutable,
never-deleted Event would decide retention and deletion (GAP-11-007,
NQ-GAP-057, both OPEN) by construction. [Case 2 choice, WU-PFC-F08-1.]

Every contract shares one replay behavior and one consumer side-effect
policy (09 section 18, section 73.1, section 74): replay may rebuild
projections only, and consumers dedupe by `event_id` and never issue a
Command.

Event names are the ones the handlers already commit (09 section 71 permits
additional names for approved facts). Nothing is renamed: the default
`<COMMAND>_COMMITTED` names emitted by the PKG-era handlers are historical
facts in existing outbox rows.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field

from semantic_types.versions import ContractVersion

JsonScalar = str | int | bool | None

SCHEMA_1_0 = ContractVersion("1.0")
REPLAY_BEHAVIOR = "PROJECTION_REBUILD_ONLY"
CONSUMER_SIDE_EFFECT_POLICY = "DEDUPE_BY_EVENT_ID_NO_COMMAND"

_UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


class EventContractViolation(ValueError):
    """A commit's Event facts do not satisfy the event type's contract. The
    commit is refused; no Event is invented or repaired."""


class EventBasisMissing(LookupError):
    """No durable committed Event exists for an outbox record, so its
    EventEnvelope cannot be reconstructed exactly (10 section 17: "No
    authoritative Event may be regenerated from guesswork")."""


@dataclass(frozen=True, slots=True)
class EventFacts:
    """What a mutation states about the Event its commit records. The
    envelope's version, identities, actor and authority are filled in by the
    CommitCoordinator from the committed facts, never by the mutation."""

    aggregate_ref: str
    payload: Mapping[str, JsonScalar] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EventContract:
    event_type: str
    aggregate_kind: str
    payload_keys: frozenset[str]
    schema_version: ContractVersion = SCHEMA_1_0
    versioned: bool = True
    """False for immutable aggregates without `record_version`: their only
    version is 1 (`RecordVersion.initial()`)."""


EventContractRegistry = Mapping[str, EventContract]


def _c(event_type: str, kind: str, *keys: str, versioned: bool = True) -> EventContract:
    return EventContract(event_type, kind, frozenset(keys), versioned=versioned)


_SESSION_TRANSITION = ("session_id", "previous_state", "state")

PRODUCTION_EVENT_CONTRACTS: EventContractRegistry = {
    c.event_type: c
    for c in (
        # F01/F02 governance
        _c(
            "WORKSPACE_CREATED",
            "workspace",
            "workspace_id",
            "owner_user_id",
            "governance_binding_id",
        ),
        _c(
            "CMD_ADD_MEMBER_COMMITTED",
            "workspace_membership",
            "membership_id",
            "member_user_id",
            "role_assignment_id",
            "role",
        ),
        _c(
            "CMD_GRANT_HUMAN_AUTHORITY_BINDING_COMMITTED",
            "authority_binding",
            "binding_id",
            "human_user_id",
            "authority_class",
            "scope_type",
            "scope_id",
            "state",
        ),
        _c(
            "CMD_REVOKE_HUMAN_AUTHORITY_BINDING_COMMITTED",
            "authority_binding",
            "binding_id",
            "previous_state",
            "state",
        ),
        # F02 inquiry context
        _c("CHALLENGE_CREATED", "challenge", "challenge_id"),
        _c(
            "SESSION_CREATED",
            "session",
            "session_id",
            "challenge_id",
            "state",
            "applied_method_key",
            "applied_method_version",
        ),
        _c("SESSION_SETUP", "session", *_SESSION_TRANSITION),
        _c("SESSION_CHALLENGE_CAPTURE", "session", *_SESSION_TRANSITION),
        # F02/F03 Burst
        _c("QUESTION_BURST_PREPARED", "burst", "burst_id", "session_id", "state", "mode"),
        _c(
            "SESSION_PARTICIPANT_ADMITTED",
            "session_participation",
            "participation_id",
            "session_id",
            "participant_user_id",
        ),
        _c(
            "QUESTION_GENERATION_OPENED",
            "session",
            *_SESSION_TRANSITION,
            "burst_id",
            "burst_state",
        ),
        _c(
            "BURST_QUESTION_CAPTURED",
            "question",
            "question_id",
            "burst_id",
            "session_id",
            "burst_question_membership_id",
            "captured_order",
            "origin",
        ),
        _c(
            "QUESTION_GENERATION_CLOSED",
            "session",
            *_SESSION_TRANSITION,
            "burst_id",
            "burst_state",
            "frozen_membership_fingerprint",
            "frozen_member_count",
        ),
        # F04 analysis
        _c(
            "SESSION_ANALYSIS_BEGUN",
            "session",
            *_SESSION_TRANSITION,
            "operation_authorization_id",
            "ai_operation_id",
            "authorization_shape",
        ),
        _c(
            "AI_OPERATION_REQUESTED",
            "ai_operation_authorization",
            "authorization_id",
            "session_id",
            "ai_operation_id",
            "authorization_shape",
            "request_case",
            "sequence_no",
            "supersedes_authorization_id",
            "retry_of_generation_id",
            versioned=False,
        ),
        _c(
            "AI_GENERATION_REQUESTED",
            "ai_generation",
            "ai_generation_id",
            "session_id",
            "operation_authorization_id",
            "ai_context_manifest_id",
            "ai_operation_id",
            "status",
        ),
        _c(
            "AI_OUTPUT_ACCEPTED",
            "ai_derived_artifact",
            "ai_derived_artifact_id",
            "ai_generation_id",
            "session_id",
            "ai_operation_id",
            "generation_status",
        ),
        _c(
            "QUESTION_CLUSTERS_ACCEPTED",
            "ai_derived_artifact",
            "ai_derived_artifact_id",
            "ai_generation_id",
            "session_id",
            "ai_operation_id",
            "generation_status",
        ),
        # PKG-era decision and selection handlers
        _c(
            "CMD_OPEN_DECISION_CONSIDERATION_COMMITTED",
            "decision",
            "decision_id",
            "challenge_id",
            "state",
        ),
        _c(
            "CMD_RECORD_HUMAN_DECISION_COMMITTED",
            "decision",
            "decision_id",
            "previous_state",
            "state",
            "decided_by_user_id",
        ),
        _c(
            "CMD_SELECT_COMPELLING_QUESTION_COMMITTED",
            "question_selection",
            "question_selection_id",
            "session_id",
            "question_id",
            "selection_type",
        ),
        _c(
            "CMD_SELECT_PRIMARY_QUESTION_COMMITTED",
            "question_selection",
            "question_selection_id",
            "session_id",
            "question_id",
            "selection_type",
        ),
    )
}


def aggregate_kind_and_id(aggregate_ref: str) -> tuple[str, str]:
    """Splits a `"<kind>:<uuid>"` aggregate ref. Raises for any other shape."""
    match = re.fullmatch(rf"([a-z_]+):({_UUID})", aggregate_ref)
    if match is None:
        raise EventContractViolation(f"MALFORMED_AGGREGATE_REF: {aggregate_ref!r}")
    return match.group(1), match.group(2)


def validate_event_facts(
    event_type: str, facts: EventFacts | None, registry: EventContractRegistry
) -> EventContract:
    """Returns the contract `facts` satisfy, or raises EventContractViolation.
    A commit whose mutation stated no Event facts has no Event basis and is
    refused (EVENT_BASIS_MISSING)."""
    if facts is None:
        raise EventContractViolation(f"EVENT_BASIS_MISSING: {event_type}")
    contract = registry.get(event_type)
    if contract is None:
        raise EventContractViolation(f"EVENT_TYPE_WITHOUT_CONTRACT: {event_type}")
    kind, _ = aggregate_kind_and_id(facts.aggregate_ref)
    if kind != contract.aggregate_kind:
        raise EventContractViolation(
            f"AGGREGATE_KIND_MISMATCH: {event_type} expects {contract.aggregate_kind}, got {kind}"
        )
    keys = frozenset(facts.payload)
    if keys != contract.payload_keys:
        raise EventContractViolation(
            f"PAYLOAD_KEYS_MISMATCH: {event_type} missing "
            f"{sorted(contract.payload_keys - keys)} extra {sorted(keys - contract.payload_keys)}"
        )
    for key, value in facts.payload.items():
        if value is not None and not isinstance(value, str | int | bool):
            raise EventContractViolation(f"PAYLOAD_VALUE_NOT_SCALAR: {event_type}.{key}")
    return contract


__all__ = [
    "CONSUMER_SIDE_EFFECT_POLICY",
    "PRODUCTION_EVENT_CONTRACTS",
    "REPLAY_BEHAVIOR",
    "SCHEMA_1_0",
    "EventBasisMissing",
    "EventContract",
    "EventContractRegistry",
    "EventContractViolation",
    "EventFacts",
    "JsonScalar",
    "aggregate_kind_and_id",
    "validate_event_facts",
]
