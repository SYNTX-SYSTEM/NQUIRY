"""TestProofBundle: test-only representation collecting authoritative
proof REFERENCES a real E2E run already produced.

TEST ONLY. Must never be imported by production code -- guarded the
same way `packages/test_support/nonproof_bootstrap.py` already is:
the static import-graph rule enforced by
`scripts/check_test_only_imports.py`, not a runtime environment flag.

Source: 14_IMPLEMENTATION_SEQUENCE.md §39 ("`TestProofBundle` gathers
authoritative references to canonical state, governance, authority,
boundaries, CommitUnit, AuditEvent, EventEnvelope, Evidence versions,
AI lineage, RecoveryRecord and SecurityEvent. Logs are never the sole
oracle."); this package's own ARCHITECTURAL_INVARIANTS line:
"TESTPROOFBUNDLE COLLECTS EXISTING PROOF ONLY; TEST != AUTHORITY; GREEN
ASSERTION != ARCHITECTURAL PROOF."

WHY THIS IS A PLAIN COLLECTOR, NOT A NEW BOUNDARY/AUTHORITY MECHANISM
--------------------------------------------------------------------
Every field below is a REFERENCE to an object a real, already-governed
production code path already produced (a `CommitUnit`, a
`BoundaryProof`, a `RecoveryRecord`, ...) -- this module computes
nothing, evaluates no boundary, and grants no authority. Constructing
a `TestProofBundle` with a given field populated is not itself proof
of anything; the proof is the referenced object, independently
constructed by the real production code under test, and independently
inspectable by whoever reads a test that built this bundle. This
package's own ARCHITECTURAL_INVARIANT ("GREEN ASSERTION !=
ARCHITECTURAL PROOF") is honored by every E2E path test in
`tests/e2e/test_proof_bundle_paths.py` asserting on the REFERENCED
OBJECTS' OWN FIELDS (e.g. `commit_unit.outcome`, `boundary_proofs[0].result`),
never merely on this bundle's own shape.

WHY `boundary_proofs` IS OFTEN EMPTY ON A COMMITTED (ALLOW) PATH,
DISCLOSED, NOT PAPERED OVER
--------------------------------------------------------------------
`application.human_decision_handler.open_decision_consideration`/
`record_human_decision` (and `application.recovery_handler.RecoveryService
.resolve_recovery`) return only a `CommitUnit` on success -- the
individual per-boundary `BoundaryProof` objects the internal
`boundaries.registry.evaluate_chain` call produced are not part of
either function's own public return type. On a DENY, by contrast, the
raised exception's own `chain_result.proofs` tuple IS a real, already-
public artifact (`HumanDecisionDenied.chain_result`/
`RecoveryResolutionDenied.chain_result`). This module does not
reach into either handler's own internals to extract what its public
contract does not expose (that would be "production code solely to
ease a test", forbidden by this package's own FILES_FORBIDDEN_TO_MODIFY
line) -- a bundle for a COMMITTED path therefore honestly carries
`boundary_proofs=()`, with the returned `CommitUnit` itself serving as
the ALLOW-path proof (a `CommitUnit` can only exist because
`CommitCoordinator.commit()` requires `upstream_chain_result is
BoundaryResult.ALLOW` as a precondition -- PKG-13's own real
enforcement, unmodified here).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from boundaries.types import BoundaryProof
from commit.coordinator import CommitUnit
from recovery.models import RecoveryRecord

E2E_PROOF_PATHS = (
    "HAPPY",
    "DENIAL",
    "STALE_AUTHORITY",
    "CROSS_WORKSPACE",
    "AI_BOUNDARY",
    "RECOVERY",
)
"""14 PKG-30's own exact six named paths (OBJECTIVE line: "happy,
denial, stale-authority, cross-Workspace, AI-boundary, recovery").
Closed -- there is no seventh path this package is authorized to add.
"""

PathName = Literal[
    "HAPPY", "DENIAL", "STALE_AUTHORITY", "CROSS_WORKSPACE", "AI_BOUNDARY", "RECOVERY"
]


@dataclass(frozen=True, slots=True)
class TestProofBundle:
    """One E2E path's own collected proof references. Every field is
    `None`/`()` by default -- a path that genuinely does not produce a
    given artifact class (e.g. `DENIAL` never produces a `CommitUnit`)
    leaves it empty rather than fabricating a placeholder value.
    """

    path_name: PathName
    canonical_state_ref: str | None = None
    """A ref string naming the canonical row this path's own outcome is
    ultimately about (e.g. `"decision:<uuid>"`, mirroring
    `domain.decision.decision_target_ref`'s own ref-string convention)
    -- never the row's own content, only its identity."""
    governance_ref: str | None = None
    """The authority-binding id (or membership id, for a role-scope
    path) this path's own boundary evaluation actually consulted."""
    authority_ref: str | None = None
    """The resolved `AuthorityResolutionProof.binding_id`-shaped ref
    this path's own commit (if any) actually used, distinct from
    `governance_ref` (which may name a binding that was REJECTED,
    e.g. a revoked one)."""
    boundary_proofs: tuple[BoundaryProof, ...] = ()
    commit_unit: CommitUnit | None = None
    ai_lineage_ref: str | None = None
    """A `GenerationId`/`AIOperationId`-shaped ref, for the AI_BOUNDARY
    path only -- disclosed `None` on every other path (this package
    introduces no new AI lineage of its own)."""
    recovery_record: RecoveryRecord | None = None
    security_event_ref: str | None = None
    """Disclosed as always `None` in this package's own bundles -- no
    E2E path this package builds triggers a real `SecurityEvent` write
    (PKG-26's own security-event-writing paths are RLS/DB-privilege
    tests, not Command paths this package's own six named E2E scenarios
    exercise). Kept as a real field (not omitted) because 14 §39 names
    SecurityEvent as one of the eleven artifact classes this bundle
    type must be ABLE to carry, independent of whether any one path
    happens to populate it."""
    p_claims_exercised: tuple[str, ...] = field(default_factory=tuple)
    """Which `P-NN` identifiers THIS SPECIFIC RUN actually exercised --
    cross-checked against `test_support.proof_claim_matrix.PROOF_CLAIM_MATRIX`
    by `tests/e2e/test_proof_bundle_paths.py`'s own
    `test_every_exercised_claim_is_a_real_matrix_entry`."""

    def __post_init__(self) -> None:
        if self.path_name not in E2E_PROOF_PATHS:
            raise ValueError(f"path_name must be one of {E2E_PROOF_PATHS}, got {self.path_name!r}")
        for claim in self.p_claims_exercised:
            if not (claim.startswith("P-") and claim[2:].isdigit()):
                raise ValueError(f"p_claims_exercised entries must look like 'P-NN', got {claim!r}")


# 14 §46's own required name is literally `TestProofBundle` (PUBLIC_INTERFACES:
# "TestProofBundle") -- not renameable to dodge pytest's own "class starting
# with Test is a test class" collection heuristic. `__test__ = False` is
# pytest's own documented escape hatch for exactly this situation (a
# production/fixture class that happens to start with "Test"), set after
# the dataclass body rather than as a dataclass field so it never becomes a
# `slots=True` instance attribute.
TestProofBundle.__test__ = False  # type: ignore[attr-defined]

__all__ = ["E2E_PROOF_PATHS", "PathName", "TestProofBundle"]
