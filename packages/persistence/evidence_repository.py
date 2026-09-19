"""EvidenceRepository: the PUBLIC_INTERFACES port 14 assigns to PKG-16.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 10 (REPOSITORY PORTS):
"`EvidenceRepository`: authoritative versioned Evidence and relation
reads, governed writes."

WHY ONE REPOSITORY COVERS ALL FIVE CONSTRUCTS
------------------------------------------------------------------------
14's own port list names exactly one Evidence-related port -- no
separate `SourceReferenceRepository`/`ClaimAnchorRepository`/
`EvidenceRelationRepository`/`EvidenceSetRepository` is ever named. This
mirrors `persistence.question_repository.QuestionRepository`'s own
precedent (PKG-06), which covers both `Question` and `QuestionLineage`
under one port because 14's own port list has no separate entry for
the lineage relation either.

WHY `update_validation_state` TAKES AN `expected_record_version` GUARD
------------------------------------------------------------------------
07 section 7 (Evidence Validation Transitions) mutates an EXISTING
Evidence row's own metadata -- a real optimistic-concurrency race is
possible (two callers re-validating the same Evidence concurrently).
Mirrors `persistence.decision_repository.SqlAlchemyDecisionRepository.record_decision`'s
own guarded-UPDATE-returns-0-rows -> `EvidenceConflict` pattern exactly.

WHY `create_*` METHODS HAVE NO SUCH GUARD
------------------------------------------------------------------------
Each `create_*` method persists a brand-new row -- there is no prior
version to race against. Any race here manifests as a primary-key or
constraint violation, a real database exception this method lets
propagate directly, the same choice every other create-only method in
this codebase already makes (`SqlAlchemyQuestionSelectionRepository.create`,
`SqlAlchemyDecisionRepository.create`).

THIS REPOSITORY IS NOT ITSELF A GOVERNED CREATION PATH
------------------------------------------------------------------------
14 PKG-16 COMMANDS: NOT_APPLICABLE -- no Command is assigned to this
package (`CreateEvidenceCandidate`, 14 section 12's own named
Command, requires BND-013, which is explicitly PKG-17's own scope:
"BOUNDARIES: Prepare BND-013 facts" is this package's own, narrower
instruction). This repository is therefore a real, write-capable
persistence adapter with NO production caller yet, the same disclosed
"built but unwired" pattern `QuestionRepository` (PKG-06) and
`BurstRepository` (PKG-07, before PKG-13 wired it through
`CommitCoordinator`) already established.
"""

from __future__ import annotations

import uuid
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from evidence.claim_anchor import ClaimAnchor
from evidence.evidence_set import EvidenceSetMember, EvidenceSetReference
from evidence.models import (
    Evidence,
    EvidenceType,
    EvidenceValidationState,
    ProvenanceOrigin,
    SourceReference,
)
from evidence.relation import EvidenceRelation, EvidenceRelationType
from semantic_types.ids import (
    ClaimAnchorId,
    EvidenceId,
    EvidenceRelationId,
    EvidenceSetId,
    GenerationId,
    SourceReferenceId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion

from persistence.tables import (
    claim_anchors_table,
    evidence_relations_table,
    evidence_set_references_table,
    evidence_table,
    source_references_table,
)


class EvidenceConflict(Exception):
    """Raised by `update_validation_state` when its own
    expected-version-guarded UPDATE affects zero rows -- a race between
    a caller's fresh read and this attempt's actual write, or an
    Evidence row that does not exist at all.
    """


@runtime_checkable
class EvidenceRepository(Protocol):
    """Port: Evidence, SourceReference, ClaimAnchor, EvidenceRelation
    and EvidenceSetReference create/read, plus the one governed
    Evidence mutation 07 section 7 names (14 section 10).
    """

    def create_source_reference(self, source_reference: SourceReference) -> None: ...
    def get_source_reference(
        self, source_reference_id: SourceReferenceId
    ) -> SourceReference | None: ...

    def create_evidence(self, evidence: Evidence) -> None: ...
    def get_evidence(self, evidence_id: EvidenceId) -> Evidence | None: ...

    def update_validation_state(
        self,
        *,
        evidence_id: EvidenceId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        new_state: EvidenceValidationState,
        reliability: str | None = None,
    ) -> None:
        """07 section 7's own transition table. Raises
        `EvidenceConflict` if `expected_record_version` no longer
        matches the stored row (including "no such row")."""
        ...

    def create_claim_anchor(self, claim_anchor: ClaimAnchor) -> None: ...
    def get_claim_anchor(self, claim_anchor_id: ClaimAnchorId) -> ClaimAnchor | None: ...

    def create_evidence_relation(self, relation: EvidenceRelation) -> None: ...
    def get_evidence_relation(
        self, evidence_relation_id: EvidenceRelationId
    ) -> EvidenceRelation | None: ...
    def list_relations_for_claim_anchor(
        self, claim_anchor_id: ClaimAnchorId
    ) -> tuple[EvidenceRelation, ...]: ...

    def create_evidence_set_reference(self, evidence_set: EvidenceSetReference) -> None: ...
    def get_evidence_set_reference(
        self, evidence_set_ref_id: EvidenceSetId
    ) -> EvidenceSetReference | None: ...

    def find_superseding_evidence_id(self, evidence_id: EvidenceId) -> EvidenceId | None:
        """PKG-17 addition (`evidence.freshness.EvidenceFreshnessPort`):
        does any current Evidence row declare `supersedes_evidence_id`
        pointing at `evidence_id`? A read-only query over the existing
        `evidence` table/column (PKG-16) -- no schema change (14 PKG-17
        DATABASE_CHANGES: none)."""
        ...


class SqlAlchemyEvidenceRepository:
    """`EvidenceRepository` backed by `source_references`/`evidence`/
    `claim_anchors`/`evidence_relations`/`evidence_set_references` via
    a SQLAlchemy Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create_source_reference(self, source_reference: SourceReference) -> None:
        self._connection.execute(
            sa.insert(source_references_table).values(**_source_reference_to_row(source_reference))
        )

    def get_source_reference(
        self, source_reference_id: SourceReferenceId
    ) -> SourceReference | None:
        stmt = sa.select(source_references_table).where(
            source_references_table.c.id == source_reference_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _source_reference_from_row(row)

    def create_evidence(self, evidence: Evidence) -> None:
        self._connection.execute(sa.insert(evidence_table).values(**_evidence_to_row(evidence)))

    def get_evidence(self, evidence_id: EvidenceId) -> Evidence | None:
        stmt = sa.select(evidence_table).where(evidence_table.c.id == evidence_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _evidence_from_row(row)

    def update_validation_state(
        self,
        *,
        evidence_id: EvidenceId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        new_state: EvidenceValidationState,
        reliability: str | None = None,
    ) -> None:
        values: dict[str, object] = {
            "validation_state": new_state.value,
            "record_version": expected_record_version.next().value,
        }
        if reliability is not None:
            values["reliability"] = reliability
        result = self._connection.execute(
            sa.update(evidence_table)
            .where(
                evidence_table.c.id == evidence_id.value,
                evidence_table.c.workspace_id == workspace_id.value,
                evidence_table.c.record_version == expected_record_version.value,
            )
            .values(**values)
        )
        if result.rowcount == 0:
            raise EvidenceConflict(
                f"evidence {evidence_id!r} not found at workspace {workspace_id!r} with "
                f"expected record_version {expected_record_version.value}"
            )

    def create_claim_anchor(self, claim_anchor: ClaimAnchor) -> None:
        self._connection.execute(
            sa.insert(claim_anchors_table).values(**_claim_anchor_to_row(claim_anchor))
        )

    def get_claim_anchor(self, claim_anchor_id: ClaimAnchorId) -> ClaimAnchor | None:
        stmt = sa.select(claim_anchors_table).where(
            claim_anchors_table.c.id == claim_anchor_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _claim_anchor_from_row(row)

    def create_evidence_relation(self, relation: EvidenceRelation) -> None:
        self._connection.execute(
            sa.insert(evidence_relations_table).values(**_relation_to_row(relation))
        )

    def get_evidence_relation(
        self, evidence_relation_id: EvidenceRelationId
    ) -> EvidenceRelation | None:
        stmt = sa.select(evidence_relations_table).where(
            evidence_relations_table.c.id == evidence_relation_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _relation_from_row(row)

    def list_relations_for_claim_anchor(
        self, claim_anchor_id: ClaimAnchorId
    ) -> tuple[EvidenceRelation, ...]:
        stmt = (
            sa.select(evidence_relations_table)
            .where(evidence_relations_table.c.claim_anchor_id == claim_anchor_id.value)
            .order_by(evidence_relations_table.c.created_at)
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_relation_from_row(row) for row in rows)

    def create_evidence_set_reference(self, evidence_set: EvidenceSetReference) -> None:
        self._connection.execute(
            sa.insert(evidence_set_references_table).values(**_evidence_set_to_row(evidence_set))
        )

    def get_evidence_set_reference(
        self, evidence_set_ref_id: EvidenceSetId
    ) -> EvidenceSetReference | None:
        stmt = sa.select(evidence_set_references_table).where(
            evidence_set_references_table.c.id == evidence_set_ref_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _evidence_set_from_row(row)

    def find_superseding_evidence_id(self, evidence_id: EvidenceId) -> EvidenceId | None:
        stmt = sa.select(evidence_table.c.id).where(
            evidence_table.c.supersedes_evidence_id == evidence_id.value
        )
        row = self._connection.execute(stmt).first()
        return None if row is None else EvidenceId(row[0])


def _source_reference_to_row(source_reference: SourceReference) -> dict[str, object]:
    return {
        "id": source_reference.source_reference_id.value,
        "workspace_id": source_reference.workspace_id.value,
        "source_type": source_reference.source_type,
        "locator": source_reference.locator,
        "external_id": source_reference.external_id,
        "title": source_reference.title,
        "retrieved_at": source_reference.retrieved_at,
        "source_published_at": source_reference.source_published_at,
        "content_fingerprint": source_reference.content_fingerprint,
        "snapshot_ref": source_reference.snapshot_ref,
        "created_by_ref": source_reference.created_by_ref,
        "origin": source_reference.origin.value,
        "validation_status": source_reference.validation_status,
        "created_at": source_reference.created_at,
        "record_version": source_reference.record_version.value,
    }


def _source_reference_from_row(row: sa.RowMapping) -> SourceReference:
    return SourceReference(
        source_reference_id=SourceReferenceId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        source_type=row["source_type"],
        locator=row["locator"],
        external_id=row["external_id"],
        title=row["title"],
        retrieved_at=row["retrieved_at"],
        source_published_at=row["source_published_at"],
        content_fingerprint=row["content_fingerprint"],
        snapshot_ref=row["snapshot_ref"],
        created_by_ref=row["created_by_ref"],
        origin=ProvenanceOrigin(row["origin"]),
        validation_status=row["validation_status"],
        created_at=row["created_at"],
        record_version=RecordVersion(row["record_version"]),
    )


def _evidence_to_row(evidence: Evidence) -> dict[str, object]:
    return {
        "id": evidence.evidence_id.value,
        "workspace_id": evidence.workspace_id.value,
        "type": evidence.type.value,
        "content": evidence.content,
        "source_reference_id": (
            None if evidence.source_reference_id is None else evidence.source_reference_id.value
        ),
        "human_source_user_id": (
            None if evidence.human_source_user_id is None else evidence.human_source_user_id.value
        ),
        "reliability": evidence.reliability,
        "captured_at": evidence.captured_at,
        "validation_state": evidence.validation_state.value,
        "content_version": evidence.content_version.value,
        "record_version": evidence.record_version.value,
        "supersedes_evidence_id": (
            None
            if evidence.supersedes_evidence_id is None
            else evidence.supersedes_evidence_id.value
        ),
        "provenance_ref": evidence.provenance_ref,
    }


def _evidence_from_row(row: sa.RowMapping) -> Evidence:
    return Evidence(
        evidence_id=EvidenceId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        type=EvidenceType(row["type"]),
        content=row["content"],
        source_reference_id=(
            None
            if row["source_reference_id"] is None
            else SourceReferenceId(row["source_reference_id"])
        ),
        human_source_user_id=(
            None if row["human_source_user_id"] is None else UserId(row["human_source_user_id"])
        ),
        reliability=row["reliability"],
        captured_at=row["captured_at"],
        validation_state=EvidenceValidationState(row["validation_state"]),
        content_version=RecordVersion(row["content_version"]),
        record_version=RecordVersion(row["record_version"]),
        supersedes_evidence_id=(
            None
            if row["supersedes_evidence_id"] is None
            else EvidenceId(row["supersedes_evidence_id"])
        ),
        provenance_ref=row["provenance_ref"],
    )


def _claim_anchor_to_row(claim_anchor: ClaimAnchor) -> dict[str, object]:
    return {
        "id": claim_anchor.claim_anchor_id.value,
        "workspace_id": claim_anchor.workspace_id.value,
        "target_type": claim_anchor.target_type,
        "target_id": claim_anchor.target_id,
        "claim_field_or_fragment": claim_anchor.claim_field_or_fragment,
        "target_content_version": claim_anchor.target_content_version.value,
        "content_fingerprint": claim_anchor.content_fingerprint,
        "created_at": claim_anchor.created_at,
    }


def _claim_anchor_from_row(row: sa.RowMapping) -> ClaimAnchor:
    return ClaimAnchor(
        claim_anchor_id=ClaimAnchorId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        target_type=row["target_type"],
        target_id=row["target_id"],
        claim_field_or_fragment=row["claim_field_or_fragment"],
        target_content_version=RecordVersion(row["target_content_version"]),
        content_fingerprint=row["content_fingerprint"],
        created_at=row["created_at"],
    )


def _relation_to_row(relation: EvidenceRelation) -> dict[str, object]:
    return {
        "id": relation.evidence_relation_id.value,
        "workspace_id": relation.workspace_id.value,
        "evidence_id": relation.evidence_id.value,
        "evidence_content_version": relation.evidence_content_version.value,
        "claim_anchor_id": relation.claim_anchor_id.value,
        "relation_type": relation.relation_type.value,
        "origin": relation.origin.value,
        "producer_ref": relation.producer_ref,
        "ai_generation_id": (
            None if relation.ai_generation_id is None else relation.ai_generation_id.value
        ),
        "human_adoption_ref": relation.human_adoption_ref,
        "created_at": relation.created_at,
        "record_version": relation.record_version.value,
    }


def _relation_from_row(row: sa.RowMapping) -> EvidenceRelation:
    return EvidenceRelation(
        evidence_relation_id=EvidenceRelationId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        evidence_id=EvidenceId(row["evidence_id"]),
        evidence_content_version=RecordVersion(row["evidence_content_version"]),
        claim_anchor_id=ClaimAnchorId(row["claim_anchor_id"]),
        relation_type=EvidenceRelationType(row["relation_type"]),
        origin=ProvenanceOrigin(row["origin"]),
        producer_ref=row["producer_ref"],
        ai_generation_id=(
            None if row["ai_generation_id"] is None else GenerationId(row["ai_generation_id"])
        ),
        human_adoption_ref=row["human_adoption_ref"],
        created_at=row["created_at"],
        record_version=RecordVersion(row["record_version"]),
    )


def _evidence_set_to_row(evidence_set: EvidenceSetReference) -> dict[str, object]:
    return {
        "id": evidence_set.evidence_set_ref_id.value,
        "workspace_id": evidence_set.workspace_id.value,
        "consumer_type": evidence_set.consumer_type,
        "consumer_id": evidence_set.consumer_id,
        "member_evidence_id_and_version_list": [
            {
                "evidence_id": str(member.evidence_id.value),
                "content_version": member.content_version.value,
            }
            for member in evidence_set.member_evidence_id_and_version_list
        ],
        "claim_anchor_refs": [ref.value for ref in evidence_set.claim_anchor_refs],
        "created_at": evidence_set.created_at,
        "fingerprint": evidence_set.fingerprint,
    }


def _evidence_set_from_row(row: sa.RowMapping) -> EvidenceSetReference:
    return EvidenceSetReference(
        evidence_set_ref_id=EvidenceSetId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        consumer_type=row["consumer_type"],
        consumer_id=row["consumer_id"],
        member_evidence_id_and_version_list=tuple(
            EvidenceSetMember(
                evidence_id=EvidenceId(_as_uuid(member["evidence_id"])),
                content_version=RecordVersion(member["content_version"]),
            )
            for member in row["member_evidence_id_and_version_list"]
        ),
        claim_anchor_refs=tuple(ClaimAnchorId(ref) for ref in (row["claim_anchor_refs"] or ())),
        created_at=row["created_at"],
        fingerprint=row["fingerprint"],
    )


def _as_uuid(value: object) -> uuid.UUID:
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


__all__ = ["EvidenceConflict", "EvidenceRepository", "SqlAlchemyEvidenceRepository"]
