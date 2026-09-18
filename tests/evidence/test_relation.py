"""T5 EVIDENCE TEST: `evidence.relation`/`persistence.evidence_repository`
-- EvidenceRelation, against real PostgreSQL where noted.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from evidence.claim_anchor import ClaimAnchor
from evidence.models import Evidence, EvidenceType, EvidenceValidationState, ProvenanceOrigin
from evidence.relation import EvidenceRelation, EvidenceRelationType
from persistence.evidence_repository import SqlAlchemyEvidenceRepository
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import ClaimAnchorId, EvidenceId, EvidenceRelationId, WorkspaceId
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    return result.workspace_id


def _seed_evidence_and_anchor(
    repo: SqlAlchemyEvidenceRepository, *, workspace_id: WorkspaceId
) -> tuple[Evidence, ClaimAnchor]:
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
    anchor = ClaimAnchor(
        claim_anchor_id=ClaimAnchorId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        target_type="Decision",
        target_id=uuid.uuid4(),
        claim_field_or_fragment="rationale",
        target_content_version=RecordVersion.initial(),
        content_fingerprint=None,
        created_at=_NOW,
    )
    repo.create_claim_anchor(anchor)
    return evidence, anchor


def _relation(
    *,
    workspace_id: WorkspaceId,
    evidence: Evidence,
    anchor: ClaimAnchor,
    relation_type: EvidenceRelationType,
    origin: ProvenanceOrigin,
    producer_ref: str,
    human_adoption_ref: uuid.UUID | None = None,
) -> EvidenceRelation:
    return EvidenceRelation(
        evidence_relation_id=EvidenceRelationId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        evidence_id=evidence.evidence_id,
        evidence_content_version=evidence.content_version,
        claim_anchor_id=anchor.claim_anchor_id,
        relation_type=relation_type,
        origin=origin,
        producer_ref=producer_ref,
        ai_generation_id=None,
        human_adoption_ref=human_adoption_ref,
        created_at=_NOW,
        record_version=RecordVersion.initial(),
    )


def test_evidence_relation_round_trip(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="relation-roundtrip@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence, anchor = _seed_evidence_and_anchor(repo, workspace_id=workspace_id)
    relation = _relation(
        workspace_id=workspace_id,
        evidence=evidence,
        anchor=anchor,
        relation_type=EvidenceRelationType.SUPPORTS,
        origin=ProvenanceOrigin.HUMAN,
        producer_ref="facilitator-1",
    )

    repo.create_evidence_relation(relation)
    fetched = repo.get_evidence_relation(relation.evidence_relation_id)

    assert fetched == relation


def test_ai_proposed_relation_defaults_to_unadopted(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: citation auto-support -- an
    AI-proposed SUPPORTS relation is stored exactly as proposed, with
    no automatic `human_adoption_ref`. 07 section 11.4: "AI may propose
    a relation. AI proposal remains derived. For consequential use, the
    relation must be adopted/accepted under the authority already
    governing the target..."
    """
    workspace_id = _bootstrap(db_connection, email="relation-ai-proposal@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence, anchor = _seed_evidence_and_anchor(repo, workspace_id=workspace_id)
    relation = _relation(
        workspace_id=workspace_id,
        evidence=evidence,
        anchor=anchor,
        relation_type=EvidenceRelationType.SUPPORTS,
        origin=ProvenanceOrigin.AI,
        producer_ref="ai-generation-service",
    )

    repo.create_evidence_relation(relation)
    fetched = repo.get_evidence_relation(relation.evidence_relation_id)

    assert fetched is not None
    assert fetched.origin is ProvenanceOrigin.AI
    assert fetched.human_adoption_ref is None


def test_source_existing_does_not_default_to_supports(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: citation auto-support, second
    shape -- creating Evidence and a ClaimAnchor creates NO
    EvidenceRelation at all by default; SUPPORTS must always be an
    explicit, separately-created relation. 07 section 9.1: "A
    resolvable source proves only: the referenced source exists or
    existed. It does not prove: the claim is supported."
    """
    workspace_id = _bootstrap(db_connection, email="relation-no-auto-support@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    _evidence, anchor = _seed_evidence_and_anchor(repo, workspace_id=workspace_id)

    relations = repo.list_relations_for_claim_anchor(anchor.claim_anchor_id)

    assert relations == ()


def test_contradictory_evidence_relations_are_both_preserved(db_connection: sa.Connection) -> None:
    """07 section 12: "Conflicting Evidence is a first-class
    architecture condition... The system must preserve both."
    """
    workspace_id = _bootstrap(db_connection, email="relation-contradiction@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence_a, anchor = _seed_evidence_and_anchor(repo, workspace_id=workspace_id)
    evidence_b = Evidence(
        evidence_id=EvidenceId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        type=EvidenceType.DOMAIN_EVIDENCE,
        content="Other users reported no drop-off at step 2.",
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
    repo.create_evidence(evidence_b)

    supports = _relation(
        workspace_id=workspace_id,
        evidence=evidence_a,
        anchor=anchor,
        relation_type=EvidenceRelationType.SUPPORTS,
        origin=ProvenanceOrigin.HUMAN,
        producer_ref="facilitator-1",
    )
    contradicts = _relation(
        workspace_id=workspace_id,
        evidence=evidence_b,
        anchor=anchor,
        relation_type=EvidenceRelationType.CONTRADICTS,
        origin=ProvenanceOrigin.HUMAN,
        producer_ref="facilitator-1",
    )
    repo.create_evidence_relation(supports)
    repo.create_evidence_relation(contradicts)

    relations = repo.list_relations_for_claim_anchor(anchor.claim_anchor_id)

    assert len(relations) == 2
    types = {r.relation_type for r in relations}
    assert types == {EvidenceRelationType.SUPPORTS, EvidenceRelationType.CONTRADICTS}


def test_cross_workspace_relation_is_not_representable(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: cross-Workspace relation."""
    workspace_a = _bootstrap(db_connection, email="relation-cross-a@nonproof.test")
    workspace_b = _bootstrap(db_connection, email="relation-cross-b@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence_a, anchor_a = _seed_evidence_and_anchor(repo, workspace_id=workspace_a)

    relation = EvidenceRelation(
        evidence_relation_id=EvidenceRelationId(_ID_GEN.new_uuid()),
        workspace_id=workspace_b,  # mismatched Workspace
        evidence_id=evidence_a.evidence_id,
        evidence_content_version=evidence_a.content_version,
        claim_anchor_id=anchor_a.claim_anchor_id,
        relation_type=EvidenceRelationType.SUPPORTS,
        origin=ProvenanceOrigin.HUMAN,
        producer_ref="facilitator-1",
        ai_generation_id=None,
        human_adoption_ref=None,
        created_at=_NOW,
        record_version=RecordVersion.initial(),
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repo.create_evidence_relation(relation)
