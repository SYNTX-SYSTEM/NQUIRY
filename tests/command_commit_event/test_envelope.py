"""T7 COMMAND TEST: CommandEnvelope construction and validation.

Pure Python -- no database. Covers the structural half of the mandatory
adversarial attacks (the persistence half lives in
`test_command_repository.py`).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from command.envelope import CommandEnvelope, compute_payload_fingerprint
from semantic_types.ids import AttemptId, CommandId, CorrelationId, EventId, WorkspaceId
from semantic_types.versions import ContractVersion, RecordVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


@dataclass(frozen=True, slots=True)
class _SamplePayload:
    note: str


def _base_kwargs(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "command_id": CommandId(uuid.uuid4()),
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
        "payload": _SamplePayload("hello"),
    }
    kwargs.update(overrides)
    return kwargs


def test_constructs_a_well_formed_envelope_with_no_targets() -> None:
    envelope = CommandEnvelope(**_base_kwargs())  # type: ignore[arg-type]
    assert envelope.command_type == "CMD_TEST_OPERATION"


def test_constructs_a_well_formed_envelope_with_targets_and_expected_versions() -> None:
    envelope = CommandEnvelope(
        **_base_kwargs(
            target_refs=("thing-a", "thing-b"),
            expected_versions={"thing-a": RecordVersion(3), "thing-b": RecordVersion(1)},
        )
    )  # type: ignore[arg-type]
    assert envelope.target_refs == ("thing-a", "thing-b")


def test_denies_event_submitted_as_command() -> None:
    """Mandatory adversarial attack: Event submitted as Command.

    `EventId` and `CommandId` are structurally distinct strong
    identities (PKG-00 semantic_types.ids: "mixing them is a semantic
    error the type system must reject"). Passing an `EventId` where a
    `command_id` is required must not silently construct a
    seemingly-valid CommandEnvelope.
    """
    kwargs = _base_kwargs(command_id=EventId(uuid.uuid4()))
    with pytest.raises(TypeError, match="command_id must be a CommandId"):
        CommandEnvelope(**kwargs)  # type: ignore[arg-type]


def test_denies_missing_expected_version_for_a_stated_target() -> None:
    """Mandatory adversarial attack: missing required expected version."""
    kwargs = _base_kwargs(target_refs=("thing-a",), expected_versions={})
    with pytest.raises(ValueError, match="expected_versions must cover exactly target_refs"):
        CommandEnvelope(**kwargs)  # type: ignore[arg-type]


def test_denies_an_orphaned_expected_version_naming_no_target() -> None:
    kwargs = _base_kwargs(target_refs=(), expected_versions={"thing-a": RecordVersion(1)})
    with pytest.raises(ValueError, match="expected_versions must cover exactly target_refs"):
        CommandEnvelope(**kwargs)  # type: ignore[arg-type]


def test_denies_a_raw_mapping_payload() -> None:
    kwargs = _base_kwargs(payload={"note": "raw dict, not a typed contract"})
    with pytest.raises(TypeError, match="must not be a raw mapping"):
        CommandEnvelope(**kwargs)  # type: ignore[arg-type]


def test_denies_empty_command_type() -> None:
    kwargs = _base_kwargs(command_type="")
    with pytest.raises(ValueError, match="command_type must be non-empty"):
        CommandEnvelope(**kwargs)  # type: ignore[arg-type]


def test_denies_non_contract_version_type() -> None:
    kwargs = _base_kwargs(command_contract_version="1.0")
    with pytest.raises(TypeError, match="command_contract_version must be a ContractVersion"):
        CommandEnvelope(**kwargs)  # type: ignore[arg-type]


def test_denies_workspace_scope_ref_that_is_not_a_workspace_id() -> None:
    kwargs = _base_kwargs(workspace_scope_ref=uuid.uuid4())
    with pytest.raises(TypeError, match="workspace_scope_ref must be a WorkspaceId"):
        CommandEnvelope(**kwargs)  # type: ignore[arg-type]


def test_payload_fingerprint_is_stable_for_equal_payloads() -> None:
    a = compute_payload_fingerprint(_SamplePayload("same"))
    b = compute_payload_fingerprint(_SamplePayload("same"))
    assert a == b


def test_payload_fingerprint_differs_for_different_payloads() -> None:
    a = compute_payload_fingerprint(_SamplePayload("one"))
    b = compute_payload_fingerprint(_SamplePayload("two"))
    assert a != b


def test_authority_context_ref_is_pure_opaque_data() -> None:
    """Mandatory adversarial attack: stale authority context reused.

    This package performs no authority resolution at all -- proving
    that changing only `authority_context_ref` between two otherwise
    identical envelopes has zero effect on construction is the
    structural half of the guarantee that a stale ref cannot be
    "reused as a reusable authorization token" (09 section 9.1). Fresh
    re-resolution is BND-014's job (PKG-13, SUCCESSOR_NOT_BUILT).
    """
    stale_ref = uuid.uuid4()
    fresh_ref = uuid.uuid4()
    stale = CommandEnvelope(**_base_kwargs(authority_context_ref=stale_ref))  # type: ignore[arg-type]
    fresh = CommandEnvelope(**_base_kwargs(authority_context_ref=fresh_ref))  # type: ignore[arg-type]
    assert stale.authority_context_ref == stale_ref
    assert fresh.authority_context_ref == fresh_ref
    # No branch anywhere in this module reads authority_context_ref to
    # decide anything -- both constructions succeed identically.
