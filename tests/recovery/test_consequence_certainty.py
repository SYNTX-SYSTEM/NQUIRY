"""T8 CONSEQUENCE CERTAINTY TEST: ConsequenceCertainty/
ConsequenceCertaintyInput/resolve_consequence_certainty, pure except
one cross-layer test against real PostgreSQL.

14 section 48's own PKG-22 scope: `packages/recovery/certainty.py`.
"""

from __future__ import annotations

import dataclasses
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from command.envelope import CommandEnvelope, CommandOutcome
from commit.coordinator import CommitOutcome, CommitUnit
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from recovery.certainty import (
    ConsequenceCertainty,
    ConsequenceCertaintyInput,
    ExternalConsequenceProofState,
    resolve_consequence_certainty,
)
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import AttemptId, CommandId, CommitId, CorrelationId, WorkspaceId
from semantic_types.versions import ContractVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()

_NOT_APPLICABLE = ExternalConsequenceProofState.NOT_APPLICABLE

_FULLY_PROVEN_COMMITTED = ConsequenceCertaintyInput(
    command_outcome=CommandOutcome.COMMITTED,
    commit_outcome=CommitOutcome.COMMITTED,
    commit_unit_found=True,
    canonical_version_confirmed_after_commit=True,
    governance_state_confirmed=True,
    audit_record_durable=True,
    outbox_record_durable=True,
    external_consequence_proof=_NOT_APPLICABLE,
)


def test_consequence_certainty_is_exactly_the_7_named_values() -> None:
    """Regression guard on 10 section 5's own closed vocabulary."""
    assert {member.value for member in ConsequenceCertainty} == {
        "PROVEN_COMMITTED",
        "PROVEN_NOT_COMMITTED",
        "EXTERNAL_CONSEQUENCE_PROVEN",
        "EXTERNAL_CONSEQUENCE_PROVEN_ABSENT",
        "EXTERNAL_CONSEQUENCE_UNKNOWN",
        "CANONICAL_STATE_UNKNOWN",
        "GOVERNANCE_STATE_UNKNOWN",
    }


def test_fully_confirmed_commit_is_proven_committed() -> None:
    assert (
        resolve_consequence_certainty(_FULLY_PROVEN_COMMITTED)
        is ConsequenceCertainty.PROVEN_COMMITTED
    )


def test_denied_command_is_proven_not_committed() -> None:
    certainty_input = dataclasses.replace(
        _FULLY_PROVEN_COMMITTED,
        command_outcome=CommandOutcome.DENIED,
        commit_outcome=None,
        commit_unit_found=None,
        canonical_version_confirmed_after_commit=None,
    )
    assert (
        resolve_consequence_certainty(certainty_input) is ConsequenceCertainty.PROVEN_NOT_COMMITTED
    )


def test_failed_precommit_with_confirmed_absence_is_proven_not_committed() -> None:
    certainty_input = dataclasses.replace(
        _FULLY_PROVEN_COMMITTED,
        command_outcome=CommandOutcome.FAILED_PRECOMMIT,
        commit_outcome=CommitOutcome.FAILED_PRECOMMIT,
        commit_unit_found=False,
        canonical_version_confirmed_after_commit=None,
    )
    assert (
        resolve_consequence_certainty(certainty_input) is ConsequenceCertainty.PROVEN_NOT_COMMITTED
    )


def test_failed_precommit_without_confirmed_absence_is_unknown() -> None:
    """Mandatory adversarial attacks: timeout before commit; DB
    exception; ambiguous connection loss. A FAILED_PRECOMMIT outcome
    alone, with the existence of a CommitUnit genuinely unverified
    (`commit_unit_found is None`), must NOT be over-claimed as proof of
    non-commit (10 section 5: "database row present != legitimate
    commit" cuts both ways -- absence of proof is not proof of
    absence either).
    """
    certainty_input = dataclasses.replace(
        _FULLY_PROVEN_COMMITTED,
        command_outcome=CommandOutcome.FAILED_PRECOMMIT,
        commit_outcome=CommitOutcome.FAILED_PRECOMMIT,
        commit_unit_found=None,
        canonical_version_confirmed_after_commit=None,
    )
    assert (
        resolve_consequence_certainty(certainty_input)
        is ConsequenceCertainty.CANONICAL_STATE_UNKNOWN
    )


def test_indeterminate_commit_outcome_is_never_proven_either_way() -> None:
    """P-20: INDETERMINATE blocks blind retry. This resolver's own
    contribution: an INDETERMINATE `CommitOutcome` must never resolve
    to `PROVEN_COMMITTED` or `PROVEN_NOT_COMMITTED`, even if some other
    fields happen to look positive -- laundering INDETERMINATE into a
    false certainty is exactly what would make a downstream blind
    retry look safe.
    """
    certainty_input = dataclasses.replace(
        _FULLY_PROVEN_COMMITTED,
        commit_outcome=CommitOutcome.INDETERMINATE,
    )
    assert (
        resolve_consequence_certainty(certainty_input)
        is ConsequenceCertainty.CANONICAL_STATE_UNKNOWN
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "commit_unit_found",
        "canonical_version_confirmed_after_commit",
        "governance_state_confirmed",
    ],
)
def test_removing_one_required_proof_link_falls_back_to_unknown(field_name: str) -> None:
    """P-25's own mandatory attack: "remove one required proof link."
    An otherwise-fully-proven commit must stop being `PROVEN_COMMITTED`
    the instant exactly one required field regresses to unverified.
    """
    certainty_input = dataclasses.replace(_FULLY_PROVEN_COMMITTED, **{field_name: None})
    assert (
        resolve_consequence_certainty(certainty_input) is not ConsequenceCertainty.PROVEN_COMMITTED
    )


def test_governance_state_explicitly_unconfirmed_is_its_own_classification() -> None:
    certainty_input = dataclasses.replace(_FULLY_PROVEN_COMMITTED, governance_state_confirmed=False)
    assert (
        resolve_consequence_certainty(certainty_input)
        is ConsequenceCertainty.GOVERNANCE_STATE_UNKNOWN
    )


def test_missing_audit_or_outbox_does_not_downgrade_an_otherwise_proven_commit() -> None:
    """Mandatory adversarial attacks: missing projection; missing
    delivery. 10 section 5: "event missing != canonical non-commit";
    "audit projection missing != audit record absent." A commit already
    fully proven by its own required chain stays `PROVEN_COMMITTED`
    even when audit/outbox durability is unconfirmed.
    """
    certainty_input = dataclasses.replace(
        _FULLY_PROVEN_COMMITTED, audit_record_durable=None, outbox_record_durable=False
    )
    assert resolve_consequence_certainty(certainty_input) is ConsequenceCertainty.PROVEN_COMMITTED


@pytest.mark.parametrize(
    ("proof_state", "expected"),
    [
        (ExternalConsequenceProofState.PROVEN, ConsequenceCertainty.EXTERNAL_CONSEQUENCE_PROVEN),
        (
            ExternalConsequenceProofState.PROVEN_ABSENT,
            ConsequenceCertainty.EXTERNAL_CONSEQUENCE_PROVEN_ABSENT,
        ),
        (ExternalConsequenceProofState.UNKNOWN, ConsequenceCertainty.EXTERNAL_CONSEQUENCE_UNKNOWN),
    ],
)
def test_external_consequence_dimension_maps_directly(
    proof_state: ExternalConsequenceProofState, expected: ConsequenceCertainty
) -> None:
    certainty_input = ConsequenceCertaintyInput(
        command_outcome=None,
        commit_outcome=None,
        commit_unit_found=None,
        canonical_version_confirmed_after_commit=None,
        governance_state_confirmed=None,
        audit_record_durable=None,
        outbox_record_durable=None,
        external_consequence_proof=proof_state,
    )
    assert resolve_consequence_certainty(certainty_input) is expected


def test_ambiguous_connection_loss_is_canonical_state_unknown() -> None:
    """Mandatory adversarial attack: ambiguous connection loss. Nothing
    was positively confirmed either way -- the only honest answer is
    the explicitly uncertain default, never a guess.
    """
    certainty_input = ConsequenceCertaintyInput(
        command_outcome=None,
        commit_outcome=None,
        commit_unit_found=None,
        canonical_version_confirmed_after_commit=None,
        governance_state_confirmed=None,
        audit_record_durable=None,
        outbox_record_durable=None,
        external_consequence_proof=_NOT_APPLICABLE,
    )
    assert (
        resolve_consequence_certainty(certainty_input)
        is ConsequenceCertainty.CANONICAL_STATE_UNKNOWN
    )


def test_consequence_certainty_input_has_no_raw_technical_event_field() -> None:
    """Mirrors `FailureSignals`' own structural proof: no field on
    `ConsequenceCertaintyInput` represents a raw technical event, a
    projection row, or a cache -- only positively-verifiable canonical/
    governance/external facts.
    """
    forbidden_substrings = (
        "timeout",
        "timed_out",
        "exception",
        "disconnect",
        "connection",
        "projection",
        "cache",
    )
    for field in dataclasses.fields(ConsequenceCertaintyInput):
        for forbidden in forbidden_substrings:
            assert forbidden not in field.name.lower(), field.name


@dataclass(frozen=True, slots=True)
class _Payload:
    note: str


def _workspace(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    return bootstrap.seed(owner_email=email).workspace_id


def test_certainty_resolved_from_a_real_committed_commit_unit(db_connection: sa.Connection) -> None:
    """Cross-layer proof: this resolver's own `commit_outcome`/
    `commit_unit_found` inputs are fed from a REAL, live-PostgreSQL
    `CommitUnit` read through the real `SqlAlchemyCommitRepository`
    (PKG-13), not a synthetic fixture value.
    """
    workspace_id = _workspace(db_connection, email="recovery-certainty-crosslayer@nonproof.test")
    command_id = CommandId(uuid.uuid4())
    attempt_id = AttemptId(uuid.uuid4())
    SqlAlchemyCommandRepository(db_connection).record_attempt(
        CommandEnvelope(
            command_id=command_id,
            command_type="CMD_TEST_OPERATION",
            command_contract_version=ContractVersion("1.0"),
            attempt_id=attempt_id,
            correlation_id=CorrelationId(uuid.uuid4()),
            requested_at=_NOW,
            requesting_actor_type="HUMAN_USER",
            requesting_actor_id="user-ref-1",
            workspace_scope_ref=workspace_id,
            target_refs=(),
            expected_versions={},
            payload=_Payload("hello"),
        ),
        received_at=_NOW,
    )
    commit_id = CommitId(uuid.uuid4())
    commit_repo = SqlAlchemyCommitRepository(db_connection)
    commit_repo.append(
        CommitUnit(
            commit_id=commit_id,
            command_id=command_id,
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            target_refs=(),
            relation_refs=(),
            governance_refs=(),
            audit_event_ids=(),
            outbox_ids=(),
            committed_at=_NOW,
            outcome=CommitOutcome.COMMITTED,
        )
    )

    real_commit_unit = commit_repo.get(commit_id)
    assert real_commit_unit is not None

    certainty_input = ConsequenceCertaintyInput(
        command_outcome=CommandOutcome.COMMITTED,
        commit_outcome=real_commit_unit.outcome,
        commit_unit_found=True,
        canonical_version_confirmed_after_commit=True,
        governance_state_confirmed=True,
        audit_record_durable=None,
        outbox_record_durable=None,
        external_consequence_proof=_NOT_APPLICABLE,
    )
    assert resolve_consequence_certainty(certainty_input) is ConsequenceCertainty.PROVEN_COMMITTED
