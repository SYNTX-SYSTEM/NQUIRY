"""T7 COMMAND TEST: Command != Event (P-16).

Source: 13_TEST_AND_FALSIFICATION_ARCHITECTURE.md P-16
(T13-P16-COMMAND-EVENT); 09_DATA_EVENT_API_CONTRACTS.md section 160.3
("Replay sends old Event to Command handler" -- "EventEnvelope is
type-distinct. Replay consumer cannot invoke canonical mutation
directly."); 14_IMPLEMENTATION_SEQUENCE.md section 50 (this exact file
is P-16's assigned test file).

WHAT THIS FILE PROVES AT PKG-10's BUILD PHASE, AND WHAT IT DOES NOT
--------------------------------------------------------------------
P-16's full precondition is "committed Command/Event pair" -- no
`EventEnvelope` type exists yet (`packages/events/` remains a PKG-00
stub; PKG-12 owns it) and no CommitUnit exists yet (PKG-13), so a real
committed Event cannot be constructed to attempt replaying as a
Command. What this package CAN and does prove is the exact mechanism
09 section 160.3 names as the defense -- "EventEnvelope is
type-distinct" -- at the one place that mechanism already exists:
`CommandEnvelope.command_id` structurally rejects an `EventId` (or any
identity other than `CommandId`). This is the necessary foundation
P-16's full proof will build on once PKG-12 introduces a real
`EventEnvelope`; it is not yet a proof that a *committed* Event cannot
be resubmitted as a Command (SUCCESSOR_NOT_BUILT).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from command.envelope import CommandEnvelope
from semantic_types.ids import AttemptId, CommandId, CorrelationId, EventId, WorkspaceId
from semantic_types.versions import ContractVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


@dataclass(frozen=True, slots=True)
class _Payload:
    note: str


def _envelope_kwargs(*, command_id: object) -> dict[str, object]:
    return {
        "command_id": command_id,
        "command_type": "CMD_TEST_OPERATION",
        "command_contract_version": ContractVersion("1.0"),
        "attempt_id": AttemptId(uuid.uuid4()),
        "correlation_id": CorrelationId(uuid.uuid4()),
        "requested_at": _NOW,
        "requesting_actor_type": "HUMAN_USER",
        "requesting_actor_id": "user-ref-1",
        "workspace_scope_ref": WorkspaceId(uuid.uuid4()),
        "target_refs": (),
        "expected_versions": {},
        "payload": _Payload("hello"),
    }


def test_a_real_command_id_constructs_successfully() -> None:
    """Legitimate control: an actual CommandId is accepted."""
    envelope = CommandEnvelope(**_envelope_kwargs(command_id=CommandId(uuid.uuid4())))  # type: ignore[arg-type]
    assert isinstance(envelope.command_id, CommandId)


def test_an_event_id_cannot_construct_a_command_envelope() -> None:
    """ATTACK: submit an EventId as command_id.
    EXPECTED DEFENSE: CommandEnvelope.__post_init__'s isinstance(command_id, CommandId) check.
    EXPECTED BOUNDARY: NOT_APPLICABLE (no BND-XXX invoked at this layer).
    EXPECTED CANONICAL RESULT: TypeError, no CommandEnvelope instance produced.
    EXPECTED PROOF ARTIFACT: the raised TypeError itself (construction never completes).
    ACTUAL RESULT: matches.
    """
    with pytest.raises(TypeError, match="command_id must be a CommandId"):
        CommandEnvelope(**_envelope_kwargs(command_id=EventId(uuid.uuid4())))  # type: ignore[arg-type]


def test_a_bare_uuid_cannot_construct_a_command_envelope() -> None:
    """ATTACK: submit a bare uuid.UUID (no strong identity at all) as command_id.
    EXPECTED DEFENSE: same isinstance check -- a bare UUID is not a CommandId either.
    EXPECTED CANONICAL RESULT: TypeError.
    ACTUAL RESULT: matches.
    """
    with pytest.raises(TypeError, match="command_id must be a CommandId"):
        CommandEnvelope(**_envelope_kwargs(command_id=uuid.uuid4()))  # type: ignore[arg-type]


def test_a_plain_string_cannot_construct_a_command_envelope() -> None:
    """ATTACK: submit a plain string id as command_id.
    EXPECTED CANONICAL RESULT: TypeError.
    ACTUAL RESULT: matches.
    """
    with pytest.raises(TypeError, match="command_id must be a CommandId"):
        CommandEnvelope(**_envelope_kwargs(command_id=str(uuid.uuid4())))  # type: ignore[arg-type]
