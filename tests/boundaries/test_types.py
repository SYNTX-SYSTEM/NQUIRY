"""T4 BOUNDARY TEST: `boundaries.types` — the generic engine vocabulary.

13 §6 T4 scope: "Boundary convergence and monotonic restriction."
Pure Python -- no database, no concrete evaluator.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from authority.actor import ActorClass, ActorIdentity
from boundaries.types import (
    TERMINAL_BOUNDARY_RESULTS,
    BoundaryContext,
    BoundaryId,
    BoundaryProof,
    BoundaryResult,
)
from semantic_types.ids import CorrelationId, UserId, WorkspaceId
from semantic_types.versions import ContractVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _actor() -> ActorIdentity:
    return ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4()))


def _context(**overrides: object) -> BoundaryContext:
    defaults: dict[str, object] = {
        "workspace_id": WorkspaceId(uuid.uuid4()),
        "operation": "TEST_OPERATION",
        "actor": _actor(),
        "correlation_id": CorrelationId(uuid.uuid4()),
        "evaluated_at": _NOW,
    }
    defaults.update(overrides)
    return BoundaryContext(**defaults)  # type: ignore[arg-type]


def _proof(**overrides: object) -> BoundaryProof:
    defaults: dict[str, object] = {
        "boundary_id": BoundaryId.BND_001,
        "boundary_version": ContractVersion("1"),
        "result": BoundaryResult.ALLOW,
        "reason_code": "OK",
        "workspace_id": WorkspaceId(uuid.uuid4()),
        "actor": _actor(),
        "input_refs": (),
        "authoritative_version_refs": (),
        "authority_proof": None,
        "evidence_proof_refs": (),
        "evaluated_at": _NOW,
        "correlation_id": CorrelationId(uuid.uuid4()),
    }
    defaults.update(overrides)
    return BoundaryProof(**defaults)  # type: ignore[arg-type]


def test_boundary_id_has_exactly_the_eighteen_named_boundaries() -> None:
    """06's boundary registry names exactly 18 boundaries, BND-001
    through BND-018.
    """
    values = {b.value for b in BoundaryId}
    expected = {f"BND-{i:03d}" for i in range(1, 19)}

    assert values == expected


def test_boundary_result_is_exactly_the_four_06_values() -> None:
    """06 §2's closed 4-value result vocabulary."""
    assert {r.value for r in BoundaryResult} == {"ALLOW", "DENY", "REQUIRE", "ESCALATE"}


def test_terminal_results_are_deny_require_escalate_only() -> None:
    """06 §3: only ALLOW "permits evaluation of the next required
    boundary" -- the other three all block.
    """
    assert {
        BoundaryResult.DENY,
        BoundaryResult.REQUIRE,
        BoundaryResult.ESCALATE,
    } == TERMINAL_BOUNDARY_RESULTS
    assert BoundaryResult.ALLOW not in TERMINAL_BOUNDARY_RESULTS


def test_direct_enum_coercion_of_an_unknown_boundary_id_is_rejected() -> None:
    with pytest.raises(ValueError):
        BoundaryId("BND-019")
    with pytest.raises(ValueError):
        BoundaryId("bnd-001")  # casing is part of the vocabulary


def test_direct_enum_coercion_of_an_unknown_result_is_rejected() -> None:
    """Mandatory-category adversarial attack: direct enum coercion."""
    with pytest.raises(ValueError):
        BoundaryResult("MAYBE")
    with pytest.raises(ValueError):
        BoundaryResult("allow")


def test_boundary_context_requires_a_non_empty_operation() -> None:
    with pytest.raises(ValueError, match="operation must be non-empty"):
        _context(operation="")


def test_boundary_proof_requires_a_result_of_the_correct_type() -> None:
    """Mandatory adversarial attack: missing result. A raw string must
    not produce a proof that merely *looks* like it holds a result.
    """
    with pytest.raises(TypeError, match="result must be a BoundaryResult"):
        _proof(result="ALLOW")


def test_boundary_proof_requires_a_boundary_id_of_the_correct_type() -> None:
    with pytest.raises(TypeError, match="boundary_id must be a BoundaryId"):
        _proof(boundary_id="BND-001")


def test_boundary_proof_requires_a_non_empty_reason_code() -> None:
    """14 §15: "Free text may accompany a reason code but cannot be the
    only proof" -- the structured half (reason_code) is mandatory
    regardless.
    """
    with pytest.raises(ValueError, match="reason_code must be non-empty"):
        _proof(reason_code="")


def test_boundary_proof_requires_a_contract_version_for_boundary_version() -> None:
    with pytest.raises(TypeError, match="boundary_version must be a ContractVersion"):
        _proof(boundary_version="1")


def test_boundary_proof_is_immutable() -> None:
    """14 §3.1: `boundaries` has no canonical write capability; a
    proof is a record of one evaluation, not a mutable object.
    """
    import dataclasses

    proof = _proof()

    with pytest.raises(dataclasses.FrozenInstanceError):
        proof.result = BoundaryResult.DENY  # type: ignore[misc]


def test_boundary_proof_can_carry_no_authority_proof_where_not_applicable() -> None:
    """`authority_proof` is genuinely optional -- "where applicable"
    (14 §15). A boundary that never touches authority (e.g. a future
    BND-001 Identity evaluator) must be able to omit it honestly rather
    than fabricate one.
    """
    proof = _proof(authority_proof=None)

    assert proof.authority_proof is None


def test_allow_does_not_carry_any_stronger_meaning_than_continue() -> None:
    """06 §2.1: ALLOW "does not mean: the operation is authorized
    overall... the transition is legal overall... the operation may
    commit... the persistence write may occur." Structural proof: the
    type itself has no field or method that could be read as any of
    those stronger claims.
    """
    proof = _proof(result=BoundaryResult.ALLOW)

    forbidden_attrs = {"is_authorized", "may_commit", "is_legal", "can_write"}
    assert forbidden_attrs.isdisjoint(vars(BoundaryProof).keys())
    assert proof.result is BoundaryResult.ALLOW
