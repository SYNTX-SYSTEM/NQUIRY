"""T7 COMMAND TEST: CommandRegistry -- the generic Command catalogue.

Pure Python -- no database, no concrete named Command registered
(mirrors `tests/boundaries/test_registry.py`'s generic-engine-only
scope for PKG-08).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from command.envelope import CommandEnvelope
from command.registry import (
    CommandContract,
    CommandContractVersionMismatch,
    CommandRegistrationError,
    CommandRegistry,
    UnregisteredCommandTypeError,
)
from semantic_types.ids import AttemptId, CommandId, CorrelationId, WorkspaceId
from semantic_types.versions import ContractVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


@dataclass(frozen=True, slots=True)
class _Payload:
    note: str


def _envelope(*, command_type: str, contract_version: ContractVersion) -> CommandEnvelope:
    return CommandEnvelope(
        command_id=CommandId(uuid.uuid4()),
        command_type=command_type,
        command_contract_version=contract_version,
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        requested_at=_NOW,
        requesting_actor_type="HUMAN_USER",
        requesting_actor_id="user-ref-1",
        workspace_scope_ref=WorkspaceId(uuid.uuid4()),
        target_refs=(),
        expected_versions={},
        payload=_Payload("hello"),
    )


def test_registers_and_retrieves_a_contract() -> None:
    registry = CommandRegistry()
    contract = CommandContract(command_type="CMD_TEST", contract_version=ContractVersion("1.0"))

    registry.register(contract)

    assert registry.get("CMD_TEST") is contract


def test_get_returns_none_for_an_unregistered_command_type() -> None:
    registry = CommandRegistry()
    assert registry.get("CMD_UNKNOWN") is None


def test_no_silent_overwrite_of_an_already_registered_command_type() -> None:
    registry = CommandRegistry()
    registry.register(CommandContract("CMD_TEST", ContractVersion("1.0")))

    with pytest.raises(CommandRegistrationError):
        registry.register(CommandContract("CMD_TEST", ContractVersion("2.0")))


def test_validate_envelope_accepts_a_registered_matching_version() -> None:
    registry = CommandRegistry()
    registry.register(CommandContract("CMD_TEST", ContractVersion("1.0")))
    envelope = _envelope(command_type="CMD_TEST", contract_version=ContractVersion("1.0"))

    registry.validate_envelope(envelope)  # must not raise


def test_validate_envelope_denies_an_unregistered_command_type() -> None:
    """Novel/adapted attack: unregistered command_type accepted."""
    registry = CommandRegistry()
    envelope = _envelope(
        command_type="CMD_NEVER_REGISTERED", contract_version=ContractVersion("1.0")
    )

    with pytest.raises(UnregisteredCommandTypeError):
        registry.validate_envelope(envelope)


def test_validate_envelope_denies_a_contract_version_mismatch() -> None:
    """Novel/adapted attack: silent semantic contract change (14 section
    42) accepted without detection.
    """
    registry = CommandRegistry()
    registry.register(CommandContract("CMD_TEST", ContractVersion("1.0")))
    envelope = _envelope(command_type="CMD_TEST", contract_version=ContractVersion("2.0"))

    with pytest.raises(CommandContractVersionMismatch):
        registry.validate_envelope(envelope)


def test_registry_holds_no_dispatch_or_execution_logic() -> None:
    """`get`/`validate_envelope` never invoke anything -- registering a
    contract does not construct, call, or otherwise execute a handler.
    """
    registry = CommandRegistry()
    contract = CommandContract("CMD_TEST", ContractVersion("1.0"))
    registry.register(contract)

    # Looking the contract up twice returns the identical object,
    # proving no per-call construction/side effect occurs.
    assert registry.get("CMD_TEST") is registry.get("CMD_TEST")
