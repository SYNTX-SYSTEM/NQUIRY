"""T6 AI TEST: `ai_contracts.aiop` -- the AIOP registry. Pure Python,
no database required.
"""

from __future__ import annotations

import pytest
from ai_contracts.aiop import (
    AIOperationContract,
    AIOperationId,
    AIOperationRegistrationError,
    AIOperationRegistry,
    validate_aiop_reference,
)
from semantic_types.versions import ContractVersion


def test_all_sixteen_operation_ids_are_present_and_distinct() -> None:
    """08 section 4's own 16 named identities, each given a full
    contract in sections 23-38."""
    values = {member.value for member in AIOperationId}
    assert len(values) == 16
    assert values == {f"AIOP-{n:03d}" for n in range(1, 17)}


def test_registers_and_resolves_a_contract() -> None:
    registry = AIOperationRegistry()
    contract = AIOperationContract(
        ai_operation_id=AIOperationId.AIOP_001, contract_version=ContractVersion("1.0")
    )

    registry.register(contract)

    assert registry.get(AIOperationId.AIOP_001) is contract
    assert registry.get(AIOperationId.AIOP_002) is None


def test_registering_the_same_operation_twice_is_rejected() -> None:
    registry = AIOperationRegistry()
    registry.register(
        AIOperationContract(
            ai_operation_id=AIOperationId.AIOP_001, contract_version=ContractVersion("1.0")
        )
    )

    with pytest.raises(AIOperationRegistrationError):
        registry.register(
            AIOperationContract(
                ai_operation_id=AIOperationId.AIOP_001, contract_version=ContractVersion("1.1")
            )
        )


def test_validate_aiop_reference_accepts_an_exact_registered_match() -> None:
    registry = AIOperationRegistry()
    registry.register(
        AIOperationContract(
            ai_operation_id=AIOperationId.AIOP_001, contract_version=ContractVersion("1.0")
        )
    )

    assert (
        validate_aiop_reference(
            ai_operation_id=AIOperationId.AIOP_001,
            contract_version=ContractVersion("1.0"),
            registry=registry,
        )
        is True
    )


def test_validate_aiop_reference_rejects_an_unregistered_operation() -> None:
    """Mandatory package-specific attack: invalid contract."""
    registry = AIOperationRegistry()

    assert (
        validate_aiop_reference(
            ai_operation_id=AIOperationId.AIOP_002,
            contract_version=ContractVersion("1.0"),
            registry=registry,
        )
        is False
    )


def test_validate_aiop_reference_rejects_a_stale_or_wrong_version() -> None:
    """Mandatory package-specific attack: wrong version. A caller citing
    a genuinely-approved operation ID at a DIFFERENT version than what
    is currently registered is never silently accepted as current."""
    registry = AIOperationRegistry()
    registry.register(
        AIOperationContract(
            ai_operation_id=AIOperationId.AIOP_001, contract_version=ContractVersion("2.0")
        )
    )

    assert (
        validate_aiop_reference(
            ai_operation_id=AIOperationId.AIOP_001,
            contract_version=ContractVersion("1.0"),
            registry=registry,
        )
        is False
    )


def test_ai_operation_contract_rejects_a_non_enum_operation_id() -> None:
    with pytest.raises(TypeError):
        AIOperationContract(
            ai_operation_id="AIOP-001",  # type: ignore[arg-type]
            contract_version=ContractVersion("1.0"),
        )


def test_ai_operation_contract_rejects_a_non_contract_version() -> None:
    with pytest.raises(TypeError):
        AIOperationContract(ai_operation_id=AIOperationId.AIOP_001, contract_version="1.0")  # type: ignore[arg-type]
