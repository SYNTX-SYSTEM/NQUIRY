"""ProvenanceEnvelope: the reconstructable semantic provenance view for
one Evidence record.

Source: 07_EVIDENCE_AND_PROVENANCE.md section 23 (Provenance
Architecture -- the 7 questions provenance answers, and the 3 it does
not), section 25 (Provenance Dimensions -- "Minimum semantic
dimensions... These are semantic requirements. They are not yet a
physical universal database schema."), section 26 (CONFLICT-005
Resolution -- "UNIFORM SEMANTIC PROVENANCE OBLIGATION: YES. IDENTICAL
PHYSICAL FIELD SET FOR EVERY ARTIFACT: NO"), section 27 (ProvenanceEnvelope
-- "`[ARCHITECTURAL CLOSURE]`... is the semantic set of provenance
facts required for one artifact. It is not a new canonical domain
object. It may be materialized through: fields, relations, operational
records, audit links, depending on artifact class. The envelope must
be reconstructable as a whole."); 14_IMPLEMENTATION_SEQUENCE.md section
22 ("`[IMPLEMENTATION CHOICE]`: hybrid typed JSONB provenance envelope
plus normalized lineage link table. JSONB schema is versioned. This
does not make ProvenanceEnvelope a universal domain Thing.").

WHY THIS MODULE HOLDS NO DATABASE TABLE OF ITS OWN
------------------------------------------------------------------------
07 section 25 is explicit: the provenance dimensions "are not yet a
physical universal database schema", and section 26 (CONFLICT-005)
closes the question architecturally -- every artifact class satisfies
the SAME semantic obligation through a DIFFERENT physical shape (07's
own examples: "human Question needs author + timestamp..."; "imported
Evidence needs external source/import lineage..."). For `Evidence`
specifically, every dimension 07 section 25 lists is already carried
by fields this package's own `evidence.models.Evidence`/
`evidence.models.SourceReference` materialize -- `ProvenanceEnvelope`
here is therefore a pure reconstruction VIEW over those already-stored
fields, not a second, competing persistence target. This is the
literal meaning of 14 section 22's own "hybrid... plus normalized
lineage link table" -- the "table" is `evidence`/`source_references`
themselves; there is no separate `provenance_envelopes` table to
create.

WHY `ai_generation_ref`/`method_version_ref`/`consumption_refs` ARE
ALWAYS EMPTY/NONE HERE
------------------------------------------------------------------------
07 section 25 lists these as dimensions "WHERE APPLICABLE". No
`AIGeneration` repository or record exists yet (PKG-23+, Phase 7), no
method-version-consuming Command exists yet, and this package builds
no consequential consumer of Evidence at all (BND-013 is PKG-17's own
scope). Honestly disclosed as `SUCCESSOR_NOT_BUILT` via `None`/`()`
rather than fabricated.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from semantic_types.ids import EvidenceId, GenerationId, SourceReferenceId
from semantic_types.versions import RecordVersion

from evidence.models import Evidence, ProvenanceOrigin, SourceReference


@dataclass(frozen=True, slots=True)
class ProvenanceEnvelope:
    """07 section 25's own "minimum semantic dimensions", assembled as
    one reconstructable value for a single `Evidence` record. Not a
    canonical domain object (07 section 27) and not itself persisted.
    """

    target_artifact_id: EvidenceId
    artifact_version: RecordVersion
    origin: ProvenanceOrigin
    producer_ref: str
    captured_at: datetime
    source_reference_id: SourceReferenceId | None
    source_version_ref: str | None
    derivation_type: str | None
    ai_generation_id: GenerationId | None
    method_version_ref: str | None
    supersession_ref: EvidenceId | None
    consumption_refs: tuple[UUID, ...]


def build_evidence_provenance_envelope(
    evidence: Evidence, *, source_reference: SourceReference | None = None
) -> ProvenanceEnvelope:
    """Reconstructs 07 section 23's own 7 provenance questions ("Where
    did this information come from? Who or what produced it?...") from
    fields `Evidence`/`SourceReference` already store -- proving the
    envelope is reconstructable as a whole (07 section 27) without
    inventing any new persistence.

    `origin`/`producer_ref` are derived honestly from whichever facts
    `evidence` actually carries: a `human_source_user_id` implies
    `ProvenanceOrigin.HUMAN`; a `source_reference_id` with no human
    source implies the origin recorded on the linked `source_reference`
    (passed in by the caller, since this module has no repository
    access of its own -- 14 section 3.1 gives `evidence` no persistence
    dependency); absent both, the origin is honestly `SYSTEM_DERIVED`
    (07 section 24's own category for "operational/proof artifacts"),
    matching `Evidence.type` being `SYSTEM_PROOF`/`AI_VALIDATION_PROOF`
    in that case.
    """
    if evidence.human_source_user_id is not None:
        origin = ProvenanceOrigin.HUMAN
        producer_ref = str(evidence.human_source_user_id.value)
    elif source_reference is not None:
        origin = source_reference.origin
        producer_ref = source_reference.created_by_ref
    else:
        origin = ProvenanceOrigin.SYSTEM_DERIVED
        producer_ref = evidence.type.value

    return ProvenanceEnvelope(
        target_artifact_id=evidence.evidence_id,
        artifact_version=evidence.content_version,
        origin=origin,
        producer_ref=producer_ref,
        captured_at=evidence.captured_at,
        source_reference_id=evidence.source_reference_id,
        source_version_ref=(
            source_reference.content_fingerprint if source_reference is not None else None
        ),
        derivation_type=None,
        ai_generation_id=None,
        method_version_ref=None,
        supersession_ref=evidence.supersedes_evidence_id,
        consumption_refs=(),
    )


__all__ = ["ProvenanceEnvelope", "build_evidence_provenance_envelope"]
