"""T4 BOUNDARY TEST: BND-013 Evidence Boundary, against real
PostgreSQL, wrapping the real `evidence.freshness.
resolve_evidence_set_freshness` (this package's own resolver) and
`persistence.evidence_repository.SqlAlchemyEvidenceRepository`
(PKG-16).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_013_evidence import Bnd013EvidenceEvaluator, Bnd013Input
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from evidence.evidence_set import (
    EvidenceSetMember,
    EvidenceSetReference,
    compute_evidence_set_fingerprint,
)
from evidence.freshness import resolve_evidence_set_freshness
from evidence.models import Evidence, EvidenceType, EvidenceValidationState
from persistence.evidence_repository import SqlAlchemyEvidenceRepository
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, EvidenceId, EvidenceSetId, WorkspaceId
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()
_EVALUATOR = Bnd013EvidenceEvaluator()


def _bootstrap(db_connection: sa.Connection, *, email: str) -> tuple[WorkspaceId, ActorIdentity]:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    return result.workspace_id, ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id)


def _context(*, workspace_id: WorkspaceId, actor: ActorIdentity) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=workspace_id,
        operation="CMD_TEST_EVIDENCE_DEPENDENT_OPERATION",
        actor=actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def _seed_fresh_set(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId
) -> EvidenceSetReference:
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = Evidence(
        evidence_id=EvidenceId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        type=EvidenceType.DOMAIN_EVIDENCE,
        content="Users reported drop-off at step 2.",
        source_reference_id=None,
        human_source_user_id=None,
        reliability=None,
        captured_at=_NOW,
        validation_state=EvidenceValidationState.UNVALIDATED,
        content_version=RecordVersion.initial(),
        record_version=RecordVersion.initial(),
        supersedes_evidence_id=None,
        provenance_ref=None,
    )
    repo.create_evidence(evidence)
    members = (
        EvidenceSetMember(
            evidence_id=evidence.evidence_id, content_version=evidence.content_version
        ),
    )
    evidence_set = EvidenceSetReference(
        evidence_set_ref_id=EvidenceSetId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        consumer_type="RecordHumanDecision",
        consumer_id=str(uuid.uuid4()),
        member_evidence_id_and_version_list=members,
        claim_anchor_refs=(),
        created_at=_NOW,
        fingerprint=compute_evidence_set_fingerprint(members),
    )
    repo.create_evidence_set_reference(evidence_set)
    return evidence_set


def test_allows_when_evidence_is_not_required(db_connection: sa.Connection) -> None:
    """Positive control: an operation not requiring DOMAIN_EVIDENCE is
    not vacuously denied (06 section 19 BOUNDARY PURPOSE)."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd013-not-required@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = Bnd013Input(
        boundary_id=BoundaryId.BND_013,
        context=context,
        evidence_required=False,
        evidence_set_ref_id=None,
        freshness=None,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "EVIDENCE_NOT_REQUIRED"
    assert proof.evidence_proof_refs == ()


def test_requires_an_evidence_set_when_required_but_absent(db_connection: sa.Connection) -> None:
    workspace_id, actor = _bootstrap(db_connection, email="bnd013-absent@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = Bnd013Input(
        boundary_id=BoundaryId.BND_013,
        context=context,
        evidence_required=True,
        evidence_set_ref_id=None,
        freshness=None,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.REQUIRE
    assert proof.reason_code == "EVIDENCE_SET_REQUIRED_BUT_ABSENT"


def test_allows_a_fresh_current_evidence_set(db_connection: sa.Connection) -> None:
    workspace_id, actor = _bootstrap(db_connection, email="bnd013-fresh@nonproof.test")
    evidence_set = _seed_fresh_set(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyEvidenceRepository(db_connection)
    freshness = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = Bnd013Input(
        boundary_id=BoundaryId.BND_013,
        context=context,
        evidence_required=True,
        evidence_set_ref_id=evidence_set.evidence_set_ref_id,
        freshness=freshness,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "EVIDENCE_SET_CURRENT"
    assert proof.evidence_proof_refs == (str(evidence_set.evidence_set_ref_id.value),)


def test_denies_when_the_evidence_set_no_longer_resolves(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: forged/vanished Evidence set ref."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd013-vanished-set@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    phantom_ref = EvidenceSetId(uuid.uuid4())
    freshness = resolve_evidence_set_freshness(phantom_ref, workspace_id=workspace_id, reader=repo)
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = Bnd013Input(
        boundary_id=BoundaryId.BND_013,
        context=context,
        evidence_required=True,
        evidence_set_ref_id=phantom_ref,
        freshness=freshness,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "EVIDENCE_SET_NOT_FOUND"


def test_denies_when_a_member_was_invalidated_after_prepare(db_connection: sa.Connection) -> None:
    """Mandatory package-specific attack: Evidence invalidated after
    prepare -- the same scenario `evidence.freshness`'s own test
    proves, wired through this evaluator's ALLOW/DENY vocabulary."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd013-invalidated@nonproof.test")
    evidence_set = _seed_fresh_set(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyEvidenceRepository(db_connection)
    member = evidence_set.member_evidence_id_and_version_list[0]
    repo.update_validation_state(
        evidence_id=member.evidence_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion.initial(),
        new_state=EvidenceValidationState.INVALIDATED,
    )
    freshness = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = Bnd013Input(
        boundary_id=BoundaryId.BND_013,
        context=context,
        evidence_required=True,
        evidence_set_ref_id=evidence_set.evidence_set_ref_id,
        freshness=freshness,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code.startswith("STALE_EVIDENCE:")
    assert "INVALIDATED" in proof.reason_code
    assert proof.evidence_proof_refs == ()


def test_denies_cross_workspace_evidence(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: cross-Workspace Evidence."""
    workspace_a, _ = _bootstrap(db_connection, email="bnd013-cross-a@nonproof.test")
    workspace_b, actor_b = _bootstrap(db_connection, email="bnd013-cross-b@nonproof.test")
    evidence_set = _seed_fresh_set(db_connection, workspace_id=workspace_a)
    repo = SqlAlchemyEvidenceRepository(db_connection)
    freshness = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_b, reader=repo
    )
    context = _context(workspace_id=workspace_b, actor=actor_b)
    boundary_input = Bnd013Input(
        boundary_id=BoundaryId.BND_013,
        context=context,
        evidence_required=True,
        evidence_set_ref_id=evidence_set.evidence_set_ref_id,
        freshness=freshness,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert "WRONG_WORKSPACE" in proof.reason_code


def test_freshness_must_match_the_declared_evidence_set_ref(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: a caller could try to smuggle a freshness
    verdict resolved for a DIFFERENT set than the one it declares.
    `Bnd013Input.__post_init__` rejects this at construction -- a
    mismatch can never even reach `evaluate()`.
    """
    workspace_id, actor = _bootstrap(
        db_connection, email="bnd013-mismatched-freshness@nonproof.test"
    )
    evidence_set = _seed_fresh_set(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyEvidenceRepository(db_connection)
    freshness = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )
    context = _context(workspace_id=workspace_id, actor=actor)

    try:
        Bnd013Input(
            boundary_id=BoundaryId.BND_013,
            context=context,
            evidence_required=True,
            evidence_set_ref_id=EvidenceSetId(
                uuid.uuid4()
            ),  # different ref than freshness resolved
            freshness=freshness,
        )
    except ValueError as exc:
        assert "must match" in str(exc)
    else:
        raise AssertionError("expected ValueError for mismatched freshness/evidence_set_ref_id")


def test_registers_cleanly_in_the_boundary_registry(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: prove BND-013 composes with the generic
    chain evaluator (`boundaries.registry.evaluate_chain`) exactly like
    every other boundary -- no special-casing required."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd013-chain@nonproof.test")
    evidence_set = _seed_fresh_set(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyEvidenceRepository(db_connection)
    freshness = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = Bnd013Input(
        boundary_id=BoundaryId.BND_013,
        context=context,
        evidence_required=True,
        evidence_set_ref_id=evidence_set.evidence_set_ref_id,
        freshness=freshness,
    )
    registry = BoundaryRegistry()
    registry.register(_EVALUATOR)

    chain_result = evaluate_chain(
        registry, [BoundaryId.BND_013], {BoundaryId.BND_013: boundary_input}, context
    )

    assert chain_result.is_allowed
    assert chain_result.proofs[0].reason_code == "EVIDENCE_SET_CURRENT"
