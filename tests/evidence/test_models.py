"""T5 EVIDENCE TEST: `evidence.models`/`persistence.evidence_repository`
-- Evidence and SourceReference, against real PostgreSQL where noted.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from evidence.models import (
    Evidence,
    EvidenceType,
    EvidenceValidationState,
    ProvenanceOrigin,
    SourceReference,
    is_legal_validation_transition,
)
from persistence.evidence_repository import EvidenceConflict, SqlAlchemyEvidenceRepository
from persistence.tables import evidence_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import EvidenceId, SourceReferenceId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap(db_connection: sa.Connection, *, email: str) -> tuple[WorkspaceId, UserId]:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    return result.workspace_id, result.owner_user_id


def _system_evidence(
    *, workspace_id: WorkspaceId, evidence_id: EvidenceId | None = None
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id or EvidenceId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        type=EvidenceType.SYSTEM_PROOF,
        content="Session S1 currently has 2 active Question Burst members.",
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


# --- Pure Python construction ---------------------------------------


def test_constructs_a_well_formed_system_proof_evidence() -> None:
    evidence = _system_evidence(workspace_id=WorkspaceId(uuid.uuid4()))
    assert evidence.type is EvidenceType.SYSTEM_PROOF
    assert evidence.validation_state is EvidenceValidationState.UNVALIDATED


def test_denies_evidence_superseding_itself() -> None:
    """Mandatory-category adversarial attack: semantic shortcut --
    self-supersession would let a single row claim to correct itself
    without a real new identity, defeating AC-07-001.
    """
    evidence_id = EvidenceId(_ID_GEN.new_uuid())
    workspace_id = WorkspaceId(uuid.uuid4())
    with pytest.raises(ValueError, match="cannot supersede itself"):
        Evidence(
            evidence_id=evidence_id,
            workspace_id=workspace_id,
            type=EvidenceType.DOMAIN_EVIDENCE,
            content="Some observation",
            source_reference_id=None,
            human_source_user_id=None,
            reliability=None,
            captured_at=_NOW,
            validation_state=EvidenceValidationState.UNVALIDATED,
            content_version=RecordVersion.initial(),
            record_version=RecordVersion.initial(),
            supersedes_evidence_id=evidence_id,
            provenance_ref=None,
        )


def test_evidence_has_no_confidence_field() -> None:
    """Mandatory adversarial attack: AI confidence cast as Evidence --
    proven structurally: `Evidence`'s own field list (09 section 41)
    has no `confidence`/`score` field of any kind to smuggle a model's
    own confidence value into. `reliability` is the only adjacent
    field, and it is a plain optional string (LEVEL 1's own field, not
    a universal sufficiency threshold -- 07 section 13.1).
    """
    field_names = {f for f in Evidence.__dataclass_fields__}
    assert "confidence" not in field_names
    assert "score" not in field_names
    assert "reliability" in field_names


def test_evidence_validation_state_is_not_truth() -> None:
    """Mandatory adversarial attack: structural validity treated as
    truth -- `STRUCTURALLY_VALID` construction succeeds regardless of
    `content`'s actual truth value; this package has no "is_true" field
    or method anywhere, structurally proving 07 section 6.2's own "does
    not mean: true" statement.
    """
    evidence = Evidence(
        evidence_id=EvidenceId(_ID_GEN.new_uuid()),
        workspace_id=WorkspaceId(uuid.uuid4()),
        type=EvidenceType.DOMAIN_EVIDENCE,
        content="The moon is made of cheese.",
        source_reference_id=None,
        human_source_user_id=None,
        reliability=None,
        captured_at=_NOW,
        validation_state=EvidenceValidationState.STRUCTURALLY_VALID,
        content_version=RecordVersion.initial(),
        record_version=RecordVersion.initial(),
        supersedes_evidence_id=None,
        provenance_ref=None,
    )
    assert evidence.validation_state is EvidenceValidationState.STRUCTURALLY_VALID
    assert not hasattr(evidence, "is_true")
    assert not hasattr(evidence, "truth")


def test_evidence_package_never_imports_authority() -> None:
    """Mandatory adversarial attack: Evidence treated as authority --
    structurally impossible: `evidence` package's own allowed
    dependencies (14 section 3.1) are `domain, semantic_types` only,
    which excludes `authority` entirely. This module holds no
    AuthorityResolver, no AuthorityRequest, and calls no resolution of
    any kind.
    """
    import evidence.models as models_module

    assert "authority" not in models_module.__dict__
    with open(models_module.__file__, encoding="utf-8") as handle:
        source = handle.read()
    assert "import authority" not in source


@pytest.mark.parametrize(
    ("current", "target", "expected"),
    [
        (EvidenceValidationState.UNVALIDATED, EvidenceValidationState.STRUCTURALLY_VALID, True),
        (EvidenceValidationState.UNVALIDATED, EvidenceValidationState.INVALIDATED, True),
        (EvidenceValidationState.UNVALIDATED, EvidenceValidationState.UNAVAILABLE, True),
        (EvidenceValidationState.STRUCTURALLY_VALID, EvidenceValidationState.INVALIDATED, True),
        (EvidenceValidationState.STRUCTURALLY_VALID, EvidenceValidationState.UNAVAILABLE, True),
        (EvidenceValidationState.UNAVAILABLE, EvidenceValidationState.STRUCTURALLY_VALID, True),
        (EvidenceValidationState.UNAVAILABLE, EvidenceValidationState.INVALIDATED, True),
        (EvidenceValidationState.INVALIDATED, EvidenceValidationState.STRUCTURALLY_VALID, False),
        (EvidenceValidationState.STRUCTURALLY_VALID, EvidenceValidationState.UNVALIDATED, False),
    ],
)
def test_validation_transition_topology(
    current: EvidenceValidationState, target: EvidenceValidationState, expected: bool
) -> None:
    assert is_legal_validation_transition(current, target) is expected


# --- Live PostgreSQL persistence proof -------------------------------


def test_evidence_created_outside_unvalidated_is_rejected(db_connection: sa.Connection) -> None:
    workspace_id, _owner = _bootstrap(db_connection, email="evidence-open-bad@nonproof.test")

    with (
        pytest.raises(sa.exc.DBAPIError, match="must be created in UNVALIDATED"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.insert(evidence_table).values(
                id=_ID_GEN.new_uuid(),
                workspace_id=workspace_id.value,
                type="DOMAIN_EVIDENCE",
                content="x",
                source_reference_id=None,
                human_source_user_id=None,
                reliability=None,
                captured_at=_NOW,
                validation_state="STRUCTURALLY_VALID",
                content_version=1,
                record_version=1,
                supersedes_evidence_id=None,
                provenance_ref=None,
            )
        )


def test_full_round_trip_create_and_get(db_connection: sa.Connection) -> None:
    workspace_id, owner = _bootstrap(db_connection, email="evidence-roundtrip@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = Evidence(
        evidence_id=EvidenceId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        type=EvidenceType.DOMAIN_EVIDENCE,
        content="Users reported drop-off at step 2 during interviews.",
        source_reference_id=None,
        human_source_user_id=owner,
        reliability="medium",
        captured_at=_NOW,
        validation_state=EvidenceValidationState.UNVALIDATED,
        content_version=RecordVersion.initial(),
        record_version=RecordVersion.initial(),
        supersedes_evidence_id=None,
        provenance_ref=None,
    )

    repo.create_evidence(evidence)
    fetched = repo.get_evidence(evidence.evidence_id)

    assert fetched == evidence


def test_update_validation_state_advances_legally(db_connection: sa.Connection) -> None:
    workspace_id, _owner = _bootstrap(db_connection, email="evidence-advance@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _system_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)

    repo.update_validation_state(
        evidence_id=evidence.evidence_id,
        workspace_id=workspace_id,
        expected_record_version=evidence.record_version,
        new_state=EvidenceValidationState.STRUCTURALLY_VALID,
    )

    fetched = repo.get_evidence(evidence.evidence_id)
    assert fetched is not None
    assert fetched.validation_state is EvidenceValidationState.STRUCTURALLY_VALID
    assert fetched.record_version == RecordVersion(2)


def test_illegal_validation_transition_is_rejected_at_the_database_layer(
    db_connection: sa.Connection,
) -> None:
    workspace_id, _owner = _bootstrap(db_connection, email="evidence-illegal@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _system_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)
    repo.update_validation_state(
        evidence_id=evidence.evidence_id,
        workspace_id=workspace_id,
        expected_record_version=evidence.record_version,
        new_state=EvidenceValidationState.INVALIDATED,
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="illegal evidence validation transition"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(evidence_table)
            .where(evidence_table.c.id == evidence.evidence_id.value)
            .values(validation_state="STRUCTURALLY_VALID", record_version=3)
        )


def test_invalidated_is_terminal_not_silently_reversible(db_connection: sa.Connection) -> None:
    """07 section 7: "INVALIDATED is not silently returned to
    STRUCTURALLY_VALID."
    """
    workspace_id, _owner = _bootstrap(db_connection, email="evidence-terminal@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _system_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)
    repo.update_validation_state(
        evidence_id=evidence.evidence_id,
        workspace_id=workspace_id,
        expected_record_version=evidence.record_version,
        new_state=EvidenceValidationState.INVALIDATED,
    )

    with pytest.raises(sa.exc.DBAPIError, match="illegal evidence validation transition"):
        repo.update_validation_state(
            evidence_id=evidence.evidence_id,
            workspace_id=workspace_id,
            expected_record_version=RecordVersion(2),
            new_state=EvidenceValidationState.STRUCTURALLY_VALID,
        )
    # The record_version supplied here is genuinely current (matches
    # the row after the first update) -- `update_validation_state`'s
    # own guard therefore matches, and the UPDATE reaches the DB
    # trigger, which refuses the pair itself. This proves the trigger
    # is the real, load-bearing defense here, not merely the
    # repository's own version guard.


def test_content_fields_are_immutable_once_captured(db_connection: sa.Connection) -> None:
    """AC-07-001: exact consumed content must remain reconstructable --
    proven by attempting to rewrite `content` directly via raw SQL.
    """
    workspace_id, _owner = _bootstrap(
        db_connection, email="evidence-immutable-content@nonproof.test"
    )
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _system_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)

    with (
        pytest.raises(sa.exc.DBAPIError, match="immutable once captured"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(evidence_table)
            .where(evidence_table.c.id == evidence.evidence_id.value)
            .values(content="a rewritten claim", record_version=2)
        )


def test_evidence_conflict_raised_on_stale_expected_version(db_connection: sa.Connection) -> None:
    """Mandatory-category persistence/concurrency attack."""
    workspace_id, _owner = _bootstrap(db_connection, email="evidence-stale@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _system_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)

    with pytest.raises(EvidenceConflict):
        repo.update_validation_state(
            evidence_id=evidence.evidence_id,
            workspace_id=workspace_id,
            expected_record_version=RecordVersion(99),
            new_state=EvidenceValidationState.STRUCTURALLY_VALID,
        )


def test_cross_workspace_supersession_is_not_representable(db_connection: sa.Connection) -> None:
    """Mandatory-category Workspace attack, Evidence supersession
    variant.
    """
    workspace_a, _owner_a = _bootstrap(db_connection, email="evidence-cross-a@nonproof.test")
    workspace_b, _owner_b = _bootstrap(db_connection, email="evidence-cross-b@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    original = _system_evidence(workspace_id=workspace_a)
    repo.create_evidence(original)

    superseding = Evidence(
        evidence_id=EvidenceId(_ID_GEN.new_uuid()),
        workspace_id=workspace_b,
        type=EvidenceType.SYSTEM_PROOF,
        content="a corrected claim",
        source_reference_id=None,
        human_source_user_id=None,
        reliability=None,
        captured_at=_NOW,
        validation_state=EvidenceValidationState.UNVALIDATED,
        content_version=RecordVersion.initial(),
        record_version=RecordVersion.initial(),
        supersedes_evidence_id=original.evidence_id,
        provenance_ref=None,
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repo.create_evidence(superseding)


def test_source_reference_round_trip(db_connection: sa.Connection) -> None:
    workspace_id, _owner = _bootstrap(db_connection, email="source-ref-roundtrip@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    source = SourceReference(
        source_reference_id=SourceReferenceId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        source_type="interview",
        locator="interview-transcript-042",
        external_id=None,
        title="Onboarding interview #42",
        retrieved_at=_NOW,
        source_published_at=None,
        content_fingerprint=None,
        snapshot_ref=None,
        created_by_ref="facilitator-1",
        origin=ProvenanceOrigin.HUMAN,
        validation_status="RESOLVED",
        created_at=_NOW,
        record_version=RecordVersion.initial(),
    )

    repo.create_source_reference(source)
    fetched = repo.get_source_reference(source.source_reference_id)

    assert fetched == source


def test_fabricated_source_reference_does_not_block_evidence_creation_but_stays_unvalidated(
    db_connection: sa.Connection,
) -> None:
    """07 section 9.3: "If source resolution fails because the source
    reference is fabricated... Evidence cannot become STRUCTURALLY_VALID
    where that source is required." This package builds no validator
    (that is a future package's own scope), so it proves the honest,
    narrower fact available now: a SourceReference recorded as
    `validation_status="INVALID"` is stored exactly as reported, and
    linked Evidence stays `UNVALIDATED` by default -- nothing in this
    package auto-promotes it.
    """
    workspace_id, _owner = _bootstrap(db_connection, email="source-fabricated@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    source = SourceReference(
        source_reference_id=SourceReferenceId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        source_type="url",
        locator="https://example.invalid/does-not-exist",
        external_id=None,
        title=None,
        retrieved_at=_NOW,
        source_published_at=None,
        content_fingerprint=None,
        snapshot_ref=None,
        created_by_ref="ai-citation-checker",
        origin=ProvenanceOrigin.AI,
        validation_status="INVALID",
        created_at=_NOW,
        record_version=RecordVersion.initial(),
    )
    repo.create_source_reference(source)
    evidence = Evidence(
        evidence_id=EvidenceId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        type=EvidenceType.DOMAIN_EVIDENCE,
        content="AI-cited claim from a fabricated source",
        source_reference_id=source.source_reference_id,
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

    fetched = repo.get_evidence(evidence.evidence_id)
    assert fetched is not None
    assert fetched.validation_state is EvidenceValidationState.UNVALIDATED
